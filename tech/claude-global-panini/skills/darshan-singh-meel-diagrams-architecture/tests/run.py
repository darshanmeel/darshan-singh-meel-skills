"""Tests for the architecture diagram types. Usage: python tests/run.py  (PASS/FAIL per test, exit 1 on any).
Needs darshan-singh-meel-diagrams next to this skill (repo or ~/.claude/skills)."""
import sys

sys.dont_write_bytecode = True
import copy, json, re, subprocess  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path.insert(0, str(BASE))
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
TYPES = ["c4-context", "c4-container", "c4-component", "deployment", "network-topology", "integration-map",
         "event-driven", "service-map", "layered-architecture", "request-path", "trust-boundaries"]
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


def red_edge(svg):
    return bool(re.search(r'class="dg-e \w+ c-red', svg))


def errs(spec):
    return d.build(spec)["errors"]


@test
def all_types_registered():
    reg = d.registry(refresh=True)
    missing = [t for t in TYPES if t not in reg]
    assert not missing, missing
    assert all(reg[t]["family"] == "darshan-singh-meel-diagrams-architecture" for t in TYPES)
    assert not [e for e in d.REG_ERRORS if "architecture" in e], d.REG_ERRORS


@test
def one_example_per_type():
    have = {load(f.stem)["type"] for f in EX.glob("*.json")}
    assert set(TYPES) <= have, set(TYPES) - have


@test
def examples_build_clean_and_svg_current():
    for f in sorted(EX.glob("*.json")):
        r = d.build(load(f.stem))
        assert not r["errors"], (f.name, r["errors"])
        assert r["geometry"]["width"] <= d.MAX_W, f.name
        svg = f.with_suffix(".svg")
        assert svg.exists() and svg.read_text(encoding="utf-8") == r["svg"], f"{svg.name} is stale: rebuild it"


@test
def check_py_reports_no_layout_lines():
    for f in sorted(EX.glob("*.json")):
        out = subprocess.run([sys.executable, str(BASE / "check.py"), str(f)], capture_output=True, text=True,
                             encoding="utf-8")
        assert out.returncode == 0 and "LAYOUT" not in out.stdout, (f.name, out.stdout)


@test
def mermaid_where_supported():
    for f in sorted(EX.glob("*.json")):
        s = load(f.stem)
        m = d.build(s)["mermaid"]
        assert m, f.name
        if s["type"].startswith("c4-"):
            assert m.splitlines()[0] in ("C4Context", "C4Container", "C4Component"), m[:40]
            assert "Rel(" in m and f"title {s['title']}" in m
        else:
            assert m.startswith("---\ntitle:"), (f.name, m[:40])


@test
def c4_requires_desc_tech_and_labels():
    s = load("booking-containers")
    s["nodes"][1].pop("tech")
    s["nodes"][0].pop("desc")
    s["edges"][0].pop("label")
    e = " ".join(errs(s))
    assert "tech required" in e and "desc required" in e and "label required" in e, e


@test
def c4_kind_must_fit_level():
    s = load("booking-context")
    s["nodes"][0]["kind"] = "component"
    assert any("not one of" in x for x in errs(s))


@test
def c4_rejects_graph_styles():
    s = load("booking-context")
    s["style"] = "dbt"
    assert any("does not fit c4-context" in x for x in errs(s))


@test
def nested_frames_hold_their_members():
    for name in ("booking-deployment", "booking-network", "booking-trust"):
        g = d.build(load(name))["geometry"]
        rect = {c["id"]: c for c in g["containers"]}
        for n in g["nodes"]:
            for c in g["containers"]:
                if n["id"] in c["members"]:
                    assert c["x"] <= n["x"] and n["x"] + n["w"] <= c["x"] + c["w"], (name, n["id"], c["id"])
        spec = load(name)
        for gr in spec["groups"]:
            if gr.get("parent"):
                a, b = rect[gr["id"]], rect[gr["parent"]]
                assert b["x"] < a["x"] and a["x"] + a["w"] < b["x"] + b["w"] and b["y"] < a["y"], (name, gr["id"])


@test
def nested_rejects_bad_parent_and_empty_group():
    s = load("booking-network")
    s["groups"].append({"id": "x", "label": "spare", "kind": "subnet_private", "parent": "nope"})
    e = " ".join(errs(s))
    assert "parent 'nope'" in e and "holds no node" in e, e


