"""Build one requirements brief (one self-contained HTML page, inline SVG) from a JSON spec.
Top-level sections are fixed (same 12, same order, every run); subsections and their blocks are chosen per input.

Usage: python build.py <spec.json> <out.html>     (run from the project root; `from` paths in profile blocks resolve there)
Spec: ../spec.md. ERROR lines stop the build; WARN lines are fixed or explained in the reply.
"""
import html
import json
import re
import sys
from pathlib import Path

VERSION = "1.1.0"
INPUTS_DIR = "generated-docs/_spec/inputs"  # where step 1 keeps the raw inputs; the build scans it for ids again
SECTIONS = ["At a glance", "Context", "Requirements", "Sources and data", "Identity and linking", "Flows",
            "Use cases and data needs", "Data findings", "Technology options", "What needs to be done",
            "Gaps, assumptions and risks", "Glossary"]
CORE = {"At a glance", "Requirements", "Technology options", "What needs to be done"}  # a one-line section here is a WARN
BLOCKS = {"text", "bullets", "table", "facts", "flow", "links", "timeline", "requirements", "sources", "needs", "profile",
          "options", "work", "terms"}
STATUS = ["clear", "gap", "conflict"]
WORK = ["build", "configure", "decide", "clarify"]
NODE = ["source", "step", "store", "consumer"]
WORDS, MAX_STEPS, LABEL = 40, 7, 12  # word cap per text · timeline steps · edge label characters
FILLER = re.compile(r"\b(robust|seamless(?:ly)?|leverag(?:e|es|ing)|cutting[- ]edge|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|"
                    r"world[- ]class|game[- ]chang\w*|synerg\w*|holistic|next[- ]generation|simply|basically|very|really|"
                    r"comprehensive|powerful|in order to|it is important to note|note that)\b", re.I)
CHAT = re.compile(r"\b(you|your|the user|claude|as discussed|as agreed|as requested|as asked|per (?:your )?request|(?:our|this) (?:conversation|chat)|"
                  r"the requester|requester|asked (?:us|me)|(?:was|were) asked|confirm with|(?:we|i) (?:could not|couldn't|did not|didn't) (?:check|verify|confirm)|"
                  r"(?:was|were) skipped|not (?:asked|provided by))\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*[a-z]{2,}", re.I)
# phones: international (+49 …, 0049 …) with 7+ digits; local (030 5550100) with 9+ digits. Not after a digit group (IBAN), not HHMM-HHMM.
PHONE_INT = re.compile(r"(?<!\d\s)(?<![\w-])(?:\+|00)\d{1,3}[\s./-]?(?:\(?\d{1,5}\)?[\s./-]?){2,4}\d{2,}\b")
PHONE_LOCAL = re.compile(r"(?<!\d\s)(?<![\w:.-])0\d{2,4}[\s/-]\d{3,}(?:[\s-]\d{2,})?\b")
GENERIC_TITLES = {"overview", "details", "general", "per need", "per source", "terms", "work items", "profile", "sources to consumers", "entities and keys",
                  "summary", "introduction", "misc", "other", "items", "list", "how the given platform fits", "how the platform fits",
                  "conflicts and how we resolve them", "conflicts", "linking rules", "what the sample shows", "findings", "requirement vs data",
                  "gaps", "assumptions", "risks", "open points", "work", "sources", "needs", "options", "glossary", "context", "flows", "flow",
                  "requirements", "data findings", "use cases"}  # wrapper titles that fit any brief: name the subsection from the input
