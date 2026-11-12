"""Tests for build.py, profile.py, inputs.py and skills.py: one case per rule. Usage: python run.py"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
T = SKILL / "references" / "templates"
EX = SKILL / "references" / "examples"
BASE = json.loads((EX / "requirements-brief-example.json").read_text(encoding="utf-8"))


def run(script, *args, cwd, home=None):
    env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)} if home else None  # skills.py: an empty ~/.claude/skills
    r = subprocess.run([sys.executable, "-B", str(script), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout + r.stderr


def build(spec, out="out/b.html", inputs=True):
    d = Path(tempfile.mkdtemp())
    (d / "out").mkdir()
    shutil.copy(EX / "profile.json", d / "profile.json")
    if inputs:
        shutil.copytree(EX / "inputs", d / "inputs")
    (d / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
    code, text = run(T / "build.py", "spec.json", out, cwd=d)
    page = (d / out).read_text(encoding="utf-8") if (d / out).is_file() else ""
    shutil.rmtree(d, ignore_errors=True)
    return code, text, page


def edit(fn):
    s = copy.deepcopy(BASE)
    fn(s)
    return s


S = lambda s, name: s["sections"][name]
B = lambda s, name, j=0: S(s, name)["blocks"][j]  # a section's own block
SB = lambda s, name, i=0, j=0: S(s, name)["subsections"][i]["blocks"][j]  # a subsection's block
CASES = [  # (name, spec, expected exit, text expected in output)
    ("section missing", edit(lambda s: s["sections"].pop("Glossary")), 1, "section 'Glossary' missing"),
    ("section unknown", edit(lambda s: s["sections"].update({"Costs": {"line": "none"}})), 1, "section 'Costs' unknown"),
    ("section empty", edit(lambda s: s["sections"].update({"Flows": {}})), 1, "give `line` (one sentence), `blocks`, or `subsections`"),
    ("line and blocks", edit(lambda s: S(s, "Flows").update(line="x")), 1, "`line` or blocks/subsections, not both"),
    ("line section ok", edit(lambda s: s["sections"].update({"Flows": {"line": "Daily batch only; no timing to explain."}})), 0, "0 WARN"),
    ("core section as a line", edit(lambda s: s["sections"].update({"At a glance": {"line": "none"}})), 0, "section 'At a glance' is one line"),
    ("blocks without subsections ok", edit(lambda s: s["sections"].update({"Flows": {"blocks": [{"type": "text", "text": "One batch, 05:00 to 07:00."}]}})), 0, "0 WARN"),
    ("subsection without blocks", edit(lambda s: S(s, "Gaps, assumptions and risks")["subsections"][0].update(blocks=[])), 1, "needs title and blocks"),
    ("generic subsection title", edit(lambda s: S(s, "Gaps, assumptions and risks")["subsections"][0].update(title="Overview")), 0, "title 'Overview' fits any brief"),
    ("subsection titled like its block", edit(lambda s: S(s, "Gaps, assumptions and risks")["subsections"][0].update(title="Bullets")), 0, "fits any brief"),
    ("unknown block", edit(lambda s: B(s, "Flows").update(type="gantt")), 1, "block type 'gantt' unknown"),
    ("typed status row", edit(lambda s: B(s, "At a glance")["rows"].append(["Status", "12 requirements: all clear"])), 1, "Status row is computed by the build"),
    ("status counts mismatch in text", edit(lambda s: S(s, "Context").update(lead="All 14 requirements land in Snowflake.")), 0, "says 14 requirements, the Requirements rows hold 12"),
    ("status unknown", edit(lambda s: B(s, "Requirements")["rows"][0].update(status="open")), 1, "needs id, text and status in"),
    ("requirement twice", edit(lambda s: B(s, "Requirements")["rows"][1].update(id="FLT-1")), 1, "requirement FLT-1 listed twice"),
    ("input id missing from rows", edit(lambda s: B(s, "Requirements")["rows"].pop(2)), 1, "input requirement ids missing from the Requirements rows: FLT-3"),
    ("id dropped from rows and list: the rescan finds it", edit(lambda s: (B(s, "Requirements")["rows"].pop(2), s["inputs"][0]["ids"].remove("FLT-3"))), 1,
     "missing from the Requirements rows: FLT-3 (found again in the inputs folder, not in the spec's inputs list: FLT-3)"),
    ("id dropped from the list only: stale list WARN", edit(lambda s: s["inputs"][0]["ids"].remove("FLT-3")), 0, "input id FLT-3 found in the inputs folder but not in the spec's inputs list"),
    ("stack item without given row", edit(lambda s: s["stack"].append("Kafka")), 1, "stack 'Kafka' is confirmed but has no given options row"),
    ("given row not in stack", edit(lambda s: B(s, "Technology options")["rows"][7].update(given=True, alternatives=[])), 0, "is not in the confirmed stack"),
    ("given row with alternatives", edit(lambda s: B(s, "Technology options")["rows"][0].update(alternatives=[{"name": "Dagster", "tradeoff": "x"}])), 1, "given platforms are not re-litigated"),
    ("source box without row", edit(lambda s: SB(s, "Sources and data", 1)["rows"][0].update(id="telematics")), 1, "source box 'tel' has no sources row"),
    ("source row not in diagram", edit(lambda s: B(s, "Context")["nodes"][1].update(kind="step")), 0, "source tel is not a source box"),
    ("source row incomplete", edit(lambda s: SB(s, "Sources and data")["rows"][0].pop("cadence")), 1, "needs id, system, connector, key, cadence"),
    ("planned source needs id and system only", edit(lambda s: SB(s, "Sources and data")["rows"][0].update(planned=True, connector="", key="", cadence="")), 0, "0 WARN"),
    ("data point shape", edit(lambda s: SB(s, "Sources and data")["rows"][0]["points"].append(["x"])), 1, "must be [name, description]"),
    ("needs unknown source", edit(lambda s: B(s, "Use cases and data needs")["rows"][0]["sources"].append("crm")), 1, "source 'crm' has no sources row"),
    ("needs missing without sources", edit(lambda s: B(s, "Use cases and data needs")["rows"][4].update(missing="x")), 1, "`missing` says what the listed sources lack"),
    ("option without alternatives", edit(lambda s: B(s, "Technology options")["rows"][2].update(alternatives=[])), 1, "give 2-3 alternatives to"),
    ("option alternative without tradeoff", edit(lambda s: B(s, "Technology options")["rows"][2]["alternatives"][0].pop("tradeoff")), 1, "give 2-3 alternatives to"),
    ("option pick is an alternative", edit(lambda s: B(s, "Technology options")["rows"][6]["alternatives"][0].update(name="dbt Core on Snowflake")), 1, "is both the pick and an alternative"),
    ("option without source", edit(lambda s: B(s, "Technology options")["rows"][2].pop("source")), 0, "no source (official page)"),
    ("work kind unknown", edit(lambda s: B(s, "What needs to be done")["rows"][0].update(kind="test")), 1, "kind in ['build', 'configure', 'decide', 'clarify']"),
    ("work without owner", edit(lambda s: B(s, "What needs to be done")["rows"][0].pop("owner")), 1, "needs id, what, kind"),
    ("work depends unknown", edit(lambda s: B(s, "What needs to be done")["rows"][0].update(depends=["W99"])), 1, "depends on 'W99', not a work item id"),
    ("work ref unknown", edit(lambda s: B(s, "What needs to be done")["rows"][0].update(ref=["FLT-99"])), 0, "ref 'FLT-99' is no requirement id"),
    ("links join unknown entity", edit(lambda s: B(s, "Identity and linking")["joins"][0].update(b="driver")), 1, "needs a, b (entity ids) and on"),
    ("links join label long", edit(lambda s: B(s, "Identity and linking")["joins"][0].update(on="sha256(email)")), 0, "join label 'sha256(email)' over 12 characters"),
    ("diagram without title", edit(lambda s: B(s, "Context").pop("title")), 1, "flow needs a title"),
    ("diagram without key", edit(lambda s: B(s, "Context").pop("key")), 0, "no key (legend line)"),
    ("flow under 3 boxes", edit(lambda s: B(s, "Context").update(nodes=B(s, "Context")["nodes"][:2], edges=[], lanes=[])), 1, "fewer than 3 boxes"),
    ("flow edge unknown", edit(lambda s: B(s, "Context")["edges"].append({"from": "fms", "to": "crm"})), 1, "names an unknown box"),
    ("flow lanes fewer than rows", edit(lambda s: B(s, "Context").update(lanes=["a", "b"])), 1, "one lane per row"),
    ("flow node kind unknown", edit(lambda s: B(s, "Context")["nodes"][4].update(kind="queue")), 1, "node kind 'queue' unknown"),
    ("edge label long", edit(lambda s: B(s, "Context")["edges"][4].update(label="COPY INTO raw tables nightly")), 0, "over 12 characters"),
    ("box text cut", edit(lambda s: B(s, "Context")["nodes"][0].update(label="Fleet management system of the northern region")), 0, "cut, shorten it"),
    ("timeline over 7 steps", edit(lambda s: B(s, "Flows")["steps"].extend([{"at": "07:00", "do": "x"}] * 2)), 0, "8 steps, over 7"),
    ("timeline step without at", edit(lambda s: B(s, "Flows")["steps"][0].pop("at")), 1, "every step needs at and do"),
    ("table ragged", edit(lambda s: SB(s, "Data findings", 1)["rows"][0].pop()), 1, "head and rows of the same length"),
    ("facts row shape", edit(lambda s: B(s, "At a glance")["rows"].append(["x"])), 1, "rows are [label, value]"),
    ("profile missing", edit(lambda s: B(s, "Data findings").update({"from": "nope.json"})), 1, "not found: nope.json"),
    ("findings without profile", edit(lambda s: S(s, "Data findings").pop("blocks")), 0, "no profile block"),
    ("TODO left", edit(lambda s: S(s, "Context").update(lead="TODO write")), 1, "TODO left"),
    ("absolute path", edit(lambda s: S(s, "Context").update(lead="see C:\\work\\req.md")), 1, "absolute or machine path"),
    ("secret literal", edit(lambda s: S(s, "Context").update(lead='api_key = "abc123" in the config')), 1, "likely secret value for 'api_key'"),
    ("e-mail address", edit(lambda s: S(s, "Context").update(lead="Statements go to jane.doe@example.com monthly.")), 1, "e-mail address in the text"),
    ("phone number", edit(lambda s: S(s, "Context").update(lead="Depot hotline +49 555 0100 gets the alert.")), 1, "phone number in the text"),
    ("phone number local form", edit(lambda s: S(s, "Context").update(lead="Depot hotline 030 5550100 gets the alert.")), 1, "phone number in the text"),
    ("times, dates and ids are not phones", edit(lambda s: S(s, "Context").update(lead="Batch 05:00, dated 2026-11-12, covers FLT-12 and 2 of 20 VINs.")), 0, "0 WARN"),
    ("time range, row count, short number, IBAN groups are not phones",
     edit(lambda s: S(s, "Context").update(lead="Window 0500-0700; 015 000 rows; code 0815 4711; account DE89 3704 0044 0532 0130 00.")), 0, "0 WARN"),
    ("generic title: linking rules", edit(lambda s: S(s, "Identity and linking")["subsections"][0].update(title="Linking rules")), 0, "fits any brief"),
    ("allowed group title in section 11", edit(lambda s: S(s, "Gaps, assumptions and risks")["subsections"][0].update(title="Gaps")), 0, "0 WARN"),
    ("stack match is a whole word", edit(lambda s: s["stack"].append("Snow")), 1, "stack 'Snow' is confirmed but has no given options row"),
    ("at a glance as a line keeps the computed status", edit(lambda s: s["sections"].update({"At a glance": {"line": "Fleet view for planners."}})), 0, "is one line"),
    ("chat voice", edit(lambda s: S(s, "Context").update(lead="As discussed, the user decides the retention.")), 0, "voice: 'As discussed'"),
    ("chat voice: requester", edit(lambda s: S(s, "Context").update(lead="The requester asked us for a daily load.")), 0, "voice: 'The requester'"),
    ("skipped note", edit(lambda s: SB(s, "Gaps, assumptions and risks")["items"].append("Profiling was skipped for the fuel file.")), 0, "voice: 'was skipped'"),
    ("filler", edit(lambda s: S(s, "Context").update(lead="A robust daily load.")), 0, "filler: 'robust'"),
    ("over 40 words", edit(lambda s: S(s, "Context").update(lead=" ".join(["word"] * 41))), 0, "41 words, cap 40"),
    ("repeated sentence", edit(lambda s: S(s, "Data findings").update(lead=S(s, "Context")["lead"])), 0, "repeat:"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fails = n = 0

    def report(name, ok, out=""):
        nonlocal fails, n
        n += 1
        fails += not ok
        print(("PASS" if ok else "FAIL"), name, "" if ok else f"\n  output:\n  {out.strip()[:600]}")

    code, out, page = build(BASE)
    ok = (code == 0 and "0 WARN" in out and "12 requirements: 7 clear · 3 gap · 2 conflict" in out and page.count("<section") == 12
          and page.count("<svg") == 3 and 'class="chip none">no source' in page and 'class="chip gap">partial' in page and 'class="chip given"' in page
          and "values withheld" in page and "FLT-12" in page and 'id="s12"' in page and "YV2" not in page and "<dt>Status</dt><dd>12 requirements: 7 clear" in page
          and 'content="darshan-singh-meel-requirements-brief' in page and "min-width:640px" in page and "note:" not in out)
    report("valid spec: 12 sections, 3 diagrams, chips, computed status, no data values", ok, out)
    for name, spec, want_code, want in CASES:
        code, out, _ = build(spec)
        report(name, code == want_code and want in out, f"exit {code}\n  {out}")
    code, out, _ = build(BASE, inputs=False)
    report("inputs folder missing: note, ids from the spec list", code == 0 and "note: inputs not found" in out, out)
    code, out, _ = build(BASE, out="nope/b.html")
    report("missing output folder", code == 1 and "output folder nope does not exist" in out, out)
    code, out, _ = build(edit(lambda s: S(s, "Context").update(lead='password = "hunter2"')))
    report("secret value not echoed", "hunter2" not in out, out)
    s = edit(lambda s: B(s, "Context")["edges"].append({"from": "tel", "to": "dash", "label": "direct"}))  # tel (1,0) → dash (1,3) passes af and raw
    code, out, page = build(s)
    report("flow: an edge spanning rows detours around the boxes in between (6-point polyline)",
           code == 0 and re.search(r'points="(?:\d+,\d+ ){5}\d+,\d+"', page) is not None, out)
    report("links: wider gap fits 'on ' + 12 characters", 'x="296"' in page, out)
    s = edit(lambda s: B(s, "Context")["edges"].extend([{"from": "fms", "to": "ws", "label": "skip"}, {"from": "dash", "to": "tel", "dashed": True}]))
    code, out, page = build(s)  # fms (0,0) → ws (2,0) passes tel; dash (1,3) → tel (1,0) passes raw and af
    report("flow: same-row skip-column edge routes around the middle box; upward edge runs top to bottom edge",
           code == 0 and re.search(r'<polyline class="" points="\d+,28 \d+,17 \d+,17 \d+,28"', page) is not None  # over the top row, 20 px added above
           and re.search(r'<polyline class="dashed" points="(?:\d+,\d+ ){5}\d+,\d+"', page) is not None, out)
    code, out, page = build(edit(lambda s: s["sections"].update({"At a glance": {"line": "Fleet view."}})))
    report("status row rendered under a one-line At a glance", "<dt>Status</dt><dd>12 requirements" in page, out)
    d0 = Path(tempfile.mkdtemp())
    (d0 / "out").mkdir()
    (d0 / "profile.json").write_text(json.dumps({"files": [{"file": "C:/Users/x/a.csv", "rows": 1, "columns": []}], "overlaps": []}), encoding="utf-8")
    (d0 / "spec.json").write_text(json.dumps(BASE), encoding="utf-8")
    code, out = run(T / "build.py", "spec.json", "out/b.html", cwd=d0)
    shutil.rmtree(d0, ignore_errors=True)
    report("profile.json with a machine path fails the build", code == 1 and "absolute or machine path in the profile" in out, out)
    report("no __pycache__ next to the templates after a build", not (T / "__pycache__").exists(), "")
    d = Path(tempfile.mkdtemp())  # profile.py: structure only, overlap, sensitive values withheld
    code, out = run(T / "profile.py", str(EX / "inputs/vehicles.csv"), str(EX / "inputs/telematics_daily.csv"), "--out", "p.json", cwd=d)
    p = json.loads((d / "p.json").read_text(encoding="utf-8"))
    cols = {c["name"]: c for c in p["files"][0]["columns"]}
    raw = (d / "p.json").read_text(encoding="utf-8") + out
    report("profile: counts, types, sensitive columns without min/max, overlap on vin",
           code == 0 and p["files"][0]["rows"] == 20 and cols["plate"]["sensitive"] and "min" not in cols["plate"] and "min" not in cols["vehicle_id"]
           and cols["card_no"]["null_pct"] == 25.0 and p["overlaps"][0]["key"] == "vin" and p["overlaps"][0]["both"] == 17
           and "YV2" not in raw and "XX-" not in raw, out)
    (d / "misc.csv").write_text("capacity,hotel,CustomerName,order_no,delivered,shipped,mixed\n10,Alp,x,7,28.02.2025,05/14/2025,13/01/2025\n20,Sea,y,8,02.10.2026,06/02/2025,05/14/2025\n", encoding="utf-8")
    code, out = run(T / "profile.py", "misc.csv", "--out", "m.json", cwd=d)
    m = {c["name"]: c for c in json.loads((d / "m.json").read_text(encoding="utf-8"))["files"][0]["columns"]}
    report("profile: token-based sensitive names, dd.mm.yyyy min/max as dates",
           not m["capacity"]["sensitive"] and not m["hotel"]["sensitive"] and m["CustomerName"]["sensitive"] and m["order_no"]["sensitive"]
           and m["delivered"]["min"] == "2025-02-28" and m["delivered"]["max"] == "2026-10-02"
           and m["shipped"]["min"] == "2025-05-14" and m["shipped"]["max"] == "2025-06-02" and "min" not in m["mixed"], out)
    shutil.copy(EX / "inputs/vehicles.csv", d / "vehicles.csv")
    code, out = run(T / "profile.py", str((d / "vehicles.csv").resolve()), "--out", "r.json", cwd=d)
    report("profile: an absolute input path is written relative to the current folder",
           json.loads((d / "r.json").read_text(encoding="utf-8"))["files"][0]["file"] == "vehicles.csv", out)
    (d / ".env").write_text("x=1\n", encoding="utf-8")
    code, out = run(T / "profile.py", ".env", "--out", "q.json", cwd=d)
    report("profile: secret file skipped", "secret file" in out and json.loads((d / "q.json").read_text(encoding="utf-8"))["files"] == [], out)
    shutil.copytree(EX / "inputs", d / "generated-docs/_spec/inputs")
    code, out = run(T / "inputs.py", "generated-docs/_spec/inputs", "--text", "generated-docs/_spec/text", cwd=d)
    j = json.loads(out[out.index("{"):])
    code2, out2 = run(T / "inputs.py", "generated-docs/_spec", "--text", "generated-docs/_spec/text", cwd=d)
    gi = (d / ".gitignore").read_text(encoding="utf-8")
    report("inputs: ids found, data files header only, text extracts, rerun skips its own extracts, .gitignore entries once",
           code == 0 and [i["ids"] for i in j["inputs"] if i["name"] == "fleet-requirements.md"][0][:3] == ["FLT-1", "FLT-2", "FLT-3"]
           and "header only" in out and "YV2" not in (d / "generated-docs/_spec/text/vehicles.csv.txt").read_text(encoding="utf-8")
           and (d / "generated-docs/_spec/text/fleet-requirements.md.txt").is_file() and ".txt.txt" not in out2 and out2.count("fleet-requirements.md ·") == 1
           and gi.count("/generated-docs/_spec/text/") == 1 and "/generated-docs/_spec/inputs/" in gi and "added to .gitignore" not in out2, out + out2)
    (d / "tickets.csv").write_text('Key,Summary,Description,Assignee,Reporter\nABC-7,Load orders,"Daily, by 06:00",Jane Doe,jane@example.com\n', encoding="utf-8")
    (d / "credentials.json").write_text("{}", encoding="utf-8")
    (d / "std.md").write_text("Dates in ISO-8601, files UTF-8, hashes SHA-256, Q1-2025, COVID-19, S3-1, PI-3, GDPR-17; story REQ-4, EPIC 12, EPIC_12, EPIC-12 and ABC-12.\n", encoding="utf-8")
    (d / "rows.json").write_text(json.dumps([{"vin": f"V{i}", "plate": f"P{i}", "km": i} for i in range(8)]), encoding="utf-8")
    (d / "config.json").write_text('{"source": "fms", "schedule": "05:00"}', encoding="utf-8")
    (d / "sub").mkdir()
    (d / "sub/std.md").write_text("REQ-9\n", encoding="utf-8")
    code, out = run(T / "inputs.py", "tickets.csv", "credentials.json", "std.md", "rows.json", "config.json", "sub", "--text", "t2", cwd=d)
    tx = (d / "t2/tickets.csv.txt").read_text(encoding="utf-8")
    rj = (d / "t2/rows.json.txt").read_text(encoding="utf-8")
    gi = (d / ".gitignore").read_text(encoding="utf-8")
    report("inputs: bare Key column, kept columns only, secret not opened, stop-list, EPIC 12 = EPIC-12, JSON records keys only, no nonsense .gitignore line",
           "tickets" in out and '"ABC-7"' in out and "secret file: not opened" in out and "Jane" not in tx and "example.com" not in tx
           and not any(x in out for x in ("ISO-8601", "UTF-8", "SHA-256", "Q1-2025", "COVID-19", "S3-1", "PI-3", "GDPR-17", "EPIC 12", "EPIC_12"))
           and out.count('"EPIC-12"') == 1 and '"REQ-4"' in out and '"ABC-12"' in out
           and "keys: km, plate, vin" in rj and "V1" not in rj and "structure only" in out and "05:00" in (d / "t2/config.json.txt").read_text(encoding="utf-8")
           and (d / "t2/std.md.txt").is_file() and (d / "t2/sub__std.md.txt").read_text(encoding="utf-8").startswith("REQ-9") and "/t2/" in gi
           and "\n/inputs/" not in gi, out)
    for name, desc in (("fake-platform", "description: >\n  Rules for Snowflake, dbt and\n  Azure Data Factory work."), ("fake-app", "description: Streamlit apps on Snowflake."),
                       ("fake-review", "description: Reviews Snowflake and Airflow code.")):
        (d / f".claude/skills/darshan-singh-meel-{name}").mkdir(parents=True)
        (d / f".claude/skills/darshan-singh-meel-{name}/SKILL.md").write_text(f"---\nname: darshan-singh-meel-{name}\n{desc}\n---\n# Body mentions Kafka\n", encoding="utf-8")
    code, out = run(T / "skills.py", "Snowflake", "ADF", "Kafka", cwd=d, home=d)
    report("skills: folded description, alias (ADF), ranked by techs matched, process skills left out, body ignored, offer line",
           code == 0 and out.index("fake-platform · Snowflake, ADF") < out.index("fake-app · Snowflake") and "fake-review" not in out
           and "offer: darshan-singh-meel-fake-platform, darshan-singh-meel-fake-app" in out and "no skill: Kafka" in out, out)
    shutil.rmtree(d, ignore_errors=True)
    print(f"{n - fails}/{n} passed")
    sys.exit(1 if fails else 0)



main()
