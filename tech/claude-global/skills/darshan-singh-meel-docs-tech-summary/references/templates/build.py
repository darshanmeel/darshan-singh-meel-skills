"""Build one tech summary (a self-contained HTML page with inline SVG, optionally Markdown with Mermaid) from a JSON spec.
Top-level sections are fixed (same 11, same order, every run); the blocks inside are chosen per repo, within a depth budget.

Usage: python build.py <spec.json> <out.html> [--md <out.md>]     (run from the repo root)
Spec: ../spec.md. ERROR lines stop the build; WARN lines are fixed or explained in the reply.
"""
import html
import json
import re
import sys
from pathlib import Path

VERSION = "1.0.0"
TOOL = "darshan-singh-meel-docs-tech-summary"
MARKER = ".generated-by-darshan-singh-meel-docs"  # the knowledge graph skips folders holding it
SECTIONS = ["At a glance", "Components", "Main flows", "Data model", "Integrations", "Tech stack",
            "Deploy and environments", "Security and access", "Run locally", "Top risks", "Where to look next"]
NEEDS = {"At a glance": ["facts", "scope"], "Components": ["flow", "components"], "Main flows": ["seq"], "Data model": ["er"],
         "Integrations": ["integrations"], "Tech stack": ["stack"], "Deploy and environments": ["envs"], "Run locally": ["commands"],
         "Top risks": ["risks"], "Where to look next": ["pointers"]}  # a section with content holds these block types
CORE = {"At a glance", "Components", "Main flows", "Tech stack", "Run locally", "Top risks", "Where to look next"}  # one line here: WARN
BLOCKS = {"text", "bullets", "table", "facts", "rules", "scope", "flow", "seq", "er", "example", "components", "integrations", "stack",
          "envs", "commands", "risks", "pointers"}
FIELDS = {"components": ["name", "does", "tech", "where"], "integrations": ["system", "direction", "via", "data"],
          "stack": ["layer", "tech", "version", "pinned_in"], "envs": ["env", "runs_on", "deploy", "access"],
          "commands": ["cmd", "does"], "risks": ["risk", "impact", "status", "mitigation"], "pointers": ["topic", "go"]}
STATUS = ["Confirmed", "Not verified", "Design risk", "Owner to decide"]
DIRECTION = ["in", "out", "both"]
NODE = ["actor", "service", "job", "tool", "store", "external", "entry"]
CARD = {"1:1": "||--||", "1:N": "||--o{", "N:1": "}o--||", "N:M": "}o--o{"}
# depth budget: over it is a WARN (a summary names the main ones; the full list lives in the Technical doc or the code)
LIMIT = {"components": 8, "flow boxes": 10, "flows": 4, "steps": 7, "participants": 6, "entities": 12, "keys": 5, "integrations": 10,
         "stack": 15, "envs": 5, "commands": 8, "risks": 7, "pointers": 10, "bullets": 8, "table rows": 12, "facts": 8, "rules": 5, "minutes": 15}
SEQ_KEY = "Solid = call · dashed = reply · numbers = steps in the table below"
WORDS, DO_WORDS, LABEL, SHORT, WPM = 40, 8, 14, 9, 200  # word cap · step `do` words · edge/relation label chars · label between neighbours · reading speed
FILLER = re.compile(r"\b(robust|seamless(?:ly)?|leverag(?:e|es|ing)|cutting[- ]edge|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|"
                    r"world[- ]class|synerg\w*|holistic|next[- ]generation|simply|basically|very|really|comprehensive|powerful|"
                    r"in order to|it is important to note|note that)\b", re.I)
CHAT = re.compile(r"\b(you|your|the user|claude|as discussed|as agreed|as requested|as asked|per (?:your )?request|"
                  r"(?:our|this) (?:conversation|chat)|asked (?:us|me)|(?:was|were) asked|confirm with|"
                  r"(?:we|i) (?:could not|couldn't|did not|didn't) (?:check|verify|confirm)|(?:was|were) skipped|we were told|in this session)\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*[a-z]{2,}", re.I)
PHONE = re.compile(r"(?<![\w-])(?:\+|00)\d{1,3}[\s./-]?(?:\(?\d{1,5}\)?[\s./-]?){2,4}\d{2,}\b")
ABS = re.compile(r"(?<![\w])[A-Za-z]:[\\/]|(?<![\w.~])/(?:Users|home|root|opt|mnt|var|srv|etc|tmp)/|(?<![\w])~/|(?<![\w.])/[a-z]/(?:Users|home)/"
                 r"|(?<![\w:])\\\\[\w.-]+\\|%\w+%[\\/]|/Workspace/Users/")
KEYS = r"[\w.-]*(?:passw(?:or)?d|pwd|secret|token|api_?key|access_?key|private_?key)[\w.-]*"
SECRET = [re.compile(rf"""(?i)\b({KEYS})["']?\s*[:=]\s*(["'])(?!<redacted>|\$\{{|\{{\{{)[^"'\n]+\2"""),
          re.compile(rf"""(?im)^[\s`>-]*(?:export\s+)?({KEYS})\s*=[ \t]*(?!<redacted>|\$|\{{|\*)[^\s"'#,;`]+"""),
          re.compile(r"(?i)\b\w+://[^\s:/@]+:(?!<redacted>|\$)([^\s@/]+)@"),
          re.compile(r"\b(dapi[0-9a-f]{32}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abp]-[\w-]{10,}|sk-[\w-]{20,})"),  # token shapes
          re.compile(r"\b(eyJ[\w-]+\.[\w-]+\.)"),  # JWT
          re.compile(r"(?i)\b(Bearer)\s+(?!<redacted>|\$)\S{8,}"),
          re.compile(r"(?i)\b(token|password|secret|key)\s*[:=]\s*(?!<redacted>|\$|\{)[^\s`\"']{6,}")]
GENERIC = {"overview", "details", "general", "summary", "introduction", "misc", "other", "items", "list", "more"}
GRAPH_DIR = re.compile(r"(?:^|/)[\w.-]*knowledge-graph/|(?:^|/)\.knowledge-graph\b")  # git-ignored by default: readers lack it
PATHLIKE = re.compile(r"^[\w.-]+(?:/[\w.*-]+)*/?(?::\d+)?$")  # one repo path, optional :line