@test
def nested_rejects_parent_loop():
    s = load("booking-network")
    s["groups"][0]["parent"] = "pub"
    assert any("loops back" in x for x in errs(s))


@test
def too_wide_gives_a_fix():
    s = load("booking-network")
    s["direction"] = "LR"
    for k in range(6):
        s["nodes"].append({"id": f"vm{k}", "label": f"batch-vm-{k} with a long name", "kind": "compute", "group": "app"})
        s["edges"].append({"from": f"vm{k - 1}" if k else "api", "to": f"vm{k}"})
    s["groups"][3]["layout"] = "row"
    e = " ".join(errs(s))
    assert "canvas would be" in e and "TB" in e, e


@test
def trust_numbers_only_crossings():
    s = load("booking-trust")
    s["nodes"].append({"id": "audit", "label": "audit log", "kind": "store", "group": "int"})
    s["edges"].append({"from": "api", "to": "audit", "label": "append"})
    r = d.build(s)
    assert not r["errors"], r["errors"]
    labels = [lb["text"] for lb in r["geometry"]["labels"] if lb["kind"] == "edge"]
    assert "append" in labels and "T1 HTTPS" in labels and "T4 OAuth 2" in labels, labels


@test
def layered_marks_rule_breaks():
    s = load("booking-layers")
    r = d.build(s)
    assert red_edge(r["svg"]) and "breaks the layer rule" in r["svg"]
    s2 = copy.deepcopy(s)
    s2["edges"] = [e for e in s2["edges"] if e["from"] != "reports"]
    r2 = d.build(s2)
    assert not r2["errors"] and not red_edge(r2["svg"]), r2["errors"]
    s3 = copy.deepcopy(s)
    s3["rule"] = "relaxed"
    assert not red_edge(d.build(s3)["svg"])  # skipping down is allowed when relaxed


@test
def layered_upward_call_is_red_even_relaxed():
    s = load("booking-layers")
    s["rule"] = "relaxed"
    s["edges"].append({"from": "pg", "to": "brepo"})
    assert red_edge(d.build(s)["svg"])


@test
def events_every_edge_touches_a_topic():
    s = load("booking-events")
    s["edges"].append({"from": "api", "to": "mail"})
    assert any("touches a topic" in x for x in errs(s))


@test
def events_auto_columns():
    g = d.build(load("booking-events"))["geometry"]
    ids = [c["id"] for c in g["containers"]]
    assert ids[:3] == ["producers", "broker", "consumers"] or {"producers", "consumers"} <= set(ids), ids
    x = {c["id"]: c["x"] for c in g["containers"]}
    assert x["producers"] < x["broker"] < x["consumers"], x


@test
def service_map_dbt_style_and_dim():
    s = load("booking-services")
    r = d.build(s)
    assert s["style"] == "dbt" and "dg-solid" in r["svg"] and "dg-dim" in r["svg"]
    s["style"] = "airflow"
    assert any("does not fit service-map" in x for x in errs(s))


@test
def service_map_health_states():
    s = load("booking-services")
    s["style"] = "plain"
    s["nodes"][3]["state"] = "down"
    s["nodes"][1]["state"] = "degraded"
    r = d.build(s)
    assert not r["errors"] and "dg-t-red" in r["svg"] and ">down<" in r["svg"], r["errors"]
    s["nodes"][1]["state"] = "broken"
    assert any("state 'broken'" in x for x in errs(s))


@test
def request_path_numbers_hops():
    r = d.build(load("booking-request"))
    labels = [lb["text"] for lb in r["geometry"]["labels"] if lb["kind"] == "edge"]
    assert "1 HTTPS" in labels and "5 SELECT FOR UPDATE 200 ms" in labels, labels


@test
def integration_via_drives_legend():
    r = d.build(load("booking-integrations"))
    assert "file transfer" in r["svg"] and "event / message" in r["svg"]
    s = load("booking-integrations")
    s["edges"][0]["via"] = "fax"
    assert any("via 'fax'" in x for x in errs(s))


if __name__ == "__main__":
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    sys.exit(1 if FAILS else 0)
