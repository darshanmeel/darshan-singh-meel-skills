"""Build one code review report from a JSON spec: fixed sections, one look, diagrams by the docs-v2 flow renderer
(docs-v2 missing: built-in style, diagrams as text).

Usage: python build.py <spec.json> <out.html>   (run from the repo root: cited paths and lines are checked there)
Spec format: ../spec.md. ERROR lines stop the build; WARN lines are fixed or explained.
"""
import html
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DOCS = Path(__file__).resolve().parents[3] / "darshan-singh-meel-docs-v2" / "references" / "templates"
VERDICTS = ["Approve", "Approve with changes", "Request changes"]
SEVS = ["Must", "Should"]
AREAS = ["Correctness", "Security", "Performance", "Design", "Complexity", "Size", "Slop", "Tests", "Obvious", "Data"]
CONFIDENCE = ["High", "Medium", "Check"]
BUDGET = {"problem": 25, "why": 20, "summary": 25, "what": 20, "evidence": 25}
IMPACT_TAGS = ["changed", "fix"]  # fix = box the proposed fix changes (whole-repo review)
MAX_LANE, MAX_CHECKED = 12, 10
COMMON = {"the", "and", "with", "use", "for", "inst", "from", "not", "only", "add", "too", "also"}
MAX_OTHER, MAX_SNIPPET = 10, 12
SECRET = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.(pem|key|p12|pfx|jks|keystore|tfvars)|[^/]*\.tfstate[^/]*|id_(rsa|dsa|ecdsa|ed25519)[^/]*|"
                    r"credentials[^/]*|secrets?[^/]*|\.npmrc|\.pypirc|\.netrc|\.git-credentials|\.docker/config\.json|"
                    r"kubeconfig[^/]*|profiles\.yml)$|(^|/)[^/]*secret[^/]*/", re.I)