CSS = """:root{--ground:#F6F6F3;--card:#FFF;--line:#D9DBDF;--ink:#17191D;--muted:#5B6068;--soft:#EEEFEC;--teal:#DDF0EE;--teal-ink:#1C5C57;
--amber:#FCEBC8;--amber-ink:#8A5A00;--green:#1E6B43;--blue:#1F5FA8;--lav:#E7E2F5;--lav-ink:#6B4FA8;--red:#A12D2D}
@media (prefers-color-scheme:dark){:root{--ground:#15171A;--card:#1E2125;--line:#3A3E44;--ink:#E8E9EB;--muted:#A3A8B0;--soft:#2A2D32;--teal:#1F3A38;
--teal-ink:#8FD3CC;--amber:#4A3A12;--amber-ink:#F0C060;--green:#6FCF97;--blue:#8AB4F8;--lav:#3A3150;--lav-ink:#C9B8F0;--red:#F08080}}
*{box-sizing:border-box} body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.55 "IBM Plex Sans","Segoe UI",Arial,sans-serif}
main{max-width:1104px;margin:0 auto;padding:32px 16px 56px;overflow-wrap:break-word}
h1{font-size:28px;font-weight:600;margin:4px 0 8px} h2{font-size:20px;font-weight:600;margin:0 0 10px} h3{font-size:16px;font-weight:600;margin:18px 0 4px}
section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:20px 24px;margin:18px 0}
ul{margin:6px 0;padding-left:22px} li{margin:3px 0} p{margin:6px 0}
code,pre,th,.eyebrow,.chip,.key,.stamp,.src,.badge{font-family:"IBM Plex Mono",Consolas,monospace}
code{font-size:13px;background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px}
pre{font-size:12.5px;background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:8px 10px;margin:0;overflow-x:auto;white-space:pre}
.eyebrow{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)} .stamp,.src{font-size:12px;color:var(--muted)}
.toc{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin:8px 0 0} .toc a{color:var(--blue)} a{color:inherit}
.lead{margin:4px 0 8px} .line,.why{color:var(--muted)}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:14px} th,td{text-align:left;vertical-align:top;padding:7px 10px;border:1px solid var(--line)}
th{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);background:var(--soft)}
.facts{display:grid;grid-template-columns:max-content 1fr;gap:5px 18px;margin:8px 0}
.facts dt{font:12px/1.6 "IBM Plex Mono",Consolas,monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.04em} .facts dd{margin:0}
.scope{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:10px 0} .scope div{border:1px solid var(--line);border-radius:6px;padding:8px 12px}
.scope h4{margin:0;font:600 11px/1.6 "IBM Plex Mono",Consolas,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.chip{display:inline-block;font-size:10.5px;font-weight:600;letter-spacing:.04em;padding:0 6px;border-radius:4px;border:1px solid;white-space:nowrap}
.chip.ok{color:var(--green);border-color:var(--green)} .chip.nv{color:var(--amber-ink);border-color:var(--amber-ink);background:var(--amber)}
.chip.dr{color:var(--blue);border-color:var(--blue)} .chip.od{color:var(--lav-ink);border-color:var(--lav-ink);background:var(--lav)}
.badge{font-size:10px;font-weight:600;color:var(--teal-ink)} .alt{color:var(--red);font-size:13px}
.io{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin:8px 0} .io b{display:block;font:600 11px/1.8 "IBM Plex Mono",Consolas,monospace;color:var(--muted)}
.dg{overflow-x:auto;margin:10px 0 0} .dg svg{display:block;max-width:100%;height:auto} .key{font-size:12px;color:var(--muted);margin:4px 0 0}
.dg text{fill:var(--ink);font:12px "IBM Plex Sans","Segoe UI",Arial,sans-serif} .dg .t{font-weight:600}
.dg .s,.dg .lbl,.dg .lanet,.dg .k{fill:var(--muted);font:11px "IBM Plex Mono",Consolas,monospace} .dg .tag{fill:var(--muted);font:9.5px "IBM Plex Mono",Consolas,monospace;letter-spacing:.08em}
.dg .box{fill:var(--card);stroke:var(--ink)} .dg .store{fill:var(--soft)} .dg .job,.dg .tool{fill:var(--teal);stroke:var(--teal-ink)} .dg .actor{fill:var(--lav);stroke:var(--lav-ink)}
.dg .external{stroke-dasharray:5 4;stroke:var(--muted)} .dg .entry{stroke-width:2.2} .dg .lane{fill:var(--soft)} .dg .bg{fill:var(--card)}
.dg .ent{fill:var(--card);stroke:var(--ink)} .dg .enth{fill:var(--soft);stroke:none}
.dg line,.dg polyline,.dg path.e{stroke:var(--ink);fill:none;stroke-width:1.2} .dg .dashed{stroke-dasharray:5 4} .dg .ar{fill:var(--ink)} .dg .life{stroke:var(--line);stroke-dasharray:4 4}
.scroll{overflow-x:auto}
@media (max-width:720px){section{padding:14px 12px} .scope,.io{grid-template-columns:minmax(0,1fr)} .facts{grid-template-columns:1fr;gap:2px} .facts dd{margin:0 0 6px} .dg svg{min-width:640px}
table.tt,.tt tbody,.tt tr,.tt td{display:block;width:100%} .tt tr:first-child{display:none} .tt tr{margin:0 0 8px;border:1px solid var(--line);border-radius:4px}
.tt td{border:0;border-bottom:1px solid var(--line);padding:5px 8px} .tt td:empty{display:none}
.tt td::before{content:attr(data-h);display:block;font:600 10px/1.6 "IBM Plex Mono",Consolas,monospace;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}}
@media print{body{background:#fff;font-size:12.5px} main{max-width:none;padding:0} section{border:0;padding:0 0 8px} .toc{display:none}
.dg,table,h3,.facts,.io{break-inside:avoid} h2,h3{break-after:avoid}}"""


