"""Tests for build.py and stack.py: one case per rule, run on copies of the example spec. Usage: python run.py"""
import copy
import html
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
BASE = json.loads((SKILL / "references" / "examples" / "tech-summary-example.json").read_text(encoding="utf-8"))


def run(script, *args, cwd):
    r = subprocess.run([sys.executable, "-B", str(script), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return r.returncode, r.stdout + r.stderr


def build(spec, git=False, md=False):
    d = Path(tempfile.mkdtemp())
    (d / "out").mkdir()
    if git:
        (d / ".git").mkdir()
        (d / "api" / "routes").mkdir(parents=True)
        (d / "api" / "services").mkdir(parents=True)
        (d / "api" / "services" / "shipments.py").write_text("x = 1\n" * 10, encoding="utf-8")
    (d / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
    code, text = run(T / "build.py", "spec.json", "out/t.html", *(["--md", "out/t.md"] if md else []), cwd=d)
    page = (d / "out" / "t.html").read_text(encoding="utf-8") if (d / "out" / "t.html").is_file() else ""
    mdtext = (d / "out" / "t.md").read_text(encoding="utf-8") if (d / "out" / "t.md").is_file() else ""
    marker = (d / "out" / ".generated-by-darshan-singh-meel-docs").is_file()
    shutil.rmtree(d, ignore_errors=True)
    return code, text, page, mdtext, marker


def strings(x, where="spec"):
    if isinstance(x, str):
        yield where, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f"{where}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f"{where}[{i}]")


def edit(fn):
    s = copy.deepcopy(BASE)
    fn(s)
    return s


S = lambda s, name: s["sections"][name]
B = lambda s, name, j=0: S(s, name)["blocks"][j]
many = lambda n, row: [dict(row, **{k: f"{v} {i}" for k, v in row.items() if k in ("name", "risk", "topic", "system", "cmd", "env", "tech")}) for i in range(n)]
CASES = [  # (name, spec, expected exit, text expected in the output)
    ("example builds clean", BASE, 0, "0 WARN"),
    ("section missing", edit(lambda s: s["sections"].pop("Top risks")), 1, "section 'Top risks' missing"),
    ("section unknown", edit(lambda s: s["sections"].update({"Costs": {"line": "none"}})), 1, "section 'Costs' unknown"),
    ("line and blocks", edit(lambda s: S(s, "Integrations").update(line="x")), 1, "`line` or blocks/subsections, not both"),
    ("line in an optional section ok", edit(lambda s: s["sections"].update({"Data model": {"line": "No persisted data: the service is stateless."}})), 0, "0 WARN"),
    ("line in a core section", edit(lambda s: s["sections"].update({"Run locally": {"line": "Not defined yet. Owner to decide."}})), 0, "section 'Run locally' is one line"),
    ("required block missing", edit(lambda s: S(s, "Components")["blocks"].pop(1)), 1, "needs a `components` block"),
    ("unknown block", edit(lambda s: B(s, "Data model", 1).update(type="gantt")), 1, "block type 'gantt' unknown"),
    ("generic subsection title", edit(lambda s: S(s, "Security and access").update(subsections=[{"title": "Overview", "blocks": [{"type": "text", "text": "Staff sign in with OIDC."}]}])), 0, "fits any repo"),
    ("row field missing", edit(lambda s: B(s, "Components", 1)["rows"][0].pop("where")), 1, "needs where"),
    ("risk status unknown", edit(lambda s: B(s, "Top risks")["rows"][0].update(status="Open")), 1, "status 'Open' not in"),
    ("direction unknown", edit(lambda s: B(s, "Integrations")["rows"][0].update(direction="sideways")), 1, "direction 'sideways'"),
    ("components over budget", edit(lambda s: B(s, "Components", 1).update(rows=many(9, B(s, "Components", 1)["rows"][0]))), 0, "9 components rows, budget 8"),
    ("risks over budget", edit(lambda s: B(s, "Top risks").update(rows=many(8, B(s, "Top risks")["rows"][0]))), 0, "8 risks rows, budget 7"),
    ("pointers over budget", edit(lambda s: B(s, "Where to look next").update(rows=many(11, B(s, "Where to look next")["rows"][0]))), 0, "budget 10"),
    ("component files", edit(lambda s: [r.update(where=f"api/x{i}.py") for i, r in enumerate(B(s, "Components", 1)["rows"])]), 0, "are single files"),
    ("component not in diagram", edit(lambda s: B(s, "Components", 1)["rows"][0].update(name="frontend")), 0, "'frontend' is no box"),
    ("flows over budget", edit(lambda s: S(s, "Main flows")["blocks"].extend(copy.deepcopy(S(s, "Main flows")["blocks"][:2]))), 0, "5 flows, budget 4"),
    ("steps over budget", edit(lambda s: B(s, "Main flows", 1)["steps"].extend(copy.deepcopy(B(s, "Main flows", 1)["steps"][:3]))), 0, "8 steps, budget 7"),
    ("step do too long", edit(lambda s: B(s, "Main flows")["steps"][0].update(do="post the new shipment with all parcels and the full address")), 0, "`do` over 8 words"),
    ("step without out", edit(lambda s: B(s, "Main flows")["steps"][0].pop("out")), 1, "step 1 needs from, to"),
    ("step unknown participant", edit(lambda s: B(s, "Main flows")["steps"][0].update(to="cdn")), 1, "step 1 needs from, to"),
    ("participant not a component", edit(lambda s: B(s, "Main flows")["participants"][0].update(label="gateway")), 0, "participant 'gateway' is no component"),
    ("example without source", edit(lambda s: B(s, "Main flows")["example"].pop("source")), 1, "example needs in, out and source"),
    ("entities over budget", edit(lambda s: B(s, "Data model")["entities"].extend({"id": f"x{i}", "name": f"extra_{i}", "keys": ["PK id"]} for i in range(8))), 0, "13 entities, budget 12"),
    ("too many columns", edit(lambda s: B(s, "Data model")["entities"][0].update(keys=["PK id", "a", "b", "c", "d", "e"])), 0, "lists 6 columns, budget 5"),
    ("relation bad card", edit(lambda s: B(s, "Data model")["rels"][0].update(card="many")), 1, "card in"),
    ("relation skips a row", edit(lambda s: B(s, "Data model")["entities"].extend({"id": f"x{i}", "name": f"extra_{i}", "keys": ["PK id"]} for i in range(4))
                                  or B(s, "Data model")["rels"].append({"a": "users", "b": "x3", "card": "1:N", "on": "user_id"})), 0, "skips a row"),
    ("flow box twice", edit(lambda s: B(s, "Components")["nodes"].append(dict(B(s, "Components")["nodes"][0], id="dup"))), 1, "repeats an id or a grid cell"),
    ("flow edge unknown", edit(lambda s: B(s, "Components")["edges"].append({"from": "api", "to": "cdn"})), 1, "names an unknown box"),
    ("flow without key", edit(lambda s: B(s, "Components").pop("key")), 0, "no key"),
    ("box text cut", edit(lambda s: B(s, "Components")["nodes"][1].update(label="web single page application for staff and drivers")), 0, "cut, shorten it"),
    ("scope empty", edit(lambda s: B(s, "At a glance", 1).update(doesnt=[])), 1, "scope `doesnt` needs 1-5 items"),
    ("table too long", edit(lambda s: B(s, "Security and access")["rows"].extend([["Topic", "How", "`x/`"]] * 9)), 0, "has 14 rows, budget 12"),
    ("config table", edit(lambda s: S(s, "Security and access")["blocks"].append({"type": "table", "head": ["Setting", "Default"], "rows": [["`LOG_LEVEL`", "info"]]})), 0, "settings table with defaults"),
    ("too long to read", edit(lambda s: S(s, "Security and access")["blocks"].extend({"type": "text", "text": f"Paragraph {i} " + "word " * 38} for i in range(60))), 0, "reading time"),
    ("chat voice", edit(lambda s: S(s, "Top risks").update(lead="As discussed, polling cost matters most.")), 0, "voice"),
    ("filler", edit(lambda s: S(s, "Top risks").update(lead="A robust design for polling.")), 0, "filler: 'robust'"),
    ("repeat", edit(lambda s: S(s, "Integrations").update(lead=S(s, "Components")["lead"])), 0, "repeat:"),
    ("TODO", edit(lambda s: S(s, "Top risks").update(lead="TODO")), 1, "TODO left"),
    ("absolute path", edit(lambda s: B(s, "Components", 1)["rows"][0].update(where="C:/work/web/src/")), 1, "absolute or machine path"),
    ("email", edit(lambda s: B(s, "At a glance")["rows"].append(["Contact", "ops@example.com"])), 1, "e-mail address or phone number"),
    ("secret in a command", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "export API_KEY=abc123", "does": "set key"})), 1, "likely secret value"),
    ("secret in a URL", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "psql postgres://app:hunter2@localhost/db", "does": "open db"})), 1, "likely secret value"),
    ("databricks token", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "databricks auth dapi" + "0123456789abcdef" * 2, "does": "x"})), 1, "likely secret value"),
    ("aws key", edit(lambda s: S(s, "Top risks").update(lead="Key AKIA" + "ABCDEFGHIJKLMNOP" + " is old.")), 1, "likely secret value"),
    ("jwt", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "curl -H 'x: eyJhbGciOi.eyJzdWIi.sig'", "does": "x"})), 1, "likely secret value"),
    ("bearer", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "curl -H 'Authorization: Bearer abcdefgh1234'", "does": "x"})), 1, "likely secret value"),
    ("unquoted token", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "run --token=abc123xyz", "does": "x"})), 1, "likely secret value"),
    ("git bash path", edit(lambda s: B(s, "Components", 1)["rows"][0].update(where="/c/Users/x/web/")), 1, "absolute or machine path"),
    ("unc path", edit(lambda s: B(s, "Components", 1)["rows"][0].update(where=r"\\server\share")), 1, "absolute or machine path"),
    ("env var path", edit(lambda s: B(s, "Components", 1)["rows"][0].update(where=r"%USERPROFILE%\web")), 1, "absolute or machine path"),
    ("workspace path", edit(lambda s: B(s, "Components", 1)["rows"][0].update(where="/Workspace/Users/x/nb")), 1, "absolute or machine path"),
    ("chat phrase", edit(lambda s: S(s, "Top risks").update(lead="In this session the polling cost matters most.")), 0, "voice"),
    ("neighbour label long", edit(lambda s: B(s, "Components")["edges"][0].update(label="https only")), 0, "between neighbours over 9"),
    ("facts over budget", edit(lambda s: B(s, "At a glance")["rows"].extend([["X", "y"]] * 3)), 0, "9 facts, budget 8"),
    ("defaults column", edit(lambda s: S(s, "Security and access")["blocks"].append({"type": "table", "head": ["Setting", "Defaults"], "rows": [["`A`", "1"]]})), 0, "settings table with defaults"),
    ("rule without line", edit(lambda s: B(s, "At a glance", 2)["rows"][0].update(where="api/services/shipments.py")), 1, "needs rule and where (path:line)"),
    ("rules over budget", edit(lambda s: B(s, "At a glance", 2).update(rows=[{"rule": f"Rule {i}", "where": f"a.py:{i}"} for i in range(6)])), 0, "6 rules, budget 5"),
    ("graph behind", edit(lambda s: s.update(graph="knowledge graph at 9f8e7d6")), 0, "graph 9f8e7d6 is not commit a1b2c3d"),
    ("graph folder link", edit(lambda s: B(s, "Where to look next")["rows"][0].update(go="`repo-knowledge-graph/index.md`")), 0, "points into the knowledge graph folder"),
    ("single-file job ok", edit(lambda s: [r.update(where=f"jobs/j{i}.py", kind="job") for i, r in enumerate(B(s, "Components", 1)["rows"])]), 0, "0 WARN"),
    ("redacted ok", edit(lambda s: B(s, "Run locally")["rows"].append({"cmd": "export API_KEY=<redacted>", "does": "set the carrier key"})), 0, "0 WARN"),
]


