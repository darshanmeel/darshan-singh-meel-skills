"""Tests for the data diagram family. Usage: python tests/run.py [--write]  (--write rebuilds references/examples/*.svg).
Prints PASS/FAIL per test, exit 1 on any failure."""
import sys

sys.dont_write_bytecode = True
import copy, json, subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path[:0] = [str(BASE), str(SKILL / "scripts")]
import check  # noqa: E402
import dbt_manifest  # noqa: E402
import diagram as d  # noqa: E402
import types_data as td  # noqa: E402

EX = SKILL / "references" / "examples"
FAILS = []
OURS = set(td.TYPES)


def test(fn):
    if "--write" in sys.argv:
        return fn
    try:
        fn()
        print("PASS", fn.__name__)
    except Exception as ex:  # an error in a test is a failure too, the other tests still run
        FAILS.append(fn.__name__)
        print("FAIL", fn.__name__, "|", ex)
    return fn


def load(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def errs(spec):
    return d.build(spec)["errors"]


# ---------- registry and examples ----------
@test
def family_registers_without_clash():
    reg = d.registry(refresh=True)
    mine = [e for e in d.REG_ERRORS if "diagrams-data" in e]
    assert not mine, mine
    assert all(reg[t]["family"] == "darshan-singh-meel-diagrams-data" for t in OURS), [t for t in OURS if t not in reg]


@test
def every_type_has_an_example():
    used = {load(p.stem)["type"] for p in EX.glob("*.json")}
    assert OURS <= used, OURS - used


@test
def examples_build_clean_and_pass_check_py():
    with tempfile.TemporaryDirectory() as tmp:
        for p in sorted(EX.glob("*.json")):
            r = d.build(load(p.stem))
            assert not r["errors"], (p.stem, r["errors"])
            assert r["geometry"]["width"] <= d.MAX_W, p.stem
            g = Path(tmp) / f"{p.stem}.json"
            g.write_text(json.dumps(r["geometry"]), encoding="utf-8")
            out = subprocess.run([sys.executable, str(BASE / "check.py"), str(g)], capture_output=True, text=True,
                                 encoding="utf-8")
            assert out.returncode == 0 and "LAYOUT" not in out.stdout, (p.stem, out.stdout)
            assert "Notice:" in r["html"] and 'class="dg-frame"' in r["html"], p.stem


@test
def example_svgs_are_current():
    for p in sorted(EX.glob("*.json")):
        svg = EX / f"{p.stem}.svg"
        assert svg.exists() and svg.read_text(encoding="utf-8") == d.build(load(p.stem))["svg"], \
            f"{p.stem}.svg is stale: python tests/run.py --write"


@test
def mermaid_forms():
    er = d.build(load("shop-er"))["mermaid"]
    assert er.startswith("---\ntitle:") and "erDiagram" in er, er[:60]
    assert "customers ||--o{ orders" in er and "orders ||..o{ payments" in er and "bigint order_id PK, FK" in er
    assert "decimal(12_2) amount" in er, "comma is not allowed in a Mermaid attribute type"
    star = d.build(load("sales-star"))["mermaid"]
    assert "dim_category ||--o{ dim_product" in star and "dim_date ||--o{ fct_sales" in star, star
    for name in ("billing-dbt", "warehouse-load", "platform-dags", "refund-dfd", "retail-mesh", "orders-cdc"):
        assert "flowchart" in d.build(load(name))["mermaid"], name


# ---------- entity tables ----------
@test
def column_strings_parse_keys():
    c = td._columns({"columns": ["order_id bigint PK,FK", "amount decimal(12, 2)", "sku varchar(32) UK"]})
    assert c[0] == {"name": "order_id", "type": "bigint", "key": "PK,FK"}, c[0]
    assert c[1]["type"] == "decimal(12, 2)" and c[1]["key"] == "", c[1]
    assert c[2]["key"] == "UK", c[2]


@test
def entity_rows_wrap_instead_of_overflowing():
    e = {"id": "t", "columns": [{"name": "a_very_long_column_name_for_testing", "type": "timestamp with time zone"}]}
    L = td._ent_layout(e, 180)
    assert L["w"] <= 180 and L["rows"][0]["type"][2] is False, L


@test
def er_validation():
    s = load("shop-er")
    s["relations"].append({"from": "orders", "to": "nope", "card": "many"})
    s["entities"][0]["columns"].append("x int PQ")
    j = " ".join(errs(s))
    assert "unknown entity 'nope'" in j and "card 'many'" in j, j


@test
def star_outrigger_sits_under_parent():
    geo = d.build(load("sales-star"))["geometry"]
    n = {x["id"]: x for x in geo["nodes"]}
    p, o = n["dim_product"], n["dim_category"]
    assert abs(p["x"] + p["w"] / 2 - (o["x"] + o["w"] / 2)) < 30 and o["y"] > p["y"] + p["h"], (p, o)
    assert n["dim_date"]["x"] < n["fct_sales"]["x"] < n["dim_store"]["x"]


@test
def star_validation():
    s = load("sales-star")
    s["dimensions"][0]["parent"] = "fct_sales"
    assert any("outrigger" in e for e in errs(s)), errs(s)


# ---------- lineage, select, impact ----------
EDGES = [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}, {"from": "x", "to": "c"}]