ABS = re.compile(r"(?<![\w])[A-Za-z]:[\\/]|(?<![\w.~])/Users/|(?<![\w])~/")
UNIX = re.compile(r"(?<![\w.~])/(?:home|root|tmp|var)/")  # may be a route: WARN, skipped after an HTTP verb
VERB = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+`?$")
KEYS = r"[\w.-]*(?:passw(?:or)?d|pwd|secret|token|api_?key|access_?key|private_?key)[\w.-]*"
SECRET_VALUE = [  # literal secret values: quoted, YAML/env style, or the password in a connection string
    re.compile(rf"""(?i)\b({KEYS})["']?\s*(?::\s*\w+\s*)?[:=]\s*(["'])(?!<redacted>|\$\{{|\{{\{{)[^"'\n]+\2"""),
    re.compile(rf"""(?im)^[\s`>-]*(?:export\s+)?({KEYS})\s*[:=][ \t]*(?!<redacted>|\$|\{{|\*|(?:str|int|bytes|bool|None|null|true|false|SecretStr|Optional)\b)[^\s"'#,;.(){{}}\[\]`]+(?=[\s"'#,;`]|$)"""),
    re.compile(r"(?i)\b\w+://[^\s:/@]+:(?!<redacted>|\$)([^\s@/]+)@"),
]
LINES = re.compile(r"^(\d+)(?:-(\d+))?$")
CSS = """.verdict{display:inline-block;font:600 13px/1.4 "IBM Plex Mono",Consolas,monospace;padding:3px 10px;border-radius:6px;border:1px solid}
.verdict.rc{color:var(--red);border-color:var(--red)} .verdict.ac{color:var(--amber-ink);background:var(--amber);border-color:var(--amber-ink)}
.verdict.ok{color:var(--green);border-color:var(--green)} .sev{font:600 11px/1.4 "IBM Plex Mono",Consolas,monospace;letter-spacing:.06em}
.sev.Must{color:var(--red)} .sev.Should{color:var(--amber-ink)} .fd{border-top:1px solid var(--line);padding:10px 0 4px;margin-top:8px}
.fd .hd{font-family:"IBM Plex Mono",Consolas,monospace;font-size:12.5px} pre.snip{background:var(--soft);border:1px solid var(--line);
border-radius:6px;padding:8px 12px;font-size:12.5px;overflow-x:auto;margin:6px 0} pre.snip code{background:none;border:0;padding:0} .file{margin-top:22px}
.map .lane span{max-width:88px;white-space:normal;overflow-wrap:anywhere;line-height:1.3}"""


# Used when docs-v2 is not installed: same tokens as docs-v2 style.css, light and dark.
BASIC_CSS = """:root{--ground:#F6F6F3;--card:#FFF;--line:#D9DBDF;--ink:#17191D;--muted:#5B6068;--soft:#EEEFEC;--amber:#FCEBC8;
--amber-ink:#8A5A00;--green:#1E6B43;--red:#A12D2D;--lav:#E7E2F5;--lav-ink:#6B4FA8}
@media (prefers-color-scheme:dark){:root{--ground:#15171A;--card:#1E2125;--line:#3A3E44;--ink:#E8E9EB;--muted:#A3A8B0;--soft:#2A2D32;
--amber:#4A3A12;--amber-ink:#F0C060;--green:#6FCF97;--red:#F08080;--lav:#3A3150;--lav-ink:#C9B8F0}}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.55 "Segoe UI",Arial,sans-serif}
main{max-width:920px;margin:0 auto;padding:24px 16px} section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin:18px 0}
a{color:inherit} code{font-size:13px;background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px;overflow-wrap:anywhere}
.eyebrow,.sub1,.key{font-size:12px;color:var(--muted)} .cap{font-size:12px;margin:8px 0 0} .toc a{margin-right:14px;font-size:13px}
.scroll{overflow-x:auto} table{border-collapse:collapse} th,td{text-align:left;vertical-align:top;padding:6px 10px;border:1px solid var(--line)}
.chip{font-size:11px;border:1px solid;border-radius:4px;padding:0 5px} .chip.syn{color:var(--lav-ink);background:var(--lav)}
ul.flow{font-family:Consolas,monospace;font-size:13px} .flow .fail{color:var(--red)}"""


def basic_esc(text, wbr=False):
    """docs-v2 esc without its break points: `code` -> <code>, **bold** -> <b>, [synthetic] -> badge."""
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(str(text)))
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("[synthetic]", '<span class="chip syn">synthetic</span>')


def text_diagram(flow):
    """A flow as text: one line per box with arrows out, e.g. 'a → b, c (join)'; boxes without arrows listed alone."""
    nodes = {n.get("id"): n for n in flow.get("nodes", [])}
    shown = set()

    def box(i):
        n = nodes.get(i, {"label": i})
        t = basic_esc(n.get("label", i)) + (f' [{basic_esc(n["tag"])}]' if n.get("tag") else "")
        if n.get("sub") and i not in shown:
            t += f" ({basic_esc(n['sub'])})"
        shown.add(i)
        return t

    out = {}
    for e in flow.get("edges", []):
        to = box(e.get("to")) + (f" ({basic_esc(e['label'])})" if e.get("label") else "")
        out.setdefault(e.get("from"), []).append(f'<span class="fail">{to}</span>' if e.get("fail") else to)
    lines = [f"{box(k)} &rarr; {', '.join(v)}" for k, v in out.items()]
    lines += [box(i) for i in nodes if i not in shown]
    return '<ul class="flow">' + "".join(f"<li>{x}</li>" for x in lines) + "</ul>", []


def docs_v2():
    """The one link to docs-v2: (esc, diagram(flow spec) -> (html, warns), style.css, None).
    Missing or incompatible -> built-in style, text diagrams, and the reason as 4th value."""
    if not (DOCS / "build.py").is_file() or not (DOCS / "style.css").is_file():
        return basic_esc, text_diagram, BASIC_CSS, "docs-v2 not installed"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(DOCS))  # its own imports (inventory.py)
    try:
        spec = importlib.util.spec_from_file_location("docs_v2_build", DOCS / "build.py")
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    except Exception:
        return basic_esc, text_diagram, BASIC_CSS, "docs-v2 does not load"
    if any(not hasattr(d, x) for x in ("flow", "uid", "LATE", "esc")):
        return basic_esc, text_diagram, BASIC_CSS, "docs-v2 has no flow, uid, LATE or esc"

    def diagram(flow):
        d.LATE.clear()
        try:
            out = d.flow(flow, d.uid(), "")
        except SystemExit as e:
            raise ValueError(str(e.code).removeprefix("ERROR ")) from None
        return out, list(dict.fromkeys(d.LATE))
    return d.esc, diagram, (DOCS / "style.css").read_text(encoding="utf-8"), None


