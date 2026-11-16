"""Mechanical checks for a diagram review: specs (rebuilt with the engine) and the pages that embed diagrams.
Usage: python review_diagrams.py <spec.json | page.html | doc.md | folder> ... [--png DIR]
Specs: JSON with top-level `id` and `type`, a list of them, or a docs-v3 doc spec (`sections` with `diagram` blocks).
Pages: engine SVGs (`class="dg"`) are re-checked from their `data-geo` record (docs v3) or against a spec with the
same id given in the same run; the docs builder's own drawings (`aria-hidden="true"`) are left to docs `check.py`.
Prints `MUST <where> | <check> | <detail>` and `SHOULD ...` lines, then `<n> MUST, <m> SHOULD`; exit 1 on any MUST.
--png DIR renders <id>.png and <id>-dark.png per spec, for looking at. Judgement checks (right type, facts,
notation meaning) stay with the reviewer: references/checklist.md."""
import datetime
import html
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "darshan-singh-meel-diagrams" / "scripts"))
import diagram  # noqa: E402

STYLE_OF = diagram.STYLE_OF
DENSE_OK = {"gantt", "timeline", "sequence", "raci", "grid", "er", "star-schema", "decision-matrix", "swot",
            "business-model-canvas", "sipoc", "fishbone", "mind-map", "quadrant", "stakeholder-map", "funnel",
            "journey", "service-blueprint", "layers", "layered-architecture", "capability-map", "nn-block",
            "context-assembly", "org-chart", "kpi-tree"}
NAME_KEYS = {"label", "name", "text", "sub", "tag", "tech", "note"}
PLACEHOLDER = re.compile(r"\b(foo|lorem|ipsum|todo|tbd|xxx+|placeholder|dummy)\b|^(node|box|step|service|table|task|"
                         r"system|component|item|actor|entity|thing)([ _-][a-z]|[ _-]?\d+)$", re.I)
SECRET = re.compile(r"(password|passwd|pwd|secret|token|api[_-]?key)\s*[=:]\s*\S+|[a-z][a-z0-9+]*://[^/\s:@]+:[^@\s]+@|"
                    r"AKIA[0-9A-Z]{16}", re.I)
MACHINE = re.compile(r"[A-Za-z]:[\\/](Users|home)\b|/Users/[^/\s]+|/home/[^/\s]+", re.I)
MM_GRAPHS = ("flowchart", "graph", "stateDiagram-v2", "erDiagram")
TEXT_PAIRS = [("ink", "card"), ("muted", "card"), ("ink", "soft"), ("muted", "soft"), ("teal_ink", "teal"),
              ("amber_ink", "amber"), ("lav_ink", "lav"), ("green", "green_bg"), ("blue", "blue_bg"),
              ("red", "red_bg"), ("card", "green"), ("card", "blue"), ("card", "red"), ("card", "ink")]
PALETTE = {v.upper() for v in list(diagram.LIGHT.values()) + list(diagram.DARK.values())}
DONE_STATES = {"failed": "upstream_failed", "upstream_failed": "upstream_failed", "skipped": "skipped"}
OUT = []
BUILT = {}  # spec id -> the SVGs the engine builds for it, to compare with the copy on a page


def say(level, where, check, detail):
    OUT.append(f"{level} {where} | {check} | {detail}")


def strings(x, key=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v, key)
    elif isinstance(x, str):
        yield key, x


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def contrast(a, b):
    def lum(hx):
        c = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def mix(fg, bg, a):
    """Colour of fg drawn at opacity a over bg."""
    return "#" + "".join(f"{round(a * int(fg[i:i + 2], 16) + (1 - a) * int(bg[i:i + 2], 16)):02x}" for i in (1, 3, 5))


def palette():
    for mode, pal in (("light", diagram.LIGHT), ("dark", diagram.DARK)):
        for fg, bg in TEXT_PAIRS:
            if contrast(pal[fg], pal[bg]) < 4.5:
                say("MUST", "palette", f"text contrast {mode}", f"{fg} on {bg} = {contrast(pal[fg], pal[bg]):.1f}:1 < 4.5:1")
        for bg in ("card", "ground", "soft", "teal", "amber", "lav", "green_bg", "blue_bg", "red_bg"):
            fill = mix(pal[bg], pal["ground"], .4)  # a dim node: outline and fill at .4, text muted at DIM_TEXT
            if contrast(mix(pal["muted"], fill, diagram.DIM_TEXT), fill) < 3:
                say("MUST", "palette", f"dim text contrast {mode}", f"muted on faded {bg} < 3:1")
        if contrast(pal["edge"], pal["card"]) < 3:
            say("MUST", "palette", f"arrow contrast {mode}", "edge on card < 3:1")


