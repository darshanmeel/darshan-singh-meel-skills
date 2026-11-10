"""Run selected cells of a Jupyter notebook, read-only only. Outputs are saved into the notebook.

Usage: python run_cells.py [--summary-only] <notebook.ipynb> <cell numbers, 1-based, e.g. 1 4 5>
Code cells tagged 'setup' (connection, imports) before them run first and are checked the same way.
--summary-only (sensitive data): also runs the cell tagged 'share' and prints only its text output;
failed cells show the error name only (messages can echo values).
Refuses the whole run if a cell, a file it names, or any sql/*.sql beside the notebook holds a
statement other than SELECT / WITH / SHOW / DESCRIBE / EXPLAIN, a dataframe, table or file write, exec/eval,
a shell command, or a magic other than %sql/%time/%timeit/%matplotlib/%load_ext/%capture. Best-effort check: the read-only role is the guarantee. Exits 1 if a cell fails.
"""
import ast
import re
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

READ = {"select", "with", "show", "describe", "desc", "explain"}
WRITE_SQL = re.compile(
    r"\b(insert|update|delete|merge|copy|truncate|create|alter|drop|grant|revoke|call|into)\b|system\$", re.I
)
# A string counts as SQL if a statement starts with a read verb, or with a write verb plus its usual next word.
OBJ = (r"(table|view|schema|database|warehouse|role|user|stage|function|procedure|task|stream|pipe|sequence"
       r"|index|tag|policy|share|integration|catalog|volume|file\s+format|materialized\s+view)\b")
SQL_START = re.compile(
    r"[(\s]*((select|with|show|describe|desc|explain)\s+\S|insert\s+(into|overwrite)|update\s+\S+\s+set\b"
    r"|delete\s+from|(merge|copy|replace)\s+into|copy\s+\S+\s+(from|to)\b|truncate\s+(table\s+)?[\w.\"`]+\s*$"
    r"|(create|alter|drop|undrop|comment\s+on)\s+(or\s+replace\s+|if\s+(not\s+)?exists\s+|\w+\s+){0,3}" + OBJ +
    r"|(grant|revoke)\s+(.+\s)?(on|role)\s|(call|exec|execute)\s+[\w.]+\s*\(|execute\s+immediate"
    r"|use\s+((role|warehouse|database|schema|catalog)\s+)?[\w.\"]+\s*$|put\s+file:|get\s+@|(remove|rm)\s+@"
    r"|load\s+data|unload\s*\(|(refresh|msck|analyze|cache|uncache|restore)\s+table|(optimize|vacuum)\s+[\w.`]+"
    r"|(begin|commit|rollback|start\s+transaction)\s*\w*\s*$|(set|unset)\s+\w+\s*=)",
    re.I,
)
MAGICS = "sql|time|timeit|matplotlib|load_ext|capture"  # any other % / %% magic and ! are refused
WRITE_PY = re.compile(
    r"\.write(Stream)?\b(?!\s*\()|\.writeTo\b|\.write_\w+\(|\.sink_\w+\(|save_?as_?table|insertInto|\bto_sql\b"
    r"|write_pandas|copy_into|create_or_replace|\.to_(csv|parquet|sql|table|excel|json|pickle|feather|hdf|orc|xml)\b"
    r"|\bdbt\s+(run|build|seed|snapshot|test|run-operation)|dbtRunner|subprocess|\bshutil\b|get_ipython"
    r"|\bos\.(system|popen|remove|unlink|rename|replace|rmdir|removedirs|truncate|write|kill|spawn|exec)"
    r"|\.(unlink|rmdir|touch)\(|\.call(proc)?\(|\.table\([^)]*\)\.(delete|update|merge)\(|\bDeltaTable\b"
    r"|(?<![.\w])(exec|eval|compile|__import__)\s*\(|\b(importlib|builtins)\b|__doc__"
    r"|^\s*%%?sql\b.*--(persist|append)|^\s*(!|%%?(?!(" + MAGICS + r")\b)\w)",
    re.I | re.M,
)
SQL_CALLS = {"execute", "executemany", "executescript", "execute_string", "execute_async", "sql", "read_sql",
             "read_sql_query"}


