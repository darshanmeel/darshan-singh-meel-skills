"""List pinned tech versions in a repo for the Tech stack section: reads only manifest and pin files, never secret files or data.
Files: .python-version, environment*.yml (conda, incl. pip:), .nvmrc, .tool-versions, pyproject.toml, requirements*.txt, package.json, go.mod, Dockerfile*, docker-compose*.yml,
compose*.yml, *.tf (required_version, provider version), dbt_project.yml (require-dbt-version).

Usage: python stack.py [repo_root]   → one line per pin: `<tech> | <version> | <file>` (paths relative to the repo root)
"""
import json
import os
import re
import sys
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "generated-docs", "__pycache__", ".terraform", "target", "analysis", "reviews"}
SECRET = re.compile(r"(^\.env|\.pem$|\.key$|\.tfvars$|\.tfstate|credentials|secrets|^\.npmrc$|^\.pypirc$|^\.netrc$|profiles\.yml$|kubeconfig)", re.I)
REQ = re.compile(r"^\s*([A-Za-z0-9_.\-\[\]]+)\s*((?:==|~=|>=|<=|<|>|\^|~)\s*[\w.*]+(?:\s*,\s*[<>=!~]+\s*[\w.*]+)*)")


def files(root):
    for d, dirs, names in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP and not x.endswith("-knowledge-graph"))  # prune: never walked into
        for n in sorted(names):
            if not SECRET.search(n):
                p = Path(d) / n
                yield p, p.relative_to(root).as_posix()


def pins(p, rel):
    name, text = p.name, p.read_text(encoding="utf-8", errors="ignore")
    if name in (".python-version", ".nvmrc"):
        yield ("Python" if name == ".python-version" else "Node.js"), text.strip()
    elif name == ".tool-versions":
        for line in text.splitlines():
            if len(line.split()) >= 2:
                yield line.split()[0], line.split()[1]
    elif name == "pyproject.toml":
        if (m := re.search(r'requires-python\s*=\s*"([^"]+)"', text)):
            yield "Python", m[1]
        block = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.S)
        for dep in re.findall(r'"([^"]+)"', block[1] if block else ""):
            if (m := REQ.match(dep)):
                yield m[1], m[2].replace(" ", "")
        poetry = re.search(r"^\[tool\.poetry\.(?:group\.\w+\.)?dependencies\](.*?)(?=^\[|\Z)", text, re.M | re.S)
        for m in re.finditer(r'^([A-Za-z0-9_.-]+)\s*=\s*"([\^~>=<\d][^"]*)"', poetry[1] if poetry else "", re.M):
            yield m[1], m[2]
    elif re.match(r"requirements.*\.txt$", name):
        for line in text.splitlines():
            if (m := REQ.match(line)):
                yield m[1], m[2].replace(" ", "")
    elif name == "package.json":
        try:
            data = json.loads(text)
        except ValueError:
            return
        if (data.get("engines") or {}).get("node"):
            yield "Node.js", data["engines"]["node"]
        for k in ("dependencies", "devDependencies"):
            for dep, v in (data.get(k) or {}).items():
                yield dep, v
    elif re.match(r"environment.*\.ya?ml$", name):  # conda: `- python=3.12` and the `pip:` list
        for m in re.finditer(r"^\s*-\s*([A-Za-z0-9_.-]+)\s*(==?|>=|<=|~=)\s*([\w.*]+)", text, re.M):
            yield m[1], ("" if m[2] == "=" else m[2]) + m[3]
    elif name == "go.mod":
        if (m := re.search(r"^go (\S+)", text, re.M)):
            yield "Go", m[1]
    elif name.startswith("Dockerfile"):
        for m in re.finditer(r"^FROM\s+(?:--\S+\s+)?(\S+)", text, re.M | re.I):
            yield "image", m[1]
    elif re.match(r"(docker-)?compose.*\.ya?ml$", name):
        for m in re.finditer(r"^\s*image:\s*['\"]?([^\s'\"]+)", text, re.M):
            yield "image", m[1]
    elif name.endswith(".tf"):
        if (m := re.search(r'required_version\s*=\s*"([^"]+)"', text)):
            yield "Terraform", m[1]
        for m in re.finditer(r'source\s*=\s*"([^"]+)"\s*\n\s*version\s*=\s*"([^"]+)"', text):
            yield m[1], m[2]
    elif name == "dbt_project.yml":
        if (m := re.search(r"require-dbt-version:\s*(.+)", text)):
            yield "dbt", m[1].strip()


def main(root):
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(root)
    n = 0
    for p, rel in files(root):
        for tech, version in pins(p, rel):
            print(f"{tech} | {version} | {rel}")
            n += 1
    print(f"stack: {n} pins")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