def t_parse(s):
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", s):
        p = [int(v) for v in s.split(":")] + [0]
        return p[0] * 60 + p[1] + p[2] / 60
    return datetime.date.fromisoformat(s).toordinal()


def gantt(spec, w):
    tasks, ends = {t["id"]: t for t in spec.get("tasks", [])}, {}
    for t in tasks.values():
        if "start" not in t and not t.get("after"):
            say("MUST", w, "gantt dates", f"{t['id']} has neither start nor after")
        for a in t.get("after", []):
            if a not in tasks:
                say("MUST", w, "gantt dependency", f"{t['id']} after unknown task {a}")
    todo = [t for t in tasks.values() if all(a in tasks for a in t.get("after", []))]
    while todo:
        t = next((t for t in todo if all(a in ends for a in t.get("after", []))), None)
        if not t:
            say("MUST", w, "gantt dependency", "cycle in after: " + ", ".join(x["id"] for x in todo))
            return
        todo.remove(t)
        after = [ends[a] for a in t.get("after", [])]
        s = t_parse(t["start"]) if "start" in t else max(after, default=0)
        if after and s < max(after):
            say("MUST", w, "gantt dependency", f"{t['id']} starts before the task it waits for ends")
        if "queued" in t and t_parse(t["queued"]) > s:
            say("MUST", w, "gantt queued", f"{t['id']} queued after it started")
        e = t_parse(t["end"]) if "end" in t else s + t.get("days", t.get("minutes", 0))
        if e < s:
            say("MUST", w, "gantt dates", f"{t['id']} ends before it starts")
        ends[t["id"]] = e


def mm_colour(mm, w):
    """Mermaid classDef with a pale fill and no text colour: a dark Mermaid theme writes light text on it."""
    pale = [c for c, f, rest in re.findall(r"classDef (\S+) fill:(#[0-9A-Fa-f]{6})([^\n]*)", mm)
            if "color:" not in rest and contrast(f, "#000000") > contrast(f, "#FFFFFF")]
    if pale:
        say("SHOULD", w, "Mermaid text colour", f"classDef {', '.join(pale)}: pale fill without color: - add color:<ink>")


def frames(steps):
    for st in steps or []:
        if isinstance(st, dict) and st.get("frame"):
            yield st
            yield from frames(st.get("steps"))
            for op in st.get("else") or []:
                yield from frames(op.get("steps"))


def airflow_states(spec, w):
    """With the default trigger rule all_success, a failed upstream gives upstream_failed and a skipped one skipped."""
    tasks = {t["id"]: t for t in spec.get("tasks", []) if isinstance(t, dict) and "id" in t}
    for t in tasks.values():
        if not t.get("state") or t.get("trigger_rule", "all_success") != "all_success":
            continue
        ups = [tasks[u].get("state") for u in t.get("upstream", []) if u in tasks]
        want = next((DONE_STATES[u] for u in ("failed", "upstream_failed", "skipped") if u in ups), None)
        if want and t["state"] != want:
            why = "skipped" if want == "skipped" else "failed"
            say("MUST", w, "airflow state", f"{t['id']} is {t['state']}: an upstream {why} and the trigger rule is "
                f"all_success, so Airflow sets {want}")


def graph_checks(spec, geo, w, style):
    for lvl, check, detail in diagram.dag_check(spec, geo):
        say("MUST" if lvl == "error" else "SHOULD", w, check, detail)
    if not geo:
        return
    nodes = {n["id"]: n for n in geo["nodes"]}
    if spec["type"] not in DENSE_OK and geo["edges"]:
        member = {m for g in geo["containers"] for m in g.get("members", [])}
        inner = {g["id"] for g in geo["containers"] for h in geo["containers"]
                 if h is not g and diagram.checker._inside(g, h)}
        top = len([n for n in nodes if n not in member]) + len([g for g in geo["containers"] if g["id"] not in inner])
        if top > 9:
            say("SHOULD", w, "too many on one level", f"{top} boxes and groups > 7±2: overview plus detail")
        for g in geo["containers"]:
            if len(g.get("members", [])) > 9:
                say("SHOULD", w, "too many in one group", f"{g.get('text') or g['id']}: {len(g['members'])} > 7±2")