def checks():
    fails = 0
    for name, spec, code, want in CASES:
        got, text, *_ = build(spec)
        if got != code or want not in text:
            fails += 1
            print(f"FAIL {name}: exit {got} (want {code}), '{want}' not in:\n{text[-600:]}")
    # page, markdown and marker
    got, text, page, md, marker = build(BASE, md=True)
    for want, where in [('content="darshan-singh-meel-docs-tech-summary', page), ("<svg", page), ("min read", page), ("Solid = call", page),
                        ("<!-- generated by darshan-singh-meel-docs-tech-summary", md), ("sequenceDiagram", md), ("erDiagram", md),
                        ("flowchart LR", md), ("||--o{", md)]:
        if want not in where:
            fails += 1
            print(f"FAIL output: '{want}' missing")
    norm = lambda t: re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", t)).replace("`", "").replace("**", "").replace("\\|", "|"))
    hp = norm(page)
    mp = re.sub(r"\s+", "", html.unescape(md.replace("<br/>", " ")).replace("`", "").replace("**", "").replace("\\|", "|"))
    for w, text_ in strings(BASE["sections"]):
        if re.search(r"\.(type|id|from|to|a|b|kind|card|direction)$", w):
            continue
        t_ = re.sub(r"\s+", "", text_.replace("`", "").replace("**", ""))
        for out_name, got_ in (("HTML", hp), ("Markdown", mp)):
            if t_ not in got_:
                fails += 1
                print(f"FAIL {out_name} misses {w}: {text_[:60]}")
    if not marker:
        fails += 1
        print("FAIL output: marker file missing")
    if page.count("<section") != 11:
        fails += 1
        print("FAIL output: not 11 sections")
    # paths are checked when run from a repo root (a .git folder)
    got, text, *_ = build(BASE, git=True)
    if ("path 'api/routes/' not found" in text or "path 'web/src/' not found" not in text
            or "'api/services/shipments.py:41': the file has fewer lines" not in text):
        fails += 1
        print(f"FAIL path check:\n{text[-600:]}")
    # stack.py: pins found, secret files never read
    d = Path(tempfile.mkdtemp())
    (d / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.12"\ndependencies = ["fastapi==0.115.2", "celery>=5.4"]\n'
                                       '[tool.poetry.dependencies]\nhttpx = "^0.27"\n', encoding="utf-8")
    (d / "package.json").write_text('{"dependencies": {"react": "^18.3.1"}}', encoding="utf-8")
    (d / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (d / "versions.tf").write_text('terraform {\n  required_version = ">= 1.9"\n}\n', encoding="utf-8")
    (d / "environment.yml").write_text("dependencies:\n  - python=3.12\n  - pip:\n    - pandas==2.2.3\n", encoding="utf-8")
    (d / ".env").write_text("SECRET_TOKEN=abc\n", encoding="utf-8")
    (d / "node_modules").mkdir()
    (d / "node_modules" / "package.json").write_text('{"dependencies": {"leftpad": "1.0.0"}}', encoding="utf-8")
    got, text = run(T / "stack.py", ".", cwd=d)
    shutil.rmtree(d, ignore_errors=True)
    for want in ("Python | >=3.12 | pyproject.toml", "fastapi | ==0.115.2", "react | ^18.3.1 | package.json", "image | python:3.12-slim | Dockerfile",
                 "Terraform | >= 1.9 | versions.tf", "httpx | ^0.27", "python | 3.12 | environment.yml", "pandas | ==2.2.3 | environment.yml", "stack: 9 pins"):
        if want not in text:
            fails += 1
            print(f"FAIL stack: '{want}' not in:\n{text}")
    if "SECRET" in text or "leftpad" in text:
        fails += 1
        print("FAIL stack: read a secret file or node_modules")
    n = len(CASES) + 4
    print(f"{n - fails}/{n} passed" if not fails else f"{fails} failed")
    return fails


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(1 if checks() else 0)
