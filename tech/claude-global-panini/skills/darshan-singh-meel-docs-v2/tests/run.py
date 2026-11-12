"""Tests for docs-v2 build.py / check.py / inventory.py. Usage: python run.py [skill folder] (default: this skill's folder).
Builds fake repos in a temp folder (outside any git repo); check.py tests need Playwright."""
import atexit, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
SKILL = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
T = SKILL / "references" / "templates"
W = Path(tempfile.mkdtemp(prefix="docs-v2-tests-"))
atexit.register(shutil.rmtree, W, ignore_errors=True)
sys.dont_write_bytecode = True  # no __pycache__ inside the skill
sys.path.insert(0, str(T)); import build
sys.stdout.reconfigure(encoding="utf-8")
ok = bad = 0
LAST = build.LAST


def check(name, cond, info=""):
    global ok, bad
    ok, bad = (ok + 1, bad) if cond else (ok, bad + 1)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"\n     {str(info)[:1500]}"))


def repo(path, files, git=False):
    shutil.rmtree(path, onerror=lambda f, x, e: (os.chmod(x, 0o777), f(x))) if path.exists() else None
    path.mkdir(parents=True)
    for f, t in files.items():
        (path / f).parent.mkdir(parents=True, exist_ok=True); (path / f).write_text(t, encoding="utf-8")
    if git:
        for c in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"]):
            subprocess.run(["git", *c], cwd=path, capture_output=True)