def spec_checks(spec, src, png_dir, ids):
    w = f"{src}#{spec.get('id', '?')}"
    r = diagram.build(spec)
    if r["html"]:
        BUILT[spec["id"]] = [m.group(0) for x in (r["svg"], r["html"]) for m in re.finditer(r"<svg\b.*?</svg>", x, re.S)]
    for e in r["errors"]:
        if not any(f"| {c} |" in e for c in ("graph not acyclic", "edge against layer order")):  # said below
            say("MUST", w, "build", e)
    for x in r["warnings"]:
        if "| direction fell back to TB |" in x:
            say("SHOULD", w, "direction fell back to TB", x.split(" | ", 2)[2])
    if not r["geometry"]:  # notation checks still run on the spec, so one defect does not hide another
        graph_checks(spec, None, w, spec.get("style") or STYLE_OF.get(spec.get("type")))
        if spec.get("type") == "gantt" and isinstance(spec.get("tasks"), list):
            gantt(spec, w)
        return
    geo, style = r["geometry"], spec.get("style") or STYLE_OF.get(spec["type"])
    if spec["id"] in ids:
        say("SHOULD", w, "id reused", f"also in {ids[spec['id']]}: two figures on one page clash")
    ids[spec["id"]] = src
    for k, s in strings(spec):
        if k in NAME_KEYS and PLACEHOLDER.search(s.strip()):
            say("MUST", w, "placeholder name", s)
        if SECRET.search(s):
            say("MUST", w, "secret in text", f"{k} = <redacted>")
        if MACHINE.search(s):
            say("MUST", w, "machine path", f"{k}: use a path relative to the repo root")
    if norm(spec["notice"]) in norm(spec["title"]):
        say("SHOULD", w, "Notice repeats title", "say the one thing to see")
    if spec.get("legend") is False and (spec.get("kinds") or spec.get("states") or style in ("dbt", "airflow")):
        say("MUST", w, "colour only signal", "legend off while colour carries kind or state")
    for e in spec.get("edges", []):
        if e.get("tone") and not (e.get("label") or e.get("kind")):
            say("SHOULD", w, "colour only signal", f"{e.get('from')} -> {e.get('to')}: tone without label or kind")
    graph_checks(spec, geo, w, style)
    if spec["type"] == "gantt":
        gantt(spec, w)
    if spec["type"] == "airflow-dag":
        airflow_states(spec, w)
    if spec["type"] == "sequence":
        for f in frames(spec.get("steps")):
            if f["frame"] == "alt" and not f.get("else"):
                say("SHOULD", w, "alt with one operand", f"{f.get('label', '')}: use opt (may happen) or break (ends the rest)")
    if spec["type"] == "quadrant":
        for a in ("x", "y"):
            if not all(spec.get(a, {}).get(k) for k in ("label", "low", "high")):
                say("SHOULD", w, "quadrant axis", f"{a} needs label, low and high")
    hexes = {h for h in re.findall(r"#[0-9A-Fa-f]{6}\b", r["svg"]) if h.upper() not in PALETTE}
    if hexes:
        say("SHOULD", w, "colour outside palette", ", ".join(sorted(hexes)))
    mm = r["mermaid"]
    if mm:
        kind, flat = re.sub(r"(?s)^---.*?---\s*", "", mm).split()[0], norm(mm)
        miss = [n["text"] for n in geo["nodes"] if kind in MM_GRAPHS and n.get("text") and not n.get("free")
                and not n["id"].startswith("_") and norm(n["text"])[:24] not in flat]
        if miss:
            say("MUST", w, "Mermaid parity", f"missing in Mermaid: {', '.join(miss[:5])}")
        if "%% Notice" not in mm:
            say("SHOULD", w, "Mermaid parity", "no Notice comment")
        mm_colour(mm, w)
    for dark in (False, True) if png_dir else ():
        out = Path(png_dir) / f"{Path(src).stem}.{spec['id']}{'-dark' if dark else ''}.png"
        err = diagram.png(r["svg"], str(out), dark)
        print(f"NOTE {w} | {err}" if err else f"PNG {out.as_posix()}")


