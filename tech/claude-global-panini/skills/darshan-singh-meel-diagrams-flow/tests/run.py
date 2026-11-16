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
    assert any("needs a label" in e for e in errs(s)), errs(s)
    s["edges"][1]["label"] = "yes"
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


def _segs(pts):
    return [(a, b) for a, b in zip(pts, pts[1:])]


def _collinear(e, f, tol=8):
    """Length of the longest stretch two orthogonal polylines share on one line."""
    best = 0
    for (a, b) in _segs(e):
        for (p, q) in _segs(f):
            for k in (0, 1):  # k = the fixed coordinate (0: vertical segment)
                if a[k] == b[k] and p[k] == q[k] and abs(a[k] - p[k]) < 1:
                    lo = max(min(a[1 - k], b[1 - k]), min(p[1 - k], q[1 - k]))
                    hi = min(max(a[1 - k], b[1 - k]), max(p[1 - k], q[1 - k]))
                    best = max(best, hi - lo)
    return best > tol


LLM_RETRY = {"id": "llm", "type": "retry-flow", "title": "T", "key": "k", "notice": "n",
             "steps": [{"id": "in", "label": "Question received", "kind": "start"},
                       {"id": "ctx", "label": "Build prompt", "sub": "top 5 KB chunks"},
                       {"id": "llm", "label": "Call primary model", "sub": "large model",
                        "retry": {"max": 3, "delay": "exp 2s"}, "timeout": "20s"},
                       {"id": "val", "label": "Validate JSON answer", "kind": "decision"},
                       {"id": "ok", "label": "Answer sent", "kind": "end"},
                       {"id": "fb", "label": "Call fallback model", "kind": "fallback", "sub": "small model"},
                       {"id": "hand", "label": "Hand to human agent", "kind": "alert"}],
             "edges": [{"from": "in", "to": "ctx"}, {"from": "ctx", "to": "llm"}, {"from": "llm", "to": "val"},
                       {"from": "val", "to": "ok", "label": "valid"},
                       {"from": "val", "to": "llm", "label": "invalid, re-ask once", "kind": "retry"},
                       {"from": "llm", "to": "fb", "kind": "fallback", "label": "3 tries failed"},
                       {"from": "fb", "to": "hand", "kind": "failure", "label": "error or invalid"},
                       {"from": "fb", "to": "ok", "label": "valid"}]}


@test
def edges_of_different_kinds_never_share_a_line():
    for spec in [LLM_RETRY] + [load(n) for n in examples()]:
        r = d.build(spec)
        assert not r["errors"], (spec["id"], r["errors"])
        raw = spec.get("edges") or spec.get("transitions") or spec.get("flows") or []
        kind = {(e["from"], e["to"]): e.get("kind") or e.get("outcome") or e.get("type") for e in raw}
        ge = [e for e in r["geometry"]["edges"] if e["from"] != e["to"]]
        for i, e in enumerate(ge):
            for f in ge[i + 1:]:
                if kind.get((e["from"], e["to"])) != kind.get((f["from"], f["to"])):
                    assert not _collinear(e["points"], f["points"]), (spec["id"], e["from"], e["to"], f["from"], f["to"])


@test
def retry_loop_room_and_mermaid_follow_the_drawn_direction():
    r = d.build(LLM_RETRY)  # too wide in LR: drawn TB, loop label inside the canvas
    assert not r["errors"] and r["geometry"]["direction"] == "TB", r["errors"]
    assert "flowchart TB" in r["mermaid"], r["mermaid"][:200]


@test
def flow_checks_one_start_labelled_exits_no_dead_end():
    s = flow()
    s["nodes"].append({"id": "a2", "label": "Second start", "kind": "start"})
    s["edges"].append({"from": "a2", "to": "b"})
    assert any("more than one 'start'" in e for e in errs(s)), errs(s)
    s = flow()
    s["nodes"].insert(2, {"id": "x", "label": "Stuck"})
    s["edges"].append({"from": "b", "to": "x"})
    assert any("x: dead end" in e for e in errs(s)), errs(s)
    s = load("expense-approval")
    s["edges"] = [dict(e, label=None) if e["from"] == "amt" else e for e in s["edges"]]
    assert any("amt -> " in e and "needs a label" in e for e in errs(s)), errs(s)
    s = load("expense-approval")  # outcomes count as labels; a review without exits is a dead end
    assert not errs(s), errs(s)
    s["edges"] = [e for e in s["edges"] if e["from"] != "skip"]
    assert any("skip: dead end" in e or "step skip" in e for e in errs(s)), errs(s)


@test
def dbt_style_colours_by_the_authors_category():
    r = d.build(load("release-impact"))
    assert not r["errors"], r["errors"]
    for cat in ("check", "build", "deploy", "release"):
        assert f">{cat}<" in r["svg"], cat
    s = flow(style="dbt")
    s["nodes"][1].update(cat="deploy", tag="k8s apply")
    r = d.build(s)
    assert not r["errors"] and ">k8s apply<" in r["svg"] and ">deploy<" in r["svg"], r["errors"]
    s = flow()
    s["nodes"][1]["cat"] = "deploy"
    assert any("cat" in e for e in errs(s)), errs(s)


@test
def swimlane_reply_moves_forward():
    s = lane(pools=[{"id": "p1", "label": "Shop"}, {"id": "p2", "label": "Supplier"}],
             lanes=[{"id": "a", "label": "Sales", "pool": "p1"}, {"id": "b", "label": "Ops", "pool": "p1"},
                    {"id": "v", "label": "Supplier", "pool": "p2"}])
    s["nodes"].insert(2, {"id": "vq", "label": "Quote price", "lane": "v"})
    s["flows"] = [f for f in s["flows"] if f["from"] != "t1"] + [
        {"from": "t1", "to": "vq", "type": "message", "label": "request"},
        {"from": "vq", "to": "g", "type": "message", "label": "quote"}]
    r = d.build(s)
    assert not r["errors"], r["errors"]
    g = d.registry()["swimlane"]["svg"].__globals__
    col = g["_sw_cols"](s, g["_sw_edges"](s))
    assert col["vq"] == col["t1"] and col["g"] > col["t1"], col
    for f in s["flows"]:
        if (f.get("type") or "sequence") == "sequence":
            assert col[f["to"]] > col[f["from"]], (f, col)
    assert r["svg"].count(">Supplier<") == 1, "one-lane pool named like its lane shows one header"
    assert '["Supplier"]' in r["mermaid"], r["mermaid"]
    s["flows"].append({"from": "s", "to": "vq", "type": "message"})
    assert any("start event only catches" in e for e in errs(s)), errs(s)


print(f"{len(FAILS)} failed" if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
