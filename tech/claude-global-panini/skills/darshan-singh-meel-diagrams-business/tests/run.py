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
    s["items"] = [{"label": f"Item number {i}", "x": 0.5, "y": 0.5} for i in range(30)]
    e = errs(s)
    assert e and "no free place" in e[0], e


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
