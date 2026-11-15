"""Tests for scripts/check_queries.py: the shipped example and templates pass, each planted fault fails.
Usage: python run.py"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
CHECK = SKILL / "scripts" / "check_queries.py"
EXAMPLE = SKILL / "references" / "examples" / "cost-jump"
TEMPLATES = SKILL / "references" / "templates"
NOTE = "### N. Title\n- **What:** x.\n- **Reads:** QUERY_HISTORY.\n- **Look for:** y."
HEADER = "-- 01. Title\n-- What: x.\n-- Reads: QUERY_HISTORY.\n-- Look for: y.\n"


def run(folder):
    r = subprocess.run([sys.executable, str(CHECK), str(folder)], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def copy_example():
    d = Path(tempfile.mkdtemp()) / "topic"
    shutil.copytree(EXAMPLE, d)
    return d


def edit_nb(path, fn):
    nb = json.loads(path.read_text(encoding="utf-8"))
    fn(nb["cells"])
    path.write_text(json.dumps(nb), encoding="utf-8")


def add_query(cells, sql, note=True):
    if note:
        cells.append({"cell_type": "markdown", "metadata": {}, "source": NOTE})
    cells.append({"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None,
                  "source": f'q("""{sql}""")'})


def case(name, setup, expect_fail, needle=""):
    d = copy_example()
    setup(d)
    code, out = run(d)
    shutil.rmtree(d.parent, ignore_errors=True)
    ok = (code != 0) == expect_fail and needle in out
    print(("PASS" if ok else "FAIL"), name, "" if ok else "\n" + out)
    return ok


def nb1(d):
    return d / "01_cost_jump.ipynb"


CASES = [
    ("example passes", lambda d: None, False),
    ("missing 00_connection", lambda d: (d / "00_connection.ipynb").unlink(), True, "00_connection.ipynb missing"),
    ("query without note", lambda d: edit_nb(nb1(d), lambda c: add_query(c, "SELECT 1", note=False)), True,
     "without a markdown note"),
    ("note missing Look for", lambda d: edit_nb(nb1(d), lambda c: c.__setitem__(2, {**c[2], "source": "### 1.\n- **What:** x\n- **Reads:** y"})),
     True, "without a markdown note"),
    ("DELETE in a notebook", lambda d: edit_nb(nb1(d), lambda c: add_query(c, "DELETE FROM t WHERE 1 = 1")), True, "not read-only"),
    ("comment-first DELETE", lambda d: edit_nb(nb1(d), lambda c: add_query(c, "-- cleanup\nDELETE FROM db.s.t")), True,
     "not read-only"),
    ("comment-first SELECT without note", lambda d: edit_nb(nb1(d), lambda c: add_query(
        c, "/* check */ SELECT 1", note=False)), True, "without a markdown note"),
    ("QUERY_TEXT selected warns", lambda d: edit_nb(nb1(d), lambda c: add_query(
        c, "SELECT query_id, query_text FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY")), False, "WARN 01_cost_jump.ipynb"),
    ("two SQL strings in one cell warn", lambda d: edit_nb(nb1(d), lambda c: c.extend([
        {"cell_type": "markdown", "metadata": {}, "source": NOTE},
        {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None,
         "source": 'a = q("""SELECT 1""")\nb = q("""SELECT 2""")'}])), False, "2 SQL strings"),
    ("write hidden after SELECT", lambda d: edit_nb(nb1(d), lambda c: add_query(c, "SELECT 1; DROP TABLE t")), True,
     "not read-only"),
    ("SYSTEM$ in a normal notebook", lambda d: edit_nb(nb1(d), lambda c: add_query(
        c, "SELECT SYSTEM$CLUSTERING_INFORMATION('db.s.t', '(d)')")), True, "SYSTEM$"),
    ("SYSTEM$ in a user notebook", lambda d: (shutil.copy(nb1(d), d / "90_user_clustering.ipynb"), edit_nb(
        d / "90_user_clustering.ipynb", lambda c: add_query(c, "SELECT SYSTEM$CLUSTERING_INFORMATION('db.s.t', '(d)')"))),
     False),
    ("literals and comments ignored", lambda d: edit_nb(nb1(d), lambda c: add_query(
        c, "SELECT 'DROP TABLE x' AS s, deleted, created -- delete later\nFROM SNOWFLAKE.ACCOUNT_USAGE.TABLES")), False),
    ("setup cell differs", lambda d: edit_nb(nb1(d), lambda c: c.__setitem__(1, {**c[1], "source": "import os\nconn = None"})),
     True, "not the connection cell"),
    ("secret literal", lambda d: edit_nb(d / "00_connection.ipynb", lambda c: c.__setitem__(
        1, {**c[1], "source": "".join(c[1]["source"]) + '\npassword = "hunter22"'})), True, "secret literal"),
    ("machine path", lambda d: edit_nb(nb1(d), lambda c: c.append(
        {"cell_type": "markdown", "metadata": {}, "source": "data in " + "C:" + "\\Users\\someone\\x"})), True,
     "machine path"),
    ("sql file with headers passes", lambda d: ((d / "sql").mkdir(), (d / "sql" / "01_q.sql").write_text(
        HEADER + "SELECT 1;\n" + HEADER + "SHOW WAREHOUSES;\n", encoding="utf-8")), False),
    ("sql statement without header", lambda d: ((d / "sql").mkdir(), (d / "sql" / "01_q.sql").write_text(
        HEADER + "SELECT 1;\nSELECT 2;\n", encoding="utf-8")), True, "statement 2: no header"),
    ("ALTER SESSION in a sql file", lambda d: ((d / "sql").mkdir(), (d / "sql" / "01_q.sql").write_text(
        HEADER + "ALTER SESSION SET TIMEZONE = 'UTC';\n", encoding="utf-8")), True, "not read-only"),
    ("CALL in a user sql file", lambda d: ((d / "sql").mkdir(), (d / "sql" / "90_user_budget.sql").write_text(
        HEADER + "CALL SNOWFLAKE.LOCAL.ACCOUNT_ROOT_BUDGET!GET_SPENDING_HISTORY();\n", encoding="utf-8")), False),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    results = [case(*c) for c in CASES]
    code, out = run(TEMPLATES)
    results.append(code == 0)
    print(("PASS" if code == 0 else "FAIL"), "templates pass", "" if code == 0 else "\n" + out)
    print(f"{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


main()
