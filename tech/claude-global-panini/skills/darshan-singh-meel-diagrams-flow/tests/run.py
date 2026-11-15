"""Tests for the flow family types. Usage: python tests/run.py [--write]  (--write refreshes the example SVGs).
Prints PASS/FAIL per test, exit 1 on any failure. Needs darshan-singh-meel-diagrams next to this skill."""
import sys

sys.dont_write_bytecode = True
import copy, json, subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path.insert(0, str(BASE))
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
TYPES = ("flowchart", "swimlane", "decision-tree", "state-machine", "activity", "retry-flow", "approval-workflow")
FAILS = []


def test(fn):
    try:
        fn()
        print("PASS", fn.__name__)
    except AssertionError as ex:
        FAILS.append(fn.__name__)
        print("FAIL", fn.__name__, "|", ex)
    return fn


def load(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def examples():
    return sorted(p.stem for p in EX.glob("*.json"))


def errs(spec):
    return d.build(spec)["errors"]


@test
def family_registers_every_type():
    reg = d.registry(refresh=True)
    for t in TYPES:
        assert t in reg and reg[t]["family"] == "darshan-singh-meel-diagrams-flow", (t, reg.get(t))
    assert not d.REG_ERRORS, d.REG_ERRORS


@test
def one_example_per_type():
    seen = {load(n)["type"] for n in examples()}
    assert seen >= set(TYPES), set(TYPES) - seen


@test
def examples_build_clean_and_pass_check_py():
    with tempfile.TemporaryDirectory() as td:
        for n in examples():
            r = d.build(load(n))
            assert not r["errors"], (n, r["errors"])
            assert not [w for w in r["warnings"] if not w.startswith("WARN")], (n, r["warnings"])
            g = Path(td) / f"{n}.json"
            g.write_text(json.dumps(r["geometry"]), encoding="utf-8")
            out = subprocess.run([sys.executable, str(BASE / "check.py"), str(g)], capture_output=True, text=True,
                                 encoding="utf-8")
            assert out.returncode == 0 and "LAYOUT" not in out.stdout, (n, out.stdout)
            assert r["geometry"]["width"] <= d.MAX_W, (n, r["geometry"]["width"])


@test
def example_svgs_are_current():
    write = "--write" in sys.argv
    for n in examples():
        svg = d.build(load(n))["svg"]
        f = EX / f"{n}.svg"
        if write:
            f.write_text(svg, encoding="utf-8")
        assert f.exists() and f.read_text(encoding="utf-8") == svg, f"{n}.svg is stale: run tests/run.py --write"


@test
def mermaid_forms():
    m = {n: d.build(load(n))["mermaid"] for n in examples()}
    for n, txt in m.items():
        assert txt and txt.startswith("---\ntitle:"), n
    assert "stateDiagram-v2" in m["order-lifecycle"] and "<<choice>>" in m["order-lifecycle"]
    assert "[*] --> n_new" in m["order-lifecycle"] and "state n_ful {" in m["order-lifecycle"]
    inner = m["order-lifecycle"].split("state n_ful {")[1].split("}")[0]
    assert "n_ship" not in inner, "a transition leaving the composite belongs at top level"
    assert "@{ shape: lean-r" in m["refund-request"]
    assert "@{ shape: fork }" in m["release-pipeline"] and "@{ shape: fr-circ }" in m["release-pipeline"]
    assert "-.->|\"dispute\"|" in m["invoice-dispute"] and "<-.->" not in m["invoice-dispute"]
    assert "linkStyle" in m["webhook-delivery"]


def flow(**kw):
    s = {"id": "t", "type": "flowchart", "title": "T", "key": "k", "notice": "n",
         "nodes": [{"id": "a", "label": "Start", "kind": "start"}, {"id": "b", "label": "Do it"},
                   {"id": "c", "label": "Done", "kind": "end"}],
         "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}
    s.update(kw)
    return s


@test
def flowchart_rules():
    assert not errs(flow())
    s = flow()
    s["nodes"][0]["kind"] = "step"
    assert any("start" in e for e in errs(s)), errs(s)
    s = flow()
    s["edges"].append({"from": "c", "to": "a"})
    assert any("end has no outgoing" in e for e in errs(s)), errs(s)
    s = flow()
    s["nodes"][1]["kind"] = "decision"
    assert any("decision with fewer than 2 exits" in e for e in errs(s)), errs(s)


@test
def flowchart_styles_and_overview():
    s = flow(style="airflow")
    s["nodes"][1]["state"] = "failed"
    r = d.build(s)
    assert not r["errors"] and "failed" in r["svg"], r["errors"]
    s = flow(groups=[{"id": "g", "label": "core"}], view="overview")
    s["nodes"][1]["group"] = "g"
    r = d.build(s)
    assert not r["errors"] and "1 item" in r["svg"], r["errors"]


@test
def too_wide_names_the_fix():
    nodes = [{"id": f"n{i}", "label": f"Step number {i} with a long name", "kind": "start" if i == 0 else "step"}
             for i in range(9)]
    s = flow(nodes=nodes, edges=[{"from": f"n{i}", "to": f"n{i + 1}"} for i in range(8)], direction="LR")
    e = errs(s)
    assert e and "1000" in e[0] and "TB" in e[0], e


def retry(**kw):
    s = load("webhook-delivery")
    s.update(kw)
    return s


@test
def retry_rules():
    s = retry()
    s["steps"][2]["retry"] = {"delay": "30s"}
    assert any("max" in e for e in errs(s)), errs(s)
    s = retry(edges=[e for e in retry()["edges"] if e.get("kind") != "failure"])
    assert any("no failure path" in e for e in errs(s)), errs(s)
    r = d.build(retry())
    assert "retry ≤5" in r["svg"] and "up for retry" in r["svg"]


@test
def approval_rules():
    s = load("expense-approval")
    s["steps"][3]["role"] = "employee"
    assert any("four-eyes" in e for e in errs(s)), errs(s)
    s = load("expense-approval")
    s["edges"] = [e for e in s["edges"] if not (e["from"] == "fin" and e["outcome"] == "rejected")]
    assert any("step fin" in e for e in errs(s)), errs(s)


@test
def decision_tree_rules():
    s = load("incident-severity")
    s["nodes"] = [n for n in s["nodes"] if n["id"] != "none"]
    assert any("at least two answers" in e for e in errs(s)), errs(s)
    s = load("incident-severity")
    s["nodes"][1].pop("answer")
    assert any("answer" in e for e in errs(s)), errs(s)
    s = load("incident-severity")
    s["direction"] = "LR"
    assert not errs(s), errs(s)


@test
def decision_tree_connectors_in_both_directions():
    for direction in ("TB", "LR"):
        s = load("incident-severity")
        s["direction"] = direction
        r = d.build(s)
        assert not r["errors"], (direction, r["errors"])
        bus = [e["points"] for e in r["geometry"]["edges"] if len(e["points"]) == 4]
        assert bus and all(p[1][0 if direction == "LR" else 1] == p[2][0 if direction == "LR" else 1] for p in bus), direction


@test
def state_machine_rules():
    s = load("order-lifecycle")
    s["transitions"].append({"from": "end", "to": "new", "event": "reopen"})
    assert any("final state has no outgoing" in e for e in errs(s)), errs(s)
    s = load("order-lifecycle")
    s["transitions"][2].pop("guard")
    assert any("choice" in e for e in errs(s)), errs(s)
    s = load("order-lifecycle")
    s["style"] = "airflow"
    assert any("fixed notation" in e for e in errs(s)), errs(s)
    s = load("order-lifecycle")
    s["states"].append({"id": "deep", "label": "Deep", "parent": "pick"})
    assert any("composite inside a composite" in e for e in errs(s)), errs(s)


@test
def state_transition_label_is_uml_form():
    s = load("order-lifecycle")
    t = next(t for t in s["transitions"] if t["to"] == "exp")
    t.update(guard="unpaid", action="notify")
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert "timeout 30m [unpaid] / notify" in r["svg"] and "[in stock]" in r["svg"] and "cancel / refund" in r["svg"]


@test
def activity_rules():
    s = load("release-pipeline")
    s["edges"] = [e for e in s["edges"] if not (e["from"] == "fork" and e["to"] != "unit")]
    assert any("node fork" in e for e in errs(s)), errs(s)
    s = load("release-pipeline")
    s["edges"][-3].pop("guard")
    assert any("guard" in e for e in errs(s)), errs(s)
    s = load("release-pipeline")
    s["direction"] = "LR"
    r = d.build(s)
    assert not r["errors"] or "1000" in r["errors"][0], r["errors"]


def lane(**kw):
    s = {"id": "t", "type": "swimlane", "title": "T", "key": "k", "notice": "n",
         "lanes": [{"id": "a", "label": "Sales"}, {"id": "b", "label": "Ops"}],
         "nodes": [{"id": "s", "kind": "start", "label": "Order in", "lane": "a"},
                   {"id": "t1", "label": "Check order", "lane": "a"},
                   {"id": "g", "kind": "gateway", "gateway": "parallel", "lane": "b"},
                   {"id": "t2", "label": "Pick", "lane": "b"}, {"id": "t3", "label": "Invoice", "lane": "a"},
                   {"id": "j", "kind": "gateway", "gateway": "parallel", "lane": "b"},
                   {"id": "e", "kind": "end", "label": "Done", "lane": "b"}],
         "flows": [{"from": "s", "to": "t1"}, {"from": "t1", "to": "g"}, {"from": "g", "to": "t2"},
                   {"from": "g", "to": "t3"}, {"from": "t2", "to": "j"}, {"from": "t3", "to": "j"},
                   {"from": "j", "to": "e"}]}
    s.update(kw)
    return s


@test
def swimlane_lr_and_tb():
    for dr in ("LR", "TB"):
        r = d.build(lane(direction=dr))
        assert not r["errors"], (dr, r["errors"])
    r = d.build(lane())
    assert r["geometry"]["width"] <= d.MAX_W and not r["errors"], r["errors"]


@test
def swimlane_rules():
    s = lane(pools=[{"id": "p1", "label": "Shop"}, {"id": "p2", "label": "Warehouse"}])
    s["lanes"][0]["pool"], s["lanes"][1]["pool"] = "p1", "p2"
    assert any("sequence flow stays inside its pool" in e for e in errs(s)), errs(s)
    s = lane()
    s["flows"][0]["type"] = "message"
    assert any("message flow connects two pools" in e for e in errs(s)), errs(s)
    s = lane()
    s["nodes"][-1]["trigger"] = "timer"
    assert any("end event cannot wait" in e for e in errs(s)), errs(s)
    s = lane()
    s["flows"].append({"from": "e", "to": "s"})
    assert any("end event" in e for e in errs(s)), errs(s)


@test
def own_shapes_keep_text_checked():
    r = d.build(load("refund-request"))
    geo = r["geometry"]
    io = next(n for n in geo["nodes"] if n["id"] == "form")
    assert io["lines"] and io["w"] > max(x["w"] for x in io["lines"]) + 24, io
    assert "fx-own" in r["svg"] and "polygon" in r["svg"]


@test
def composite_edges_attach_to_frame():
    r = d.build(load("order-lifecycle"))
    g = r["geometry"]
    frame = next(c for c in g["containers"] if c["id"] == "ful")
    e = next(e for e in g["edges"] if e["from"] == "ful")
    x, y = e["points"][0]
    on = abs(x - frame["x"]) < 1 or abs(x - frame["x"] - frame["w"]) < 1 or abs(y - frame["y"]) < 1 or \
        abs(y - frame["y"] - frame["h"]) < 1
    assert on, (e["points"][0], frame)


@test
def two_diagrams_on_one_page_keep_own_css():
    a, b = d.build(load("refund-request")), d.build(load("invoice-dispute"))
    page = d.page([a, b])
    assert "#dg-refund-request .fx-own" in page and "#dg-invoice-dispute .fx-own" in page


@test
def reference_snippets_build_clean():
    import re
    n = 0
    for f in (SKILL / "references").glob("*.md"):
        for block in re.findall(r"```json\n(.*?)```", f.read_text(encoding="utf-8"), re.S):
            spec = json.loads(block)
            r = d.build(spec)
            assert not r["errors"], (f.name, spec["id"], r["errors"])
            n += 1
    assert n >= 4, n


print(f"{len(FAILS)} failed" if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
