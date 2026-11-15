"""Planted-error test: the dbt skill's check_queries.py on the example's notebook. Usage: python run.py"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True   # no __pycache__ left in the skill folders
DBT = Path(__file__).resolve().parents[2] / "darshan-singh-meel-dbt"
sys.path.insert(0, str(DBT / "scripts"))
import check_queries  # noqa: E402

FAILS = []
MD = "### Step\n- **Grain:** one row = node × week\n- **Look for:** a large week-over-week rise"


def ok(cond, msg):
    if not cond:
        FAILS.append(msg)


def nb(path, cells):
    path.write_text(json.dumps({"cells": [{"cell_type": t, "metadata": {}, "source": s} for t, s in cells],
                                "metadata": {}, "nbformat": 4, "nbformat_minor": 5}), encoding="utf-8")


def main():
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copy(DBT / "references" / "templates" / "00_connection.ipynb", d / "00_connection.ipynb")
        nb(d / "01_cost_by_model_week.ipynb", [
            ("markdown", "# 01 Cost by model and week"), ("code", "%run ./00_connection.ipynb"),
            ("markdown", MD),
            ("code", 'df1 = q(r"""select node_id, sum(a.credits_used_compute) as credits from d\n'
                     'left join snowflake.account_usage.query_attribution_history a on a.query_id = d.query_id\n'
                     'group by 1""", as_of=AS_OF)'),
            ("markdown", MD),
            ("code", 'df2 = q(r"""select role_name, sum(a.credits_attributed_compute) from d\n'
                     'left join snowflake.account_usage.query_attribution_history a on a.warehouse_name = d.warehouse_name\n'
                     'group by 1""", as_of=AS_OF)'),
            ("code", 'stmt = "create or replace table analytics.scratch.cost_wk as select 1"\nq(stmt)'),
        ])
        e = "\n".join(check_queries.check(d))
        ok("cell 7: SQL passed to q() through a variable" in e, f"variable-passed write not flagged: {e}")
        ok("cell 7: not read-only: create" in e, f"write literal not flagged: {e}")
        ok("cell 7: query without a markdown cell" in e, f"missing markdown not flagged: {e}")
        ok("cell 4:" not in e and "cell 6:" not in e and "00_connection" not in e,
           f"wrong column and fan-out are reader findings, not script errors: {e}")
    finally:
        shutil.rmtree(d)
    for f in FAILS:
        print("FAIL", f)
    print(f"{len(FAILS)} FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
