"""Checks the built widget before a deploy: built from the committed source, self-contained, small, deployed.

    python tools/check_dist.py [app folder]     (default: the folder above tools/)

Exit 1 on any ERROR. Stdlib only, no Node needed.
"""
import fnmatch
import hashlib
import re
import subprocess
import sys
from pathlib import Path

# The fallback mount sends the whole page on every rerun; the warehouse runtime caps a message at 32 MB.
MAX_BYTES = 2_000_000
RUNTIMES = re.compile(r"SYSTEM\$WAREHOUSE_RUNTIME|SYSTEM\$ST_CONTAINER_RUNTIME_PY3_\d+")
CSP = re.compile(r"\beval\s*\(|\bFunction\s*\(")
REMOTE = re.compile(r"""url\(\s*["']?(?:https?:)?//|@import\s+(?:url\()?\s*["']?(?:https?:)?//|\b(?:src|href)\s*=\s*["'](?:https?:)?//|\b(?:import|from)\s*["'](?:https?:)?//""")
PLACEHOLDER = re.compile(r"<[^<>\s][^<>\n]*>")


def source_hash(frontend):
    """Same hash as sourceHash() in vite.config.ts; None when git can't list the source."""
    try:
        r = subprocess.run(["git", "ls-files", "-z", "."], cwd=frontend, capture_output=True)
    except FileNotFoundError:
        return None
    files = sorted(f for f in r.stdout.decode("utf-8").split("\0") if f) if r.returncode == 0 else []
    if not files:
        return None
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode("utf-8") + b"\0")
        h.update((frontend / f).read_bytes().replace(b"\r\n", b"\n"))
        h.update(b"\0")
    return h.hexdigest()[:16]


def artifacts(snowflake_yml):
    """The artifact paths listed in snowflake.yml (plain `- path` or `- src: path` items)."""
    out, inside = [], False
    for line in snowflake_yml.read_text(encoding="utf-8").splitlines():
        if re.match(r"\s*artifacts:\s*$", line):
            inside = True
        elif inside and (m := re.match(r"\s*-\s*(?:src:\s*)?(\S+)", line)):
            out.append(m[1].strip("'\"").rstrip("/"))
        elif inside and line.strip() and not re.match(r"\s+dest:", line):
            inside = False
    return out


def covers(entry, path):
    """True when an artifact entry (a path, a folder or a glob) ships `path`."""
    return entry in (".", "*") or path == entry or path.startswith(entry + "/") or fnmatch.fnmatch(path, entry)


def check_build(name, text, size, want_hash, errors):
    m = re.search(r"source-hash[\"']?\s*(?:content=\"|:\s*)([0-9a-f]{16})", text)
    if not m:
        errors.append(f"{name} has no source-hash: build with the template's Vite configs")
    elif want_hash and m[1] != want_hash:
        errors.append(f"{name} is stale: commit the frontend source, then npm run build (and build:v2)")
    if REMOTE.search(text):
        errors.append(f"{name} loads from another site (script, style, font or import): bundle it")
    if CSP.search(text):
        errors.append(f"{name}: eval() or Function(): the content security policy blocks it")
    if size > MAX_BYTES:
        errors.append(f"{name} is {size:,} bytes > {MAX_BYTES:,}: drop dependencies or inline less")


def check(app):
    errors, notes = [], []
    frontend, page = app / "component" / "frontend", app / "component" / "dist" / "index.html"
    v2 = app / "component" / "dist-v2" / "widget.js"
    if not page.is_file():
        return ["no build: cd component/frontend && npm ci && npm run build"], notes
    want = source_hash(frontend)
    if want is None:
        notes.append("skip source-hash: not a git checkout, or component/frontend is not committed")

    html = page.read_text(encoding="utf-8")
    check_build("dist/index.html", html, page.stat().st_size, want, errors)
    for ref in re.findall(r'\b(?:src|href)\s*=\s*["\']([^"\']+)', html):
        if not ref.startswith(("data:", "#", "http:", "https:", "//")):
            errors.append(f"index.html loads '{ref}': the build must inline everything")
    if v2.is_file():
        check_build("dist-v2/widget.js", v2.read_text(encoding="utf-8"), v2.stat().st_size, want, errors)

    for name in ("snowflake.yml", "environment.yml", "requirements.txt", "pyproject.toml"):
        p = app / name
        if p.is_file() and (m := PLACEHOLDER.search(p.read_text(encoding="utf-8"))):
            errors.append(f"{name} still has the placeholder {m[0]}: fill it in")

    yml = app / "snowflake.yml"
    if yml.is_file():
        arts = artifacts(yml)
        runtime = re.search(r"^\s*runtime_name:\s*(\S+)", yml.read_text(encoding="utf-8"), re.M)
        if not runtime:
            errors.append("snowflake.yml has no runtime_name: leaving it out now means the container runtime")
        elif not RUNTIMES.fullmatch(runtime[1].strip("'\"")):
            errors.append(f"snowflake.yml runtime_name '{runtime[1]}' is not a known runtime name")
        container = bool(runtime and "CONTAINER" in runtime[1])
        want_art, other = ("component/dist-v2/widget.js", "component/dist/index.html") if container else \
                          ("component/dist/index.html", "component/dist-v2/widget.js")
        if not any(covers(a, want_art) for a in arts):
            errors.append(f"snowflake.yml artifacts miss {want_art}: the app deploys without the widget")
        if any(covers(a, other) for a in arts):
            errors.append(f"snowflake.yml also ships {other}: one build per runtime, or widget.py picks the wrong mount")
        for a in arts:
            if covers(a, "component/frontend/package.json") or a.startswith("component/frontend"):
                errors.append(f"snowflake.yml artifact '{a}' uploads the frontend source (and node_modules): list the build file only")
    else:
        notes.append("skip artifacts: no snowflake.yml")

    for py in app.glob("*.py"):
        if re.search(r"""["']https?://(?:localhost|127\.0\.0\.1)""", py.read_text(encoding="utf-8")):
            errors.append(f"{py.name}: a localhost dev URL in the code: read it only from WIDGET_DEV_URL, with no default")
    return errors, notes


def main():
    app = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors, notes = check(app)
    for n in notes:
        print("NOTE", n)
    for e in errors:
        print("ERROR", e)
    print("dist OK" if not errors else f"{len(errors)} ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
