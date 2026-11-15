"""Tests for scripts/check_queries.py. Usage: python tests/run.py (from the skill folder or anywhere)."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

SKILL = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "check_queries.py"
TEMPLATES = SKILL / "references" / "templates"


def run(*paths):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, paths)], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def nb(cells):
    return {"cells": [{"cell_type": t, "metadata": {}, "source": s, **({"outputs": [], "execution_count": None} if t == "code" else {})}
                      for t, s in cells], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}


NOTE = "**Does:** x\n**Reads:** y\n**Look for:** z"
GOOD_Q = 'q("""\nSELECT 1 AS one FROM system.billing.usage\n""")'


def case(tmp, name, files):
    d = tmp / name
    d.mkdir()
    for rel, content in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(content) if rel.endswith(".ipynb") else content, encoding="utf-8")
    return d


def main():
    tmp = pathlib.Path(tempfile.mkdtemp())
    results = []

    def expect(label, path, code, needle=None):
        rc, out = run(path)
        ok = rc == code and (needle is None or needle in out)
        results.append(ok)
        print("PASS" if ok else "FAIL", label, "" if ok else out)

    good = tmp / "templates"
    shutil.copytree(TEMPLATES, good)
    expect("templates pass", good, 0)
    conn = json.loads((TEMPLATES / "00_connection.ipynb").read_text(encoding="utf-8"))

    d = case(tmp, "no_connection", {"01_q.ipynb": nb([("markdown", NOTE), ("code", GOOD_Q)])})
    expect("missing 00_connection", d, 1, "without 00_connection")

    d = case(tmp, "no_note", {"00_connection.ipynb": conn, "01_q.ipynb": nb([("code", "x = 1"), ("code", GOOD_Q)])})
    expect("query without markdown note", d, 1, "without a markdown note")

    d = case(tmp, "partial_note", {"00_connection.ipynb": conn,
                                   "01_q.ipynb": nb([("markdown", "**Does:** x"), ("code", GOOD_Q)])})
    expect("note missing Reads / Look for", d, 1, "missing: reads, look for")

    d = case(tmp, "write", {"00_connection.ipynb": conn, "01_q.ipynb": nb([("markdown", NOTE),
             ("code", 'q("""\nDELETE FROM main.s.t WHERE id = 1\n""")')])})
    expect("DELETE refused", d, 1, "starts with DELETE")

    d = case(tmp, "cte_write", {"00_connection.ipynb": conn, "01_q.ipynb": nb([("markdown", NOTE),
             ("code", 'q("""\nWITH a AS (SELECT 1) INSERT INTO main.s.t SELECT * FROM a\n""")')])})
    expect("WITH ... INSERT refused", d, 1, "contains INSERT")

    d = case(tmp, "magic", {"00_connection.ipynb": conn, "01_q.ipynb": nb([("markdown", NOTE),
             ("code", "%%sql\nOPTIMIZE main.s.t")])})
    expect("%%sql OPTIMIZE refused", d, 1, "starts with OPTIMIZE")

    d = case(tmp, "keyword_in_string", {"00_connection.ipynb": conn, "01_q.ipynb": nb([("markdown", NOTE),
             ("code", 'q("""\nSELECT delete_time, update_time FROM system.compute.clusters '
                      "WHERE operation_type = 'VACUUM' -- DROP in a comment\n\"\"\")")])})
    expect("keywords in names, strings, comments allowed", d, 0)

    one_liners = {
        "q one-line OPTIMIZE": ('q("OPTIMIZE cat.s.t")', "starts with OPTIMIZE"),
        "q one-line VACUUM": ('q("VACUUM cat.s.t")', "starts with VACUUM"),
        "q f-string OPTIMIZE": ('TABLE = "cat.s.t"\nq(f"OPTIMIZE {TABLE}")', "starts with OPTIMIZE"),
        "q '+' OPTIMIZE": ('TABLE = "cat.s.t"\nq("OPTIMIZE " + TABLE)', "starts with OPTIMIZE"),
        "spark.sql DROP VIEW": ('spark.sql("DROP VIEW cat.s.v")', "starts with DROP"),
        "saveAsTable": ('spark.table("cat.s.t").write.saveAsTable("x")', "Python table write"),
        "second q in a cell": (GOOD_Q + '\nq("OPTIMIZE cat.s.t ZORDER BY (a)")', "starts with OPTIMIZE"),
        "f-string SQL": ('T = "x"\nq(f"SELECT a FROM {T}")', "string formatting"),
        "backslash in non-raw string": ('q("""\nSELECT regexp_extract(a, \'\\\\d+\') AS n FROM system.billing.usage\n""")',
                                        "non-raw"),
    }
    for label, (code, needle) in one_liners.items():
        d = case(tmp, label.replace(" ", "_").replace("'", "").replace("+", "plus"),
                 {"00_connection.ipynb": conn, "01_q.ipynb": nb([("markdown", NOTE), ("code", code)])})
        expect(label + " refused", d, 1, needle)

    d = case(tmp, "allowed", {"00_connection.ipynb": conn, "01_q.ipynb": nb([
        ("markdown", NOTE), ("code", 'q("SHOW CREATE TABLE cat.s.t")'),
        ("markdown", NOTE), ("code", 'q(r"""\nSELECT regexp_extract(a, \'\\\\d+\') AS n FROM system.billing.usage\n""")'),
        ("code", 'print("Update the note before sharing")')])})
    expect("SHOW CREATE, raw regex string and prose allowed", d, 0)

    d = case(tmp, "secret", {"00_connection.ipynb": conn,
             "01_q.ipynb": nb([("code", 'token = "' + "dapi" + "0" * 32 + '"')])})
    expect("token literal flagged", d, 1, "secret-like")

    d = case(tmp, "path", {"00_connection.ipynb": conn,
             "01_q.ipynb": nb([("markdown", "Saved under C:" + "\\Users\\someone\\x")])})
    expect("machine path flagged", d, 1, "machine path")

    d = case(tmp, "sql_header", {"sql/01_x.sql": "-- what: x\nSELECT 1;\n"})
    expect(".sql header missing views / look for", d, 1, "header missing views:, look for:")

    d = case(tmp, "sql_write", {"sql/01_x.sql": "-- what: x\n-- views: v\n-- look for: z\nGRANT SELECT ON t TO x;\n"})
    expect(".sql GRANT refused", d, 1, "starts with GRANT")

    d = case(tmp, "changes_skipped", {"00_connection.ipynb": conn, "topic-changes.ipynb": nb([("code", '%%sql\nOPTIMIZE main.s.t')]),
             "changes/01_fix.sql": "OPTIMIZE main.s.t;\n"})
    expect("changes notebook and folder skipped", d, 0)

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"{results.count(True)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


main()
