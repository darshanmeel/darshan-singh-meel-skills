"""Tests for review-v2 build.py: one case per builder rule. Usage: python run.py [skills folder] (default: this skill's parent)"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILLS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
BUILD = SKILLS / "darshan-singh-meel-review-v2" / "references" / "templates" / "build.py"
BASE = json.loads((SKILLS / "darshan-singh-meel-review-v2" / "references" / "examples" / "review-v2-example.json").read_text(encoding="utf-8"))
FILES = {"models/marts/fct_order_revenue.sql": 30, "src/export/orders_api.py": 40, "models/marts/schema.yml": 5,
         "src/export/__init__.py": 1, "tests/test_orders_api.py": 10, ".env": 2,
         "src/export/csv_legacy.py": 5}


def repo(git=False):
    d = Path(tempfile.mkdtemp())
    if git:
        subprocess.run(["git", "init", "-q", str(d)], check=True)
    for p, n in FILES.items():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        (d / p).write_text("".join(f"line {i}\n" for i in range(n)), encoding="utf-8")
    (d / "reviews" / "_spec").mkdir(parents=True)
    return d


def build(spec, build=BUILD, out="reviews/r.html", git=False):
    d = repo(git)
    (d / "reviews/_spec/r.json").write_text(json.dumps(spec), encoding="utf-8")
    r = subprocess.run([sys.executable, str(build), "reviews/_spec/r.json", out], cwd=d, capture_output=True, text=True, encoding="utf-8")
    html = (d / out).read_text(encoding="utf-8") if (d / out).is_file() else ""
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout + r.stderr, html


def edit(fn):
    s = copy.deepcopy(BASE)
    fn(s)
    return s


f0 = lambda s: s["files"][0]["findings"][0]  # the Must Data finding with a diagram
f1 = lambda s: s["files"][1]["findings"][0]  # the Must Security finding
f2 = lambda s: s["files"][1]["findings"][1]  # the Should Performance finding
ENV = {"path": ".env", "what": "committed env file", "findings": [{"sev": "Must", "area": "Security", "summary": "env file committed · remove it and rotate",
       "problem": "A committed env file is in the tree.", "why": "Anyone with repo access reads it.", "fix": "Remove it, git-ignore it and rotate the values."}]}
CHAIN = {"title": "chain", "nodes": [{"id": "a", "label": "aa", "col": 0, "row": 0}, {"id": "b", "label": "bb", "col": 1, "row": 0},
         {"id": "c", "label": "cc", "col": 2, "row": 0}], "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}
CASES = [  # (name, spec, expected exit, text expected in output)
    ("unknown path", edit(lambda s: f1(s).update() or s["files"][1].update(path="src/missing.py")), 1, "is not a file in the repo"),
    ("line past end", edit(lambda s: f1(s).update(lines="38-41")), 1, "outside src/export/orders_api.py (1-40)"),
    ("bad line format", edit(lambda s: f1(s).update(lines="31:34")), 1, "must be N or N-M"),
    ("missing lines", edit(lambda s: f1(s).pop("lines")), 1, "needs lines"),
    ("dotdot path", edit(lambda s: s["checked"].append("../x.py")), 1, "must be relative to the repo root"),
    ("absolute path in text", edit(lambda s: f1(s).update(why="see C:\\work\\x.py")), 1, "absolute or machine path"),
    ("severity Minor", edit(lambda s: f1(s).update(sev="Minor")), 1, "sev 'Minor' unknown"),
    ("unknown area", edit(lambda s: f1(s).update(area="Style")), 1, "area 'Style' unknown"),
    ("Must without fix", edit(lambda s: f1(s).update(fix="")), 1, "needs fix (Must and Should need a concrete fix)"),
    ("Must but Approve", edit(lambda s: s.update(verdict="Approve with changes")), 1, "with a Must finding: use 'Request changes'"),
    ("Should but Approve", edit(lambda s: (s.update(verdict="Approve"), [f.update(sev="Should") for fl in s["files"] for f in fl["findings"]])), 1, "use 'Approve with changes'"),
    ("Request changes, no Must", edit(lambda s: [f.update(sev="Should") for fl in s["files"] for f in fl["findings"]]), 0, "WARN verdict 'Request changes' without a Must"),
    ("unknown verdict", edit(lambda s: s.update(verdict="LGTM")), 1, "verdict 'LGTM' unknown"),
    ("file without findings", edit(lambda s: s["files"][1].update(findings=[])), 1, "list the file under checked instead"),
    ("checked also a file", edit(lambda s: s["checked"].append("src/export/orders_api.py")), 1, "also has a file section"),
    ("other over 10", edit(lambda s: s.update(other=s["other"] * 11)), 1, "other has 11 items (max 10)"),
    ("unused bad confidence", edit(lambda s: s.update(unused=[["src/export/__init__.py", "a", "b", "Low", "c"]])), 1, "confidence 'Low' unknown"),
    ("secret with lines", edit(lambda s: s["other"].append({"area": "Security", "path": ".env", "lines": "1", "what": "a", "why": "b", "impact": "c"})), 1, "secret file: cite it by path only"),
    ("secret by path ok", edit(lambda s: s["other"].append({"area": "Security", "path": ".env", "what": "committed env file", "why": "b", "impact": "c"})), 0, "0 WARN"),
    ("missing scope goal", edit(lambda s: s["scope"].pop("goal")), 1, "scope needs reviewed"),
    ("problem over budget", edit(lambda s: f1(s).update(problem=" ".join(["word"] * 26))), 0, "problem is 26 words (max 25)"),
    ("why over budget", edit(lambda s: f1(s).update(why=" ".join(["word"] * 21))), 0, "why is 21 words (max 20)"),
    ("main line over budget", edit(lambda s: f1(s).update(summary=" ".join(["word"] * 22) + " · fix it")), 0, "words (max 25): shorten summary"),
    ("summary without ·", edit(lambda s: f1(s).update(summary="use a bound parameter")), 0, "summary should read 'problem · fix'"),
    ("diagram under 3 boxes", edit(lambda s: f0(s)["diagram"].update(nodes=f0(s)["diagram"]["nodes"][:2], edges=f0(s)["diagram"]["edges"][:1])), 0, "boxes (min 3)"),
    ("diagram duplicates text", edit(lambda s: f0(s)["diagram"].update(nodes=[dict(n, label=w, sub="") for n, w in zip(CHAIN["nodes"], ["order_total", "order_items", "join"])], edges=CHAIN["edges"])), 0, "diagram duplicates the text"),
    ("diagram straight chain", edit(lambda s: f0(s).update(diagram=CHAIN)), 0, "diagram is a straight chain"),
    ("chain with lanes ok", edit(lambda s: f0(s).update(diagram=dict(CHAIN, lanes=["before", "after"]))), 0, "0 WARN"),
    ("secret file section, no lines", edit(lambda s: s["files"].append(ENV)), 0, "- [Security] .env — env file committed"),
    ("also lists other files", edit(lambda s: f1(s).update(also=["src/export/csv_legacy.py:2-3"])), 0, "(+1 files)"),
    ("also bad lines", edit(lambda s: f1(s).update(also=["src/export/csv_legacy.py:9"])), 1, "lines 9 outside src/export/csv_legacy.py"),
    ("near-identical summaries", edit(lambda s: s["files"][0]["findings"].append(dict(f2(s), lines="5"))), 0, "near-identical summary"),
    ("secret literal in code", edit(lambda s: f1(s).update(code='JWT_SECRET: hunter22x')), 1, "likely secret value for 'JWT_SECRET'"),
    ("secret quoted in problem", edit(lambda s: f1(s).update(problem='`api_key = "abc123"` is committed.')), 1, "likely secret value for 'api_key'"),
    ("password in connection string", edit(lambda s: f1(s).update(evidence="postgresql://app:pw1@db/x")), 1, "likely secret value for 'connection string'"),
    ("redacted secret ok", edit(lambda s: f1(s).update(code="JWT_SECRET: <redacted>")), 0, "0 WARN"),
    ("route is not a machine path", edit(lambda s: f1(s).update(why="GET /home/feed leaks rows.")), 0, "0 WARN"),
    ("machine path in text", edit(lambda s: f1(s).update(why="cache written to /tmp/x.")), 0, "machine-like path"),
    ("other on unlisted file", edit(lambda s: s["other"][0].update(path="src/export/csv_legacy.py", lines="2")), 0, "is in neither files nor checked"),
    ("checked twice", edit(lambda s: s["checked"].append("src/export/__init__.py")), 0, "checked src/export/__init__.py: listed twice"),
    ("diagram without title", edit(lambda s: f0(s)["diagram"].pop("title")), 1, "diagram needs a title"),
    ("impact under 3 affected", edit(lambda s: s["impact"].update(nodes=s["impact"]["nodes"][:3], edges=s["impact"]["edges"][:2])), 0, "fewer than 3 affected boxes"),
    ("impact without changed", edit(lambda s: s["impact"]["nodes"][0].pop("tag")), 1, "mark the changed box"),
    ("snippet too long", edit(lambda s: f1(s).update(code="\n".join(["x = 1"] * 13))), 0, "code snippet over 12 lines"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fails = 0
    code, out, page = build(BASE)
    ok = code == 0 and "0 WARN" in out and "Verdict: Request changes" in out
    links = re.findall(r'href="#(f-\d+)"', page)
    ok = ok and len(links) == 3 and all(page.count(f'id="{x}"') == 1 for x in links)  # each main line -> one finding
    ok = ok and "Must 2 &middot; Should 1 &middot; Minor 1" in page and "(1 minor)" in page and "Diagram B" in page
    print(("PASS" if ok else "FAIL"), "valid spec: counts, links, terminal summary")
    fails += not ok
    for name, spec, want_code, want in CASES:
        code, out, _ = build(spec)
        ok = code == want_code and want in out
        fails += not ok
        print(("PASS" if ok else "FAIL"), name, "" if ok else f"\n  exit {code}, output:\n  {out.strip()[:600]}")
    code, out, _ = build(BASE, out="nope/r.html")
    ok = code == 1 and "output folder nope does not exist" in out
    fails += not ok
    print(("PASS" if ok else "FAIL"), "missing output folder")
    code, out, _ = build(BASE, git=True)
    ok = code == 0 and "note: reviews/r.html is not git-ignored" in out and "0 WARN" in out
    fails += not ok
    print(("PASS" if ok else "FAIL"), "not git-ignored is a note")
    code, out, _ = build(edit(lambda s: f1(s).update(code="JWT_SECRET: hunter22x")))
    ok = "hunter22x" not in out
    fails += not ok
    print(("PASS" if ok else "FAIL"), "secret value not echoed")
    for name, docs in (("docs-v2 incompatible", "LATE = []\nesc = str\n"),("docs-v2 missing", None)):
        fake = Path(tempfile.mkdtemp()) / "skills"
        shutil.copytree(BUILD.parents[2], fake / "darshan-singh-meel-review-v2")
        (fake / "darshan-singh-meel-docs-v2").mkdir()  # empty folder = not installed
        if docs:
            (fake / "darshan-singh-meel-docs-v2/references/templates").mkdir(parents=True)
            (fake / "darshan-singh-meel-docs-v2/references/templates/build.py").write_text(docs, encoding="utf-8")
            (fake / "darshan-singh-meel-docs-v2/references/templates/style.css").write_text("", encoding="utf-8")
        code, out, page = build(BASE, build=fake / "darshan-singh-meel-review-v2/references/templates/build.py")
        shutil.rmtree(fake.parent, ignore_errors=True)
        ok = (code == 0 and "0 WARN" in out and "ERROR" not in out and "note: docs-v2" in out and "Layout not checked" in out
              and page.count("Diagram drawn as text") == 2 and "stg_orders" in page and "&rarr;" in page and "--red:" in page)
        fails += not ok
        print(("PASS" if ok else "FAIL"), name, "→ built-in style, text diagrams", "" if ok else f"\n  exit {code}, output:\n  {out.strip()[:600]}")
    print(f"{len(CASES) + 6 - fails}/{len(CASES) + 6} passed")
    sys.exit(1 if fails else 0)


main()