@test
def select_follows_dbt_graph_operators():
    ids = list("abcdx")
    assert td.select_ids("c", ids, EDGES) == {"c"}
    assert td.select_ids("+c", ids, EDGES) == {"a", "b", "c", "x"}
    assert td.select_ids("1+c", ids, EDGES) == {"b", "c", "x"}
    assert td.select_ids("b+", ids, EDGES) == {"b", "c", "d"}
    assert td.select_ids("b+1", ids, EDGES) == {"b", "c"}
    assert td.select_ids("@b", ids, EDGES) == {"a", "b", "c", "d", "x"}
    assert td.select_ids("a d", ids, EDGES) == {"a", "d"}


@test
def impact_dims_unaffected_and_marks_path_red():
    s = load("customer-impact")
    _, nodes, edges, _, _, _ = td.map_lineage(s)
    n = {x["id"]: x for x in nodes}
    assert n["crm_contacts"]["tone"] == "red" and not n["churn"].get("dim") and n["fct_revenue"]["dim"]
    red = {(e["from"], e["to"]) for e in edges if e.get("tone") == "red"}
    assert ("dim_customers", "crm_dash") in red and ("fct_revenue", "crm_dash") not in red, red
    s.update(impact="crm_dash", impact_dir="up")
    _, nodes, _, _, _, _ = td.map_lineage(s)
    assert not {x["id"]: x for x in nodes}["fct_revenue"].get("dim")


@test
def select_and_impact_validation():
    s = load("customer-impact")
    s.update(select="+nope", impact="gone")
    j = " ".join(errs(s))
    assert "no node 'nope'" in j and "impact: no node 'gone'" in j, j


@test
def dbt_layers_derive_in_flow_order():
    s = load("billing-dbt")
    _, _, _, groups, _, _ = td.map_dbt(s)
    assert [g["id"] for g in groups] == ["sources", "staging", "intermediate", "marts", "exposures"], groups
    geo = d.build(s)["geometry"]
    xs = sorted((c["x"], c["x"] + c["w"]) for c in geo["containers"])
    assert len(xs) == 5 and all(a[1] < b[0] for a, b in zip(xs, xs[1:])), "layers must be columns left to right"


@test
def dbt_overview_counts_per_layer():
    st = d.style_graph(*td.map_dbt(load("billing-overview"))[:4])
    n = {x["id"]: x for x in st["nodes"]}
    assert set(n) == {"sources", "staging", "intermediate", "marts", "exposures"}, set(n)
    assert n["staging"]["sub"] == "2 models\n1 snapshot" and n["staging"]["shape"] == "rounded", n["staging"]


@test
def dbt_select_keeps_a_subgraph():
    s = dict(load("billing-dbt"), select="+fct_mrr")
    _, nodes, _, groups, _, _ = td.map_dbt(s)
    assert {x["id"] for x in nodes} == {"src_invoices", "stg_invoices", "plan_prices", "int_mrr_moves", "fct_mrr"}
    assert "exposures" not in {g["id"] for g in groups}
    assert not errs(s)


