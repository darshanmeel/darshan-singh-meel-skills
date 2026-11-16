"""Tests for the business diagram types. Usage: python tests/run.py  (PASS/FAIL per test, exit 1 on any).
Builds every example, runs the base skill's check.py on it (0 LAYOUT lines), and checks validation, maths and styles."""
import sys

sys.dont_write_bytecode = True
import copy, json, subprocess  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path.insert(0, str(BASE))
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
FAILS = []
TYPES = ("org-chart", "team-topology", "capability-map", "value-stream", "value-chain", "sipoc", "quadrant",
         "stakeholder-map", "swot", "funnel", "mind-map", "fishbone", "business-model-canvas", "kpi-tree", "decision-matrix")
MERMAID = {"org-chart", "team-topology", "capability-map", "value-stream", "quadrant", "stakeholder-map", "mind-map",
           "fishbone", "kpi-tree"}


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
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(EX.glob("*.json"))}


def errs(spec):
    return d.build(spec)["errors"]


@test
def all_types_registered():
    reg = d.registry(refresh=True)
    assert not d.REG_ERRORS, d.REG_ERRORS
    for t in TYPES:
        assert t in reg and reg[t]["family"] == "darshan-singh-meel-diagrams-business", t


@test
def one_example_per_type():
    got = sorted(s["type"] for s in examples().values())
    assert got == sorted(TYPES), got


@test
def examples_build_clean():
    for name, s in examples().items():
        r = d.build(s)
        assert not r["errors"], (name, r["errors"])
        assert r["geometry"]["width"] <= d.MAX_W, name
        assert not [w for w in r["warnings"] if w.startswith(("WARN", "registry"))], (name, r["warnings"])
        assert 'class="dg-frame"' in r["html"] and "Notice:" in r["html"], name


@test
def check_py_finds_no_layout_lines():
    for f in sorted(EX.glob("*.json")):
        p = subprocess.run([sys.executable, "-B", str(BASE / "check.py"), str(f)], capture_output=True, text=True,
                           encoding="utf-8")
        assert p.returncode == 0 and "LAYOUT" not in p.stdout and "ERROR" not in p.stdout, (f.name, p.stdout)


@test
def example_svgs_are_current():
    for name, s in examples().items():
        f = EX / f"{name}.svg"
        assert f.exists() and f.read_text(encoding="utf-8") == d.build(s)["svg"], f"{name}.svg is stale: rebuild it"


@test
def mermaid_where_supported():
    for name, s in examples().items():
        m = d.build(s)["mermaid"]
        if s["type"] in MERMAID:
            assert m and m.startswith("---\ntitle:"), name
        else:
            assert m is None, name
    assert "quadrantChart" in d.build(load("backlog-priority"))["mermaid"]
    assert "ishikawa-beta" in d.build(load("late-report-fishbone"))["mermaid"]
    mm = d.build(load("platform-themes"))["mermaid"]
    assert "mindmap" in mm and "  root((" in mm


@test
def team_topology_takes_every_graph_style():
    s = load("team-deps")
    for st in d.GRAPH_STYLES:
        r = d.build(dict(s, style=st))
        assert not r["errors"], (st, r["errors"])
    r = d.build(dict(s, view="overview"))
    assert not r["errors"] and "2 stream-aligned teams" in r["svg"], r["errors"]
    assert "X-as-a-Service" in d.build(s)["svg"]


@test
def value_stream_totals():
    svg = d.build(load("feature-delivery"))["svg"]
    assert "Lead time 141 h" in svg and "process time 25 h" in svg and "flow efficiency 18%" in svg


@test
def decision_matrix_weighted_scores():
    svg = d.build(load("orchestrator-choice"))["svg"]
    assert "4.05" in svg and "3.30" in svg and "3.55" in svg and "highest" in svg


@test
def funnel_conversions():
    svg = d.build(load("trial-funnel"))["svg"]
    assert "13% of previous · biggest drop" in svg and "1.1% of first stage" in svg
    assert not errs(dict(load("trial-funnel"), scale="value"))


@test
def mind_map_folds_deepest_level_when_wide():
    s = load("platform-themes")
    assert "freshness · volume" in d.build(s)["svg"]
    e = errs(dict(s, compact=False))
    assert e and e[0].startswith("layout: canvas would be") and "one map per branch" in e[0], e


@test
def org_chart_stacks_leaves_when_wide():
    s = copy.deepcopy(load("data-org"))
    s["stack_leaves"] = False
    for i in range(6):
        s["units"].append({"id": f"x{i}", "label": f"Regional analytics team {i}", "sub": "4 analysts", "parent": "an"})
    assert errs(s) and "split the chart" in errs(s)[0]
    s["stack_leaves"] = "auto"
    assert not errs(s), errs(s)


@test
def quadrant_reports_crowding():
    s = load("backlog-priority")
    s["items"] = [{"label": f"Item number {i}", "x": 0.45, "y": 0.45} for i in range(30)]
    e = errs(s)
    assert e and "no free place inside its quadrant" in e[0], e