ALLOWED_TITLES = {"Gaps, assumptions and risks": {"gaps", "assumptions", "risks", "open points"}}  # the one section where these groups are the content
STACK_RX = re.compile(r"\b(\d+) requirements\b", re.I)
ABS = re.compile(r"(?<![\w])[A-Za-z]:[\\/]|(?<![\w.~])/(?:Users|home|root|opt|mnt|var|srv|etc|tmp)/|(?<![\w])~/")
KEYS = r"[\w.-]*(?:passw(?:or)?d|pwd|secret|token|api_?key|access_?key|private_?key)[\w.-]*"
SECRET_VALUE = [
    re.compile(rf"""(?i)\b({KEYS})["']?\s*(?::\s*\w+\s*)?[:=]\s*(["'])(?!<redacted>|\$\{{|\{{\{{)[^"'\n]+\2"""),
    re.compile(rf"""(?im)^[\s`>-]*(?:export\s+)?({KEYS})\s*[:=][ \t]*(?!<redacted>|\$|\{{|\*)[^\s"'#,;.(){{}}\[\]`]+(?=[\s"'#,;`]|$)"""),
    re.compile(r"(?i)\b\w+://[^\s:/@]+:(?!<redacted>|\$)([^\s@/]+)@"),
]
CSS = """:root{--ground:#F6F6F3;--card:#FFF;--line:#D9DBDF;--ink:#17191D;--muted:#5B6068;--soft:#EEEFEC;--teal:#DDF0EE;--teal-ink:#1C5C57;
--amber:#FCEBC8;--amber-ink:#8A5A00;--green:#1E6B43;--blue:#1F5FA8;--lav:#E7E2F5;--lav-ink:#6B4FA8;--red:#A12D2D}
@media (prefers-color-scheme:dark){:root{--ground:#15171A;--card:#1E2125;--line:#3A3E44;--ink:#E8E9EB;--muted:#A3A8B0;--soft:#2A2D32;--teal:#1F3A38;
--teal-ink:#8FD3CC;--amber:#4A3A12;--amber-ink:#F0C060;--green:#6FCF97;--blue:#8AB4F8;--lav:#3A3150;--lav-ink:#C9B8F0;--red:#F08080}}
*{box-sizing:border-box} body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.55 "IBM Plex Sans","Segoe UI",Arial,sans-serif}
main{max-width:1104px;margin:0 auto;padding:32px 16px 56px;overflow-wrap:break-word}
h1{font-size:28px;font-weight:600;margin:4px 0 8px} h2{font-size:20px;font-weight:600;margin:0 0 10px} h3{font-size:16px;font-weight:600;margin:16px 0 6px}
h4{font-size:14px;font-weight:600;margin:12px 0 4px} section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:20px 24px;margin:18px 0}
ul{margin:6px 0;padding-left:22px} li{margin:3px 0} p{margin:6px 0}
code,.m,th,.eyebrow,.chip,.key,.stamp,.src,.kind{font-family:"IBM Plex Mono",Consolas,monospace}
code{font-size:13px;background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px}
.eyebrow{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)} .stamp,.src{font-size:12px;color:var(--muted)}
.toc{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin:8px 0 0} .toc a{color:var(--blue)} a{color:inherit}
.lead{margin:4px 0 8px} .line{color:var(--muted)}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:14px} th,td{text-align:left;vertical-align:top;padding:7px 10px;border:1px solid var(--line)}
th{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);background:var(--soft)} td.m{font-size:12.5px}
.facts{display:grid;grid-template-columns:max-content 1fr;gap:5px 18px;margin:8px 0} .facts dt{font:12px/1.6 "IBM Plex Mono",Consolas,monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.facts dd{margin:0}
.chip{display:inline-block;font-size:10.5px;font-weight:600;letter-spacing:.04em;padding:0 6px;border-radius:4px;border:1px solid;white-space:nowrap;vertical-align:1px}
.chip.clear{color:var(--green);border-color:var(--green)} .chip.gap{color:var(--amber-ink);border-color:var(--amber-ink);background:var(--amber)}
.chip.conflict{color:var(--red);border-color:var(--red)} .chip.given{color:var(--lav-ink);border-color:var(--lav-ink);background:var(--lav)}
.chip.none{color:var(--red);border-color:var(--red)} .chip.sens{color:var(--amber-ink);border-color:var(--amber-ink)} .chip.id{color:var(--blue);border-color:var(--blue)}
.kind{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.meta{font-size:13px;color:var(--muted);margin:0 0 4px} .meta b{color:var(--ink);font-weight:600}
.dg{overflow-x:auto;margin:10px 0 0} .dg svg{display:block;max-width:100%;height:auto} .key{font-size:12px;color:var(--muted);margin:4px 0 0}
.dg text{fill:var(--ink);font:12px "IBM Plex Sans","Segoe UI",Arial,sans-serif} .dg .t{font-weight:600} .dg .s,.dg .id,.dg .lbl,.dg .at,.dg .lanet{fill:var(--muted);font:11px "IBM Plex Mono",Consolas,monospace}
.dg .tag{fill:var(--muted);font:9.5px "IBM Plex Mono",Consolas,monospace;letter-spacing:.08em} .dg .out{fill:var(--teal-ink);font:11px "IBM Plex Mono",Consolas,monospace}
.dg .box{fill:var(--card);stroke:var(--ink)} .dg .source{fill:var(--soft)} .dg .store{fill:var(--teal);stroke:var(--teal-ink)} .dg .consumer{fill:var(--lav);stroke:var(--lav-ink)}
.dg .ent{fill:var(--card);stroke:var(--ink)} .dg .enth{fill:var(--soft);stroke:var(--ink)} .dg .lane{fill:var(--soft)} .dg .bg{fill:var(--card)}
.dg line,.dg polyline{stroke:var(--ink);fill:none;stroke-width:1.2} .dg .dashed{stroke-dasharray:5 4} .dg .ar{fill:var(--ink)}
.terms{columns:2;column-gap:32px;font-size:14px;margin:8px 0} .terms div{break-inside:avoid;margin:3px 0} .terms b{font-weight:600}
.scroll{overflow-x:auto}
@media (max-width:720px){section{padding:14px 12px} .terms{columns:1} .facts{grid-template-columns:1fr;gap:2px} .facts dd{margin:0 0 6px} .dg svg{min-width:640px}
table.tt,.tt tbody,.tt tr,.tt td{display:block;width:100%} .tt tr:first-child{display:none} .tt tr{margin:0 0 8px;border:1px solid var(--line);border-radius:4px}
.tt td{border:0;border-bottom:1px solid var(--line);padding:5px 8px} .tt td:empty{display:none}
.tt td::before{content:attr(data-h);display:block;font:600 10px/1.6 "IBM Plex Mono",Consolas,monospace;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}}
@media print{body{background:#fff;font-size:12.5px} main{max-width:none;padding:0} section{border:0;padding:0 0 8px;break-inside:auto} .toc{display:none}
.dg,table,h3,h4,.facts{break-inside:avoid} h2{break-after:avoid} a{text-decoration:none;color:inherit} .dg svg{max-width:100%}}"""


