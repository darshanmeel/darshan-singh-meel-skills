"""Build one architecture review (current → problems → proposal → workflows → impact → migration) from a JSON spec:
fixed sections, one look, diagrams and Input → Process → Output strips by the docs-v2 renderer
(docs-v2 missing: built-in style, diagrams and strips as text).

Usage: python build.py <spec.json> <out.html>             (run from the repo root: cited paths and lines are checked there)
       python build.py --changed <spec.json> <out.html>   which sections cite files changed since <out.html> was built
       python build.py --use <spec.json> <C-id|M-n> <tool> make an alternative the pick (a change, or moves row n); lists every text to rewrite
       python build.py --checklist <spec.json>            write the accuracy checklist next to the spec (tick each item)
Spec format: ../spec.md. ERROR lines stop the build; WARN lines are fixed or explained.
"""
import hashlib
import html
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.3.0"
DOCS = Path(__file__).resolve().parents[3] / "darshan-singh-meel-docs-v2" / "references" / "templates"
MARKER = ".generated-by-darshan-singh-meel-docs"  # the knowledge-graph skill skips folders holding it
VERDICTS = ["keep", "evolve", "redesign"]
AREAS = {"bottleneck": "Bottleneck", "cost": "Cost driver", "spof": "Single point of failure", "scaling": "Scaling limit",
         "security": "Security", "correctness": "Correctness", "tech_debt": "Tech debt"}
SEVS = ["High", "Medium", "Low"]
DIMS = {"cost": "Cost", "performance": "Performance", "maintenance": "Maintenance", "tech_debt": "Tech debt", "risk": "Risk"}
KINDS = ["measured", "estimate"]
EFFORT, RISK = ["S", "M", "L"], ["Low", "Medium", "High"]
CASES = ["typical", "edge", "rejected", "failure"]
DECISIONS = ["keep", "move", "later"]
# target in Technical-doc shape: section → docs-v2 block types allowed (or one "stays: …" line)
# (Configuration, Security and access, Tests optional; Tests expected once a tool moves)
TECH = {"Data model": {"text", "er", "views", "bullets"}, "Configuration": {"config", "text", "bullets"},
        "Security and access": {"access", "text", "bullets"}, "Deploy and environments": {"flow", "steps", "io", "environments", "bullets"},
        "Operations": {"io", "symptoms", "tasks", "bullets"}, "Tests": {"tests", "text", "bullets"}}
TECH_NEED = ["Data model", "Deploy and environments", "Operations"]
VENDOR = {"amazon", "aws", "azure", "google", "microsoft", "apache", "cloud"}  # 'Amazon MWAA' is written 'MWAA'
UNCHECKED = re.compile(r"\b(unchecked|not (?:yet )?(?:checked|verified)|unverified|if its\b[^.;]*\bis)\b", re.I)
PATTERNS = set(re.findall(r"^### `([a-z0-9-]+)`", (Path(__file__).resolve().parents[1] / "patterns.md").read_text(encoding="utf-8"), re.M)
               if (Path(__file__).resolve().parents[1] / "patterns.md").is_file() else [])
CHECKLIST = "architecture-checklist.md"
SECTIONS = ["Summary", "Current architecture", "Problems", "Proposed architecture", "Workflows: current vs proposed",
            "Impact", "Migration", "Open questions and assumptions"]
CELL, DO, VALUE, LEAD_SENT = 40, 8, 12, 2  # word caps: any text · strip step `do` · strip and trace values · lead sentences
MAX_STEPS, MAX_LANE = 7, 12
PLACEHOLDER = {"skipped", "skip", "not run", "not called", "n/a", "na", "none", "unchanged", "same", "ok", "done"}
FILLER = re.compile(r"\b(robust|seamless(?:ly)?|leverag(?:e|es|ing)|cutting[- ]edge|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|"
                    r"world[- ]class|game[- ]chang\w*|synerg\w*|holistic|next[- ]generation|simply|basically|very|really|"
                    r"comprehensive|powerful|in order to|it is important to note|note that)\b", re.I)
SECRET = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.(pem|key|p12|pfx|jks|keystore|tfvars)|[^/]*\.tfstate[^/]*|id_(rsa|dsa|ecdsa|ed25519)[^/]*|"
                    r"credentials[^/]*|secrets?[^/]*|\.npmrc|\.pypirc|\.netrc|\.git-credentials|\.docker/config\.json|"
                    r"kubeconfig[^/]*|profiles\.yml)$|(^|/)[^/]*secret[^/]*/", re.I)
ABS = re.compile(r"(?<![\w])[A-Za-z]:[\\/]|(?<![\w.~])/(?:Users|home|root)/|(?<![\w])~/")
KEYS = r"[\w.-]*(?:passw(?:or)?d|pwd|secret|token|api_?key|access_?key|private_?key)[\w.-]*"
SECRET_VALUE = [  # literal secret values: quoted, YAML/env style, or the password in a connection string
    re.compile(rf"""(?i)\b({KEYS})["']?\s*(?::\s*\w+\s*)?[:=]\s*(["'])(?!<redacted>|\$\{{|\{{\{{)[^"'\n]+\2"""),
    re.compile(rf"""(?im)^[\s`>-]*(?:export\s+)?({KEYS})\s*[:=][ \t]*(?!<redacted>|\$|\{{|\*|(?:str|int|bytes|bool|None|null|true|false|SecretStr|Optional)\b)[^\s"'#,;.(){{}}\[\]`]+(?=[\s"'#,;`]|$)"""),
    re.compile(r"(?i)\b\w+://[^\s:/@]+:(?!<redacted>|\$)([^\s@/]+)@"),
]
CITE = re.compile(r"^(.+?)(?::(\d+(?:-\d+)?))?$")
RANGE = re.compile(r"\d[\d,.]*\s*(?:[–-]|to)\s*~?\$?\d[\d,.]*")
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
CSS = """.verdict{display:inline-block;font:600 13px/1.4 "IBM Plex Mono",Consolas,monospace;padding:3px 10px;border-radius:6px;border:1px solid;text-transform:uppercase}
.verdict.keep{color:var(--green);border-color:var(--green)} .verdict.evolve{color:var(--amber-ink);background:var(--amber);border-color:var(--amber-ink)}
.verdict.redesign{color:var(--red);border-color:var(--red)} .sev{font:600 11px/1.4 "IBM Plex Mono",Consolas,monospace;letter-spacing:.06em}
.sev.High{color:var(--red)} .sev.Medium{color:var(--amber-ink)} .sev.Low{color:var(--muted)}
.pb{border-top:1px solid var(--line);padding:10px 0 4px;margin-top:8px} .pb .hd{font-family:"IBM Plex Mono",Consolas,monospace;font-size:12.5px}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:8px}
.opt{border:1px solid var(--line);border-radius:8px;padding:8px 12px} .opt.chosen{border:2px solid var(--green)} .opt ul{padding-left:18px}
.wf{font:600 10px/1.4 "IBM Plex Mono",Consolas,monospace;letter-spacing:.06em;color:var(--muted);margin:12px 0 0}
.mig li{margin:6px 0} .qw{color:var(--green);border-color:var(--green)}
.map .lane span{max-width:88px;white-space:normal;overflow-wrap:anywhere;line-height:1.3}
.dec{font:600 11px/1.4 "IBM Plex Mono",Consolas,monospace;text-transform:uppercase} .dec.move{color:var(--amber-ink)} .dec.keep{color:var(--green)}
.dec.later{color:var(--muted)}"""

# Used when docs-v2 is not installed: same tokens as docs-v2 style.css, light and dark.
BASIC_CSS = """:root{--ground:#F6F6F3;--card:#FFF;--line:#D9DBDF;--ink:#17191D;--muted:#5B6068;--soft:#EEEFEC;--amber:#FCEBC8;
--amber-ink:#8A5A00;--green:#1E6B43;--red:#A12D2D;--lav:#E7E2F5;--lav-ink:#6B4FA8;--blue:#1F5FA8}
@media (prefers-color-scheme:dark){:root{--ground:#15171A;--card:#1E2125;--line:#3A3E44;--ink:#E8E9EB;--muted:#A3A8B0;--soft:#2A2D32;
--amber:#4A3A12;--amber-ink:#F0C060;--green:#6FCF97;--red:#F08080;--lav:#3A3150;--lav-ink:#C9B8F0;--blue:#8AB4F8}}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.55 "Segoe UI",Arial,sans-serif}
main{max-width:1104px;margin:0 auto;padding:24px 16px} section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin:18px 0}
a{color:inherit} code{font-size:13px;background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px;overflow-wrap:anywhere}
.eyebrow,.sub1,.key,.src{font-size:12px;color:var(--muted)} .cap{font-size:12px;margin:8px 0 0} .toc a{margin-right:14px;font-size:13px}
.scroll{overflow-x:auto} table{border-collapse:collapse} th,td{text-align:left;vertical-align:top;padding:6px 10px;border:1px solid var(--line)}
.chip{font-size:11px;border:1px solid;border-radius:4px;padding:0 5px} .chip.syn{color:var(--lav-ink);background:var(--lav)}
ul.flow,ol.ipo{font-family:Consolas,monospace;font-size:13px} .flow .fail{color:var(--red)}"""


def basic_esc(text, wbr=False):
    """docs-v2 esc without its break points: `code` -> <code>, **bold** -> <b>, [synthetic] -> badge."""
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(str(text)))
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("[synthetic]", '<span class="chip syn">synthetic</span>')


def text_diagram(flow):
    """A flow as text: one line per box with its arrows out; boxes without arrows listed alone."""
    nodes = {n.get("id"): n for n in flow.get("nodes", [])}
    shown = set()

    def box(i):
        n = nodes.get(i, {"label": i})
        t = basic_esc(n.get("label", i)) + (f' [{basic_esc(n["tag"])}]' if n.get("tag") else "")
        shown.add(i)
        return t
    out = {}
    for e in flow.get("edges", []):
        to = box(e.get("to")) + (f" ({basic_esc(e['label'])})" if e.get("label") else "")
        out.setdefault(e.get("from"), []).append(f'<span class="fail">{to}</span>' if e.get("fail") else to)
    lines = [f"{box(k)} &rarr; {', '.join(v)}" for k, v in out.items()] + [box(i) for i in nodes if i not in shown]
    return '<ul class="flow">' + "".join(f"<li>{x}</li>" for x in lines) + "</ul>", []


def values(v):
    return [x for _, x in v if x is not None] if isinstance(v, list) else [v]


def kv_text(v):
    return "; ".join(f"{basic_esc(k)}: {basic_esc(x)}" for k, x in v) if isinstance(v, list) else basic_esc(v)


