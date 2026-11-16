"""Planted-error tests for review_diagrams.py; also: every family example passes with 0 MUST. Usage: python run.py"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True   # no __pycache__ left in the skill folders
SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS / "darshan-singh-meel-diagrams-review" / "scripts"))
import review_diagrams as rd  # noqa: E402

FAILS = []
HEAD = {"title": "Orders lineage: sources to marts", "key": "Pill colour = kind", "notice": "fct_orders feeds the dashboard."}


def ok(cond, msg):
    if not cond:
        FAILS.append(msg)


def run(*paths):
    rd.OUT.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        code = rd.main([str(p) for p in paths])
    return code, "\n".join(rd.OUT)


def spec(d, name, s):
    (d / f"{name}.json").write_text(json.dumps({"id": name, **HEAD, **s}), encoding="utf-8")
    return d / f"{name}.json"


def main():
    code, out = run(*sorted(SKILLS.glob("darshan-singh-meel-diagrams*/references/examples")))
    ok(code == 0 and "MUST" not in out, f"examples should pass: {out}")
    ok("palette" not in out, f"palette contrast below WCAG AA: {out}")
    d = Path(tempfile.mkdtemp())
    try:
        lin = {"type": "boxes", "style": "dbt", "groups": [{"id": "staging", "label": "staging"},
                                                            {"id": "marts", "label": "marts"}]}
        p = spec(d, "backward", {**lin, "nodes": [
            {"id": "stg", "label": "stg_orders", "kind": "model", "group": "staging"},
            {"id": "stg2", "label": "stg_payments", "kind": "model", "group": "staging"},
            {"id": "fct", "label": "fct_orders", "kind": "model", "group": "marts"}],
            "edges": [{"from": "stg", "to": "fct"}, {"from": "fct", "to": "stg2"}]})
        out = run(p)[1]
        ok("links back" in out or "edge against layer order" in out, f"backward dbt edge not flagged: {out}")
        p = spec(d, "loop", {"type": "dbt-lineage", "nodes": [
            {"id": "a", "resource_type": "model", "layer": "staging", "depends_on": ["b"]},
            {"id": "b", "resource_type": "model", "layer": "marts", "depends_on": ["a"]}]})
        ok("MUST" in run(p)[1], "cycle in dbt-lineage not flagged")
        p = spec(d, "masked", {**lin, "nodes": [
            {"id": "stg", "label": "stg_orders", "kind": "model", "group": "staging"},
            {"id": "fct", "label": "fct_orders", "kind": "model", "group": "marts"}],
            "edges": [{"from": "stg", "to": "fct", "label": "x" * 60}, {"from": "fct", "to": "stg"}]})
        out = run(p)[1]
        ok("label over 36" in out and "graph not acyclic" in out and "edge against layer order" in out,
           f"a build error hides the notation checks: {out}")
        p = spec(d, "names", {"type": "boxes", "nodes": [{"id": "a", "label": "Service A"},
                                                         {"id": "b", "label": "orders-db", "sub": "password=hunter2"}],
                              "edges": [{"from": "a", "to": "b"}]})
        out = run(p)[1]
        ok("placeholder name | Service A" in out, f"placeholder not flagged: {out}")
        ok("secret in text | sub = <redacted>" in out and "hunter2" not in out, f"secret not flagged or leaked: {out}")
        p = spec(d, "run", {"type": "airflow-dag", "legend": False, "tasks": [
            {"id": "load", "operator": "PythonOperator", "state": "failed"},
            {"id": "dbt_build", "operator": "BashOperator", "upstream": ["load"], "state": "upstream_failed"}]})
        ok("colour only signal | legend off" in run(p)[1], "airflow legend off not flagged")
        p = spec(d, "plan", {"type": "gantt", "start": "2026-01-05", "end": "2026-02-27", "tasks": [
            {"id": "api", "label": "Build API", "start": "2026-01-05", "days": 20},
            {"id": "test", "label": "Test", "after": ["api"], "start": "2026-01-10", "days": 5}]})
        ok("gantt dependency | test starts before" in run(p)[1], "gantt dependency not flagged")
        page = d / "page.html"
        page.write_text('<figure class="dg-fig"><svg id="dg-x" class="dg" width="1200"><g id="m1"/></svg></figure>'
                        '<svg id="dg-x" class="dg"><title>t</title><desc>d</desc><image href="https://cdn.example/a.png"/>'
                        '</svg><p>see C:\\Users\\someone\\x.svg</p>', encoding="utf-8")
        out = run(page)[1]
        for want in ("duplicate id | dg-x", "accessibility", "canvas too wide", "external resource", "machine path",
                     "figure needs the scroll frame"):
            ok(want in out, f"page check missing: {want}: {out}")
        code, out = run(*sorted((SKILLS / "darshan-singh-meel-docs-v3" / "references" / "examples").glob("*.html")))
        ok(code == 0 and "MUST" not in out and "not built by the engine" not in out,
           f"docs-v3 pages: the builder's own drawings are not engine diagrams: {out}")
        doc = d / "doc-spec.json"
        doc.write_text(json.dumps({"type": "technical", "sections": {"Main flows": [
            {"type": "h3", "text": "Nightly build"},
            {"type": "diagram", "id": "C", "key": "Pill colour = resource type", "notice": "fct_orders reads staging.",
             "spec": {"type": "dbt-lineage", "nodes": [
                 {"id": "stg_orders", "resource_type": "model", "layer": "staging", "depends_on": ["fct_orders"]},
                 {"id": "fct_orders", "resource_type": "model", "layer": "marts", "depends_on": ["stg_orders"]}]}}]}}),
            encoding="utf-8")
        out = run(doc)[1]
        ok("doc-spec.json#c | graph not acyclic" in out, f"diagram block inside a docs-v3 spec not rebuilt: {out}")
        run_spec = {"type": "airflow-dag", "tasks": [
            {"id": "load", "operator": "BashOperator", "state": "failed"},
            {"id": "dbt_build", "operator": "BashOperator", "upstream": ["load"], "state": "skipped"},
            {"id": "alert", "operator": "SlackWebhookOperator", "upstream": ["dbt_build"], "state": "success",
             "trigger_rule": "one_failed"}]}
        p = spec(d, "night", run_spec)
        out = run(p)[1]
        ok("airflow state | dbt_build is skipped" in out and "| alert is" not in out, f"airflow state vs rule: {out}")
        ok("Mermaid text colour" in out, f"pale Mermaid classDef without color not flagged: {out}")
        frag = d / "frag.html"
        built = rd.diagram.build({"id": "night", **HEAD, **run_spec})["html"]
        frag.write_text(built, encoding="utf-8")
        ok("| no spec |" in run(frag)[1], "engine svg on a page with no spec not flagged")
        out = run(p, frag)[1]
        ok("frag.html" not in out, f"page svg equal to its spec flagged: {out}")
        frag.write_text(built.replace('<rect ', '<rect x="900" ', 1), encoding="utf-8")
        ok("page SVG differs from its spec" in run(p, frag)[1], "hand-edited page svg not flagged")
        geo = rd.diagram.build({"id": "night", **HEAD, **run_spec})["geometry"]
        geo["nodes"][1].update(x=geo["nodes"][0]["x"], y=geo["nodes"][0]["y"])
        dgv = d / "v3.html"
        dgv.write_text('<style>.dgv { overflow-x:auto; }</style><div class="dgv" data-id="C" data-geo="'
                       + json.dumps(geo).replace("&", "&amp;").replace('"', "&quot;") + '">'
                       + built.split('<div class="dg-frame"', 1)[1].split(">", 1)[1].split("</div>")[0]
                       + '</div><p class="key">Key: x</p>', encoding="utf-8")
        out = run(dgv)[1]
        ok("LAYOUT boxes overlap" in out, f"data-geo layout not re-checked: {out}")
        ok("Notice text missing" in out, f"dgv without Notice not flagged: {out}")
        p = spec(d, "seq", {"type": "sequence", "participants": [{"id": "a", "label": "checkout-api"},
                                                                 {"id": "b", "label": "payments-api"}],
                            "steps": [{"from": "a", "to": "b", "label": "charge"},
                                      {"frame": "alt", "label": "[declined]",
                                       "steps": [{"from": "b", "to": "a", "label": "402", "kind": "reply"}]}]})
        ok("alt with one operand" in run(p)[1], "alt with one operand not flagged")
        md = d / "doc.md"
        md.write_text("# Doc\n\n```mermaid\nflowchart LR\n  a --> b\n```\n\nNext.\n\n![x](diagrams/gone.svg)\n",
                      encoding="utf-8")
        out = run(md)[1]
        ok("Notice under Mermaid" in out and "missing SVG file | diagrams/gone.svg" in out, f"markdown checks: {out}")
    finally:
        shutil.rmtree(d)
    for f in FAILS:
        print("FAIL", f)
    print(f"{len(FAILS)} FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
