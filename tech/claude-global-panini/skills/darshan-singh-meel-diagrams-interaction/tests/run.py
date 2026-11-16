"""Tests for the interaction diagram types. Usage: python tests/run.py [--write]
--write rebuilds references/examples/*.svg from their specs. Prints PASS/FAIL per test, exit 1 on any failure."""
import sys

sys.dont_write_bytecode = True
import copy, json, subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
BASE = SKILL.parent / "darshan-singh-meel-diagrams" / "scripts"
sys.path.insert(0, str(BASE))
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
sys.stdout.reconfigure(encoding="utf-8")
TYPES = ("sequence", "timeline", "gantt", "journey", "service-blueprint", "raci", "handoff")
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


def errors(spec):
    return d.build(spec)["errors"]


if "--write" in sys.argv:
    for f in sorted(EX.glob("*.json")):
        r = d.build(json.loads(f.read_text(encoding="utf-8")))
        if r["svg"]:
            f.with_suffix(".svg").write_text(r["svg"], encoding="utf-8")
        print("wrote" if not r["errors"] else "FAILED", f.with_suffix(".svg").name, *r["errors"])


# ---------- registry and examples ----------
@test
def types_registered():
    reg = d.registry(refresh=True)
    for t in TYPES:
        assert t in reg, t
        assert reg[t]["family"] == "darshan-singh-meel-diagrams-interaction", (t, reg[t]["family"])
    assert not [e for e in d.REG_ERRORS if "interaction" in e], d.REG_ERRORS


@test
def every_type_has_an_example():
    have = {load(f.stem)["type"] for f in EX.glob("*.json")}
    assert set(TYPES) <= have, set(TYPES) - have


@test
def examples_build_clean():
    for f in sorted(EX.glob("*.json")):
        r = d.build(json.loads(f.read_text(encoding="utf-8")))
        assert not r["errors"], (f.name, r["errors"])
        assert not [w for w in r["warnings"] if w.startswith("WARN")], (f.name, r["warnings"])
        assert r["geometry"]["width"] <= d.MAX_W, f.name
        assert "prefers-color-scheme:dark" in r["svg"] and "Notice:" in r["html"], f.name


@test
def check_py_finds_no_layout_lines():
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for f in sorted(EX.glob("*.json")):
            r = d.build(json.loads(f.read_text(encoding="utf-8")))
            p = Path(td) / f"{f.stem}.geo.json"
            p.write_text(json.dumps(r["geometry"]), encoding="utf-8")
            paths.append(str(p))
        out = subprocess.run([sys.executable, str(BASE / "check.py"), *paths], capture_output=True, text=True,
                             encoding="utf-8")
        lines = [x for x in out.stdout.splitlines() if x.startswith("LAYOUT")]
        assert out.returncode == 0 and not lines, lines or out.stderr


@test
def example_svgs_are_current():
    for f in sorted(EX.glob("*.json")):
        svg = f.with_suffix(".svg")
        assert svg.exists(), f"{svg.name} missing: python tests/run.py --write"
        assert svg.read_text(encoding="utf-8") == d.build(json.loads(f.read_text(encoding="utf-8")))["svg"], \
            f"{svg.name} is stale: python tests/run.py --write"


@test
def graph_styles_shown():
    styles = {(load(f.stem)["type"], load(f.stem).get("style", "plain")) for f in EX.glob("*.json")}
    assert ("gantt", "airflow") in styles and ("gantt", "dbt") in styles and ("handoff", "airflow") in styles, styles


# ---------- mermaid ----------
@test
def mermaid_forms():
    want = {"sequence": "sequenceDiagram", "timeline": "timeline", "gantt": "gantt", "journey": "journey",
            "handoff": "flowchart"}
    for f in sorted(EX.glob("*.json")):
        s = load(f.stem)
        m = d.build(s)["mermaid"]
        if s["type"] in ("raci", "service-blueprint"):
            assert m is None, f.name
            continue
        assert m.startswith("---\ntitle:"), (f.name, m[:40])
        assert m.splitlines()[3].startswith(want[s["type"]]), (f.name, m.splitlines()[3])


@test
def mermaid_sequence_blocks_balance():
    m = d.build(load("checkout-payment"))["mermaid"]
    opens = sum(1 for x in m.splitlines() if x.strip().split(" ")[0] in ("alt", "opt", "loop", "par", "break", "critical"))
    ends = sum(1 for x in m.splitlines() if x.strip() == "end")
    assert opens == ends == 2, (opens, ends)
    pluses = m.count("->>+") + m.count("-)+")
    minuses = m.count("-->>-")
    assert pluses >= minuses, m


