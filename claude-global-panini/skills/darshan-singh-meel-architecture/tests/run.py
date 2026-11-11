"""Tests for architecture build.py: one case per builder rule. Usage: python run.py [skills folder] (default: this skill's parent)"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILLS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
SKILL = SKILLS / "darshan-singh-meel-architecture"
BUILD = SKILL / "references" / "templates" / "build.py"
BASE = json.loads((SKILL / "references" / "examples" / "architecture-example.json").read_text(encoding="utf-8"))
FILES = {"dags/orders_daily.py": 30, "extract/pull_orders.py": 50, "models/marts/fct_orders.sql": 30, "models/marts/fct_returns.sql": 20,
         "models/marts/fct_refunds.sql": 20, "infra/snowflake/warehouses.tf": 20, "infra/airflow/vm.tf": 20, "dbt_project.yml": 20,
         "README.md": 30, "reviews/review-v2-2026-11-10-0930.html": 3, ".env": 2}
FACTS = {"facts": [{"fact": "marts", "value": 3, "how": "ls models/marts | wc -l"}]}


def repo(git=False, facts=True, inv=None):
    d = Path(tempfile.mkdtemp())
    if git:
        subprocess.run(["git", "init", "-q", str(d)], check=True)
    for p, n in FILES.items():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        (d / p).write_text("".join(f"line {i}\n" for i in range(n)), encoding="utf-8")
    (d / "generated-docs" / "_spec").mkdir(parents=True)
    if facts:
        (d / "generated-docs/_spec/facts.json").write_text(json.dumps(FACTS), encoding="utf-8")
        (d / "generated-docs/_spec/inventory.json").write_text(json.dumps(inv or {"scan": True}), encoding="utf-8")
    return d


def build(spec, build=BUILD, out="generated-docs/a.html", git=False, facts=True, empty=False, args=(), inv=None):
    d = Path(tempfile.mkdtemp()) if empty else repo(git, facts, inv)
    (d / "generated-docs/_spec").mkdir(parents=True, exist_ok=True)
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(spec), encoding="utf-8")
    r = subprocess.run([sys.executable, str(build), *args, "generated-docs/_spec/a.json", out], cwd=d, capture_output=True, text=True, encoding="utf-8")
    page = (d / out).read_text(encoding="utf-8") if (d / out).is_file() else ""
    marker = (d / "generated-docs/.generated-by-darshan-singh-meel-docs").is_file()
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout + r.stderr, page, marker


def edit(fn):
    s = copy.deepcopy(BASE)
    fn(s)
    return s


P = lambda s, i: s["problems"][i]
C = lambda s, i: s["proposal"]["changes"][i]
I = lambda s, i: s["impact"][i]
M = lambda s, i: s["migration"][i]
W = lambda s, i, side="current": s["workflows"][i][side]
CASES = [  # (name, spec, expected exit, text expected in output)
    ("unknown verdict", edit(lambda s: s.update(verdict="rewrite")), 1, "verdict 'rewrite' unknown"),
    ("evidence missing", edit(lambda s: P(s, 0).update(evidence=[])), 1, "needs evidence"),
    ("evidence without line", edit(lambda s: P(s, 0).update(evidence=["dbt_project.yml"])), 1, "needs a line"),
    ("evidence not in repo", edit(lambda s: P(s, 0).update(evidence=["src/x.py:3"])), 1, "src/x.py is not a file in the repo"),
    ("evidence past file end", edit(lambda s: P(s, 0).update(evidence=["dbt_project.yml:40"])), 1, "lines 40 outside dbt_project.yml (1-20)"),
    ("secret cited with line", edit(lambda s: P(s, 4).update(evidence=[".env:1"])), 1, "secret file: cite it by path only"),
    ("secret cited by path ok", edit(lambda s: P(s, 4).update(evidence=[".env"])), 0, "0 WARN"),
    ("dotdot path", edit(lambda s: P(s, 0).update(evidence=["../x.py:1"])), 1, "must be a path from the repo root"),
    ("absolute path in text", edit(lambda s: P(s, 0).update(detail="see C:\\work\\x.py")), 1, "absolute or machine path"),
    ("secret literal", edit(lambda s: P(s, 4).update(detail='`api_key = "abc123"` is committed')), 1, "likely secret value for 'api_key'"),
    ("unknown area", edit(lambda s: P(s, 0).update(area="style")), 1, "area 'style' unknown"),
    ("unknown severity", edit(lambda s: P(s, 0).update(sev="Must")), 1, "sev 'Must' unknown"),
    ("bad problem id", edit(lambda s: P(s, 1).update(id="P1")), 1, "id must be P1, P2"),
    ("change fixes nothing", edit(lambda s: C(s, 4).update(fixes=[])), 1, "fixes no problem"),
    ("change fixes unknown", edit(lambda s: C(s, 4).update(fixes=["P9"])), 1, "fixes 'P9', which is no problem id"),
    ("change without impact", edit(lambda s: s.update(impact=[r for r in s["impact"] if r["change"] != "C5"])), 1, "change C5: no impact row"),
    ("High without change", edit(lambda s: C(s, 1).update(fixes=["P5"])), 0, "problem P2 is High and no change fixes it"),
    ("High accepted ok", edit(lambda s: (C(s, 1).update(fixes=["P5"]), P(s, 1).update(accept="restart takes 5 min; one missed night a year is fine"))), 0, "0 WARN"),
    ("keep with High", edit(lambda s: s.update(verdict="keep")), 0, "verdict keep with High problems"),
    ("redesign without High", edit(lambda s: (s.update(verdict="redesign"), P(s, 0).update(sev="Medium"), P(s, 1).update(sev="Medium"))), 0, "verdict redesign without a High problem"),
    ("one option", edit(lambda s: s["proposal"].update(options=s["proposal"]["options"][:1])), 1, "list 2-3 options"),
    ("two chosen", edit(lambda s: s["proposal"]["options"][1].update(chosen=True)), 1, "exactly one option chosen"),
    ("option without trade-off", edit(lambda s: s["proposal"]["options"][1].update(costs="")), 1, "needs name, what, gains and costs"),
    ("proposal diagram untagged", edit(lambda s: [n.pop("tag", None) for n in s["proposal"]["diagram"]["nodes"]]), 1, "tag the boxes"),
    ("diagram without title", edit(lambda s: s["current"]["l0"].pop("title")), 1, "diagram needs a title"),
    ("l0 with lanes", edit(lambda s: s["current"]["l0"].update(lanes=["a"])), 0, "the big picture is one row"),
    ("kind unknown", edit(lambda s: I(s, 0).update(kind="guess")), 1, "kind 'guess' unknown"),
    ("measured without source", edit(lambda s: I(s, 5).pop("source")), 1, "measured needs source"),
    ("estimate without assumption", edit(lambda s: I(s, 1).pop("assumption")), 1, "estimate needs assumption"),
    ("invented precision", edit(lambda s: I(s, 1).update(saving="~73.5 min earlier")), 0, "invented precision (73.5)"),
    ("range is fine", edit(lambda s: I(s, 1).update(saving="~60–80 min earlier")), 0, "0 WARN"),
    ("cost estimate without source", edit(lambda s: I(s, 0).pop("source")), 0, "cost estimate without source"),
    ("unknown fact", edit(lambda s: I(s, 5).update(fact="rows", source=None) or I(s, 5).pop("source")), 1, "fact 'rows' is not in facts.json"),
    ("fact value missing in row", edit(lambda s: I(s, 6).update(now="revenue `CASE` copied", saving="one edit per rule change")), 0, "fact 'marts' = 3, not in now"),
    ("measured number not in source", edit(lambda s: (I(s, 6).pop("fact"), I(s, 6).update(source="models/marts/fct_orders.sql:12-20"))), 0, "measured 3 is not in models/marts/fct_orders.sql:12-20"),
    ("measured duration without number", edit(lambda s: I(s, 7).update(now="outage until noticed", proposed="restart in seconds")), 0, "a duration without a number"),
    ("text contradicts fact", edit(lambda s: C(s, 3).update(why="one edit for 4 marts")), 0, "text says 4 marts, facts.json says 3"),
    ("unknown dim", edit(lambda s: I(s, 0).update(dim="speed")), 1, "dim 'speed' unknown"),
    ("at count", edit(lambda s: W(s, 0)["examples"][0]["at"].pop()), 1, "3 `at` values, want one per step (4)"),
    ("no trace", edit(lambda s: W(s, 0, "proposed").update(examples=[])), 1, "needs one example trace"),
    ("two traces", edit(lambda s: W(s, 0)["examples"].append(dict(W(s, 0)["examples"][0], title="again", case="edge"))), 0, "2 traces"),
    ("step without out", edit(lambda s: W(s, 0)["steps"][0].pop("out")), 1, "needs do and out"),
    ("placeholder cell", edit(lambda s: W(s, 0)["examples"][0]["at"].__setitem__(1, "skipped")), 0, "placeholder words"),
    ("step do over 8 words", edit(lambda s: W(s, 0)["steps"][0].update(do="Read the whole orders table from the primary Postgres")), 0, "texts over 8 words"),
    ("one workflow", edit(lambda s: s.update(workflows=s["workflows"][:1])), 0, "workflows: 1 given"),
    ("workflow unknown change", edit(lambda s: s["workflows"][0].update(changes=["C9"])), 1, "change 'C9' is no change id"),
    ("filler word", edit(lambda s: C(s, 0).update(why="a robust way to scan days of rows")), 0, "filler: 'robust'"),
    ("repeated sentence", edit(lambda s: C(s, 1).update(why=C(s, 0)["why"])), 0, "repeat:"),
    ("lead too long", edit(lambda s: s.update(summary="One. Two. Three.")), 0, "has 3 sentences"),
    ("migration unknown change", edit(lambda s: M(s, 0).update(changes=["C9"])), 1, "change 'C9' is no change id"),
    ("migration no rollback", edit(lambda s: M(s, 0).update(rollback="")), 1, "needs step and rollback"),
    ("migration bad effort", edit(lambda s: M(s, 0).update(effort="XL")), 1, "effort 'XL' unknown"),
    ("quick win late", edit(lambda s: s.update(migration=[s["migration"][2], s["migration"][0], s["migration"][1]] + s["migration"][3:]) or M(s, 3).update(needs=[1])), 0, "is a quick win (S, Low) after step 1"),
    ("needs a later step", edit(lambda s: M(s, 3).update(needs=[5])), 1, "needs 5: name an earlier step"),
    ("change in no step", edit(lambda s: s.update(migration=s["migration"][:4])), 0, "change C2 is in no migration step"),
    ("keep with L step", edit(lambda s: (s.update(verdict="keep"), P(s, 0).update(sev="Medium"), P(s, 1).update(sev="Medium"))), 0, "effort L with verdict keep"),
    ("review missing", edit(lambda s: s.update(review="reviews/nope.html")), 1, "reviews/nope.html is not a file"),
    ("review not named", edit(lambda s: s.pop("review")), 0, "spec names none"),
    ("top unknown", edit(lambda s: s.update(top=["C9"])), 1, "top: up to 3 change ids"),
    ("move without change", edit(lambda s: s["proposal"]["moves"][1].pop("change")), 1, "a move needs to (the target) and change"),
    ("move unknown decision", edit(lambda s: s["proposal"]["moves"][0].update(decision="rewrite")), 1, "decision 'rewrite' unknown"),
    ("moves empty", edit(lambda s: s["proposal"].update(moves=[])), 0, "proposal moves is empty"),
    ("all components move", edit(lambda s: [m.update(decision="move", to="x", change="C1") for m in s["proposal"]["moves"]]), 0, "every component moves"),
    ("redesign with few moves", edit(lambda s: s.update(verdict="redesign")), 0, "verdict redesign but 2 of 5 components move"),
    ("tool without alternatives", edit(lambda s: C(s, 1).update(alternatives=C(s, 1)["alternatives"][:1])), 1, "give 2-3 alternatives to Amazon MWAA"),
    ("pick is an alternative", edit(lambda s: C(s, 1)["alternatives"][0].update(name="Amazon MWAA")), 1, "is both the pick and an alternative"),
    ("swap without signal", edit(lambda s: C(s, 1).pop("signal")), 1, "needs its signal"),
    ("alternatives without tool", edit(lambda s: C(s, 1).pop("tool")), 1, "alternatives without tool"),
    ("unknown pattern", edit(lambda s: C(s, 1).update(pattern="lift-and-shift")), 0, "pattern 'lift-and-shift' is not in patterns.md"),
    ("tool change not in moves", edit(lambda s: s["proposal"]["moves"].pop(3)), 0, "change C5 moves to GitHub Actions but no moves row"),
    ("technical section missing", edit(lambda s: s["proposal"]["technical"].pop("Operations")), 0, "say what changes in Operations"),
    ("technical stays line ok", edit(lambda s: s["proposal"]["technical"].update(Operations="Stays: same runbook; alerts as today.")), 0, "0 WARN"),
    ("technical wrong block", edit(lambda s: s["proposal"]["technical"]["Operations"].append({"type": "er", "title": "x"})), 1, "block 'er' not allowed"),
    ("technical unknown section", edit(lambda s: s["proposal"]["technical"].update(Testing="stays")), 1, "'Testing' unknown"),
    ("tool move without Tests", edit(lambda s: s["proposal"]["technical"].pop("Tests")), 0, "add Tests"),
    ("security section ok", edit(lambda s: s["proposal"]["technical"].update({"Security and access": "Stays: deploy role only."})), 0, "0 WARN"),
    ("later without until", edit(lambda s: s["proposal"]["moves"][4].pop("until")), 0, "later needs until"),
    ("later blocker unchecked", edit(lambda s: s["proposal"]["moves"][4].update(why="auto-ingest of nested files unchecked")), 0,
     "'unchecked' in why: check the blocker in Snowpipe auto-ingest"),
    ("question leaves a blocker unchecked", edit(lambda s: s["questions"].append("Can Snowpipe load nested JSON? Not verified.")), 0,
     "'Not verified': check a tool"),
    ("move whose change has no tool", edit(lambda s: s["proposal"]["moves"][0].update(decision="move", to="SQLMesh")), 0,
     "moves to SQLMesh but its change C1 names no tool"),
    ("3 free fixes, later without until", edit(lambda s: ([C(s, i).update(free_in="Snowpipe") for i in (0, 2, 3)], s["proposal"]["moves"][4].pop("until"))), 0,
     "come free in Snowpipe"),
    ("smaller option not chosen", edit(lambda s: (s["proposal"]["options"][0].update(size="3 models, 4 tasks → ~200 lines, 4 tasks"),
                                                  s["proposal"]["options"][1].update(size="~400 lines, 4 tasks → ~150 lines, 2 tasks"))), 0,
     "option 'Move transforms to Spark' ends smaller than the chosen"),
    ("smaller option with why_not ok", edit(lambda s: (s["proposal"]["options"][0].update(size="3 models, 4 tasks → ~200 lines, 4 tasks",
                                                                                          why_not="Spark needs a second platform; docs page: Snowpark limits"),
                                                       s["proposal"]["options"][1].update(size="~400 lines, 4 tasks → ~150 lines, 2 tasks"))), 0, "0 WARN"),
    ("no typical workflow", edit(lambda s: [e.update(case="edge") for w in s["workflows"] for sd in ("current", "proposed") for e in w[sd]["examples"]]), 0,
     "workflows: none is typical"),
    ("old pick left in a tied text", edit(lambda s: s["impact"][3].update(proposed="Astronomer Hosted, smallest size")), 0,
     "name Astronomer, an alternative, not the pick Amazon MWAA"),
    ("proposed strip without why", edit(lambda s: [x.pop("why", None) for x in W(s, 0, "proposed")["steps"]]), 0, "give `why` on the steps"),
    ("High fix late", edit(lambda s: M(s, 4).pop("wait")), 0, "migration 5 fixes a High problem after step 1"),
    ("TODO left", edit(lambda s: C(s, 1)["tool"].update(why="TODO: why")), 1, "TODO left"),
    ("components row shape", edit(lambda s: s["proposal"]["components"].append(["x"])), 1, "use [component, responsibility, where]"),
    ("current keep row needs no alternatives", edit(lambda s: s["proposal"]["moves"][0].update(current=True) or s["proposal"]["moves"][0].pop("alternatives")), 0, "0 WARN"),
    ("current on a move row", edit(lambda s: [m.update(current=True) for m in s["proposal"]["moves"] if m["decision"] == "move"][:1]), 1, "current (latest version, fits the target) means keep"),
    ("goes_with unknown change", edit(lambda s: C(s, 0).update(goes_with=["C9"])), 1, "goes_with 'C9' is no other change id"),
    ("change with no fixes but goes_with ok", edit(lambda s: C(s, 4).update(fixes=[], goes_with=["C1"])), 0, "built"),
    ("goes_with ok", edit(lambda s: C(s, 0).update(goes_with=["C2"])), 0, "0 WARN"),
    ("keep row without alternatives", edit(lambda s: s["proposal"]["moves"][0].pop("alternatives")), 0, "move 1 (dbt marts): no alternatives"),
    ("move row alternatives from its change ok", edit(lambda s: s["proposal"]["moves"][1].pop("alternatives", None)), 0, "0 WARN"),
    ("row alternatives malformed", edit(lambda s: s["proposal"]["moves"][0].update(alternatives=[{"name": "x"}])), 1, "give 2-3 alternatives, each"),
    ("option without size", edit(lambda s: s["proposal"]["options"][1].pop("size")), 0, "option 'Move transforms to Spark': no size"),
    ("3 fixes free in an unmoved tool", edit(lambda s: [C(s, i).update(free_in="SQLMesh") for i in (0, 2, 3)]), 0, "come free in SQLMesh"),
    ("free fixes with a later row ok", edit(lambda s: [C(s, i).update(free_in="Snowpipe") for i in (0, 2, 3)]), 0, "0 WARN"),
    ("workflow needs unknown change", edit(lambda s: s["workflows"][0].update(needs=["C9"])), 1, "change 'C9' is no change id"),
    ("subtitle form", edit(lambda s: s.update(subtitle="Airflow and dbt")), 0, "subtitle should read"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fails, n = 0, 0

    def report(name, ok, out=""):
        nonlocal fails, n
        n += 1
        fails += not ok
        print(("PASS" if ok else "FAIL"), name, "" if ok else f"\n  output:\n  {out.strip()[:700]}")

    code, out, page, marker = build(BASE)
    ok = (code == 0 and "0 WARN" in out and "Verdict: evolve" in out and "- C1 Incremental marts — cost:" in out and marker
          and page.count('class="pb"') == 10 and "Diagram D" in page and 'id="ex-5.1b"' in page and 'id="st-4.1.1"' in page
          and 'id="st-5.1p.1"' not in page and "quick win" in page and "file scan (no graph)" in page and "Keep, move, later" in page
          and "<b>Alternatives:</b> Snowflake Tasks" in page and "Main flow 4.2" in page and "Accuracy: not reviewed" in out
          and "2 move, 2 keep, 1 later" in out and "<h3>Operations</h3>" in page and 'title="infra/snowflake/warehouses.tf:5-9">warehouses.<wbr>tf:5-9' in page
          and 'id="M3"' in page and "Alternatives: Fivetran or Airbyte" in page and "<b>Size:</b>" in page and "Until: a dashboard" in page
          and "now measured &middot; effect by design" in page and "<h3>Tests</h3>" in page and "3 edits → 1 per rule change (measured)" in out)
    report("valid spec: counts, links, ids, terminal block, marker", ok, out)
    for name, spec, want_code, want in CASES:
        code, out, _, _ = build(spec)
        report(name, code == want_code and want in out, f"exit {code}\n  {out}")
    code, out, _, _ = build(BASE, out="nope/a.html")
    report("missing output folder", code == 1 and "output folder nope does not exist" in out, out)
    code, out, _, _ = build(BASE, inv={"tests": ["tests/test_orders.py"]})
    report("all traces synthetic while the repo has tests: WARN", "every trace is synthetic but the inventory lists 1 test files" in out, out)
    code, out, _, _ = build(BASE, facts=False)
    report("no inventory is a WARN", "WARN no inventory.json next to the spec" in out, out)
    code, out, page, marker = build(BASE, empty=True)
    report("empty folder: checks skipped, no marker", code == 0 and "note: no repo files" in out and "0 WARN" in out and not marker, out)
    code, out, page, _ = build(BASE, git=True)
    report("git: commit stamp", code == 0 and ("repo not in git" in page or "repo " in page), out)
    d = repo(git=True)  # --changed: sections citing files edited since the page's commit
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(BASE), encoding="utf-8")
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=d, capture_output=True)
    g("add", "-A"), g("commit", "-qm", "x")
    run = lambda *a: subprocess.run([sys.executable, str(BUILD), *a, "generated-docs/_spec/a.json", "generated-docs/a.html"], cwd=d,
                                    capture_output=True, text=True, encoding="utf-8")
    run()
    (d / "infra/airflow/vm.tf").write_text("changed\n" * 20, encoding="utf-8")
    r = run("--changed")
    shutil.rmtree(d, ignore_errors=True)
    report("--changed names sections citing edited files", r.returncode == 0 and "3 Problems: infra/airflow/vm.tf changed" in r.stdout
           and "6 Impact: infra/airflow/vm.tf" in r.stdout, r.stdout + r.stderr)
    d = repo()  # --checklist writes the accuracy items; the build counts the ticked ones
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(BASE), encoding="utf-8")
    run = lambda *a: subprocess.run([sys.executable, str(BUILD), *a], cwd=d, capture_output=True, text=True, encoding="utf-8")
    r1 = run("--checklist", "generated-docs/_spec/a.json")
    f = d / "generated-docs/_spec/architecture-checklist.md"
    r2 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    f.write_text(f.read_text(encoding="utf-8").replace("- [ ] ", "- [x] "), encoding="utf-8")
    r3 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    report("--checklist: unticked items WARN, all ticked pass", "items, 0 ticked" in r1.stdout and "checklist items not ticked" in r2.stdout
           and "0 WARN" in r3.stdout and "Accuracy: " in r3.stdout and " of " in r3.stdout, r1.stdout + r2.stdout + r3.stdout)
    r4 = run("--use", "generated-docs/_spec/a.json", "C2", "dagster+")
    sp = json.loads((d / "generated-docs/_spec/a.json").read_text(encoding="utf-8"))
    r5 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    c2 = sp["proposal"]["changes"][1]
    report("--use: alternative becomes the pick, short names and tied texts listed, TODO stops the build",
           c2["tool"]["name"] == "Dagster+" and c2["alternatives"][1]["name"] == "Amazon MWAA" and sp["proposal"]["moves"][1]["to"] == "Dagster+"
           and "rewrite proposal.changes[1].title: Scheduler on MWAA" in r4.stdout and "rewrite migration[4].step" in r4.stdout
           and "check impact[2].proposed" in r4.stdout and r5.returncode == 1 and "TODO left" in r5.stdout + r5.stderr,
           r4.stdout + r4.stderr + r5.stdout + r5.stderr)
    sp["proposal"]["changes"][1]["tool"]["why"] = "asset lineage across extract and dbt"
    sp["proposal"]["changes"][1]["alternatives"][1]["tradeoff"] = "managed Airflow; DAG code moves unchanged"
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(sp), encoding="utf-8")
    r5 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    left = int(re.search(r"(\d+) checklist items not ticked", r5.stdout)[1]) if "checklist items not ticked" in r5.stdout else 0
    report("--use: texts still naming the old pick WARN; tied impact, migration, option and workflow items lose their ticks",
           r5.returncode == 0 and "name Amazon MWAA, an alternative, not the pick Dagster+" in r5.stdout
           and "proposal C2.title" in r5.stdout and "migration[4].step" in r5.stdout and left >= 12, r5.stdout + r5.stderr)
    r6 = run("--use", "generated-docs/_spec/a.json", "C2", "Kestra")
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(BASE), encoding="utf-8")
    r7 = run("--use", "generated-docs/_spec/a.json", "M3", "DuckDB or Polars")
    m3 = json.loads((d / "generated-docs/_spec/a.json").read_text(encoding="utf-8"))["proposal"]["moves"][2]
    r9 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    report("--use on a keep row: old pick = the current tool, its in-place change cleared, the build asks for a change",
           r7.returncode == 0 and m3["decision"] == "move" and m3["to"] == "DuckDB or Polars" and "TODO" in m3["why"] and "change" not in m3
           and m3["alternatives"][2]["name"] == "Python + pandas" and "add a change (tool DuckDB or Polars" in r7.stdout and "C3 was this row's change" in r7.stdout
           and "rewrite current.hotspots[1].value" in r7.stdout and r9.returncode == 1 and "a move needs to (the target) and change" in r9.stdout + r9.stderr,
           r7.stdout + r7.stderr + r9.stdout + r9.stderr)
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(BASE), encoding="utf-8")
    r10 = run("--use", "generated-docs/_spec/a.json", "M1", "SQLMesh")
    m1 = json.loads((d / "generated-docs/_spec/a.json").read_text(encoding="utf-8"))["proposal"]["moves"][0]
    report("--use on a keep row tuned in place: no move rides on the tuning change",
           r10.returncode == 0 and m1["to"] == "SQLMesh" and "change" not in m1 and m1["alternatives"][0]["name"] == "dbt on Snowflake"
           and "C1 was this row's change" in r10.stdout, r10.stdout + r10.stderr)
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(BASE), encoding="utf-8")
    run("--checklist", "generated-docs/_spec/a.json")
    f.write_text(f.read_text(encoding="utf-8").replace("- [ ] ", "- [x] "), encoding="utf-8")
    sp = copy.deepcopy(BASE)
    sp["migration"][0], sp["migration"][1] = sp["migration"][1], sp["migration"][0]
    (d / "generated-docs/_spec/a.json").write_text(json.dumps(sp), encoding="utf-8")
    r8 = run("generated-docs/_spec/a.json", "generated-docs/a.html")
    report("--checklist: reordered steps lose their ticks", "2 checklist items not ticked" in r8.stdout, r8.stdout + r8.stderr)
    report("--use: unknown alternative says how to add one", r6.returncode == 1 and "is not one of its alternatives" in r6.stderr
           and "add it to alternatives" in r6.stderr, r6.stderr)
    shutil.rmtree(d, ignore_errors=True)
    code, out, _, _ = build(edit(lambda s: P(s, 4).update(detail='`api_key = "abc123"`')))
    report("secret value not echoed", "abc123" not in out, out)
    for name, docs in (("docs-v2 incompatible", "LATE = []\nesc = str\n"), ("docs-v2 missing", None)):
        fake = Path(tempfile.mkdtemp()) / "skills"
        shutil.copytree(SKILL, fake / "darshan-singh-meel-architecture")
        (fake / "darshan-singh-meel-docs-v2").mkdir()
        if docs:
            (fake / "darshan-singh-meel-docs-v2/references/templates").mkdir(parents=True)
            (fake / "darshan-singh-meel-docs-v2/references/templates/build.py").write_text(docs, encoding="utf-8")
            (fake / "darshan-singh-meel-docs-v2/references/templates/style.css").write_text("", encoding="utf-8")
        code, out, page, _ = build(BASE, build=fake / "darshan-singh-meel-architecture/references/templates/build.py")
        shutil.rmtree(fake.parent, ignore_errors=True)
        ok = (code == 0 and "0 WARN" in out and "note: docs-v2" in out and "Layout not checked" in out
              and page.count("Diagram drawn as text") == 3 and "int_order_revenue" in page and "Snowflake Tasks" in page
              and "clear the failed task" in page and 'id="ex-5.1b"' in page and "--red:" in page)
        report(f"{name} → built-in style, text diagrams and strips", ok, out)
    print(f"{n - fails}/{n} passed")
    sys.exit(1 if fails else 0)


main()