def text_strip(b, sec, h3, ex0):
    """An Input → steps → Output strip and its trace as plain lists (docs-v2 missing)."""
    steps = "".join(f"<li>{k}. {basic_esc(s['do'])} &rarr; {basic_esc(s['out'])}"
                    + (f" (<code>{basic_esc(s['where'])}</code>)" if s.get("where") else "") + "</li>" for k, s in enumerate(b["steps"], 1))
    out = f'<ol class="ipo"><li>Input: {kv_text(b["input"])}</li>{steps}<li>Output: {kv_text(b["output"])}</li></ol>'
    for k, c in enumerate(b.get("examples") or [], ex0):
        at = " &middot; ".join(f"{j}: {kv_text(v) if v is not None else '&ndash;'}" for j, v in enumerate(c.get("at") or [], 1))
        out += (f'<p id="ex-{sec}.{h3}{chr(97 + k)}"><b>Example {sec}.{h3}{chr(97 + k)}</b> ({basic_esc(c["case"])}) {basic_esc(c["title"])}'
                f' &mdash; expect {basic_esc(c["expect"])}<br>In: {kv_text(c["in"])} &middot; {at} &middot; Out: {kv_text(c["out"])}</p>')
    return out


def text_blocks(bs, sec, h3):
    """docs-v2 blocks as plain lists (docs-v2 missing): text, bullets, typed rows, er tables, steps."""
    out = ""
    for b in bs:
        t = b.get("type")
        if t == "text":
            out += f'<p class="lead">{basic_esc(b["text"])}</p>'
        elif t == "bullets":
            out += "<ul>" + "".join(f"<li>{basic_esc(i)}</li>" for i in b["items"]) + "</ul>"
        elif t == "er":
            out += "<ul>" + "".join(f'<li><b>{basic_esc(e["name"])}</b>: {", ".join(basic_esc(c[0]) for c in e["cols"])}</li>'
                                    for e in b["entities"]) + "</ul>"
        elif t == "flow":
            out += text_diagram(b)[0]
        elif t == "io":
            out += f'<p>In: <code>{basic_esc(b["input"])}</code> &rarr; <code>{basic_esc(b.get("result", ""))}</code></p>'
        else:  # typed rows and steps: one line per row
            out += "<ul>" + "".join("<li>" + " &middot; ".join(basic_esc(c) for c in r) + "</li>" for r in b.get("rows", [])) + "</ul>"
    return out


def docs_v2():
    """The one link to docs-v2: {esc, diagram(flow) -> (html, warns), strip(ipo, sec, h3, ex0, suffix) -> html,
    blocks(list, sec, h3, slot) -> html, css, why}. Missing or incompatible -> built-in style, text diagrams, strips and
    blocks, and the reason in why."""
    plain = lambda why: {"esc": basic_esc, "diagram": text_diagram, "strip": lambda b, s, h, e, x="": text_strip(b, s, h, e),
                         "blocks": lambda bs, s, h, slot: text_blocks(bs, s, h), "css": BASIC_CSS, "why": why}
    if not (DOCS / "build.py").is_file() or not (DOCS / "style.css").is_file():
        return plain("docs-v2 not installed")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(DOCS))  # its own imports (inventory.py)
    try:
        spec = importlib.util.spec_from_file_location("docs_v2_build", DOCS / "build.py")
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    except Exception:
        return plain("docs-v2 does not load")
    if any(not hasattr(d, x) for x in ("flow", "uid", "LATE", "esc")):
        return plain("docs-v2 has no flow, uid, LATE or esc")
    pos = isinstance(getattr(d, "POS", None), dict)

    def diagram(flow):
        d.LATE.clear()
        try:
            out = d.flow(flow, d.uid(), "")
        except SystemExit as e:
            raise ValueError(str(e.code).removeprefix("ERROR ")) from None
        return out, list(dict.fromkeys(d.LATE))

    def strip(b, sec, h3, ex0, suffix=""):
        if not (hasattr(d, "ipo") and pos):
            return text_strip(b, sec, h3, ex0)
        d.POS.update(kind="", slot="", sec=sec, h3=h3, ex=ex0)
        d.POS.setdefault("said", set())
        try:
            out = d.ipo(dict(b))
        except SystemExit as e:
            raise ValueError(str(e.code).removeprefix("ERROR ")) from None
        return out.replace(f'id="st-{sec}.{h3}.', f'id="st-{sec}.{h3}{suffix}.') if suffix else out

    def blocks(bs, sec, h3, slot):
        if not (hasattr(d, "block") and pos):
            return text_blocks(bs, sec, h3)
        d.POS.update(kind="technical", slot=slot, sec=sec, h3=h3, ex=0)
        d.POS.setdefault("said", set())
        try:
            return "".join(d.block(dict(b), "technical") for b in bs)
        except (SystemExit, KeyError, TypeError) as e:
            raise ValueError(str(getattr(e, "code", e)).removeprefix("ERROR ")) from None
    return {"esc": d.esc, "diagram": diagram, "strip": strip, "blocks": blocks,
            "css": (DOCS / "style.css").read_text(encoding="utf-8"), "why": None}


def words(text):
    return len([w for w in str(text).split() if re.search(r"\w", w)])


def strings(x):
    if isinstance(x, dict):
        return [s for v in x.values() for s in strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in strings(v)]
    return [x] if isinstance(x, str) else []


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def has_files(root, out):
    skip = {"generated-docs", "reviews", ".git"}
    return any(p.is_file() and p.resolve() != out.resolve() for p in root.rglob("*") if not skip & set(p.relative_to(root).parts))


def cite(where, c, root, err, check_files, need_line=False):
    """`path` or `path:N[-M]` from the repo root; the file exists, lines inside it. Secret files: path only, never opened."""
    m = CITE.match(str(c or ""))
    path, lines = (m.group(1), m.group(2)) if m else ("", None)
    if not path or "\\" in path or path.startswith("/") or ".." in path.split("/") or ABS.search(path):
        return err.append(f"{where}: '{c}' must be a path from the repo root, with / (no .., no absolute path)")
    secret = bool(SECRET.search(path))
    if secret and lines:
        return err.append(f"{where}: {path} is a secret file: cite it by path only (no lines, never opened)")
    if need_line and not lines and not secret:
        err.append(f"{where}: '{c}' needs a line: path:N or path:N-M")
    if not check_files:
        return
    f = root / path
    if not f.is_file():
        return err.append(f"{where}: {path} is not a file in the repo")
    if lines and not secret:
        a, _, b = lines.partition("-")
        a, b = int(a), int(b or a)
        data = f.read_bytes()
        n = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        if a < 1 or b < a or b > n:
            err.append(f"{where}: lines {lines} outside {path} (1-{n})")


def cited_text(root, c):
    """The text of a cited path:N-M (None: no lines, a secret file, or unreadable)."""
    m = CITE.match(str(c or ""))
    if not m or not m.group(2) or SECRET.search(m.group(1)):
        return None
    a, _, b = m.group(2).partition("-")
    try:
        lines = (root / m.group(1)).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    return "\n".join(lines[int(a) - 1:int(b or a)])


def secret_values(s):
    return [m.group(1) if r is not SECRET_VALUE[2] else "connection string" for r in SECRET_VALUE for m in r.finditer(s)]


def sig_figs(num):
    """Significant figures of a written number: 1,200 -> 2 · 37.4 -> 3 · 0.05 -> 1."""
    digits = num.replace(",", "")
    whole, _, frac = digits.partition(".")
    s = (whole + frac).lstrip("0")
    return len(s if frac else s.rstrip("0")) or 1


def precise(text):
    """Numbers in text with more than 2 significant figures, ranges (a–b) left out."""
    t = RANGE.sub(" ", str(text))
    t = re.sub(r"\b\d{1,2}:\d{2}\b|\b(19|20)\d{2}\b|\b\d+(?:\.\d+){2,}\b", " ", t)  # times, years, versions
    t = re.sub(r"`[^`]*`|\b[A-Za-z][\w.-]*\d[\w.-]*\b", " ", t)  # names holding digits (t3.large, P1)
    return [n for n in NUMBER.findall(t) if sig_figs(n) > 2]