def run(cwd, spec, out="generated-docs/doc.html"):
    sp = cwd / "generated-docs/_spec/doc.json"; sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(spec), encoding="utf-8")
    r = subprocess.run([sys.executable, str(T / "build.py"), str(sp), out], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout + r.stderr, r.returncode


def inventory(cwd, *args):
    r = subprocess.run([sys.executable, str(T / "inventory.py"), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout + r.stderr, r.returncode


def page(cwd):
    return (cwd / "generated-docs/doc.html").read_text(encoding="utf-8")


item = lambda t, **k: {"case": "typical", "title": t, "expect": "e", "in": [["k", "v"]], "out": "o", **k}
two = lambda **k: [item("t", **k), item("u", case="edge")]
trace = lambda items: [dict(c, at=c.get("at", ["1"])) for c in items]  # ipo examples: one `at` per step
ipo = lambda items=None, steps=1, **k: {"type": "ipo", "input": "i", "steps": [{"do": "s", "out": "1 row", "why": "w"}] * steps, "output": "o",
                                       "examples": trace(items or two()), **k}
mf = lambda items=None, h3="in → out", extra=(): [{"type": "h3", "text": h3}, ipo(items), *extra]
box = lambda i="a", **k: {"id": i, "label": i, "col": 0, "row": 0, **k}


def auto_ids(spec):
    """Give every diagram without id the next letter and a valid title, in document order."""
    names = sorted(spec["sections"], key=lambda n: (build.ORDER["technical"] + [LAST]).index(n))
    k = 0
    for n in names:
        for b in build.flat(spec["sections"][n]):
            if b["type"] in ("flow", "er", "journey"):
                b.setdefault("id", chr(65 + k)); k += 1
                if n == "Main flows" and b["type"] == "flow" and not b.get("parent"):
                    continue  # Main flows titles are written by the build
                if n in ("Architecture", "Screens and navigation", "Endpoints", "Commands", "Events and messages") and not b.get("parent"):
                    b.setdefault("numbered", False)  # maps: "<area> area", no numbers (plan diagram_titles)
                    b.setdefault("title", f"e{k} area")
                b.setdefault("title", "ER: x" if b["type"] == "er" else f"j, {len(b['stages'])} stages" if b["type"] == "journey"
                             else f"inside {b['parent'][1]}" if b.get("parent") else f"e{k}, {len(b['edges'])} steps" if b.get("edges") else f"e{k} area")
    return spec


def tech(sections, auto=True, **kw):
    base = {"Overview": [{"type": "text", "text": "x"}, {"type": "flow", "nodes": [box()]}],
            "Architecture": [{"type": "flow", "nodes": [box()]}, {"type": "components", "rows": []}],
            "Main flows": mf(),
            "Deploy and environments": [{"type": "steps", "rows": []}, {"type": "environments", "rows": []}],
            "Operations": [{"type": "symptoms", "rows": []}]}
    base.update(sections)
    spec = {"type": "technical", "app_types": [], "title": "t", "subtitle": "py · daily · src → out", "sections": base, **kw}
    return auto_ids(spec) if auto else spec


FILES = {"src/jobs/load_orders.py": "def load_orders_job():\n    merge_newest_wins()\n" + "x = 1\n" * 8,  # 10 lines
         "src/common/utils.py": "def helper_function(): pass\n", "tests/utils.py": "LOOKBACK_DAYS = 2\n",
         "sql/views.sql": "CREATE VIEW export.sales_orders AS SELECT * FROM clean.order_lines;\n",
         "pkg/run_process.py": "def main(): pass\n", ".env": "SECRET_ONLY_IN_ENV=1\n", "README.md": "# r\n",
         "secrets/notes.txt": "ONLY_IN_SECRET_FOLDER = 1\n", ".docker/config.json": '{"ONLY_IN_DOCKER_CFG": 1}\n'}

# ---- 1 citations (non-git folder) ----
R1 = W / "r1"; repo(R1, FILES)
spec = tech({"Architecture": [{"type": "flow", "nodes": [box()]},
    {"type": "components", "rows": [["a", "b", "`src/jobs/load_orders.py:5`"], ["a", "b", "`src/jobs/load_orders.py:11`"],
     ["a", "b", "jobs/load_orders.py"], ["a", "b", "`utils.py`"], ["a", "b", "`views.sql:1`"], ["a", "b", "`nothere.py`"],
     ["a", "b", "`src/jobs/load_orders.py:2-40`"], ["a", "b", "`src/jobs/load_orders.py:3,4,12`"], ["a", "b", "`.env:9`"],
     ["a", "b", "`spark.sql(q)` and `jobs/*.py` and `generated-docs/_spec/<doc>.json` and `pyspark.sql.functions`"],
     ["a", "b", "`../outside/x.py:1`"], ["a", "b", "`/abs/x.py`"]]}],
    "Main flows": mf([item("t", source="tests/missing_test.py:3"), item("u", case="edge")])})
out, rc = run(R1, spec)
check("cite: line inside file ok", ":5`" not in out, out)
check("cite: line past EOF -> ERROR", "ERROR Architecture: `src/jobs/load_orders.py:11` is past the end of the file (10 lines)" in out, out)
check("cite: non-root path -> ERROR + hint", "`jobs/load_orders.py` is not in the repo (did you mean src/jobs/load_orders.py?)" in out, out)
check("cite: bare name 2 matches -> WARN", "WARN Architecture: file name `utils.py` matches 2 repo files" in out, out)
check("cite: bare name 1 match ok", "views.sql" not in out, out)
check("cite: bare name 0 matches -> WARN", "file name `nothere.py` matches 0 repo files" in out, out)
check("cite: range end past EOF -> ERROR", "`src/jobs/load_orders.py:2-40` is past the end" in out, out)
check("cite: comma list past EOF -> ERROR", "`src/jobs/load_orders.py:3,4,12` is past the end" in out, out)
check("cite: secret file line not read", ".env" not in out, out)
check("cite: code/globs/placeholders not paths", not re.search(r"spark\.sql|\*\.py|<doc>|pyspark", out), out)
check("cite: example source checked", "`tests/missing_test.py` is not in the repo" in out, out)
check("cite: ../ and absolute paths -> ERROR (L6)", "`../outside/x.py` is absolute or leaves the repo" in out and "`/abs/x.py` is absolute" in out, out)
check("cite: errors stop build", rc != 0, out)

# ---- 2 identifiers ----
spec = tech({"Performance and limits": [{"type": "bullets", "items": [
    "`load_orders_job` `merge_newest_wins()` `LOOKBACK_DAYS` `clean.order_lines` `run_process.main` `helper_function(x, y)`",
    "`load_orders_jobs` `Load_Orders_Job` `SECRET_ONLY_IN_ENV` `staging_<env>` `made_up_name` `export.sales_ordersX` `only_in_spec_token`",
    "`tbl_*_suffix` `{name}_job` `short_x` `ONLY_IN_SECRET_FOLDER` `ONLY_IN_DOCKER_CFG`"]}]}, ids_skip=["made_up_name"])
out, rc = run(R1, spec)
miss = set(re.findall(r"`([^`]+)` not found in repo", out))
check("ids: real names found (word, call, dotted, module.func)", not miss & {"load_orders_job", "merge_newest_wins", "LOOKBACK_DAYS", "clean.order_lines", "run_process.main", "helper_function"}, out)
check("ids: wrong / wrong case / secret-only / spec-only -> WARN", {"load_orders_jobs", "Load_Orders_Job", "SECRET_ONLY_IN_ENV", "export.sales_ordersX", "only_in_spec_token"} <= miss, out)
check("ids: placeholders, globs, ids_skip, short skipped", not miss & {"staging_<env>", "made_up_name", "tbl_*_suffix", "{name}_job", "short_x"}, out)
check("ids: secret folder and .docker/config.json never read (L7)", {"ONLY_IN_SECRET_FOLDER", "ONLY_IN_DOCKER_CFG"} <= miss, out)

# ---- 3 coverage vs inventory (graph has nodes only: sparse) ----
long = "very_long_table_name_that_the_box_will_shorten_in_the_middle_for_sure_yes_indeed_and_more_and_more"
nodes = [{"id": "t1", "type": "task", "name": "load_orders", "path": "src/jobs/load_orders.py"},
         {"id": "t2", "type": "task", "name": "explode_lines", "path": "src/jobs/x.py"},
         {"id": "t3", "type": "table", "name": long, "path": "sql/views.sql"},
         {"id": "t4", "type": "table", "name": "fixture_table", "path": "tests/fixtures.sql"},
         {"id": "t5", "type": "table", "name": "test_orders", "path": "sql/t.sql"},
         {"id": "t6", "type": "view", "name": "skipped_view", "path": "sql/views.sql"},
         {"id": "t7", "type": "function", "name": "not_counted", "path": "x.py"},
         {"id": "t8", "type": "task", "name": "Checkout", "path": ".github/workflows/ci.yml"},
         {"id": "d1", "type": "dag", "name": "orders_dag", "path": "src/jobs/load_orders.py"}]
spec = tech({"Overview": [{"type": "text", "text": "runs load_orders"}, {"type": "flow", "nodes": [{"id": "a", "label": long, "col": 0, "row": 0}]}],
             "Main flows": mf(h3="Scheduled run → written data")}, coverage_skip={"skipped_view": "internal"})
out, rc = run(R1, spec)
check("coverage: no graph -> WARN coverage not checked (H2)", "WARN coverage not checked: no generated-docs/_spec/inventory.json (no .knowledge-graph pointer and no r1-knowledge-graph/graph/ folder): run python <skill>/references/templates/inventory.py (no graph: it plans from a file scan)" in out, out)
(R1 / "r1-knowledge-graph/graph").mkdir(parents=True, exist_ok=True)
(R1 / "r1-knowledge-graph/graph/nodes.jsonl").write_text("\n".join(json.dumps(n) for n in nodes), encoding="utf-8")
out, rc = run(R1, spec)
check("coverage: graph but no inventory -> WARN with the command", "WARN coverage not checked: no generated-docs/_spec/inventory.json: run python <skill>/references/templates/inventory.py" in out, out)
iout, irc = inventory(R1)
check("inventory: sparse graph (no edges, no meta) works and says what was not checked", irc == 0 and "note: graph/edges.jsonl missing" in iout and "meta.json missing" in iout, iout)
inv = json.loads((R1 / "generated-docs/_spec/inventory.json").read_text(encoding="utf-8"))
check("inventory: CI task flagged, tests and test_ names left out", [x.get("ci") for x in inv["items"]["task"] if x["name"] == "Checkout"] == [True]
      and "fixture_table" not in json.dumps(inv["items"]) and "test_orders" not in json.dumps(inv["items"]), inv["items"])
check("inventory: no flows -> one plan h3", [m["h3"] for m in inv["plan"]["main_flows"]] == ["Scheduled run → written data"], inv["plan"])
out, rc = run(R1, spec)
check("coverage: missing task -> WARN with name", "WARN coverage: 1 of 2 task items from inventory.json are not in the visible text: explode_lines" in out, out)
check("coverage: name only in a hover tip does not count (H4)", f"table items from inventory.json are not in the visible text: {long}" in out, out)
check("coverage: tests/, test_, CI, skip, other types ignored", not re.search(r"fixture_table|test_orders|skipped_view|not_counted|Checkout",
      "|".join(x for x in out.splitlines() if "coverage" in x)), out)
check("plan: required sections from the profile", "WARN missing section: Job DAG and schedule" in out and "WARN missing section: Data model" in out, out)
check("plan: app_types differ -> WARN", "WARN app_types [] differ from the plan's ['pipeline']" in out, out)
check("built line counts WARN (L3)", re.search(r"built generated-docs/doc.html: \d+ sections, \d+ WARN", out), out)
spec2 = tech({"Endpoints": [{"type": "flow", "nodes": [box()]}, {"type": "endpoints", "rows": []}], "Main flows": mf(h3="Scheduled run → written data")})
out, rc = run(R1, spec2)
check("plan: section not applicable -> ERROR (one rule: leave it out)", "ERROR Endpoints: not applicable to this repo (no endpoint nodes in the graph; plan in inventory.json): leave the section out" in out, out)
spec2 = tech({"Main flows": mf(h3="Other → thing")})
out, rc = run(R1, spec2)
check("plan: Main flows h3 differ from plan -> ERROR", "ERROR Main flows: h3 titles must be the plan's, in order" in out and "want ['Scheduled run → written data'], got ['Other → thing']" in out, out)
ug = {"type": "user-guide", "app_types": ["pipeline"], "title": "u", "subtitle": "a · b · c → d", "sections": {
      "How it reaches you": [{"type": "flow", "id": "A", "title": "a area", "nodes": [box()]}],
      "How to x": [{"type": "steps", "rows": [["a", "b"]]}, {"type": "examples", "items": two()}],
      "Problems and fixes": [{"type": "problems", "rows": []}], "Who to contact": [{"type": "bullets", "items": ["x"]}]}}
out, rc = run(R1, ug)
check("coverage: only technical docs", "coverage" not in out and rc == 0, out)
check("graph folder excluded from repo files", "r1-knowledge-graph" not in out, out)
shutil.rmtree(R1 / "generated-docs/_spec"); shutil.rmtree(R1 / "r1-knowledge-graph")

# ---- 4 hand-shortened names ----
spec = tech({"Overview": [{"type": "text", "text": "x"}, {"type": "flow", "nodes": [{"id": "a", "label": "load_or…ders", "col": 0, "row": 0},
      {"id": "b", "label": "Fan-out", "sub": "x_...", "col": 1, "row": 0}, {"id": "c", "label": "…", "col": 2, "row": 0}],
      "groups": [{"label": "Repeats for each …", "nodes": ["c"]}]}],
    "Data model": [{"type": "er", "entities": [{"id": "e", "name": "gld_..._orders", "cols": [["id", "PK"]]}]}, {"type": "views", "rows": [["`v_…_x`", "a", "1:1"]]}],
    "Main flows": mf([item("t", **{"in": "calls `merge(...)` and more…"}), item("u", case="edge")])},
    tabs={"does": ["writes `a_…_b`"]})
out, rc = run(R1, spec)
check("cut: box label/sub -> ERROR", "'load_or…ders'" in out and "'x_...'" in out, out)
check("cut: ER name -> ERROR", "'gld_..._orders'" in out, out)
check("cut: table cell -> ERROR", "'`v_…_x`'" in out, out)
check("cut: tabs -> ERROR", "tabs: hand-shortened name 'writes `a_…_b`'" in out, out)
check("cut: prose and code args not flagged", "merge(" not in out and "Repeats" not in out and "name '…'" not in out, out)

# ---- 5 diagram ids and titles ----
fl = lambda i, **k: {"type": "flow", **({"id": i} if i else {}), **k, "nodes": [box()]}
spec = tech({"Overview": [{"type": "text", "text": "x"}, fl("B", title="first area")],
             "Architecture": [fl("A", title="Diagram 1 · arch"), {"type": "components", "rows": []}],
             "Data model": [{"type": "er", "id": "C", "title": "ER: area", "entities": [{"id": "e", "name": "t", "cols": [["id", "PK"]]}]},
                            {"type": "er", "title": "ER: no id", "entities": [{"id": "e", "name": "t", "cols": [["id", "PK"]]}]}, {"type": "views", "rows": []}],
             "Main flows": [{"type": "h3", "text": "a → b"}, ipo(),
                            {"type": "flow", "id": "E", "nodes": [box(see="Z")]},
                            {"type": "flow", "id": "D", "title": "inside a", "parent": ["E", "a"], "nodes": [box()]}]}, auto=False)
out, rc = run(R1, spec)
check("ids: order across flows/ERs/journeys -> ERROR", "diagram ids must run ['A', 'B', 'C', 'D', 'E'] in document order" in out and "got ['B', 'A', 'E', 'D', 'C']" in out, out)
check("ids: title starting Diagram -> ERROR", "title 'Diagram 1 · arch' starts with 'Diagram'" in out, out)
check("ids: title without id -> ERROR (M4)", "ERROR Data model: er 'ER: no id' needs an id (next letter) and a title" in out, out)
check("ids: see to unknown id -> ERROR", "see/parent 'Z' is not a diagram id" in out, out)
s = spec["sections"]
s["Overview"][1]["id"], s["Architecture"][0]["id"], s["Architecture"][0]["title"] = "A", "B", "arch area"
s["Data model"].pop(1); s["Main flows"][2]["id"], s["Main flows"][3]["id"], s["Data model"][0]["id"] = "C", "D", "E"
s["Main flows"][3]["parent"][0] = "C"
s["Main flows"][2]["nodes"][0]["see"] = "A"
out, rc = run(R1, spec)
check("ids: valid sequence builds; prefix written", rc == 0 and "Diagram E &middot; ER: area" in page(R1), out)
spec = tech({"Overview": [{"type": "text", "text": "x"}, {"type": "flow", "nodes": [box()]}],
             "Architecture": [{"type": "flow", "id": "B", "title": "two boxes, 2 steps", "nodes": [box(), box("b", col=1)], "edges": [{"from": "a", "to": "b"}]}, {"type": "components", "rows": []}],
             "Main flows": [{"type": "h3", "text": "a → b"}, ipo(),
                            {"type": "flow", "id": "C", "title": "wrong", "parent": ["B", "a"], "nodes": [box()]}],
             "Data model": [{"type": "er", "id": "D", "title": "orders area", "entities": [{"id": "e", "name": "t", "cols": [["id", "PK"]]}]}, {"type": "views", "rows": []}]},
            auto=False)
out, rc = run(R1, spec)
check("titles: flow without id and title -> ERROR (M4)", "ERROR Overview: flow '(no id, no title)' needs an id" in out, out)
check("titles: '<entry>, <N> steps' counts arrows (N6)", "flow title must be '<entry>, 1 steps' (N = its arrows) or '<area> area', got 'two boxes, 2 steps'" in out, out)
check("titles: sub-flow must be 'inside <box>'", "sub-flow title must be 'inside a', got 'wrong'" in out, out)
err = []; build.diagram_ids({"sections": {"Example": [{"type": "journey", "id": "A", "title": "j, 2 stages", "stages": [{"title": "s", "rows": [["a", "b"]]}]}]}},
                           ["Example"], err, [], None)
check("titles: journey must be '<entry>, <N> stages'", any("journey title must be '<entry>, 1 stages', got 'j, 2 stages'" in e for e in err), err)
check("titles: ER must be 'ER: <area>'", "ER title 'orders area' must be 'ER: <area>'" in out, out)

# ---- 6 unused + steps cols ----
spec = tech({"Deploy and environments": [{"type": "steps", "cols": ["Step", "Command / CI job"], "rows": [["a", "b"]]}, {"type": "environments", "rows": []}],
             LAST: [{"type": "issues", "items": []}, {"type": "unused", "rows": [["`README.md`", "no link", "Not verified"], ["x", "y"]]}]})
out, rc = run(R1, spec)
check("steps: other cols -> ERROR", "steps columns are fixed here" in out, out)
check("steps: row length vs fixed cols -> ERROR", "steps row has 2 cells, want 3" in out, out)
check("unused: row length -> ERROR", "unused row has 2 cells, want 3" in out, out)
spec["sections"]["Deploy and environments"][0] = {"type": "steps", "rows": [["Test", "`pytest`", "CI"]]}
spec["sections"][LAST][1]["rows"].pop()
out, rc = run(R1, spec)
check("steps/unused: fixed headers rendered; 1-2 typed rows -> inline list", rc == 0 and "<th>Where it runs</th>" in page(R1) and "<h3>Unused files</h3>" in page(R1)
      and '<span class="k">Why it looks unused</span> no link' in page(R1) and "<th>Why it looks unused</th>" not in page(R1), out)
spec["sections"][LAST][1]["rows"] = [["`README.md`", w, "Not verified"] for w in ("no link", "no import", "no ref")]
out, rc = run(R1, spec)
check("typed table with 3 rows stays a table; a column with one value for all rows is said once above it",
      rc == 0 and "<th>Why it looks unused</th>" in page(R1) and "<th>Status</th>" not in page(R1)
      and '<p class="key allrows">All rows: <b>Status</b> = <span class="chip nv">Not verified</span></p>' in page(R1), out)
spec["sections"][LAST].insert(1, {"type": "h3", "text": "Unused files"})
out, rc = run(R1, spec)
check("unused: old h3+table form -> recipe ERROR", "recipe `text? issues unused? assumptions? decisions?`" in out, out)

# ---- 7 wrapping ----
e = build.esc("LandingToConsolidatedJob v4.0.0 x_job.py:38-63", True)
check("wrap: CamelCase break points", "Landing<wbr>To<wbr>Consolidated<wbr>Job" in e, e)
check("wrap: versions and ranges never broken", '<span class="nw">4.0.0</span>' in e and '<span class="nw">38-63</span>' in e and "4.<wbr>" not in e, e)
check("wrap: nlines splits CamelCase, keeps versions whole", build.nlines("LandingToConsolidatedJob", 14) == 3 and build.nlines("ab 4.0.0", 6) == 2, "")

# ---- 8 examples ----
spec = tech({"Main flows": mf(h3="one → a") + mf(h3="two → b", items=[item(f"t{i}", case="edge" if i else "typical") for i in range(4)])
             + mf(h3="three → c", items=[item("no expect", expect=""), {"case": "typical", "title": "no in", "expect": "e", "out": "o"}])
             + mf(h3="four → d", items=[item("edge first", case="edge"), item("odd", case="weird"), item("tagged", tag="5.1a")])
             + mf(h3="five → e", items=[item("alone")])})
out, rc = run(R1, spec)
check("examples: missing expect or in -> ERROR, no traceback (H7)", "ERROR Main flows: example 1 'no expect' needs expect" in out and "example 2 'no in' needs in" in out and "Traceback" not in out, out)
check("examples: >3 in Main flows -> ERROR (M1)", "ERROR Main flows: 4 examples under 'two → b' (max 3 per flow)" in out, out)
check("examples: first not typical -> ERROR", "example a under 'four → d' must be the typical case, got 'edge'" in out, out)
check("examples: unknown case -> ERROR", "unknown case 'weird'" in out, out)
check("examples: id in tag -> ERROR (H6)", "tag '5.1a' looks like an id" in out, out)
check("examples: one card -> WARN", "WARN Main flows: examples under 'five → e': want 2-3," in out, out)
spec = tech({"Main flows": mf(h3="one → a") + mf(h3="two → b", items=[item("x"), item("y", case="failure", source="README.md:1", synthetic=True)]),
             "Business rules": [{"type": "rules", "rows": [["r", "`a` 1 → 2", "keeps 1", "b"], ["s", "see step 3.2.1", "drops 2", ""], ["t", "x 3 → 4", "keeps 3", "c"]]}]})
out, rc = run(R1, spec)
p = page(R1)
check("examples: ids per section.h3 + letter", rc == 0 and all(x in p for x in ('id="ex-3.1a"', '<span class="id">3.1b</span>', 'id="ex-3.2a"', 'id="ex-3.2b"')), out + str(re.findall(r"ex-[\w.]+", p)))
check("rules: one row per rule (Rule · Example in → out · Why / impact · Where), step pointer links to the strip step",
      "<th>Rule</th><th>Example in &rarr; out</th><th>Why / impact</th><th>Where</th>" in p and '<a href="#st-3.2.1">step 3.2.1</a>' in p
      and 'id="st-3.2.1"' in p and 'class="extab"' not in p, out)
build.POS.update(sec=4, h3=0, ex=0)
check("examples: no h3 -> section + letter", build.ex_id() == "4a", "")
check("examples: EXPECT on traces", '<span class="lbl2">EXPECT</span>' in p, "")
spec = tech({"Main flows": mf(items=[item("a"), item("b", case="edge"), item("c", case="edge"), item("d", case="edge")])})
out, rc = run(R1, spec)
check("examples: max 3 per Main flows h3", "max 3 per flow" in out, out)

# ---- 9 git repo: untracked counted, ignored not, output folder never searched ----
R2 = W / "r2"; repo(R2, {**FILES, ".gitignore": "ignored/\n"}, git=True)
(R2 / "new_untracked.py").write_text("untracked_name_here = 1\n", encoding="utf-8")
(R2 / "ignored").mkdir(); (R2 / "ignored/x.py").write_text("ignored_name_here = 1\n", encoding="utf-8")
spec = tech({"Performance and limits": [{"type": "bullets", "items": ["`untracked_name_here` `ignored_name_here` `in_spec_only_name` `new_untracked.py:1`"]}]})
run(R2, spec)
out, rc = run(R2, spec)  # second run: the first build's html and the spec must not count as repo files
miss = set(re.findall(r"`([^`]+)` not found in repo", out))
check("git: untracked found, ignored and spec-only not", miss == {"ignored_name_here", "in_spec_only_name"} and "new_untracked" not in out, out)

# ---- 10 no repo files (examples) -> skipped quietly ----
R3 = W / "r3"; shutil.rmtree(R3, ignore_errors=True); R3.mkdir(parents=True)
sp = W / "r3spec.json"
sp.write_text(json.dumps(tech({"Performance and limits": [{"type": "bullets", "items": ["`src/none.py:4` `no_such_name_x`"]}]})), encoding="utf-8")
for k in (1, 2):
    r = subprocess.run([sys.executable, str(T / "build.py"), str(sp), f"o{k}.html"], cwd=R3, capture_output=True, text=True, encoding="utf-8")
    check(f"no repo files: checks skipped (run {k})", r.returncode == 0 and "note: no repo files" in r.stdout and "WARN" not in r.stdout.replace("0 WARN", ""), r.stdout + r.stderr)
check("output is pure ASCII (M8)", (R3 / "o1.html").read_bytes().isascii() and "&#8594;" in (R3 / "o1.html").read_text(encoding="utf-8"), "")

# ---- 11 check.py: crowded arrow ends, group-border crossings, line crossings, details, shots ----
H = ('<!doctype html><html><head><style>{}</style></head><body><main><section><h2>x</h2><h3 id="d-Q">Diagram Q</h3><div class="map-wrap"><div class="map" '
     'style="width:600px;height:400px">{}<svg width="600" height="400">{}</svg>{}</div></div></section>{}</main></body></html>')
css = (T / "style.css").read_text(encoding="utf-8")
grp = '<div class="grp" style="left:200px;top:40px;width:200px;height:120px"><span style="width:40px">g</span></div>'
lines = ('<polyline points="20,300 100,300 100,200" fill="none" stroke="#000"/><polyline points="20,330 106,330 106,200" fill="none" stroke="#000"/>'
         '<polyline points="250,20 250,220" fill="none" stroke="#000"/><polyline points="260,20 260,220" fill="none" stroke="#000"/>'
         '<polyline points="450,20 450,220" fill="none" stroke="#000"/>')
boxes = '<div class="b" style="left:60px;top:150px;width:120px;height:50px">box</div>'
closed = '<details><summary>s</summary><div class="card"><p style="width:20px;white-space:nowrap;overflow:hidden">aaaaaaaaaaaaaaaaaaaaaaaaa</p></div></details>'
(W / "crowd.html").write_text(H.format(css, grp, lines, boxes, ""), encoding="utf-8")
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "crowd.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: arrow ends 6px apart on one side", "arrows 1 and 2 end 6px apart on one side" in r.stdout, r.stdout)
check("check.py: LAYOUT line names the diagram id and map number (L4)", "LAYOUT x | diagram Q (map-1) | arrows 1 and 2" in r.stdout, r.stdout)
check("check.py: lines cross group border 10px apart", "edges 3 and 4 cross the group border 10px apart" in r.stdout and "edges 4 and 5" not in r.stdout, r.stdout)
cross = "".join(f'<polyline points="{x},10 {x},390" fill="none" stroke="#000"/>' for x in (300, 340)) + \
        "".join(f'<polyline points="280,{y} 380,{y}" fill="none" stroke="#000"/>' for y in (250, 290))
(W / "cross.html").write_text(H.format(css, "", cross, "", closed), encoding="utf-8")
shots = W / "shots"; shutil.rmtree(shots, ignore_errors=True)
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "cross.html"), str(shots)], capture_output=True, text=True, encoding="utf-8")
check("check.py: 4 crossings in one diagram -> LAYOUT (M11)", "4 line crossings in one diagram (max 3)" in r.stdout, r.stdout)
check("check.py: closed details are opened and measured (M11)", "value cut off" in r.stdout, r.stdout)
check("check.py: one shot per diagram + page (M12)", (shots / "page.png").is_file() and (shots / "map-1.png").is_file(), r.stdout)

