"""Tests for dbt_inventory.py and check_queries.py on synthetic inputs. Usage: python run.py"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True   # no scripts/__pycache__ left in the skill folder
SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import check_queries  # noqa: E402
import dbt_inventory as inv  # noqa: E402

FAILS = []


def ok(cond, msg):
    if not cond:
        FAILS.append(msg)


def node(uid, rtype, path, deps=(), config=None, raw="", **kw):
    name = uid.split(".")[2]
    return uid, {"unique_id": uid, "name": name, "resource_type": rtype, "package_name": "shop",
                 "original_file_path": path, "depends_on": {"nodes": list(deps), "macros": kw.pop("macros", [])},
                 "config": {"materialized": "view", **(config or {})}, "raw_code": raw,
                 "relation_name": f'"ANALYTICS"."MARTS"."{name.upper()}"', **kw}


def maps(nodes):
    child = {k: [] for k in nodes}
    for k, n in nodes.items():
        for p in n["depends_on"]["nodes"]:
            child.setdefault(p, []).append(k)
    return child, {k: n["depends_on"]["nodes"] for k, n in nodes.items()}


def manifest():
    nodes = dict([
        node("model.shop.stg_erp__orders", "model", "models/staging/erp/stg_erp__orders.sql", ["source.shop.erp.orders"],
             description="One row per order."),
        node("model.shop.dim_customer", "model", "models/marts/dim_customer.sql", ["source.shop.erp.customers"],
             {"materialized": "table"}, access="public", description="One row per customer.", group="sales"),
        node("model.shop.fct_orders", "model", "models/marts/fct_orders.sql",
             ["model.shop.stg_erp__orders", "model.shop.dim_customer"], {"materialized": "incremental"},
             raw="select o.* from {{ ref('stg_erp__orders') }} o\nleft join {{ ref('dim_customer') }} c\n  on c.customer_id = o.customer_id\nwhere o.amount > 0",
             macros=["macro.shop.cents"]),
        node("model.shop.rpt_legacy", "model", "models/marts/rpt_legacy.sql", ["model.shop.fct_orders"],
             raw="{% set r = run_query('select 1') %} select * from raw.erp.orders"),
        node("test.shop.unique_fct_orders_order_id", "test", "models/marts/_models.yml", ["model.shop.fct_orders"],
             {"severity": "warn"}, test_metadata={"name": "unique"}),
        node("snapshot.shop.customers_snapshot", "snapshot", "snapshots/s.yml", ["source.shop.erp.customers"],
             {"invalidate_hard_deletes": True}),
        node("seed.shop.country_codes", "seed", "seeds/country_codes.csv"),
    ])
    child, parent = maps(nodes)
    return {"metadata": {"project_name": "shop"}, "nodes": nodes, "child_map": child, "parent_map": parent,
            "sources": {"source.shop.erp.orders": {"source_name": "erp", "name": "orders",
                                                   "freshness": {"warn_after": {"count": 6, "period": "hour"}}},
                        "source.shop.erp.customers": {"source_name": "erp", "name": "customers", "freshness": None}},
            "exposures": {}, "macros": {
                "macro.shop.cents": {"name": "cents", "package_name": "shop", "depends_on": {"macros": []}},
                "macro.shop.old_helper": {"name": "old_helper", "package_name": "shop", "depends_on": {"macros": []}}}}


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        res = fn(*a)
    return res, out.getvalue()


def test_inventory():
    m = manifest()
    r, text = quiet(inv.health, m)
    ok(r["untested_models"] == ["stg_erp__orders", "dim_customer", "rpt_legacy"] or
       sorted(r["untested_models"]) == ["dim_customer", "rpt_legacy", "stg_erp__orders"], f"untested {r['untested_models']}")
    ok("fct_orders" not in r["no_pk_test"], "unique test counts as pk test")
    ok(r["sources_without_freshness"] == ["erp.customers"], f"freshness {r['sources_without_freshness']}")
    ok(r["source_outside_staging"] == ["dim_customer"], f"layering {r['source_outside_staging']}")
    ok(r["orphan_models"] == ["rpt_legacy"], f"orphans {r['orphan_models']}")
    ok(r["incremental_no_unique_key"] == ["fct_orders"], "incremental unique_key")
    ok(r["incremental_no_on_schema_change"] == ["fct_orders"], "on_schema_change")
    ok(r["public_no_contract"] == ["dim_customer"], "public contract")
    ok(r["hardcoded_relations"] == ["rpt_legacy"], f"hardcoded {r['hardcoded_relations']}")
    ok(r["introspective_macros"] == ["rpt_legacy"], "introspective")
    ok(r["warn_tests"] == ["unique_fct_orders_order_id"], "warn tests")
    ok(len(r["deprecated_configs"]) == 1, "deprecated snapshot config")
    ok(r["seeds_without_column_types"] == ["country_codes"], "seed types")
    ok(sorted(r["no_group"]) == ["fct_orders", "rpt_legacy"], f"no_group {r['no_group']}")
    ok("select" not in text.lower(), "health never prints code")

    out, _ = quiet(inv.impact, m, "dim_customer")
    ok([n for _, n in out] == ["model.shop.fct_orders", "model.shop.rpt_legacy", "test.shop.unique_fct_orders_order_id"]
       or {n for _, n in out} == {"model.shop.fct_orders", "model.shop.rpt_legacy", "test.shop.unique_fct_orders_order_id"},
       f"impact {out}")
    ok(dict((n, d) for d, n in out)["model.shop.rpt_legacy"] == 2, "impact depth")
    up, _ = quiet(inv.upstream, m, "fct_orders")
    ok({n for _, n in up} >= {"source.shop.erp.orders", "source.shop.erp.customers"}, f"upstream {up}")
    j, _ = quiet(inv.joins, m, "dim_customer")
    ok(j == [("fct_orders", "c", "c.customer_id = o.customer_id")], f"joins {j}")
    rel, _ = quiet(inv.relations, m, "models/marts")
    ok("analytics.marts.dim_customer" in rel and "analytics.marts.stg_erp__orders" not in rel, f"relations {rel}")
    mac, _ = quiet(inv.unused_macros, m)
    ok(mac == ["macro.shop.old_helper"], f"macros {mac}")
    users, _ = quiet(inv.macro_users, m, "cents")
    ok(users == ["model.shop.fct_orders"], f"macro users {users}")

    rr = {"elapsed_time": 12.0, "results": [
        {"unique_id": "model.shop.fct_orders", "status": "success", "execution_time": 9.5, "failures": None,
         "compiled_code": "select secret_value", "timing": []},
        {"unique_id": "test.shop.unique_fct_orders_order_id", "status": "fail", "execution_time": 1.2, "failures": 3,
         "timing": []}]}
    rows, text = quiet(inv.timing, rr, None, 20)
    ok(rows[0][1] == "model.shop.fct_orders" and "errors: 1" in text, "timing order and errors")
    ok("secret_value" not in text, "timing never prints compiled code")
    rows, _ = quiet(inv.timing, rr, "test", 20)
    ok(len(rows) == 1, "timing --type filter")
    rr["results"][0]["timing"] = [{"name": "execute", "started_at": "2026-01-01T02:00:00Z"}]
    rr["results"][1]["timing"] = [{"name": "execute", "started_at": "2026-01-01T01:00:00Z"}]
    rows, text = quiet(inv.timing, rr, None, 20, "started")
    ok(rows[0][1] == "test.shop.unique_fct_orders_order_id" and "2026-01-01T01:00:00" in text, f"timing --order started {rows}")
    ok(quiet(inv.health, m, {"unique_grain"})[0]["no_pk_test"].count("fct_orders") == 1, "--pk-tests replaces the default set")


def test_joins_and_columns():
    m = manifest()
    dim = "model.shop.dim_customer"
    extra = dict([
        node("model.shop.m_lower", "model", "models/marts/m_lower.sql", ["model.shop.fct_orders", dim],
             raw="select x.* from (select o.order_id from {{ ref('fct_orders') }} o\n"
                 "  join {{ ref('dim_customer') }} c on lower(o.customer_id) = lower(c.customer_id)) x"),
        node("model.shop.m_using", "model", "models/marts/m_using.sql", ["model.shop.fct_orders", dim],
             raw="select segment from {{ ref('fct_orders') }} join {{ ref('dim_customer') }} using (customer_id)"),
        node("model.shop.m_from", "model", "models/marts/m_from.sql", ["model.shop.fct_orders", dim],
             raw="select c.segment from {{ ref('dim_customer') }} c\njoin {{ ref('fct_orders') }} o on o.customer_id = c.customer_id\ngroup by 1"),
        node("model.shop.m_macro", "model", "models/marts/m_macro.sql", [dim],
             raw="{{ join_customers(ref('dim_customer')) }}"),
        node("test.shop.not_null_dim_customer_segment", "test", "models/marts/_models.yml", [dim],
             test_metadata={"name": "not_null"}, column_name="segment"),
    ])
    m["nodes"].update(extra)
    m["child_map"], m["parent_map"] = maps(m["nodes"])
    j, _ = quiet(inv.joins, m, "dim_customer")
    ok(("fct_orders", "c", "c.customer_id = o.customer_id") in j, f"joins plain {j}")
    ok(("m_lower", "c", "lower(o.customer_id) = lower(c.customer_id)") in j, f"joins with functions {j}")
    ok(("m_using", "dim_customer", "using (customer_id)") in j, f"joins using {j}")
    ok(("m_from", "c", "o.customer_id = c.customer_id") in j, f"target on the from side {j}")
    ok(("m_macro", "", "depends on dim_customer but no join parsed") in j, f"unparsed child listed {j}")
    cu, _ = quiet(inv.column_users, m, "dim_customer", "segment")
    ok(("m_using", "uses the column") in cu and ("m_from", "uses the column") in cu, f"column users {cu}")
    ok(("fct_orders", "select * (passes it on)") in cu and ("not_null_dim_customer_segment", "test on the column") in cu,
       f"column pass-through and test {cu}")
    ok(("m_lower", "select * (passes it on)") in cu, f"x.* pass-through {cu}")


def nb(path, cells):
    path.write_text(json.dumps({"cells": [{"cell_type": t, "metadata": {}, "source": s} for t, s in cells],
                                "metadata": {}, "nbformat": 4, "nbformat_minor": 5}), encoding="utf-8")


def test_check_queries():
    tpl = SKILL / "references" / "templates"
    d = Path(tempfile.mkdtemp())
    try:
        good = d / "good"
        (good / "sql").mkdir(parents=True)
        for f in ("00_connection.ipynb", "01_question.ipynb"):
            shutil.copy(tpl / f, good / f)
        shutil.copy(tpl / "query.sql", good / "sql" / "01_dbt_queries.sql")
        ok(check_queries.check(good) == [], f"templates should pass: {check_queries.check(good)}")

        bad = d / "bad"
        (bad / "sql").mkdir(parents=True)
        nb(bad / "01_q.ipynb", [("code", "%%sql\nselect 1"),
                               ("markdown", "What: cleanup"), ("code", 'q("delete from analytics.marts.t")'),
                               ("markdown", "x"), ("code", 'q("""with a as (select 1) insert into t select * from a""")'),
                               ("markdown", "x"), ("code", 'password = "hunter2hunter2"')])
        (bad / "sql" / "01_x.sql").write_text("select system$clustering_information('t');\n", encoding="utf-8")
        (bad / "sql" / "02_y.sql").write_text("-- what: x\n-- reads: y\n-- look for: z\n-- from C:\\Users\\someone\\x\ncall p();\n",
                                              encoding="utf-8")
        e = "\n".join(check_queries.check(bad))
        ok("00_connection.ipynb missing" in e, "missing connection notebook")
        ok("cell 1: query without a markdown" in e, "md before query")
        ok("not read-only: delete" in e, "delete caught")
        ok("not read-only: with a as" in e, "write inside WITH caught")
        ok("secret-looking literal" in e, "secret caught")
        ok("01_x.sql: header missing" in e and "01_x.sql: not read-only: select system$" in e, "system$ and header")
        ok("02_y.sql: absolute machine path" in e and "02_y.sql: not read-only: call" in e, "path and call")
        ok("02_y.sql: header missing" not in e, "complete header accepted")

        md = "x\n- **Grain:** one row = node\n- **Look for:** y"
        tricky = d / "tricky"
        tricky.mkdir()
        nb(tricky / "00_connection.ipynb", [("markdown", md), ("code", 'q("select count(*) from analytics.marts.t")')])
        nb(tricky / "01_q.ipynb", [
            ("markdown", md), ("code", 'stmt = "create or replace table t as select 1"\nq(stmt)'),
            ("markdown", md), ("code", "cursor.execute(s)"),
            ("markdown", md), ("code", 'q("""select a from t where x rlike \'\\\\d\'""")'),
            ("markdown", ""), ("code", 'q("select 1")'),
            ("markdown", "What: x"), ("code", 'q("select 1")'),
            ("markdown", md), ("code", 'a = q("select 1")\nb = q("select 2")'),
            ("markdown", md), ("code", "q(\"select ';' as sep\")"),
            ("markdown", md), ("code", 'url = "postgres://bob:pw123@host/db"'),
            ("markdown", md), ("code", 'pw = os.environ.get("DB_PASSWORD", "hunter2")'),
            ("markdown", md), ("code", 'out = "D:\\\\work\\\\x.csv"'),
        ])
        nb(tricky / "02-changes.ipynb", [("code", 'q("delete from t")')])
        nb(tricky / "03_changes_summary.ipynb", [("code", 'q("delete from t")')])
        e = "\n".join(check_queries.check(tricky))
        ok("00_connection.ipynb cell 2: query against data" in e, "data query in 00_connection")
        ok("01_q.ipynb cell 2: not read-only: create" in e, "write in a variable literal caught")
        ok("01_q.ipynb cell 2: SQL passed to q() through a variable" in e, "q(var) flagged")
        ok("01_q.ipynb cell 4: SQL passed to execute() through a variable" in e, "execute(var) flagged")
        ok("01_q.ipynb cell 6: SQL string with a backslash is not raw" in e, "non-raw backslash flagged")
        ok("cell 8: query without a markdown" in e and "cell 10: query without a markdown" in e, "empty / weak markdown")
        ok("cell 12: more than one SQL statement" in e, "two queries in one cell")
        ok("cell 14:" not in e, f"';' inside a string literal is not a statement split: {e}")
        ok("cell 16: secret-looking literal" in e and "cell 18: secret-looking literal" in e, "url and env default secrets")
        ok("cell 20: absolute machine path" in e, "drive-letter path")
        ok("02-changes.ipynb" not in e and "03_changes_summary.ipynb cell 1" in e, "only *-changes notebooks skipped")
    finally:
        shutil.rmtree(d)


if __name__ == "__main__":
    test_inventory()
    test_joins_and_columns()
    test_check_queries()
    for f in FAILS:
        print("FAIL", f)
    print(f"{len(FAILS)} FAIL")
    sys.exit(1 if FAILS else 0)
