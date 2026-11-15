"""Check a query folder made with darshan-singh-meel-snowflake (notebooks and .sql files).

Usage: python check_queries.py <folder>
ERROR (exit 1): no 00_connection.ipynb beside other notebooks; a notebook whose first code cell differs from the
connection cell; a code cell with SQL and no markdown note (What / Reads / Look for) right before it; a .sql
statement without that header; SQL that is not read-only outside NN_user_* files; secret literals; machine paths.
WARN: file names that do not follow NN_<name>; sensitive columns selected (QUERY_TEXT, BIND_VALUES, POLICY_BODY,
*_DEFINITION); more than one SQL string in a code cell.
Best-effort text checks: the read-only role is the guarantee. Standard library only.
"""
import ast
import json
import re
import sys
from pathlib import Path

READ = {"select", "with", "show", "describe", "desc", "explain"}
WRITE = re.compile(r"\b(insert|update|delete|merge|truncate|create|alter|drop|undrop|grant|revoke|call|execute|put|remove)\b"
                   r"|system\$", re.I)
SQL_START = re.compile(r"\s*\(?\s*(select|with|show|describe|desc|explain|insert|update|delete|merge|create|alter|drop"
                       r"|grant|revoke|call|use|copy|put|remove|truncate|execute|set|unset|begin|commit)\b", re.I)
LABELS = ("what:", "reads:", "look for:")
SECRET = re.compile(r"(password|passwd|pwd|token|secret|private_key|passphrase)\w*\s*[=:]\s*[\"'][^\"'\s]{3,}[\"']"
                    r"|-----BEGIN [A-Z ]*PRIVATE KEY", re.I)
MACHINE = re.compile(r"(?<![\w\\])[A-Za-z]:[\\/](Users|home)\b|/Users/[a-z]|/home/[a-z]", re.I)
NAME = re.compile(r"^\d{2}_[a-z0-9_]+\.(ipynb|sql)$")
SENSITIVE = re.compile(r"\b(query_text|bind_values|policy_body|\w+_definition)\b", re.I)


def chunks(sql):
    """Split on ';' outside quotes and comments; keeps comments in each chunk."""
    out, start, i, n = [], 0, 0, len(sql)
    while i < n:
        two = sql[i:i + 2]
        if two == "--":
            j = sql.find("\n", i)
            i = n if j < 0 else j
        elif two == "/*":
            j = sql.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif two == "$$":
            j = sql.find("$$", i + 2)
            i = n if j < 0 else j + 2
        elif sql[i] in "'\"":
            q, i = sql[i], i + 1
            while i < n and not (sql[i] == q and sql[i + 1:i + 2] != q):
                i += 2 if sql[i:i + 2] in (q + q, "\\" + q) else 1
            i += 1
        elif sql[i] == ";":
            out.append(sql[start:i])
            start = i = i + 1
        else:
            i += 1
    out.append(sql[start:])
    return [c for c in out if code(c)]


def code(chunk):
    """Statement text without comments; string literals blanked."""
    s = re.sub(r"/\*.*?\*/|\$\$.*?\$\$", " ", chunk, flags=re.S)
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"'(?:[^']|'')*'", "''", s)
    return s.strip()


def not_read_only(sql):
    for c in chunks(sql):
        s = code(c)
        first = re.match(r"[(\s]*(\w+)", s)
        if not first or first.group(1).lower() not in READ:
            return s[:50]
        if hit := WRITE.search(s):
            return hit.group(0)