# ---- 12 inventory.py on synthetic graphs ----
R4 = W / "r4"; repo(R4, {"README.md": "# r\n"})
iout, irc = inventory(R4)
check("inventory: no graph -> file-scan plan + note, exit 0", irc == 0 and "note: no knowledge graph: plan from a file scan; build the graph for flows and coverage" in iout, iout)
RN = W / "rn"; repo(RN, {"src/shop/cli.py": "def main():\n    pass\n", "src/shop/core.py": "def parse(t):\n    return t\n\n\ndef _x():\n    pass\n",
                         "dags/orders_daily.py": "x = 1\n", "app/routes/orders.py": "x = 1\n", "frontend/src/pages/Home.tsx": "x\n",
                         "pyproject.toml": "[project]\nname = 'shop'\n[project.scripts]\nshop = 'shop.cli:main'\n",
                         "tests/test_core.py": "def test_x(): pass\n", ".github/workflows/ci.yml": "on: push\n", ".env": "TOKEN=1\n",
                         "secrets/key.py": "def leak(): pass\n", "infra/main.tf": "x\n", "infra/modules/net/main.tf": "x\n"})
iout, irc = inventory(RN)
ni = json.loads((RN / "generated-docs/_spec/inventory.json").read_text(encoding="utf-8"))
h3s = [m["h3"] for m in ni["plan"]["main_flows"]]
check("no graph: one Main flows h3 per program, app, job or root (script + cli.py merged), no flows (M6)",
      irc == 0 and ni.get("scan") and ni["graph"] == "" and ni["flows"] == []
      and {"orders_daily: Scheduled run → written data", "app: HTTP request → response", "shop: Command line → output",
           "frontend: User action → screen", "infra: Terraform root → cloud resources"} == set(h3s)
      and ni["plan"]["main_flows"][2]["files"] == ["pyproject.toml", "src/shop/cli.py"]
      and len(h3s) == len(set(h3s)) and all(not m["diagram"] and m["steps"] == 0 for m in ni["plan"]["main_flows"]), (iout, h3s))
check("no graph: kinds, CI file as deploy unit, tests, config; secrets never read",
      {"pipeline", "web_api", "cli", "ui", "infra"} <= {k["kind"] for k in ni["profile"]} and ni["plan"]["deploy"]["units"] == [".github/workflows/ci.yml"]
      and ni["tests"] == ["tests/test_core.py"] and [x["name"] for x in ni["items"]["config"]] == ["pyproject.toml"]
      and ".env" not in json.dumps(ni) and "leak" not in json.dumps(ni) and "infra/modules/net" not in h3s, ni["profile"])
check("no graph: no section ruled out, coverage only of scanned types",
      all(d["not_applicable"] == {} for d in ni["plan"]["sections"].values()) and "flow" not in ni["plan"]["coverage"]
      and {"config", "test_file", "endpoint", "cli_command"} <= set(ni["plan"]["coverage"]), ni["plan"]["coverage"])
mfs = [b for h in h3s for b in ({"type": "h3", "text": h}, ipo())]
spec = tech({"Main flows": mfs}, app_types=ni["plan"]["app_types"])
out, rc = run(RN, spec)
check("no graph: build accepts the scan plan (plan h3s, note), coverage WARN names scanned items",
      rc == 0 and "note: inventory.json is from a file scan" in out and "Main flows: h3 titles" not in out
      and "pyproject.toml" in out.split("coverage:", 1)[-1] and "orders_daily" not in out.split("coverage:", 1)[-1], out)
(R4 / ".knowledge-graph").write_text("missing-folder", encoding="utf-8")
iout, irc = inventory(R4)
check("inventory: pointer to a missing folder -> clear exit", irc != 0 and ".knowledge-graph points to missing-folder" in iout, iout)
g = R4 / "g"; (g / "graph").mkdir(parents=True); (R4 / ".knowledge-graph").write_text("g", encoding="utf-8")
iout, irc = inventory(R4)
check("inventory: graph without nodes.jsonl -> clear exit", irc != 0 and "nodes.jsonl is missing" in iout, iout)
tbl = lambda n, **k: {"id": f"table:{n}", "type": "table", "name": n, "path": f"sql/{n}.sql", "line_start": 1, **k}
N = [tbl(f"t{i:02d}") for i in range(14)] + [tbl("u1"), tbl("u2"), 
    {"id": "flow:b", "type": "flow", "name": "Order load", "path": "src/b.py", "line_start": 5, "summary": "landing file -> orders table"},
    {"id": "flow:a", "type": "flow", "name": "Export", "path": "src/a.py", "line_start": 9},
    {"id": "function:x", "type": "function", "name": "read_file", "path": "src/a.py", "line_start": 1},
    {"id": "function:y", "type": "function", "name": "write_out", "path": "src/a.py", "line_start": 3},
    {"id": "endpoint:1", "type": "endpoint", "name": "GET /orders", "path": "src/api.py", "line_start": 2},
    {"id": "tc", "type": "test_case", "name": "test_x", "path": "tests/test_a.py", "line_start": 1}, {"bad": "node without id"}]
E = [{"from": "function:y", "to": "flow:a", "type": "part_of", "step": 2}, {"from": "function:x", "to": "flow:a", "type": "part_of", "step": 1},
     {"from": "table:t01", "to": "table:t00", "type": "fk"}, {"from": "table:t02", "to": "table:t01", "type": "fk"}] + \
    [{"from": f"table:t{i:02d}", "to": "table:t03", "type": "fk"} for i in range(4, 14)]
(g / "graph/nodes.jsonl").write_text("\n".join(json.dumps(n) for n in N), encoding="utf-8")
(g / "graph/edges.jsonl").write_text("\n".join(json.dumps(e) for e in E), encoding="utf-8")
(g / "meta.json").write_text('{"commit": "abc"}', encoding="utf-8")
iout, irc = inventory(R4)
a = (R4 / "generated-docs/_spec/inventory.json").read_bytes(); fa = (R4 / "generated-docs/_spec/facts.json").read_bytes()
inventory(R4)
check("inventory: deterministic (byte-identical twice)", irc == 0 and a == (R4 / "generated-docs/_spec/inventory.json").read_bytes()
      and fa == (R4 / "generated-docs/_spec/facts.json").read_bytes(), iout)
inv = json.loads(a)
check("inventory: flows in inventory order, steps by step number", [f["name"] for f in inv["flows"]] == ["Export", "Order load"]
      and [s["name"] for s in inv["flows"][0]["steps"]] == ["read_file", "write_out"], inv["flows"])
check("inventory: h3 from steps and from the summary chain", [m["h3"] for m in inv["plan"]["main_flows"]] == ["Export", "Order load: landing file → orders table"], inv["plan"]["main_flows"])
areas = [(x["title"], len(x["tables"])) for x in inv["plan"]["er_areas"]]
check("inventory: ER areas = root + descendants, merged <=9, cut in parts of 9", areas == [("ER: t00", 3), ("ER: t03 (part 1)", 9), ("ER: t03 (part 2)", 2), ("ER: u1 + 1 more", 2)], areas)
check("inventory: profile and not-applicable sections", [k["kind"] for k in inv["profile"]] == ["web_api"]
      and "Commands" in inv["plan"]["sections"]["technical"]["not_applicable"] and "Endpoints" in inv["plan"]["sections"]["technical"]["required"], inv["profile"])
check("inventory: tests listed apart, graph path relative, facts with how", inv["tests"] == ["tests/test_a.py"] and inv["graph"] == "g"
      and all("inventory.json" in f["how"] and f["how"].startswith("python -c") for f in json.loads(fa)["facts"]), json.loads(fa))

# ---- 13 issues, top issues, subtitle, absolute paths, review age, facts, M9, M10, loose boxes, long words, L2 ----
R5 = W / "r5"; repo(R5, {**FILES, "reviews/code-review.md": "# review\n"}, git=False)
iss = lambda sev, st="Confirmed (review)", where="`src/jobs/load_orders.py:1-2`", issue="`merge_newest_wins` drops rows": \
    {"sev": sev, "issue": issue, "where": where, "impact": "x", "status": st, "fix": "y"}
spec = tech({LAST: [{"type": "issues", "items": [iss("Must"), iss("Should", "Fixed since review"), iss("Should", issue="`helper_function` is slow")]}],
             "Business rules": [{"type": "rules", "rows": [["`LOOKBACK_DAYS` window", "1 → 2", "late rows kept", "`src/jobs/load_orders.py:1`"]]}],
             "Architecture": [{"type": "flow", "nodes": [box("load_orders", kind="code"), box("made_up_box", kind="code", col=1), box("c", col=2),
                                                         box("x" * 60, col=3, **{"in": "y" * 40})],
                               "edges": [{"from": "load_orders", "to": "made_up_box"}, {"from": "load_orders", "to": "x" * 60}]},
                              {"type": "components", "rows": []}]},
            subtitle="no form here", review="reviews/code-review.md",
            tabs={"top_issues": [{"text": "fixed one", "status": "Fixed since review"}],
                  "does": [r"writes C:\Users\someone\out.csv and /home/me/x"]})
out, rc = run(R5, spec)
check("top issues: count = min(10, open Must+Should) -> WARN (M6)", "WARN top issues: 1 given, want min(10, open Must + Should) = 2" in out, out)
check("top issues: fixed one listed -> WARN (H5)", "top issues: ['fixed one'] are fixed since the review" in out, out)
check("subtitle form -> WARN (L5)", "WARN subtitle 'no form here': want" in out, out)
check("absolute paths in text -> WARN (L6)", "absolute or machine paths in the spec" in out and "/home/me/x" in out and "C:\\\\Users" in out or "C:\\Users" in out, out)
check("cited lines hold none of the row names -> WARN (M9)", "WARN Business rules: `src/jobs/load_orders.py:1` holds none of ['LOOKBACK_DAYS']" in out
      and "helper_function" in out and "holds none of ['merge_newest_wins']" not in out, out)
check("code box label not in repo -> WARN (M10)", "code box 'made_up_box' not found in repo" in out and "box 'load_orders'" not in out, out)
check("box without arrow -> WARN (M11)", "boxes without an arrow: ['c']" in out, out)
check("unbreakable long text in a box -> WARN (M11)", "breaks mid-word" in out, out)
check("facts.json missing -> WARN (M13)", "WARN no generated-docs/_spec/facts.json: run python <skill>/references/templates/inventory.py" in out, out)
check("built with WARN only", rc == 0 and '<span class="chip fx">Fixed since review</span>' in page(R5), out)
(R5 / "generated-docs/_spec/facts.json").write_text(json.dumps({"facts": [{"fact": "a", "value": 1, "how": "python ../scratch/count.py"},
    {"fact": "b", "value": 2, "how": "python <skill>/references/templates/inventory.py"}, {"fact": "c", "value": 3, "how": "python tools/missing.py"}]}), encoding="utf-8")
out, rc = run(R5, spec)
check("facts: how outside the repo or missing -> WARN, <skill> ok (M13)", "'a': how" in out and "'c': how" in out and "'b': how" not in out, out)
subprocess.run(["git", "init", "-q"], cwd=R5); subprocess.run(["git", "add", "-A"], cwd=R5)
subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"], cwd=R5)
out, rc = run(R5, spec)
check("review committed with the code -> no age WARN; mtime ignored (N13)", "is older than the last code change" not in out, out)
(R5 / "src/common/utils.py").write_text("def helper_function(): pass\n# changed\n", encoding="utf-8")
subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "later", "--date", "2099-01-01T00:00:00"], cwd=R5,
               env={**os.environ, "GIT_COMMITTER_DATE": "2099-01-01T00:00:00"})