def statements(sql, backslash=True):
    """Split SQL on ';' outside literals; comments dropped, literal contents blanked."""
    out, cur, i, n = [], [], 0, len(sql)
    while i < n:
        c, two = sql[i], sql[i : i + 2]
        if two in ("--", "//"):
            j = sql.find("\n", i)
            j = n if j < 0 else j
            # Some dialects read -- / // as operators: if the "comment" could hide a statement, keep it as code.
            if ";" in sql[i:j] or WRITE_SQL.search(sql[i:j]):
                cur.append(c)
                i += 1
            else:
                i = j
        elif two == "/*" or two == "$$" or c in "'\"`":
            end = {"/*": "*/", "$$": "$$"}.get(two, c)
            j = i + len(end) if two in ("/*", "$$") else i + 1
            while j < n and not sql.startswith(end, j):
                j += 2 if backslash and sql[j] == "\\" else 1
            if j >= n:  # unterminated: keep the raw rest so nothing hides behind it
                cur.append(sql[i:])
                break
            cur.append(" " if two == "/*" else "''")
            i = j + len(end)
        elif c == ";":
            out.append("".join(cur))
            cur, i = [], i + 1
        else:
            cur.append(c)
            i += 1
    out.append("".join(cur))
    return [s.strip() for s in out if s.strip()]


def both(sql):
    """Statements read with and without backslash escapes (dialects differ), so neither reading hides one."""
    return statements(sql) + statements(sql, backslash=False)


def bad_sql(sql):
    for s in both(sql):
        first = re.match(r"[(\s]*(\w+)", s)
        if not first or first.group(1).lower() not in READ:
            return s[:60]
        hit = WRITE_SQL.search(re.sub(r"^[(\s]*show\s+create\b", "show", s, flags=re.I))
        if hit:
            return hit.group(0)


def looks_sql(s):
    return any(SQL_START.match(st) for st in both(s))


def read_sql_file(f):
    return f.read_text(encoding="utf-8-sig", errors="replace")


