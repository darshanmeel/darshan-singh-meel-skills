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
