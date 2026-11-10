"""Build one document from a JSON spec: fixed sections, one look, diagrams laid out here.

Usage: python build.py <spec.json> <out.html>   (run from the repo root: git, reviews/ and the graph are read from there)
The model writes only the spec (content, boxes, arrows, examples). Spec format: spec.md.
"""
import html
import json
import math
import re
import subprocess
import sys
from pathlib import Path

LAST = "Known issues, assumptions, and decisions needed"
ORDER = {
    "overview": ["What it is and why", "How it works", "Who uses it", "Example", "Value and cost", "Schedule",
                 "Design and operational risks", "Words used"],
    "technical": ["Overview", "Architecture", "Job DAG and schedule", "Screens and navigation", "Endpoints", "Commands",
                  "Events and messages", "Main flows", "Data model", "Business rules", "Configuration",
                  "Security and access", "Deploy and environments", "Operations", "Performance and limits", "Tests",
                  "Key decisions"],
    "user-guide": ["How it reaches you", "Screens", "What answers what", "How to *", "When data is fresh",
                   "History and deletions", "Errors and messages", "Problems and fixes", "Who to contact"],
}
REQUIRED = {  # always, then per app type
    "overview": {"*": ["What it is and why", "How it works", "Example"]},
    "technical": {"*": ["Overview", "Architecture", "Main flows", "Deploy and environments", "Operations"],
                  "pipeline": ["Job DAG and schedule", "Data model"], "ui": ["Screens and navigation"],
                  "api": ["Endpoints"], "cli": ["Commands"], "events": ["Events and messages"]},
    "user-guide": {"*": ["How it reaches you", "How to *", "Problems and fixes", "Who to contact"], "pipeline": ["What answers what", "When data is fresh"],
                   "ui": ["Screens"], "api": ["What answers what"]},
}
# Block order per section, as a regex over block types: ? optional, * any, + one or more, (a|b) either.
RECIPES = {
    "overview": {
        "What it is and why": "labels", "How it works": "flow steps?", "Who uses it": "people",
        "Example": "text? journey examples bullets?", "Value and cost": "labels", "Schedule": "schedule bullets?",
        "Design and operational risks": "bullets", "Words used": "terms",
        LAST: "text? issues assumptions? decisions?"},
    "technical": {
        "Overview": "text? flow", "Architecture": "flow components bullets?",
        "Job DAG and schedule": "flow+ schedule bullets?", "Screens and navigation": "flow+ elements bullets?",
        "Endpoints": "flow+ endpoints bullets?", "Commands": "flow+ commands bullets?",
        "Events and messages": "flow+ events bullets?",
        "Main flows": "(h3 text? steps? flow* journey? examples io* bullets?)+",
        "Data model": "text? er+ views bullets?", "Business rules": "rules examples?", "Configuration": "config bullets?",
        "Security and access": "access bullets?", "Deploy and environments": "flow? steps io* environments bullets?",
        "Operations": "io* symptoms (h3 steps io*)?", "Performance and limits": "bullets", "Tests": "tests io* bullets?",
        "Key decisions": "choices", LAST: "text? issues (h3 table)? assumptions? decisions?"},
    "user-guide": {
        "How it reaches you": "flow bullets? examples?", "Screens": "flow+ elements",
        "What answers what": "text? flow* table (h3 bullets)?", "How to *": "steps (io|examples|journey)+ bullets?",
        "When data is fresh": "flow? (schedule|table) io? bullets?", "History and deletions": "text? journey bullets? io?",
        "Errors and messages": "messages", "Problems and fixes": "problems", "Who to contact": "bullets",
        LAST: "text? issues assumptions? decisions?"},
}
H3_FIXED = {("technical", "Operations"): "Rerun and backfill", ("technical", LAST): "Unused files",
            ("user-guide", "What answers what"): "Columns every"}
TYPED = {  # builder-owned headers; the spec gives rows only
    "people": ["Who", "What they get"], "schedule": ["Environment", "Runs", "Notes"],
    "components": ["Component", "Responsibility", "Where"], "rules": ["Rule", "Input &rarr; output", "Where"],
    "config": ["Setting", "Default", "Where", "Purpose"], "access": ["Who", "Access", "How"],
    "environments": ["Environment", "Where", "How deployed"], "symptoms": ["Symptom", "Cause", "Fix"],
    "tests": ["Test", "Covers"], "choices": ["Decision", "Why"], "elements": ["Element", "What it does"],
    "endpoints": ["Endpoint", "Does", "Example"], "commands": ["Command", "Does", "Example"],
    "events": ["Event", "From &rarr; to", "Payload"], "messages": ["Message", "Means", "Do"],
    "problems": ["Problem", "What to do"], "views": ["View", "Built from", "Rows"],
    "assumptions": ["Assumption", "Why it matters"],
    "decisions": ["Decision", "Options", "Recommendation", "If it waits"],
}
TYPED_H3 = {"assumptions": "Assumptions", "decisions": "Decisions needed"}
L0_LABELS = ["What", "Why", "Key idea", "Result"]
EXAMPLE_BLOCKS = {"examples", "io", "journey"}
ISSUE_COLS = {
    "overview": [("Issue", "issue"), ("What it means", "impact"), ("Status", "status")],
    "technical": [("Issue", "issue"), ("Where", "where"), ("Impact", "impact"), ("Status", "status"), ("Suggested fix", "fix")],
    "user-guide": [("If you see", "see"), ("Do this", "do"), ("Status", "status")],
}
SEV = ["Must", "Should", "Question", "Other"]
INK, RED = "#17191D", "#A12D2D"
PAD, GX, GY = 20, 44, 44
CH = 20  # px between parallel lines, and between arrow ends on one side of a box
_ids = [0]


def uid():
    _ids[0] += 1
    return f"m{_ids[0]}"