@test
def mermaid_escapes_separators():
    s = load("checkout-payment")
    s["steps"][0]["label"] = "Pay; total #2: 84.90"
    m = d.build(s)["mermaid"]
    line = [x for x in m.splitlines() if "total" in x][0]
    assert line.count(":") == 1 and "#59;" in line and "#35;" in line, line


@test
def mermaid_gantt_times_full():
    m = d.build(load("nightly-run-gantt"))["mermaid"]
    assert "dateFormat HH:mm:ss" in m and "03:42:00, 1320s" in m, m


# ---------- validation and layout errors ----------
@test
def raci_one_accountable():
    s = load("data-incident-raci")
    s["tasks"][0]["cells"] = ["A", "A", "R", "", ""]
    assert any("exactly one A" in e for e in errors(s)), errors(s)
    s["tasks"][0]["cells"] = ["A", "C", "", "", ""]
    assert any("at least one R" in e for e in errors(s)), errors(s)
    s["tasks"][0]["cells"] = ["A", "R", "X", "", ""]
    assert any("letters R, A, C, I" in e for e in errors(s)), errors(s)


@test
def sequence_rejects_unknown_and_long():
    s = load("checkout-payment")
    s["steps"].append({"from": "web", "to": "ghost", "label": "x"})
    assert any("unknown participant 'ghost'" in e for e in errors(s)), errors(s)
    s = load("checkout-payment")
    s["steps"].append({"from": "web", "to": "api", "label": "x" * 40})
    assert any("over 36 characters" in e for e in errors(s)), errors(s)


@test
def sequence_too_wide_says_fix():
    s = {"id": "wide", "type": "sequence", "title": "T", "key": "k", "notice": "n",
         "participants": [{"id": f"p{i}", "label": f"service-number-{i}"} for i in range(9)],
         "steps": [{"from": f"p{i}", "to": f"p{i + 1}", "label": "a call with a long label"} for i in range(8)]}
    e = errors(s)
    assert any("layout:" in x and "fewer participants" in x for x in e), e


@test
def sequence_nested_frames_and_notes():
    s = {"id": "nest", "type": "sequence", "title": "T", "key": "k", "notice": "n",
         "participants": [{"id": "a", "label": "Client"}, {"id": "b", "label": "API"}, {"id": "c", "label": "DB"}],
         "steps": [{"frame": "loop", "label": "[each page]", "steps": [
             {"frame": "par", "label": "[fetch]", "steps": [{"from": "a", "to": "b", "label": "GET page"}],
              "else": [{"label": "[count]", "steps": [{"from": "b", "to": "c", "label": "SELECT count(*)"},
                                                      {"from": "c", "to": "b", "label": "n", "kind": "reply"}]}]},
             {"note": "cursor kept in memory", "over": ["a", "b"]},
             {"from": "b", "to": "b", "label": "cache page"}]},
             {"from": "b", "to": "a", "label": "pages", "kind": "reply"}]}
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert "par [fetch]" in r["mermaid"] and "and [count]" in r["mermaid"] and "Note over n_a,n_b" in r["mermaid"], r["mermaid"]


@test
def sequence_activation_per_operand():
    s = {"id": "alt", "type": "sequence", "title": "T", "key": "k", "notice": "n",
         "participants": [{"id": "w", "label": "web"}, {"id": "a", "label": "api"}, {"id": "d", "label": "db"}],
         "steps": [{"from": "w", "to": "a", "label": "POST"},
                   {"frame": "alt", "label": "[ok]", "steps": [{"from": "a", "to": "d", "label": "INSERT"},
                                                              {"from": "d", "to": "a", "label": "ok", "kind": "reply"},
                                                              {"from": "a", "to": "w", "label": "201", "kind": "reply"}],
                    "else": [{"label": "[bad]", "steps": [{"from": "a", "to": "w", "label": "422", "kind": "reply"}]}]}]}
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert r["svg"].count('class="ia-act"') == 3, r["svg"].count('class="ia-act"')  # api in each operand + db
    assert "activate n_a" in r["mermaid"].split("else [bad]")[1], r["mermaid"]
    s["steps"][1]["frame"], s["steps"][1]["label"] = "break", "[blocked]"
    del s["steps"][1]["else"]
    s["steps"].append({"from": "a", "to": "w", "label": "200", "kind": "reply"})
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert r["svg"].count('class="ia-act"') == 3, r["svg"].count('class="ia-act"')  # api before and after break + db
    assert r["mermaid"].rstrip().splitlines()[-2].strip() == "activate n_a", r["mermaid"]