def sql_in_cell(src):
    """SQL strings in a code cell: a %%sql body, or Python string literals that start like SQL."""
    lines = src.splitlines()
    if lines and lines[0].lstrip().startswith("%%sql"):
        return ["\n".join(lines[1:])]
    py = "\n".join("" if re.match(r"\s*[%!]", line) else line for line in lines)
    found = []
    for node in ast.walk(ast.parse(py)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and SQL_START.match(code(node.value)):
            found.append(node.value)
    return found


def has_note(text):
    t = text.replace("*", "").lower()
    return all(label in t for label in LABELS)


def sensitive(sql):
    m = SENSITIVE.search(code(sql))
    return m.group(0) if m else None


def check_notebook(f, setup, err, warn):
    nb = json.loads(f.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    src = ["".join(c.get("source", "")) for c in cells]
    codes = [i for i, c in enumerate(cells) if c.get("cell_type") == "code"]
    user = "_user_" in f.name
    if f.name != "00_connection.ipynb" and setup is not None and codes and src[codes[0]].strip() != setup:
        err.append(f"{f.name}: first code cell is not the connection cell of 00_connection.ipynb")
    for i in codes:
        try:
            sqls = sql_in_cell(src[i])
        except SyntaxError:
            err.append(f"{f.name} cell {i + 1}: code that cannot be parsed")
            continue
        if sqls and not (i > 0 and cells[i - 1].get("cell_type") == "markdown" and has_note(src[i - 1])):
            err.append(f"{f.name} cell {i + 1}: query without a markdown note (What / Reads / Look for) right before it")
        if len(sqls) > 1:
            warn.append(f"{f.name} cell {i + 1}: {len(sqls)} SQL strings in one cell; one query per code cell")
        for s in sqls:
            if col := sensitive(s):
                warn.append(f"{f.name} cell {i + 1}: selects {col}; use QUERY_ID / QUERY_PARAMETERIZED_HASH instead")
        if not user:
            for s in sqls:
                if bad := not_read_only(s):
                    err.append(f"{f.name} cell {i + 1}: not read-only ({bad}); move it to an NN_user_ notebook")


def check_sql(f, err, warn):
    text = f.read_text(encoding="utf-8-sig")
    for n, c in enumerate(chunks(text), 1):
        header = []
        for line in c.strip().splitlines():
            if line.strip() and not line.strip().startswith("--"):
                break
            header.append(line)
        if not has_note("\n".join(header)):
            err.append(f"{f.name} statement {n}: no header comment with What / Reads / Look for")
        if col := sensitive(c):
            warn.append(f"{f.name} statement {n}: selects {col}; use QUERY_ID / QUERY_PARAMETERIZED_HASH instead")
    if "_user_" not in f.name and (bad := not_read_only(text)):
        err.append(f"{f.name}: not read-only ({bad}); move it to an NN_user_ file")


def connection_cell(folder):
    f = folder / "00_connection.ipynb"
    if not f.is_file():
        return None
    cells = json.loads(f.read_text(encoding="utf-8")).get("cells", [])
    first = next((c for c in cells if c.get("cell_type") == "code"), None)
    return "".join(first.get("source", "")).strip() if first else None


def main(folder):
    folder = Path(folder)
    err, warn = [], []
    notebooks = sorted(p for p in folder.glob("*.ipynb"))
    sqls = sorted(folder.glob("*.sql")) + sorted(folder.glob("sql/*.sql"))
    if not notebooks and not sqls:
        sys.exit(f"no .ipynb or .sql files in {folder}")
    setup = connection_cell(folder)
    if notebooks and setup is None:
        err.append("00_connection.ipynb missing (or has no code cell): the connection notebook comes first")
    for f in notebooks + sqls:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if f.suffix == ".ipynb":  # scan the cell text, not the JSON escaping around it
            text = "\n".join("".join(c.get("source", "")) for c in json.loads(text).get("cells", []))
        if m := SECRET.search(text):
            err.append(f"{f.name}: secret literal ({m.group(1) or 'private key'}=<redacted>); read it from an environment variable")
        if m := MACHINE.search(text):
            err.append(f"{f.name}: machine path '{m.group(0)}'")
        if not NAME.match(f.name):
            warn.append(f"{f.name}: name does not follow NN_<name>")
    for f in notebooks:
        check_notebook(f, setup, err, warn)
    for f in sqls:
        check_sql(f, err, warn)
    for w in warn:
        print("WARN", w)
    for e in err:
        print("ERROR", e)
    print(f"{len(err)} ERROR, {len(warn)} WARN")
    return 1 if err else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