out, rc = run(R5, spec)
check("review older than the last code commit (git log) -> WARN (H5, N13)", "review reviews/code-review.md is older than the last code change" in out, out)
for bad_spec, want in ((dict(spec, type="tech"), "ERROR type 'tech' unknown"), ({k: v for k, v in spec.items() if k != "title"}, "ERROR the spec needs a title"),
                       (tech({"Performance and limits": [{"type": "nope"}]}), "ERROR Performance and limits: recipe `bullets`, got `nope`")):
    out, rc = run(R5, bad_spec)
    check(f"spec mistake -> ERROR line, no traceback (L2): {want[:30]}", want in out and "Traceback" not in out and rc != 0, out)
out, rc = run(R5, {"type": "custom", "title": "c", "sections": {"A": [{"type": "nope"}]}})
check("unknown block in custom -> ERROR line (L2)", "ERROR unknown block type 'nope'" in out and "Traceback" not in out, out)

# ---- round 3 rules (N1-N28) ----
import inventory as inv
check("parts: no lone extension or short tail (N14)", build.parts("ci.yml") == ["ci.yml"] and build.parts("get_db") == ["get_db"], build.parts("get_db"))
check("parts: long word in a box keeps its one break point (N14)", build.parts("vorversicherungen_id") == ["vorversicherungen_", "id"], build.parts("vorversicherungen_id"))
check("parts: table cell keeps every break point", build.parts("get_db", box=False) == ["get_", "db"], build.parts("get_db", box=False))
check("crossings: plus shape = 1, parallel = 0", build.crossings([[(0, 5), (10, 5)], [(5, 0), (5, 10)]]) == 1
      and build.crossings([[(0, 5), (10, 5)], [(0, 8), (10, 8)]]) == 0)
check("rel: path outside cwd -> folder name only (N28)", inv.rel(Path(os.path.abspath(os.sep)) / "zz_outside" / "g") == "g")
check("is_test_file: a process node on a test path is not a test (N7)",
      inv.is_test_file({"type": "function", "path": "tests/test_a.py"}) and not inv.is_test_file({"type": "process", "path": "tests/test_a.py"}))
P = lambda ns, es=(): [x["kind"] for x in inv.profile(ns, list(es))]
check("profile: in-process timer is no pipeline; dag is (N20)",
      "pipeline" not in P([{"id": "t", "type": "function", "name": "timer"}]) and "pipeline" in P([{"id": "d", "type": "dag", "name": "d"}]))
check("profile: schedules edge into a job -> pipeline (N20)",
      "pipeline" in P([{"id": "s", "type": "schedule", "name": "s"}, {"id": "j", "type": "job", "name": "j", "path": "jobs/j.py"}],
                      [{"from": "s", "to": "j", "type": "schedules"}]))
check("topo: one order from calls/reads edges, None when ambiguous",
      inv.topo(["a", "b", "c"], [{"from": "a", "to": "b", "type": "calls"}, {"from": "c", "to": "b", "type": "reads"}]) == ["a", "b", "c"]
      and inv.topo(["a", "b", "c"], [{"from": "a", "to": "b", "type": "calls"}]) is None)
byid = {"f": {"id": "f", "summary": ""}}
check("h3: unordered flow keeps its name; ordered steps that are functions too (N3)",
      inv.h3({"id": "f", "name": "Deploy", "ordered": False, "steps": [{"name": "a"}, {"name": "b"}]}, byid) == "Deploy"
      and inv.h3({"id": "f", "name": "Deploy", "ordered": True, "steps": [{"name": "a", "type": "function"}, {"name": "b", "type": "function"}]}, byid) == "Deploy")
N3 = [{"id": "f1", "type": "flow", "name": "ui", "path": "a"}, {"id": "f2", "type": "flow", "name": "api", "path": "b"},
      {"id": "s", "type": "ui_screen", "name": "S"}, {"id": "e", "type": "endpoint", "name": "GET /x"}]
E3 = [{"from": "s", "to": "f1", "type": "part_of", "step": 1}, {"from": "e", "to": "f2", "type": "part_of", "step": 1}]
check("flows: endpoint flow sorts before ui flow (N23)", [f["name"] for f in inv.flows(N3, E3, {n["id"]: n for n in N3})] == ["api", "ui"])
plan = {"main_flows": [{"h3": "A: x → y", "flow": "f", "steps": 3, "ordered": True, "diagram": True, "entry": "x"},
                       {"h3": "B", "flow": "g", "steps": 2, "ordered": False, "diagram": False, "entry": None}]}
fl = lambda **k: {"type": "flow", "id": "Z", "nodes": [box("x"), box("y", col=1), box("z", col=2), box("w", col=3), box("f", col=1, row=1, kind="fail")],
                  "edges": [{"from": "x", "to": "y", "step": 1}, {"from": "y", "to": "z", "step": 2}, {"from": "z", "to": "w", "step": 3},
                            {"from": "x", "to": "f", "fail": True, "label": "404"}], **k}
st = lambda n: {"type": "ipo", "steps": [{"do": "s", "out": "1 row", "branch": "404", "why": "w"}] + [{"do": "s", "out": "1 row"}] * (n - 1)}
def mfc(blocks, spec=None):
    err, warn = [], []; build.NOTES.clear(); build.main_flows(spec or {}, blocks, plan, err, warn); return err, warn, blocks
err, warn, bl = mfc([{"type": "h3", "text": "A: x → y"}, st(3), fl(), {"type": "h3", "text": "B"}, st(2)])
check("main flows: plan h3s, generated title '<h3>, N steps': the flow, not a box (N4/N6, M6)", not err and not warn and bl[2]["title"] == "A: x → y, 3 steps", (err, warn))
err, _, _ = mfc([{"type": "h3", "text": "A: x → y"}, st(3), {"type": "h3", "text": "B"}, st(2), fl()])
check("main flows: missing diagram (true) and extra diagram (false) -> ERROR (N4)",
      any("needs a flow diagram" in e for e in err) and any("has no diagram in the plan" in e for e in err), err)
err, _, _ = mfc([{"type": "h3", "text": "A: x → y"}, st(3), fl(title="my title"), {"type": "h3", "text": "B"}, st(2)])
check("main flows: own title -> ERROR (build writes it)", any("a Main flows title is written by the build" in e for e in err), err)
err, warn, _ = mfc([{"type": "h3", "text": "A: x → y"}, st(1), fl(), {"type": "h3", "text": "B"}, st(2)])
check("main flows: arrows vs ipo steps and ipo steps != plan steps -> WARN (N22)",
      not any("numbered arrows" in w for w in warn) and any("cover graph steps [1], the graph flow has 3 ordered steps" in w for w in warn), warn)
err, _, _ = mfc([{"type": "h3", "text": "Other"}, st(3), fl(), {"type": "h3", "text": "B"}, st(2)],
                {"h3_override": {"A: x → y": {"title": "Other", "why": "graph names the wrong entry"}}})
check("main flows: h3_override with why -> note, no ERROR", not err and build.NOTES and "shown as 'Other'" in build.NOTES[0], (err, build.NOTES))
err, _, _ = mfc([{"type": "h3", "text": "Other"}, st(3), fl(), {"type": "h3", "text": "B"}, st(2)], {"h3_override": {"A: x → y": {"title": "Other"}}})
check("main flows: h3_override without why -> ERROR", any("h3_override 'A: x → y'" in e for e in err), err)
err = []; build.operations_tasks([{"type": "tasks", "rows": [["Rerun and backfill", "x", "y"], ["Run tests", "x", "y"]]}],
                                {"how_tos": ["Run tests"], "rerun_and_backfill": False}, err, [])
check("operations: Rerun and backfill only for pipelines; how-to from plan ok (N16)", len(err) == 1 and "for pipelines and dbt only" in err[0], err)
iss = lambda st, sev="Must": {"type": "issues", "items": [{"issue": "i", "sev": sev, "status": st, "where": "`a`", "fix": "f"}]}
for spec_, want in (({"sections": {LAST: [iss("Confirmed")]}}, "must be one of"),
                    ({"sections": {LAST: [iss("Confirmed (review)")]}}, "no review is named"),
                    ({"review": "reviews/r.md", "sections": {LAST: [iss("Confirmed (review)")]}, "tabs": {"top_issues": [{"text": "i", "status": "Confirmed (review)"}]}}, None)):
    err, warn = [], []; build.top_issues(spec_, err, warn)
    check(f"statuses enum, review-only statuses need a review (N5): {want}", (want in " ".join(err)) if want else not err and not warn, (err, warn))
h = build.tabs({"sections": {LAST: [iss("Not verified", "Other")]}})
check("tabs: empty Top issues names the other items, not 'No known issues'", "No open Must or Should issue (not reviewed): 1 other item under Known issues" in h, h[-400:])
pi = build.paths_in("see `My Folder/a b.py:3`", {"My Folder/a b.py"})
check("paths_in: backticked repo path with spaces found whole (N2)", pi == [("My Folder/a b.py", "3")], pi)
import hashlib
R9 = W / "r9"; repo(R9, {"src/a.py": "x = 1\n", "src/b.py": "y = 2\n", ".env": "K=1\n"})
cwd0 = os.getcwd(); os.chdir(R9)
meta = {"file_hashes": {"src/a.py": hashlib.sha256(b"x = 1\n").hexdigest()[:12], "src/b.py": "deadbeef", "src/gone.py": "abc", ".env": "abc"}}
got = inv.stale(meta); os.chdir(cwd0)
check("stale: changed + deleted files, secrets never read (N8)", got == ["src/b.py", "src/gone.py (deleted)"], got)
(R9 / "generated-docs/_spec").mkdir(parents=True, exist_ok=True)
(R9 / "generated-docs/_spec/facts.json").write_text(json.dumps({"facts": [
    {"fact": "ok", "value": 1, "how": "grep -c 'def ' src/a.py"}, {"fact": "re", "value": 1, "how": r"grep -cE 'a\.py' src/a.py"},
    {"fact": "q", "value": 1, "how": "wc -l \"src/missing.py\""}]}), encoding="utf-8")
warn = []; build.facts_warn(R9 / "generated-docs/_spec/doc.json", R9, ["src/a.py"], warn)
check("facts: shlex tokens, regex with backslash is no path, missing quoted path -> WARN (N12)",
      len(warn) == 1 and "'q'" in warn[0] and "src/missing.py" in warn[0], warn)
ex = lambda syn: {"type": "examples", "items": [item("t", synthetic=syn), item("u", case="edge", synthetic=syn)]}
warn = []; build.synthetic_share({"sections": {"Main flows": [{"type": "h3", "text": "a → b"}, ex(True)]}}, ["Main flows"], ["tests/t.py"], warn)
check("synthetic share: card a synthetic and > 1/3 synthetic with tests -> WARN (N18)",
      any("example a under 'a → b' is synthetic" in w for w in warn) and any("2 of 2 cards are synthetic" in w for w in warn), warn)
spec = tech({"Main flows": [{"type": "h3", "text": "in → out"}, ipo(steps=1, input="see Example 3.1z9")]})
out, rc = run(R9, spec)
check("example reference the doc does not have -> ERROR (N17)", "names Example 3.1z9" in out and rc != 0, out)
spec = tech({"Architecture": [{"type": "flow", "nodes": [box("d", kind="decision"), box("e", col=1)], "edges": [{"from": "d", "to": "e"}]},
                              {"type": "components", "rows": []}]})
out, rc = run(R9, spec)
check("decision box with 1 outgoing arrow -> WARN", "decision box 'd' has 1 outgoing arrow" in out, out)
spec = tech({"Data model": [{"type": "er", "entities": [{"id": f"t{i}", "name": f"t{i}", "grain": "one row per t", "cols": [["id", "PK"]]} for i in range(5)]}]})
out, rc = run(R9, spec)
check("ER without relations -> builds (grid, 3 per row) (N20)", "Traceback" not in out and "ERROR Data model" not in out and "diagram" not in out.split("ERROR")[-1][:0], out)

# ---- round 4 rules (verify-3: N3-N16 partly, M1-M6, L1-L7) ----
nd = lambda i, t, name, **k: {"id": i, "type": t, "name": name, **k}
fl3 = {"id": "f", "name": "Load", "ordered": True, "steps": [{"name": "read", "type": "function"}, {"name": "orders", "type": "table"}]}
check("h3: ordered flow ending on an output -> '<name> → <output>', never step functions (N3)",
      inv.h3(fl3, byid) == "Load → orders" and inv.h3(dict(fl3, steps=fl3["steps"][::-1]), byid) == "Load")
fls = [{"id": "a", "name": "Alpha: x", "steps": [{"name": "main"}]}, {"id": "b", "name": "Beta → y", "steps": [{"name": "main"}]},
       {"id": "c", "name": "Gamma", "steps": [{"name": "run"}]}]
mm = [{"h3": f["name"], "flow": f["id"], "diagram": True} for f in fls]
check("entries: a shared first step -> flow name head, unique titles (L1)", inv.entries(mm, fls) == ["Alpha", "Beta", "run"], inv.entries(mm, fls))
err, warn = build.check(tech({"Architecture": [{"type": "flow", "id": "B", "title": "a area", "numbered": False, "nodes": [box()]},
                                              {"type": "components", "rows": []}],
                              "Overview": [{"type": "flow", "id": "A", "title": "a area", "nodes": [box()]}]}, auto=False), "technical",
                        ["Overview", "Architecture", "Main flows", "Deploy and environments", "Operations"], None)
