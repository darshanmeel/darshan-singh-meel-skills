"""Check a prototype folder. Usage: python check_prototype.py prototypes/<name> [--done] [--no-gitignore]
FAIL (exit 1): NOTES.md without question, branch or run command (--done: answer and keep too); /prototypes/
missing in the project's .gitignore; a secret-looking file or value; Data: a non-local connection or a data source outside the folder; a dbt profile
that is more than one local DuckDB file; Pipeline: a real operator or client; UI: not 2-5 variants found in code.
Secret-looking files are never opened; values are never printed. --no-gitignore: for an example kept in a repo."""
import pathlib
import re
import sys

SECRET_FILES = re.compile(
    r"^(\.env.*|.*\.(pem|key|p12|pfx|jks|keystore|tfvars)|.*\.tfstate.*|id_.*|credentials.*|secrets.*|"
    r"\.npmrc|\.pypirc|\.netrc|\.git-credentials|kubeconfig)$", re.I)
SKIP_DIRS = {".venv", "node_modules", "target", "dbt_packages", "logs", ".airflow", "__pycache__", ".git"}
CODE = {".py", ".sql", ".yml", ".yaml", ".toml", ".json", ".js", ".jsx", ".ts", ".tsx", ".html", ".md", ".cfg", ".ini"}
NAME = r"(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)"
SECRETS = {
    "quoted secret": re.compile(NAME + r"""["']?\s*[:=]\s*["'][^"'<{$\s]{6,}["']""", re.I),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "cloud access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "URL with credentials": re.compile(r"\w+://[^/\s:@]+:[^@\s/]+@"),
}
CONFIG_SECRET = re.compile(r"^\s*" + NAME + r"\s*[:=]\s*[^\s<{$\"']{6,}", re.I)
REMOTE = {
    "warehouse or cloud client import": re.compile(
        r"^\s*(import|from)\s+(snowflake|databricks|google\.cloud|redshift_connector|pyathena|psycopg\d?|"
        r"pyodbc|pymysql|sqlalchemy|boto3|trino|azure)\b", re.M),
    "remote URL": re.compile(r"\b(postgres(ql)?|mysql|snowflake|databricks|jdbc|s3a?|gs|gcs|abfss?|az|r2|https?)://", re.I),
    "MotherDuck": re.compile(r"""["'\s](md|motherduck):""", re.I),
    "remote DuckDB extension": re.compile(
        r"\b(INSTALL|LOAD)\s+(httpfs|postgres|mysql|aws|azure|iceberg|delta)\b|\bTYPE\s+(postgres|mysql)\b", re.I),
    # a database or file opened outside the folder: absolute, home or parent path, or a key=value connection string
    "data source outside the folder": re.compile(
        r"""\b(connect|ATTACH|read_\w+|FROM)\s*\(?\s*['"]([A-Za-z]:|[/\\~]|[^'"]*\.\.|[^'"]*=)""", re.I),
}
REAL_TASKS = re.compile(
    r"airflow\.providers|BashOperator|\bVariable\b|get_connection|"
    r"^\s*(?:import|from)\s+(?:requests|httpx|socket|boto3|urllib|smtplib|snowflake|databricks)\b", re.M)
PROFILE_KEYS = {"target", "type", "path", "schema", "threads"}


def section(notes, title):
    m = re.search(rf"^## {re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", notes, re.M | re.S)
    body = re.sub(r"<!--.*?-->", "", m[1], flags=re.S).strip() if m else ""
    return "" if re.search(r"<[^>\n]+>", body) else body  # an unfilled <placeholder> counts as empty


def files(folder):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(folder).parts):
            yield p