def words(text):
    return len([w for w in str(text).split() if re.search(r"\w", w)])


def strings(x):
    if isinstance(x, dict):
        return [s for v in x.values() for s in strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in strings(v)]
    return [x] if isinstance(x, str) else []


def has_files(root, out):
    skip = {"reviews", ".git"}
    return any(p.is_file() and p.resolve() != out.resolve() for p in root.rglob("*") if not skip & set(p.relative_to(root).parts))


def cite(where, path, lines, root, err, check_files):
    """A path from the repo root that exists; lines within the file. Secret files: path only, never opened."""
    if not path or "\\" in path or path.startswith("/") or ".." in path.split("/") or ABS.search(path) or UNIX.search(path):
        return err.append(f"{where}: path '{path}' must be relative to the repo root, with / (no .., no absolute path)")
    secret = bool(SECRET.search(path))
    if secret and lines:
        return err.append(f"{where}: {path} is a secret file: cite it by path only (no lines, never opened)")
    if lines and not LINES.match(str(lines)):
        return err.append(f"{where}: lines '{lines}' must be N or N-M")
    if not check_files:
        return
    f = root / path
    if not f.is_file():
        return err.append(f"{where}: {path} is not a file in the repo")
    if lines and not secret:
        a, b = LINES.match(str(lines)).groups()
        a, b = int(a), int(b or a)
        data = f.read_bytes()
        n = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        if a < 1 or b < a or b > n:
            err.append(f"{where}: lines {lines} outside {path} (1-{n})")


def diagram_text_dup(dg, f):
    """True when every word in the diagram's boxes and arrows is already in the finding's text."""
    have = set(re.findall(r"\w+", " ".join(str(f.get(k, "")) for k in ("problem", "why", "fix", "code")).lower()))
    shown = " ".join(str(n.get(k, "")) for n in dg.get("nodes", []) for k in ("label", "sub", "in", "out"))
    shown += " " + " ".join(str(e.get("label", "")) for e in dg.get("edges", []))
    return set(re.findall(r"\w+", shown.lower())) <= have


def straight_chain(dg):
    """True when the diagram is one line of boxes: no lanes, no decision box, no box with 2+ arrows in or out."""
    if dg.get("lanes") or any(n.get("kind") == "decision" for n in dg.get("nodes", [])):
        return False
    ends = [[e.get(k) for e in dg.get("edges", [])] for k in ("from", "to")]
    return all(side.count(x) <= 1 for side in ends for x in side)


def stems(t):
    return {w[:4] for w in re.findall(r"\w{3,}", str(t).lower())} - COMMON


def secret_values(s):
    """Key names of likely secret literals in s (never the value)."""
    return [m.group(1) if r is not SECRET_VALUE[2] else "connection string" for r in SECRET_VALUE for m in r.finditer(s)]


def lane_warns(dg, where, warn):
    for name in dg.get("lanes", []):
        if len(str(name)) > MAX_LANE:
            warn.append(f"{where}: lane '{name}' is over {MAX_LANE} characters and runs into the boxes: shorten it")


def fix_drift(f):
    """True when the fix half of summary shares no word stem with fix or code."""
    want = stems(str(f.get("summary", "")).rsplit("·", 1)[-1])
    return bool(want) and not want & stems(str(f.get("fix", "")) + " " + str(f.get("code", "")))


