"""Check query notebooks and .sql files made with the Databricks skill.
Usage: python check_queries.py <folder | file.ipynb | file.sql> ...
Rules: a folder with question notebooks has 00_connection.ipynb; every code cell with SQL has a markdown cell
right before it with Does / Reads / Look for; every .sql file starts with a header holding what: / views: /
look for:; every statement is SELECT / WITH / SHOW / DESCRIBE / EXPLAIN with no write keyword (SHOW CREATE
allowed); the first argument of q() / execute() / sql() is always SQL, f-strings and '+' folded; SQL built by
string formatting, a backslash in a non-raw SQL string and Python table writes fail; no token-like literal,
secret assignment or machine path. Skips *changes* / *prerequisite* notebooks and changes/ folders (user-run).
Prints FAIL lines and '<n> FAIL'; exit 1 on any FAIL. Best-effort: the read-only role is the guarantee."""
import ast
import json
import pathlib
import re
import sys

READ = {"SELECT", "WITH", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"}
WRITE = re.compile(r"\b(INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|GRANT|REVOKE|TRUNCATE|COPY|OPTIMIZE|VACUUM"
                   r"|CALL|REFRESH|RESTORE|MSCK|ANALYZE|REPAIR|CACHE|UNCACHE|EXECUTE|PUT|REMOVE)\b", re.I)
READ_START = re.compile(r"^[(\s]*(" + "|".join(sorted(READ)) + r")\b", re.I)
# A write verb plus its usual next word, so prose such as "Update the note" does not count as SQL.
WRITE_START = re.compile(
    r"^[(\s]*(INSERT\s+(INTO|OVERWRITE)|UPDATE\s+\S+\s+SET\b|DELETE\s+FROM|(MERGE|COPY)\s+INTO"
    r"|(CREATE|ALTER|DROP|UNDROP)\s+(OR\s+REPLACE\s+|IF\s+(NOT\s+)?EXISTS\s+|\w+\s+){0,3}"
    r"(TABLE|VIEW|SCHEMA|DATABASE|CATALOG|FUNCTION|VOLUME|SHARE|RECIPIENT|CONNECTION|LOCATION)\b"
    r"|(GRANT|REVOKE)\s+.+\s(ON|TO|FROM)\s|TRUNCATE\s+TABLE|(OPTIMIZE|VACUUM)\s+[\w.`?]"
    r"|(REFRESH|MSCK|ANALYZE|CACHE|UNCACHE|RESTORE|REPAIR)\s+TABLE|CALL\s+[\w.]+\s*\(|USE\s+\S+\s*$|SET\s+\S+\s*=)",
    re.I | re.S)
SQLISH = re.compile(r"\n|\b(FROM|TABLE|SCHEMA|CATALOG|INTO|VALUES|WHERE|GRANTS|TBLPROPERTIES|DETAIL|HISTORY)\b|=", re.I)
SQL_CALLS = {"q", "execute", "executemany", "sql"}  # their first argument is always SQL
WRITE_PY = re.compile(r"\.write(Stream|To)?\b|saveAsTable|insertInto|\bDeltaTable\b|\.to_(table|sql)\b|write_pandas")
FORMATTED = "SQL built by string formatting: use :name parameters (IDENTIFIER(:name) for object names)"
RAW = 'backslash in a non-raw string: Python eats it before SQL sees it; use q(r"""...""")'
SECRET = re.compile(r"dapi[0-9a-f]{32}|(?i:\b(token|password|passwd|secret|client_secret|api_key)\s*[=:]\s*[\"'][^\"'\s]{8,}[\"'])")
MACHINE = re.compile(r"(?<![\w\\])[A-Za-z]:[\\/]+(?:Users|home)\b|(?<![\w.~])/(?:Users|home)/[A-Za-z]")
NOTE = ("does", "reads", "look for")
SKIP = re.compile(r"changes|prerequisite", re.I)


def strip_sql(s):
    """Remove comments and string literals so keywords inside them do not count."""
    s = re.sub(r"--[^\n]*|/\*.*?\*/", " ", s, flags=re.S)
    return re.sub(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", "''", s, flags=re.S)


def bad_sql(text):
    for stmt in strip_sql(text).split(";"):
        if not stmt.strip():
            continue
        first = stmt.split()[0].lstrip("(").upper()
        if first not in READ:
            return f"not read-only: starts with {first}"
        if m := WRITE.search(re.sub(r"^\s*SHOW\s+CREATE\b", "SHOW", stmt, flags=re.I)):
            return f"not read-only: contains {m[1].upper()}"
    return None


def text(node):
    """String value of a literal; '+' joins and f-strings folded, '?' for each {...} or non-literal part."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(text(v) or "?" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = text(node.left), text(node.right)
        if a is not None or b is not None:
            return (a or "?") + (b or "?")
    return None


def looks_sql(s):
    body = re.sub(r"^(\s*--[^\n]*\n)+", "", s)
    return bool(WRITE_START.match(body) or (READ_START.match(body) and SQLISH.search(body.strip())))


def not_raw(py, node):
    """True if a string literal in node has a backslash in its source and no r prefix."""
    for n in ast.walk(node):
        if isinstance(n, (ast.Constant, ast.JoinedStr)):
            seg = ast.get_source_segment(py, n) or ""
            if "\\" in seg and not re.match(r"[fFbBuU]?[rR]|[rR][fFbB]", seg):
                return True
    return False


def sql_in_cell(src):
    """SQL texts in a code cell, and problems found while extracting them."""
    lines = src.splitlines()
    if lines and lines[0].lstrip().startswith("%%sql"):
        return ["\n".join(lines[1:])], []
    out = [line.split("%sql", 1)[1] for line in lines if line.lstrip().startswith("%sql")]
    issues = [f"Python table write: {m[0]}"] if (m := WRITE_PY.search(src)) else []
    py = "\n".join("" if line.lstrip().startswith(("%", "!")) else line for line in lines)  # keeps line numbers
    try:
        tree = ast.parse(py)
    except SyntaxError:
        found = re.findall(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'', py, re.S)
        return out + [a or b for a, b in found if looks_sql(a or b)], issues
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body and isinstance(n.body[0], ast.Expr)}
    done = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and node.args
                and getattr(node.func, "attr", getattr(node.func, "id", "")) in SQL_CALLS):
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Call) and getattr(arg.func, "attr", "") == "format":
            issues.append(FORMATTED)
        if (t := text(arg)) is None:
            continue
        out.append(t)
        done.update(id(n) for n in ast.walk(arg))
        if not isinstance(arg, ast.Constant):
            issues.append(FORMATTED)
        if not_raw(py, arg):
            issues.append(RAW)
    for node in ast.walk(tree):
        if id(node) in done or id(node) in docs or not isinstance(node, (ast.Constant, ast.JoinedStr, ast.BinOp)):
            continue
        if (t := text(node)) is not None and looks_sql(t):
            out.append(t)
            done.update(id(n) for n in ast.walk(node))
            if not_raw(py, node):
                issues.append(RAW)
    return out, issues


def text_checks(where, text, fails):
    if m := SECRET.search(text):
        fails.append(f"{where}: secret-like value '{m[0][:12]}...'")
    if m := MACHINE.search(text):
        fails.append(f"{where}: machine path '{m[0]}'")


def check_notebook(path, fails):
    cells = json.loads(path.read_text(encoding="utf-8")).get("cells", [])
    prev = None
    for i, cell in enumerate(cells, 1):
        src = "".join(cell.get("source", []))
        where = f"{path.as_posix()}#cell {i}"
        text_checks(where, src, fails)
        sqls, issues = sql_in_cell(src) if cell.get("cell_type") == "code" else ([], [])
        fails.extend(f"{where}: {x}" for x in dict.fromkeys(issues))
        if sqls:
            note = "".join(prev.get("source", [])).lower() if prev and prev.get("cell_type") == "markdown" else ""
            if missing := [k for k in NOTE if k not in note]:
                fails.append(f"{where}: query without a markdown note before it (missing: {', '.join(missing)})")
            for s in sqls:
                if reason := bad_sql(s):
                    fails.append(f"{where}: {reason}")
        if src.strip():
            prev = cell


def check_sql(path, fails):
    text = path.read_text(encoding="utf-8")
    header = re.match(r"(\s*--[^\n]*\n)*", text)[0].lower()
    if missing := [k for k in ("what:", "views:", "look for:") if k not in header]:
        fails.append(f"{path.as_posix()}: header missing {', '.join(missing)}")
    if reason := bad_sql(text):
        fails.append(f"{path.as_posix()}: {reason}")
    text_checks(path.as_posix(), text, fails)


def check_folder(folder, fails):
    nbs = [p for p in folder.glob("*.ipynb") if not SKIP.search(p.name)]
    if nbs and not (folder / "00_connection.ipynb").is_file():
        fails.append(f"{folder.as_posix()}: question notebooks without 00_connection.ipynb")
    for p in sorted(folder.rglob("*")):
        if SKIP.search(p.name) or any(part == "changes" or ".ipynb_checkpoints" in part for part in p.parts):
            continue
        if p.suffix == ".ipynb":
            check_notebook(p, fails)
        elif p.suffix == ".sql":
            check_sql(p, fails)


def main(args):
    fails = []
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            check_folder(p, fails)
        elif p.suffix == ".ipynb":
            check_notebook(p, fails)
        elif p.suffix == ".sql":
            check_sql(p, fails)
        else:
            fails.append(f"{a}: not a folder, .ipynb or .sql")
    for f in fails:
        print("FAIL", f)
    print(f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