def esc(text, wbr=False):
    """Escape; `code` -> <code>, **bold** -> <b>, [synthetic] -> badge; wbr: line-break points after _ . / - in names."""
    t = html.escape(str(text))
    if wbr:
        t = re.sub(r"([_./-])", r"\1<wbr>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("[synthetic]", '<span class="chip syn">synthetic</span>')


def status(s):
    """Badge only for review statuses; any other value (e.g. "active") stays plain text, with break points in names."""
    s = str(s)
    cls = "ok" if s.startswith("Confirmed") else "nv" if s.startswith("Not verified") else ""
    return f'<span class="chip {cls}">{esc(s)}</span>' if cls else esc(s, True)


# ---------- diagrams ----------
def die(msg):
    sys.exit(f"ERROR {msg}")


def nlines(text, per):
    """Lines the browser needs at `per` chars a line: breaks at spaces and after _ . / - (the <wbr> points);
    a longer run splits anywhere (overflow-wrap)."""
    if text is None or text == "":
        return 0
    per, n, cur = max(1, int(per)), 1, 0
    for word in str(text).split():
        for i, part in enumerate(re.findall(r"[^_./-]*[_./-]+|[^_./-]+", word)):
            need = len(part) + (1 if cur and i == 0 else 0)
            if cur + need <= per:
                cur += need
                continue
            n, cur = n + (1 if cur else 0), len(part)
            while cur > per:
                n, cur = n + 1, cur - per
    return n


def cut(t, per, most):
    """Middle ellipsis for a name that needs more than `most` lines: returns (head, tail), else the text."""
    t = str(t)
    if nlines(t, per) <= most:
        return t
    keep = int(per * most)
    while keep > 6 and nlines(t[:keep // 2] + "~" + t[len(t) - keep // 2:], per) > most:
        keep -= 2
    return t[:keep // 2], t[len(t) - keep // 2:]


def plain(v):
    return "~".join(v) if isinstance(v, tuple) else "" if v is None else str(v)


def show(v):
    return esc(v[0], True) + "&hellip;" + esc(v[1], True) if isinstance(v, tuple) else esc(v, True)


def markers(p):
    arrow = lambda i, c: (f'<marker id="{p}{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    return (f'<defs>{arrow("h", INK)}{arrow("r", RED)}'
            f'<marker id="{p}one" viewBox="0 0 12 12" refX="1" refY="6" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto">'
            f'<path d="M4,1 L4,11 M8,1 L8,11" stroke="{INK}" stroke-width="1.4"/></marker>'
            f'<marker id="{p}many" viewBox="0 0 12 12" refX="11" refY="6" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto">'
            f'<path d="M1,6 L11,1 M1,6 L11,11 M1,6 L11,6 M3,1 L3,11" stroke="{INK}" stroke-width="1.4" fill="none"/></marker></defs>')


def poly(pts, dashed=False, color=INK, end="", start=""):
    p = " ".join(f"{x},{y}" for x, y in pts)
    d = ' class="flow" stroke-dasharray="5 4"' if dashed else ""
    s = f' marker-start="url(#{start})"' if start else ""
    return (f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round"{d}{s} '
            f'marker-end="url(#{end})"/>')


# (field, px of the box width it cannot use, px per char, most lines before a middle ellipsis)
FIELDS = [("label", 22, 7.4, 4),("sub", 22, 6.6, 2), ("in", 62, 6.4, 2), ("out", 62, 6.4, 2)]


def fit(n, w):
    """Copy of a box with extreme names shortened in the middle; the full names move to the hover tip."""
    n, full = dict(n), []
    for k, inset, px, most in FIELDS:
        if n.get(k):
            v = cut(n[k], (w - inset) / px, most)
            if isinstance(v, tuple):
                full.append(str(n[k]))
            n[k] = v
    if full:
        n["tip"] = " | ".join(full + ([n["tip"]] if n.get("tip") else []))
    return n


def box_height(n, w):
    nl = lambda v, inset, px: nlines(plain(v), (w - inset) / px)
    h = 16 + (14 if n.get("tag") else 0) + 18 * nl(n["label"], 22, 7.4) + 16.5 * nl(n.get("sub"), 22, 6.6)
    h += 16 * nl(n.get("runs"), 22, 6.4)
    if n.get("bullets"):
        h += 8 + sum(16.5 * nl(b, 38, 6.6) + 2 for b in n["bullets"])
    if n.get("in") or n.get("out"):
        h += 10 + sum(max(16, 16 * nl(n[k], 62, 6.4)) + 2 for k in ("in", "out") if n.get(k))
    return max(62, math.ceil(h + (17 if n.get("see") else 0)))


def box_html(n, x, y, w, h):
    rich = n.get("bullets") or n.get("in") or n.get("out")
    inner = f'<span class="tag">{esc(n["tag"])}</span>' if n.get("tag") else ""
    inner += f'<span class="t">{show(n["label"])}</span>'
    inner += f'<span class="s">{show(n["sub"])}</span>' if n.get("sub") else ""
    inner += "<ul>" + "".join(f"<li>{esc(b, True)}</li>" for b in n["bullets"]) + "</ul>" if n.get("bullets") else ""
    inner += f'<span class="run">{esc(n["runs"], True)}</span>' if n.get("runs") else ""
    if n.get("in") or n.get("out"):
        inner += '<div class="io">' + "".join(f'<span class="l {k}">{k.upper()}</span><span>{show(n[k])}</span>'
                                              for k in ("in", "out") if n.get(k)) + "</div>"
    inner += f'<a class="see" href="#d-{esc(n["see"])}">&#9656; Diagram {esc(n["see"])}</a>' if n.get("see") else ""
    tip = f' data-tip="{html.escape(n["tip"])}" tabindex="0"' if n.get("tip") else ""
    return (f'<div class="b {html.escape(n.get("kind", ""))}{" rich" if rich else ""}"{tip} '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{inner}</div>')


def hit(a, b, pad=0):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def crosses(s, r):
    (x1, y1), (x2, y2) = s
    return hit((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), r, 2)


def starts(a, b):
    """Candidate positions between a and b, middle first."""
    if b < a:
        return []
    return sorted({round(a + (b - a) * f) for f in (0, .1, .25, .4, .5, .6, .75, .9, 1)}, key=lambda v: abs(v - (a + b) / 2))


def wrap(label):
    """A label as one line, and (2+ words) as two lines split where the longer line is shortest."""
    if not label:
        return []
    w = label.split()
    two = min(([" ".join(w[:k]), " ".join(w[k:])] for k in range(1, len(w))), key=lambda x: max(map(len, x)), default=None)
    return [[label]] + ([two] if two else [])


def lwidth(lines):
    return max(round(6.6 * len(x)) + 10 for x in lines)


def spot(segs, j, num, label, solid, marks, W, H, ends_first=False):
    """Room for line j's number and label: on a horizontal part, label above the line right of the number (else
    above the number, else on two lines); on a vertical part, beside it. Never on a box, a line, another number or
    label, or the arrowhead. Returns [(kind, rect, label lines)] or None."""
    others = [s for k, ss in enumerate(segs) if k != j for s in ss]
    nw, sep = (20, 6) if num else (0, 0)
    first, last = segs[j][0], segs[j][-1]

    def ok(r, own):
        return (r[0] >= 2 and r[1] >= 2 and r[2] <= W - 2 and r[3] <= H - 2 and not any(hit(r, o, 3) for o in solid + marks)
                and not any(crosses(s, r) for s in others + [s for s in segs[j] if s is not own]))

    def span(s, a, b, start, head):
        """Free range [lo, hi] along part s: `start` px after its first point, `head` px before its last."""
        (x1, y1), (x2, y2) = s
        u1, u2 = (x1, x2) if y1 == y2 else (y1, y2)
        ga, gb = (start if s is first else a), (head if s is last else b)
        return (u1 + ga, u2 - gb) if u2 >= u1 else (u2 + gb, u1 - ga)

    length = lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1])
    # a part shared with another line (a common trunk) is tried last: a label there could belong to either line
    box = lambda s: (min(s[0][0], s[1][0]), min(s[0][1], s[1][1]), max(s[0][0], s[1][0]), max(s[0][1], s[1][1]))
    shared = lambda s: any((o[0][1] == o[1][1]) == (s[0][1] == s[1][1]) and crosses(o, box(s)) for o in others)
    order = sorted(segs[j], key=lambda s: (shared(s), s is not last if ends_first else 0, s[0][1] != s[1][1], -length(s)))
    for mode, lines in [("side", x) for x in wrap(label)[:1] or [[]]] + ([("up", x) for x in wrap(label)] if label else []):
        lw, lh = (lwidth(lines), 16 * len(lines)) if lines else (0, 0)
        for s in order:
            (x1, y1), (x2, y2) = s
            if y1 == y2:
                bw = nw + (sep + lw if lw else 0) if mode == "side" else max(nw, lw)
                lo, hi = span(s, 10, 10, 6 if num else 12, 18)
                for sx in starts(lo, hi - bw):
                    nx = sx if mode == "side" else sx + (bw - nw) // 2
                    lx, top = (sx + nw + sep, y1 - 3 - lh) if mode == "side" else (sx, y1 - (13 if num else 3) - lh)
                    got = ([("num", (nx, y1 - 10, nx + 20, y1 + 10), None)] if num else []) +                           ([("lbl", (lx, top, lx + lw, top + lh), lines)] if lw else [])
                    if all(ok(r, s) for _, r, _ in got):
                        return got
            elif mode == "side" or len(lines) > 1:  # beside a vertical part; a 2-line label is narrower
                lo, hi = span(s, 14, 14, 12, 24)
                for cy in starts(lo, hi):
                    for side in (1, -1):
                        lx = x1 + nw // 2 + 4 if side > 0 else x1 - nw // 2 - 4 - lw
                        got = ([("num", (x1 - 10, cy - 10, x1 + 10, cy + 10), None)] if num else []) +                               ([("lbl", (lx, cy - lh // 2, lx + lw, cy + lh - lh // 2), lines)] if lw else [])
                        if all(ok(r, s) for _, r, _ in got):
                            return got
    return None


def mark(what, r, lines, n):
    a, b, c, z = r
    if what == "num":
        return f'<span class="num" style="left:{a + 10}px;top:{b + 10}px">{n}</span>'
    return f'<span class="lbl" style="left:{a}px;top:{b}px;height:{z - b}px">{"<br>".join(esc(x) for x in lines)}</span>'


def route(a, b, occ, rows):
    """Simplest orthogonal path from cell a to cell b that crosses no box. Returns (kind, side at a, side at b,
    channels); a channel is ("v", gap left of column k) or ("h", gap above row k)."""
    (ac, ar), (bc, br) = a, b
    s, t = (bc > ac) - (bc < ac), (br > ar) - (br < ar)
    free = lambda cells: not set(cells) & occ
    mid = lambda u, v: range(min(u, v) + 1, max(u, v))
    h, h2 = ("r", "l") if s >= 0 else ("l", "r")
    v, v2 = ("b", "t") if t >= 0 else ("t", "b")
    ka, kb = (ac + 1, bc) if s > 0 else (ac, bc + 1)
    hb = br if t > 0 else br + 1
    if not t and free((c, ar) for c in mid(ac, bc)):
        return "H", h, h2, []
    if not s and free((ac, r) for r in mid(ar, br)):
        return "V", v, v2, []
    if s and t:
        if free([(ac, r) for r in mid(ar, br)] + [(ac, br)] + [(c, br) for c in mid(ac, bc)]):
            return "L1", v, h2, []
        if free([(c, ar) for c in mid(ac, bc)] + [(bc, ar)] + [(bc, r) for r in mid(ar, br)]):
            return "L2", h, v2, []
        if free((c, br) for c in mid(ac, bc)):
            return "Z", h, h2, [("v", ka)]
        if free((c, ar) for c in mid(ac, bc)):
            return "Z", h, h2, [("v", kb)]
        return "ZZ", h, v2, [("v", ka), ("h", hb)]
    if not s:  # same column, boxes between: up or down the gap on the right
        return "Z", "r", "r", [("v", ac + 1)]
    q = ar + 1 if ar + 1 < rows or ar == 0 else ar  # same row, boxes between: the gap below (above for the last row)
    side = "b" if q > ar else "t"
    return "U", side, side, [("h", q)]


def runs(j, rt, a, b):
    """The straight parts of arrow j that run along a row or a column line (not in a gap channel), as
    (axis, line, lo, hi, arrow ends on it). Positions are doubled: gap k = 2k, cell k = 2k + 1, box sides 2k + 0.5 / 1.5."""
    kind, sa, sb, ch = rt
    (ac, ar), (bc, br) = a, b
    side = lambda s, c, r: {"l": 2 * c + .5, "r": 2 * c + 1.5, "t": 2 * r + .5, "b": 2 * r + 1.5}[s]
    pa, pb = side(sa, ac, ar), side(sb, bc, br)
    ends = lambda *e: [(j, x) for x in e]
    if kind == "H":
        out = [("h", ar, pa, pb, ends(0, 1))]
    elif kind == "V":
        out = [("v", ac, pa, pb, ends(0, 1))]
    elif kind == "L1":
        out = [("v", ac, pa, 2 * br + 1, ends(0)), ("h", br, 2 * ac + 1, pb, ends(1))]
    elif kind == "L2":
        out = [("h", ar, pa, 2 * bc + 1, ends(0)), ("v", bc, 2 * ar + 1, pb, ends(1))]
    elif kind == "Z":
        out = [("h", ar, pa, 2 * ch[0][1], ends(0)), ("h", br, 2 * ch[0][1], pb, ends(1))]
    elif kind == "U":
        out = [("v", ac, pa, 2 * ch[0][1], ends(0)), ("v", bc, 2 * ch[0][1], pb, ends(1))]
    else:  # ZZ
        out = [("h", ar, pa, 2 * ch[0][1], ends(0)), ("v", bc, 2 * ch[1][1], pb, ends(1))]
    return [(ax, ln, min(lo, hi), max(lo, hi), e) for ax, ln, lo, hi, e in out]


def slots(edges, rt, cell):
    """Offset of each arrow end from its row or column centre line, in CH steps. Ends on one box side are ordered by
    the box at the other end (so lines don't cross) and centred; then every part along a row or column line takes the
    nearest offset that keeps it CH away from all other parts it overlaps, so no two lines lie on top of each other."""
    att = {}  # (box, side) -> arrow ends there: (edge, 0 = start / 1 = end, cell at the other end)
    for j, (e, r) in enumerate(zip(edges, rt)):
        att.setdefault((e["from"], r[1]), []).append((j, 0, cell[e["to"]]))
        att.setdefault((e["to"], r[2]), []).append((j, 1, cell[e["from"]]))
    want = {}
    for (i, s), lst in att.items():
        ax = 1 if s in "lr" else 0
        lst.sort(key=lambda a: (a[2][ax], a[2][1 - ax], a[0]))
        own = cell[i][ax]
        nb, m = sum(a[2][ax] < own for a in lst), sum(a[2][ax] == own for a in lst)
        for q, a in enumerate(lst):
            want[a[:2]] = q - nb - (m - 1) / 2 if m else q - (len(lst) - 1) / 2
    ps = [x for j, (e, r) in enumerate(zip(edges, rt)) for x in runs(j, r, cell[e["from"]], cell[e["to"]])]
    pref = [sum(want[k] for k in x[4]) / len(x[4]) for x in ps]
    off, done = {}, []
    for q in sorted(range(len(ps)), key=lambda q: (abs(pref[q]), q)):
        ax, ln, lo, hi, ends = ps[q]
        near = [o for k, o in done if ps[k][:2] == (ax, ln) and ps[k][2] <= hi and lo <= ps[k][3]]
        o = next(pref[q] + d for d in (x * sgn / 2 for x in range(40) for sgn in (1, -1)) if all(abs(pref[q] + d - n) >= 1 for n in near))
        done.append((q, o))
        off.update(dict.fromkeys(ends, o))
    spread = {}  # (axis, line) -> largest offset used on it
    for q, o in done:
        spread[ps[q][:2]] = max(spread.get(ps[q][:2], 0), abs(o))
    return off, spread


def points(kind, pa, pb, tr):
    if kind in ("H", "V"):
        return [pa, pb]
    if kind == "L1":
        return [pa, (pa[0], pb[1]), pb]
    if kind == "L2":
        return [pa, (pb[0], pa[1]), pb]
    if kind == "Z":
        return [pa, (tr[0], pa[1]), (tr[0], pb[1]), pb]
    if kind == "U":
        return [pa, (pa[0], tr[0]), (pb[0], tr[0]), pb]
    return [pa, (tr[0], pa[1]), (tr[0], tr[1]), (pb[0], tr[1]), pb]


def fan(nodes, edges, groups, did):
    """A box with more than 4 outgoing arrows: its targets move into one frame that one arrow reaches."""
    owner, frames, srcs = {}, {}, set()
    for src in nodes:
        kids = list(dict.fromkeys(e["to"] for e in edges if e["from"] == src))
        if len(kids) <= 4 or src in owner or set(kids) & (set(owner) | srcs):
            continue
        g = next((g for g in groups if set(g["nodes"]) == set(kids)), None)
        first = nodes[min(kids, key=lambda i: (nodes[i]["row"], nodes[i]["col"]))]
        fid = f"{src}-children"
        frames[fid] = {"id": fid, "frame": [nodes[i] for i in kids], "col": first["col"], "row": first["row"],
                       "label": g["label"] if g else f"{len(kids)} children"}
        owner.update(dict.fromkeys(kids, fid))
        srcs.add(src)
    if not frames:
        return nodes, edges, groups
    merged = []
    for e in edges:
        a, b = owner.get(e["from"], e["from"]), owner.get(e["to"], e["to"])
        twin = next((m for m in merged if (m["from"], m["to"]) == (a, b) and {a, b} & set(frames)), None)
        if a == b:
            continue
        if twin:
            for k in ("label", "fail", "dashed"):
                if twin.get(k) != e.get(k):
                    twin[k] = None
        else:
            merged.append(dict(e, **{"from": a, "to": b}))
    left = [g for g in groups if not set(g["nodes"]) <= set(owner)]
    mixed = [g["label"] for g in left if set(g["nodes"]) & set(owner)]
    if mixed:
        die(f"diagram {did}: group {mixed} mixes boxes inside and outside a fan-out frame")
    return {i: n for i, n in nodes.items() if i not in owner} | frames, merged, left


def frame_layout(f, w, k):
    """Fan-out frame: the children in a grid of at most k columns, no arrows between them."""
    mw = min(w, 150)
    kids, n = [fit(c, mw) for c in f["frame"]], len(f["frame"])
    k = -(-n // -(-n // k))
    rows = [kids[q:q + k] for q in range(0, n, k)]
    mh = [max(box_height(c, mw) for c in r) for r in rows]
    fw = k * mw + (k - 1) * 12 + 24
    band = 15 * nlines(f["label"], (fw - 20) / 7) + 12
    cells = [(12 + c * (mw + 12), band + sum(mh[:q]) + 12 * q, mw, mh[q], x) for q, r in enumerate(rows) for c, x in enumerate(r)]
    return fw, band + sum(mh) + 12 * len(rows), cells


def l0_size(did, cols, edges):
    """Overview: gaps sized for the longest arrow label (above its number, two lines at most), then one box width
    for that box count from what is left of the 1020 px. Below 100 px a box is too narrow: fewer boxes or labels."""
    labs = [e["label"] for e in edges if e.get("label")]
    gap = max([GX] + [max(20, lwidth(wrap(x)[-1])) + 32 for x in labs])  # + the line ends kept free
    room = lambda n: (1020 - 2 * PAD - (n - 1) * gap) // n
    if room(cols) < 100:
        most = max([n for n in range(1, cols) if room(n) >= 100], default=1)
        die(f"overview flow {did}: {cols} boxes" + (f" with arrow labels like '{max(labs, key=len)}'" if labs else "")
            + f" leave {room(cols)} px per box (min 100): use at most {most} boxes in the row, or shorter or fewer labels")
    return min(180, room(cols) // 10 * 10), gap


def flow(d, p, kind=""):
    did = d.get("id") or d.get("title") or "(no id)"
    nodes = {n["id"]: n for n in d["nodes"]}
    for n in nodes.values():
        if "col" not in n or "row" not in n:
            die(f"diagram {did}: node {n['id']} needs col and row")
    edges = d.get("edges", [])
    for e in edges:
        if e["from"] not in nodes or e["to"] not in nodes or e["from"] == e["to"]:
            die(f"diagram {did}: edge {e['from']} -> {e['to']}: unknown node or loop")
    taken = {}
    for n in nodes.values():
        if taken.setdefault((n["col"], n["row"]), n["id"]) != n["id"]:
            die(f"diagram {did}: {taken[(n['col'], n['row'])]} and {n['id']} share col {n['col']}, row {n['row']}")
    lanes = d.get("lanes", [])
    nodes, edges, groups = fan(nodes, edges, d.get("groups", []), did)
    cs = sorted({n["col"] for n in nodes.values()})  # empty columns (and rows, without lanes) are dropped
    rs = sorted({n["row"] for n in nodes.values()}) if not lanes else list(range(max([len(lanes)] + [n["row"] + 1 for n in nodes.values()])))
    cell = {i: (cs.index(n["col"]), rs.index(n["row"])) for i, n in nodes.items()}
    # box width: overview set by l0_size; else the spec's box_w, else 180 narrowed in steps until arrow labels fit
    gap = GX
    if kind == "overview":
        w0, gap = l0_size(did, len(cs), edges)
        widths = [w0]
    else:
        widths = [d["box_w"]] if "box_w" in d else range(180, 139, -10)
    for k in (4, 3, 2) if any("frame" in n for n in nodes.values()) else (4,):
        for w in widths:
            out, why = draw(d, did, p, nodes, edges, groups, lanes, cell, len(cs), len(rs), w, k, kind, gap)
            if out:
                return out
    die(why)


def draw(d, did, p, nodes, edges, groups, lanes, cell, C, R, w, k, kind, gap=GX):
    occ = set(cell.values())
    fr = {i: frame_layout(n, w, k) for i, n in nodes.items() if "frame" in n}
    bx = {i: fit(n, w) for i, n in nodes.items() if "frame" not in n}
    rt = [route(cell[e["from"]], cell[e["to"]], occ, R) for e in edges]
    off, spread = slots(edges, rt, cell)
    bh = [0] * R
    for i, n in bx.items():
        bh[cell[i][1]] = max(bh[cell[i][1]], box_height(n, w))
    bh = [max(bh[r], int(2 * spread[("h", r)] * CH + 24) if ("h", r) in spread else 0) for r in range(R)]
    rowh = [max([bh[r]] + [fr[i][1] for i in fr if cell[i][1] == r]) or 40 for r in range(R)]
    colw = [max([w if any(cell[i][0] == c for i in bx) else 0] + [fr[i][0] for i in fr if cell[i][0] == c]) for c in range(C)]
    uses = [r[3] for r in rt]
    tracks = {}
    for j, u in enumerate(uses):
        for ch in u:
            tracks.setdefault(ch, []).append(j)
    gb = []
    for g in groups:
        if any(i not in cell for i in g["nodes"]):
            die(f"diagram {did}: group '{g['label']}' names an unknown box")
        gc = [cell[i] for i in g["nodes"]]
        c0, c1, r0, r1 = min(c for c, _ in gc), max(c for c, _ in gc), min(r for _, r in gc), max(r for _, r in gc)
        extra = [i for i, (c, r) in cell.items() if c0 <= c <= c1 and r0 <= r <= r1 and i not in g["nodes"]]
        if extra:
            die(f"diagram {did}: group '{g['label']}' would enclose {extra}: move them out of its rows/columns or add them")
        lw = (c1 - c0 + 1) * w + 4  # the narrowest the frame can be, so the label always fits inside
        gb.append((g, c0, c1, r0, r1, lw, 15 * nlines(g["label"], lw / 7) + 12))
    for q, a in enumerate(gb):
        for b in gb[q + 1:]:
            if a[1] <= b[2] and b[1] <= a[2] and a[3] <= b[4] and b[3] <= a[4]:
                die(f"diagram {did}: groups '{a[0]['label']}' and '{b[0]['label']}' overlap: give them separate rows or columns")
    iL = lambda q: 12 if any(g[2] == q - 1 for g in gb) else 0
    iR = lambda q: 12 if any(g[1] == q for g in gb) else 0
    iU = lambda q: 12 if any(g[4] == q - 1 for g in gb) else 0
    iD = lambda q: max([g[6] for g in gb if g[3] == q], default=0)

    def need(ch, a, b, inner, base):
        n = len(tracks.get(ch, []))
        return max(base if inner else 0, a + b + (CH * (n + 1) if n else 16 if inner else 0))

    cg = [need(("v", q), iL(q), iR(q), 0 < q < C, gap) for q in range(C + 1)]
    rg = [need(("h", q), iU(q), iD(q), 0 < q < R, GY) for q in range(R + 1)]
    x0, num = PAD + (100 if lanes else 0), d.get("numbered", True)
    tries = {}  # arrow -> times more room was made for it
    for attempt in range(80):
        gx = [x0 + sum(cg[:q]) + sum(colw[:q]) for q in range(C + 1)]  # left / top edge of each gap
        gy = [PAD + sum(rg[:q]) + sum(rowh[:q]) for q in range(R + 1)]
        X, Y = [gx[c] + cg[c] for c in range(C)], [gy[r] + rg[r] for r in range(R)]
        W, H = gx[C] + cg[C] + PAD, gy[R] + rg[R] + PAD
        if W > 1020 and not attempt:
            c0 = next((c for c in range(C) if X[c] + colw[c] + PAD > 1020), C - 1)
            out = [i for i in nodes if cell[i][0] >= c0]
            return None, (f"diagram {did} is {W}px wide (max 1020): col {sorted({nodes[i]['col'] for i in out})} "
                          f"({', '.join(str(nodes[i]['label'])[:30] for i in out)}) does not fit: move those boxes into a "
                          f"sub-flow behind one box (see: \"B\" opens flow B)" + (", or use fewer boxes" if kind == "overview" else ""))
        rect = {}
        for i in nodes:
            c, r = cell[i]
            ww, hh = fr[i][:2] if i in fr else (w, bh[r])
            rect[i] = (X[c] + (colw[c] - ww) // 2, Y[r] + (rowh[r] - hh) // 2, ww, hh)

        def port(j, end):
            i, s = edges[j]["to" if end else "from"], rt[j][2 if end else 1]
            (x, y, ww, hh), (c, r), o = rect[i], cell[i], round(off[(j, end)] * CH)
            cy, cx = Y[r] + rowh[r] // 2 + o, X[c] + colw[c] // 2 + o
            return {"l": (x, cy), "r": (x + ww, cy), "t": (cx, y), "b": (cx, y + hh)}[s]

        def track(ch, j):
            lst, (a, q) = tracks[ch], ch
            lo, hi = (gx[q] + iL(q), gx[q] + cg[q] - iR(q)) if a == "v" else (gy[q] + iU(q), gy[q] + rg[q] - iD(q))
            return round(lo + (hi - lo) * (lst.index(j) + 1) / (len(lst) + 1))

        pts = [points(rt[j][0], port(j, 0), port(j, 1), [track(ch, j) for ch in uses[j]]) for j in range(len(edges))]
        segs = [[(a, b) for a, b in zip(q, q[1:]) if a != b] for q in pts]
        gr = []
        for g, c0, c1, r0, r1, lw, band in gb:
            rr = [rect[i] for i in g["nodes"]]
            fx, fy = min(r[0] for r in rr) - 12, min(r[1] for r in rr) - band
            gr.append((g["label"], fx, fy, max(r[0] + r[2] for r in rr) + 12 - fx, max(r[1] + r[3] for r in rr) + 12 - fy, lw, band))
        solid = [(x, y, x + ww, y + hh) for x, y, ww, hh in rect.values()] + \
                [(fx + 10, fy + 6, fx + 10 + lw, fy + band - 6) for _, fx, fy, _, _, lw, band in gr]
        marks, front, fail = [], [], None
        for j, e in enumerate(edges):
            lab = e.get("label")
            if not (num or lab):
                continue
            got = spot(segs, j, num, lab, solid, marks, W, H)
            if got is None:
                fail = j
                break
            for what, r, lines in got:
                marks.append(r)
                front.append(mark(what, r, lines, j + 1))
        if fail is None:
            break
        tries[fail] = tries.get(fail, 0) + 1
        hs = [s for s in segs[fail] if s[0][1] == s[1][1]]
        vs = [s for s in segs[fail] if s[0][0] == s[1][0]]
        wide = {q for s in hs for q in range(C + 1) if gx[q] < max(s[0][0], s[1][0]) and min(s[0][0], s[1][0]) < gx[q] + cg[q]}
        tall = {q for s in vs for q in range(R + 1) if gy[q] < max(s[0][1], s[1][1]) and min(s[0][1], s[1][1]) < gy[q] + rg[q]}
        if tries[fail] <= 8 and wide and W + 24 * len(wide) <= 1020:
            for q in wide:
                cg[q] += 24
        elif tries[fail] <= 8 and tall:
            for q in tall:
                rg[q] += 24
        else:  # more room no longer helps this arrow
            break
    if fail is not None:
        e = edges[fail]
        lab = e.get("label") or ""
        why = (f"label '{lab}' is over 3 words: shorten it" if len(lab.split()) > 3 else
               "too many lines and labels crowd the gaps around it: move those boxes apart (leave a column or row "
               "free), drop labels the text already says, or move part of the flow into a sub-flow")
        return None, (f"diagram {did}: no room for arrow {fail + 1} ({e['from']} -> {e['to']}): {why}"
                      + (", or use fewer boxes in the row" if kind == "overview" else ""))
    back, svg, boxes = [], [markers(p)], []
    for r, name in enumerate(lanes[:R]):
        top, bot = (0 if r == 0 else gy[r] + rg[r] // 2), (H if r == R - 1 else gy[r + 1] + rg[r + 1] // 2)
        back.append(f'<div class="lane" style="top:{top}px;height:{bot - top}px;width:{W}px"><span>{esc(name)}</span></div>')
    for label, fx, fy, fw, fh, lw, _ in gr:
        back.append(f'<div class="grp" style="left:{fx}px;top:{fy}px;width:{fw}px;height:{fh}px">'
                    f'<span style="width:{lw}px">{esc(label)}</span></div>')
    for i, (fw, fh, cells) in fr.items():
        x, y = rect[i][:2]
        back.append(f'<div class="grp fan" style="left:{x}px;top:{y}px;width:{fw}px;height:{fh}px">'
                    f'<span style="width:{fw - 20}px">{esc(nodes[i]["label"])}</span></div>')
        boxes += [box_html(n, x + cx, y + cy, cw, ch) for cx, cy, cw, ch, n in cells]
    for e, q in zip(edges, pts):
        fail = e.get("fail")
        svg.append(poly(q, e.get("dashed") or fail, RED if fail else INK, f"{p}{'r' if fail else 'h'}"))
    boxes += [box_html(n, *rect[i]) for i, n in bx.items()]
    return (f'<div class="map-wrap"><div class="map" style="width:{W}px;height:{H}px">{"".join(back)}'
            f'<svg width="{W}" height="{H}" aria-hidden="true">{"".join(svg)}</svg>{"".join(boxes + front)}</div></div>'), None


def er(d, p):
    """Tables by relationship tree: parents one column left of their children, so lines only join neighbours.
    A key to a table further away is written in the row ("FK -> table") instead of drawn."""
    did = d.get("id") or d.get("title") or "(data model)"
    ents = {e["id"]: e for e in d["entities"]}
    names = {i: [c[0] for c in e["cols"]] for i, e in ents.items()}
    rels = d.get("rels", [])
    for r in rels:
        if r["from"] not in ents or r["to"] not in ents or r["from_col"] not in names[r["from"]] or r["to_col"] not in names[r["to"]]:
            die(f"ER {did}: rel {r['from']}.{r['from_col']} -> {r['to']}.{r['to_col']}: unknown table or column")
    depth = {}

    def dep(i, path=()):
        if i not in depth:
            ps = [r["from"] for r in rels if r["to"] == i and r["from"] not in path + (i,)]
            depth[i] = max((dep(q, path + (i,)) + 1 for q in ps), default=0)
        return depth[i]

    for i in ents:
        dep(i)
    drawn = [r for r in rels if depth[r["to"]] - depth[r["from"]] == 1]
    notes = {}
    for r in rels:
        if r not in drawn:
            notes.setdefault((r["to"], r["to_col"]), []).append(ents[r["from"]]["name"])
    n = max(depth.values()) + 1
    cols = [[i for i in ents if depth[i] == c] for c in range(n)]
    for c in range(1, n):  # children follow their parents' order
        pr = [(cols[c - 1].index(r["from"]), r["to"]) for r in drawn if depth[r["from"]] == c - 1]
        cols[c].sort(key=lambda i: sum(a for a, b in pr if b == i) / max(1, sum(b == i for _, b in pr)))
    lines_in = [[r for r in drawn if depth[r["from"]] == c - 1] for c in range(n)]
    gaps = [0] + [max(80, CH * (len(lines_in[c]) + 1) + 40) for c in range(1, n)]

    def sizes(ew):
        size = {}
        for i, e in ents.items():
            kw = 20 + 26 * max([len((t or "").split()) for _, t in e["cols"]] + [0])
            per = ew - kw - 20
            rh = [max(22, math.ceil(16.5 * nlines(c, per / 7.4) + sum(15 * nlines(f"FK > {m}", per / 6.6) for m in notes.get((i, c), [])) + 6))
                  for c, _ in e["cols"]]
            sch = len(e.get("schema", "")) * 7.4 + 18 if e.get("schema") else 0  # tag + its 8px gap to the name
            head = math.ceil(13 + 17 * nlines(e["name"], (ew - 20 - sch) / 7.4) + 15 * nlines(e.get("grain"), (ew - 20) / 6.4))
            size[i] = (kw, rh, head, head + sum(rh) + 4)
        return size

    for attempt in range(40):  # a label that doesn't fit widens its gap; tables get narrower to stay in 1020 px
        ew = min(d.get("box_w", 260), (1020 - 2 * PAD - sum(gaps)) // n)
        if ew < 170:
            die(f"ER {did} is {n} tables deep (max 1020 px): split it into one ER per area" if not attempt else
                f"ER {did}: relationship labels do not fit in 1020 px: shorten them (e.g. 1:N) or split the ER")
        size = sizes(ew)
        X = [PAD + c * ew + sum(gaps[1:c + 1]) for c in range(n)]
        pos = {}
        for c, ids in enumerate(cols):
            y = PAD
            for i in ids:
                pos[i] = (X[c], y)
                y += size[i][3] + 30
        W, H = X[-1] + ew + PAD, max(pos[i][1] + size[i][3] for i in ents) + PAD
        row_y = lambda i, c: pos[i][1] + 1 + size[i][2] + sum(size[i][1][:names[i].index(c)]) + size[i][1][names[i].index(c)] // 2
        ends = [((X[depth[r["to"]] - 1] + ew, row_y(r["from"], r["from_col"])), (X[depth[r["to"]]], row_y(r["to"], r["to_col"])))
                for r in drawn]
        # tracks in a gap: the line that turns furthest takes the track nearest its source, so lines don't cross
        far = lambda j: (ends[j][1][1] <= ends[j][0][1], -ends[j][1][1] if ends[j][1][1] > ends[j][0][1] else ends[j][1][1])
        track = {j: q for c in range(1, n) for q, j in enumerate(sorted((j for j, r in enumerate(drawn) if depth[r["to"]] == c), key=far))}
        pts = []
        for j, r in enumerate(drawn):
            c, (a, b) = depth[r["to"]], ends[j]
            tx = round(X[c - 1] + ew + gaps[c] * (track[j] + 1) / (len(lines_in[c]) + 1))
            pts.append([a, b] if a[1] == b[1] else [a, (tx, a[1]), (tx, b[1]), b])
        segs = [list(zip(q, q[1:])) for q in pts]
        solid = [(x, y, x + ew, y + size[i][3]) for i, (x, y) in pos.items()]
        marks, parts, fail = [], [], None
        for j, r in enumerate(drawn):
            if r.get("label"):
                got = spot(segs, j, False, r["label"], solid, marks, W, H, ends_first=True)  # label next to the many end
                if got is None:
                    fail = j
                    break
                (what, rect, lines), = got
                marks.append(rect)
                parts.append(mark(what, rect, lines, 0))
        if fail is None:
            break
        gaps[depth[drawn[fail]["to"]]] += 24
    else:
        die(f"ER {did}: relationship labels do not fit: shorten them (e.g. 1:N)")
    svg = [markers(p)] + [poly(q, r.get("logical", True), INK, f"{p}many", f"{p}one") for q, r in zip(pts, drawn)]
    for i, e in ents.items():
        (x, y), (kw, rh, head, eh) = pos[i], size[i]
        trs = ""
        for (c, t), h in zip(e["cols"], rh):
            note = "".join(f'<small class="fkn">FK &rarr; {esc(m, True)}</small>' for m in notes.get((i, c), []))
            keys = "".join(f'<span class="k{html.escape(k.lower())}">{esc(k)}</span> ' for k in (t or "").split())
            trs += f'<tr style="height:{h}px"><td>{esc(c, True)}{note}</td><td>{keys}</td></tr>'
        parts.append(f'<div class="ent" style="left:{x}px;top:{y}px;width:{ew}px;height:{eh}px">'
                     f'<div class="eh" style="height:{head}px"><span class="sch">{esc(e.get("schema", ""))}</span><b>{esc(e["name"], True)}</b>'
                     f'<small>{esc(e.get("grain", ""), True)}</small></div>'
                     f'<table><colgroup><col><col style="width:{kw}px"></colgroup>{trs}</table></div>')
    return (f'<div class="map-wrap"><div class="map" style="width:{W}px;height:{H}px">'
            f'<svg width="{W}" height="{H}" aria-hidden="true">{"".join(svg)}</svg>{"".join(parts)}</div></div>')


def journey(d, p):
    stages = []
    for s in d["stages"]:
        trs = ""
        for r in s["rows"]:
            r = r if isinstance(r, dict) else {"field": r[0], "value": r[1]}
            sub = f'<small>{esc(r["sub"], True)}</small>' if r.get("sub") else ""
            if "old" in r:
                val = f'<span class="old">{"NULL" if r["old"] is None else esc(r["old"], True)}</span><span class="new">{esc(r["value"], True)}</span>'
                cls = "chg"
            else:
                val = '<span class="tc">NULL</span>' if r["value"] is None else esc(r["value"], True)
                cls = "calc" if r.get("calc") else "chg" if r.get("changed") else ""
            trs += f'<tr><td>{esc(r["field"], True)}{sub}</td><td class="{cls}">{val}</td></tr>'
        stages.append(f'<div class="stage{" changed" if s.get("changed") else ""}"><div class="h"><b>{esc(s["title"])}</b>'
                      f'<small>{esc(s.get("sub", ""), True)}</small></div><table>{trs}</table><p class="what">{esc(s.get("what", ""), True)}</p></div>')
    rows = [stages[q:q + 3] for q in range(0, len(stages), 3)]  # more than 3 stages: next row, same stage width
    pad = '<div class="arrow"></div><div class="stage pad"></div>'
    return "".join((f'<div class="jnext">&#8627; CONTINUES: STAGE {3 * q + 1}</div>' if q else "") + '<div class="journey">'
                   + '<div class="arrow">&rarr;</div>'.join(r) + (pad * (3 - len(r)) if len(rows) > 1 else "") + "</div>"
                   for q, r in enumerate(rows))


# ---------- other blocks ----------
KW = (r"\b(SELECT|FROM|WHERE|LEFT JOIN|INNER JOIN|JOIN|ON|AND|OR|GROUP BY|ORDER BY|HAVING|AS|CASE|WHEN|THEN|ELSE|END|IN|IS|"
      r"NOT|NULL|UNION ALL|LIMIT|WITH|DISTINCT|OVER|PARTITION BY|QUALIFY|MERGE|INTO|USING|MATCHED|UPDATE|SET|INSERT|VALUES)\b")


def highlight(code, lang):
    t = html.escape(code)
    if lang == "sql":  # one pass, so keywords inside strings stay plain
        return re.sub(r"(&#x27;.*?&#x27;)|" + KW, lambda m: f'<span class="{"ts" if m[1] else "tb"}">{m[0]}</span>', t)
    if lang == "json":
        t = re.sub(r"(&quot;(?:(?!&quot;).)*&quot;)(\s*:)", r'<span class="tk">\1</span>\2', t)
        t = re.sub(r"(:\s*)(&quot;(?:(?!&quot;).)*&quot;)", r'\1<span class="ts">\2</span>', t)
        return re.sub(r"(:\s*)(-?\d+\.?\d*|true|false|null)\b", r'\1<span class="tn">\2</span>', t)
    if lang == "shell":
        return re.sub(r"^(\$ )", r'<span class="tc">\1</span>', t, flags=re.M)
    return t


def result_table(r):
    syn = set(r.get("synthetic", []))
    head = "".join(f"<th>{esc(c)}</th>" for c in r["cols"])
    cell = lambda v: '<span class="tc">NULL</span>' if v is None else esc(v)
    body = "".join("<tr>" + "".join(f'<td>{cell(v)}{" <span class=\"chip syn\">synthetic</span>" if j == 0 and i in syn else ""}</td>'
                                    for j, v in enumerate(row)) + "</tr>" for i, row in enumerate(r["rows"]))
    return f'<div class="scroll"><table class="res"><tr>{head}</tr>{body}</table></div>'


def io(b):
    what = esc(b.get("label", "Input")) + (" &middot; " + esc(b["title"]) if b.get("title") else "")
    inp = f'<div class="payload"><div class="h"><span class="in">IN</span><span>{what}</span></div><pre>{highlight(b["input"], b.get("lang", "text"))}</pre></div>'
    r = b.get("result")
    body = result_table(r) if isinstance(r, dict) else f'<pre>{highlight(r or "", b.get("result_lang", "text"))}</pre>'
    out = f'<div class="payload"><div class="h"><span class="out">OUT</span><span>{esc(b.get("result_title", "result"))}</span></div>{body}</div>'
    return f'<div class="payloads">{inp}{out}</div>'


def kv(v):
    if isinstance(v, list):
        return "<table>" + "".join(f'<tr><td><span class="k">{esc(k)}</span>{esc(x, True)}</td></tr>' for k, x in v) + "</table>"
    return f'<p class="res-t">{esc(v, True)}</p>'


def examples(b):
    cards = []
    for c in b["items"]:
        syn = ' <span class="chip syn">synthetic</span>' if c.get("synthetic") else ""
        src = f'<p class="src">{esc(c["source"])}</p>' if c.get("source") else ""
        cards.append(f'<div class="card {html.escape(c.get("case", "typical"))}"><div class="h"><span class="tag">{esc(c.get("tag", c.get("case", "typical"))).upper()}</span>'
                     f'{syn}<b>{esc(c["title"])}</b></div><div class="lbl2">IN</div>{kv(c["in"])}<div class="lbl2">OUT</div>{kv(c["out"])}{src}</div>')
    return f'<div class="cards">{"".join(cards)}</div>'


def issues(b, kind):
    cols = ISSUE_COLS[kind]
    head = "<th>#</th>" + "".join(f"<th>{c}</th>" for c, _ in cols)
    items = b["items"]
    sev = lambda i: i.get("sev") if i.get("sev") in SEV else "Other"
    groups = [(s, [i for i in items if sev(i) == s]) for s in SEV] if kind != "overview" else [("", items)]
    used = [g for g in groups if g[1]]
    body, n = "", 0
    for sev, rows in used:
        if sev and len(used) > 1:
            body += f'<tr class="sev"><td colspan="{len(cols) + 1}">{sev}</td></tr>'
        for it in rows:
            n += 1
            body += f"<tr><td>{n}</td>" + "".join(
                f'<td{" class=m" if k == "where" else ""}>{status(it.get(k, ""))}</td>' for _, k in cols) + "</tr>"
    return f'<div class="scroll"><table class="issues"><tr>{head}</tr>{body}</table></div>' if n else "<p>No known issues.</p>"


def table(head, rows):
    """head: ready HTML per column; every cell may be a review status."""
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{status(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><tr>{th}</tr>{body}</table></div>'


def block(b, kind):
    t = b["type"]
    if t == "text":
        out = f'<p class="lead">{esc(b["text"])}</p>'
    elif t == "h3":
        out = f'<h3>{esc(b["text"])}</h3>'
    elif t == "bullets":
        out = "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ul>"
    elif t == "labels":
        out = "<ul>" + "".join(f"<li><b>{esc(a)}:</b> {esc(x)}</li>" for a, x in b["items"]) + "</ul>"
    elif t == "table":
        out = table([esc(c) for c in b["cols"]], b["rows"])
    elif t in TYPED:
        out = (f"<h3>{TYPED_H3[t]}</h3>" if t in TYPED_H3 else "") + table(TYPED[t], b["rows"])
    elif t == "steps":
        cols = b.get("cols", ["Step", "In", "Out"])
        head = "<th>#</th>" + "".join(f"<th>{esc(c)}</th>" for c in cols)
        body = "".join(f'<tr><td><span class="n">{i}</span></td>' + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
                       for i, r in enumerate(b["rows"], 1))
        out = f'<table class="steps"><tr>{head}</tr>{body}</table>'
    elif t == "terms":
        out = '<ul class="terms">' + "".join(f"<li><b>{esc(a)}</b> &mdash; {esc(m)}</li>" for a, m in b["items"]) + "</ul>"
    elif t == "io":
        out = io(b)
    elif t == "examples":
        out = examples(b)
    elif t == "issues":
        out = issues(b, kind)
    elif t == "details":
        inner = "".join(block(x, kind) for x in b["blocks"])
        out = f'<details{" open" if b.get("open") else ""}><summary>{esc(b["summary"])}</summary>{inner}</details>'
    elif t in ("flow", "er", "journey"):
        out = ""
        if b.get("id"):
            out += f'<h3 id="d-{esc(b["id"])}">Diagram {esc(b["id"])} &middot; {esc(b.get("title", ""))}</h3>'
        if b.get("parent"):
            pd, pb = b["parent"]
            out += f'<p class="key">Sub-flow of <b>{esc(pb)}</b> in <a href="#d-{esc(pd)}">Diagram {esc(pd)}</a></p>'
        out += flow(b, uid(), kind) if t == "flow" else er(b, uid()) if t == "er" else journey(b, uid())
        out += f'<p class="key">Key: {esc(b["key"])}</p>' if b.get("key") else ""
        out += f'<p class="cap">Notice: {esc(b["notice"])}</p>' if b.get("notice") else ""
    else:
        sys.exit(f"unknown block type: {t}")
    return out + (f'<p class="src">{esc(b["source"])}</p>' if b.get("source") else "")


def tabs(t):
    names = [("Does", "does"), ("Doesn't", "doesnt"), ("Limitations", "limitations"), ("Top issues", "top_issues")]
    bar = "".join(f'<label for="t{i}">{n}</label>' for i, (n, _) in enumerate(names, 1))
    panels = ""
    for i, (n, k) in enumerate(names, 1):
        items = t.get(k) or (["No known issues"] if k == "top_issues" else ["None"])
        tag = "ol" if k == "top_issues" else "ul"
        lis = "".join(f'<li>{esc(x["text"]) + " " + status(x["status"]) if isinstance(x, dict) else esc(x)}</li>' for x in items)
        panels += f'<div class="panel p{i}" data-title="{n}"><{tag}>{lis}</{tag}></div>'
    radios = "".join(f'<input type="radio" name="tabs" id="t{i}" aria-label="{n}"{" checked" if i == 1 else ""}>'
                     for i, (n, _) in enumerate(names, 1))
    return f'<div class="tabs">{radios}<div class="bar">{bar}</div>{panels}</div>'


def slot(kind, name):
    return "How to *" if kind == "user-guide" and name.startswith("How to ") else name


def flat(blocks):
    return [x for b in blocks for x in (b["blocks"] if b["type"] == "details" else [b])]


def rx(recipe, relax=False):
    """Recipe -> regex over "type " words. relax drops the minimums, except the word that opens a group
    (it marks where each repeat starts, which keeps the regex from backtracking exponentially)."""
    toks, out = re.findall(r"[\w-]+|[()|?*+]", recipe), []
    for i, t in enumerate(toks):
        nxt, prev = (toks[i + 1] if i + 1 < len(toks) else ""), (toks[i - 1] if i else "")
        if t in ("?", "*", "+"):
            out.append("*" if relax and t == "+" else t)
        elif t in ("(", "|"):
            out.append("(?:" if t == "(" else "|")
        else:
            out.append(")" if t == ")" else f"(?:{t} )")
            if relax and nxt not in ("?", "*", "+") and prev != "(":
                out.append("?")
    return "".join(out)


def fits(recipe, types, relax=False):
    return re.fullmatch(rx(recipe, relax), "".join(t + " " for t in types)) is not None


def l0(b, err, warn):
    """Overview flow = L0: one row of boxes, people below, nothing else."""
    nodes = b["nodes"]
    bad = (["lanes"] if b.get("lanes") else []) + (["box_w"] if "box_w" in b else []) + \
          (["sub-flows (see/parent)"] if b.get("parent") or any(n.get("see") for n in nodes) else []) + \
          [f"{n['id']}: >2 bullets" for n in nodes if len(n.get("bullets", [])) > 2] + \
          [f"{n['id']}: row {n.get('row')}" for n in nodes
           if n.get("row", 0) > 1 or (n.get("row") == 1 and n.get("kind") != "person")]
    if bad:
        err.append(f"overview flow is L0 (one row of boxes, person boxes in row 1, fixed width, no lanes or "
                   f"sub-flows, <=2 bullets per box): {bad}")
    main_row = sum(1 for n in nodes if n.get("row", 0) == 0)
    if not 3 <= main_row <= 7:
        warn.append(f"overview flow: {main_row} boxes in the main row (want 3-7)")


def amounts(spec, err, warn):
    """Overview only: too little is the problem; far more is a smell."""
    for name, blocks in spec["sections"].items():
        for b in flat(blocks):
            if b["type"] == "flow":
                l0(b, err, warn)
            elif b["type"] == "journey":
                st, rows = b["stages"], [len(s["rows"]) for s in b["stages"]]
                if len(st) < 3 or min(rows) < 3:
                    warn.append(f"{name}: journey needs at least 3 stages x 3 rows (has {len(st)} stages, rows {rows})")
                if len(st) > 5 or max(rows) > 8:
                    warn.append(f"{name}: journey above 5 stages or 8 rows (has {len(st)} stages, rows {rows})")
            elif b["type"] == "examples":
                n = len(b["items"])
                if not 2 <= n <= 6:
                    warn.append(f"{name}: {n} cards (want 2-6: typical + edge or failure)")
                if not any(c.get("case") in ("edge", "rejected", "failure") for c in b["items"]):
                    warn.append(f"{name}: no edge, rejected or failure card (want typical + edge or failure)")
    found = sum(len(b["items"]) for b in flat(spec["sections"].get(LAST, [])) if b["type"] == "issues")
    tops = len(spec.get("tabs", {}).get("top_issues", []))
    if found < tops:
        warn.append(f"known issues: {found} listed but {tops} top issues (every top issue must be listed)")
    if found > 12:
        warn.append(f"known issues: {found} listed (keep ~12 in the overview; the rest go in the technical doc)")


def check(spec, kind, names):
    """Return (errors, warnings). Errors: wrong blocks or order, labels, row lengths. Warnings: minimums."""
    err, warn = [], []
    have = {slot(kind, n) for n in names}
    want = REQUIRED[kind]["*"] + [s for a in spec.get("app_types", []) for s in REQUIRED[kind].get(a, [])]
    warn += [f"missing section: {w} (add it, or one bullet 'Not defined in source - confirm with owner.')"
             for w in dict.fromkeys(want) if w not in have]
    for n in names:
        blocks = flat(spec["sections"][n])
        types = [b["type"] for b in blocks]
        recipe = RECIPES.get(kind, {}).get(slot(kind, n))
        if recipe and not fits(recipe, types):
            short = fits(recipe, types, relax=True)
            (warn if short else err).append(f"{n}: recipe `{recipe}`, got `{' '.join(types) or '(empty)'}`"
                                            + (" - a required block is missing" if short else ""))
        fixed = H3_FIXED.get((kind, n))
        for b in blocks:
            t = b["type"]
            cols = len(TYPED[t]) if t in TYPED else len(b["cols"]) if t == "table" else 0
            err += [f"{n}: {t} row has {len(r)} cells, want {cols}: {r}" for r in b.get("rows", []) if cols and len(r) != cols]
            if t == "er" and len(b["entities"]) > 9:
                err.append(f"{n}: ER has {len(b['entities'])} tables (max ~9): split it into one ER per area")
            if t == "h3" and fixed and not b["text"].startswith(fixed):
                err.append(f"{n}: h3 must start with '{fixed}', got '{b['text']}'")
        if kind == "overview" and n in ("What it is and why", "Value and cost"):
            got = [a for b in blocks if b["type"] == "labels" for a, _ in b["items"]]
            first = n == "What it is and why"
            if not (got[:4] == L0_LABELS if first else got and set(got) <= {"Value", "Cost"}):
                err.append(f"{n}: labels must be " + (f"{L0_LABELS} first" if first else "Value or Cost") + f", got {got}")
        if kind == "technical" and n == "Main flows":
            flows = []
            for b in blocks:
                if b["type"] == "h3":
                    flows.append([b["text"], False])
                elif flows and b["type"] in EXAMPLE_BLOCKS:
                    flows[-1][1] = True
            warn += [f"no example in main flow: {t}" for t, ok in flows if not ok]
        elif (slot(kind, n) == "How to *" or (kind, n) in (("overview", "Example"), ("technical", "Business rules"))) \
                and not set(types) & EXAMPLE_BLOCKS:
            warn.append(f"no example in: {n}")
        if kind == "technical" and n == "Business rules":  # every rule gets an example card
            rules = sum(len(b["rows"]) for b in blocks if b["type"] == "rules")
            cards = sum(len(b["items"]) for b in blocks if b["type"] == "examples")
            if cards < rules:
                warn.append(f"Business rules: {rules} rules but {cards} example cards (at least one card per rule)")
    if kind == "overview":
        amounts(spec, err, warn)
    return err, warn


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def graph_commit():
    link = Path(".knowledge-graph")
    top = Path(git("rev-parse", "--show-toplevel") or Path.cwd())
    folder = Path(link.read_text(encoding="utf-8").strip()) if link.is_file() else Path(f"{top.name}-knowledge-graph")
    try:
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    v = next((meta[k] for k in ("commit", "repo_commit", "git_commit", "head", "sha") if isinstance(meta.get(k), str) and meta[k]), "")
    return v[:12]


def stamp(spec, out_dir):
    parts = []
    head = git("rev-parse", "--short", "HEAD")
    if head:
        try:  # the docs being rebuilt must not make the repo look dirty
            rel = out_dir.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            rel = "."
        skip = [f":(exclude){rel}"] if rel != "." else []
        parts.append(f"repo {head}" + ("+dirty" if git("status", "--porcelain", "--", ".", *skip) else ""))
    graph = graph_commit()
    if graph:
        parts.append(f"graph {graph}")
    if spec.get("review"):
        parts.append(f"review {spec['review']}")
    return f'<p class="sub1 stamp">{" &middot; ".join(esc(p) for p in parts)}</p>' if parts else ""


def review_warn(spec):
    """Known issues come from one review: the newest file in reviews/, named in the spec."""
    files = sorted((f for f in Path("reviews").glob("*") if f.is_file() and not f.name.startswith(".")),
                   key=lambda f: f.stat().st_mtime)
    named = spec.get("review")
    if named and not Path(named).is_file():
        return [f"review file not found: {named}"]
    if files and not named:
        return [f'set "review" to the one review the known issues come from (newest: {files[-1].as_posix()})']
    if files and Path(named).resolve() != files[-1].resolve():
        return [f"review {named} is not the newest ({files[-1].as_posix()}): use the newest, or ask which one"]
    return []


def main(spec_path, out_path):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; spec text can hold arrows
    sys.stderr.reconfigure(encoding="utf-8")
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    kind, sections = spec["type"], spec["sections"]
    if kind == "custom":  # README, runbook, design doc...: free section names, written order, same look
        ORDER["custom"], REQUIRED["custom"], ISSUE_COLS["custom"] = [n for n in sections if n != LAST], {"*": []}, ISSUE_COLS["technical"]
    allowed = ORDER[kind] + [LAST]
    bad = [n for n in sections if slot(kind, n) not in allowed]
    if bad:
        sys.exit(f"sections not allowed for {kind}: {bad}. Allowed, in order: {allowed}")
    names = sorted(sections, key=lambda n: allowed.index(slot(kind, n)))  # stable sort keeps "How to" order
    err, warn = check(spec, kind, names)
    for w in warn + review_warn(spec):
        print("WARN", w)
    if err:
        sys.exit("\n".join(f"ERROR {e}" for e in err))
    out = Path(out_path)
    title = (lambda i, n: f"{i + 1} {n}") if kind == "technical" else (lambda i, n: n)
    toc = "".join(f'<a href="#s{i}">{esc(title(i, n))}</a>' for i, n in enumerate(names))
    src = f'<p class="src">Known issues from review <code>{esc(spec["review"])}</code></p>' if spec.get("review") else ""
    body = "".join(f'<section><h2 id="s{i}">{esc(title(i, n))}</h2>{src if n == LAST else ""}'
                   f'{"".join(block(b, kind) for b in sections[n])}</section>' for i, n in enumerate(names))
    css = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
    sub = f'<p class="sub1">{esc(spec["subtitle"])}</p>' if spec.get("subtitle") else ""
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-docs-v2"><title>{esc(spec["title"])}</title><style>{css}</style></head><body><main>'
            f'<div class="eyebrow">{kind.replace("-", " ")}</div><h1>{esc(spec["title"])}</h1>{stamp(spec, out.parent)}{sub}'
            f'{tabs(spec.get("tabs", {}))}<nav class="toc">{toc}</nav>{body}</main></body></html>')
    out.write_text(page, encoding="utf-8")
    (out.parent / ".generated-by-darshan-singh-meel-docs").touch()  # the graph skill skips folders holding this
    print(f"built {out_path}: {len(names)} sections")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