check("diagram titles must be unique -> ERROR (L1)", any("diagram title 'a area' is used 2 times" in e for e in err), err)
cmd = lambda **k: {"Commands": [{"type": "flow", "id": "B", "nodes": [box(), box("b", col=1)], "edges": [{"from": "a", "to": "b"}], **k},
                                {"type": "commands", "rows": []}]}
names_ = ["Overview", "Architecture", "Commands", "Main flows", "Deploy and environments"]
err, _ = build.check(tech(cmd(title="cli, 1 steps"), app_types=["cli"]), "technical", names_, None)
err2, _ = build.check(tech(cmd(title="cli area", numbered=False), app_types=["cli"]), "technical", names_, None)
check("title form fixed per section: Commands is a map (area, no numbers) (N4)",
      any("in Commands a flow is a map" in e for e in err) and not any("in Commands" in e for e in err2), (err, err2))
pl = {"main_flows": [{"h3": "A: x → y", "flow": "f", "steps": 4, "ordered": True, "diagram": True, "entry": "x", "boxes": ["x", "y", "z"]}]}
blk = [{"type": "h3", "text": "A: x → y"}, st(2), {"type": "flow", "id": "Z", "nodes": [box("x", kind="entry"), box("y", col=1, kind="code"),
       box("q", col=2, kind="code"), box("GET /e", col=3, kind="code")], "edges": [{"from": "x", "to": "y", "step": 1}, {"from": "y", "to": "q", "step": 2},
                                                                             {"from": "y", "to": "GET /e", "fail": True}]}]
build.ENTRIES.add("GET /e")
err, warn = [], []; build.main_flows({}, blk, pl, err, warn)
check("main flows: title N = arrows; rows != arrows -> WARN; code box not a plan step -> WARN, entry point ok (N4/N6)",
      blk[2]["title"] == "A: x → y, 2 steps" and not any("numbered arrows" in w for w in warn)
      and any("boxes ['q'] are not steps" in w for w in warn), (blk[2]["title"], warn))
sub = {"type": "flow", "id": "Y", "parent": ["Z", "y"], "title": "inside y", "nodes": [box()]}
err, warn = [], []; build.main_flows({}, blk[:3] + [dict(sub)], pl, err, warn)
err2, _ = [], []; build.main_flows({}, blk[:3] + [{k: v for k, v in sub.items() if k != "parent"}], pl, err2, [])
check("main flows: a sub-flow (parent) under an h3 is fine, a second top flow -> ERROR (M3)",
      not err and any("has a second flow" in e for e in err2) and build.fits(build.RECIPES["technical"]["Main flows"], ["h3", "ipo", "flow", "flow"]), (err, err2))
ki = lambda **k: {"issue": "x", "where": "`a`", "fix": "f", "status": "Not verified", **k}
for spec_, want in (({"sections": {LAST: [{"type": "issues", "items": [ki(sev="Must")]}]}}, "kind '' must be one of"),
                    ({"sections": {LAST: [{"type": "issues", "items": [ki(sev="Should", kind="security")]}]}}, "kind 'security' means sev 'Must'"),
                    ({"sections": {LAST: [{"type": "issues", "items": [ki(sev="Must", kind="security", status="Confirmed (test)")]}]}}, "Confirmed (test) needs"),
                    ({"sections": {LAST: [{"type": "issues", "items": [ki(sev="Question", kind="unclear_intent")]}]}}, None),
                    ({"review": "r.md", "sections": {LAST: [{"type": "issues", "items": [ki(sev="Other")]}]}}, None)):
    err, warn = [], []; build.top_issues(spec_, err, warn)
    check(f"severity from the issue kind, fixed rubric (N5): {want}", (want in " ".join(err)) if want else not err, err)
spec = tech({LAST: [{"type": "issues", "items": [ki(sev="Should", kind="missing_handling", issue="no `retry_config_value` set",
                                                     absent=["retry_config_value", "helper_function"])]}]},
            tabs={"top_issues": [{"text": "x", "status": "Not verified"}]})
out, rc = run(R9, spec)
check("issue absent names: not looked up; one in the repo -> WARN (N11)", "`retry_config_value` not found" not in out
      and "`helper_function` is listed as absent but is in the repo" not in out, out)
(R9 / "src/c.py").write_text("def helper_function(): pass\n", encoding="utf-8")
out, rc = run(R9, spec)
check("issue absent name that exists -> WARN (N11)", "`helper_function` is listed as absent but is in the repo" in out, out)
spec = tech({"Architecture": [{"type": "flow", "nodes": [box("src/", kind="code"), box("Postgres", kind="data", col=1), box("npm run dev", kind="entry", col=2)],
                               "edges": [{"from": "src/", "to": "Postgres"}, {"from": "npm run dev", "to": "src/"}]}, {"type": "components", "rows": []}]})
(R9 / "generated-docs/_spec/inventory.json").write_text(json.dumps({"templates": inv.version(), "items": {"external_system": [{"name": "postgres"}],
    "cli_command": [{"name": "npm run dev"}]}, "entry_points": [], "flows": [], "tests": [],
    "plan": {"coverage": [], "sections": {}, "main_flows": [{"h3": "in → out", "steps": 0, "diagram": False, "entry": None, "boxes": []}]}}), encoding="utf-8")
out, rc = run(R9, spec)
check("name check accepts a folder, a graph command name, an external system in any case (M1)", "not found in repo" not in out, out)
(R9 / "generated-docs/_spec/inventory.json").unlink()
P2 = lambda ns, es=(): inv.plan([k["kind"] for k in inv.profile(ns, list(es))], {"data_objects": [d for d in ns if d["type"] == "table"], "fks": [],
    "items": {"process": [inv.item(n) for n in ns if n["type"] == "process"]}, "flows": [], "entry_points": [], "_byid": {n["id"]: n for n in ns},
    "_tables": [], "_fks": [], "tests": []}, ns, list(es))
lib = [nd("m", "module", "pkg.api", path="src/pkg/api.py"), nd("f", "function", "load", path="src/pkg/api.py"), nd("g", "function", "_hidden", path="src/pkg/api.py"),
       nd("c", "class", "Reader", path="src/pkg/api.py"), nd("cm", "function", "Reader.read", path="src/pkg/api.py"), nd("i", "function", "load.inner", path="src/pkg/api.py"),
       nd("p", "process", "Release", path="pyproject.toml"), nd("t", "table", "only_one", path="x.sql")]
pl = P2(lib)
na = pl["sections"]["technical"]["not_applicable"]
check("library: public API (no _names, Class.method only) is a coverage type (M6)", [a["name"] for a in pl["api"]] == ["Reader", "Reader.read", "load"]
      and "api" in pl["coverage"], pl["api"])
check("library: no Operations, no how-tos; one table, no fk -> no Data model (N16)",
      "Operations" in na and "Data model" in na and pl["how_tos"] == [] and pl["er_areas"] == [], (na, pl["how_tos"]))
web = [nd("e", "endpoint", "GET /x", path="app.py"), nd("p", "process", "Test the backend", path="README.md", tags=["test"]),
       nd("q", "process", "Deploy", path="README.md"), nd("j", "job", "ci_check", path=".github/workflows/ci.yml"),
       nd("s", "terraform_resource", "aws_scheduler.x", path="main.tf"), nd("l", "function", "handler", path="h.py")]
pl = P2(web, [{"from": "s", "to": "l", "type": "schedules"}])
check("web service: test process -> how-to 'Run the tests'; Operations required (M2, N16)",
      pl["how_tos"] == ["Deploy", "Run the tests"] and "Operations" in pl["sections"]["technical"]["required"], pl["how_tos"])
check("deploy plan from CI jobs; a Terraform scheduler is a schedule (M4)", pl["deploy"]["units"] == [] and "Job DAG and schedule" in pl["sections"]["technical"]["required"]
      and pl["rerun_and_backfill"] is False, pl["deploy"])
check("a test-tagged process stays in items (M2)", not inv.is_test({"type": "process", "tags": ["test"], "path": "tests/x"}))
dep = {"deploy": {"units": ["ci_check"], "deploys": ["img → app"]}, "sections": {"technical": {"required": [], "not_applicable": {}}}}
err, warn = build.check(tech({"Deploy and environments": [{"type": "steps", "rows": [["run `img`", "x", "y"]]}]}, app_types=[]), "technical",
                        ["Overview", "Architecture", "Main flows", "Deploy and environments", "Operations"], dep)
check("Deploy must name each CI job and deploys edge source from the plan (M4)", any("['ci_check']" in w for w in warn), warn)
(R9 / "generated-docs/_spec/facts.json").write_text(json.dumps({"facts": [{"fact": "test files", "value": 3, "how": "python -c \"print(3)\""},
    {"fact": "endpoints", "value": 2, "how": "python -c \"print(5)\""}]}), encoding="utf-8")
spec = tech({"Tests": [{"type": "tests", "rows": []}, {"type": "bullets", "items": ["4 test files", "3 test files"]}]})
out, rc = run(R9, spec)
check("numbers in the text against facts.json (M5)", "text says '4 test files' but facts.json 'test files' is 3" in out
      and "'3 test files'" not in out, out)
r = subprocess.run([sys.executable, str(T / "inventory.py"), "--check-facts"], cwd=R9, capture_output=True, text=True, encoding="utf-8")
check("inventory.py --check-facts reruns each how, flags a mismatch (L5)", r.returncode == 1 and "ok test files = 3" in r.stdout
      and "MISMATCH endpoints: facts.json says 2, how printed '5'" in r.stdout, r.stdout + r.stderr)
err = []; build.ellipsis({"sections": {"A": [{"type": "table", "cols": ["a"], "rows": [["`Loading...`"], ["Saving…"]]}]},
                         "tabs": {}}, ["A"], err)
err2 = []; build.ellipsis({"sections": {"A": [{"type": "table", "cols": ["a"], "rows": [["`load_or...`"]]}]}, "tabs": {}}, ["A"], err2)
check("UI text with an ellipsis allowed, a cut name still ERROR (L3)", not err and err2, (err, err2))
out, rc = run(R9, tech({}), out="nowhere/doc.html")
check("missing output folder -> one ERROR line, no traceback (L6)", rc != 0 and "ERROR output folder nowhere does not exist" in out and "Traceback" not in out, out)
err, warn = [], []; build.operations_tasks([{"type": "tasks", "rows": [["Deploy", "x", "y"]]}], {"how_tos": ["Deploy", "Run the tests"], "rerun_and_backfill": False}, err, warn)
check("Operations: every plan how-to has a tasks row (M2)", not err and any("['Run the tests']" in w for w in warn), (err, warn))
# ---- round 5 rules (verify-4: A1-A3, N14) ----
dep = {"deploy": {"units": ["db", "Init"], "deploys": []}, "sections": {"technical": {"required": [], "not_applicable": {}}}}
dnames = ["Overview", "Architecture", "Main flows", "Deploy and environments", "Operations"]
_, warn = build.check(tech({"Deploy and environments": [{"type": "steps", "rows": [["run dbt Initial", "x", "y"]]}]}, app_types=[]), "technical", dnames, dep)
_, warn2 = build.check(tech({"Deploy and environments": [{"type": "steps", "rows": [["start `db`, then Init", "x", "y"]]}]}, app_types=[]), "technical", dnames, dep)
check("deploy units match as whole words: `db` not in `dbt` (A1)", any("['db', 'Init']" in w for w in warn)
      and not any("Deploy and environments: [" in w for w in warn2), (warn, warn2))
ci = [nd("j", "job", "build", path=".github/workflows/ci.yml"), nd("u", "task", "actions/checkout@v4", path=".github/workflows/ci.yml"),
      nd("v", "task", "Init", path=".github/workflows/ci.yml")]
pi = inv.plan([k["kind"] for k in inv.profile(ci, [])], {"data_objects": [], "fks": [], "items": {"job": [{**inv.item(ci[0]), "ci": True}],
     "task": [{**inv.item(n), "ci": True} for n in ci[1:]]}, "flows": [], "entry_points": [], "_byid": {n["id"]: n for n in ci},
     "_tables": [], "_fks": [], "tests": []}, ci, [])
check("a CI action reference is not a deploy unit (A1)", pi["deploy"]["units"] == ["build", "Init"], pi["deploy"])
(R9 / "src/svc.py").write_text("class TaskService: pass\n", encoding="utf-8")
box_spec = lambda lab: tech({"Architecture": [{"type": "flow", "nodes": [box(lab, kind="code")]}, {"type": "components", "rows": []}]})
out, _ = run(R9, box_spec("taskservice"))
out2, _ = run(R9, box_spec("TaskService"))
(R9 / "generated-docs/_spec/inventory.json").write_text(json.dumps({"templates": inv.version(), "items": {"external_system": [{"name": "postgres"}]},
    "entry_points": [], "flows": [], "tests": [], "plan": {"coverage": [], "sections": {}, "main_flows": [{"h3": "in → out", "steps": 0,
    "diagram": False, "entry": None, "boxes": []}]}}), encoding="utf-8")
out3, _ = run(R9, box_spec("Postgres"))
(R9 / "generated-docs/_spec/inventory.json").unlink()
check("one-word box label keeps its case; external system any case (A2)", "box 'taskservice' not found" in out
      and "not found in repo" not in out2 and "not found in repo" not in out3, (out, out2, out3))
(R9 / "generated-docs/_spec/facts.json").write_text(json.dumps({"facts": [{"fact": "views", "value": 17, "how": "python -c \"print(17)\""},
    {"fact": "views with deletion_time", "value": 6, "how": "python -c \"print(6)\""}]}), encoding="utf-8")
out, _ = run(R9, tech({"Tests": [{"type": "tests", "rows": []}, {"type": "bullets", "items": ["6 views with deletion_time", "17 views", "5 views"]}]}))
check("a sub-count matching a fact that names the noun passes; another number WARNs (A3)", "'6 views'" not in out and "'17 views'" not in out
      and "text says '5 views' but facts.json 'views' is 17" in out, out)