# ---------- Airflow and orchestration ----------
@test
def airflow_dag_states_assets_and_rules():
    _, nodes, edges, _, _, states = td.map_airflow(load("warehouse-load"))
    n = {x["id"]: x for x in nodes}
    assert n["row_counts"]["state"] == "no_status" and "no_status" in states
    assert n["asset_warehouse_marts"]["tag"] == "asset"
    assert "rule all_done" in n["cleanup_tmp"]["sub"]
    assert any(e.get("kind") == "outlet" and e["to"] == "asset_warehouse_marts" for e in edges)


@test
def airflow_dag_rejects_unknown_state_and_nesting():
    s = load("warehouse-load")
    s["tasks"][0]["state"] = "done"
    s["groups"].append({"id": "inner", "label": "inner", "parent": "extract"})
    j = " ".join(errs(s))
    assert "state 'done'" in j and "nested task groups" in j, j


@test
def dag_overview_infers_asset_edges():
    _, nodes, edges, _, _, _ = td.map_dags(load("platform-dags"))
    es = {(e["from"], e["to"]): e for e in edges}
    assert es[("ingest_crm", "dbt_build")]["label"] == "raw.crm" and es[("ingest_crm", "dbt_build")]["kind"] == "asset"
    assert es[("dbt_build", "finance_export")]["kind"] == "trigger"
    n = {x["id"]: x for x in nodes}
    assert n["dbt_build"]["tag"] == "DAG · on 2 assets" and n["finance_export"]["tag"] == "DAG · manual"
    s = dict(load("platform-dags"), show_assets=True)
    _, nodes, edges, _, _, _ = td.map_dags(s)
    assert "asset_raw_crm" in {x["id"] for x in nodes} and not errs(s)


@test
def external_asset_becomes_a_node():
    s = load("platform-dags")
    s["dags"][3]["schedule"] = {"any": ["marts.core", "vendor.prices"]}
    _, nodes, _, _, _, _ = td.map_dags(s)
    n = {x["id"]: x for x in nodes}
    assert n["asset_vendor_prices"]["tag"] == "asset · external" and n["churn_scoring"]["tag"] == "DAG · on any asset"


@test
def orchestration_redirects_container_edges():
    s = load("daily-sales-adf")
    s.pop("collapse")
    _, nodes, edges, groups, _, _ = td.map_orch(s)
    pairs = {(e["from"], e["to"], e["kind"]) for e in edges}
    assert ("get_tables", "copy_table", "on_succeeded") in pairs and ("log_rows", "alert_teams", "on_failed") in pairs
    assert ("tr_daily", "get_tables", "trigger") in pairs and ("publish", "pl_pl_publish_marts", "trigger") in pairs
    assert groups[0]["label"] == "ForEach · each source table"
    assert not errs(s)
    s["activities"][1]["depends_on"] = [{"activity": "get_tables", "on": "maybe"}]
    assert any("on 'maybe'" in e for e in errs(s))


@test
def mixed_edge_kinds_get_their_own_side():
    es = td._part_kinds([{"from": "a", "to": "b", "kind": "on_succeeded"}, {"from": "a", "to": "c", "kind": "on_failed"}], False)
    assert es[0].get("from_side") is None and es[1]["from_side"] == "bottom", es


# ---------- DFD, medallion, streaming, mesh ----------
@test
def dfd_rules():
    s = load("refund-dfd")
    s["edges"].append({"from": "customer", "to": "orders", "label": "x"})
    s["edges"].append({"from": "p1", "to": "p3"})
    j = " ".join(errs(s))
    assert "starts or ends at a process" in j and "name the data" in j, j
    assert "style" in " ".join(errs(dict(load("refund-dfd"), style="dbt")))


@test
def dfd_stores_drawn_as_two_lines():
    svg = d.build(load("refund-dfd"))["svg"]
    assert 'g[data-id="orders"]>.dg-sh{stroke-dasharray' in svg


@test
def styles_apply_to_family_types():
    for name, style, extra in (("lakehouse-medallion", "dbt", {}), ("orders-cdc", "dbt", {}),
                               ("retail-mesh", "dbt", {"view": "overview"}), ("customer-impact", "plain", {})):
        s = dict(load(name), style=style, **extra)
        assert not errs(s), (name, style, errs(s))