def esc(t):
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(str(t)))
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def plain(t):
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", str(t).replace("`", ""))


def strings(x, where="spec"):
    if isinstance(x, str):
        yield where, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f"{where}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f"{where}[{i}]")


def blocks_of(sec):
    for b in sec.get("blocks") or []:
        yield {}, b
    for sub in sec.get("subsections") or []:
        for b in sub.get("blocks") or []:
            yield sub, b


def all_blocks(spec, kind=None):
    for name, sec in (spec.get("sections") or {}).items():
        if isinstance(sec, dict):
            for sub, b in blocks_of(sec):
                if kind is None or b.get("type") == kind:
                    yield name, sub, b


def rows(b, key="rows"):
    return b.get(key) or []


def cited(b):
    """Rows of a block that may cite repo paths (`where`, `pinned_in`, `go`)."""
    return (b.get("steps") or []) if b.get("type") == "seq" else rows(b) if b.get("type") in FIELDS or b.get("type") == "rules" else []


def is_code(where):
    """Example payloads and commands are code: no word cap, filler or repeat checks (paths, secrets and PII still are)."""
    return bool(re.search(r"\.example\.(in|out)$|\.(in|out)$|\.cmd$|\.expect$", where))


def check(spec, root):
    err, warn = [], []
    for k in ("title", "date", "sections"):
        if not spec.get(k):
            err.append(f"spec needs {k}")
    secs = spec.get("sections") or {}
    for s in SECTIONS:
        if s not in secs:
            err.append(f"section '{s}' missing: every tech summary has the {len(SECTIONS)} fixed sections (one `line` when there is nothing to say)")
    for s in secs:
        if s not in SECTIONS:
            err.append(f"section '{s}' unknown: the top level is fixed, put it in one of: {', '.join(SECTIONS)}")
    for name, sec in secs.items():
        if not isinstance(sec, dict) or not (sec.get("line") or sec.get("blocks") or sec.get("subsections")):
            err.append(f"section '{name}': give `line`, `blocks` or `subsections` [{{title, blocks}}]")
            continue
        if sec.get("line"):
            if sec.get("blocks") or sec.get("subsections"):
                err.append(f"section '{name}': `line` or blocks/subsections, not both")
            if name in CORE:
                warn.append(f"section '{name}' is one line: this section carries the summary, fill it")
            continue
        for i, sub in enumerate(sec.get("subsections") or []):
            if not sub.get("title") or not sub.get("blocks"):
                err.append(f"section '{name}' subsection {i + 1}: needs title and blocks")
            elif sub["title"].strip().lower() in GENERIC | {name.lower()}:
                warn.append(f"section '{name}' subsection '{sub['title']}' fits any repo: name it from the repo, or use the section's `blocks`")
        types = {b.get("type") for _, b in blocks_of(sec)}
        for t in types - BLOCKS:
            err.append(f"section '{name}': block type '{t}' unknown ({', '.join(sorted(BLOCKS))})")
        for t in NEEDS.get(name, []):
            if t not in types:
                err.append(f"section '{name}': needs a `{t}` block (or the whole section as one `line`)")
    if err:
        return err, warn

    for t, need in FIELDS.items():
        for name, sub, b in all_blocks(spec, t):
            for r in rows(b):
                miss = [k for k in need if not r.get(k)]
                if miss:
                    err.append(f"{name}: {t} row {r.get(need[0])!r} needs {', '.join(miss)}")
            if len(rows(b)) > LIMIT[t]:
                warn.append(f"{name}: {len(rows(b))} {t} rows, budget {LIMIT[t]}: keep the main ones, point to the Technical doc for the rest")
    for name, sub, b in all_blocks(spec, "risks"):
        for r in rows(b):
            if r.get("status") and r["status"] not in STATUS:
                err.append(f"{name}: risk {r.get('risk')!r} status '{r['status']}' not in {STATUS}")
    for name, sub, b in all_blocks(spec, "integrations"):
        for r in rows(b):
            if r.get("direction") and r["direction"] not in DIRECTION:
                err.append(f"{name}: integration {r.get('system')!r} direction '{r['direction']}' not in {DIRECTION}")
    comps = [r for _, _, b in all_blocks(spec, "components") for r in rows(b)]
    files = [r for r in comps if r.get("kind") not in ("job", "script") and re.search(r"\.\w{1,5}(?::\d+)?$", str(r.get("where", "")))]
    if comps and len(files) * 2 > len(comps):
        warn.append(f"Components: {len(files)} of {len(comps)} components are single files: a component is a module, service or folder (a single file is fine for kind job or script)")
    names = {plain(r.get("name", "")).lower() for r in comps} | {plain(r.get("system", "")).lower() for _, _, b in all_blocks(spec, "integrations") for r in rows(b)}

    boxes = {plain(n.get("label", "")).lower() for _, _, b in all_blocks(spec, "flow") for n in b.get("nodes") or []}
    flows = 0
    for name, sub, b in all_blocks(spec):
        t, w = b["type"], f"{name}: {b['type']} '{b.get('title', '')}'"
        if t in ("flow", "seq", "er"):
            if not b.get("title"):
                err.append(f"{name}: {t} needs a title")
            if not b.get("key") and t != "seq":  # sequence diagrams get the fixed key SEQ_KEY
                warn.append(f"{w}: no key (one-line legend)")
        if t == "flow":
            ids = {}
            for n in b.get("nodes") or []:
                if not n.get("id") or not n.get("label") or not isinstance(n.get("col"), int) or not isinstance(n.get("row"), int):
                    err.append(f"{w}: box {n!r} needs id, label, col, row")
                elif n["id"] in ids or (n["col"], n["row"]) in {(m["col"], m["row"]) for m in ids.values()}:
                    err.append(f"{w}: box {n['id']} repeats an id or a grid cell")
                else:
                    ids[n["id"]] = n
                if n.get("kind", "service") not in NODE:
                    err.append(f"{w}: box kind '{n.get('kind')}' unknown ({', '.join(NODE)})")
            if len(ids) < 3:
                err.append(f"{w}: fewer than 3 boxes, write it as bullets")
            if len(ids) > LIMIT["flow boxes"]:
                warn.append(f"{w}: {len(ids)} boxes, budget {LIMIT['flow boxes']}: group boxes (one per module or service)")
            for e in b.get("edges") or []:
                if e.get("from") not in ids or e.get("to") not in ids:
                    err.append(f"{w}: edge {e!r} names an unknown box")
                elif len(e.get("label") or "") > LABEL:
                    warn.append(f"{w}: edge label '{e['label']}' over {LABEL} characters")
                elif (ids[e["from"]]["row"] == ids[e["to"]]["row"] and abs(ids[e["from"]]["col"] - ids[e["to"]]["col"]) == 1
                      and len(e.get("label") or "") > SHORT):
                    warn.append(f"{w}: edge label '{e['label']}' between neighbours over {SHORT} characters (the gap is narrow)")
            lanes = b.get("lanes") or []
            if lanes and ids and len(lanes) <= max(n["row"] for n in ids.values()):
                err.append(f"{w}: one lane per row ({len(lanes)} lanes)")
        if t == "seq":
            flows += 1
            parts = [p.get("id") for p in b.get("participants") or []]
            if len(parts) < 2 or not all(p.get("id") and p.get("label") for p in b.get("participants") or []):
                err.append(f"{w}: needs 2+ participants, each {{id, label}}")
            if len(parts) > LIMIT["participants"]:
                warn.append(f"{w}: {len(parts)} participants, budget {LIMIT['participants']}: merge the plumbing ones")
            for p in b.get("participants") or []:
                if names and plain(p.get("label", "")).lower() not in names | boxes:
                    warn.append(f"{w}: participant '{p.get('label')}' is no component, integration or diagram box")
            steps = b.get("steps") or []
            if not steps:
                err.append(f"{w}: no steps")
            if len(steps) > LIMIT["steps"]:
                warn.append(f"{w}: {len(steps)} steps, budget {LIMIT['steps']}: merge plumbing into the step that produces data")
            for i, s in enumerate(steps, 1):
                if s.get("from") not in parts or s.get("to") not in parts or not s.get("do") or not s.get("out"):
                    err.append(f"{w}: step {i} needs from, to (participant ids), do, out")
                elif len(plain(s["do"]).split()) > DO_WORDS:
                    warn.append(f"{w}: step {i} `do` over {DO_WORDS} words, move detail to `out`")
            ex = b.get("example")
            if ex is not None and (not ex.get("in") or not ex.get("out") or not ex.get("source")):
                err.append(f"{w}: example needs in, out and source")
        if t == "er":
            ents = {e.get("id"): e for e in b.get("entities") or []}
            if any(not e.get("id") or not e.get("name") for e in ents.values()):
                err.append(f"{w}: every entity needs id and name")
            if len(ents) > LIMIT["entities"]:
                warn.append(f"{w}: {len(ents)} entities, budget {LIMIT['entities']}: keep the core ones, name the rest in a bullet")
            for e in ents.values():
                if len(e.get("keys") or []) > LIMIT["keys"]:
                    warn.append(f"{w}: entity {e.get('name')} lists {len(e['keys'])} columns, budget {LIMIT['keys']}: keys only, `more` for the count")
            for r in b.get("rels") or []:
                if r.get("a") not in ents or r.get("b") not in ents or r.get("card") not in CARD or not r.get("on"):
                    err.append(f"{w}: relation {r!r} needs a, b (entity ids), card in {list(CARD)}, on")
                elif len(r["on"]) > LABEL:
                    warn.append(f"{w}: relation label '{r['on']}' over {LABEL} characters")
        if t == "example" and not (b.get("title") and b.get("in") and b.get("out") and b.get("source")):
            err.append(f"{name}: example needs title, in, out, source")
        if t == "scope":
            for k in ("does", "doesnt"):
                if not 1 <= len(b.get(k) or []) <= 5:
                    err.append(f"{name}: scope `{k}` needs 1-5 items")
            if len(b.get("limits") or []) > 5:
                warn.append(f"{name}: scope lists {len(b['limits'])} limitations, keep the real ones (≤5)")
        if t == "table":
            if not b.get("head") or any(len(r) != len(b["head"]) for r in rows(b)):
                err.append(f"{name}: table head and rows of the same length")
            elif len(rows(b)) > LIMIT["table rows"]:
                warn.append(f"{name}: table '{b.get('title', '')}' has {len(rows(b))} rows, budget {LIMIT['table rows']}: full lists belong in the Technical doc")
            if any(re.search(r"\bdefaults?\b", str(h), re.I) for h in b.get("head") or []):
                warn.append(f"{name}: a settings table with defaults is Technical-doc depth: name the few settings that matter in bullets")
        if t == "facts" and any(len(r) != 2 for r in rows(b)):
            err.append(f"{name}: facts rows are [label, value]")
        elif t == "facts" and len(rows(b)) > LIMIT["facts"]:
            warn.append(f"{name}: {len(rows(b))} facts, budget {LIMIT['facts']}")
        if t == "rules":
            for r in rows(b):
                if not r.get("rule") or not re.search(r":\d+$", str(r.get("where", ""))):
                    err.append(f"{name}: rules row {r.get('rule')!r} needs rule and where (path:line)")
            if len(rows(b)) > LIMIT["rules"]:
                warn.append(f"{name}: {len(rows(b))} rules, budget {LIMIT['rules']}: keep the ones that change behaviour most")
        if t == "bullets":
            if not b.get("items"):
                err.append(f"{name}: bullets need items")
            elif len(b["items"]) > LIMIT["bullets"]:
                warn.append(f"{name}: {len(b['items'])} bullets, budget {LIMIT['bullets']}")
        if t == "text" and not b.get("text"):
            err.append(f"{name}: text missing")
    if flows > LIMIT["flows"]:
        warn.append(f"Main flows: {flows} flows, budget {LIMIT['flows']}: keep the ones a new engineer meets first")
    for r in comps:
        if boxes and plain(r.get("name", "")).lower() not in boxes:
            warn.append(f"Components: '{r.get('name')}' is no box in a flow diagram (same label)")

    if (root / ".git").exists():  # run from a repo root: every path the summary cites must exist
        for name, sub, b in all_blocks(spec):
            for r in cited(b):
                for k in ("where", "pinned_in", "go"):
                    p = (plain(r.get(k, "")).split() or [""])[0].split("#")[0].rstrip(",")
                    if not (PATHLIKE.match(p) and ("/" in p or re.search(r"\.\w+(?::\d+)?$", p))):
                        continue
                    f, line = re.match(r"(.*?)(?::(\d+))?$", p).groups()
                    if not (root / f).exists():
                        warn.append(f"{name}: path '{p}' not found from the repo root")
                    elif line and (root / f).is_file() and int(line) > len((root / f).read_text(encoding="utf-8", errors="ignore").splitlines()):
                        warn.append(f"{name}: '{p}': the file has fewer lines")
    for name, sub, b in all_blocks(spec):
        for r in cited(b):
            for k in ("where", "go"):
                if GRAPH_DIR.search(plain(r.get(k, ""))):
                    warn.append(f"{name}: '{r[k]}' points into the knowledge graph folder, git-ignored by default: point to code or committed docs")
    g = re.search(r"\b[0-9a-f]{7,40}\b", spec.get("graph") or "")
    if g and spec.get("commit") and not (g[0].startswith(spec["commit"]) or spec["commit"].startswith(g[0])):
        warn.append(f"graph {g[0]} is not commit {spec['commit']}: the graph is behind, recount every number from the code")
    seen = {}
    for where, s in strings(spec):
        if "TODO" in s:
            err.append(f"{where}: TODO left")
        if ABS.search(s):
            err.append(f"{where}: absolute or machine path; paths are relative to the repo root")
        if EMAIL.search(s) or any(len(re.sub(r"\D", "", m[0])) >= 7 for m in PHONE.finditer(s)):
            err.append(f"{where}: e-mail address or phone number: no personal data, name the role")
        for rx in SECRET:
            if (m := rx.search(s)):
                err.append(f"{where}: likely secret value for '{m[1]}' (write <redacted>)")
                break
        if is_code(where):
            continue
        if (m := CHAT.search(s)):
            warn.append(f"{where}: voice: '{m[0]}': write as the owner, open points as facts")
        if (m := FILLER.search(s)):
            warn.append(f"{where}: filler: '{m[0]}'")
        if len(plain(s).split()) > WORDS:
            warn.append(f"{where}: {len(plain(s).split())} words, cap {WORDS}: split or cut")
        for sent in re.split(r"(?<=[.!?])\s+", plain(s)):
            k = sent.strip().lower()
            if len(k.split()) >= 6:
                if k in seen and seen[k] != where:
                    warn.append(f"{where}: repeat: '{sent.strip()[:60]}' also in {seen[k]}")
                seen.setdefault(k, where)
    if minutes(spec) > LIMIT["minutes"]:
        warn.append(f"reading time ~{minutes(spec)} min, budget {LIMIT['minutes']}: cut detail, point to the Technical doc")
    return err, warn


def minutes(spec):
    """Reading time: prose words at WPM plus half a minute per diagram (code and payloads are skimmed, not counted)."""
    words = sum(len(plain(s).split()) for w, s in strings(spec.get("sections")) if not is_code(w))
    diagrams = sum(1 for _, _, b in all_blocks(spec) if b["type"] in ("flow", "seq", "er"))
    return round(words / WPM + diagrams * 0.5)


# ---- SVG ----------------------------------------------------------------------------------------------------------
CH = 6.6  # px per character at 12px


def wrap(text, width, lines, warn, where):
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


def label_bg(x, y, t, cls="lbl", anchor="middle"):
    w = len(t) * CH + 6
    x0 = x - w / 2 if anchor == "middle" else x - 3
    return f'<rect class="bg" x="{x0:.0f}" y="{y - 11}" width="{w:.0f}" height="14" rx="2"/>' + tx(x, y, t, cls, anchor)


def svg(w, h, body, title):
    return (f'<div class="dg"><svg viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{html.escape(title)}">'
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5 0 10z" class="ar"/></marker></defs>' + body + "</svg></div>")


def svg_flow(d, warn, where):
    """Boxes on a grid: same row → right/left arrow (over the row when a box sits between); other rows → elbow through the gap."""
    W, H, GX, GY, PAD = 150, 56, 72, 34, 8
    nodes = {n["id"]: n for n in d["nodes"]}
    lanes = d.get("lanes") or []
    LW = 14 + max((len(l) for l in lanes), default=0) * CH if lanes else 0
    cols = max(n["col"] for n in nodes.values()) + 1
    nrows = max(n["row"] for n in nodes.values()) + 1
    edges = d.get("edges") or []
    over0 = any(nodes[e["from"]]["row"] == nodes[e["to"]]["row"] == 0 and abs(nodes[e["from"]]["col"] - nodes[e["to"]]["col"]) > 1 for e in edges)
    TOP = 22 if over0 else 0
    X = lambda c: PAD + LW + c * (W + GX)
    Y = lambda r: PAD + TOP + r * (H + GY)
    width, height = PAD * 2 + LW + cols * W + (cols - 1) * GX, PAD * 2 + TOP + nrows * H + (nrows - 1) * GY
    out, used = [], {}
    for r, name in enumerate(lanes):
        out.append(f'<rect class="lane" x="{PAD}" y="{Y(r) - GY / 2 + 2:.0f}" width="{width - PAD * 2}" height="{H + GY - 4}" rx="4"/>')
        out.append(tx(PAD + 7, Y(r) + 4, name.upper(), "lanet", "start"))
    sides = {}  # (box, "t"/"b") → the vertical edges using that side; their ends spread along it, ordered by the other box's column
    for i, e in enumerate(edges):
        a, b = nodes[e["from"]], nodes[e["to"]]
        if a["row"] != b["row"]:
            down = b["row"] > a["row"]
            sides.setdefault((a["id"], "b" if down else "t"), []).append((b["col"], i))
            sides.setdefault((b["id"], "t" if down else "b"), []).append((a["col"], i))
    port = {(nid, s, i): X(nodes[nid]["col"]) + W * (k + 1) / (len(v) + 1)
            for (nid, s), v in sides.items() for k, (_, i) in enumerate(sorted(v))}
    for i, e in enumerate(edges):
        a, b = nodes[e["from"]], nodes[e["to"]]
        cls = "dashed" if e.get("dashed") else ""
        if a["row"] == b["row"]:
            left, right = (a, b) if a["col"] < b["col"] else (b, a)
            between = any(n["row"] == a["row"] and left["col"] < n["col"] < right["col"] for n in nodes.values())
            if not between:
                y = Y(a["row"]) + H / 2
                x1, x2 = X(left["col"]) + W, X(right["col"])
                ends = 'marker-end="url(#ar)"' if left is a else 'marker-start="url(#ar)"'
                out.append(f'<line class="{cls}" x1="{x1}" y1="{y:.0f}" x2="{x2}" y2="{y:.0f}" {ends}/>')
                lx, ly = (x1 + x2) / 2, y - 6
            else:
                k = used[("row", a["row"])] = used.get(("row", a["row"]), 0) + 1
                ye, yt = Y(a["row"]), Y(a["row"]) - (TOP if a["row"] == 0 else GY / 2) + 6 + (k - 1) * 6
                x1, x2 = X(a["col"]) + W / 2 + (k - 1) * 8, X(b["col"]) + W / 2 - (k - 1) * 8
                out.append(f'<polyline class="{cls}" points="{x1:.0f},{ye} {x1:.0f},{yt:.0f} {x2:.0f},{yt:.0f} {x2:.0f},{ye}" marker-end="url(#ar)"/>')
                lx, ly = (x1 + x2) / 2, yt - 3
        else:
            down = b["row"] > a["row"]
            y1 = Y(a["row"]) + (H if down else 0)
            y2 = Y(b["row"]) + (0 if down else H)
            x1, x2 = port[(a["id"], "b" if down else "t", i)], port[(b["id"], "t" if down else "b", i)]
            if a["col"] == b["col"] and abs(a["row"] - b["row"]) == 1:
                x2 = x1  # neighbours in one column: one straight line
            blocked = any(n["col"] == b["col"] and min(a["row"], b["row"]) < n["row"] < max(a["row"], b["row"]) for n in nodes.values())
            if blocked:  # run down the column gap beside the boxes in the way
                k = used[("col", b["col"])] = used.get(("col", b["col"]), 0) + 1
                xg = X(b["col"]) + W + GX / 2 + (k - 1) * 8
                ym1, ym2 = y1 + (GY / 2 if down else -GY / 2), y2 + (-GY / 2 if down else GY / 2)
                pts = f"{x1:.0f},{y1} {x1:.0f},{ym1:.0f} {xg:.0f},{ym1:.0f} {xg:.0f},{ym2:.0f} {x2:.0f},{ym2:.0f} {x2:.0f},{y2}"
                lx, ly = xg, (ym1 + ym2) / 2
            else:
                ym = (y1 + y2) / 2 if abs(b["row"] - a["row"]) == 1 else y2 + (-GY / 2 if down else GY / 2)
                pts = f"{x1:.0f},{y1} {x1:.0f},{ym:.0f} {x2:.0f},{ym:.0f} {x2:.0f},{y2}"
                lx, ly = ((x1 + x2) / 2, ym - 4) if x1 != x2 else (x1 + 6 + len(e.get("label") or "") * CH / 2, ym + 4)
            out.append(f'<polyline class="{cls}" points="{pts}" marker-end="url(#ar)"/>')
        if e.get("label"):
            out.append(label_bg(lx, ly, e["label"]))
    for n in nodes.values():
        x, y, kind = X(n["col"]), Y(n["row"]), n.get("kind", "service")
        out.append(f'<g class="n"><rect class="box {kind}" x="{x}" y="{y}" width="{W}" height="{H}" rx="{20 if kind == "actor" else 6}"/>')
        lines = wrap(n["label"], 21, 2, warn, where)
        sub = wrap(n["sub"], 22, 1, warn, where) if n.get("sub") else []
        top = y + H / 2 - (len(lines) + len(sub)) * 7.5 + 11
        for k, l in enumerate(lines):
            out.append(tx(x + W / 2, top + k * 15, l, "t"))
        for k, l in enumerate(sub):
            out.append(tx(x + W / 2, top + len(lines) * 15 + k * 14 - 1, l, "s"))
        if n.get("tag"):
            out.append(tx(x + W - 6, y + 11, n["tag"].upper(), "tag", "end"))
        out.append("</g>")
    return svg(width, height, "".join(out), d["title"])


def svg_seq(d, warn, where):
    """Sequence diagram: participants as columns, numbered messages top to bottom; `back` = dashed reply."""
    CW, BW, BH, PAD, RH = 160, 140, 40, 8, 34
    parts = [p["id"] for p in d["participants"]]
    X = lambda pid: PAD + parts.index(pid) * CW + BW / 2
    steps = d["steps"]
    y0 = PAD + BH + 26
    height = y0 + len(steps) * RH + 4
    out, right = [], PAD * 2 + (len(parts) - 1) * CW + BW
    for p in d["participants"]:
        x = X(p["id"])
        out.append(f'<line class="life" x1="{x:.0f}" y1="{PAD + BH}" x2="{x:.0f}" y2="{height - 4}"/>')
        out.append(f'<g class="n"><rect class="box {p.get("kind", "service")}" x="{x - BW / 2:.0f}" y="{PAD}" width="{BW}" height="{BH}" rx="{16 if p.get("kind") == "actor" else 6}"/>')
        lines = wrap(p["label"], 20, 2, warn, where)
        out.append("".join(tx(x, PAD + BH / 2 + 4 - (len(lines) - 1) * 7.5 + k * 15, l, "t") for k, l in enumerate(lines)) + "</g>")
    for i, s in enumerate(steps, 1):
        y, x1, x2 = y0 + (i - 1) * RH + 12, X(s["from"]), X(s["to"])
        cls = "dashed" if s.get("back") else ""
        text = f"{i} {plain(s['do'])}"
        if x1 == x2:  # call to itself
            out.append(f'<polyline class="{cls}" points="{x1:.0f},{y - 6} {x1 + 26:.0f},{y - 6} {x1 + 26:.0f},{y + 6} {x1 + 2:.0f},{y + 6}" marker-end="url(#ar)"/>')
            out.append(label_bg(x1 + 32, y + 4, text, "lbl", "start"))
            right = max(right, x1 + 36 + len(text) * CH)
        else:
            out.append(f'<line class="{cls}" x1="{x1:.0f}" y1="{y + 6}" x2="{x2:.0f}" y2="{y + 6}" marker-end="url(#ar)"/>')
            lx = min(x1, x2) + 8
            out.append(label_bg(lx, y, text, "lbl", "start"))
            right = max(right, lx + len(text) * CH + 6)
    return svg(right + PAD, height, "".join(out), d["title"])


def svg_er(d, warn, where):
    """Entity cards in rows of up to 4; relations between neighbours are straight, others run through the gaps."""
    W, HH, LH, GX, GY, PAD, BUS = 160, 26, 16, 110, 56, 8, 18
    ents = d["entities"]
    per = min(4, len(ents))
    hs = [HH + LH * (len(e.get("keys") or []) + (1 if e.get("more") else 0)) + 10 for e in ents]
    nrows = -(-len(ents) // per)
    rh = [max(hs[r * per:(r + 1) * per]) for r in range(nrows)]
    at = {e["id"]: divmod(i, per) for i, e in enumerate(ents)}
    rels = d.get("rels") or []
    bus = {}
    for r in rels:
        (ra, ca), (rb, cb) = at[r["a"]], at[r["b"]]
        if ra == rb and abs(ca - cb) > 1:
            bus[ra] = bus.get(ra, 0) + BUS
        if abs(ra - rb) > 1:
            warn.append(f"{where}: relation {r['a']}-{r['b']} skips a row: order entities so related ones are neighbours")
    top = [PAD + sum(rh[:r]) + r * GY + sum(bus.get(k, 0) for k in range(r)) for r in range(nrows)]
    pos = {e["id"]: (PAD + at[e["id"]][1] * (W + GX), top[at[e["id"]][0]], hs[i]) for i, e in enumerate(ents)}
    out, used = [], {}
    for r in rels:
        (ax, ay, ah), (bx, by, bh) = pos[r["a"]], pos[r["b"]]
        (ra, ca), (rb, cb) = at[r["a"]], at[r["b"]]
        cls = "dashed" if r.get("logical") else ""
        end_a, end_b = r["card"].split(":")  # printed next to each entity
        if ra == rb and abs(ca - cb) == 1:
            lx, rx = (ax + W, bx) if ca < cb else (bx + W, ax)
            y = ay + HH / 2 + 4
            out.append(f'<line class="{cls}" x1="{lx}" y1="{y:.0f}" x2="{rx}" y2="{y:.0f}"/>')
            left, right = (end_a, end_b) if ca < cb else (end_b, end_a)
            out.append(tx(lx + 5, y - 5, left, "k", "start") + tx(rx - 5, y - 5, right, "k", "end") + label_bg((lx + rx) / 2, y + 15, r["on"]))
        elif ra == rb:
            k = used[ra] = used.get(ra, 0) + 1
            yb = top[ra] + rh[ra] + k * BUS - 4
            x1, x2 = ax + W / 2, bx + W / 2
            out.append(f'<polyline class="{cls}" points="{x1:.0f},{ay + ah} {x1:.0f},{yb} {x2:.0f},{yb} {x2:.0f},{by + bh}"/>')
            out.append(tx(x1 + 5, ay + ah + 13, end_a, "k", "start") + tx(x2 + 5, by + bh + 13, end_b, "k", "start"))
            out.append(label_bg((x1 + x2) / 2, yb - 3, f"on {r['on']}"))
        else:
            (ux, uy, uh, ur), (lx_, ly_) = ((ax, ay, ah, ra), (bx, by)) if ra < rb else ((bx, by, bh, rb), (ax, ay))
            x1, x2 = ux + W / 2, lx_ + W / 2 + (8 if ux != lx_ else 0)
            ym = top[ur] + rh[ur] + bus.get(ur, 0) + GY / 2
            out.append(f'<polyline class="{cls}" points="{x1:.0f},{uy + uh} {x1:.0f},{ym:.0f} {x2:.0f},{ym:.0f} {x2:.0f},{ly_}"/>')
            up_end, low_end = (end_a, end_b) if ra < rb else (end_b, end_a)
            out.append(tx(x1 + 5, uy + uh + 13, up_end, "k", "start") + tx(x2 + 5, ly_ - 5, low_end, "k", "start"))
            t_ = f"on {r['on']}"  # over the horizontal run when it is long enough, else beside the vertical one
            fits = abs(x1 - x2) > len(t_) * CH + 12
            out.append(label_bg((x1 + x2) / 2, ym - 4, t_) if fits else label_bg(x2 + 4, (ym + ly_) / 2 + 4, t_, "lbl", "start"))
    for e in ents:
        x, y, h = pos[e["id"]]
        out.append(f'<g class="n"><rect class="ent" x="{x}" y="{y}" width="{W}" height="{h}" rx="6"/>'
                   f'<rect class="enth" x="{x + 1}" y="{y + 1}" width="{W - 2}" height="{HH - 1}" rx="5"/>')
        out.append(tx(x + 10, y + 17, wrap(e["name"], 22, 1, warn, where)[0], "t", "start"))
        lines = list(e.get("keys") or []) + ([f"+ {e['more']} columns"] if e.get("more") else [])
        for k, line in enumerate(lines):
            out.append(tx(x + 10, y + HH + 15 + k * LH, wrap(line, 23, 1, warn, where)[0], "k", "start"))
        out.append("</g>")
    width = PAD * 2 + per * W + (per - 1) * GX
    height = top[-1] + rh[-1] + bus.get(nrows - 1, 0) + PAD + 6
    return svg(width, height, "".join(out), d["title"])


# ---- HTML ---------------------------------------------------------------------------------------------------------
def table(head, body, cls="tt"):
    h = "".join(f"<th>{esc(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f'<td data-h="{html.escape(plain(head[i]))}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in body)
    return f'<div class="scroll"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'


def chip(status):
    cls = {"Confirmed": "ok", "Not verified": "nv", "Design risk": "dr", "Owner to decide": "od"}[status]
    return f'<span class="chip {cls}">{esc(status)}</span>'


def code(x):
    return f"<code>{html.escape(plain(x))}</code>" if x else "&ndash;"


def io(ex):
    return ('<div class="io">' + f'<div><b>IN</b><pre>{html.escape(ex["in"])}</pre></div><div><b>OUT</b><pre>{html.escape(ex["out"])}</pre></div></div>'
            + f'<p class="src">{esc(ex["source"])}</p>')


def key_line(b):
    return f'<p class="key">Key: {esc(b["key"])}</p>' if b.get("key") else ""


def block(b, warn, where):
    t = b["type"]
    if t == "text":
        return f"<p>{esc(b['text'])}</p>"
    if t == "bullets":
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ul>"
    if t == "table":
        return (f"<h3>{esc(b['title'])}</h3>" if b.get("title") else "") + table(b["head"], [[esc(c) for c in r] for r in rows(b)])
    if t == "facts":
        return '<dl class="facts">' + "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows(b)) + "</dl>"
    if t == "rules":
        return "<ul>" + "".join(f'<li>{esc(r["rule"])} <span class="src">{html.escape(r["where"])}</span></li>' for r in rows(b)) + "</ul>"
    if t == "scope":
        col = lambda h, items: f"<div><h4>{h}</h4><ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul></div>"
        return ('<div class="scope">' + col("Does", b["does"]) + col("Doesn't", b["doesnt"])
                + col("Limitations", b.get("limits") or ["No known limitations"]) + "</div>")
    if t == "flow":
        return f"<h3>{esc(b['title'])}</h3>" + svg_flow(b, warn, where) + key_line(b)
    if t == "er":
        return f"<h3>{esc(b['title'])}</h3>" + svg_er(b, warn, where) + key_line(b)
    if t == "seq":
        body = []
        for i, s in enumerate(b["steps"], 1):
            out = esc(s["out"]) + (f'<br><span class="alt">If not: {esc(s["alt"])}</span>' if s.get("alt") else "")
            body.append([str(i), esc(s["do"]), out, code(s.get("where"))])
        return (f"<h3>{esc(b['title'])}</h3>" + (f'<p class="why">{esc(b["why"])}</p>' if b.get("why") else "")
                + svg_seq(b, warn, where) + key_line({"key": b.get("key") or SEQ_KEY}) + table(["#", "Step", "Output", "Where"], body)
                + (io(b["example"]) if b.get("example") else ""))
    if t == "example":
        return f"<h3>{esc(b['title'])}</h3>" + io(b)
    if t == "components":
        return table(["Component", "Does", "Tech", "Where"], [[f"<b>{esc(r['name'])}</b>", esc(r["does"]), esc(r["tech"]), code(r["where"])] for r in rows(b)])
    if t == "integrations":
        arrow = {"in": "&larr; in", "out": "&rarr; out", "both": "&harr; both"}
        return table(["System", "Direction", "Via", "Data", "Auth"], [[f"<b>{esc(r['system'])}</b>", arrow[r["direction"]], esc(r["via"]), esc(r["data"]),
                                                                      esc(r.get("auth", "&ndash;"))] for r in rows(b)])
    if t == "stack":
        return table(["Layer", "Tech", "Version", "Pinned in"], [[esc(r["layer"]), esc(r["tech"]), code(r["version"]), code(r["pinned_in"])] for r in rows(b)])
    if t == "envs":
        return table(["Environment", "Runs on", "Deploy", "Access"], [[f"<b>{esc(r['env'])}</b>", esc(r["runs_on"]), esc(r["deploy"]), esc(r["access"])] for r in rows(b)])
    if t == "commands":
        return table(["Command", "Does", "Expect"], [[f"<pre>{html.escape(r['cmd'])}</pre>", esc(r["does"]), esc(r.get("expect", ""))] for r in rows(b)])
    if t == "risks":
        return table(["Risk", "Impact", "Status", "Mitigation", "Where"], [[esc(r["risk"]), esc(r["impact"]), chip(r["status"]), esc(r["mitigation"]),
                                                                           code(r.get("where"))] for r in rows(b)])
    if t == "pointers":
        return table(["For", "Go to", "Why"], [[esc(r["topic"]), esc(r["go"]), esc(r.get("why", ""))] for r in rows(b)])
    return ""


def stamp(spec):
    bits = [spec["date"]] + [f"{k} {spec[k]}" for k in ("commit", "graph") if spec.get(k)]
    return " &middot; ".join(esc(b) for b in bits)


def render(spec, warn):
    secs = spec["sections"]
    toc = "".join(f'<a href="#s{i}">{i} {html.escape(s)}</a>' for i, s in enumerate(SECTIONS, 1))
    out = [f'<p class="eyebrow">Tech summary &middot; ~{minutes(spec)} min read</p><h1>{esc(spec["title"])}</h1>']
    if spec.get("subtitle"):
        out.append(f'<p class="lead">{esc(spec["subtitle"])}</p>')
    out.append(f'<p class="stamp">{stamp(spec)}</p><nav class="toc">{toc}</nav>')
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
                out.append(block(b, warn, f"{name}: {b['type']} '{b.get('title', '')}'"))
        out.append("</section>")
    head = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="generator" content="{TOOL} {VERSION}"><title>{html.escape(plain(spec["title"]))}</title>'
            f"<style>{CSS}</style></head><body><main>")
    return head + "".join(out) + "</main></body></html>"


# ---- Markdown (Mermaid) -------------------------------------------------------------------------------------------
def mid(x):
    return re.sub(r"\W", "_", str(x))


def mq(x):
    return plain(x).replace('"', "'").replace("<", "&lt;")


def mdx(x):
    """Markdown text: `<` escaped outside code spans, so `<redacted>` and `<env>` stay visible."""
    return re.sub(r"(`[^`]*`)|<", lambda m: m[1] or "&lt;", str(x))


