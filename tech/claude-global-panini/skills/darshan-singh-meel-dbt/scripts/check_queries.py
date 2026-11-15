"""Check an analysis folder (notebooks and .sql files) before handing it over.

Usage: check_queries.py <analysis/topic folder>
Errors: no 00_connection.ipynb next to question notebooks; a query in 00_connection.ipynb that reads a relation;
a SQL code cell without a markdown cell right before it that states `Grain` and `Look for`; more than one SQL
statement in a cell; SQL passed to q()/execute()/read_sql() through a variable; a non-raw SQL string with a
backslash; a statement that is not SELECT/WITH/SHOW/DESCRIBE/EXPLAIN; a .sql file without its header;
a secret-looking literal; an absolute machine path. Prints 'N ERROR' and exits 1 if N > 0.
Sees SQL written in the cells only: SQL built at run time or read from files elsewhere is not checked.
"""
import ast
import io
import json
import re
import sys
import tokenize
from pathlib import Path

ALLOWED = ("select", "with", "show", "describe", "desc", "explain")
SQL_START = re.compile(r"^\s*(select|with|show|describe|desc|explain|insert|update|delete|merge|create|alter|drop|"
                       r"truncate|grant|revoke|call|use|copy|put|get|remove|rm|undrop|comment|execute|optimize|vacuum)\b", re.I)
WRITE_INSIDE = re.compile(r"\b(insert\s+(into|overwrite)|delete\s+from|merge\s+into|update\s+\w[\w.]*\s+set|select\b[^;]*?\binto\s+\w)", re.I | re.S)
SECRET = re.compile(r"(password|passwd|token|secret|private_key|api_key)\s*[=:]\s*['\"][^'\"]{4,}|-----BEGIN [A-Z ]*PRIVATE KEY"
                    r"|://[^/\s:@'\"]+:[^@\s'\"]+@"
                    r"|(?:environ\.get|getenv)\(\s*['\"][^'\"]*(?:password|passwd|token|secret|api_key|private_key)[^'\"]*['\"]\s*,\s*['\"][^'\"]+",
                    re.I)
MACHINE = re.compile(r"(?<!\w)[A-Za-z]:\\{1,2}[\w.$-]|/Users/[^/\s]+/|/home/[^/\s]+/")
SQL_HEADER = ("-- what:", "-- reads:", "-- look for:")
CALLS = {"q", "sql", "execute", "executemany", "read_sql", "read_sql_query"}
RELATION = re.compile(r"\bfrom\s+[A-Za-z_\"`]", re.I)
NOISE = re.compile(r"'(?:[^']|'')*'|/\*.*?\*/|--[^\n]*", re.S)


def strip_noise(sql):
    """Drop comments and the contents of string literals, so `;` or keywords inside them do not count."""
    return NOISE.sub(lambda m: "''" if m.group().startswith("'") else " ", sql)


def statements(sql):
    return [s.strip() for s in strip_noise(sql).split(";") if s.strip()]


def bad_statements(sql):
    out = []
    for s in statements(sql):
        word = s.split(None, 1)[0].lower()
        if word not in ALLOWED or re.search(r"\bsystem\$", s, re.I) or WRITE_INSIDE.search(s):
            out.append(s[:60].replace("\n", " "))
    return out


def is_sql(text):
    return bool(SQL_START.match(strip_noise(text)))


def source(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def python_parts(src):
    """(SQL literals, problems) of a Python code cell; magics and shell lines are blanked first."""
    code = "\n".join("" if ln.lstrip().startswith(("%", "!")) else ln for ln in src.splitlines())
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [], ["code cell does not parse; check it by reading"]
    sqls, problems = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and is_sql(n.value):
            sqls.append(n.value)
    funcs = [f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
    inside = {id(x) for f in funcs for x in ast.walk(f)}   # calls inside a helper's own body use its parameter
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and id(n) not in inside and n.args:
            name = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
            if name in CALLS and not isinstance(n.args[0], (ast.Constant, ast.JoinedStr)):
                problems.append(f"SQL passed to {name}() through a variable; read the cell")
    try:
        for t in tokenize.generate_tokens(io.StringIO(code).readline):
            if t.type == tokenize.STRING and "\\" in t.string:
                prefix = t.string[:len(t.string) - len(t.string.lstrip("rRbBuUfF"))]
                if "r" not in prefix.lower() and is_sql(ast.literal_eval(t.string)):
                    problems.append('SQL string with a backslash is not raw: use r"""')
    except (tokenize.TokenError, SyntaxError, ValueError):
        pass
    return sqls, problems


def cell_parts(cell):
    src = source(cell)
    if src.lstrip().startswith(("%%sql", "%sql")):
        return ([src.split("\n", 1)[1]] if "\n" in src else []), []
    if is_sql(src):
        return [src], []
    return python_parts(src)


def check_text(path, text, errors):
    if SECRET.search(text):
        errors.append(f"{path}: secret-looking literal")
    if MACHINE.search(text):
        errors.append(f"{path}: absolute machine path")


def good_markdown(cell):
    text = source(cell).lower()
    return cell.get("cell_type") == "markdown" and "grain" in text and "look for" in text


def check_notebook(path, errors):
    cells = json.loads(path.read_text(encoding="utf-8")).get("cells", [])
    connection = path.name == "00_connection.ipynb"
    for i, c in enumerate(cells):
        where = f"{path.name} cell {i + 1}"
        check_text(where, source(c), errors)
        if c.get("cell_type") != "code":
            continue
        sqls, problems = cell_parts(c)
        errors.extend(f"{where}: {p}" for p in problems)
        if not sqls:
            continue
        if i == 0 or not good_markdown(cells[i - 1]):
            errors.append(f"{where}: query without a markdown cell right before it stating Grain and Look for")
        if not connection and (len(sqls) > 1 or any(len(statements(s)) > 1 for s in sqls)):
            errors.append(f"{where}: more than one SQL statement in one cell")
        for s in sqls:
            if connection and RELATION.search(strip_noise(s)):
                errors.append(f"{where}: query against data in 00_connection.ipynb")
            for b in bad_statements(s):
                errors.append(f"{where}: not read-only: {b}")


def check_sql(path, errors):
    text = path.read_text(encoding="utf-8")
    check_text(path.name, text, errors)
    head = text.lower()[:600]
    missing = [h for h in SQL_HEADER if h not in head]
    if missing:
        errors.append(f"{path.name}: header missing {', '.join(missing)}")
    for s in bad_statements(text):
        errors.append(f"{path.name}: not read-only: {s}")


def check(folder):
    folder, errors = Path(folder), []
    notebooks = sorted(p for p in folder.glob("*.ipynb") if not p.stem.endswith("-changes"))
    if notebooks and not (folder / "00_connection.ipynb").is_file():
        errors.append(f"{folder.name}: 00_connection.ipynb missing")
    for p in notebooks:
        check_notebook(p, errors)
    for p in sorted(folder.rglob("*.sql")):
        check_sql(p, errors)
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    errs = check(sys.argv[1])
    for e in errs:
        print("ERROR", e)
    print(f"{len(errs)} ERROR")
    sys.exit(1 if errs else 0)