@test
def too_wide_falls_back_to_top_down():
    nodes = [{"id": f"t{i}", "label": f"transform_step_number_{i}", "kind": "table"} for i in range(9)]
    s = {"id": "w", "type": "lineage", "title": "T", "key": "k", "notice": "n", "nodes": nodes,
         "edges": [{"from": f"t{i}", "to": f"t{i + 1}"} for i in range(8)]}
    r = d.build(s)
    assert not r["errors"] and r["geometry"]["height"] > r["geometry"]["width"], r["errors"]
    s["direction"] = "LR"
    assert any("max 1000" in e for e in errs(s))


@test
def mesh_overview_counts_products():
    s = dict(load("retail-mesh"), view="overview")
    _, nodes, _, groups, _, _ = td.map_mesh(s)
    n = {x["id"]: x for x in nodes}
    assert n["customer"]["tag"] == "domain · 2 data products" and not groups, n["customer"]
    assert not errs(s)


@test
def topic_tags_from_partitions():
    _, nodes, _, _, _, _ = td.map_stream(load("orders-cdc"))
    n = {x["id"]: x for x in nodes}
    assert n["t_orders"]["tag"] == "12 partitions · keep 7d", n["t_orders"]


# ---------- dbt manifest converter ----------
MANIFEST = {
    "metadata": {"project_name": "billing"},
    "nodes": {
        "model.billing.stg_invoices": {"resource_type": "model", "name": "stg_invoices", "fqn": ["billing", "staging", "stg_invoices"],
                                       "config": {"materialized": "view"},
                                       "depends_on": {"nodes": ["source.billing.billing.invoices"]}},
        "model.billing.fct_mrr": {"resource_type": "model", "name": "fct_mrr", "fqn": ["billing", "marts", "fct_mrr"],
                                  "config": {"materialized": "table"}, "depends_on": {"nodes": ["model.billing.stg_invoices"]}},
        "test.billing.not_null_fct_mrr_id": {"resource_type": "test", "attached_node": "model.billing.fct_mrr",
                                             "depends_on": {"nodes": ["model.billing.fct_mrr"]}},
        "test.billing.unique_fct_mrr_id": {"resource_type": "test", "depends_on": {"nodes": ["model.billing.fct_mrr"]}}},
    "sources": {"source.billing.billing.invoices": {"resource_type": "source", "source_name": "billing", "name": "invoices",
                                                    "fqn": ["billing", "billing", "invoices"]}},
    "exposures": {"exposure.billing.board": {"resource_type": "exposure", "name": "board", "label": "MRR board",
                                             "depends_on": {"nodes": ["model.billing.fct_mrr"]}}}}


@test
def manifest_converts_to_a_buildable_spec():
    s = dbt_manifest.to_spec(copy.deepcopy(MANIFEST), "billing-lineage", layers=["staging", "marts"])
    n = {x["id"]: x for x in s["nodes"]}
    assert n["fct_mrr"]["tests"] == 2 and n["fct_mrr"]["layer"] == "marts" and n["fct_mrr"]["depends_on"] == ["stg_invoices"]
    assert n["src_billing_invoices"]["label"] == "billing.invoices" and n["exp_board"]["layer"] == "exposures"
    assert [x["id"] for x in s["layers"]] == ["sources", "staging", "marts", "exposures"]
    assert any("notice" in e for e in errs(s)), "an empty notice must stop the build"
    s["notice"] = "fct_mrr feeds the board."
    assert not errs(s), errs(s)


def write():
    for p in sorted(EX.glob("*.json")):
        r = d.build(load(p.stem))
        if r["errors"]:
            print("NOT WRITTEN", p.stem, r["errors"])
            continue
        (EX / f"{p.stem}.svg").write_text(r["svg"], encoding="utf-8")
        print("wrote", f"{p.stem}.svg")


if __name__ == "__main__":
    if "--write" in sys.argv:
        write()
        sys.exit(0)
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    sys.exit(1 if FAILS else 0)