def md_table(head, body):
    cell = lambda c: mdx(c).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(cell(c) for c in r) + " |" for r in body]) + "\n"


def md_block(b):
    t = b["type"]
    if t == "text":
        return mdx(b["text"]) + "\n"
    if t == "bullets":
        return "\n".join(f"- {mdx(i)}" for i in b["items"]) + "\n"
    if t == "rules":
        return "\n".join(f"- {mdx(r['rule'])} (`{r['where']}`)" for r in rows(b)) + "\n"
    if t == "table":
        return (f"### {b['title']}\n\n" if b.get("title") else "") + md_table(b["head"], rows(b))
    if t == "facts":
        return md_table(["Fact", "Value"], rows(b))
    if t == "scope":
        return "".join(f"**{h}**\n\n" + "\n".join(f"- {mdx(i)}" for i in items) + "\n\n"
                       for h, items in (("Does", b["does"]), ("Doesn't", b["doesnt"]), ("Limitations", b.get("limits") or ["No known limitations"])))
    key = b.get("key") or (SEQ_KEY if t == "seq" else "")
    keyl = f"\nKey: {key}\n" if key else ""
    if t == "flow":
        shape = {"actor": '(["{}"])', "store": '[("{}")]', "external": '{{{{"{}"}}}}', "job": '[["{}"]]'}
        lines = ["```mermaid", "flowchart LR"]
        for n in b["nodes"]:
            lab = mq(n["label"]) + (f"<br/>{mq(n['sub'])}" if n.get("sub") else "")
            lines.append(f"  {mid(n['id'])}" + shape.get(n.get("kind"), '["{}"]').format(lab))
        for e in b.get("edges") or []:
            arrow = "-.->" if e.get("dashed") else "-->"
            lines.append(f"  {mid(e['from'])} {arrow}" + (f"|{mq(e['label'])}|" if e.get("label") else "") + f" {mid(e['to'])}")
        return f"### {b['title']}\n\n" + "\n".join(lines + ["```"]) + "\n" + keyl
    if t == "seq":
        lines = ["```mermaid", "sequenceDiagram"] + [f"  participant {mid(p['id'])} as {mq(p['label'])}" for p in b["participants"]]
        lines += [f"  {mid(s['from'])}{'-->>' if s.get('back') else '->>'}{mid(s['to'])}: {i}. {mq(s['do'])}" for i, s in enumerate(b["steps"], 1)]
        body = [[str(i), s["do"], s["out"] + (f" — If not: {s['alt']}" if s.get("alt") else ""), f"`{s['where']}`" if s.get("where") else "–"]
                for i, s in enumerate(b["steps"], 1)]
        ex = b.get("example")
        return (f"### {b['title']}\n\n" + (f"{mdx(b['why'])}\n\n" if b.get("why") else "") + "\n".join(lines + ["```"]) + "\n" + keyl + "\n"
                + md_table(["#", "Step", "Output", "Where"], body) + (md_io(ex) if ex else ""))
    if t == "example":
        return f"### {b['title']}\n\n" + md_io(b)
    if t == "er":
        names = {e["id"]: mid(e["id"]) for e in b["entities"]}
        lines = ["```mermaid", "erDiagram"]
        for e in b["entities"]:
            attrs = []
            for k in e.get("keys") or []:
                tag, _, col = k.partition(" ") if k.split(" ")[0] in ("PK", "FK", "UK") else ("", "", k)
                attrs.append(f"    key {mid(col.split(' ')[0])}" + (f" {tag}" if tag else ""))
            lines += [f'  {names[e["id"]]}["{mq(e["name"])}"] {{'] + attrs + ["  }"]
        for r in b.get("rels") or []:
            rel = CARD[r["card"]].replace("--", "..") if r.get("logical") else CARD[r["card"]]
            lines.append(f'  {names[r["a"]]} {rel} {names[r["b"]]} : "on {mq(r["on"])}"')
        keys = [[f"`{e['name']}`", ", ".join(e.get("keys") or []) + (f", + {e['more']} columns" if e.get("more") else "")] for e in b["entities"]]
        return f"### {b['title']}\n\n" + "\n".join(lines + ["```"]) + "\n" + keyl + "\n" + md_table(["Entity", "Keys"], keys)
    if t == "components":
        return md_table(["Component", "Does", "Tech", "Where"], [[f"**{r['name']}**", r["does"], r["tech"], f"`{r['where']}`"] for r in rows(b)])
    if t == "integrations":
        return md_table(["System", "Direction", "Via", "Data", "Auth"], [[r["system"], r["direction"], r["via"], r["data"], r.get("auth", "–")] for r in rows(b)])
    if t == "stack":
        return md_table(["Layer", "Tech", "Version", "Pinned in"], [[r["layer"], r["tech"], f"`{r['version']}`", f"`{r['pinned_in']}`"] for r in rows(b)])
    if t == "envs":
        return md_table(["Environment", "Runs on", "Deploy", "Access"], [[r["env"], r["runs_on"], r["deploy"], r["access"]] for r in rows(b)])
    if t == "commands":
        return md_table(["Command", "Does", "Expect"], [[f"`{r['cmd']}`", r["does"], r.get("expect", "")] for r in rows(b)])
    if t == "risks":
        return md_table(["Risk", "Impact", "Status", "Mitigation", "Where"], [[r["risk"], r["impact"], r["status"], r["mitigation"],
                                                                             f"`{r['where']}`" if r.get("where") else "–"] for r in rows(b)])
    if t == "pointers":
        return md_table(["For", "Go to", "Why"], [[r["topic"], r["go"], r.get("why", "")] for r in rows(b)])
    return ""