def page_checks(path):
    s, w = path.read_text(encoding="utf-8"), path.as_posix()
    if MACHINE.search(s):
        say("MUST", w, "machine path", "use paths relative to the repo root")
    if path.suffix == ".md":
        lines = s.splitlines()
        for i, ln in enumerate(lines):
            if ln.strip().startswith("```mermaid"):
                end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == "```"), len(lines))
                if not any("notice" in x.lower() for x in lines[end + 1:end + 6]):
                    say("SHOULD", f"{w}:{i + 1}", "Notice under Mermaid", "write key and Notice as text below the block")
                mm_colour("\n".join(lines[i + 1:end]), f"{w}:{i + 1}")
        for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+\.svg)\)", s):
            if not m.group(1).startswith("http") and not (path.parent / m.group(1)).exists():
                say("MUST", w, "missing SVG file", m.group(1))
        return
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', s)
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        say("MUST", w, "duplicate id", f"{d} ({ids.count(d)}x): give each diagram its own id")
    geo_at = {}  # docs v3: <div class="dgv" data-geo="..."> holds the layout record of the svg inside it
    for m in re.finditer(r'<div class="dgv"([^>]*)>', s):
        g, did = re.search(r'data-geo="([^"]*)"', m.group(1)), re.search(r'data-id="([^"]*)"', m.group(1))
        start = s.find("<svg", m.end())
        geo_at[start] = json.loads(html.unescape(g.group(1))) if g else None
        after = re.sub(r"<[^>]+>", " ", s[s.find("</svg>", start):][:1500])
        if "Notice" not in after:
            say("SHOULD", w, "figure", f"diagram {did.group(1) if did else '?'}: Notice text missing below the frame")
    if geo_at and not re.search(r"\.dgv\s*\{[^}]*overflow-x:\s*auto", s):
        say("SHOULD", w, "figure", ".dgv frame has no overflow-x:auto: the diagram cannot scroll sideways on phones")
    for m in re.finditer(r"<svg\b(.*?)</svg>", s, re.S):
        tag, body = m.group(1).split(">", 1)[0], m.group(1)
        sid = re.search(r'(?<![\w-])id="([^"]+)"', tag)
        where = f"{w}#{sid.group(1) if sid else 'svg@' + str(m.start())}"
        if re.search(r'(href|src)="(https?:)?//', body):
            say("MUST", where, "external resource", "diagrams are static: inline everything")
        if 'aria-hidden="true"' in tag:  # docs builder's own drawing: its text is in the page, docs check.py proves it
            continue
        if "<title" not in body or ("<desc" not in body and "aria-label" not in tag):
            say("MUST", where, "accessibility", "svg needs <title> and <desc> (role=img, aria-labelledby)")
        wd = re.search(r'\bwidth="(\d+)', tag)
        if wd and int(wd.group(1)) > 1000:
            say("MUST", where, "canvas too wide", f"{wd.group(1)}px > 1000px")
        if 'class="dg"' not in tag:
            say("SHOULD", where, "not built by the engine", "no layout check proves it: rebuild from a spec")
            continue
        if geo_at.get(m.start()):
            for p, x in diagram.checker.check(geo_at[m.start()])[0]:
                say("MUST", where, f"LAYOUT {p}", x)
            continue
        sid = sid.group(1)[3:] if sid and sid.group(1).startswith("dg-") else None
        if sid not in BUILT:
            say("MUST", where, "no spec", "layout unproven: give its spec in the same run, or rebuild the figure")
        elif re.sub(r"\s+", " ", m.group(0)) not in [re.sub(r"\s+", " ", x) for x in BUILT[sid]]:
            say("MUST", where, "page SVG differs from its spec", "hand-edited or stale: rebuild the figure from the spec")
    for m in re.finditer(r'<figure class="dg-fig".*?</figure>', s, re.S):
        if "Notice" not in m.group(0) or "overflow-x:auto" not in m.group(0).replace(" ", ""):
            say("SHOULD", w, "figure", "figure needs the scroll frame, key and Notice text")


def doc_diagrams(x, h3=None):
    """docs-v3 doc spec -> engine specs of its `diagram` blocks, with the fields the docs build copies in.
    A Main flows block has no title: the build writes '<h3>, <type>'."""
    if isinstance(x, list):
        for v in x:
            if isinstance(v, dict) and v.get("type") == "h3":
                h3 = v.get("text")
            yield from doc_diagrams(v, h3)
    elif isinstance(x, dict):
        if x.get("type") == "diagram" and isinstance(x.get("spec"), dict):
            yield {**x["spec"], "id": str(x.get("id", "?")).lower(), "key": x.get("key", ""),
                   "notice": x.get("notice", ""), "title": x.get("title") or f"{h3}, {x['spec'].get('type')}"}
            return
        for v in x.values():
            yield from doc_diagrams(v, h3)


def main(argv):
    png_dir = argv[argv.index("--png") + 1] if "--png" in argv else None
    files = []
    for a in [a for i, a in enumerate(argv) if a != "--png" and (i == 0 or argv[i - 1] != "--png")]:
        p = Path(a)
        files += sorted(x for x in p.rglob("*") if x.suffix in (".json", ".html", ".md")) if p.is_dir() else [p]
    if png_dir:
        Path(png_dir).mkdir(parents=True, exist_ok=True)
    palette()
    ids = {}
    BUILT.clear()
    for f in [f for f in files if f.suffix == ".json"]:  # specs first, so pages can be compared with them
        d = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(d, dict) and "sections" in d:
            doc_ids = {}  # docs v3 ids are letters, unique within one doc only
            for spec in doc_diagrams(d):
                spec_checks(spec, f.as_posix(), png_dir, doc_ids)
            continue
        for spec in d if isinstance(d, list) else [d]:
            if isinstance(spec, dict) and "type" in spec and "id" in spec:
                spec_checks(spec, f.as_posix(), png_dir, ids)
    for f in [f for f in files if f.suffix != ".json"]:
        page_checks(f)
    for x in OUT:
        print(x)
    must = sum(x.startswith("MUST") for x in OUT)
    print(f"{must} MUST, {len(OUT) - must} SHOULD")
    return 1 if must else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