(R9 / "generated-docs/_spec/facts.json").unlink()
fo = {"type": "flow", "id": "F", "nodes": [box("s"), box("t1", col=1), box("t2", col=1, row=1), box("t3", col=1, row=2)],
      "edges": [{"from": "s", "to": x} for x in ("t1", "t2", "t3")]}
h = build.block(fo, "technical")
pts = [[tuple(map(int, p.split(","))) for p in q.split()] for q in re.findall(r'<polyline points="([^"]+)"', h)]
check("fan-out: arrows leaving one box side start at one point and share their track (N14)",
      len({q[0] for q in pts[1:]}) == 1 and len({q[1][0] for q in pts[1:]}) == 1 and build.crossings(pts) == 0, pts)
(W / "fan.html").write_text(f"<!doctype html><html><head><style>{css}</style></head><body><main><section><h2>x</h2>{h}</section></main></body></html>", encoding="utf-8")
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "fan.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: a fan-out tree is no overlap and no crowding (N14)", r.returncode == 0, r.stdout)
# ---- ipo (Main flows: input > steps > output + example traces) ----
spec = tech({"Main flows": [{"type": "h3", "text": "a → b"}, {"type": "ipo", "steps": [{"do": "read"}], "output": "o",
             "examples": [item("t", at=["x", "y"]), item("u", case="edge")]}]})
out, rc = run(R9, spec)
check("ipo: missing input, step out, at -> ERROR", "ipo under 'a → b' needs input" in out and "ipo step 1 under 'a → b' needs out" in out
      and "example 2 'u' needs at" in out and "'t': 2 `at` values, want one per step (1;" in out and rc != 0, out)
spec = tech({"Main flows": [{"type": "h3", "text": "a → b"}, ipo([item("t", at=["x", ""]), item("u", case="failure", at=["y", "z"], source="src/a.py:1")], steps=2)]})
out, rc = run(R9, spec)
p = page(R9)
check("ipo: strip Input > numbered steps > Output, one trace row per example, '' = unchanged",
      rc == 0 and '<ol class="ipo"><li class="io-in"><span class="lbl2">INPUT</span>' in p and p.count('<span class="n">') == 2
      and '<li class="io-out"><span class="lbl2">OUTPUT</span>' in p and "<th>Ex</th><th>In</th><th>1</th><th>2</th><th>Out</th>" in p
      and '<tr id="ex-3.1b" class="failure more">' in p and '<span class="tc">=</span>' in p and "3.1b src/<wbr>a.<wbr>py:1" in p, out)
check("ipo: Main flows takes ipo, no steps table or cards", not build.fits(build.RECIPES["technical"]["Main flows"], ["h3", "steps", "examples"]), "")
spec = tech({"Main flows": [{"type": "h3", "text": "a → b"}, dict(ipo(), steps=[{"do": "x", "out": "o", "where": "src/nope.py:3"}])]})
out, rc = run(R9, spec)
check("ipo: step where is a citation (checked)", "`src/nope.py:3` is not in the repo" in out or "`src/nope.py` is not in the repo" in out, out)
warn = []; build.synthetic_share({"sections": {"Main flows": [{"type": "h3", "text": "a → b"}, ipo([item("t", synthetic=True), item("u", case="edge")])]}},
                                 ["Main flows"], ["tests/t.py"], warn)
check("ipo: synthetic example a with tests -> WARN", any("example a under 'a → b' is synthetic" in w for w in warn), warn)

# ---- word budgets ----
long = lambda n: " ".join(["word"] * n)
spec = tech({"Overview": [{"type": "text", "text": "One. Two. Three."}, {"type": "flow", "nodes": [box()]}],
             "Architecture": [{"type": "text", "text": "Uses `alpha_one` and `beta_two` and `gamma_three`."},
                              {"type": "flow", "nodes": [box("alpha_one"), box("beta_two", col=1), box("gamma_three", col=2)]},
                              {"type": "components", "rows": [["c", long(41), "w"], ["c", "ok", "w"], ["c", long(45), "w"]]}],
             "Main flows": [{"type": "h3", "text": "a → b"},
                            dict(ipo([item("t", expect=long(13)), item("u", case="edge")]), steps=[{"do": long(9), "out": long(13)}])]})
names_ = ["Overview", "Architecture", "Main flows", "Deploy and environments", "Operations"]
_, warn = build.check(spec, "technical", names_, None)
check("budget: lead text > 2 sentences -> WARN", any("words: Overview: lead text has 3 words, 3 sentences" in w for w in warn), warn)
check("budget: lead that restates the next block -> WARN", any("words: Architecture: lead text names 3 of its 3 names again in the next flow" in w for w in warn), warn)
check("budget: table cells > 40 words -> one WARN with count and longest: split into fact + why",
      any("words: Architecture: 2 table cells over 40 words (longest 45:" in w and "split it into fact + why" in w for w in warn), warn)
check("budget: ipo do > 8, step output and trace value > 12 -> WARN",
      any("1 ipo step `do`s over 8 words (longest 9" in w for w in warn) and any("1 ipo step outputs over 12 words" in w for w in warn)
      and any("1 trace values over 12 words (longest 13" in w for w in warn), warn)
spec = tech({"Overview": [{"type": "text", "text": "Short lead, " + long(30) + "."}, {"type": "flow", "nodes": [box()]}]})
_, warn = build.check(spec, "technical", names_, None)
check("budget: lead within 2 sentences / 40 words -> no WARN", not any(w.startswith("words:") for w in warn), warn)

# ---- inline lists ----
spec = {"type": "user-guide", "app_types": [], "title": "t", "subtitle": "a · b · c → d",
        "sections": {"What answers what": [{"type": "table", "cols": ["Question"], "rows": [["Where is X?"], ["Who owns Y?"]]}],
                     "Problems and fixes": [{"type": "problems", "rows": [["No data", "Wait for 06:00"]]}]}}
out, rc = run(R9, spec)
p = page(R9)
check("lists: single-column table -> list; 1-row typed table -> one line, no table",
      "<ul><li>Where is X?</li><li>Who owns Y?</li></ul>" in p and '<ul class="rows"><li><b>No data</b> &middot; <span class="k">What to do</span> Wait for' in p
      and "<th>Problem</th>" not in p, out)
check("overview How it works: flow only (steps dropped)", not build.fits(build.RECIPES["overview"]["How it works"], ["flow", "steps"])
      and build.fits(build.RECIPES["overview"]["How it works"], ["flow"]), "")

# ---- plan: a Main flows diagram only for a flow that branches ----
st_ = lambda i, t="function": {"id": i, "name": i, "type": t}
check("inventory: branches = a decision step or a step leading to 2+ steps",
      inv.branches([st_("a"), st_("b"), st_("c")], [{"from": "a", "to": "b", "type": "calls"}, {"from": "a", "to": "c", "type": "calls"}])
      and inv.branches([st_("a"), st_("d", "decision")], [])
      and not inv.branches([st_("a"), st_("b"), st_("c")], [{"from": "a", "to": "b", "type": "calls"}, {"from": "b", "to": "c", "type": "calls"}]), "")