def md_io(ex):
    return f"\n**IN**\n\n```\n{ex['in']}\n```\n\n**OUT**\n\n```\n{ex['out']}\n```\n\n_{ex['source']}_\n"


def render_md(spec):
    out = [f"<!-- generated by {TOOL} {VERSION} -->", f"# {plain(spec['title'])}", "",
           f"Tech summary · ~{minutes(spec)} min read · " + " · ".join([spec["date"]] + [f"{k} {spec[k]}" for k in ("commit", "graph") if spec.get(k)]), ""]
    if spec.get("subtitle"):
        out += [mdx(spec["subtitle"]), ""]
    for i, name in enumerate(SECTIONS, 1):
        sec = spec["sections"][name]
        out += [f"## {i} {name}", ""]
        if sec.get("line"):
            out += [mdx(sec["line"]), ""]
            continue
        if sec.get("lead"):
            out += [mdx(sec["lead"]), ""]
        last = None
        for sub, b in blocks_of(sec):
            if sub and sub is not last:
                out += [f"### {sub['title']}", ""]
            last = sub
            out += [md_block(b)]
    return "\n".join(out)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) not in (2, 4) or (len(argv) == 4 and argv[2] != "--md"):
        sys.exit(__doc__)
    root = Path.cwd()
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    outs = [Path(argv[1])] + ([Path(argv[3])] if len(argv) == 4 else [])
    err, warn = check(spec, root)
    for o in outs:
        if not o.parent.is_dir():
            err.append(f"output folder {o.parent.as_posix()} does not exist")
    if err:
        for e in err:
            print("ERROR", e)
        sys.exit(1)
    with open(outs[0], "w", encoding="utf-8", newline="\n") as f:
        f.write(render(spec, warn))
    if len(outs) == 2:
        with open(outs[1], "w", encoding="utf-8", newline="\n") as f:
            f.write(render_md(spec))
    for o in outs:
        (o.parent / MARKER).touch()
    for w in warn:
        print("WARN", w)
    n = lambda t: sum(len(rows(b)) for _, _, b in all_blocks(spec, t))
    print(f"{n('components')} components · {sum(1 for _ in all_blocks(spec, 'seq'))} flows · "
          f"{sum(len(b.get('entities') or []) for _, _, b in all_blocks(spec, 'er'))} entities · {n('integrations')} integrations · "
          f"{n('risks')} risks · ~{minutes(spec)} min read")
    print(f"built {', '.join(o.as_posix() for o in outs)}: {len(SECTIONS)} sections, {len(warn)} WARN (templates {VERSION})")


if __name__ == "__main__":
    main(sys.argv[1:])