def check_profile(text):
    """The prototype's own dbt profile: plain allow-listed keys only. Returns rule names, never values."""
    bad = []
    for line in text.splitlines():
        m = re.match(r"\s*([\w-]+):\s*(.*)$", line.split("#")[0].rstrip())
        if not m or not m[2]:
            continue  # comment, blank, or a nesting key (profile name, outputs, target name)
        key, value = m[1], m[2].strip("'\"")
        if key not in PROFILE_KEYS:
            bad.append(f"key '{key}' not allowed")
        elif key == "type" and value != "duckdb":
            bad.append("type is not duckdb")
        elif key == "path" and (re.search(r"[:{~]|\.\.", value) or value.startswith(("/", "\\")) or not value.endswith(".duckdb")):
            bad.append("path is not a relative .duckdb file inside the folder")
    return bad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1 or not pathlib.Path(args[0], "NOTES.md").is_file():
        sys.exit("usage: check_prototype.py prototypes/<name> [--done] [--no-gitignore]  (folder needs NOTES.md)")
    folder = pathlib.Path(args[0]).resolve()
    root = folder.parent.parent
    fail = []
    notes = (folder / "NOTES.md").read_text(encoding="utf-8")

    branch = re.search(r"^Branch:\s*(Logic|UI|Data|Pipeline)\s*$", notes, re.M)
    if not branch:
        fail.append("NOTES.md: 'Branch:' must be Logic, UI, Data or Pipeline")
    if not re.search(r"^Run:\s*`[^`<]+`", notes, re.M):
        fail.append("NOTES.md: 'Run:' needs one command in backticks")
    for title in ["Question"] + (["Answer", "Keep"] if "--done" in sys.argv else []):
        if not section(notes, title):
            fail.append(f"NOTES.md: section '{title}' is empty or still a placeholder")
    branch = branch[1] if branch else ""

    if folder.parent.name != "prototypes":
        fail.append("folder is not prototypes/<name>")
    elif "--no-gitignore" not in sys.argv:
        ignore = root / ".gitignore"
        lines = ignore.read_text(encoding="utf-8").splitlines() if ignore.is_file() else []
        if not any(line.strip() in ("/prototypes/", "prototypes/", "/prototypes") for line in lines):
            fail.append(".gitignore at the project root has no /prototypes/ line")

    outside = [root / line.strip("-` \t") for line in section(notes, "Files outside prototypes/").splitlines()
               if line.strip("-` \t").lower() not in ("", "none")]
    for p in outside:
        if not p.is_file():
            fail.append(f"NOTES.md lists a file that does not exist: {p.relative_to(root).as_posix()}")
        elif "prototype" not in p.name.lower():
            fail.append(f"file outside prototypes/ without 'prototype' in its name: {p.relative_to(root).as_posix()}")

    code = ""
    for p in list(files(folder)) + [p for p in outside if p.is_file()]:
        rel = p.relative_to(root).as_posix()
        if SECRET_FILES.match(p.name):
            fail.append(f"{rel}: secret-looking file name (not opened)")
            continue
        if p.suffix.lower() not in CODE or p.stat().st_size > 1_000_000:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if p.name == "profiles.yml":
            fail += [f"{rel}: dbt profile - {b}" for b in check_profile(text)]
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for rule, rx in SECRETS.items():
                if rx.search(line):
                    fail.append(f"{rel}:{n}: {rule} <redacted>")
            if p.suffix.lower() in (".yml", ".yaml", ".toml", ".cfg", ".ini") and CONFIG_SECRET.search(line):
                fail.append(f"{rel}:{n}: secret in config <redacted>")
        if p.suffix.lower() != ".md":
            code += text
            if branch == "Data":
                fail += [f"{rel}: {rule} - Data prototypes stay local" for rule, rx in REMOTE.items() if rx.search(text)]
            if branch == "Pipeline" and (m := REAL_TASKS.search(text)):
                fail.append(f"{rel}: '{m[0]}' - Pipeline tasks are stubs (print, sleep, raise)")

    if branch == "UI":
        keys = re.findall(r"^\s*-\s*`?([\w-]+)`?\s+-\s+\S", section(notes, "Variants"), re.M)
        if not 2 <= len(keys) <= 5:
            fail.append(f"NOTES.md: section 'Variants' lists {len(keys)} variants, needs 2-5 lines '- <key> - <structure>'")
        for k in keys:
            if not re.search(rf"""["']{re.escape(k)}["']""", code):
                fail.append(f"variant '{k}' from NOTES.md not found as a quoted key in the prototype's code")

    for f in fail:
        print("FAIL", f)
    print(f"{folder.name} ({branch or 'no branch'}): {len(fail)} FAIL")
    sys.exit(1 if fail else 0)


main()
