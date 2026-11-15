"""Tests for the AI / ML diagram types. Usage: python tests/run.py [--write]
Builds every example, runs the base check.py on its geometry, checks validation rules and styles.
--write regenerates references/examples/*.svg from the specs first. Prints PASS/FAIL per test, exit 1 on any."""
import sys

sys.dont_write_bytecode = True
import copy, json, subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path.insert(0, str(BASE))
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
TYPES = ["rag-pipeline", "agent-loop", "multi-agent", "ml-lifecycle", "feature-store", "eval-pipeline",
         "model-serving", "context-assembly", "nn-block"]
FAILS = []


def test(fn):
    try:
        fn()
        print("PASS", fn.__name__)
    except AssertionError as ex:
        FAILS.append(fn.__name__)
        print("FAIL", fn.__name__, "|", ex)
    return fn


def specs():
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(EX.glob("*.json"))}


def by_type(t):
    return copy.deepcopy(next(s for s in specs().values() if s["type"] == t))


def errors(s):
    return d.build(s)["errors"]


if "--write" in sys.argv:
    for name, s in specs().items():
        r = d.build(s)
        if r["svg"]:
            (EX / f"{name}.svg").write_text(r["svg"], encoding="utf-8")


# ---------- registry and examples ----------
@test
def every_type_registered():
    reg = d.registry(refresh=True)
    mine = [e for e in d.REG_ERRORS if "diagrams-ai" in e]
    assert not mine, mine
    for t in TYPES:
        assert t in reg and reg[t]["family"] == "darshan-singh-meel-diagrams-ai", t
        assert reg[t]["doc"], t


@test
def one_example_per_type():
    have = {s["type"] for s in specs().values()}
    assert have == set(TYPES), set(TYPES) ^ have
    for name in specs():
        assert (EX / f"{name}.svg").exists(), f"{name}.svg missing: run tests/run.py --write"


@test
def examples_build_clean():
    for name, s in specs().items():
        r = d.build(s)
        assert not r["errors"], (name, r["errors"])
        assert r["geometry"]["width"] <= d.MAX_W, name
        assert "prefers-color-scheme:dark" in r["svg"] and "Notice:" in r["html"], name


@test
def check_py_finds_no_layout_problem():
    with tempfile.TemporaryDirectory() as td:
        for name, s in specs().items():
            g = Path(td) / f"{name}.json"
            g.write_text(json.dumps(d.build(s)["geometry"]), encoding="utf-8")
            out = subprocess.run([sys.executable, str(BASE / "check.py"), str(g)], capture_output=True, text=True)
            bad = [x for x in out.stdout.splitlines() if x.startswith("LAYOUT")]
            assert out.returncode == 0 and not bad, (name, bad)


@test
def example_svgs_are_current():
    for name, s in specs().items():
        assert (EX / f"{name}.svg").read_text(encoding="utf-8") == d.build(s)["svg"], \
            f"{name}.svg is stale: run tests/run.py --write"


@test
def mermaid_for_every_type():
    for name, s in specs().items():
        m = d.build(s)["mermaid"]
        assert m and m.startswith('---\ntitle: "'), name
        assert "flowchart" in m.splitlines()[3], name


@test
def no_machine_paths_in_examples():
    for f in list(EX.iterdir()) + [SKILL / "scripts" / "types_ai.py"]:
        t = f.read_text(encoding="utf-8")
        for bad in (":\\Users", "/Users/", "/home/", "C:/"):
            assert bad not in t, (f.name, bad)


# ---------- validation rules ----------
@test
def rag_store_must_join_both_bands():
    s = by_type("rag-pipeline")
    s["edges"] = [e for e in s["edges"] if e["from"] not in {x["id"] for x in s["stores"]}]
    assert any("no edge to a query step" in e for e in errors(s)), errors(s)


@test
def agent_loop_needs_a_tool():
    s = by_type("agent-loop")
    for n in s["nodes"]:
        if n.get("kind") == "tool":
            n["kind"] = "step"
    assert any("no tool" in e for e in errors(s)), errors(s)


@test
def lifecycle_needs_a_loop():
    s = by_type("ml-lifecycle")
    s["loops"] = []
    assert any("closes the loop" in e for e in errors(s)), errors(s)


@test
def feature_store_training_reads_offline():
    s = by_type("feature-store")
    off = {x["id"] for x in s["offline"]}
    s["edges"] = [e for e in s["edges"] if e["from"] not in off]
    assert any("offline store -> training" in e for e in errors(s)), errors(s)


@test
def eval_metric_needs_a_grader():
    s = by_type("eval-pipeline")
    for g in s["graders"]:
        g["metrics"] = [m for m in g["metrics"] if m != "grounded"]
    assert any("metric grounded" in e for e in errors(s)), errors(s)


@test
def eval_metric_colour_follows_threshold():
    s = by_type("eval-pipeline")
    r = d.build(s)
    assert "misses gate" in r["svg"] and "meets gate" in r["svg"]


@test
def context_over_limit_is_an_error():
    s = by_type("context-assembly")
    s["limit"] = 4000
    assert any("over the limit" in e for e in errors(s)), errors(s)


@test
def serving_needs_model_and_gateway():
    s = by_type("model-serving")
    s["nodes"] = [n for n in s["nodes"] if n.get("kind") not in ("gateway", "router")]
    s["edges"] = [e for e in s["edges"] if e["from"] in {n["id"] for n in s["nodes"]}
                  and e["to"] in {n["id"] for n in s["nodes"]}]
    assert any("gateway" in e for e in errors(s)), errors(s)


@test
def unknown_kind_is_reported():
    s = by_type("multi-agent")
    s["nodes"][0]["kind"] = "wizard"
    assert any("kind 'wizard'" in e for e in errors(s)), errors(s)


@test
def nn_residual_ends_must_exist():
    s = by_type("nn-block")
    s["residuals"].append({"from": "embed", "to": "nowhere"})
    assert any("nowhere" in e for e in errors(s)), errors(s)


# ---------- graph styles ----------
@test
def every_graph_type_takes_every_style():
    for t in TYPES:
        if t == "context-assembly":
            continue
        for style in ("plain", "dbt", "airflow"):
            s = by_type(t)
            s["style"] = style
            r = d.build(s)
            assert not r["errors"], (t, style, r["errors"])


@test
def airflow_style_drops_family_kind_legend():
    s = by_type("multi-agent")
    svg = d.build(s)["svg"]
    assert "up for retry" in svg and ">agent<" not in svg


@test
def overview_collapses_groups_on_fixed_layouts():
    s = by_type("ml-lifecycle")
    s["view"] = "overview"
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert len(r["geometry"]["nodes"]) == 2, [n["id"] for n in r["geometry"]["nodes"]]


@test
def too_wide_layered_graph_falls_back_to_top_down():
    s = by_type("rag-pipeline")
    s["style"] = "dbt"
    r = d.build(s)
    assert not r["errors"] and r["geometry"]["width"] <= d.MAX_W, r["errors"]


print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