@test
def gantt_start_before_after_ends():
    s = load("dbt-run-timing")
    t = next(x for x in s["tasks"] if x.get("after"))
    dep = next(x for x in s["tasks"] if x["id"] == t["after"][0])
    t["start"] = dep.get("start") or s["start"]
    t.pop("queued", None)
    assert any(f"task {t['id']}: start" in e and f"before '{dep['id']}' ends" in e for e in errors(s)), errors(s)


@test
def gantt_label_column_enforced():
    s = load("nightly-run-gantt")
    s["tasks"][0]["label"] = "a_very_long_task_identifier_that_cannot_fit_in_the_column_x"
    assert any("label column would be" in e for e in errors(s)), errors(s)


@test
def gantt_mermaid_vert_and_states():
    s = load("nightly-run-gantt")
    s["markers"] = [{"date": "04:30", "label": "SLA"}]
    m = d.build(s)["mermaid"]
    assert "SLA : vert, " in m and "04:30:00, 1s" in m, m
    assert ":done," in m and "queued time is in the SVG only" in m, m


@test
def gantt_task_outside_window():
    s = load("lakehouse-roadmap")
    s["end"] = "2026-03-01"
    e = errors(s)
    assert any("outside start/end" in x for x in e), e


@test
def gantt_rejects_bad_state_and_after():
    s = load("nightly-run-gantt")
    s["tasks"][0]["state"] = "done"
    s["tasks"][1]["after"] = ["nope"]
    e = errors(s)
    assert any("not an Airflow state" in x for x in e) and any("after 'nope'" in x for x in e), e


@test
def gantt_plain_without_sections():
    s = load("lakehouse-roadmap")
    s.pop("sections")
    for t in s["tasks"]:
        t.pop("section")
    r = d.build(s)
    assert not r["errors"], r["errors"]


@test
def journey_scores():
    s = load("analyst-onboarding-journey")
    s["stages"][0]["score"] = 6
    assert any("score is 1" in e for e in errors(s)), errors(s)
    s = load("analyst-onboarding-journey")
    del s["stages"][0]["score"]
    assert any("every stage a score or none" in e for e in errors(s)), errors(s)


@test
def timeline_switches_to_tb_when_long():
    s = {"id": "long", "type": "timeline", "title": "T", "key": "k", "notice": "n",
         "periods": [{"label": f"Q{i % 4 + 1} {2023 + i // 4}", "events": [{"label": f"Release {i}.0", "sub": "minor"}]}
                     for i in range(10)]}
    r = d.build(s)
    assert not r["errors"], r["errors"]
    assert r["geometry"]["height"] > r["geometry"]["width"] / 2, (r["geometry"]["width"], r["geometry"]["height"])


@test
def handoff_rejects_overview():
    s = load("model-release-handoff")
    s["view"] = "overview"
    assert any("not supported" in e for e in errors(s)), errors(s)


@test
def handoff_plain_and_dbt():
    for style in ("plain", "dbt"):
        s = load("model-release-handoff")
        s["style"] = style
        if style == "dbt":  # pills are wider than boxes: four time slots fit
            s["steps"] = [x for x in s["steps"] if x["col"] < 4]
            s["handoffs"] = [h for h in s["handoffs"] if h["to"] not in ("canary", "promote")]
            s["columns"] = s["columns"][:4]
            s["steps"][0]["kind"] = "seed"
        r = d.build(s)
        assert not r["errors"], (style, r["errors"])


@test
def blueprint_rejects_bad_lane():
    s = load("data-access-blueprint")
    s["items"][0]["lane"] = "kitchen"
    assert any("lane one of" in e for e in errors(s)), errors(s)


@test
def specs_unchanged_by_build():
    for f in sorted(EX.glob("*.json")):
        s = load(f.stem)
        before = copy.deepcopy(s)
        d.build(s)
        assert s == before, f.name


print(f"\n{'FAILED: ' + ', '.join(FAILS) if FAILS else 'ALL PASSED'}")
sys.exit(1 if FAILS else 0)