def check(spec, root, check_files):
    err, warn = [], []
    if spec.get("verdict") not in VERDICTS:
        err.append(f"verdict '{spec.get('verdict')}' unknown: use one of {VERDICTS}")
    sc = spec.get("scope") or {}
    if not sc.get("reviewed") or not sc.get("goal"):
        err.append("scope needs reviewed (what was reviewed) and goal (what the change should do)")
    if not spec.get("checks"):
        warn.append("checks is empty: list what ran, or 'not run (why)'")
    for c in spec.get("checks", []):
        if not (isinstance(c, list) and len(c) == 2):
            err.append(f"check {c}: use [name, result]")
    seen, sums = set(), []
    for i, fl in enumerate(spec.get("files", []), 1):
        p = fl.get("path", "")
        where = f"files[{i}] {p}"
        cite(where, p, None, root, err, check_files)
        if p in seen:
            err.append(f"{where}: listed twice: one section per file")
        seen.add(p)
        if not fl.get("what"):
            err.append(f"{where}: needs what (one line: what changed / what it does)")
        elif words(fl["what"]) > BUDGET["what"]:
            warn.append(f"{where}: what is {words(fl['what'])} words (max {BUDGET['what']})")
        if not fl.get("findings"):
            err.append(f"{where}: no Must or Should finding: list the file under checked instead")
        if sum(1 for f in fl.get("findings", []) if f.get("diagram")) > 1:
            warn.append(f"{where}: more than one diagram: keep the one that explains the issue best")
        for j, f in enumerate(fl.get("findings", []), 1):
            w = f"{where} finding {j}"
            if f.get("sev") not in SEVS:
                err.append(f"{w}: sev '{f.get('sev')}' unknown: Must or Should (Minor goes to other)")
            if f.get("area") not in AREAS:
                err.append(f"{w}: area '{f.get('area')}' unknown: use one of {AREAS}")
            if not f.get("lines"):
                err.append(f"{w}: needs lines (N or N-M)") if not SECRET.search(p) else None
            cite(w, p, f.get("lines"), root, err, check_files)
            for a in f.get("also", []):
                ap, _, al = str(a).partition(":")
                cite(f"{w} also", ap, al or None, root, err, check_files)
                if ap == p:
                    err.append(f"{w} also: {ap} is the finding's own file")
            sums.append((w, p, stems(f.get("summary", ""))))
            for k in ("summary", "problem", "why", "fix"):
                if not str(f.get(k, "")).strip():
                    err.append(f"{w}: needs {k}" + (" (Must and Should need a concrete fix)" if k == "fix" else ""))
                elif k in BUDGET and words(f[k]) > BUDGET[k]:
                    warn.append(f"{w}: {k} is {words(f[k])} words (max {BUDGET[k]})")
            if f.get("summary") and "·" not in f["summary"]:
                warn.append(f"{w}: summary should read 'problem · fix'")
            elif f.get("summary") and fix_drift(f):
                warn.append(f"{w}: the fix in summary shares no word with fix: make them say the same fix")
            if f.get("evidence") and words(f["evidence"]) > BUDGET["evidence"]:
                warn.append(f"{w}: evidence is {words(f['evidence'])} words (max {BUDGET['evidence']})")
            if f.get("code"):
                if SECRET.search(p):
                    err.append(f"{w}: no code snippet for a secret file")
                elif len(str(f["code"]).splitlines()) > MAX_SNIPPET:
                    warn.append(f"{w}: code snippet over {MAX_SNIPPET} lines: show only the fix")
            dg = f.get("diagram")
            if dg:
                if not dg.get("title") or str(dg["title"]).startswith("Diagram"):
                    err.append(f"{w}: diagram needs a title (the build adds 'Diagram X ·')")
                if len(dg.get("nodes", [])) < 3:
                    warn.append(f"{w}: diagram has {len(dg.get('nodes', []))} boxes (min 3): say it in words instead")
                elif not dg.get("edges") or diagram_text_dup(dg, f):
                    warn.append(f"{w}: diagram duplicates the text (no arrows, or nothing beyond the finding's words): drop it")
                elif straight_chain(dg):
                    warn.append(f"{w}: diagram is a straight chain (a sentence): write it, or show what words can't "
                                "(before/after, fan-out, timeline)")
                lane_warns(dg, w, warn)
    for k, (w1, p1, s1) in enumerate(sums):
        for w2, p2, s2 in sums[k + 1:]:
            if p1 != p2 and s1 and len(s1 & s2) >= 0.6 * len(s1 | s2):
                warn.append(f"{w1} and {w2}: near-identical summary: same problem → one finding in the worst file, "
                            "the other paths in also")
    checked = spec.get("checked", [])
    for p in checked:
        cite(f"checked {p}", p, None, root, err, check_files)
        if p in seen:
            err.append(f"checked {p}: also has a file section")
    for p in sorted({p for p in checked if checked.count(p) > 1}):
        warn.append(f"checked {p}: listed twice")
    also = {str(a).partition(":")[0] for fl in spec.get("files", []) for f in fl.get("findings", []) for a in f.get("also", [])}
    other = spec.get("other", [])
    if len(other) > MAX_OTHER:
        err.append(f"other has {len(other)} items (max {MAX_OTHER}): keep the most useful")
    for i, o in enumerate(other, 1):
        cite(f"other[{i}]", o.get("path", ""), o.get("lines"), root, err, check_files)
        if o.get("area") not in AREAS:
            err.append(f"other[{i}]: area '{o.get('area')}' unknown: use one of {AREAS}")
        if not all(o.get(k) for k in ("what", "why", "impact")):
            err.append(f"other[{i}]: needs what, why and impact")
        if o.get("path") and o["path"] not in seen | set(checked) | also and not SECRET.search(o["path"]):
            warn.append(f"other[{i}]: {o['path']} is in neither files nor checked: add it to checked")
    for i, u in enumerate(spec.get("unused") or [], 1):
        if not (isinstance(u, list) and len(u) == 5):
            err.append(f"unused[{i}]: use [file, why it looks unused, evidence, confidence, suggestion]")
            continue
        cite(f"unused[{i}]", u[0], None, root, err, check_files)
        if u[3] not in CONFIDENCE:
            err.append(f"unused[{i}]: confidence '{u[3]}' unknown: use one of {CONFIDENCE}")
    imp = spec.get("impact")
    if imp:
        changed = [n for n in imp.get("nodes", []) if n.get("tag") in IMPACT_TAGS]
        if not changed:
            err.append("impact: mark the changed box(es) with tag 'changed' (a diff) or 'fix' (whole repo: what the fix changes)")
        lane_warns(imp, "impact", warn)
        if len(imp.get("nodes", [])) - len(changed) < 3:
            warn.append("impact: fewer than 3 affected boxes: list them in words instead of a diagram")
        if not imp.get("title") or str(imp["title"]).startswith("Diagram"):
            err.append("impact: needs a title (the build adds 'Diagram A ·')")
    sevs = [f.get("sev") for fl in spec.get("files", []) for f in fl.get("findings", [])]
    v = spec.get("verdict")
    if "Must" in sevs and v != "Request changes":
        err.append(f"verdict '{v}' with a Must finding: use 'Request changes'")
    elif "Must" not in sevs and "Should" in sevs and v == "Approve":
        err.append("verdict 'Approve' with a Should finding: use 'Approve with changes'")
    elif "Must" not in sevs and v == "Request changes":
        warn.append("verdict 'Request changes' without a Must finding: say why under questions, or use 'Approve with changes'")
    elif not sevs and v != "Approve":
        warn.append(f"verdict '{v}' without Must or Should findings: use 'Approve'")
    for s in strings(spec):
        if ABS.search(s):
            err.append(f"absolute or machine path in '{s[:60]}': paths are relative to the repo root")
        elif any(not VERB.search(s[:m.start()]) for m in UNIX.finditer(s)):
            warn.append(f"machine-like path in '{s[:60]}': use a repo-relative path (a route: put the HTTP verb before it)")
        for k in secret_values(s):
            err.append(f"likely secret value for '{k}': write <redacted>, cite the file and line")
    return err, list(dict.fromkeys(warn))


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def render(spec, esc, diagram, css, plain=None):
    """Returns (page, terminal lines, layout warns)."""
    ids, late = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), []
    rank = lambda f: (SEVS.index(f["sev"]), int(str(f.get("lines") or "0").split("-")[0]))
    files = sorted(spec.get("files", []), key=lambda fl: (min(SEVS.index(f["sev"]) for f in fl["findings"]), fl["path"]))
    flat, n = [], 0
    for fl in files:
        fl["findings"] = sorted(fl["findings"], key=rank)
        for f in fl["findings"]:
            n += 1
            f["n"] = n
            flat.append((fl["path"], f))
    loc = lambda p, ln: f"{p}:{ln}" if ln else p
    more = lambda f: f" (+{len(f['also'])} files)" if f.get("also") else ""

    def draw(dg, where):
        did = next(ids)
        try:
            out, w = diagram(dict({"numbered": False}, **dg, id=did))  # steps only when numbered: true
        except ValueError as e:
            sys.exit(f"ERROR {where} diagram: {e}")
        late.extend(w)
        cap = (f'<p class="key">Key: {esc(dg["key"])}</p>' if dg.get("key") else "") + (
            f'<p class="cap">Notice: {esc(dg["notice"])}</p>' if dg.get("notice") else "")
        why = f'<p class="cap">Diagram drawn as text: {plain}.</p>' if plain else ""
        return f'<h3 id="d-{did}">Diagram {did} &middot; {esc(dg["title"])}</h3>{out}{cap}{why}'

    other = spec.get("other", [])
    minor = {}
    for k, o in enumerate(other, 1):
        minor.setdefault(o["path"], []).append(k)
    count = {s: sum(1 for _, f in flat if f["sev"] == s) for s in SEVS}
    v = spec["verdict"]
    vcls = {"Request changes": "rc", "Approve with changes": "ac", "Approve": "ok"}[v]
    checks = " &middot; ".join(f"{esc(a)} &rarr; {esc(b)}" for a, b in spec.get("checks", [])) or "none"
    counts = (f"Must {count['Must']} &middot; Should {count['Should']} &middot; Minor {len(other)} &middot; "
              f"Questions {len(spec.get('questions', []))}")
    sc = spec["scope"]
    main = (f'<p><span class="verdict {vcls}">{esc(v)}</span></p><ul><li><b>Reviewed:</b> {esc(sc["reviewed"])}</li>'
            f'<li><b>Goal:</b> {esc(sc["goal"])}</li><li><b>Checks run:</b> {checks}</li><li><b>Findings:</b> {counts}</li></ul>')
    term = [f"Verdict: {v}"]
    for s, head in (("Must", "Must fix"), ("Should", "Should fix")):
        items = [(p, f) for p, f in flat if f["sev"] == s]
        if not items:
            continue
        main += f"<h3>{head}</h3><ul>" + "".join(
            f'<li>[{esc(f["area"])}] <a href="#f-{f["n"]}"><code>{esc(loc(p, f.get("lines")))}</code></a> &mdash; {esc(f["summary"])}{more(f)}</li>'
            for p, f in items) + "</ul>"
        term += [head] + [f"- [{f['area']}] {loc(p, f.get('lines'))} — {f['summary']}{more(f)}" for p, f in items]
    for p, f in flat:
        line = f"[{f['area']}] {loc(p, f.get('lines'))} — {f['summary']}"
        if words(line) > BUDGET["summary"]:
            late.append(f"main list line for {loc(p, f.get('lines'))} is {words(line)} words (max {BUDGET['summary']}): shorten summary")
    if spec.get("questions"):
        main += "<h3>Questions</h3><ul>" + "".join(f"<li>{esc(q)}</li>" for q in spec["questions"]) + "</ul>"
    if spec.get("impact"):
        main += draw(spec["impact"], "impact")
    if "unused" in spec:
        rows = spec["unused"] or []
        head = ["File", "Why it looks unused", "Evidence", "Confidence", "Suggestion"]
        main += "<h3>Unused files</h3>" + ('<div class="scroll"><table><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr>"
            + "".join("<tr>" + "".join(f'<td class="m">{esc(f"`{c}`" if k == 0 else c, True)}</td>' for k, c in enumerate(r))
                      + "</tr>" for r in rows) + "</table></div>" if rows else "<p>None found.</p>")
    if spec.get("net_size"):
        main += f'<p><b>Net size:</b> {esc(spec["net_size"])}</p>'
    body = ""
    for fl in files:
        c = {s: sum(1 for f in fl["findings"] if f["sev"] == s) for s in SEVS}
        tag = " &middot; ".join(f"{c[s]} {s}" for s in SEVS if c[s])
        body += f'<div class="file"><h3><code>{esc(fl["path"])}</code> <span class="sev">{tag}</span></h3><p class="lead">{esc(fl["what"])}</p>'
        for f in fl["findings"]:
            snip = f'<pre class="snip"><code>{html.escape(str(f["code"]))}</code></pre>' if f.get("code") else ""
            body += (f'<div class="fd" id="f-{f["n"]}"><div class="hd"><span class="sev {f["sev"]}">{f["sev"].upper()}</span> '
                     f'&middot; {esc(f["area"])} &middot; lines {esc(f.get("lines") or "-")}</div><ul><li><b>Problem:</b> {esc(f["problem"])}</li>'
                     f'<li><b>Why:</b> {esc(f["why"])}</li><li><b>Fix:</b> {esc(f["fix"])}</li>'
                     + (f'<li><b>Also:</b> {", ".join(f"<code>{esc(a)}</code>" for a in f["also"])}</li>' if f.get("also") else "")
                     + (f'<li><b>Evidence:</b> {esc(f["evidence"])}</li>' if f.get("evidence") else "") + f'</ul>{snip}'
                     + (draw(f["diagram"], f"{fl['path']} finding {f['n']}") if f.get("diagram") else "") + "</div>")
        if fl["path"] in minor:
            body += '<p class="cap">Minor: ' + ", ".join(f'<a href="#o-{k}">other {k}</a>' for k in minor[fl["path"]]) + "</p>"
        body += "</div>"
    note = lambda p: f" ({len(minor[p])} minor)" if p in minor else ""
    paths = spec.get("checked", [])
    if len(paths) > MAX_CHECKED:  # long lists grouped by folder
        by = {}
        for p in paths:
            d, _, name = p.rpartition("/")
            by.setdefault(d, []).append(name + note(p))
        checked = f"<p>{len(paths)} files</p><ul>" + "".join(
            f'<li><code>{esc(d + "/" if d else "./")}</code> {" &middot; ".join(esc(x) for x in names)}</li>'
            for d, names in sorted(by.items())) + "</ul>"
    else:
        checked = " &middot; ".join(f"<code>{esc(p)}</code>{note(p)}" for p in paths)
        checked = f"<p>{checked}</p>" if checked else ""
    secs = [("Main review", main), ("Files", body or "<p>No Must or Should findings.</p>"),
            ("Checked, no main findings", checked or "<p>None.</p>")]
    if other:
        secs.append(("Other findings", "<ol>" + "".join(
            f'<li id="o-{k}">[{esc(o["area"])}] <code>{esc(loc(o["path"], o.get("lines")))}</code> &mdash; {esc(o["what"])} &middot; '
            f'{esc(o["why"])} &middot; {esc(o["impact"])}</li>' for k, o in enumerate(other, 1)) + "</ol>"))
    toc = "".join(f'<a href="#s{i}">{i + 1} {t}</a>' for i, (t, _) in enumerate(secs))
    secs_html = "".join(f'<section><h2 id="s{i}">{i + 1} {t}</h2>{h}</section>' for i, (t, h) in enumerate(secs))
    commit = git("rev-parse", "--short", "HEAD")
    stamp = f'{esc(spec.get("date") or datetime.now().strftime("%Y-%m-%d %H:%M"))} &middot; ' + (
        f"repo {commit}" if commit else "repo not in git")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-review-v2"><title>{esc(spec.get("title") or "Code review")}</title>'
            f'<style>{css}{CSS}</style></head><body><main><div class="eyebrow">code review</div><h1>{esc(spec.get("title") or "Code review")}</h1>'
            f'<p class="sub1">{stamp}</p><nav class="toc">{toc}</nav>{secs_html}</main></body></html>')
    return page, term, late