def text(node):
    """String value of a literal; '+' joins and f-strings folded, '?' for each {…}."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value if isinstance(node.value, str) else node.value.decode("utf-8", "replace")
    if isinstance(node, ast.JoinedStr):
        return "".join(text(v) or "?" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = text(node.left), text(node.right)
        if a is not None and b is not None:
            return a + b


def named_file(s, nb_dir):
    """SQL in a file the string names: any .sql file, or a small other file whose text looks like SQL."""
    try:
        f = nb_dir / s.strip()
        if not f.is_file():
            return None
        if f.suffix.lower() == ".sql":
            return read_sql_file(f)
        if f.stat().st_size <= 1_000_000 and looks_sql(t := read_sql_file(f)):
            return t
    except (OSError, ValueError):
        return None


def write_mode(node):
    """open(..., 'w'/'a'/'x'/'+') or Path.open('w'): a file write."""
    if not isinstance(node, ast.Call) or getattr(node.func, "attr", getattr(node.func, "id", "")) != "open":
        return False
    args = node.args[1:] if isinstance(node.func, ast.Name) else node.args
    modes = [text(a) for a in args + [k.value for k in node.keywords if k.arg == "mode"]]
    return any(m and set(m) <= set("rwabtx+") and set(m) & set("wax+") for m in modes)


def sql_in_cell(src, nb_dir):
    """SQL texts in a cell: %%sql / %sql bodies, SQL-like strings, execute()/sql() args, files they name."""
    lines = src.splitlines()
    if lines and (m := re.match(r"\s*%%sql\b(.*)", lines[0])):
        body = "\n".join(lines[1:])
        # The magic line may hold connection or option text; check it only if it could hold a statement.
        sql = [m.group(1), body] if looks_sql(m.group(1)) or WRITE_SQL.search(m.group(1)) else [body]
        return sql + [t for f in re.findall(r"[\w./\\-]+\.sql\b", src) if (t := named_file(f, nb_dir))]
    sql = [m.group(1) for line in lines if (m := re.match(r"\s*%sql\b(.*)", line))]
    sql += [t for s in sql for f in re.findall(r"[\w./\\-]+\.sql\b", s) if (t := named_file(f, nb_dir))]
    py = "\n".join("" if re.match(r"\s*%{1,2}[A-Za-z]", line) else line for line in lines)
    tree = ast.parse(py)
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    for node in ast.walk(tree):
        if write_mode(node):
            sql.append("open(..., 'w')")
        if isinstance(node, ast.Call) and node.args:
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if name in SQL_CALLS and (t := text(node.args[0])) is not None:
                sql.append(t)
        s = text(node)
        if s is None or id(node) in docs:
            continue
        if (t := named_file(s, nb_dir)) is not None:
            sql.append(t)
        elif looks_sql(s):
            sql.append(s)
    return sql


def refusal(src, nb_dir):
    hit = WRITE_PY.search(src)
    if hit:
        return hit.group(0).strip()
    try:
        texts = sql_in_cell(src, nb_dir)
    except SyntaxError:
        return "code that cannot be parsed"
    for t in texts:
        if bad := bad_sql(t):
            return bad


def main(path, wanted, summary=False):
    nb = nbformat.read(path, as_version=4)
    nb_dir = Path(path).resolve().parent
    if not all(1 <= n <= len(nb.cells) for n in wanted):
        sys.exit(f"cell numbers must be 1-{len(nb.cells)}")
    setup = tagged(nb, "setup")
    share = tagged(nb, "share") if summary else set()
    if summary and not share:
        sys.exit("--summary-only needs the Share with Claude cell tagged 'share'")
    last = max(set(wanted) | share)
    to_run = sorted(set(wanted) | share | {i for i in setup if i < last})
    for f in sorted(nb_dir.glob("sql/**/*.sql")):
        if bad := bad_sql(read_sql_file(f)):
            sys.exit(f"REFUSED: {f.relative_to(nb_dir)} contains '{bad}' — sql/ files are SELECT-only.")
    for n in to_run:
        cell = nb.cells[n - 1]
        if cell.cell_type != "code":
            sys.exit(f"cell {n} is not a code cell")
        if bad := refusal(cell.source, nb_dir):
            sys.exit(f"REFUSED: cell {n} contains '{bad}' — only SELECT/SHOW/DESCRIBE/EXPLAIN may run. "
                     "Move it to the changes or prerequisite_ddl notebook for the user to run.")
    client = NotebookClient(nb, timeout=600, allow_errors=True, resources={"metadata": {"path": str(nb_dir)}})
    failed, ran = [], set()
    with client.setup_kernel():
        for n in to_run:
            client.execute_cell(nb.cells[n - 1], n - 1)
            ran.add(n)
            err = next((o for o in nb.cells[n - 1].outputs if o.output_type == "error"), None)
            if err:
                failed.append(f"cell {n} failed: {err.ename}")
                if n in setup:
                    failed.append("setup cell failed — later cells not run")
                    break
    nbformat.write(nb, path)
    print(f"ran cells {to_run}; outputs saved to {path}")
    if summary:
        print("--- Share with Claude (only output shown; do not open the notebook) ---")
        # Only this call's share output: a cell skipped after a setup failure still holds an earlier run's text.
        print(share_text(nb, share) if share <= ran else "(share cell not run in this call — no summary)")
    if failed:
        sys.exit("\n".join(failed))


def share_text(nb, cells):
    """Text output of the given cells only: stdout and text/plain results; errors, stderr, images left out."""
    out = []
    for n in sorted(cells):
        for o in nb.cells[n - 1].get("outputs", []):
            if o.get("output_type") == "stream" and o.get("name") == "stdout":
                out.append(o.get("text", ""))
            elif o.get("output_type") in ("execute_result", "display_data"):
                out.append(o.get("data", {}).get("text/plain", ""))
    return "".join(t if t.endswith("\n") else t + "\n" for t in out if t).rstrip("\n")


def tagged(nb, tag):
    """Code cells with this tag: 'setup' (connection, imports) runs first; 'share' = the Share with Claude cell."""
    return {i for i, c in enumerate(nb.cells, 1)
            if c.cell_type == "code" and tag in c.get("metadata", {}).get("tags", [])}


if __name__ == "__main__":
    args = sys.argv[1:]
    summary = "--summary-only" in args
    args = [a for a in args if a != "--summary-only"]
    if len(args) < 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main(args[0], [int(x) for x in args[1:]], summary)