# ---- check.py: ipo strip and traces at 1280 and 390 px ----
spec = tech({"Main flows": [{"type": "h3", "text": "a → b"}, ipo([item("t", at=["some_long_table_name_value"] * 6), item("u", case="edge", at=["v"] + [""] * 5)], steps=6)]})
out, rc = run(R9, spec)
r = subprocess.run([sys.executable, str(T / "check.py"), str(R9 / "generated-docs/doc.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: 6-step ipo + traces clean at 1280 and 390 px", rc == 0 and r.returncode == 0, out + r.stdout + r.stderr)
css = (T / "style.css").read_text(encoding="utf-8")
(W / "narrow.html").write_text(f"<!doctype html><html><head><meta name='viewport' content='width=device-width'><style>{css}</style></head><body><main><section><h2>x</h2>"
                               f"<div style='width:600px'>wide</div></section></main></body></html>", encoding="utf-8")
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "narrow.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: narrow pass at 390 px reports sideways scroll", "LAYOUT page | scrolls sideways at 390px" in r.stdout, r.stdout)

# ---- v3: say each fact once (rules rows, ipo cap, trace tokens, Operations tasks, repeats, no-graph) ----
NM = ["Overview", "Architecture", "Main flows", "Business rules", "Deploy and environments", "Operations"]
def chk(sec, plan_=None):
    s_ = tech(sec)
    return build.check(s_, "technical", sorted(s_["sections"], key=lambda n: (build.ORDER["technical"] + [LAST]).index(n)), plan_)
st1 = lambda **k: {"do": "Read rows", "out": "`orders` rows", "where": "src/a.py:1", **k}
mfw = lambda steps, items=None: [{"type": "h3", "text": "in → out"}, dict(ipo(items), steps=steps)]
err, warn = chk({"Main flows": mfw([st1()]), "Business rules": [{"type": "rules", "rows": [
    ["Newest wins", "2 events → 1 row", "w", "src/b.py:1"], ["newest  wins", "3 → 1", "w", "src/b.py:1"],
    ["Shown in a step", "see step 3.1.9", "w", ""], ["Pointer with Where", "see step 3.1.1", "w", "src/a.py:1"],
    ["No example", "keeps the later one", "w", "src/b.py:1"], ["No value", "older → newer", "", "src/b.py:1"]]}]})
check("rules: duplicate rule -> ERROR; pointer to a missing step -> ERROR",
      any("rule 'newest wins' is listed 2 times" in e for e in err) and any("points to step 3.1.9, which Main flows does not have" in e for e in err), err)
check("rules: pointer + Where -> WARN; no 'in → out' -> WARN; no example value -> WARN",
      any("'Pointer with Where' points to step 3.1.1 and cites its lines again" in w for w in warn)
      and any("without an example 'in → out': ['No example']" in w for w in warn) and any("no example value: ['No value']" in w for w in warn), warn)
check("rules: Business rules takes no examples block (one row per rule)", not build.fits(build.RECIPES["technical"]["Business rules"], ["rules", "examples"]), "")
_, warn = chk({"Main flows": mfw([st1()]), "Business rules": [{"type": "rules", "rows": [["Rows read", "`a` 1 → 2", "w", "`src/a.py:1`"]]}]})
check("repeat: a rule citing a Main flows step's lines -> WARN, points to 'see step 3.1.1'",
      any("repeat: `src/a.py:1` cited in Main flows, Business rules: a rule a Main flows step shows points to it ('see step 3.1.1'" in w
          for w in warn), warn)
_, warn = chk({"Main flows": mfw([st1()] * 8)})
check("ipo: more than 7 steps -> WARN (merge plumbing steps, graph: [k, ...])", any("has 8 ipo steps (max 7)" in w for w in warn), warn)
_, warn = chk({"Main flows": mfw([{"do": "Fetch `BASE` + path", "out": "HTTP request"}, {"do": "Load the dashboard", "out": "Dashboard"},
                                  {"do": "Parse argv", "out": "`args` 2 values"}])})
check("ipo: step out with no new name or number -> one WARN naming the steps",
      any("whose out adds no name or number to their do: 1 'HTTP request', 2 'Dashboard'" in w for w in warn)
      and not any("3 '`args`" in w for w in warn), warn)
items_ = [item("t", at=["skipped", "valid"]), item("u", case="edge", at=[None, "=", ][:2]), item("v", case="failure", at=["404", "–"])]
_, warn = chk({"Main flows": mfw([st1(), st1(do="Write", out="`out` 1 row")], items_)})
check("trace: placeholder word -> WARN; bare word without a value -> WARN; =, null, – accepted",
      any("use placeholder words ('t' step 1: 'skipped')" in w for w in warn) and any("hold no example value ('t' step 2: 'valid')" in w for w in warn)
      and not any("'u' step" in w or "'v' step" in w for w in warn), warn)
spec = tech({"Main flows": mfw([st1(), st1(do="Write the rows", out="`out` 1 row", where="src/b.py:1")],
                               [item("t", at=["1", "2"]), item("u", case="edge", at=[None, ""]), item("v", case="failure", at=["3", "-"])])})
out, rc = run(R9, spec)
p = page(R9)
check("trace: '' and '=' -> '=', null/'-' -> '–' (greyed), one legend line naming the tokens used",
      rc == 0 and 'class="nr"><div><span class="tc">&#8211;</span>' in p and 'class="eq"><div><span class="tc">=</span>' in p
      and '<p class="key legend">= unchanged from the column before &middot; &ndash; not reached, or a step this example does not touch</p>' in p, out)
check("trace: rows labelled with the step's do (phone), traces after the first two in <details>",
      'data-h="2 Write the rows"' in p and '<details><summary>More examples: 3.1c</summary>' in p and p.count('<table class="trace">') == 2, "")
check("strip: where as basename:line with the full path in its title; Sources line once",
      '<span class="src" title="src/a.py:1">a.<wbr>py:1</span>' in p and "<p class=\"src\">Sources: src/a.py &middot; src/b.py</p>" in p, out)
plan_b = {"main_flows": [{"h3": "in → out", "flow": "f", "steps": 3, "ordered": True, "diagram": True, "entry": "x", "boxes": []}],
          "sections": {}, "app_types": []}
fl_b = {"type": "flow", "id": "Q", "nodes": [box("x"), box("y", col=1), box("z", col=2, kind="fail")],
        "edges": [{"from": "x", "to": "y"}, {"from": "x", "to": "z", "fail": True}]}
blk = mfw([st1(graph=[1, 2]), st1(do="Write", out="`out` 1 row")]) + [fl_b]
err, warn = [], []; build.main_flows({}, blk, plan_b, err, warn)
check("main flows: a step's graph: [1, 2] merges graph steps (no count WARN); diagram without a branch step -> WARN",
      not any("cover graph steps" in w for w in warn) and any("mark the step the branch leaves with `branch:" in w for w in warn), warn)
blk = mfw([st1(graph=[1, 2]), st1(do="Write", out="`out` 1 row", branch="404, nothing stored")]) + [fl_b]
err, warn = [], []; build.main_flows({}, blk, plan_b, err, warn)
check("main flows: branch step marked -> no WARN; the strip links to the diagram",
      not warn and blk[1]["_dia"] == "Q" and 'else 404, nothing stored &#9656; <a href="#d-Q">Diagram Q</a>' in build.ipo(blk[1]), warn)
err, warn = [], []; build.main_flows({}, mfw([st1()] * 2) + [fl_b], plan_b, err, warn)
check("main flows: steps covering 2 of 3 graph steps -> WARN", any("cover graph steps [1, 2], the graph flow has 3 ordered steps" in w for w in warn), warn)
check("Operations: one tasks table (Task · Command · When); h3 + steps refused",
      build.fits(build.RECIPES["technical"]["Operations"], ["symptoms", "tasks"]) and not build.fits(build.RECIPES["technical"]["Operations"], ["symptoms", "h3", "steps"])
      and build.TYPED["tasks"] == ["Task", "Command", "When", "Where"], "")
err, warn = [], []; build.operations_tasks([{"type": "tasks", "rows": [["", "x", "y"], ["Run the tests", "`pytest`", "CI"], ["Run the tests", "a", "b"]]}],
                                           {"how_tos": ["Run the tests"], "rerun_and_backfill": False}, err, warn)
check("Operations: first row without a Task -> ERROR; a task started twice -> WARN",
      any("first tasks row needs a Task" in e for e in err) and any("start more than once" in w for w in warn), (err, warn))
_, warn = chk({"Deploy and environments": [{"type": "steps", "rows": [["Test", "`make test all`", "CI"]]}, {"type": "environments", "rows": []}],
               "Operations": [{"type": "symptoms", "rows": []}, {"type": "tasks", "rows": [["Run the tests", "`make test all`", "before a merge", ""]]}]})
check("repeat: same command in Deploy and Operations -> WARN", any("command `make test all` in Deploy and environments, Operations" in w for w in warn), warn)
same = "The nightly job reloads every changed partition from the landing zone."
_, warn = chk({"Overview": [{"type": "text", "text": same}, {"type": "flow", "nodes": [box()], "key": "Arrow k = ipo step k"}],
               "Architecture": [{"type": "flow", "nodes": [box()]}, {"type": "components", "rows": []}, {"type": "bullets", "items": [same]}]})
check("repeat: same sentence (>= 6 words) in two sections -> WARN; 'ipo' in a key -> WARN",
      any("repeat: 'the nightly job reloads every changed partition from the landing' in 2 blocks (Overview, Architecture)" in w for w in warn)
      and any("'ipo' is a spec word" in w for w in warn), warn)
RV = W / "rv"; repo(RV, {"src/a.py": "x\n", "reviews/_spec/review-v2-1.json": "{}", "reviews/code-review.md": "# r\n"})
cwd = os.getcwd(); os.chdir(RV)
files_ = build.review_files(); os.chdir(cwd)
check("reviews: reviews/_spec (review-v2 specs) is not a code review", files_ == ["reviews/code-review.md"], files_)

# ---- insight round: every word a fact or an insight (why slots, group rows, columns said once, '=' only unchanged, phone) ----
# H3: a step's why, shown under its output; a branch step without one -> WARN
blk_ = mfw([st1(why="downstream joins need one row per key"), st1(do="Write", out="`out` 1 row", branch="404, nothing stored")])
_, warn = chk({"Main flows": blk_})
check("why: branch step without `why` -> WARN", any("that drop, filter, branch or write data without `why`: 2:" in w for w in warn), warn)
spec = tech({"Main flows": mfw([st1(why="downstream joins need one row per key"), st1(do="Write the rows", out="`out` 1 row", where="src/b.py:1")],
                               [item("t", at=["1", "2"]), item("u", case="edge", at=["3", None]), item("v", case="failure", at=["4", None])])
             + [{"type": "h3", "text": "x → y"}, dict(ipo([item("t", at=["5"]), item("u", case="edge", at=[None])]),
                                                     steps=[st1(do="Load", out="`y` 2 rows", where="src/b.py:1")])]},
            app_types=[])
out, rc = run(R9, spec)
p = page(R9)
check("why: shown as one muted line under the step's output", rc == 0 and '<span class="why">downstream joins need one row per key</span>' in p, out)
check("legend: once per section; '–' also means a step the example does not touch",
      p.count('<p class="key legend">') == 1 and "&ndash; not reached, or a step this example does not touch" in p, out)
check("phone: traces after the first behind one toggle (CSS), the first trace open",
      '<input type="checkbox" class="more" id="more-3.1"' in p and '<label class="more-l" for="more-3.1">More examples: 3.1b, 3.1c</label>' in p
      and '<tr id="ex-3.1b" class="edge more">' in p and '<tr id="ex-3.1a" class="typical">' in p, out)
_, warn = chk({"Main flows": mfw([st1(), st1(do="Write", out="`out` 1 row"), st1(do="Send", out="`msg` 1")],
                                 [item("t", at=["1", "=", "="]), item("u", case="edge", at=["2", "3", "="])])})
check("trace: more than half '=' -> WARN (a one-step example is a rule example; untouched step is '–')",
      any("more than half '=' cells ('t')" in w for w in warn) and not any("('u')" in w and "more than half" in w for w in warn), warn)

# H3 + L4: rules Rule · Example · Why / impact · Where; every rule a why (a pointer may use its step's why); short Where
_, warn = chk({"Main flows": mfw([st1(why="w")]), "Business rules": [{"type": "rules", "rows": [
    ["Keep newest", "2 events → 1 row", "", "src/b.py:1"], ["Shown", "see step 3.1.1", "", ""]]}]})
check("rules: rule without Why / impact -> WARN; a pointer to a step with a why is fine",
      any("rules without a Why / impact: ['Keep newest']" in w for w in warn) and not any("'Shown'" in w and "Why" in w for w in warn), warn)
spec = tech({"Business rules": [{"type": "rules", "rows": [["Keep newest", "2 events → 1 row", "replays would double revenue", "src/b.py:1"],
                                                          ["Drop nulls", "`id` NULL → 0 rows", "a null key breaks the merge", "src/a.py:1"],
                                                          ["Trim", "' a' → 'a'", "joins match", "src/a.py:1"]]}]})
out, rc = run(R9, spec)
p = page(R9)
check("rules: Where as basename:line (full path in its title), full paths once under the table (L4)",
      rc == 0 and '<span class="src" title="src/b.py:1">b.<wbr>py:1</span>' in p and "<p class=\"src\">Sources: src/b.py &middot; src/a.py</p>" in p, out)

# H2 / L1: columns said once; near-constant -> WARN; same cell 4+ times -> WARN; status near-constant shown only where it differs
rows_ = [[f"`v{k}`", "1:1, no filter", "live rows" if k < 4 else f"{k} rows"] for k in range(5)]
_, warn = chk({"Data model": [{"type": "views", "rows": rows_}]})
check("repeat: a column with one value in every row -> no WARN (the build says it once)", not any("'1:1, no filter'" in w for w in warn), warn)
check("repeat: near-constant column (>= 70%) -> WARN naming it and the count",
      any("repeat: Data model: views column 'Rows' is 'live rows' in 4 of 5 rows" in w for w in warn), warn)
rows_ = [[f"`c{k}`", "parses one file", f"src/a.py:{k + 1}"] for k in range(4)] + [["`d`", "x", "y"], ["`e`", "z", "w"]]
_, warn = chk({"Architecture": [{"type": "flow", "nodes": [box()]}, {"type": "components", "rows": rows_}]})
check("repeat: the same cell (2+ words) in 4+ rows -> WARN: merge into a group row",
      any("components column 'Responsibility': 'parses one file' in 4 rows: merge those rows into one group row" in w for w in warn), warn)
h = build.table(["File", "Why it looks unused", "Status"], [["a", "x", "Confirmed (review)"], ["b", "y", "Confirmed (review)"],
                                                           ["c", "z", "Confirmed (review)"], ["d", "w", "Not verified"]])
check("status column with one status in >= 70% of rows: said once, only the others shown (L1)",
      "All rows: <b>Status</b> = <span class=\"chip ok\">Confirmed (review)</span> unless shown" in h and h.count("Confirmed (review)") == 1
      and '<span class="chip nv">Not verified</span>' in h, h)
build.POS.update(kind="technical")
h = build.issues({"items": [{"sev": "Must", "issue": f"i{k}", "where": "w", "impact": "x", "status": "Confirmed (code)", "fix": "f"} for k in range(3)]}, "technical")
check("issues: one status for all -> said once above the table", "All rows: <b>Status</b> = <span class=\"chip ok\">Confirmed (code)</span></p>" in h
      and h.count("Confirmed (code)") == 1, h)

# H1: group rows and covers count for coverage
_, warn = chk({"Tests": [{"type": "tests", "rows": [["3 schema files: `a.schema`, `b.schema`", "unused expected output"],
                                                    ["`*.schema` files", "unused", {"covers": ["x.schema", "y.schema"]}],
                                                    ["2 marker files", "package markers", {"covers": ["p/__init__.py", "q/__init__.py"]}]]}]})
check("group row: says N but lists M names -> WARN; a covers row need not say how many (count in its hover title, M2)",
      any("group row '3 schema files: `a.schema`, `b.schema`' says 3 but lists 2 names" in w for w in warn)
      and not any("`*.schema` files" in w for w in warn) and not any("'2 marker files'" in w for w in warn), warn)
sp = {"sections": {"Tests": [{"type": "tests", "rows": [["2 marker files", "package markers", {"covers": ["p/__init__.py", "q/__init__.py"]}],
                                                        ["`tests/t.py`", "x"], ["y", "z", {"covers": ["typo.py"]}]]}]}}
build.split_covers(sp)
warn = []
build.coverage(sp, "<p>tests/t.py</p>", {"tests": ["tests/t.py", "p/__init__.py", "q/__init__.py"], "items": {}, "plan": {"coverage": ["test_file"], "api": []}}, warn)
check("coverage: names in a row's covers count; covers names that are no inventory item -> WARN (H1)",
      not any("test_file items" in w for w in warn) and any("covers names that are no inventory.json item: ['typo.py']" in w for w in warn), warn)
check("covers: rendered as the row's hover title, not as a cell", 'title="covers 2: p/__init__.py, q/__init__.py"' in build.table(
      build.TYPED["tests"], sp["sections"]["Tests"][0]["rows"], covers=sp["sections"]["Tests"][0]["_covers"]), "")

# M1: no word target in cells
_, warn = chk({"Architecture": [{"type": "flow", "nodes": [box()]}, {"type": "components", "rows": [["c", long(30), "w"]]}]})
check("budget: a 30-word cell is fine (cap 40, no word target)", not any("table cells over" in w for w in warn), warn)

# M5 + L4: tasks: human names (how-to in Where or covers), one heading row per task, numbered rows, short Where
err, warn = [], []
build.operations_tasks([{"type": "tasks", "rows": [["Ship a model change", "`make deploy`", "after merge", "`making a change` (README)"],
                                                   ["", "`make check`", "after deploy", ""],
                                                   ["Run the tests", "`pytest`", "before a merge", ""]]}],
                       {"how_tos": ["making a change", "Run the tests"], "rerun_and_backfill": False}, err, warn)
check("tasks: a plain-words task with its how-to in Where is accepted (M5)", not err and not warn, (err, warn))
h = build.tasks_table([["Ship it", "`make deploy`", "after merge", "src/a.py:3"], ["", "`make check`", "after deploy", "src/b.py:1"],
                       ["Run the tests", "`pytest`", "before a merge", ""]])
check("tasks: one heading row per task, its rows numbered under it, Where short (M5, L4)",
      '<tr class="grp"><td colspan="3">Ship it</td></tr>' in h and '<span class="n">1</span>' in h and '<span class="n">2</span>' in h
      and "<th>Task</th>" not in h and "<th>Command</th><th>When</th><th>Where</th>" in h and 'title="src/a.py:3">a.<wbr>py:3' in h, h)

# M3: a Main flows diagram draws the branches, arrows numbered with the strip's step numbers
plan_m = {"main_flows": [{"h3": "in → out", "flow": "f", "steps": 2, "ordered": True, "diagram": True, "entry": "x", "boxes": []}],
          "sections": {}, "app_types": []}
chain = {"type": "flow", "id": "Q", "nodes": [box("x"), box("y", col=1), box("z", col=2)],
         "edges": [{"from": "x", "to": "y", "step": 1}, {"from": "y", "to": "z", "step": 2}]}
err, warn = [], []; build.main_flows({}, mfw([st1(), st1(do="Write", out="`o` 1", branch="404", why="w")]) + [chain], plan_m, err, warn)
check("diagram: a straight chain redraws the strip -> ERROR; branch step not drawn -> ERROR (M3)",
      any("is one straight chain" in e for e in err) and any("does not draw the branch of step 2" in e for e in err), err)
nostep = dict(chain, edges=[{"from": "x", "to": "y"}, {"from": "x", "to": "z", "fail": True}])
err, warn = [], []; build.main_flows({}, mfw([st1(), st1(do="Write", out="`o` 1")]) + [nostep], plan_m, err, warn)
check("diagram: no arrow carries `step` -> ERROR", any("their step: `step: k`" in e for e in err), err)
fork_ = dict(chain, nodes=chain["nodes"] + [box("f", col=2, row=1, kind="fail")],
             edges=[{"from": "x", "to": "y", "step": 1}, {"from": "y", "to": "z", "step": 2}, {"from": "y", "to": "f", "fail": True, "label": "404"}])
blk = mfw([st1(), st1(do="Write", out="`o` 1", branch="404", why="w")]) + [fork_]
err, warn = [], []; build.main_flows({}, blk, plan_m, err, warn)
h = build.flow(blk[2], build.uid())
check("diagram: branch drawn -> clean; title N = strip steps it draws; numbers = step numbers, branch arrow unnumbered",
      not err and blk[2]["title"] == "in → out, 2 steps" and h.count('class="num"') == 2 and ">2</span>" in h and ">3</span>" not in h, (err, blk[2]["title"]))
err, warn = [], []; build.main_flows({}, mfw([st1()]) + [dict(fork_)], dict(plan_m, main_flows=[dict(plan_m["main_flows"][0], steps=1)]), err, warn)
check("diagram: arrow step past the strip -> ERROR", any("arrows with step 2: the strip under 'in → out' has steps 1-1" in e for e in err), err)

# L2: a diagram key said once per section
spec = tech({"Commands": [{"type": "flow", "id": "C", "title": "e area", "numbered": False, "nodes": [box()], "key": "teal = code"},
                          {"type": "flow", "id": "D", "parent": ["C", "a"], "title": "inside a", "nodes": [box()], "key": "teal = code"},
                          {"type": "commands", "rows": []}]}, auto=False, app_types=["cli"])
spec["sections"]["Overview"][1].update(id="A", title="o area", numbered=False)
spec["sections"]["Architecture"][0].update(id="B", title="b area", numbered=False)
spec["sections"]["Main flows"] = mfw([st1()])
out, rc = run(R9, spec)
check("key: the same key under two diagrams of a section -> shown once (L2)", rc == 0 and page(R9).count("Key: teal = code") == 1, out)

# M4: check.py tests tables at 390 px; stacked typed tables are clean
spec = tech({"Business rules": [{"type": "rules", "rows": [[f"Rule {k} keeps the newest `KAFKA_TIMESTAMP` value per key", "`value.event_time` 2024-01-01 → kept",
                                                            "a replay would otherwise double the totals for finance", "src/a.py:1"] for k in range(3)]}],
             "Main flows": mfw([st1()])})
out, rc = run(R9, spec)
r = subprocess.run([sys.executable, str(T / "check.py"), str(R9 / "generated-docs/doc.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: rules table stacked at 390 px, nothing cut (M4)", rc == 0 and r.returncode == 0, out + r.stdout)
css = (T / "style.css").read_text(encoding="utf-8")
(W / "widetable.html").write_text(f"<!doctype html><html><head><meta name='viewport' content='width=device-width'><style>{css}</style></head><body><main>"
                                  f"<section><h2>x</h2><div class='scroll'><table><tr><th>a</th></tr><tr><td><div style='width:600px'>wide</div></td></tr></table></div>"
                                  f"</section></main></body></html>", encoding="utf-8")
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "widetable.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: a table wider than its box at 390 px -> LAYOUT", "table wider than page at 390px" in r.stdout, r.stdout)

# M6: no graph: a library package is one public-API h3; modules without a public callable left out
RL = W / "rl"; repo(RL, {"src/kit/__init__.py": "", "src/kit/cli.py": "def main():\n    pass\n", "src/kit/__main__.py": "from .cli import main\n",
                         "src/kit/parse.py": "def parse(t):\n    return t\n", "src/kit/fmt.py": "class Fmt:\n    pass\n", "src/kit/_x.py": "def y(): pass\n",
                         "pyproject.toml": "[project]\nname = 'kit'\n[project.scripts]\nkit = 'kit.cli:main'\n"})
iout, irc = inventory(RL)
ni = json.loads((RL / "generated-docs/_spec/inventory.json").read_text(encoding="utf-8"))
mf_ = {m["h3"]: m["files"] for m in ni["plan"]["main_flows"]}
check("no graph: CLI script + cli.py + __main__.py = one h3; the package API = one h3, CLI files and empty modules left out (M6)",
      irc == 0 and list(mf_) == ["kit: Command line → output", "kit: Function call → return value"]
      and mf_["kit: Command line → output"] == ["pyproject.toml", "src/kit/__main__.py", "src/kit/cli.py"]
      and mf_["kit: Function call → return value"] == ["src/kit/fmt.py", "src/kit/parse.py"], (iout, mf_))

# ---- final round: insight review fixes ----
# H1: example b of a trace shows on a desktop; check.py flags a hidden example row
css = (T / "style.css").read_text(encoding="utf-8")
check("css: only the phone toggle (input.more) is hidden, never a trace row tr.more (H1)",
      "input.more, .more-l { display:none; }" in css and not re.search(r"(^|[\s,}])\.more\s*[,{]", css), "")
spec = tech({"Main flows": mfw([st1(why="w")], [item("t", at=["1"]), item("u", case="edge", at=["2"]), item("v", case="failure", at=["3"])])})
out, rc = run(R9, spec)
r = subprocess.run([sys.executable, str(T / "check.py"), str(R9 / "generated-docs/doc.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: 3 examples -> all 3 trace rows shown at 1280 px, 0 layout problems (H1)", rc == 0 and r.returncode == 0, out + r.stdout + r.stderr)
(W / "hidden.html").write_text(f"<!doctype html><html><head><style>{css}</style></head><body><main><section><h2>x</h2><div class='scroll'><table class='trace'>"
                               f"<tr><th>Ex</th></tr><tr id='ex-3.1a'><td>a</td></tr><tr id='ex-3.1b' style='display:none'><td>b</td></tr></table></div>"
                               f"</section></main></body></html>", encoding="utf-8")
r = subprocess.run([sys.executable, str(T / "check.py"), str(W / "hidden.html")], capture_output=True, text=True, encoding="utf-8")
check("check.py: an example row hidden at 1280 px -> LAYOUT (H1)", "example 3.1b hidden (1 of 2 example rows shown)" in r.stdout, r.stdout)

# M1: a flow without any why, and a write step without one -> WARN
_, warn = chk({"Main flows": mfw([st1(), st1(do="Write", out="`out` 1 row")])})
check("why: no step of a flow has a why -> WARN (M1)", any("no step under 'in → out' has a `why`" in w for w in warn), warn)
_, warn = chk({"Main flows": mfw([st1(why="downstream joins need one row per key"), st1(do="Filter rows", out="`out` 1 row"),
                                  st1(do="Write rows", out="`out` 2 rows")], [item("t", at=["1", "2", "3"]), item("u", case="edge", at=["1", "2", "3"])])})
check("why: filter and write steps without a why -> WARN, read step fine (M1)",
      any("write data without `why`: 2, 3:" in w for w in warn), warn)

# L1: a why that restates the step's out
_, warn = chk({"Main flows": mfw([st1(out="only change rows since the last run", why="only change rows since last run, nothing older")])})
check("why: restating the step's out -> WARN (L1)", any("whys under 'in → out' that restate the step's out or branch: 1" in w for w in warn), warn)
_, warn = chk({"Main flows": mfw([st1(why="downstream joins need one row per key")])})
check("why: a why with its own reason -> no restate WARN (L1)", not any("restate" in w for w in warn), warn)

# L5: '=' in the first step column says nothing
err, _ = chk({"Main flows": mfw([st1(why="w"), st1(do="Write", out="`o` 2", why="w")], [item("t", at=["=", "2"]), item("u", case="edge", at=["1", "2"])])})
check("trace: '=' at step 1 -> ERROR (L5)", any("'=' at step 1 only repeats In" in e for e in err), err)

# M2: graph bookkeeping in a cell -> WARN
_, warn = chk({"Business rules": [{"type": "rules", "rows": [["Newest event wins (2 graph rules)", "2 events → 1 row", "a replay would double totals",
                                                               "src/b.py:1", {"covers": ["r1", "r2"]}]]}]})
check("rules: '(2 graph rules)' in a cell -> WARN; count lives in the hover title (M2)", any("says how the graph counts ('2 graph rules')" in w for w in warn), warn)

# M3: a see-step row may cite other lines; a Why that holds a citation -> WARN
_, warn = chk({"Main flows": mfw([st1(why="w")]), "Business rules": [{"type": "rules", "rows": [
    ["Rename keeps old ids", "see step 3.1.1", "", "src/b.py:1"], ["Null person id dropped", "`id` null → no row", "tested at `src/b.py:1`", "src/a.py:1"]]}]})
check("rules: see-step row citing other lines than the step -> no WARN (M3)", not any("cites its lines again" in w for w in warn), warn)
check("rules: a citation in Why / impact -> WARN (M3)", any("Why / impact cells citing code lines: ['Null person id dropped']" in w for w in warn), warn)

# M5: rule named by an identifier only; a cell naming more than 6 names; Why column min width
_, warn = chk({"Business rules": [{"type": "rules", "rows": [["`task_dependency_order`", "a → b", "a later task reads stale rows", "src/b.py:1"]]}]})
check("rules: rule named by a snake_case id only -> WARN (M5)", any("rules named by an identifier only: ['`task_dependency_order`']" in w for w in warn), warn)
build.HIDDEN.clear()
names8 = ", ".join(f"`n{k}`" for k in range(8))
h = build.table(build.TYPED["rules"], [["One row per element applies to: " + names8, "x → y", "w", "src/a.py:1"]] * 3, True)
check("cell: more than 6 names -> first 6 then '+2 more', full list in the hover title, hidden names still covered (M5)",
      "+2 more" in h and "<code>n5</code>" in h and "<code>n6</code>" not in h and 'title="One row per element applies to: n0, n1' in h
      and {"n6", "n7"} <= build.HIDDEN, h)
check("css: Why / impact column has a min width (M5)", '.tt td[data-h="Why / impact"] { min-width:' in css, "")

# L2: a see-step row's empty cells join the Example cell
h = build.table(build.TYPED["rules"], [["a", "see step 3.1.1", "", ""], ["b", "x → y", "w", "src/a.py:1"], ["c", "x → z", "v", "src/a.py:2"]], True)
check("rules: see-step row spans its empty Why and Where cells (L2)", 'colspan="3"' in h and h.count("<td") == 2 + 4 + 4, h)

# L4: a status in half the rows is said once
h = build.table(["File", "Why", "Status"], [["a", "x", "Confirmed (review)"], ["b", "y", "Confirmed (review)"], ["c", "z", "Not verified"], ["d", "w", "Fixed since review"]])
check("status in >= half the rows -> said once, '... unless shown' (L4)", "Confirmed (review)</span> unless shown" in h and h.count("Confirmed (review)") == 1, h)

# M4: adjacent same-shape tables merge; more than 3 tables in a section -> WARN
sp = tech({"Tests": [{"type": "tests", "rows": [["`a`", "x"], ["`b`", "y"]]}, {"type": "tests", "rows": [["`c`", "z"]]}]})
err, warn = build.check(sp, "technical", sorted(sp["sections"], key=lambda n: (build.ORDER["technical"] + [LAST]).index(n)), None)
check("tables: two adjacent tests tables -> one table of 3 rows, recipe ok (M4)",
      not any("Tests: recipe" in e for e in err) and [len(b["rows"]) for b in sp["sections"]["Tests"]] == [3], (err, sp["sections"]["Tests"]))
rows3 = [["a b", "c d"], ["e f", "g h"], ["i j", "k l"]]
_, warn = chk({"Known issues, assumptions, and decisions needed": [
    {"type": "issues", "items": [{"sev": "Should", "kind": "config", "issue": "i", "where": "src/a.py:1", "impact": "x", "status": "Not verified", "fix": "f"}]},
    {"type": "unused", "rows": [["`src/a.py`", "w", "Not verified"]] * 3}, {"type": "assumptions", "rows": rows3},
    {"type": "decisions", "rows": [["d", "o", "r", "w"]] * 3}]})
check("tables: 4 tables in one section -> WARN (M4)", any("4 tables (issues, unused, assumptions, decisions; max 3)" in w for w in warn), warn)

# author voice: chat leakage in visible text -> WARN; owner-voiced facts, reader-facing "you" and code spans pass
w = []; build.chat_voice({"sections": {"A": [{"type": "bullets", "items": ["You didn't confirm this on prod", "As discussed, retries are 3",
     "Retention: Not defined in source — confirm with owner"]}]}, "tabs": {}}, ["A"], w)
w2 = []; build.chat_voice({"sections": {"A": [{"type": "bullets", "items": ["Not yet tested in production", "Owner to decide: retention period",
      "If you see a 403, ask your admin", "`ask_the_user_flag` is off"]}]}, "tabs": {}, "title": "Orders"}, ["A"], w2)
w3 = []; build.chat_voice({"sections": {"A": [{"type": "bullets", "items": ["You need to run this on prod to confirm",
      "Retries could not be checked", "Please verify the schedule"]}]}, "tabs": {}}, ["A"], w3)
check("author voice: 'run on prod to confirm', 'could not be checked', 'please verify' -> WARN", len(w3) == 3, w3)
check("author voice: chat phrases -> WARN chat voice, owner voice passes", len(w) == 3 and all("chat voice" in x for x in w) and not w2, (w, w2))

# L8: the full and panini variants ship the same templates and examples
other = {"claude-global": "claude-global-panini", "claude-global-panini": "claude-global"}.get(SKILL.parents[1].name)
twin = SKILL.parents[2] / other / "skills" / SKILL.name if other else None
if twin and twin.is_dir():
    diff = [f.relative_to(SKILL).as_posix() for d in ("references/templates", "references/examples", "tests") for f in sorted((SKILL / d).glob("*"))
            if f.is_file() and f.suffix != ".pyc" and (not (twin / f.relative_to(SKILL)).is_file() or (twin / f.relative_to(SKILL)).read_bytes() != f.read_bytes())]
    check(f"variants: templates, examples and tests identical in {other} (L8)", not diff, diff)

print(f"\n{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