@test
def quadrant_labels_stay_in_their_quadrant():
    s = load("backlog-priority")
    r = d.build(s)
    PW, PH = s.get("size", [600, 440])
    for n in r["geometry"]["nodes"]:
        it = next((i for i in s["items"] if i["label"] == n["text"]), None)
        if not it:
            continue
        dot = next(lb for lb in r["geometry"]["labels"] if lb["text"] == "point " + it["label"])
        dx, dy = dot["x"] + 6, dot["y"] + 6
        x0, y0 = dx - it["x"] * PW, dy - (1 - it["y"]) * PH
        mx, my = x0 + PW / 2, y0 + PH / 2
        assert (n["x"] >= mx) == (dx >= mx) and (n["x"] + n["w"] <= mx or n["x"] >= mx), it["label"]
        assert (n["y"] >= my) == (dy >= my) and (n["y"] + n["h"] <= my or n["y"] >= my), it["label"]


@test
def points_on_a_divider_are_rejected():
    s = copy.deepcopy(load("backlog-priority"))
    s["items"][0]["x"] = 0.5
    assert any("on the divider" in e for e in errs(s)), errs(s)
    s = copy.deepcopy(load("crm-stakeholders"))
    s["stakeholders"][0]["interest"] = 3
    assert any("sits on the divider" in e for e in errs(s)), errs(s)
    assert not [e for e in errs(dict(s, scale=6)) if "divider" in e]  # an even scale has no middle value


@test
def value_stream_first_wait_needs_start():
    s = copy.deepcopy(load("feature-delivery"))
    assert s.get("start") and s["stages"][0].get("wait") is not None, "example must cover the counted first wait"
    s.pop("start")
    assert any("stages[0].wait needs 'start'" in e for e in errs(s)), errs(s)
    s["stages"][0].pop("wait")
    assert not errs(s), errs(s)


@test
def team_topology_airflow_states_keep_the_type():
    s = copy.deepcopy(load("team-deps"))
    s["style"] = "airflow"
    s["states"] = {"done": {"tone": "green", "label": "onboarded"}, "todo": {"tone": "amber", "label": "not started"}}
    for i, t in enumerate(s["teams"]):
        t["state"] = "done" if i % 2 else "todo"
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert "stream-aligned team" in r["svg"] and "onboarded" in r["svg"] and "not started" in r["svg"]
    leg = [lb["text"] for lb in r["geometry"]["labels"] if lb.get("kind") == "legend"]
    assert "onboarded" in leg and not [x for x in leg if x.endswith(" team")], leg  # fill = state, not type
    assert "stream-aligned team · " in r["mermaid"] and "· onboarded" in r["mermaid"]
    plain = d.build(dict(s, states=None, style="airflow", teams=[{k: v for k, v in t.items() if k != "state"}
                                                                  for t in s["teams"]]))
    assert not plain["errors"] and "stream-aligned team" in plain["svg"], plain["errors"]


@test
def team_topology_arrows_keep_their_own_port():
    for st in d.GRAPH_STYLES:
        g = d.build(dict(load("team-deps"), style=st))["geometry"]
        starts = {}
        for e in g["edges"]:
            starts.setdefault((e["from"], tuple(e["points"][0])), []).append(e["to"])
        assert all(len(v) == 1 for v in starts.values()), (st, starts)


@test
def value_chain_names_the_advantage():
    s = load("saas-value-chain")
    assert any(a.get("tone") == "green" for a in s["primary"])
    assert "advantage" in d.build(s)["svg"]


@test
def validation_catches_bad_specs():
    cases = [
        ("trial-funnel", lambda s: s["stages"].append({"label": "Grows", "value": 99999}), "must not grow"),
        ("orchestrator-choice", lambda s: s["criteria"][0]["scores"].pop(), "scores for 3 options"),
        ("backlog-priority", lambda s: s["items"].append({"label": "Off", "x": 1.4, "y": 0.2}), "from 0 to 1"),
        ("crm-stakeholders", lambda s: s["stakeholders"].append({"label": "X", "power": 7, "interest": 2}), "from 1 to 5"),
        ("revenue-kpi-tree", lambda s: s["metrics"].append({"id": "r2", "label": "Second root"}), "exactly one root"),
        ("data-org", lambda s: s["units"].append({"id": "z", "label": "Z", "parent": "nope"}), "parent 'nope'"),
        ("late-report-fishbone", lambda s: s["categories"].extend(s["categories"][:3]), "at most 8"),
        ("retail-capabilities", lambda s: s["areas"][0]["caps"].append({"label": "X", "heat": "hot"}), "heat 'hot'"),
        ("team-deps", lambda s: s["interactions"].append({"from": "sre", "to": "pay", "mode": "pairing"}), "mode 'pairing'"),
        ("claims-sipoc", lambda s: s.pop("inputs"), "inputs: required"),
        ("ai-assistant-swot", lambda s: s.pop("threats"), "threats: required"),
        ("analytics-bmc", lambda s: s.pop("channels"), "channels: required"),
        ("feature-delivery", lambda s: s["stages"][0].update(time="2 days"), "must be a number"),
        ("feature-delivery", lambda s: s.pop("start"), "stages[0].wait needs 'start'"),
    ]
    for name, change, want in cases:
        s = copy.deepcopy(load(name))
        change(s)
        e = errs(s)
        assert any(want in x for x in e), (name, want, e)


@test
def dark_mode_and_scoping():
    for name in ("crm-stakeholders", "revenue-kpi-tree"):
        svg = d.build(load(name))["svg"]
        assert "prefers-color-scheme:dark" in svg and f"#dg-{name} .bz-" in svg, name


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failed")
    sys.exit(1 if FAILS else 0)