def main(spec_path, out_path):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; spec text holds · and →
    sys.stderr.reconfigure(encoding="utf-8")
    esc, diagram, css, plain = docs_v2()
    if plain:
        print(f"note: {plain}: built-in style, diagrams drawn as text, layout not checked")
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out, root = Path(out_path), Path.cwd()
    if not out.parent.is_dir():
        sys.exit(f"ERROR output folder {out.parent.as_posix()} does not exist: create it (mkdir -p {out.parent.as_posix()}), then rerun")
    check_files = has_files(root, out)
    if not check_files:
        print(f"note: no repo files under {root.name or root}: path and line checks skipped")
    err, warn = check(spec, root, check_files)
    for w in warn:
        print("WARN", w)
    if err:
        sys.exit("\n".join(f"ERROR {e}" for e in err))
    page, term, late = render(spec, esc, diagram, css, plain)
    for w in dict.fromkeys(late):
        print("WARN", w)
    out.write_bytes(page.encode("ascii", "xmlcharrefreplace"))
    if git("rev-parse", "--is-inside-work-tree") == "true" and git("check-ignore", "-q", out.as_posix()) is None:
        print(f"note: {out.as_posix()} is not git-ignored: add /reviews/ to .gitignore")
    print("\n".join(term + [f"Report: {out.as_posix()}"] + ([f"Layout not checked: {plain}"] if plain else [])))
    nf = sum(len(fl["findings"]) for fl in spec.get("files", []))
    print(f"built {out.as_posix()}: {len(spec.get('files', []))} files, {nf} findings, {len(warn) + len(set(late))} WARN")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