def basis(where, row, root, err, warn, check_files, facts, field):
    """A number's basis: measured -> source (path:line) or fact (facts.json); estimate -> assumption."""
    k = row.get("kind")
    if k not in KINDS:
        return err.append(f"{where}: kind '{k}' unknown: measured (from code, config, graph or tests, cited) or estimate (with its assumption)")
    if row.get("source"):
        cite(f"{where} source", row["source"], root, err, check_files)
    if k == "measured":
        if not row.get("source") and not row.get("fact"):
            err.append(f"{where}: measured needs source (path:line) or fact (a facts.json name)")
        num = [n.rstrip(",") for n in NUMBER.findall(re.sub(r"`[^`]*`", " ", str(row.get(field[0], ""))))]
        text = cited_text(root, row.get("source")) if check_files and row.get("source") and not row.get("fact") else None
        if text is not None and num and not any(re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", text) for n in num):
            warn.append(f"{where}: measured {', '.join(num)} is not in {row['source']}: cite the line holding it, use a fact, or mark it estimate")
        if not num and not row.get("fact") and re.search(r"\b(seconds?|minutes?|hours?|ms)\b", " ".join(str(row.get(x, "")) for x in field)):
            warn.append(f"{where}: a duration without a number from the source is an estimate (run, restart and wait times are not in code)")
        if row.get("fact") and check_files:
            f = facts.get(row["fact"])
            if f is None:
                err.append(f"{where}: fact '{row['fact']}' is not in facts.json next to the spec: add it with its how, then run "
                           "docs-v2 inventory.py --check-facts")
            elif str(f) not in " ".join(str(row.get(x, "")) for x in field):
                warn.append(f"{where}: fact '{row['fact']}' = {f}, not in {' / '.join(field)}")
    else:
        if not str(row.get("assumption", "")).strip():
            err.append(f"{where}: estimate needs assumption (what the number rests on)")
        loose = [n for x in field for n in precise(row.get(x, ""))]
        if loose:
            warn.append(f"{where}: estimate with invented precision ({', '.join(loose)}): round it or give a range (20–30%)")


def flow_check(where, dg, err, warn, need=3):
    if not isinstance(dg, dict) or not dg.get("nodes"):
        return err.append(f"{where}: needs a diagram (docs-v2 flow: nodes, edges, title)")
    if not dg.get("title") or str(dg["title"]).startswith("Diagram"):
        err.append(f"{where}: diagram needs a title (the build adds 'Diagram X ·')")
    if len(dg["nodes"]) < need:
        warn.append(f"{where}: diagram has {len(dg['nodes'])} boxes (min {need}): say it in words instead")
    for name in dg.get("lanes", []):
        if len(str(name)) > MAX_LANE:
            warn.append(f"{where}: lane '{name}' is over {MAX_LANE} characters and runs into the boxes: shorten it")


def ipo_check(where, b, root, err, warn, check_files):
    if not isinstance(b, dict):
        return err.append(f"{where}: needs input, steps [{{do, out, where?}}], output, examples")
    miss = [k for k in ("input", "steps", "output") if b.get(k) in (None, "", [])]
    if miss:
        return err.append(f"{where}: needs {', '.join(miss)} (input, steps [{{do, out, where?}}], output, examples)")
    steps = b["steps"]
    if len(steps) > MAX_STEPS:
        warn.append(f"{where}: {len(steps)} steps (max {MAX_STEPS}): merge plumbing into the step that produces data")
    for k, s in enumerate(steps, 1):
        if not (isinstance(s, dict) and s.get("do") and s.get("out")):
            err.append(f"{where} step {k}: needs do and out (the output of the step)")
        elif s.get("where"):
            cite(f"{where} step {k}", s["where"], root, err, check_files)
    ex = b.get("examples") or []
    if not ex:
        err.append(f"{where}: needs one example trace (case, title, expect, in, at, out)")
    elif len(ex) > 1:
        warn.append(f"{where}: {len(ex)} traces: one per strip, the case that shows the difference")
    for c in ex:
        lack = [f for f in ("case", "title", "expect", "in", "at", "out") if c.get(f) in (None, "", [])]
        if lack:
            err.append(f"{where}: example '{c.get('title', '')}' needs {', '.join(lack)}")
        if c.get("case") not in CASES + [None, ""]:
            err.append(f"{where}: example case '{c['case']}' unknown: use one of {CASES}")
        at = c.get("at") or []
        if isinstance(at, list) and at and len(at) != len(steps):
            err.append(f"{where}: example '{c.get('title', '')}': {len(at)} `at` values, want one per step ({len(steps)})")
        ph = [str(v) for v in at if isinstance(v, str) and v.strip(" .").lower() in PLACEHOLDER]
        if ph:
            warn.append(f"{where}: trace cells with placeholder words ({', '.join(ph)}): give the value at that step, \"=\" or null")
        if c.get("source"):
            cite(f"{where} example source", c["source"], root, err, check_files)


def prose(spec):
    """(where, text, cap, lead): every reader-facing text the build checks for budgets, filler and repeats."""
    out = [("summary", spec.get("summary", ""), CELL, True)]
    cur, pr = spec.get("current") or {}, spec.get("proposal") or {}
    out.append(("current lead", cur.get("lead", ""), CELL, True))
    out += [(f"runtime {r[0]}", r[1], CELL, False) for r in cur.get("runtime", []) if isinstance(r, list) and len(r) > 1]
    for i, h in enumerate(cur.get("hotspots", []), 1):
        out += [(f"hotspot {i}", h.get(k, ""), CELL, False) for k in ("what", "value", "assumption")]
    for p in spec.get("problems", []):
        out += [(p.get("id", "problem"), p.get(k, ""), CELL, False) for k in ("title", "detail", "cost", "accept")]
    out.append(("proposal lead", pr.get("lead", ""), CELL, True))
    for c in pr.get("changes", []):
        out += [(c.get("id", "change"), c.get(k, ""), CELL, False) for k in ("title", "what", "why")]
    for o in pr.get("options", []):
        out += [(f"option {o.get('name')}", o.get(k, ""), CELL, False) for k in ("what", "gains", "costs", "size", "why_not")]
    out += [("stays", s, CELL, False) for s in pr.get("stays", [])]
    for m in pr.get("moves", []):
        out += [(f"move {m.get('component')}", m.get(k, ""), CELL, False) for k in ("now", "to", "why", "until")]
        out += [(f"move {m.get('component')} alternative", a.get("tradeoff", ""), CELL, False) for a in m.get("alternatives") or [] if isinstance(a, dict)]
    for c in pr.get("changes", []):
        t = c.get("tool") if isinstance(c.get("tool"), dict) else {}
        out += [(f"{c.get('id')} pick", t.get("why", ""), CELL, False)] + [(f"{c.get('id')} prereq", x, CELL, False) for x in c.get("prereq", [])]
        out += [(f"{c.get('id')} alternative", a.get("tradeoff", ""), CELL, False) for a in c.get("alternatives", []) if isinstance(a, dict)]
    for name, v in (pr.get("technical") or {}).items():
        for b in [{"type": "text", "text": v}] if isinstance(v, str) else v if isinstance(v, list) else []:
            if isinstance(b, dict):
                out += [(f"target {name}", b.get("text", ""), CELL, True)] + [(f"target {name}", x, CELL, False) for x in b.get("items", [])]
                out += [(f"target {name}", x, CELL, False) for r in b.get("rows", []) if isinstance(r, list) for x in r if isinstance(x, str)]
    for i, w in enumerate(spec.get("workflows", []), 1):
        for side in ("current", "proposed"):
            b, at = w.get(side) or {}, f"workflow {i}"  # an unchanged step may repeat between its current and proposed strips
            out += [(at, v, VALUE, False) for v in values(b.get("input", "")) + values(b.get("output", ""))]
            for s in b.get("steps", []) if isinstance(b.get("steps"), list) else []:
                if isinstance(s, dict):
                    out += [(at, s.get("do", ""), DO, False), (at, s.get("out", ""), VALUE, False), (at, s.get("why", ""), CELL, False)]
            for c in b.get("examples") or []:
                vs = [c.get("title"), c.get("expect")] + values(c.get("in")) + values(c.get("out")) + [y for a in c.get("at") or [] for y in values(a)]
                out += [(at, v or "", VALUE, False) for v in vs]
    for i, r in enumerate(spec.get("impact", []), 1):
        out += [(f"impact {i}", r.get(k, ""), CELL, False) for k in ("now", "proposed", "saving", "assumption")]
    for i, m in enumerate(spec.get("migration", []), 1):
        out += [(f"migration {i}", m.get(k, ""), CELL, False) for k in ("step", "rollback")]
    out += [("questions", q, CELL, False) for q in spec.get("questions", [])]
    out += [("assumptions", x, CELL, False) for a in spec.get("assumptions", []) for x in (a if isinstance(a, list) else [a])]
    return [(w, str(t), cap, lead) for w, t, cap, lead in out if t is not None]


def word_rules(spec, warn):
    """Every word carries a fact: word caps, filler words, and no sentence said twice."""
    over, sents = {}, {}
    for where, t, cap, lead in prose(spec):
        if words(t) > cap:
            over.setdefault(cap, []).append(f"{where}: '{' '.join(t.split()[:6])} …' ({words(t)})")
        n = len(re.findall(r"[.!?](?=\s|$)", t))
        if lead and n > LEAD_SENT:
            warn.append(f"words: {where} has {n} sentences (max {LEAD_SENT}): lead with the conclusion, cut the rest")
        for m in FILLER.finditer(re.sub(r"`[^`]*`", " ", t)):
            warn.append(f"filler: '{m[0]}' in {where}: say the fact (a name, number, consequence) or cut the word")
        for part in re.split(r"(?<=[.;!?])\s+", re.sub(r"`[^`]*`", lambda m: m[0].replace(" ", "_"), t)):
            w = re.findall(r"\w+", part.lower())
            if len(w) >= 6:
                sents.setdefault(" ".join(w), set()).add(where)
    for cap, items in over.items():
        warn.append(f"words: {len(items)} texts over {cap} words ({'; '.join(items[:3])}): keep the fact, names and numbers; cut the prose")
    for t, at in sents.items():
        if len(at) > 1:
            warn.append(f"repeat: '{' '.join(t.split()[:10])}' in {', '.join(sorted(at))}: say it once, point to it from the other")


def forms(name):
    """How a tool name shows up in text: 'Amazon MWAA' also as 'MWAA'; 'Fivetran or Airbyte' and 'Python + pandas' as each part."""
    out = set()
    for part in re.split(r"\s+or\s+|\s*/\s*|\s+\+\s+|,\s*", str(name).split(" (")[0]):
        w = part.split()
        out.add(" ".join(w))
        while len(w) > 1 and w[0].lower() in VENDOR:
            w = w[1:]
        out.add(" ".join(w))
    return {f for f in out if len(f) >= 3}


def names(text, name, skip=""):
    """True when text names the tool (any of its forms not also in skip, e.g. the pick's own name)."""
    return any(re.search(rf"(?<!\w){re.escape(f)}(?!\w)", str(text), re.I) for f in forms(name)
               if not re.search(rf"(?<!\w){re.escape(f)}(?!\w)", skip, re.I))


def tied(spec, cid):
    """(where, text) of the proposed-side texts that depend on change cid's pick: the change, its moves row, its impact rows
    (not `now`), migration steps, the proposed strips of its workflows, the chosen option."""
    pr = spec.get("proposal") or {}
    c = next((x for x in pr.get("changes", []) if x.get("id") == cid), {})
    out = [(f"proposal {cid}.{k}", c.get(k, "")) for k in ("title", "what", "why")] + [(f"proposal {cid}.prereq", x) for x in c.get("prereq", [])]
    out += [(f"proposal.moves[{k}].{f}", m.get(f, "")) for k, m in enumerate(pr.get("moves", [])) if m.get("change") == cid for f in ("to", "why", "until")]
    out += [(f"impact[{k}].{f}", r.get(f, "")) for k, r in enumerate(spec.get("impact", [])) if r.get("change") == cid
            for f in ("proposed", "saving", "assumption")]
    out += [(f"migration[{k}].{f}", m.get(f, "")) for k, m in enumerate(spec.get("migration", [])) if cid in m.get("changes", [])
            for f in ("step", "rollback", "wait")]
    out += [(f"workflows[{k}].proposed", " · ".join(strings(w.get("proposed") or {}))) for k, w in enumerate(spec.get("workflows", []))
            if cid in w.get("changes", [])]
    out += [(f"option {o.get('name')}", o.get(f, "")) for o in pr.get("options", []) if o.get("chosen") for f in ("what", "gains", "costs", "size")]
    return [(w, t) for w, t in out if isinstance(t, str) and t]


def size_of(text):
    """(lines, tasks) after the first → of an option size ('~3,600 lines, 17 tasks → ~1,500 lines, 1 task'); before it when
    'same'. The largest count per unit wins (a total, not a per-model figure); a range counts at its upper end."""
    before, _, after = str(text).partition("→")
    side = before if not after or re.search(r"\bsame\b", after) else after

    def num(unit):
        found = [float((m[3] or m[1]).replace(",", "")) * (1000 if (m[4] if m[3] else m[2]) else 1)
                 for m in re.finditer(rf"(\d(?:[\d,.]*\d)?)\s*(k)?(?:\s*[–-]\s*~?(\d(?:[\d,.]*\d)?)\s*(k)?)?\s*(?:{unit})\b", side)]
        return max(found) if found else None
    return num("lines?"), num("tasks?|jobs?")


def target_check(pr, root, err, warn, check_files, cids, verdict):
    """Section 4 in Technical-doc shape: keep / move / later per component, each move a pick with signal and alternatives,
    the target's data model, deploy and operations (blocks, or one line saying they stay)."""
    moves = pr.get("moves", [])
    tools = {c.get("id") for c in pr.get("changes", []) if c.get("tool")}
    if not moves:
        warn.append("proposal moves is empty: one row per component: keep (why) · move (to, change) · later (what first)")
    for i, m in enumerate(moves, 1):
        w = f"move {i} ({m.get('component')})"
        if m.get("decision") not in DECISIONS:
            err.append(f"{w}: decision '{m.get('decision')}' unknown: use one of {DECISIONS}")
        for k in ("component", "now", "why"):
            if not str(m.get(k, "")).strip():
                err.append(f"{w}: needs {k}")
        if m.get("decision") == "move" and not (m.get("to") and m.get("change")):
            err.append(f"{w}: a move needs to (the target) and change (the C… that does it)")
        if m.get("change") and m["change"] not in cids:
            err.append(f"{w}: change '{m['change']}' is no change id")
        if m.get("current") and m.get("decision") != "keep":
            err.append(f"{w}: current (latest version, fits the target) means keep: drop current, or show the signal that it no longer fits")
        if m.get("decision") == "later" and not str(m.get("until", "")).strip():
            warn.append(f"{w}: later needs until: a condition someone can check (a number, a date, a docs page), not 'once it pays off'")
        if m.get("decision") == "move" and m.get("change") in cids and m.get("change") not in tools:
            warn.append(f"{w}: moves to {m.get('to')} but its change {m['change']} names no tool: add a change that does the move "
                        "(tool, signal, pattern, impact, migration step), or keep the row and tune in place")
        for k in ("why", "until"):
            if UNCHECKED.search(str(m.get(k, ""))):
                warn.append(f"{w}: '{UNCHECKED.search(str(m[k]))[0]}' in {k}: check the blocker in {m.get('to') or 'the tool'}'s official docs now, name the page")
        alts = m.get("alternatives")
        if alts is not None:
            if not (isinstance(alts, list) and 2 <= len(alts) <= 3 and all(isinstance(a, dict) and a.get("name") and a.get("tradeoff") for a in alts)):
                err.append(f"{w}: give 2-3 alternatives, each {{name, tradeoff}}")
        elif m.get("current") and m.get("decision") == "keep":
            pass  # current version and fits the target: nothing to suggest
        elif not (m.get("change") in tools and m.get("decision") == "move"):
            warn.append(f"{w}: no alternatives: name 2-3 current tools the user could ask for instead ({{name, tradeoff}}), keep and later rows too")
    moved = sum(1 for m in moves if m.get("decision") == "move")
    if verdict == "redesign" and moves and moved * 2 < len(moves):
        warn.append(f"verdict redesign but {moved} of {len(moves)} components move: evolve, or show the signals for the rest")
    if verdict != "redesign" and len(moves) >= 3 and moved == len(moves):
        warn.append("every component moves: that is a redesign; keep what works and say why it stays")
    for c in pr.get("changes", []):
        w, t = f"change {c.get('id')}", c.get("tool")
        alts = c.get("alternatives") or []
        if t is None:
            if alts:
                err.append(f"{w}: alternatives without tool: name the pick (tool: {{name, why}})")
            continue
        if not (isinstance(t, dict) and str(t.get("name", "")).strip() and str(t.get("why", "")).strip()):
            err.append(f"{w}: tool needs name and why (why it fits this repo)")
            continue
        if not 2 <= len(alts) <= 3 or not all(isinstance(a, dict) and a.get("name") and a.get("tradeoff") for a in alts):
            err.append(f"{w}: give 2-3 alternatives to {t['name']}, each {{name, tradeoff}}")
        if any(str(a.get("name", "")).lower() == t["name"].lower() for a in alts if isinstance(a, dict)):
            err.append(f"{w}: {t['name']} is both the pick and an alternative")
        if not c.get("signal"):
            err.append(f"{w}: a move to {t['name']} needs its signal: signal [path:line] showing the pattern in the code")
        for x in c.get("signal", []):
            cite(f"{w} signal", x, root, err, check_files, need_line=True)
        if PATTERNS and c.get("pattern") not in PATTERNS:
            warn.append(f"{w}: pattern '{c.get('pattern')}' is not in patterns.md: use its id, or add the move there")
        if not any(m.get("change") == c.get("id") and m.get("decision") == "move" for m in moves):
            warn.append(f"{w} moves to {t['name']} but no moves row (decision move) names it")
    free = {}
    for c in pr.get("changes", []):
        if c.get("free_in"):
            free.setdefault(str(c["free_in"]), []).append(c.get("id"))
    for tool, ids in free.items():
        if len(ids) >= 3 and not any(names(m.get("to", ""), tool) and (m.get("decision") == "move" or m.get("decision") == "later" and m.get("until"))
                                     for m in moves):
            warn.append(f"changes {', '.join(ids)} come free in {tool}: {len(ids)} fixes hand-built on the old engine are a signal for the move: "
                        f"add a move row to {tool} (or later with until: what must hold first), and size both options")
    opts = pr.get("options", [])
    chosen = next((o for o in opts if o.get("chosen")), None)
    if chosen and not str(chosen.get("why_not", "")).strip():
        cl, ct = size_of(chosen.get("size", ""))
        for o in opts:
            ol, ot = size_of(o.get("size", ""))
            if o is not chosen and None not in (cl, ct, ol, ot) and ol < cl and ot < ct:
                warn.append(f"option '{o.get('name')}' ends smaller than the chosen '{chosen.get('name')}' ({ol:g} vs {cl:g} lines, {ot:g} vs {ct:g} tasks): "
                            "choose it, or give the chosen option why_not: the blocker, checked in the docs (name the page)")
    for o in opts:
        for k in ("costs", "why_not"):
            if UNCHECKED.search(str(o.get(k, ""))):
                warn.append(f"option '{o.get('name')}': '{UNCHECKED.search(str(o[k]))[0]}' in {k}: check it in the official docs now, name the page")
    for o in pr.get("options", []):
        if not str(o.get("size", "")).strip():
            warn.append(f"option '{o.get('name')}': no size: lines, tasks and tests before → after (estimate), never costs only")
    for i, r in enumerate(pr.get("components", []), 1):
        if not (isinstance(r, list) and len(r) == 3):
            err.append(f"proposal components[{i}]: use [component, responsibility, where] (new or changed only)")
    tech = pr.get("technical") or {}
    for name in tech:
        if name not in TECH:
            err.append(f"proposal technical: '{name}' unknown: use {list(TECH)}")
    if "Tests" not in tech and tools:
        warn.append("proposal technical: a tool moves, so its tests move too: add Tests (tests block: what replaces each suite), or 'Stays: …'")
    for name, kinds in TECH.items():
        v = tech.get(name)
        if v is None:
            if name in TECH_NEED:
                warn.append(f"proposal technical: say what changes in {name}, or one line 'stays: …'")
        elif not isinstance(v, (str, list)) or (isinstance(v, list) and not v):
            err.append(f"proposal technical {name}: a list of docs-v2 blocks, or one line saying it stays")
        elif isinstance(v, list):
            for b in v:
                if not isinstance(b, dict) or b.get("type") not in kinds:
                    err.append(f"proposal technical {name}: block '{b.get('type') if isinstance(b, dict) else b}' not allowed: use {sorted(kinds)}")
                elif b["type"] in ("flow", "er") and not b.get("title"):
                    err.append(f"proposal technical {name}: {b['type']} needs a title (the build adds 'Diagram X ·')")


def check(spec, root, check_files, facts, has_review, inv=None):
    inv = inv or {}
    err, warn = [], []
    if not spec.get("title"):
        err.append("title missing")
    v = spec.get("verdict")
    if v not in VERDICTS:
        err.append(f"verdict '{v}' unknown: use one of {VERDICTS}")
    if not str(spec.get("summary", "")).strip():
        err.append("summary missing: one line, why this verdict")
    sub = str(spec.get("subtitle", ""))
    if sub and (sub.count("·") != 2 or sub.count("→") != 1):
        warn.append("subtitle should read '<stack> · <schedule> · <source> → <outputs>' (two ·, one →)")
    if spec.get("review"):
        cite("review", spec["review"], root, err, check_files)
    elif has_review:
        warn.append("reviews/ has a review but the spec names none: set review (its tech-debt findings feed Problems)")
    cur = spec.get("current") or {}
    flow_check("current l0", cur.get("l0"), err, warn)
    if isinstance(cur.get("l0"), dict):
        n = len(cur["l0"].get("nodes", []))
        if n > 7 or cur["l0"].get("lanes"):
            warn.append(f"current l0: the big picture is one row of 3-7 boxes without lanes ({n} boxes): the detail goes in components")
    flow_check("current components", cur.get("components"), err, warn)
    for i, r in enumerate(cur.get("runtime", []), 1):
        if not (isinstance(r, list) and len(r) in (2, 3)):
            err.append(f"runtime[{i}]: use [label, text] or [label, text, path:line]")
        elif len(r) == 3:
            cite(f"runtime[{i}]", r[2], root, err, check_files)
    if not cur.get("runtime"):
        warn.append("current runtime is empty: where it runs and how it deploys (scheduler, compute, deploy)")
    if not cur.get("hotspots"):
        warn.append("current hotspots is empty: where time and cost go")
    for i, h in enumerate(cur.get("hotspots", []), 1):
        if not (h.get("what") and h.get("value")):
            err.append(f"hotspot {i}: needs what and value")
        basis(f"hotspot {i}", h, root, err, warn, check_files, facts, ["value"])

    probs = spec.get("problems", [])
    pids = [p.get("id") for p in probs]
    if not probs:
        warn.append("problems is empty: with nothing to fix, the verdict is keep and the doc says why")
    for p in probs:
        w = f"problem {p.get('id')}"
        if not re.fullmatch(r"P\d+", str(p.get("id"))) or pids.count(p.get("id")) > 1:
            err.append(f"{w}: id must be P1, P2 … and unique")
        if p.get("area") not in AREAS:
            err.append(f"{w}: area '{p.get('area')}' unknown: use one of {list(AREAS)}")
        if p.get("sev") not in SEVS:
            err.append(f"{w}: sev '{p.get('sev')}' unknown: use one of {SEVS}")
        for k in ("title", "detail"):
            if not str(p.get(k, "")).strip():
                err.append(f"{w}: needs {k}")
        if not p.get("evidence"):
            err.append(f"{w}: needs evidence: at least one path:line from the repo")
        for c in p.get("evidence", []):
            cite(f"{w} evidence", c, root, err, check_files, need_line=True)

    pr = spec.get("proposal") or {}
    changes = pr.get("changes", [])
    cids = [c.get("id") for c in changes]
    if not changes:
        err.append("proposal changes is empty: keep still lists its small changes (the verdict says how big they are)")
    flow_check("proposal diagram", pr.get("diagram"), err, warn)
    if isinstance(pr.get("diagram"), dict) and not any(n.get("tag") in ("new", "changed") for n in pr["diagram"].get("nodes", [])):
        err.append("proposal diagram: tag the boxes the changes add or alter ('new' or 'changed')")
    fixed = set()
    for c in changes:
        w = f"change {c.get('id')}"
        if not re.fullmatch(r"C\d+", str(c.get("id"))) or cids.count(c.get("id")) > 1:
            err.append(f"{w}: id must be C1, C2 … and unique")
        for k in ("title", "what", "why"):
            if not str(c.get(k, "")).strip():
                err.append(f"{w}: needs {k}")
        if not c.get("fixes") and not c.get("goes_with"):
            err.append(f"{w}: fixes no problem: every change removes ≥1 problem (fixes: [P…]), or is required by one (goes_with: [C…])")
        for x in c.get("goes_with", []):
            if x not in cids or x == c.get("id"):
                err.append(f"{w}: goes_with '{x}' is no other change id")
        for p in c.get("fixes", []):
            if p not in pids:
                err.append(f"{w}: fixes '{p}', which is no problem id")
            fixed.add(p)
    opts = pr.get("options", [])
    if not 2 <= len(opts) <= 3:
        err.append(f"proposal options: {len(opts)} given: list 2-3 options considered, one chosen")
    if sum(1 for o in opts if o.get("chosen")) != 1:
        err.append("proposal options: mark exactly one option chosen: true")
    for o in opts:
        if not all(str(o.get(k, "")).strip() for k in ("name", "what", "gains", "costs")):
            err.append(f"option '{o.get('name')}': needs name, what, gains and costs (the trade-off)")
    if not pr.get("stays"):
        warn.append("proposal stays is empty: say what stays as it is")

    for p in probs:
        if p.get("sev") == "High" and p.get("id") not in fixed and not p.get("accept"):
            warn.append(f"problem {p.get('id')} is High and no change fixes it: add a change, or accept: 'why it stays'")
    highs = [p for p in probs if p.get("sev") == "High"]
    if v == "keep" and highs:
        warn.append(f"verdict keep with High problems ({', '.join(p['id'] for p in highs)}): evolve, or say why under accept")
    if v == "redesign" and not highs:
        warn.append("verdict redesign without a High problem: evolve, or raise the severity the evidence supports")

    target_check(pr, root, err, warn, check_files, cids, v)
    for c in changes:  # after --use: texts still written for the old pick
        t = c.get("tool")
        if not (isinstance(t, dict) and t.get("name")):
            continue
        for a in c.get("alternatives", []):
            hits = list(dict.fromkeys(w for w, x in tied(spec, c.get("id")) if isinstance(a, dict) and names(x, a.get("name", ""), t["name"])))
            if hits:
                warn.append(f"change {c.get('id')}: {', '.join(hits[:6])}{' …' if len(hits) > 6 else ''} name {a['name']}, an alternative, "
                            f"not the pick {t['name']}: rewrite them for {t['name']}")
    for q in spec.get("questions", []):
        if UNCHECKED.search(str(q)):
            warn.append(f"question '{str(q)[:50]}': '{UNCHECKED.search(str(q))[0]}': check a tool's behaviour in its official docs now "
                        "(name the page); ask only what the repo and docs cannot answer")
    if spec.get("current_doc"):
        cite("current_doc", spec["current_doc"], root, err, check_files)
    wfs = spec.get("workflows", [])
    if not 2 <= len(wfs) <= 3:
        warn.append(f"workflows: {len(wfs)} given: 2-3 real end-to-end flows")
    for i, wf in enumerate(wfs, 1):
        w = f"workflow {i}"
        if "→" not in str(wf.get("title", "")):
            warn.append(f"{w}: title should read '<input> → <output>'")
        for c in wf.get("changes", []) + wf.get("needs", []):
            if c not in cids:
                err.append(f"{w}: change '{c}' is no change id")
        if not wf.get("changes"):
            warn.append(f"{w}: name the changes that make the proposed flow differ (changes: [C…])")
        ipo_check(f"{w} current", wf.get("current"), root, err, warn, check_files)
        ipo_check(f"{w} proposed", wf.get("proposed"), root, err, warn, check_files)
        ps = (wf.get("proposed") or {}).get("steps") or []
        if isinstance(ps, list) and ps and not any(isinstance(x, dict) and x.get("why") for x in ps):
            warn.append(f"{w} proposed: give `why` on the steps the changes alter (section 4 Main flows shows it)")

    first = lambda b: ((b or {}).get("examples") or [{}])[0] if isinstance((b or {}).get("examples"), list) else {}
    if wfs and not any(isinstance(first(wf.get("current")), dict) and first(wf.get("current")).get("case") == "typical" for wf in wfs):
        warn.append("workflows: none is typical: trace the main run end to end, from its entry point to its final output "
                    "(Main flows in section 4 reuse these strips)")
    traces = [e for wf in wfs for sd in ("current", "proposed") for e in ((wf.get(sd) or {}).get("examples") or []) if isinstance(e, dict)]
    if traces and all(e.get("synthetic") for e in traces) and inv.get("tests"):
        warn.append(f"workflows: every trace is synthetic but the inventory lists {len(inv['tests'])} test files: take values from their "
                    "fixtures (source: path:line); synthetic only where none fits")

    rows = spec.get("impact", [])
    for i, r in enumerate(rows, 1):
        w = f"impact {i} ({r.get('change')} {r.get('dim')})"
        if r.get("change") not in cids:
            err.append(f"{w}: change '{r.get('change')}' is no change id")
        if r.get("dim") not in DIMS:
            err.append(f"{w}: dim '{r.get('dim')}' unknown: use one of {list(DIMS)}")
        for k in ("now", "proposed", "saving"):
            if not str(r.get(k, "")).strip():
                err.append(f"{w}: needs {k}")
        basis(w, r, root, err, warn, check_files, facts, ["now", "proposed", "saving"])
        if r.get("dim") == "cost" and r.get("kind") == "estimate" and not r.get("source"):
            warn.append(f"{w}: cost estimate without source: cite the config it rests on (warehouse size, schedule, retention, cluster)")
    for c in cids:
        if not any(r.get("change") == c for r in rows):
            err.append(f"change {c}: no impact row: give cost, performance, maintenance, tech debt or risk now → proposed → saving")

    steps = spec.get("migration", [])
    if not steps:
        err.append("migration is empty: ordered steps, quick wins first")
    seen, slow, plain_step = set(), None, None
    high = {c.get("id") for c in changes if any(p.get("sev") == "High" and p.get("id") in c.get("fixes", []) for p in probs)}
    for k, m in enumerate(steps, 1):
        w = f"migration {k}"
        if not str(m.get("step", "")).strip() or not str(m.get("rollback", "")).strip():
            err.append(f"{w}: needs step and rollback")
        if m.get("effort") not in EFFORT:
            err.append(f"{w}: effort '{m.get('effort')}' unknown: use one of {EFFORT}")
        if m.get("risk") not in RISK:
            err.append(f"{w}: risk '{m.get('risk')}' unknown: use one of {RISK}")
        if not m.get("changes"):
            err.append(f"{w}: name the changes it ships (changes: [C…])")
        for c in m.get("changes", []):
            if c not in cids:
                err.append(f"{w}: change '{c}' is no change id")
            seen.add(c)
        for n in m.get("needs", []):
            if not (isinstance(n, int) and 1 <= n < k):
                err.append(f"{w}: needs {n}: name an earlier step number")
        quick = m.get("effort") == "S" and m.get("risk") == "Low"
        fixes_high = bool(high & set(m.get("changes", [])))
        if fixes_high and plain_step and not (m.get("needs") or m.get("wait")):
            warn.append(f"{w} fixes a High problem after step {plain_step}, which fixes none: move it first, or give needs: [k] "
                        "or wait: 'why it waits'")
        if not fixes_high and plain_step is None:
            plain_step = k
        if quick and slow and not (m.get("needs") or m.get("wait")):
            warn.append(f"{w} is a quick win (S, Low) after step {slow}: move it first, or give needs: [k] for the step it waits for")
        if not quick and not fixes_high and slow is None:
            slow = k
        if v == "keep" and m.get("effort") == "L":
            warn.append(f"{w}: effort L with verdict keep: an L step is evolve")
    for c in cids:
        if c not in seen:
            warn.append(f"change {c} is in no migration step")

    for i, a in enumerate(spec.get("assumptions", []), 1):
        if not (isinstance(a, list) and len(a) == 2):
            err.append(f"assumptions[{i}]: use [assumption, why it matters]")
    top = spec.get("top", [])
    if len(top) > 3 or any(t not in cids for t in top):
        err.append("top: up to 3 change ids")
    word_rules(spec, warn)
    for s in strings(spec):
        if "TODO" in s:
            err.append(f"TODO left in '{s[:60]}': write the text (after --use: the new pick's why and the old pick's trade-off)")
        if ABS.search(s):
            err.append(f"absolute or machine path in '{s[:60]}': paths are relative to the repo root")
        for k in secret_values(s):
            err.append(f"likely secret value for '{k}': write <redacted>, cite the file and line")
    return err, list(dict.fromkeys(warn))


def find_graph(root):
    link = root / ".knowledge-graph"
    if link.is_file():
        p = root / link.read_text(encoding="utf-8").strip()
        return p if (p / "graph").is_dir() else None
    top = git("rev-parse", "--show-toplevel")
    p = root / f"{Path(top).name if top else root.name}-knowledge-graph"
    return p if (p / "graph").is_dir() else None


def graph_commit(g):
    try:
        m = json.loads((g / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return ""
    c = next((m[k] for k in ("commit", "repo_commit", "git_commit", "head", "sha") if isinstance(m, dict) and isinstance(m.get(k), str)), "")
    return c.strip().lower()[:12] if re.fullmatch(r"[0-9a-f]{7,40}", c.strip().lower()) else ""


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def inputs(spec_path, root, check_files, warn):
    """What the review rests on (graph, inventory, facts, review) and staleness warnings; also the stamp parts."""
    head = git("rev-parse", "--short", "HEAD")
    inv = load(spec_path.parent / "inventory.json") or {}
    facts = {f.get("fact"): f.get("value") for f in (load(spec_path.parent / "facts.json") or {}).get("facts", []) if isinstance(f, dict)}
    g = find_graph(root) if check_files else None
    gc = graph_commit(g) if g else ""
    parts, used = [], []
    if g:
        used.append(f"graph {g.name}" + (f" @ {gc}" if gc else ""))
        if gc and head and not head.startswith(gc[:7]) and not gc.startswith(head[:7]):
            warn.append(f"graph built at {gc}, repo at {head}: update the graph, rerun docs-v2 inventory.py, then rebuild")
        if inv.get("graph_commit") and gc and not str(inv["graph_commit"]).startswith(gc[:7]):
            warn.append("inventory.json is older than the graph: rerun docs-v2 inventory.py")
    elif inv.get("scan"):
        used.append("file scan (no graph)")
    elif check_files:
        used.append("code only (no graph)")
    if check_files and not inv:
        warn.append("no inventory.json next to the spec: run docs-v2 inventory.py first (plan and facts)")
    if inv:
        used.append("inventory" + (" (file scan)" if inv.get("scan") else ""))
    if facts:
        used.append(f"{len(facts)} facts")
    for _, txt, _, _ in prose(load(spec_path) or {}) if check_files else []:  # "12 test files" must match the fact
        for name, val in facts.items():
            for m in re.finditer(rf"(?<![\w:.,/-])(\d[\d,]*)\s+{re.escape(str(name).split(' (')[0])}\b", txt, re.I):
                if m[1].replace(",", "") != str(val):
                    warn.append(f"text says {m[1]} {name}, facts.json says {val}")
    if head:
        parts.append(f"repo {head}" + ("+dirty" if git("status", "--porcelain", "--", ".", ":(exclude)generated-docs") else ""))
    elif check_files:
        parts.append("repo not in git")
    if gc:
        parts.append(f"graph {gc}")
    return facts, used, parts, head, inv


def render(spec, R, used, stamp, head, accuracy):
    """Returns (page, terminal lines, layout warns)."""
    esc, diagram, strip, plain = R["esc"], R["diagram"], R["strip"], R["why"]
    ids, late = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), []
    probs = sorted(spec.get("problems", []), key=lambda p: (SEVS.index(p["sev"]), int(p["id"][1:])))
    pr = spec["proposal"]
    changes = {c["id"]: c for c in pr["changes"]}
    by_p = {}
    for c in pr["changes"]:
        for p in c["fixes"]:
            by_p.setdefault(p, []).append(c["id"])
    code = lambda c: f"<code>{esc(c)}</code>"
    short = lambda c: (f'<code title="{html.escape(str(c))}">'  # phone: basename:line, breaks after _ and .
                       + re.sub(r"([_.])", r"\1<wbr>", html.escape(str(c).rsplit("/", 1)[-1])) + "</code>")
    clink = lambda c: f'<a href="#{c}">{c}</a>'
    plink = lambda p: f'<a href="#{p}">{p}</a>'

    def draw(dg, where):
        did = next(ids)
        try:
            out, w = diagram(dict({"numbered": False}, **dg, id=did))
        except ValueError as e:
            sys.exit(f"ERROR {where} diagram: {e}")
        late.extend(w)
        if "&hellip;<wbr>" in out:
            late.append(f"diagram {did} ({where}): a box text is cut with … (full text only on hover): shorten label or sub")
        cap = (f'<p class="key">Key: {esc(dg["key"])}</p>' if dg.get("key") else "") + (
            f'<p class="cap">Notice: {esc(dg["notice"])}</p>' if dg.get("notice") else "")
        why = f'<p class="cap">Diagram drawn as text: {plain}.</p>' if plain else ""
        return f'<h3 id="d-{did}">Diagram {did} &middot; {esc(dg["title"])}</h3>{out}{cap}{why}'

    def based(r, cell=False):
        src = short if cell else code
        if r["kind"] == "measured":
            return kl(r) + " &middot; " + (src(r["source"]) if r.get("source") else f'fact {esc(r["fact"])}')
        return "estimate &middot; " + esc(r["assumption"]) + (f" ({src(r['source'])})" if r.get("source") else "")

    # 1 Summary
    rows = spec.get("impact", [])
    kl = lambda r: kind_label(r).replace("·", "&middot;")
    head_row = lambda c: next((r for r in rows if r["change"] == c and r.get("headline")), next(r for r in rows if r["change"] == c))
    top = spec.get("top") or list(changes)[:3]
    tops = [(c, head_row(c)) for c in top]
    count = {s: sum(1 for p in probs if p["sev"] == s) for s in SEVS}
    steps = spec.get("migration", [])
    quick = [m for m in steps if m["effort"] == "S" and m["risk"] == "Low"]
    moves = pr.get("moves", [])
    mc = {d: sum(1 for m in moves if m["decision"] == d) for d in DECISIONS}
    s1 = (f'<p><span class="verdict {spec["verdict"]}">{esc(spec["verdict"])}</span></p><p class="lead">{esc(spec["summary"])}</p>'
          "<h3>Top changes</h3><ol>" + "".join(
              f'<li>{clink(c)} {esc(changes[c]["title"])} &mdash; {DIMS[r["dim"]].lower()}: {esc(r["saving"])} ({kl(r)})</li>' for c, r in tops)
          + "</ol><ul>" + f'<li><b>Problems:</b> High {count["High"]} &middot; Medium {count["Medium"]} &middot; Low {count["Low"]}</li>'
          + (f'<li><b>Components:</b> {mc["move"]} move &middot; {mc["keep"]} keep &middot; {mc["later"]} later</li>' if moves else "")
          + f'<li><b>Plan:</b> {len(changes)} changes, {len(steps)} steps, {len(quick)} quick wins</li>'
          + (f'<li><b>Based on:</b> {esc(" · ".join(used))}</li>' if used else "") + "</ul>")
    # 2 Current architecture
    cur = spec["current"]
    lab = lambda r: f'<li><b>{esc(r[0])}:</b> {esc(r[1])}' + (f' {code(r[2])}' if len(r) > 2 else "") + "</li>"
    s2 = (f'<p class="lead">{esc(cur.get("lead", ""))}</p>' if cur.get("lead") else "")
    s2 += f'<p class="key">Current design in full: {code(spec["current_doc"])}</p>' if spec.get("current_doc") else ""
    s2 += draw(cur["l0"], "current l0") + draw(cur["components"], "current components")
    if cur.get("runtime"):
        s2 += "<h3>Runtime and deploy</h3><ul>" + "".join(lab(r) for r in cur["runtime"]) + "</ul>"
    if cur.get("hotspots"):
        s2 += "<h3>Where time and cost go</h3><ul>" + "".join(
            f'<li><b>{esc(h["what"])}:</b> {esc(h["value"])} <span class="src">{based(h)}</span></li>' for h in cur["hotspots"]) + "</ul>"
    # 3 Problems
    s3 = ""
    for p in probs:
        fix = (f'<li><b>Fixed by:</b> {", ".join(clink(c) for c in by_p[p["id"]])}</li>' if p["id"] in by_p else
               f'<li><b>Accepted:</b> {esc(p["accept"])}</li>' if p.get("accept") else "<li><b>Fixed by:</b> no change proposed</li>")
        s3 += (f'<div class="pb" id="{p["id"]}"><div class="hd">{p["id"]} &middot; <span class="sev {p["sev"]}">{p["sev"].upper()}</span> &middot; '
               f'{AREAS[p["area"]]}</div><h3>{esc(p["title"])}</h3><ul><li>{esc(p["detail"])}</li>'
               + (f'<li><b>Costs:</b> {esc(p["cost"])}</li>' if p.get("cost") else "")
               + f'<li><b>Evidence:</b> {", ".join(code(c) for c in p["evidence"])}</li>{fix}</ul></div>')
    # 4 Proposed architecture: keep / move / later, then the target in Technical-doc shape, then the changes
    s4 = f'<p class="lead">{esc(pr.get("lead", ""))}</p>' if pr.get("lead") else ""
    if moves:
        th = ["Component", "Now", "Decision", "To", "Why"]
        inst = lambda m: (f'<br><span class="src">Until: {esc(m["until"])}</span>' if m.get("until") else "") + ((f'<br><span class="src">Alternatives: ' + " &middot; ".join(f'{esc(a["name"])} &mdash; {esc(a["tradeoff"])}' for a in m["alternatives"])
                          + "</span>") if m.get("alternatives") else "")
        body = "".join(f'<tr id="M{k}">' + "".join(f'<td data-h="{h}">{c}</td>' for h, c in zip(th, [
            f'<span class="src">M{k}</span> <b>{esc(m["component"])}</b>', esc(m["now"]), f'<span class="dec {m["decision"]}">{m["decision"]}</span>' + (' <span class="src">current, fits</span>' if m.get("current") else "")
            + (f' {clink(m["change"])}' if m.get("change") else ""), (esc(m["to"]) if m.get("to") else "&ndash;"), esc(m["why"]) + inst(m)])) + "</tr>"
            for k, m in enumerate(moves, 1))
        s4 += "<h3>Keep, move, later</h3>"
        if any(m.get("alternatives") for m in moves):
            s4 += '<p class="key">Alternatives = tools to ask for: "use &lt;tool&gt; instead for M&lt;n&gt;" rebuilds the target around it.</p>'
        s4 += (
               f'<div class="scroll"><table class="tt moves"><tr>{"".join(f"<th>{h}</th>" for h in th)}</tr>{body}</table></div>')
    s4 += draw(pr["diagram"], "proposal")
    if pr.get("components"):
        s4 += R["blocks"]([{"type": "components", "rows": pr["components"]}], 4, 0, "Architecture")
    if pr.get("stays"):
        s4 += f'<p class="key"><b>Stays:</b> {" &middot; ".join(esc(x) for x in pr["stays"])}</p>'
    for k, wf in enumerate(spec.get("workflows", []), 1):
        b = dict(wf["proposed"], examples=[])
        try:
            st = strip(b, 4, k, 0)
        except ValueError as e:
            sys.exit(f"ERROR workflow {k} proposed: {e}")
        s4 += f'<h3 id="mf-{k}">Main flow 4.{k} &middot; {esc(wf["title"])}</h3>{st}'
    tech = pr.get("technical") or {}
    for name in TECH:
        v = tech.get(name)
        if v is None:
            continue
        if isinstance(v, str):
            s4 += f'<h3>{name}</h3><p>{esc(v)}</p>'
            continue
        out = ""
        for blk in v:
            if blk["type"] in ("flow", "er"):
                blk = dict(blk, id=next(ids))
            try:
                out += R["blocks"]([blk], 4, 0, name)
            except ValueError as e:
                sys.exit(f"ERROR proposal technical {name}: {e}")
        s4 += f"<h3>{name}</h3>{out}"
    s4 += "<h3>Changes</h3>"
    if any(c.get("tool") for c in pr["changes"]):
        s4 += '<p class="key">Each move: one pick and its alternatives; ask "use &lt;alternative&gt; instead" to rebuild the target around it.</p>'
    for c in pr["changes"]:
        t = c.get("tool")
        pick = (f'<li><b>Pick:</b> {esc(t["name"])} &mdash; {esc(t["why"])}</li><li><b>Alternatives:</b> '
                + " &middot; ".join(f'{esc(x["name"])} &mdash; {esc(x["tradeoff"])}' for x in c.get("alternatives", [])) + "</li>") if t else ""
        s4 += (f'<div class="pb" id="{c["id"]}"><div class="hd">{c["id"]} &middot; fixes {", ".join(plink(p) for p in c["fixes"])}</div>'
               f'<ul><li><b>{esc(c["title"])}:</b> {esc(c["what"])}</li><li><b>Why:</b> {esc(c["why"])}</li>{pick}'
               + (f'<li><b>Free in:</b> {esc(c["free_in"])} provides this fix built in</li>' if c.get("free_in") else "")
               + (f'<li><b>Also needs:</b> {"; ".join(esc(x) for x in c["prereq"])}</li>' if c.get("prereq") else "")
               + (f'<li><b>Goes with:</b> {", ".join(clink(x) for x in c["goes_with"])}</li>' if c.get("goes_with") else "")
               + (f'<li><b>Signal:</b> {", ".join(code(x) for x in c["signal"])}</li>' if c.get("signal") else "") + "</ul></div>")
    s4 += "<h3>Options considered</h3><div class=\"opts\">" + "".join(
        f'<div class="opt{" chosen" if o.get("chosen") else ""}"><b>{esc(o["name"])}</b>{" &middot; chosen" if o.get("chosen") else ""}'
        f'<ul><li>{esc(o["what"])}</li><li><b>Gains:</b> {esc(o["gains"])}</li><li><b>Costs:</b> {esc(o["costs"])}</li>'
        + (f'<li><b>Size:</b> {esc(o["size"])}</li>' if o.get("size") else "")
        + (f'<li><b>Why not smaller:</b> {esc(o["why_not"])}</li>' if o.get("why_not") else "") + '</ul></div>'
        for o in pr["options"]) + "</div>"
    # 5 Workflows: the current strip and trace; the proposed trace (its strip is Main flow 4.k)
    s5 = ""
    for k, wf in enumerate(spec.get("workflows", []), 1):
        try:
            a = strip(wf["current"], 5, k, 0)
            b = strip(wf["proposed"], 5, k, len(wf["current"].get("examples") or []), "p")
        except ValueError as e:
            sys.exit(f"ERROR workflow {k}: {e}")
        b = re.sub(r'^<ol class="ipo">.*?</ol>(<p class="src">Sources:.*?</p>)?', "", b, flags=re.S)
        s5 += (f'<h3>{esc(wf["title"])}</h3>' + (f'<p class="key">Changed by {", ".join(clink(c) for c in wf["changes"])}'
                                                + (f' &middot; needs {", ".join(clink(c) for c in wf["needs"])}' if wf.get("needs") else "") + "</p>" if wf.get("changes") else "")
               + f'<p class="wf">CURRENT</p>{a}<p class="wf">PROPOSED &middot; steps in <a href="#mf-{k}">Main flow 4.{k}</a></p>{b}')
    # 6 Impact: one table, grouped by change
    th = ["Change", "Dimension", "Now", "Proposed", "Saving", "Basis"]
    body, last = "", None
    for r in sorted(rows, key=lambda r: list(changes).index(r["change"])):
        cells = [clink(r["change"]) + " " + esc(changes[r["change"]]["title"]) if r["change"] != last else "", DIMS[r["dim"]],
                 esc(r["now"], True), esc(r["proposed"], True), esc(r["saving"], True), based(r, True)]
        last = r["change"]
        body += "<tr>" + "".join(f'<td data-h="{h}">{c}</td>' for h, c in zip(th, cells)) + "</tr>"
    s6 = ('<p class="key">measured = read from code, config, graph or tests (cited) &middot; effect by design = the now value is measured, '
          'the change follows from the design &middot; estimate = the assumption it rests on</p>'
          f'<div class="scroll"><table class="tt"><tr>{"".join(f"<th>{h}</th>" for h in th)}</tr>{body}</table></div>')
    # 7 Migration
    s7 = '<ol class="mig">' + "".join(
        f'<li><b>{esc(m["step"])}</b> &middot; {", ".join(clink(c) for c in m["changes"])} &middot; effort {m["effort"]} &middot; risk {m["risk"]}'
        + (' <span class="chip qw">quick win</span>' if m in quick else "")
        + (f' &middot; after step {", ".join(map(str, m["needs"]))}' if m.get("needs") else "")
        + (f'<br><span class="src">Waits: {esc(m["wait"])}</span>' if m.get("wait") else "")
        + f'<br><span class="src">Rollback: {esc(m["rollback"])}</span></li>' for m in steps) + "</ol>"
    # 8 Open questions and assumptions
    s8 = ("<h3>Questions</h3><ul>" + "".join(f"<li>{esc(q)}</li>" for q in spec["questions"]) + "</ul>" if spec.get("questions") else "")
    s8 += ("<h3>Assumptions</h3><ul>" + "".join(f"<li><b>{esc(a)}</b> &mdash; {esc(b)}</li>" for a, b in spec["assumptions"]) + "</ul>"
           if spec.get("assumptions") else "")
    secs = zip(SECTIONS, [s1, s2, s3 or "<p>No problems found.</p>", s4, s5 or "<p>No workflows given.</p>", s6, s7, s8 or "<p>None.</p>"])
    toc = "".join(f'<a href="#s{i}">{i + 1} {t}</a>' for i, t in enumerate(SECTIONS))
    secs_html = "".join(f'<section><h2 id="s{i}">{i + 1} {t}</h2>{h}</section>' for i, (t, h) in enumerate(secs))
    stamp = [spec.get("date") or datetime.now().strftime("%Y-%m-%d %H:%M")] + stamp + ([f"review {spec['review']}"] if spec.get("review") else [])
    title = esc(spec["title"])
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-architecture {VERSION}">'
            + (f'<meta name="repo-commit" content="{html.escape(head)}">' if head else "")
            + f'<title>{title}</title><style>{R["css"]}{CSS}</style></head><body><main><div class="eyebrow">architecture review</div><h1>{title}</h1>'
            f'<p class="sub1">{" &middot; ".join(esc(s) for s in stamp)}</p>'
            + (f'<p class="sub1">{esc(spec["subtitle"])}</p>' if spec.get("subtitle") else "")
            + f'<nav class="toc">{toc}</nav>{secs_html}</main></body></html>')
    term = [f"Verdict: {spec['verdict']} — {spec['summary']}"] + [
        f"- {c} {changes[c]['title']} — {DIMS[r['dim']].lower()}: {r['saving']} ({kind_label(r)})" for c, r in tops]
    term.append(f"Problems: High {count['High']}, Medium {count['Medium']}, Low {count['Low']} · "
                + (f"components: {mc['move']} move, {mc['keep']} keep, {mc['later']} later · " if moves else "")
                + f"{len(steps)} migration steps, {len(quick)} quick wins")
    term.append(accuracy)
    return page, term, late


def changed(spec_path, out_path):
    """Sections citing files changed since the page's repo-commit (git diff + untracked)."""
    page = Path(out_path).read_text(encoding="utf-8") if Path(out_path).is_file() else ""
    m = re.search(r'<meta name="repo-commit" content="([0-9a-f+dirty]+)"', page)
    if not m:
        sys.exit(f"ERROR {out_path} has no repo-commit stamp: rebuild it in full")
    since = m[1].split("+")[0]
    diff = git("diff", "--name-only", since, "--", ".", ":(exclude)generated-docs")
    if diff is None:
        sys.exit(f"ERROR git diff {since} failed: the commit is gone; rebuild in full")
    files = set(diff.splitlines()) | set((git("ls-files", "--others", "--exclude-standard") or "").splitlines())
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    cur, pr = spec.get("current") or {}, spec.get("proposal") or {}
    per = {"2 Current architecture": strings(cur), "3 Problems": strings(spec.get("problems", [])), "4 Proposed architecture": strings(pr),
           "5 Workflows": strings(spec.get("workflows", [])), "6 Impact": strings(spec.get("impact", []))}
    hit = 0
    for sec, texts in per.items():
        cited = {CITE.match(t).group(1) for t in texts if CITE.match(t)}
        for f in sorted(cited & files):
            print(f"{sec}: {f} changed since {since}")
            hit += 1
    print(f"changed since {since}: {len(files)} files, {hit} cited" + ("" if hit else ": refresh the stamp only (rebuild)"))


def kind_label(r):
    """'measured' only when the saving itself is a counted number; a measured now with a design consequence says so."""
    if r.get("kind") != "measured":
        return str(r.get("kind"))
    return "measured" if NUMBER.search(str(r.get("saving", ""))) else "now measured · effect by design"


def tag(x):
    return hashlib.sha1(json.dumps(x, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:6]


def items(spec):
    """The accuracy and feasibility pass (step 13) as one line per thing to open and confirm. Each ends in a hash of what
    it checks: an edited or reordered problem, change, row or step loses its tick."""
    pr, out = spec.get("proposal") or {}, []
    picks = {c.get("id"): c["tool"].get("name") for c in pr.get("changes", []) if isinstance(c.get("tool"), dict)}
    targets = sorted({str(picks.get(m.get("change")) or m.get("to")) for m in pr.get("moves", [])  # one per target tool
                      if m.get("decision") in ("move", "later") and m.get("to")})
    for p in spec.get("problems", []):
        out += [f"{p.get('id')} {c}: the line shows what the detail says (cite where it is done or raised, not a caller) #{tag(p)}"
                for c in p.get("evidence", [])]
    for k, m in enumerate(pr.get("moves", []), 1):
        out.append(f"M{k} {m.get('component')}: {m.get('decision')} fits the evidence; alternatives current, each trade-off true for this repo"
                   + (f"; until is checkable and the blocker checked in {m.get('to')}'s docs" if m.get("decision") == "later" else "")
                   + f" #{tag([m, picks.get(m.get('change'))])}")
    for c in pr.get("changes", []):
        i = c.get("id")
        n0 = len(out)
        out.append(f"{i}: works at the pinned versions; every consumer of what it changes is handled (routes, origins, ports, roles, schedules, volumes)")
        out.append(f"{i}: removes its problems in full (a leaked secret is rotated, not moved); what it leaves out is said")
        out += [f"{i} signal {x}: the code shows the pattern" for x in c.get("signal", [])]
        out += [f"{i} needs: {x}" for x in c.get("prereq", [])]
        if isinstance(c.get("tool"), dict):
            out.append(f"{i} pick {c['tool'].get('name')}: current name and feature checked in its official docs; alternatives current")
        if c.get("free_in"):
            out.append(f"{i} free in {c['free_in']}: its docs show the feature (name the page)")
        out[n0:] = [f"{x} #{tag(c)}" for x in out[n0:]]
    plain = [c.get("id") for c in pr.get("changes", []) if not c.get("free_in") and not c.get("tool")]
    out += [f"{t}: fixes {', '.join(plain)} checked against its docs: not built in (name the page), else set free_in #{tag(plain)}"
            for t in targets if plain]
    for r in spec.get("impact", []):
        w = f"impact {r.get('change')} {r.get('dim')}"
        out.append((f"{w}: number read from {r.get('source') or 'fact ' + str(r.get('fact'))}" if r.get("kind") == "measured" else
                    f"{w}: assumption plausible; a platform behaviour it rests on is in questions or assumptions") + f" #{tag([r, picks.get(r.get('change'))])}")
    for o in pr.get("options", []):
        if o.get("size"):
            out.append(f"option {o.get('name')}: size counted by a script (lines, tasks, tests), target estimate stated #{tag([o, sorted(picks.values())])}")
    for k, w in enumerate(spec.get("workflows", []), 1):
        out.append(f"workflow {k} {w.get('title')}: a real flow from an entry point to an output; trace values from tests, fixtures or docs "
                   f"#{tag([w, [picks.get(c) for c in w.get('changes', [])]])}")
    for k, m in enumerate(spec.get("migration", []), 1):
        out.append(f"migration {k}: rollback undoes it, stateful stores too; nothing it needs comes later #{tag([m, [picks.get(c) for c in m.get('changes', [])]])}")
    out.append("diagrams: every box and label matches the code or a change (no box marked changed that does not change)")
    out.append("terms: technical terms exact (symmetric vs asymmetric keys, automatic vs manual switches); no dates or schedules without a source")
    return out


def ticks(spec_path, spec):
    """(terminal line, warn or None) from the checklist next to the spec."""
    f = spec_path.parent / CHECKLIST
    if not f.is_file():
        return f"Accuracy: not reviewed (python <skill>/references/templates/build.py --checklist {spec_path.as_posix()}, tick each item)", None
    done = {ln[6:].strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.lower().startswith("- [x] ")}
    want = items(spec)
    left = [x for x in want if x not in done]
    if left:
        return f"Accuracy: {len(want) - len(left)} of {len(want)} checked", f"accuracy: {len(left)} checklist items not ticked (first: '{left[0][:70]}')"
    return f"Accuracy: {len(want)} of {len(want)} checked", None


def checklist(spec_path):
    spec_path = Path(spec_path)
    f = spec_path.parent / CHECKLIST
    old = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
    done = {ln[6:].strip() for ln in old if ln.lower().startswith("- [x] ")}
    want = items(json.loads(spec_path.read_text(encoding="utf-8")))
    f.write_text("# Accuracy and feasibility — open each, fix the spec, then tick: - [x]\n"
                 + "".join(f"- [{'x' if x in done else ' '}] {x}\n" for x in want), encoding="utf-8")
    print(f"{f.as_posix()}: {len(want)} items, {sum(x in done for x in want)} ticked")


def use(spec_path, cid, name):
    """Make an alternative the pick of change cid (or of moves row M-n); the old pick becomes an alternative. Prints every text
    naming the old pick and every text tied to the change: rewrite those (target, workflows, impact, migration, options), then rebuild."""
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    pr = spec.get("proposal") or {}
    chg = {x.get("id"): x for x in pr.get("changes", [])}
    if re.fullmatch(r"M\d+", cid):
        moves = pr.get("moves", [])
        c = moves[int(cid[1:]) - 1] if 1 <= int(cid[1:]) <= len(moves) else None
        x = chg.get((c or {}).get("change"), {})
        if c and isinstance(x.get("tool"), dict) and any(str(a.get("name", "")).lower() == name.lower() for a in x.get("alternatives", [])):
            return use(spec_path, c["change"], name)  # a move row: its change holds the pick
        if not c or not c.get("alternatives"):
            sys.exit(f"ERROR {cid}: no moves row with alternatives" + (f" (its change {c['change']} holds them)" if c and c.get("change") else ""))
    else:
        c = chg.get(cid)
        if not c or not isinstance(c.get("tool"), dict):
            sys.exit(f"ERROR {cid}: no change with a tool")
    alts = c.get("alternatives", [])
    alt = next((x for x in alts if str(x.get("name", "")).lower() == name.lower()), None)
    if not alt:
        sys.exit(f"ERROR {cid}: '{name}' is not one of its alternatives ({', '.join(x.get('name', '') for x in alts)}). Unlisted tool: "
                 "check its fit in its official docs, add it to alternatives (replace the weakest), rerun --use; no fit: say why in one line")
    tie = None
    if cid.startswith("M"):  # the row's tool: `to` of a move or later row, the current tool (`now`) of a keep row
        old = c["to"] if c.get("decision") in ("move", "later") and c.get("to") else re.split(r",|;| \(", c["now"])[0].strip()
        alts[alts.index(alt)] = {"name": old, "tradeoff": f"TODO: trade-off of {old} vs {alt['name']}"}
        was = c.pop("change", None)
        c.pop("until", None)
        c.update(decision="move", to=alt["name"], why=f"TODO: why {alt['name']} fits this repo (was: {alt['tradeoff']})")
        print(f"{cid}: add a change (tool {alt['name']}, signal, pattern, impact, migration step) and set this row's change to its id"
              + (f"; {was} was this row's change: keep it only if it still applies" if was else ""))
        tie = was
    else:
        old = c["tool"]["name"]
        alts[alts.index(alt)] = {"name": old, "tradeoff": f"TODO: trade-off of {old} vs {alt['name']}"}
        c["tool"] = {"name": alt["name"], "why": f"TODO: why {alt['name']} fits this repo (was: {alt['tradeoff']})"}
        tie = cid
        for k, m in enumerate(pr.get("moves", [])):
            if m.get("change") == cid and str(m.get("to", "")).lower() == old.lower():
                m["to"] = alt["name"]
                print(f"set proposal.moves[{k}].to = {alt['name']}")
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def walk(x, at):
        if isinstance(x, dict):
            for k, v in x.items():
                yield from walk(v, f"{at}.{k}" if at else k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                yield from walk(v, f"{at}[{i}]")
        elif isinstance(x, str) and names(x, old) and "TODO" not in x and not at.endswith(".name"):
            yield at, x
    hits = list(walk(spec, ""))
    for at, x in hits:
        print(f"rewrite {at}: {x[:90]}")
    named = {x for _, x in hits}
    rest = [(w, x) for w, x in (tied(spec, tie) if tie else []) if x not in named and "TODO" not in x]
    for w, x in rest:
        print(f"check {w}: {x[:90]}")
    print(f"{cid}: pick {alt['name']} (was {old}); {len(hits)} texts name {old}, {len(rest)} more depend on the pick: rewrite them for "
          f"{alt['name']} (its current features from official docs) and the TODOs, then rebuild and tick the checklist items that lost their tick")


def main(spec_path, out_path):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; spec text holds · and →
    sys.stderr.reconfigure(encoding="utf-8")
    R = docs_v2()
    plain = R["why"]
    if plain:
        print(f"note: {plain}: built-in style, diagrams and steps drawn as text, layout not checked")
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out, root = Path(out_path), Path.cwd()
    if not out.parent.is_dir():
        sys.exit(f"ERROR output folder {out.parent.as_posix()} does not exist: create it (mkdir -p {out.parent.as_posix()}), then rerun")
    check_files = has_files(root, out)
    if not check_files:
        print(f"note: no repo files under {root.name or root}: path, line, fact and graph checks skipped")
    warn = []
    facts, used, stamp, head, inv = inputs(spec_path, root, check_files, warn)
    if check_files and not head:
        print("note: repo not in git: no commit stamp, no graph staleness check, --changed unavailable (say so in the reply)")
    has_review = check_files and any(p.is_file() for p in (root / "reviews").glob("*.html")) if (root / "reviews").is_dir() else False
    err, w2 = check(spec, root, check_files, facts, has_review, inv)
    accuracy, tw = ticks(spec_path, spec)
    warn = list(dict.fromkeys(warn + w2 + ([tw] if tw else [])))
    for w in warn:
        print("WARN", w)
    if err:
        sys.exit("\n".join(f"ERROR {e}" for e in err))
    page, term, late = render(spec, R, used, stamp, head, accuracy)
    for w in dict.fromkeys(late):
        print("WARN", w)
    out.write_bytes(page.encode("ascii", "xmlcharrefreplace"))
    if check_files:
        (out.parent / MARKER).touch()
    print("\n".join(term + [f"Report: {out.as_posix()}"] + ([f"Layout not checked: {plain}"] if plain else [])))
    print(f"built {out.as_posix()}: {len(spec.get('problems', []))} problems, {len(spec['proposal']['changes'])} changes, "
          f"{len(warn) + len(set(late))} WARN (architecture {VERSION})")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--changed":
        changed(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "--checklist":
        checklist(sys.argv[2])
    elif len(sys.argv) == 5 and sys.argv[1] == "--use":
        sys.stdout.reconfigure(encoding="utf-8")
        use(*sys.argv[2:])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