def esc(t):
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(str(t)))
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def plain(t):
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", str(t).replace("`", ""))


def strings(x, where="spec"):
    """Every string in the spec with its path, for text checks."""
    if isinstance(x, str):
        yield where, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f"{where}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f"{where}[{i}]")


def words(t):
    return len(plain(t).split())


def blocks_of(sec):
    """(subsection or {} for the section's own blocks, block) in page order."""
    for b in sec.get("blocks") or []:
        yield {}, b
    for sub in sec.get("subsections") or []:
        for b in sub.get("blocks") or []:
            yield sub, b


def all_blocks(spec, kind=None):
    for name, sec in spec.get("sections", {}).items():
        if isinstance(sec, dict):
            for sub, b in blocks_of(sec):
                if kind is None or b.get("type") == kind:
                    yield name, sub, b


def rows(b, key="rows"):
    return b.get(key) or []


def pii(s):
    """'e-mail address' or 'phone number' when the text holds one, else None."""
    if EMAIL.search(s):
        return "e-mail address"
    for m in PHONE_INT.finditer(s):
        if len(re.sub(r"\D", "", m[0])) >= 7:
            return "phone number"
    for m in PHONE_LOCAL.finditer(s):
        if len(re.sub(r"\D", "", m[0])) >= 9 and not re.fullmatch(r"[0-2]\d[0-5]\d-[0-2]\d[0-5]\d", m[0]):
            return "phone number"
    return None


def scan_ids(folder):
    """Requirement ids in the inputs folder, found again by inputs.py (None when the folder is missing)."""
    if not folder.is_dir():
        return None
    import importlib.util
    sys.dont_write_bytecode = True  # no __pycache__ next to the templates
    spec = importlib.util.spec_from_file_location("inputs", Path(__file__).with_name("inputs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    found = set()
    for p in sorted(x for x in folder.rglob("*") if x.is_file()):
        kind, text, note = mod.one(p)
        found |= mod.ids_in(text or "")
    return found


def check(spec, root):
    err, warn = [], []
    for k in ("title", "date", "sections"):
        if not spec.get(k):
            err.append(f"spec needs {k}")
    secs = spec.get("sections") or {}
    for s in SECTIONS:
        if s not in secs:
            err.append(f"section '{s}' missing: every brief has the {len(SECTIONS)} fixed sections (one line when there is nothing to say)")
    for s in secs:
        if s not in SECTIONS:
            err.append(f"section '{s}' unknown: the top level is fixed, put it in a subsection of one of: {', '.join(SECTIONS)}")
    for name, sec in secs.items():
        if not isinstance(sec, dict) or not (sec.get("line") or sec.get("blocks") or sec.get("subsections")):
            err.append(f"section '{name}': give `line` (one sentence), `blocks`, or `subsections` [{{title, blocks}}]")
            continue
        if sec.get("line"):
            if sec.get("blocks") or sec.get("subsections"):
                err.append(f"section '{name}': `line` or blocks/subsections, not both")
            if name in CORE:
                warn.append(f"section '{name}' is one line: this section carries the brief, fill it")
        for i, sub in enumerate(sec.get("subsections") or []):
            w = f"section '{name}' subsection {i + 1}"
            if not sub.get("title") or not sub.get("blocks"):
                err.append(f"{w}: needs title and blocks (blocks without a title go in the section's own `blocks`)")
            elif (sub["title"].strip().lower() in (GENERIC_TITLES | {name.lower()} | {b.get("type", "") for b in sub["blocks"]}) - ALLOWED_TITLES.get(name, set())):
                warn.append(f"{w}: title '{sub['title']}' fits any brief: name it from the input, or put the blocks in the section's `blocks`")
        for sub, b in blocks_of(sec):
            if b.get("type") not in BLOCKS:
                err.append(f"section '{name}': block type '{b.get('type')}' unknown ({', '.join(sorted(BLOCKS))})")
    if "At a glance" in secs and any(str(r[0]).strip().lower() == "status" for _, b in blocks_of(secs["At a glance"]) if b.get("type") == "facts"
                                    for r in rows(b) if isinstance(r, list) and len(r) == 2):
        err.append("At a glance: the Status row is computed by the build from the requirements rows; remove the typed one")
    if err:
        return err, warn
    # typed ids, then references between blocks
    req, src, ents, needs_of, work_ids = {}, {}, set(), [], {}
    for name, sub, b in all_blocks(spec, "requirements"):
        for r in rows(b):
            if not r.get("id") or not r.get("text") or r.get("status") not in STATUS:
                err.append(f"requirement {r.get('id')!r}: needs id, text and status in {STATUS}")
            elif r["id"] in req:
                err.append(f"requirement {r['id']} listed twice")
            else:
                req[r["id"]] = r
    for name, sub, b in all_blocks(spec, "sources"):
        for r in rows(b):
            need = ("id", "system") if r.get("planned") else ("id", "system", "connector", "key", "cadence")
            if not all(r.get(k) for k in need):
                err.append(f"source {r.get('id')!r}: needs {', '.join(need)} (and points [[name, description]]); `planned: true` for a source not yet defined")
            elif r["id"] in src:
                err.append(f"source {r['id']} listed twice")
            else:
                src[r["id"]] = r
            for p in r.get("points") or []:
                if not isinstance(p, list) or len(p) not in (2, 3):
                    err.append(f"source {r.get('id')}: data point {p!r} must be [name, description] or [name, description, note]")
    given = []
    for name, sub, b in all_blocks(spec, "options"):
        for r in rows(b):
            if not r.get("need") or not r.get("rec") or not r.get("why"):
                err.append(f"option {r.get('need')!r}: needs need, rec and why")
                continue
            needs_of.append(r["need"])
            alts = r.get("alternatives") or []
            if r.get("given"):
                given.append(r["rec"])
                if alts:
                    err.append(f"option '{r['need']}': given platforms are not re-litigated, drop the alternatives")
                continue
            if not 2 <= len(alts) <= 3 or any(not a.get("name") or not a.get("tradeoff") for a in alts):
                err.append(f"option '{r['need']}': give 2-3 alternatives to {r['rec']}, each {{name, tradeoff}} (or mark it given)")
            if any(a.get("name", "").lower() == r["rec"].lower() for a in alts):
                err.append(f"option '{r['need']}': {r['rec']} is both the pick and an alternative")
            if not r.get("source"):
                warn.append(f"option '{r['need']}': no source (official page) for the product facts")
    named = lambda tech, text: re.search(r"(?<![\w])" + re.escape(tech) + r"(?![\w])", text, re.I)  # the tech as a whole word
    for tech in spec.get("stack") or []:  # the confirmed stack: each item is a given row, used as given
        if not any(named(tech, g) for g in given):
            err.append(f"stack '{tech}' is confirmed but has no given options row (rec naming it, given: true)")
    for g in given:
        if spec.get("stack") and not any(named(t, g) for t in spec["stack"]):
            warn.append(f"option given '{g}' is not in the confirmed stack {spec['stack']}: confirm it or drop given")
    for name, sub, b in all_blocks(spec, "work"):
        for r in rows(b):
            if not all(r.get(k) for k in ("id", "what", "kind", "owner", "ref")) or r["kind"] not in WORK:
                err.append(f"work item {r.get('id')!r}: needs id, what, kind in {WORK}, owner, ref [ids]")
            elif r["id"] in work_ids:
                err.append(f"work item {r['id']} listed twice")
            else:
                work_ids[r["id"]] = r
    for name, sub, b in all_blocks(spec, "work"):
        for r in rows(b):
            for d in r.get("depends") or []:
                if d not in work_ids:
                    err.append(f"work item {r.get('id')}: depends on '{d}', not a work item id")
            for ref in r.get("ref") or []:
                if ref not in req and ref not in src and ref not in needs_of:
                    warn.append(f"work item {r.get('id')}: ref '{ref}' is no requirement id, source id or option need")
    for name, sub, b in all_blocks(spec, "links"):
        ids = [e.get("id") for e in b.get("entities") or []]
        ents |= set(ids)
        for j in b.get("joins") or []:
            if j.get("a") not in ids or j.get("b") not in ids or not j.get("on"):
                err.append(f"links '{b.get('title')}': join {j!r} needs a, b (entity ids) and on")
            elif len(j["on"]) > LABEL:
                warn.append(f"links '{b.get('title')}': join label '{j['on']}' over {LABEL} characters, shorten it")
    for name, sub, b in all_blocks(spec, "needs"):
        for r in rows(b):
            if not r.get("use") or not r.get("data"):
                err.append(f"needs row {r!r}: needs use, data, sources [ids]")
            for s in r.get("sources") or []:
                if s not in src:
                    err.append(f"needs row '{r.get('use')}': source '{s}' has no sources row")
            if r.get("missing") and not r.get("sources"):
                err.append(f"needs row '{r.get('use')}': `missing` says what the listed sources lack; with no source, leave `sources` empty")
    in_diagram = set()
    for name, sub, b in all_blocks(spec):
        t = b["type"]
        w = f"{name} / {sub.get('title')}: {t}"
        if t in ("flow", "links", "timeline"):
            if not b.get("title"):
                err.append(f"{w} needs a title")
            if not b.get("key"):
                warn.append(f"{w} '{b.get('title')}': no key (legend line)")
        if t == "flow":
            ids = {}
            for n in b.get("nodes") or []:
                if not n.get("id") or not n.get("label") or not isinstance(n.get("col"), int) or not isinstance(n.get("row"), int):
                    err.append(f"{w}: node {n!r} needs id, label, col, row")
                elif n["id"] in ids:
                    err.append(f"{w}: node id {n['id']} twice")
                else:
                    ids[n["id"]] = n
                if n.get("kind", "step") not in NODE:
                    err.append(f"{w}: node kind '{n.get('kind')}' unknown ({', '.join(NODE)})")
                if n.get("kind") == "source":
                    if n["id"] not in src:
                        err.append(f"{w}: source box '{n['id']}' has no sources row (same id)")
                    in_diagram.add(n["id"])
            if len(ids) < 3:
                err.append(f"{w}: fewer than 3 boxes, write it as text")
            for e in b.get("edges") or []:
                if e.get("from") not in ids or e.get("to") not in ids:
                    err.append(f"{w}: edge {e!r} names an unknown box")
                if len(e.get("label") or "") > LABEL:
                    warn.append(f"{w}: edge label '{e['label']}' over {LABEL} characters, shorten it")
            lanes = b.get("lanes") or []
            if lanes and len(lanes) <= max((n.get("row", 0) for n in ids.values()), default=0):
                err.append(f"{w}: one lane per row ({len(lanes)} lanes, rows go to {max(n['row'] for n in ids.values())})")
        if t == "timeline":
            st = b.get("steps") or []
            if any(not s.get("at") or not s.get("do") for s in st):
                err.append(f"{w}: every step needs at and do")
            if len(st) > MAX_STEPS:
                warn.append(f"{w} '{b.get('title')}': {len(st)} steps, over {MAX_STEPS}: merge steps")
        if t == "table" and (not b.get("head") or any(len(r) != len(b["head"]) for r in rows(b))):
            err.append(f"{w}: head and rows of the same length")
        if t == "facts" and any(len(r) != 2 for r in rows(b)):
            err.append(f"{w}: rows are [label, value]")
        if t == "terms" and any(len(r) != 2 for r in rows(b)):
            err.append(f"{w}: rows are [term, meaning]")
        if t == "bullets" and not b.get("items"):
            err.append(f"{w}: items missing")
        if t == "text" and not b.get("text"):
            err.append(f"{w}: text missing")
        if t == "profile":
            p = root / b.get("from", "")
            if not b.get("from") or not p.is_file():
                err.append(f"{w}: `from` must be the profile.json written by profile.py (not found: {b.get('from')})")
            else:
                try:
                    for pw, ps in strings(json.loads(p.read_text(encoding="utf-8")), b["from"]):
                        if ABS.search(ps):
                            err.append(f"{pw}: absolute or machine path in the profile; run profile.py from the project root with relative paths")
                except ValueError:
                    err.append(f"{w}: {b['from']} is not JSON")
    for s in src:
        if s not in in_diagram:
            warn.append(f"source {s} is not a source box in any flow diagram (Context)")
    listed = [i for inp in spec.get("inputs") or [] for i in inp.get("ids") or []]
    scanned = scan_ids(root / (spec.get("inputs_dir") or INPUTS_DIR))
    if scanned is None:
        print(f"note: {spec.get('inputs_dir') or INPUTS_DIR} not found: ids checked from the spec's inputs list only")
    else:
        for i in scanned - set(listed):
            warn.append(f"input id {i} found in the inputs folder but not in the spec's inputs list")
    missing = [i for i in dict.fromkeys(listed + sorted(scanned or [])) if i not in req]
    if missing:
        unlisted = [i for i in missing if i not in listed]
        err.append(f"input requirement ids missing from the Requirements rows: {', '.join(missing)}"
                   + (f" (found again in the inputs folder, not in the spec's inputs list: {', '.join(unlisted)})" if unlisted else ""))
    if "Requirements" in secs and not secs["Requirements"].get("line") and not req:
        err.append("Requirements: no requirements block; list every requirement with its id and status")
    if "Data findings" in secs and not secs["Data findings"].get("line") and not any(all_blocks(spec, "profile")):
        warn.append("Data findings has content but no profile block: numbers come from profile.py, or the section is one line")
    seen = {}
    for where, s in strings(spec):
        if "TODO" in s:
            err.append(f"{where}: TODO left")
        if ABS.search(s):
            err.append(f"{where}: absolute or machine path; paths are relative to the project root")
        if (what := pii(s)):
            err.append(f"{where}: {what} in the text: no personal data in a brief, say the field name")
        for m in STACK_RX.finditer(s):
            if int(m[1]) != len(req) and not where.startswith("spec.sections.Requirements"):
                warn.append(f"{where}: says {m[1]} requirements, the Requirements rows hold {len(req)}")
        for rx in SECRET_VALUE:
            if (m := rx.search(s)):
                err.append(f"{where}: likely secret value for '{m[1]}' (write <redacted>)")
                break
        if (m := CHAT.search(s)):
            warn.append(f"{where}: voice: '{m[0]}': write as the author, open points as facts")
        if (m := FILLER.search(s)):
            warn.append(f"{where}: filler: '{m[0]}'")
        if words(s) > WORDS:
            warn.append(f"{where}: {words(s)} words, cap {WORDS}: split or cut")
        for sent in re.split(r"(?<=[.!?])\s+", plain(s)):
            k = sent.strip().lower()
            if len(k.split()) >= 6:
                if k in seen and seen[k] != where:
                    warn.append(f"{where}: repeat: '{sent.strip()[:60]}' also in {seen[k]}")
                seen.setdefault(k, where)
    return err, warn


# ---- SVG ----------------------------------------------------------------------------------------------------------
CH = 6.6  # px per character at 12px


def wrap(text, width, lines, warn, where):
    """Greedy word wrap into at most `lines` lines of `width` characters; the rest is cut with … (WARN)."""
    out, cur = [], ""
    for w in plain(text).split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    out.append(cur)
    if len(out) > lines:
        warn.append(f"{where}: box text '{plain(text)}' cut, shorten it")
        out = out[:lines]
        out[-1] = out[-1][:width - 1] + "…"
    return out


def tx(x, y, t, cls="", anchor="middle"):
    return f'<text x="{x:.0f}" y="{y:.0f}" class="{cls}" text-anchor="{anchor}">{html.escape(t)}</text>'


def label_bg(x, y, t, cls="lbl"):
    w = len(t) * CH + 6
    return f'<rect class="bg" x="{x - w / 2:.0f}" y="{y - 11}" width="{w:.0f}" height="14" rx="2"/>' + tx(x, y, t, cls)


def svg(w, h, body, title):
    return (f'<div class="dg"><svg viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{html.escape(title)}">'
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5 0 10z" class="ar"/></marker></defs>' + body + "</svg></div>")


def svg_flow(d, warn, where):
    W, H, GX, GY, PAD = 150, 56, 72, 30, 8
    nodes = {n["id"]: n for n in d["nodes"]}
    lanes = d.get("lanes") or []
    LW = 14 + max((len(l) for l in lanes), default=0) * CH if lanes else 0
    cols = max(n["col"] for n in nodes.values()) + 1
    nrows = max(n["row"] for n in nodes.values()) + 1
    edges = d.get("edges") or []
    skip0 = sum(1 for e in edges if nodes[e["from"]]["row"] == nodes[e["to"]]["row"] == 0 and abs(nodes[e["from"]]["col"] - nodes[e["to"]]["col"]) > 1)
    TOP = 8 * skip0 + 12 if skip0 else 0  # room above the top row for edges routed over it
    X = lambda c: PAD + LW + c * (W + GX)
    Y = lambda r: PAD + TOP + r * (H + GY)
    width, height = PAD * 2 + LW + cols * W + (cols - 1) * GX, PAD * 2 + TOP + nrows * H + (nrows - 1) * GY
    out = []
    for r, name in enumerate(lanes):
        out.append(f'<rect class="lane" x="{PAD}" y="{Y(r) - GY / 2 + 2:.0f}" width="{width - PAD * 2}" height="{H + GY - 4}" rx="4"/>')
        out.append(tx(PAD + 7, Y(r) + 4, name.upper(), "lanet", "start"))
    # same row → right side to left side (over the row when a box sits between); lower row → bottom to top; upper row → top to bottom, dashed
    side = lambda e: "h" if nodes[e["from"]]["row"] == nodes[e["to"]]["row"] else "v"
    outs = {i: sorted((e for e in edges if e["from"] == i and side(e) == "v"), key=lambda e: nodes[e["to"]]["col"]) for i in nodes}
    ins = {i: sorted((e for e in edges if e["to"] == i and side(e) == "v"), key=lambda e: nodes[e["from"]]["col"]) for i in nodes}
    gap_used = {}  # column gaps and row tops already carrying a detour: later ones shift 8 px
    for e in edges:
        a, b = nodes[e["from"]], nodes[e["to"]]
        cls = "dashed" if e.get("dashed") else ""
        if a["row"] == b["row"]:
            left, right = (a, b) if a["col"] < b["col"] else (b, a)
            between = [n for n in nodes.values() if n["row"] == a["row"] and left["col"] < n["col"] < right["col"]]
            y = Y(a["row"]) + H / 2
            if not between:
                x1, x2 = X(left["col"]) + W, X(right["col"])
                ends = 'marker-end="url(#ar)"' if left is a else 'marker-start="url(#ar)"'
                out.append(f'<line class="{cls}" x1="{x1}" y1="{y:.0f}" x2="{x2}" y2="{y:.0f}" {ends}/>')
                lx, ly = (x1 + x2) / 2, y - 6
            else:  # a box in between: up out of the source, over the row in the gap above it, down into the target
                k = gap_used[("row", a["row"])] = gap_used.get(("row", a["row"]), 0) + 1
                ye = Y(a["row"])
                yt = ye - GY / 2 + 4 - (k - 1) * 8
                x1, x2 = X(a["col"]) + W / 2 + (k - 1) * 8, X(b["col"]) + W / 2 - (k - 1) * 8
                out.append(f'<polyline class="{cls}" points="{x1:.0f},{ye} {x1:.0f},{yt:.0f} {x2:.0f},{yt:.0f} {x2:.0f},{ye}" marker-end="url(#ar)"/>')
                lx, ly = (x1 + x2) / 2, yt - 4
        elif b["row"] > a["row"]:
            oi, on = outs[a["id"]].index(e), len(outs[a["id"]])
            ii, inn = ins[b["id"]].index(e), len(ins[b["id"]])
            x1, y1 = X(a["col"]) + W * (oi + 1) / (on + 1), Y(a["row"]) + H
            x2, y2 = X(b["col"]) + W * (ii + 1) / (inn + 1), Y(b["row"])
            ym = y1 + GY / 2 + (oi - (on - 1) / 2) * 8
            between = [n for n in nodes.values() if n["col"] == b["col"] and a["row"] < n["row"] < b["row"]]
            if a["col"] == b["col"] and on == 1 and inn == 1 and not between:
                out.append(f'<line class="{cls}" x1="{x1:.0f}" y1="{y1}" x2="{x2:.0f}" y2="{y2}" marker-end="url(#ar)"/>')
                lx, ly = x1 + 8 + len(e.get("label") or "") * CH / 2, (y1 + y2) / 2 + 4
            elif between:  # a box sits in the way: run down the column gap beside it, then in from above
                k = gap_used[("col", b["col"])] = gap_used.get(("col", b["col"]), 0) + 1
                xg = (X(b["col"]) - GX / 2 if b["col"] else X(b["col"]) + W + GX / 2) + (k - 1) * 8
                yg = y2 - GY / 2 - (k - 1) * 6
                out.append(f'<polyline class="{cls}" points="{x1:.0f},{y1} {x1:.0f},{ym:.0f} {xg:.0f},{ym:.0f} {xg:.0f},{yg:.0f} {x2:.0f},{yg:.0f} {x2:.0f},{y2}" marker-end="url(#ar)"/>')
                lx, ly = xg, (ym + yg) / 2 + 4
            else:
                out.append(f'<polyline class="{cls}" points="{x1:.0f},{y1} {x1:.0f},{ym:.0f} {x2:.0f},{ym:.0f} {x2:.0f},{y2}" marker-end="url(#ar)"/>')
                lx, ly = (x1 + x2) / 2, ym - 4
        else:  # upward: from the source's top edge to the target's bottom edge, dashed
            x1, y1, x2, y2 = X(a["col"]) + W / 2, Y(a["row"]), X(b["col"]) + W / 2, Y(b["row"]) + H
            ym = y1 - GY / 2
            between = [n for n in nodes.values() if n["col"] == b["col"] and b["row"] < n["row"] < a["row"]]
            if a["col"] == b["col"] and not between:
                out.append(f'<line class="dashed" x1="{x1:.0f}" y1="{y1}" x2="{x2:.0f}" y2="{y2}" marker-end="url(#ar)"/>')
                lx, ly = x1 + 8 + len(e.get("label") or "") * CH / 2, (y1 + y2) / 2 + 4
            elif between:
                k = gap_used[("col", b["col"])] = gap_used.get(("col", b["col"]), 0) + 1
                xg = (X(b["col"]) - GX / 2 if b["col"] else X(b["col"]) + W + GX / 2) + (k - 1) * 8
                yg = y2 + GY / 2 - 8  # above the run the downward edges use
                out.append(f'<polyline class="dashed" points="{x1:.0f},{y1} {x1:.0f},{ym:.0f} {xg:.0f},{ym:.0f} {xg:.0f},{yg:.0f} {x2:.0f},{yg:.0f} {x2:.0f},{y2}" marker-end="url(#ar)"/>')
                lx, ly = xg, (ym + yg) / 2 + 4
            else:
                out.append(f'<polyline class="dashed" points="{x1:.0f},{y1} {x1:.0f},{ym:.0f} {x2:.0f},{ym:.0f} {x2:.0f},{y2}" marker-end="url(#ar)"/>')
                lx, ly = (x1 + x2) / 2, ym - 4
        if e.get("label"):
            out.append(label_bg(lx, ly, e["label"]))
    for n in nodes.values():
        x, y = X(n["col"]), Y(n["row"])
        kind = n.get("kind", "step")
        out.append(f'<rect class="box {kind}" x="{x}" y="{y}" width="{W}" height="{H}" rx="{20 if kind == "consumer" else 7}"/>')
        lines = wrap(n["label"], 21, 2, warn, where)
        sub = wrap(n["sub"], 22, 1, warn, where) if n.get("sub") else []
        top = y + H / 2 - (len(lines) + len(sub)) * 7.5 + 10
        for k, l in enumerate(lines):
            out.append(tx(x + W / 2, top + k * 15, l, "t"))
        for k, l in enumerate(sub):
            out.append(tx(x + W / 2, top + len(lines) * 15 + k * 14 - 1, l, "s"))
        if n.get("tag"):
            out.append(tx(x + W - 6, y + 11, n["tag"].upper(), "tag", "end"))
    return svg(width, height, "".join(out), d["title"])


def svg_links(d, warn, where):
    W, HH, LH, GX, GY, PAD, BUS = 180, 26, 16, 108, 64, 8, 18  # GX fits "on " + a 12-character key
    ents = d["entities"]
    per = min(4, len(ents))
    heights = [HH + LH * len(e.get("ids") or []) + 8 for e in ents]
    nrows = -(-len(ents) // per)
    row_h = [max(heights[r * per:(r + 1) * per]) for r in range(nrows)]
    joins = d.get("joins") or []
    pos, out, bus = {}, [], {}
    for i, e in enumerate(ents):
        r, c = divmod(i, per)
        pos[e["id"]] = (PAD + c * (W + GX), PAD + sum(row_h[:r]) + r * GY + sum(bus.get(k, 0) for k in range(r)), heights[i], r, c)
    # same-row joins between non-adjacent boxes run on a bus below the row; count them first
    for j in joins:
        ra, rb = pos[j["a"]][3], pos[j["b"]][3]
        if ra == rb and abs(pos[j["a"]][4] - pos[j["b"]][4]) > 1:
            bus[ra] = bus.get(ra, 0) + BUS
    for i, e in enumerate(ents):
        r, c = divmod(i, per)
        pos[e["id"]] = (PAD + c * (W + GX), PAD + sum(row_h[:r]) + r * GY + sum(bus.get(k, 0) for k in range(r)), heights[i], r, c)
    used = {}
    for j in joins:
        (ax, ay, ah, ar, ac), (bx, by, bh, br, bc) = pos[j["a"]], pos[j["b"]]
        if ar == br and abs(ac - bc) == 1:
            (lx, rx) = (ax + W, bx) if ac < bc else (bx + W, ax)
            y = ay + min(ah, bh) / 2
            out.append(f'<line x1="{lx}" y1="{y:.0f}" x2="{rx}" y2="{y:.0f}"/>')
            out.append(label_bg((lx + rx) / 2, y - 6, f"on {j['on']}"))
        elif ar == br:
            k = used[ar] = used.get(ar, 0) + 1
            yb = ay + row_h[ar] + 6 + k * BUS
            x1, x2 = ax + W / 2, bx + W / 2
            out.append(f'<polyline points="{x1:.0f},{ay + ah} {x1:.0f},{yb} {x2:.0f},{yb} {x2:.0f},{by + bh}"/>')
            out.append(label_bg((x1 + x2) / 2, yb - 4, f"on {j['on']}"))
        else:
            x1, y1, x2, y2 = ax + W / 2, ay + ah / 2, bx + W / 2, by + bh / 2
            out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>')
            out.append(label_bg((x1 + x2) / 2, (y1 + y2) / 2 + 4, f"on {j['on']}"))
    for e in ents:
        x, y, h, r, c = pos[e["id"]]
        out.append(f'<rect class="ent" x="{x}" y="{y}" width="{W}" height="{h}" rx="6"/>')
        out.append(f'<rect class="enth" x="{x}" y="{y}" width="{W}" height="{HH}" rx="6"/><rect class="enth" x="{x}" y="{y + HH - 6}" width="{W}" height="6"/>')
        out.append(tx(x + 10, y + 17, wrap(e["label"], 24, 1, warn, where)[0], "t", "start"))
        for k, i in enumerate(e.get("ids") or []):
            out.append(tx(x + 10, y + HH + 13 + k * LH, wrap(i, 26, 1, warn, where)[0], "id", "start"))
    width = PAD * 2 + per * W + (per - 1) * GX
    height = PAD * 2 + sum(row_h) + (nrows - 1) * GY + sum(bus.values())
    return svg(width, height, "".join(out), d["title"])


def svg_timeline(d, warn, where):
    W, H, GX, PAD, TOP = 150, 50, 34, 8, 20
    steps = d["steps"]
    out = []
    for i, s in enumerate(steps):
        x = PAD + i * (W + GX)
        out.append(tx(x + W / 2, TOP - 6, s["at"], "at"))
        out.append(f'<rect class="box step" x="{x}" y="{TOP}" width="{W}" height="{H}" rx="7"/>')
        lines = wrap(s["do"], 21, 2, warn, where)
        top = TOP + H / 2 - len(lines) * 7.5 + 10
        for k, l in enumerate(lines):
            out.append(tx(x + W / 2, top + k * 15, l, "t"))
        if s.get("out"):
            out.append(tx(x + W / 2, TOP + H + 16, wrap(s["out"], 22, 1, warn, where)[0], "out"))
        if i:
            out.append(f'<line x1="{x - GX + 2}" y1="{TOP + H / 2}" x2="{x - 2}" y2="{TOP + H / 2}" marker-end="url(#ar)"/>')
    width = PAD * 2 + len(steps) * W + (len(steps) - 1) * GX
    return svg(width, TOP + H + 30, "".join(out), d["title"])


# ---- HTML blocks ----------------------------------------------------------------------------------------------------
def table(head, body_rows, cls="tt"):
    h = "".join(f"<th>{esc(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f'<td data-h="{html.escape(plain(head[i]))}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in body_rows)
    return f'<div class="scroll"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'


def chip(kind, text=None):
    return f'<span class="chip {kind}">{esc(text or kind)}</span>'


def diagram(b, fn, warn, where):
    return fn(b, warn, where) + (f'<p class="key">Key: {esc(b["key"])}</p>' if b.get("key") else "")


def render_sources(b):
    out = []
    for r in rows(b):
        out.append(f'<h4>{chip("id", r["id"])} {esc(r["system"])}' + (" " + chip("gap", "planned") if r.get("planned") else "") + "</h4>")
        meta = [(k.capitalize(), r[k]) for k in ("connector", "key", "cadence", "volume") if r.get(k)]
        if meta:
            out.append('<p class="meta">' + " &middot; ".join(f"<b>{k}</b> {esc(v)}" for k, v in meta) + "</p>")
        if r.get("note"):
            out.append(f"<p>{esc(r['note'])}</p>")
        pts = r.get("points") or []
        if pts:
            three = any(len(p) == 3 for p in pts)
            head = ["Data point", "Description"] + (["Note"] if three else [])
            out.append(table(head, [[f"<code>{html.escape(p[0])}</code>", esc(p[1])] + ([esc(p[2]) if len(p) == 3 else ""] if three else []) for p in pts]))
    return "".join(out)


def render_profile(b, root):
    p = json.loads((root / b["from"]).read_text(encoding="utf-8"))
    out = []
    for f in p.get("files") or []:
        out.append(f'<h4>{esc(f["file"])}</h4><p class="meta"><b>Rows</b> {f["rows"]} &middot; <b>Columns</b> {len(f["columns"])}</p>')
        body = []
        for c in f["columns"]:
            sens = c.get("sensitive")
            mm = ["&ndash;", "&ndash;"] if sens or c.get("min") is None else [esc(c["min"]), esc(c["max"])]
            body.append([f"<code>{html.escape(c['name'])}</code>" + (" " + chip("sens", "values withheld") if sens else ""), c["type"],
                         str(c["count"]), f"{c['null_pct']:.0f}%", str(c["distinct"]), *mm])
        out.append(table(["Column", "Type", "Non-null", "Null", "Distinct", "Min", "Max"], body))
    if p.get("overlaps"):
        out.append("<h4>Key overlap between files</h4>")
        out.append(table(["Key", "A", "B", "Distinct in A", "Distinct in B", "In both", "A keys found in B"],
                         [[f"<code>{html.escape(o['key'])}</code>", esc(o["a"]), esc(o["b"]), str(o["a_distinct"]), str(o["b_distinct"]), str(o["both"]),
                           f"{o['pct_a_in_b']:.0f}%"] for o in p["overlaps"]]))
    return "".join(out)


def block(b, root, warn, where):
    t = b["type"]
    if t == "text":
        return f"<p>{esc(b['text'])}</p>"
    if t == "bullets":
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ul>"
    if t == "table":
        return (f"<h4>{esc(b['title'])}</h4>" if b.get("title") else "") + table(b["head"], [[esc(c) for c in r] for r in rows(b)])
    if t == "facts":
        return '<dl class="facts">' + "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows(b)) + "</dl>"
    if t == "flow":
        return diagram(b, svg_flow, warn, where)
    if t == "links":
        return diagram(b, svg_links, warn, where)
    if t == "timeline":
        return diagram(b, svg_timeline, warn, where)
    if t == "requirements":
        body = [[f"<b>{esc(r['id'])}</b>", esc(r["text"]), chip(r["status"]), esc(r.get("source", "")), esc(r.get("note", ""))] for r in rows(b)]
        return table(["ID", "Requirement", "Status", "Source", "Note"], body)
    if t == "sources":
        return render_sources(b)
    if t == "needs":
        body = []
        for r in rows(b):
            srcs = " ".join(chip("id", s) for s in r.get("sources") or []) or chip("none", "no source")
            if r.get("missing"):
                srcs += " " + chip("gap", "partial") + f" missing: {esc(r['missing'])}"
            body.append([esc(r["use"]), esc(r["data"]), srcs, esc(r.get("note", ""))])
        return table(["Use case", "Data needed", "Sources", "Note"], body)
    if t == "profile":
        return render_profile(b, root)
    if t == "options":
        body = []
        for r in rows(b):
            rec = esc(r["rec"]) + (" " + chip("given") if r.get("given") else "")
            alts = "<br>".join(f"{esc(a['name'])} &mdash; {esc(a['tradeoff'])}" for a in r.get("alternatives") or []) or ("given" if r.get("given") else "")
            body.append([esc(r["need"]), rec, esc(r["why"]), alts, f'<span class="src">{esc(r.get("source", ""))}</span>'])
        return table(["Need", "Recommended", "Why", "Alternatives", "Source"], body)
    if t == "work":
        body = [[f"<b>{esc(r['id'])}</b>", esc(r["what"]), f'<span class="kind">{r["kind"]}</span>', esc(r["owner"]),
                 ", ".join(esc(d) for d in r.get("depends") or []) or "&ndash;", " ".join(chip("id", x) for x in r["ref"])] for r in rows(b)]
        return table(["ID", "What", "Kind", "Owner", "Depends on", "Ref"], body)
    if t == "terms":
        return '<div class="terms">' + "".join(f"<div><b>{esc(k)}</b> &mdash; {esc(v)}</div>" for k, v in rows(b)) + "</div>"
    return ""


def render(spec, root, warn):
    secs = spec["sections"]
    toc = "".join(f'<a href="#s{i}">{i} {html.escape(s)}</a>' for i, s in enumerate(SECTIONS, 1))
    inputs = " &middot; ".join(esc(i["name"]) for i in spec.get("inputs") or [])
    out = [f'<p class="eyebrow">Requirements brief</p><h1>{esc(spec["title"])}</h1>']
    if spec.get("subtitle"):
        out.append(f'<p class="lead">{esc(spec["subtitle"])}</p>')
    out.append(f'<p class="stamp">{esc(spec["date"])}' + (f" &middot; Inputs: {inputs}" if inputs else "") + "</p>")
    out.append(f'<nav class="toc">{toc}</nav>')
    for i, name in enumerate(SECTIONS, 1):
        sec = secs[name]
        out.append(f'<section id="s{i}"><h2>{i} {html.escape(name)}</h2>')
        if sec.get("line"):
            out.append(f'<p class="line">{esc(sec["line"])}</p>')
        else:
            if sec.get("lead"):
                out.append(f'<p class="lead">{esc(sec["lead"])}</p>')
            last = None
            for sub, b in blocks_of(sec):
                if sub and sub is not last:
                    out.append(f"<h3>{esc(sub['title'])}</h3>")
                last = sub
                out.append(block(b, root, warn, f"{name} / {sub.get('title', '')}"))
        if name == "At a glance":  # computed from the rows, shown even when the section is one line
            out.append(f'<dl class="facts"><dt>Status</dt><dd>{esc(status_line(spec))}</dd></dl>')
        out.append("</section>")
    head = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-requirements-brief {VERSION}"><title>{html.escape(plain(spec["title"]))}</title>'
            f"<style>{CSS}</style></head><body><main>")
    return head + "".join(out) + "</main></body></html>"


def status_line(spec):
    """Counts from the typed rows (never typed by hand): shown in At a glance and printed by the build."""
    req = [r for _, _, b in all_blocks(spec, "requirements") for r in rows(b)]
    by = {s: sum(r["status"] == s for r in req) for s in STATUS}
    work = [r for _, _, b in all_blocks(spec, "work") for r in rows(b)]
    gaps = sum(1 for _, _, b in all_blocks(spec, "needs") for r in rows(b) if not r.get("sources"))
    open_ = sum(r["kind"] in ("decide", "clarify") for r in work)
    n = lambda k, one, many: f"{k} {one if k == 1 else many}"
    return (f"{n(len(req), 'requirement', 'requirements')}: {by['clear']} clear · {by['gap']} gap · {by['conflict']} conflict · "
            f"{n(gaps, 'use case', 'use cases')} without a source · {n(open_, 'decision or clarification', 'decisions and clarifications')} open (section 10)")


def summary(spec):
    src = sum(len(rows(b)) for _, _, b in all_blocks(spec, "sources"))
    opt = [r for _, _, b in all_blocks(spec, "options") for r in rows(b)]
    work = sum(len(rows(b)) for _, _, b in all_blocks(spec, "work"))
    return f"{status_line(spec)} · {src} sources · {len(opt)} tech options ({sum(bool(o.get('given')) for o in opt)} given) · {work} work items"


def main(spec_path, out_path):
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path.cwd()
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out = Path(out_path)
    err, warn = check(spec, root)
    if not out.parent.is_dir():
        err.append(f"output folder {out.parent.as_posix()} does not exist")
    if err:
        for e in err:
            print("ERROR", e)
        sys.exit(1)
    page = render(spec, root, warn)
    out.write_text(page, encoding="utf-8")
    for w in warn:
        print("WARN", w)
    print(summary(spec))
    print(f"built {out.as_posix()}: {len(SECTIONS)} sections, {len(warn)} WARN")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
