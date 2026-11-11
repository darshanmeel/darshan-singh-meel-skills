"""Build one document from a JSON spec: fixed sections, one look, diagrams laid out here.

Usage: python build.py <spec.json> <out.html>   (run from the repo root: git, repo files, reviews/ and the graph are read
from there; cited paths and lines, backticked names and box labels are checked against the repo, and the structure and,
for technical docs, coverage against <spec folder>/inventory.json written by inventory.py)
The model writes only the spec (content, boxes, arrows, examples). Spec format: spec.md.
"""
import html
import json
import math
import os
import re
import shlex
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # importing inventory.py must not leave __pycache__ in the skill folder
from inventory import HOW, diagram_titles, find_graph, graph_meta, meta_commit, meta_date, rel, secret, stale, version  # noqa: E402

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
    "technical": {"*": ["Overview", "Architecture", "Main flows", "Deploy and environments"],
                  "pipeline": ["Job DAG and schedule", "Data model", "Operations"], "ui": ["Screens and navigation"],
                  "api": ["Endpoints", "Operations"], "cli": ["Commands"], "events": ["Events and messages", "Operations"]},
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
        "Overview": "text? flow", "Architecture": "flow components api? bullets?",
        "Job DAG and schedule": "flow+ schedule bullets?", "Screens and navigation": "flow+ elements bullets?",
        "Endpoints": "flow+ endpoints bullets?", "Commands": "flow+ commands bullets?",
        "Events and messages": "flow+ events bullets?",
        "Main flows": "(h3 steps flow* journey? examples io?)+",
        "Data model": "text? er+ views? bullets?", "Business rules": "rules examples?", "Configuration": "config bullets?",
        "Security and access": "(access bullets?|bullets)", "Deploy and environments": "flow? steps io* environments? bullets?",
        "Operations": "io* symptoms (h3 steps io*)*", "Performance and limits": "bullets", "Tests": "tests io* bullets?",
        "Key decisions": "choices", LAST: "text? issues unused? assumptions? decisions?"},
    "user-guide": {
        "How it reaches you": "flow bullets? examples?", "Screens": "flow+ elements",
        "What answers what": "text? flow* table (h3 bullets)?", "How to *": "steps (io|examples|journey)+ bullets?",
        "When data is fresh": "flow? (schedule|table) io? bullets?", "History and deletions": "text? journey bullets? io?",
        "Errors and messages": "messages", "Problems and fixes": "problems", "Who to contact": "bullets",
        LAST: "text? issues assumptions? decisions?"},
}
H3_FIXED = {("user-guide", "What answers what"): "Columns every"}
RERUN = "Rerun and backfill"  # technical Operations h3 for pipelines; the other Operations h3s are the plan's how_tos
STEP_COLS = {  # fixed steps columns per section; other sections keep the default or their own cols
    ("overview", "How it works"): ["Step", "What happens"], ("technical", "Main flows"): ["Step", "In", "Out"],
    ("technical", "Deploy and environments"): ["Step", "Command", "Where it runs"],
    ("technical", "Operations"): ["Step", "How"], ("user-guide", "How to *"): ["Step", "You see"]}
TYPED = {  # builder-owned headers; the spec gives rows only
    "people": ["Who", "What they get"], "schedule": ["Environment", "Runs", "Notes"],
    "components": ["Component", "Responsibility", "Where"], "api": ["Call", "Returns", "Raises", "Where"],
    "rules": ["Rule", "Input &rarr; output", "Where"],
    "config": ["Setting", "Default (code) / deploy value", "Where", "Purpose"], "access": ["Who", "Access", "How"],
    "environments": ["Environment", "Where", "How deployed"], "symptoms": ["Symptom", "Cause", "Fix"],
    "tests": ["Test", "Covers"], "choices": ["Decision", "Why"], "elements": ["Element", "What it does"],
    "endpoints": ["Endpoint", "Does", "Example"], "commands": ["Command", "Does", "Example"],
    "events": ["Event", "From &rarr; to", "Payload"], "messages": ["Message", "Means", "Do"],
    "problems": ["Problem", "What to do"], "views": ["View", "Built from", "Rows"],
    "unused": ["File", "Why it looks unused", "Status"], "assumptions": ["Assumption", "Why it matters"],
    "decisions": ["Decision", "Options", "Recommendation", "If it waits"],
}
TYPED_H3 = {"unused": "Unused files", "assumptions": "Assumptions", "decisions": "Decisions needed"}
L0_LABELS = ["What", "Why", "Key idea", "Result"]
EXAMPLE_BLOCKS = {"examples", "io", "journey"}
CASES = ["typical", "edge", "rejected", "failure"]
EX_FIELDS = ["case", "title", "expect", "in", "out"]
ISSUE_COLS = {
    "overview": [("Issue", "issue"), ("What it means", "impact"), ("Status", "status")],
    "technical": [("Issue", "issue"), ("Where", "where"), ("Impact", "impact"), ("Status", "status"), ("Suggested fix", "fix")],
    "user-guide": [("If you see", "see"), ("Do this", "do"), ("Status", "status")],
}
SEV = ["Must", "Should", "Question", "Other"]
# no review: the issue's kind fixes its severity (the review's own order otherwise)
RUBRIC = {"security": "Must", "data_loss": "Must", "wrong_result": "Must", "crash": "Must",
          "missing_handling": "Should", "config": "Should", "performance": "Should", "cost": "Should",
          "unclear_intent": "Question", "docs_conflict": "Question",
          "style": "Other", "dead_code": "Other", "docs": "Other", "test_gap": "Other"}
# issue statuses, exactly: the review found it and it is still in the code · a failing test or a run proves it ·
# the code shows it (opened and read) · nobody proved it · fixed in code after the review
STATUSES = ["Confirmed (review)", "Confirmed (test)", "Confirmed (code)", "Not verified", "Fixed since review"]
REVIEW_ONLY = ["Confirmed (review)", "Fixed since review"]  # need a named review
EXREF = re.compile(r"\bExample (\d+(?:\.\d+)?[a-z]|\d+(?:\.\d+)?z\d+)\b")  # "see Example 5.1b"
INK, RED = "#17191D", "#A12D2D"
PAD, GX, GY = 20, 44, 44
CH = 20  # px between parallel lines, and between arrow ends on one side of a box
SPREAD = 40  # px between arrow ends when 2 or more meet one box side (capped by the box width)
# line-break points in names: after _ and /, after . and - unless both neighbours are digits (4.0.0, :38-63),
# and between a lower- and an upper-case letter (CamelCase)
BRK = re.compile(r"(?<=[_/])|(?<=[.-])(?!\d)|(?<=(?<!\d)[.-])|(?<=[a-z])(?=[A-Z])")
NUMS = re.compile(r"\d+(?:[.:–-]\d+)+")  # versions, dates, line ranges: never broken
_ids = [0]
POS = {"kind": "", "slot": "", "sec": 0, "h3": 0, "ex": 0}  # where block() is: example ids, steps columns
LATE = []  # warnings found while drawing (printed with the coverage warnings)


def uid():
    _ids[0] += 1
    return f"m{_ids[0]}"


def parts(word, box=True):
    """A word cut at its break points (BRK), except a cut that leaves a piece of 1-2 chars at the start, or of 1-3
    chars at the end after `.`, `_` or `-` (`ci.yml`, `parse_ini`, `get_db` stay whole: no lone extension or tail).
    A word with one break point that is too long for a narrow box line (> 14 chars) keeps it."""
    ps = [p for p in BRK.split(word) if p]
    keep = lambda: box and (len(ps) > 2 or len(word) <= 14)  # table cells: every break point (columns can be narrow)
    while len(ps) > 1 and len(ps[-1]) <= 3 and ps[-2][-1] in "._-" and keep():
        ps[-2:] = [ps[-2] + ps[-1]]
    while len(ps) > 1 and len(ps[0]) <= 2 and keep():
        ps[:2] = [ps[0] + ps[1]]
    return ps


def esc(text, wbr=False, box=False):
    """Escape; `code` -> <code>, **bold** -> <b>, [synthetic] -> badge; wbr: line-break points in names (parts; in a
    diagram box without the short-tail cuts)."""
    t = html.escape(str(text))
    if wbr:
        t = NUMS.sub(lambda m: f'<span class="nw">{m[0]}</span>', re.sub(r"\S+", lambda m: "<wbr>".join(parts(m[0], box)), t))
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("[synthetic]", '<span class="chip syn">synthetic</span>')


def status(s):
    """Badge only for review statuses; any other value (e.g. "active") stays plain text, with break points in names."""
    s = str(s)
    cls = "ok" if s.startswith("Confirmed") else "nv" if s.startswith("Not verified") else "fx" if s.startswith("Fixed since review") else ""
    return f'<span class="chip {cls}">{esc(s)}</span>' if cls else esc(s, True)


# ---------- diagrams ----------
def die(msg):
    sys.exit(f"ERROR {msg}")


def is_fixed(status_text):
    return str(status_text).startswith("Fixed")


def nlines(text, per):
    """Lines the browser needs at `per` chars a line: breaks at spaces and at the <wbr> points (BRK);
    a longer run splits anywhere (overflow-wrap)."""
    if text is None or text == "":
        return 0
    per, n, cur = max(1, int(per)), 1, 0
    for word in str(text).split():
        for i, part in enumerate(parts(word)):
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
    return esc(v[0], True, True) + "&hellip;<wbr>" + esc(v[1], True, True) if isinstance(v, tuple) else esc(v, True, True)


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
FIELDS = [("label", 22, 7.4, 4), ("sub", 22, 6.6, 2), ("in", 62, 6.4, 2), ("out", 62, 6.4, 2)]


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
    inner += "<ul>" + "".join(f"<li>{esc(b, True, True)}</li>" for b in n["bullets"]) + "</ul>" if n.get("bullets") else ""
    inner += f'<span class="run">{esc(n["runs"], True, True)}</span>' if n.get("runs") else ""
    if n.get("in") or n.get("out"):
        inner += '<div class="io">' + "".join(f'<span class="l {k}">{k.upper()}</span><span>{show(n[k])}</span>'
                                              for k in ("in", "out") if n.get(k)) + "</div>"
    inner += f'<a class="see" href="#d-{esc(n["see"])}">&#9656; Diagram {esc(n["see"])}</a>' if n.get("see") else ""
    tip = f' data-tip="{html.escape(n["tip"])}" tabindex="0"' if n.get("tip") else ""
    return (f'<div class="b {html.escape(n.get("kind", ""))}{" rich" if rich else ""}"{tip} '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{inner}</div>')


def hit(a, b, pad=0):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def crosses(s, r, pad=2):
    (x1, y1), (x2, y2) = s
    return hit((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), r, pad)


FOREIGN = 7  # px a number or label keeps from any line that is not its own (check.py flags < 6)


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


def spot(segs, j, num, label, solid, marks, W, H, ends_first=False, pad=FOREIGN):
    """Room for line j's number and label: on a horizontal part, label above the line right of the number (else
    above the number, else on two lines); on a vertical part, beside it. Never on a box, a line, another number or
    label, or the arrowhead. Returns [(kind, rect, label lines)] or None."""
    others = [s for k, ss in enumerate(segs) if k != j for s in ss]
    nw, sep = (20, 6) if num else (0, 0)
    first, last = segs[j][0], segs[j][-1]

    def ok(r, own):
        return (r[0] >= 2 and r[1] >= 2 and r[2] <= W - 2 and r[3] <= H - 2 and not any(hit(r, o, 3) for o in solid + marks)
                and not any(crosses(s, r, pad) for s in others) and not any(crosses(s, r) for s in segs[j] if s is not own))

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
    """Number or label of line n (1 = first polyline); data-e lets check.py tell its own line from the others."""
    a, b, c, z = r
    if what == "num":
        return f'<span class="num" data-e="{n}" style="left:{a + 10}px;top:{b + 10}px">{n}</span>'
    return f'<span class="lbl" data-e="{n}" style="left:{a}px;top:{b}px;height:{z - b}px">{"<br>".join(esc(x) for x in lines)}</span>'


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


def slots(edges, rt, cell, tree=True):
    """Offset of each arrow end from its row or column centre line, in CH steps. Ends on one box side are ordered by
    the box at the other end (so lines don't cross) and centred; then every part along a row or column line takes the
    nearest offset that keeps it CH away from all other parts it overlaps, so no two lines lie on top of each other.
    Arrows leaving one box side (a fan-out) leave from one point and share their first part: a tree, not nested
    lines (tree=False: each its own point). Returns (offsets, spread, rep): rep[j] = the first arrow of j's fan-out."""
    att = {}  # (box, side) -> arrow ends there: (edge, 0 = start / 1 = end, cell at the other end)
    rep = list(range(len(edges)))
    for j, (e, r) in enumerate(zip(edges, rt)):
        lst = att.setdefault((e["from"], r[1]), [])
        first = next((a[0] for a in lst if a[1] == 0), None)
        if first is None or not tree:
            lst.append((j, 0, cell[e["to"]]))
        else:
            rep[j] = first
        att.setdefault((e["to"], r[2]), []).append((j, 1, cell[e["from"]]))
    want = {}
    for (i, s), lst in att.items():
        ax = 1 if s in "lr" else 0
        lst.sort(key=lambda a: (a[2][ax], a[2][1 - ax], a[0]))
        own = cell[i][ax]
        nb, m = sum(a[2][ax] < own for a in lst), sum(a[2][ax] == own for a in lst)
        for q, a in enumerate(lst):
            want[a[:2]] = q - nb - (m - 1) / 2 if m else q - (len(lst) - 1) / 2
    for j in range(len(edges)):
        want[(j, 0)] = want[(rep[j], 0)]
    ps = [x for j, (e, r) in enumerate(zip(edges, rt)) for x in runs(j, r, cell[e["from"]], cell[e["to"]])]
    # the first parts of one fan-out move as one unit: they lie on one line
    size = Counter(rep)
    unit = [next((("f", rep[j]) for j, end in x[4] if not end and size[rep[j]] > 1), q) for q, x in enumerate(ps)]
    groups = {}
    for q, u in enumerate(unit):
        groups.setdefault(u, []).append(q)
    off, done = {}, []
    for qs in sorted(groups.values(), key=lambda qs: (min(abs(sum(want[k] for k in ps[q][4]) / len(ps[q][4])) for q in qs), qs[0])):
        ax, ln = ps[qs[0]][:2]
        lo, hi = min(ps[q][2] for q in qs), max(ps[q][3] for q in qs)
        ends = [k for q in qs for k in ps[q][4]]
        pref = sum(want[k] for k in ends) / len(ends)
        near = [o for k, o in done if ps[k][:2] == (ax, ln) and ps[k][2] <= hi and lo <= ps[k][3]]
        o = next(pref + d for d in (x * sgn / 2 for x in range(40) for sgn in (1, -1)) if all(abs(pref + d - n) >= 1 for n in near))
        done += [(q, o) for q in qs]
        off.update(dict.fromkeys(ends, o))
    spread = {}  # (axis, line) -> largest offset used on it
    for q, o in done:
        spread[ps[q][:2]] = max(spread.get(ps[q][:2], 0), abs(o))
    return off, spread, rep


def track_key(ch, kind, a, b):
    """Order of the lines in one gap (small key = left / top track). A line that turns and travels further takes the
    track nearer its source, so a fan-out to targets on one side does not cross itself; a U-shaped line (both ends on
    one row or column) with the longer span goes outside."""
    (ac, ar), (bc, br) = a, b
    axis, q = ch
    if kind == "U" or (axis == "v" and ac == bc) or (axis == "h" and ar == br):
        span = abs(bc - ac) if axis == "h" else abs(br - ar)
        return span if q > (ar if axis == "h" else ac) else -span
    far = abs(br - ar) if axis == "v" else abs(bc - ac)
    return -far if q > (ac if axis == "v" else ar) else far


def crossings(pts):
    """Times a horizontal part of one line crosses a vertical part of another (ends excluded), as check.py counts."""
    segs = [list(zip(q, q[1:])) for q in pts]
    n = 0
    for k, sa in enumerate(segs):
        for sb in segs[k + 1:]:
            for p1, p2 in sa:
                for q1, q2 in sb:
                    h, v = ((p1, p2), (q1, q2)) if p1[1] == p2[1] and q1[0] == q2[0] else ((q1, q2), (p1, p2)) if q1[1] == q2[1] and p1[0] == p2[0] else (None, None)
                    if h and min(h[0][0], h[1][0]) < v[0][0] - 1 and v[0][0] + 1 < max(h[0][0], h[1][0])                             and min(v[0][1], v[1][1]) < h[0][1] - 1 and h[0][1] + 1 < max(v[0][1], v[1][1]):
                        n += 1
    return n


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
    # labels FOREIGN px from other lines, fan-outs as trees; if no layout allows that, separate fan-out lines; then 2 px
    for pad, tree in ((FOREIGN, True), (FOREIGN, False), (2, True), (2, False)):
        for k in (4, 3, 2) if any("frame" in n for n in nodes.values()) else (4,):
            for w in widths:
                out, why = draw(d, did, p, nodes, edges, groups, lanes, cell, len(cs), len(rs), w, k, kind, gap, pad, tree)
                if out:
                    long_words(d, did, w)
                    return out
    die(why)


def long_words(d, did, w):
    """A part of a box text with no break point that is longer than one line breaks mid-word: WARN."""
    for n in d["nodes"]:
        for k, inset, px, _ in FIELDS:
            per = (w - inset) / px
            long = [q for word in str(n.get(k) or "").split() for q in parts(word) if len(q) > per]
            if long:
                LATE.append(f"diagram {did}: box '{n['label']}' {k}: {long} longer than one line ({int(per)} chars) "
                            f"breaks mid-word: shorten it, or use a name that breaks at _ / . - or CamelCase")


def draw(d, did, p, nodes, edges, groups, lanes, cell, C, R, w, k, kind, gap=GX, pad=FOREIGN, tree=True):
    occ = set(cell.values())
    fr = {i: frame_layout(n, w, k) for i, n in nodes.items() if "frame" in n}
    bx = {i: fit(n, w) for i, n in nodes.items() if "frame" not in n}
    rt = [route(cell[e["from"]], cell[e["to"]], occ, R) for e in edges]
    off, spread, rep = slots(edges, rt, cell, tree)
    # 2+ arrow ends on one box side: SPREAD px apart instead of CH, so they don't meet in one spot. One step per row or
    # column line keeps every straight part on it straight; a column's step is capped by its narrowest box.
    step = {}
    for (i, s), n in Counter(x for e, r in zip(edges, rt) for x in ((e["from"], r[1]), (e["to"], r[2]))).items():
        line = ("h", cell[i][1]) if s in "lr" else ("v", cell[i][0])
        if n >= 2 and spread.get(line):
            step[line] = SPREAD  # rows grow to fit
            if line[0] == "v":
                narrow = min(fr[i][0] if i in fr else w for i in cell if cell[i][0] == line[1])
                step[line] = max(CH, min(SPREAD, (narrow / 2 - 12) / spread[line]))
    st = lambda line: step.get(line, CH)
    bh = [0] * R
    for i, n in bx.items():
        bh[cell[i][1]] = max(bh[cell[i][1]], box_height(n, w))
    bh = [max(bh[r], int(2 * spread[("h", r)] * st(("h", r)) + 24) if ("h", r) in spread else 0) for r in range(R)]
    rowh = [max([bh[r]] + [fr[i][1] for i in fr if cell[i][1] == r]) or 40 for r in range(R)]
    colw = [max([w if any(cell[i][0] == c for i in bx) else 0] + [fr[i][0] for i in fr if cell[i][0] == c]) for c in range(C)]
    uses = [r[3] for r in rt]
    tracks = {}
    for j, u in enumerate(uses):
        for ch in u:  # a fan-out's lines share one track in a gap (rep: its first line)
            lst = tracks.setdefault(ch, [])
            lst += [] if rep[j] in lst else [rep[j]]
    ends = lambda j: (cell[edges[j]["from"]], cell[edges[j]["to"]])
    orders = [lambda ch, j: j, lambda ch, j: (track_key(ch, rt[j][0], *ends(j)), j),
              lambda ch, j: (track_key(ch, rt[j][0], *ends(j)[::-1]), j)]  # edge order · far line near its source · near its target
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
            (x, y, ww, hh), (c, r) = rect[i], cell[i]
            o = round(off[(j, end)] * st(("h", r) if s in "lr" else ("v", c)))
            cy, cx = Y[r] + rowh[r] // 2 + o, X[c] + colw[c] // 2 + o
            return {"l": (x, cy), "r": (x + ww, cy), "t": (cx, y), "b": (cx, y + hh)}[s]

        def track(ch, j):
            lst, (a, q) = tracks[ch], ch
            lo, hi = (gx[q] + iL(q), gx[q] + cg[q] - iR(q)) if a == "v" else (gy[q] + iU(q), gy[q] + rg[q] - iD(q))
            return round(lo + (hi - lo) * (lst.index(rep[j]) + 1) / (len(lst) + 1))

        lay = lambda: [points(rt[j][0], port(j, 0), port(j, 1), [track(ch, j) for ch in uses[j]]) for j in range(len(edges))]
        if not attempt and tracks:  # the line order in each gap: whichever of the three orders crosses least
            best = None
            for key in orders:
                for ch, lst in tracks.items():
                    lst.sort(key=lambda j: key(ch, j))
                n = crossings(lay())
                if best is None or n < best[0]:
                    best = (n, {ch: list(lst) for ch, lst in tracks.items()})
            tracks.update(best[1])
        pts = lay()
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
            got = spot(segs, j, num, lab, solid, marks, W, H, False, pad)
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
    if not rels and len(ents) > 1:  # no keys: a grid, 3 tables a row, instead of one tall column
        n = min(3, len(ents))
        cols, gaps, lines_in = [list(ents)[c::n] for c in range(n)], [0] + [40] * (n - 1), [[] for _ in range(n)]
        depth = {i: c for c in range(n) for i in cols[c]}

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

    # a label that doesn't fit widens its gap; tables get narrower to stay in 1020 px. Labels keep FOREIGN px from
    # other lines; only if that never fits, the old 2 px (check.py then names the spot)
    gaps0, pad, tries = list(gaps), FOREIGN, 0
    while True:
        tries += 1
        ew = min(d.get("box_w", 260), (1020 - 2 * PAD - sum(gaps)) // n)
        if ew < 170 or tries > 40:
            if tries == 1 and pad == FOREIGN:
                die(f"ER {did} is {n} tables deep (max 1020 px): split it into one ER per area")
            if pad == FOREIGN:
                gaps, pad, tries = list(gaps0), 2, 0
                continue
            die(f"ER {did}: relationship labels do not fit in 1020 px: shorten them (e.g. 1:N) or split the ER")
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
                got = spot(segs, j, False, r["label"], solid, marks, W, H, True, pad)  # label next to the many end
                if got is None:
                    fail = j
                    break
                (what, rect, lines), = got
                marks.append(rect)
                parts.append(mark(what, rect, lines, j + 1))
        if fail is None:
            break
        gaps[depth[drawn[fail]["to"]]] += 24
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


def kv(v, cell=False):
    """In/out values: [[k, v]] → each value under its key; text → one line. cell: compact, for a table cell."""
    if isinstance(v, list):
        if cell:
            return "".join(f'<div class="kv"><span class="k">{esc(k)}</span> {esc(x, True)}</div>' for k, x in v)
        return "<table>" + "".join(f'<tr><td><span class="k">{esc(k)}</span>{esc(x, True)}</td></tr>' for k, x in v) + "</table>"
    return esc(v, True) if cell else f'<p class="res-t">{esc(v, True)}</p>'


def ex_id():
    """Next example id in this section: <section>.<h3 index><letter> (5.1a), or <section><letter> before any h3."""
    k, POS["ex"] = POS["ex"], POS["ex"] + 1
    letter = chr(97 + k) if k < 26 else f"z{k - 25}"
    return f'{POS["sec"]}.{POS["h3"]}{letter}' if POS["h3"] else f'{POS["sec"]}{letter}'


def examples(b):
    """Cards: id, case, title, then EXPECT, IN, OUT. Business rules with more than 3 → one compact table
    (Ex · Case · Expect · In · Out), sources under it."""
    items = [(ex_id(), c) for c in b["items"]]
    case = lambda c: html.escape(c["case"])
    tag = lambda c: f'<span class="tag">{esc(c.get("tag", c["case"])).upper()}</span>'
    syn = lambda c: ' <span class="chip syn">synthetic</span>' if c.get("synthetic") else ""
    if len(items) > 3 and POS["slot"] == "Business rules":
        rows = "".join(f'<tr id="ex-{i}" class="{case(c)}"><td class="exn">{i}</td><td>{tag(c)}{syn(c)}<b>{esc(c["title"])}</b></td>'
                       f'<td>{esc(c["expect"], True)}</td><td>{kv(c["in"], True)}</td><td>{kv(c["out"], True)}</td></tr>'
                       for i, c in items)
        src = " &middot; ".join(f"{i} {esc(c['source'], True)}" for i, c in items if c.get("source"))
        return (f'<div class="scroll"><table class="extab"><tr><th>Ex</th><th>Case</th><th>Expect</th><th>In</th><th>Out</th></tr>'
                f'{rows}</table></div>' + (f'<p class="src">{src}</p>' if src else ""))
    cards = []
    for i, c in items:
        src = f'<p class="src">{esc(c["source"], True)}</p>' if c.get("source") else ""
        exp = f'<div class="lbl2">EXPECT</div><p class="res-t">{esc(c["expect"], True)}</p>'
        cards.append(f'<div class="card {case(c)}" id="ex-{i}"><div class="h"><span class="exn">EXAMPLE {i}</span>{tag(c)}{syn(c)}'
                     f'<b>{esc(c["title"])}</b></div>{exp}<div class="lbl2">IN</div>{kv(c["in"])}<div class="lbl2">OUT</div>{kv(c["out"])}{src}</div>')
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
            proof = lambda k: f'<br><span class="src">{esc(it["test"], True)}</span>' if k == "status" and it.get("test") else ""
            body += f"<tr><td>{n}</td>" + "".join(
                f'<td{" class=m" if k == "where" else ""}>{status(it.get(k, ""))}{proof(k)}</td>' for _, k in cols) + "</tr>"
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
        POS["h3"], POS["ex"] = POS["h3"] + 1, 0
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
        cols = step_cols(b, POS["kind"], POS["slot"])
        head = "<th>#</th>" + "".join(f"<th>{esc(c)}</th>" for c in cols)
        body = "".join(f'<tr><td><span class="n">{i}</span></td>' + "".join(f"<td>{esc(c, True)}</td>" for c in r) + "</tr>"
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
        die(f"unknown block type '{t}' (allowed: text, h3, bullets, labels, table, steps, terms, io, examples, issues, details, flow, er, journey, {', '.join(TYPED)})")
    return out + (f'<p class="src">{esc(b["source"], True)}</p>' if b.get("source") else "")


def issue_items(spec):
    return [i for b in flat(spec["sections"].get(LAST, [])) if b["type"] == "issues" for i in b["items"]]


def tabs(spec):
    """Does · Doesn't · Limitations · Top issues. Empty Top issues: "No known issues" only when nothing is listed."""
    t, listed = spec.get("tabs", {}), len(issue_items(spec))
    names = [("Does", "does"), ("Doesn't", "doesnt"), ("Limitations", "limitations"), ("Top issues", "top_issues")]
    bar = "".join(f'<label for="t{i}">{n}</label>' for i, (n, _) in enumerate(names, 1))
    none = (f"No open Must or Should issue{'' if spec.get('review') else ' (not reviewed)'}: {listed} other "
            f"item{'s' if listed != 1 else ''} under Known issues") if listed else "No known issues"
    panels = ""
    for i, (n, k) in enumerate(names, 1):
        items = t.get(k) or ([none] if k == "top_issues" else ["None"])
        tag = "ol" if k == "top_issues" else "ul"
        lis = "".join(f'<li>{esc(x["text"]) + " " + status(x["status"]) if isinstance(x, dict) else esc(x)}</li>' for x in items)
        panels += f'<div class="panel p{i}" data-title="{n}"><{tag}>{lis}</{tag}></div>'
    radios = "".join(f'<input type="radio" name="tabs" id="t{i}" aria-label="{n}"{" checked" if i == 1 else ""}>'
                     for i, (n, _) in enumerate(names, 1))
    return f'<div class="tabs">{radios}<div class="bar">{bar}</div>{panels}</div>'


def slot(kind, name):
    return "How to *" if kind == "user-guide" and name.startswith("How to ") else name


def step_cols(b, kind, sec):
    return STEP_COLS.get((kind, sec)) or b.get("cols", ["Step", "In", "Out"])


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
    if found > 12:
        warn.append(f"known issues: {found} listed (keep ~12 in the overview; the rest go in the technical doc)")


def top_issues(spec, err, warn):
    """Every doc: Top issues = min(10, open Must + Should), each listed under Known issues; fixed ones stay out.
    Statuses are one of STATUSES exactly; without a named review, never Confirmed (review) or Fixed since review."""
    items = issue_items(spec)
    tops = spec.get("tabs", {}).get("top_issues", [])
    allowed = STATUSES if spec.get("review") else [s for s in STATUSES if s not in REVIEW_ONLY]
    for where, x in [("issue", i) for i in items] + [("top issue", t) for t in tops if isinstance(t, dict)]:
        st = x.get("status", "")
        if st not in allowed:
            err.append(f"{where} '{str(x.get('issue') or x.get('text') or '')[:60]}': status '{st}' must be one of {allowed}"
                       + ("" if spec.get("review") or st not in REVIEW_ONLY else " (no review is named: nothing is Confirmed (review) or Fixed since review)"))
    for i in items:
        what, kd = f"issue '{str(i.get('issue') or i.get('see') or '')[:60]}'", i.get("kind")
        if not spec.get("review") and kd not in RUBRIC:
            err.append(f"{what}: kind '{kd or ''}' must be one of {', '.join(RUBRIC)} (no review: the kind fixes the severity)")
        elif not spec.get("review") and i.get("sev") != RUBRIC[kd]:
            err.append(f"{what}: kind '{kd}' means sev '{RUBRIC[kd]}', got '{i.get('sev')}'")
        if i.get("status") == "Confirmed (test)" and not i.get("test"):
            err.append(f"{what}: Confirmed (test) needs \"test\": the test (path::name) or command that proved it")
    opened = sum(1 for i in items if i.get("sev") in ("Must", "Should") and not is_fixed(i.get("status", "")))
    if len(items) < len(tops):
        warn.append(f"known issues: {len(items)} listed but {len(tops)} top issues (every top issue must be listed)")
    if len(tops) != min(10, opened):
        warn.append(f"top issues: {len(tops)} given, want min(10, open Must + Should) = {min(10, opened)}")
    fixed = [t.get("text") for t in tops if isinstance(t, dict) and is_fixed(t.get("status", ""))]
    if fixed:
        warn.append(f"top issues: {fixed} are fixed since the review: leave them out of Top issues")


def example_items(n, b, err, warn, main):
    """Every example: case (typical, edge, rejected, failure), title, expect, in, out; ids come from the build.
    Main flows: 2-3 cards, card a typical, at least one other case."""
    items = b["items"]
    for k, c in enumerate(items):
        miss = [f for f in EX_FIELDS if c.get(f) in (None, "", [])]
        if miss:
            err.append(f"{n}: example {k + 1} '{c.get('title', '')}' needs {', '.join(miss)} (each card: case, title, expect, in, out)")
        if c.get("case") not in CASES + [None, ""]:
            err.append(f"{n}: example '{c.get('title', '')}': unknown case '{c['case']}' (use {', '.join(CASES)})")
        if re.search(r"\d", str(c.get("tag", ""))):
            err.append(f"{n}: example '{c.get('title', '')}': tag '{c['tag']}' looks like an id: ids are added by the build, never in tag")
    if not main:
        return
    if len(items) > 3:
        err.append(f"{n}: {len(items)} examples under '{POS['h3text']}' (max 3 cards; the table form is only for Business rules)")
    if items and items[0].get("case") != "typical":
        err.append(f"{n}: example a under '{POS['h3text']}' must be the typical case, got '{items[0].get('case')}'")
    if len(items) < 2 or all(c.get("case") == "typical" for c in items):
        warn.append(f"{n}: examples under '{POS['h3text']}': want 2-3 cards, a typical plus an edge, rejected or failure case")


NOTES = []  # printed as note: lines (documented overrides)


def arrow_count(b):
    """Numbered arrows a flow will show: its edges after a fan-out frame merges them (one per frame)."""
    nodes, edges = {n["id"]: n for n in b.get("nodes", [])}, b.get("edges", [])
    if any("col" not in n or "row" not in n for n in nodes.values()) or any(e.get("from") not in nodes or e.get("to") not in nodes for e in edges):
        return len(edges)
    return len(fan(nodes, edges, b.get("groups", []), b.get("id") or "?")[1])


ENTRIES = set()  # entry point names from inventory.json (endpoints, commands, screens, jobs)


def bare(label):
    """A box label as a name: no backticks, no trailing call parentheses."""
    return re.sub(r"\(.*\)$", "", str(label).strip().strip("`"))


def entry_of(h3_text):
    """Without a plan entry: the input side of "<name>: <input> → <output>"."""
    return h3_text.split(" → ")[0].split(": ")[-1].strip() or h3_text


def main_flows(spec, blocks, plan, err, warn):
    """Technical Main flows: h3s = the plan's (or a documented h3_override), in order. Per h3 the plan decides whether
    there is a flow diagram (diagram: true iff the graph gives >= 3 ordered steps); its title is written here:
    "<entry>, <N> steps", N = its numbered arrows, one steps row per arrow. More flows under one h3 are sub-flows
    (parent). Code and entry boxes are the plan flow's steps (plan boxes) or entry points."""
    over = spec.get("h3_override", {}) or {}
    pm = (plan or {}).get("main_flows")
    if pm is not None:
        keys = [m["h3"] for m in pm]
        for k, v in over.items():
            if k not in keys:
                err.append(f"h3_override: '{k}' is not a plan h3 (inventory.json plan.main_flows): {keys}")
            elif not isinstance(v, dict) or not v.get("title") or not v.get("why"):
                err.append(f"h3_override '{k}': give {{\"title\": \"<shown h3>\", \"why\": \"<what the graph gets wrong>\"}}")
            else:
                NOTES.append(f"Main flows: plan h3 '{k}' shown as '{v['title']}': {v['why']}")
        want = [over[k]["title"] if isinstance(over.get(k), dict) and over[k].get("title") and over[k].get("why") else k for k in keys]
    groups, cur = [], None
    for b in blocks:
        if b["type"] == "h3":
            cur = {"h3": b["text"], "steps": None, "flows": []}
            groups.append(cur)
        elif cur and b["type"] == "steps" and cur["steps"] is None:
            cur["steps"] = len(b["rows"])
        elif cur and b["type"] == "flow" and not b.get("parent"):  # a sub-flow keeps its "inside <box>" title
            cur["flows"].append(b)
            if len(cur["flows"]) == 2:
                err.append(f"Main flows: '{cur['h3']}' has a second flow {b.get('id', '?')} without parent: one flow per h3, "
                           f"more only as sub-flows (parent: [\"<id>\", \"<box>\"])")
    h3s = [g["h3"] for g in groups]
    if pm is None:
        err += [f"Main flows: h3 '{t}' must read '<input> → <output>'" for t in h3s if "→" not in t]
    elif h3s != want:
        err.append(f"Main flows: h3 titles must be the plan's, in order (inventory.json plan.main_flows, or h3_override): want {want}, got {h3s}")
    for k, g in enumerate(groups):
        m = pm[k] if pm is not None and k < len(pm) and h3s == want else None
        n = g["steps"] or 0
        if m is not None and "diagram" in m:
            if m["diagram"] and not g["flows"]:
                err.append(f"Main flows: '{g['h3']}' needs a flow diagram (plan: {m['steps']} ordered steps, diagram: true)")
            if not m["diagram"] and g["flows"]:
                err.append(f"Main flows: '{g['h3']}' has no diagram in the plan (diagram: false: fewer than 3 ordered steps "
                           f"in the graph): leave the flow out, the steps table shows it")
            if m.get("ordered") and m["steps"] and n * 2 < m["steps"]:
                warn.append(f"Main flows: '{g['h3']}' has {n} steps rows, the graph flow {m['steps']} ordered steps (want at least half)")
        for f in g["flows"][:1]:
            got = arrow_count(f)
            gen = f"{(m or {}).get('entry') or entry_of(g['h3'])}, {got} steps"
            if f.get("title") and f["title"] != gen:
                err.append(f"diagram {f.get('id', '?')}: a Main flows title is written by the build: leave out title (it is '{gen}'), got '{f['title']}'")
            f["title"], f["_main"] = gen, True
            if not f.get("numbered", True):
                err.append(f"diagram {f.get('id', '?')}: a Main flows diagram is numbered (leave out numbered: false)")
            if got != n:
                warn.append(f"diagram {f.get('id', '?')}: {got} numbered arrows but {n} steps rows under '{g['h3']}': "
                            f"N = the arrows everywhere: one steps row per arrow, row k = arrow k")
            ok = set((m or {}).get("boxes") or []) | ENTRIES
            off = [x["label"] for x in f.get("nodes", []) if x.get("kind") in ("code", "entry") and m and m.get("boxes")
                   and bare(x["label"]) not in ok]
            if off:
                warn.append(f"diagram {f.get('id', '?')}: code/entry boxes {off} are not steps of the plan flow under '{g['h3']}' "
                            f"(plan boxes: {m['boxes']}) nor entry points: use the step names, or a plain box for an added step")


def operations_h3(blocks, plan, err, warn):
    """Technical Operations h3s: "Rerun and backfill" (pipelines only) or a plan how-to (process node), exact name;
    every plan how-to has its h3."""
    hows = (plan or {}).get("how_tos")
    rerun = not plan or plan.get("rerun_and_backfill", True)
    for b in blocks:
        t = b.get("text", "") if b["type"] == "h3" else None
        if t is None or (t == RERUN and rerun) or (t in hows if hows is not None else t.startswith("How to ")):
            continue
        err.append(f"Operations: h3 '{t}' must be " + (f"'{RERUN}' or " if rerun else "")
                   + (f"a plan how-to (inventory.json plan.how_tos: {hows})" if hows is not None else "'How to …'")
                   + ("" if rerun else f" ('{RERUN}' is for pipelines and dbt only)"))
    have = [b.get("text") for b in blocks if b["type"] == "h3"]
    miss = [h for h in hows or [] if h not in have]
    if miss:
        warn.append(f"Operations: plan how-tos without an h3: {miss} (one h3 + steps each, in plan order)")


def check(spec, kind, names, plan):
    """Return (errors, warnings). Errors: wrong blocks or order, labels, row lengths. Warnings: minimums."""
    err, warn = [], []
    have = {slot(kind, n) for n in names}
    sec = (plan or {}).get("sections", {}).get(kind)
    if sec:
        want, na = sec["required"], sec.get("not_applicable", {})
        err += [f"{n}: not applicable to this repo ({na[slot(kind, n)]}; plan in inventory.json): leave the section out"
                for n in names if slot(kind, n) in na]
        if sorted(spec.get("app_types", [])) != sorted(plan.get("app_types", [])):
            warn.append(f"app_types {spec.get('app_types', [])} differ from the plan's {plan.get('app_types', [])}: use the plan's")
    else:
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
        fixed, sc = H3_FIXED.get((kind, n)), STEP_COLS.get((kind, slot(kind, n)))
        main = kind == "technical" and n == "Main flows"
        POS["h3text"] = ""
        for b in blocks:
            t = b["type"]
            if t == "steps" and sc and b.get("cols") not in (None, sc):
                err.append(f"{n}: steps columns are fixed here: leave out cols (the build uses {sc}), got {b['cols']}")
            cols = len(TYPED[t]) if t in TYPED else len(b["cols"]) if t == "table" else \
                len(step_cols(b, kind, slot(kind, n))) if t == "steps" else 0
            err += [f"{n}: {t} row has {len(r)} cells, want {cols}: {r}" for r in b.get("rows", []) if cols and len(r) != cols]
            if t == "h3":
                POS["h3text"] = b["text"]
            if t == "examples":
                example_items(n, b, err, warn, main)
            if t == "er" and len(b["entities"]) > 9:
                err.append(f"{n}: ER has {len(b['entities'])} tables (max ~9): split it into one ER per area")
            if t == "h3" and fixed and not b["text"].startswith(fixed):
                err.append(f"{n}: h3 must start with '{fixed}', got '{b['text']}'")
        if kind == "overview" and n in ("What it is and why", "Value and cost"):
            got = [a for b in blocks if b["type"] == "labels" for a, _ in b["items"]]
            first = n == "What it is and why"
            if not (got[:4] == L0_LABELS if first else got and set(got) <= {"Value", "Cost"}):
                err.append(f"{n}: labels must be " + (f"{L0_LABELS} first" if first else "Value or Cost") + f", got {got}")
        if main:
            main_flows(spec, blocks, plan, err, warn)
        elif (slot(kind, n) == "How to *" or (kind, n) in (("overview", "Example"), ("technical", "Business rules"))) \
                and not set(types) & EXAMPLE_BLOCKS:
            warn.append(f"no example in: {n}")
        if kind == "technical" and n == "Operations":
            operations_h3(blocks, plan, err, warn)
        if kind == "technical" and n == "Architecture" and (plan or {}).get("api") and "api" not in types:
            warn.append(f"Architecture: library public API ({len(plan['api'])} functions and classes, inventory.json plan.api): "
                        f"add an `api` table, one row per call (Call · Returns · Raises · Where)")
        dep = (plan or {}).get("deploy")
        if kind == "technical" and n == "Deploy and environments" and isinstance(dep, dict):
            text = " ".join(strings(blocks)).replace("`", "")
            miss = [x for x in dep.get("units", []) + [d.split(" → ")[0] for d in dep.get("deploys", [])]
                    if not re.search(rf"(?<!\w){re.escape(x)}(?!\w)", text)]  # whole words: `db` is not in `dbt`
            if miss:
                warn.append(f"Deploy and environments: {list(dict.fromkeys(miss))} from the graph (CI and compose jobs, deploys "
                            f"edges: inventory.json plan.deploy) are not named: one steps row or environments row each")
        if kind == "technical" and n == "Business rules":  # every rule gets an example card, or points to one
            rows = [r for b in blocks if b["type"] == "rules" for r in b["rows"]]
            refs = sum(1 for r in rows if EXREF.search(" ".join(map(str, r))))
            cards = sum(len(b["items"]) for b in blocks if b["type"] == "examples")
            if cards < len(rows) - refs:
                warn.append(f"Business rules: {len(rows)} rules, {refs} point to an existing example ('see Example 5.1a'), "
                            f"{cards} example cards (one card per other rule at least)")
    if kind == "overview":
        amounts(spec, err, warn)
    top_issues(spec, err, warn)
    sub = str(spec.get("subtitle", ""))
    if sub.count("·") != 2 or sub.count("→") != 1:
        warn.append(f"subtitle '{sub}': want '<stack> · <schedule> · <source> → <outputs>' (two ·, one →)")
    absolute = sorted({m for v in strings(spec) for m in ABS.findall(v)})
    if absolute:
        warn.append(f"absolute or machine paths in the spec: {absolute}: use paths from the repo root")
    diagram_ids(spec, names, err, warn, plan if kind == "technical" else None, kind)
    forms = ((plan or {}).get("diagram_titles") or diagram_titles(spec.get("app_types", []))).get(kind, {})
    for n in names:
        tops = [b for b in flat(spec["sections"][n]) if b["type"] == "flow" and not b.get("parent")]
        want = forms.get(slot(kind, n))
        for b in tops if want else []:
            title, arrows = str(b.get("title") or ""), arrow_count(b)
            if want == "area" and (not title.endswith(" area") or b.get("numbered", True) and arrows):
                err.append(f"diagram {b.get('id', '?')}: in {n} a flow is a map: title '<area> area' and numbered: false "
                           f"(plan diagram_titles), got '{title}'")
            elif want == "steps" and arrows and (title.endswith(" area") or not b.get("numbered", True)):
                err.append(f"diagram {b.get('id', '?')}: in {n} a flow is numbered steps: title '<entry>, {arrows} steps', numbered "
                           f"(plan diagram_titles), got '{title}'")
    seen = Counter(str(b.get("title")) for n in names for b in flat(spec["sections"][n]) if b["type"] in ("flow", "er", "journey"))
    err += [f"diagram title '{t}' is used {k} times: every title is unique (name the entry or area apart)" for t, k in seen.items() if k > 1]
    ellipsis(spec, names, err)
    return err, warn


ABS = re.compile(r"(?<![\w])[A-Za-z]:[\\/][^\s`'\"]*|(?<![\w.~])/(?:Users|home|root|tmp|var)/[^\s`'\"]*|(?<![\w])~/[^\s`'\"]*")
STEPS_TITLE = re.compile(r"^.+, (\d+) (steps|stages)$")


def diagram_ids(spec, names, err, warn, plan, kind=""):
    """Diagram ids (flow, er, journey) run A, B, C... in document order; the build writes "Diagram X ·".
    Every diagram needs an id and a title in a fixed form: "<entry>, <N> steps" (journey: stages) · "inside <box>"
    (sub-flow) · "<area> area" (flow) · "ER: <area>" (ER; in a technical doc the plan's areas, in order)."""
    ds = [(n, b) for n in names for b in flat(spec["sections"][n]) if b["type"] in ("flow", "er", "journey")]
    ids = [b["id"] for _, b in ds if b.get("id")]
    want = [chr(65 + k) for k in range(len(ids))]
    if ids != want:
        err.append(f"diagram ids must run {want} in document order (flows, ERs and journeys together), got {ids}")
    ers = []
    for n, b in ds:
        title, did, t = str(b.get("title") or ""), b.get("id") or "", b["type"]
        if not did or not title:
            err.append(f"{n}: {t} '{title or did or '(no id, no title)'}' needs an id (next letter) and a title")
        if title.lower().startswith("diagram"):
            err.append(f"diagram {did}: title '{title}' starts with 'Diagram': give the name only (the build adds 'Diagram X ·')")
        refs = [x["see"] for x in b.get("nodes", []) if x.get("see")] + ([b["parent"][0]] if b.get("parent") else [])
        err += [f"diagram {did}: see/parent '{r}' is not a diagram id in this doc" for r in refs if r not in ids]
        if t == "flow" and b.get("edges"):
            linked = {e[k] for e in b["edges"] for k in ("from", "to")}
            loose = [x["label"] for x in b["nodes"] if x["id"] not in linked]
            if loose:
                warn.append(f"diagram {did}: boxes without an arrow: {loose} (connect them or leave them out)")
        for x in b.get("nodes", []) if t == "flow" else []:
            outs = len({e["to"] for e in b.get("edges", []) if e.get("from") == x["id"]})
            if x.get("kind") == "decision" and outs < 2:
                warn.append(f"diagram {did}: decision box '{x['label']}' has {outs} outgoing arrow{'s' if outs != 1 else ''} "
                            f"(want one per branch, at least 2; else make it a plain box)")
        if not title:
            continue
        m = STEPS_TITLE.match(title)
        if t == "er":
            ers.append(title)
            if not title.startswith("ER: ") or len(title) < 5:
                err.append(f"diagram {did}: ER title '{title}' must be 'ER: <area>'")
        elif t == "flow" and b.get("parent"):
            if title != f"inside {b['parent'][1]}":
                err.append(f"diagram {did}: sub-flow title must be 'inside {b['parent'][1]}', got '{title}'")
        elif t == "journey":
            if not (m and m[2] == "stages" and int(m[1]) == len(b["stages"])):
                err.append(f"diagram {did}: journey title must be '<entry>, {len(b['stages'])} stages', got '{title}'")
        elif not b.get("_main"):  # Main flows titles are written by the build (main_flows)
            arrows = arrow_count(b)
            area = title.endswith(" area") and len(title) > 5
            if not (area or m and m[2] == "steps" and int(m[1]) == arrows and arrows):
                err.append(f"diagram {did}: flow title must be " + (f"'<entry>, {arrows} steps' (N = its arrows) or " if arrows else "")
                           + f"'<area> area', got '{title}'")
    areas = [a["title"] for a in (plan or {}).get("er_areas", [])]
    if plan and ers and ers != areas:
        err.append(f"Data model: ER titles must be the plan's areas, in order (inventory.json plan.er_areas): want {areas}, got {ers}")


DOTS = r"(?:…|\.\.\.)"
NAME_CUT = re.compile(rf"\w{DOTS}|{DOTS}\w")  # box labels, entity names: any ellipsis touching a name
UI_DOTS = re.compile(rf"(?<![\w./-])[A-Za-z][a-z]*{DOTS}(?!\w)")  # Loading..., Saving…: UI text, not a cut
CELL_CUT = re.compile(rf"\w{DOTS}\w|_{DOTS}|{DOTS}_|`[^`]*(?:\w{DOTS}|{DOTS}\w)[^`]*`")  # cells: only inside a name


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def ellipsis(spec, names, err):
    """A hand-shortened name (ab…yz, x_..._y) hides the real one: the build shortens names, the spec gives them in full.
    A plain word ending in an ellipsis ("Loading...", "Saving…") is UI text and allowed."""
    name_cut = lambda v: NAME_CUT.search(UI_DOTS.sub(" ", str(v or "")))
    cell_cut = lambda v: CELL_CUT.search(UI_DOTS.sub(" ", str(v)))
    bad = []
    for n in names:
        for b in flat(spec["sections"][n]):
            t = b["type"]
            if t == "flow":
                bad += [(n, x[k]) for x in b["nodes"] for k in ("label", "sub", "in", "out") if name_cut(x.get(k))]
            elif t == "er":
                bad += [(n, v) for e in b["entities"] for v in [e["name"]] + [c[0] for c in e["cols"]] if name_cut(v)]
            elif t in TYPED or t in ("table", "steps", "examples", "journey", "issues"):
                part = b.get("rows", b.get("items", b.get("stages", [])))
                bad += [(n, v) for v in strings(part) if cell_cut(v)]
    bad += [("tabs", v) for v in strings(spec.get("tabs", {})) if cell_cut(v)]
    err += [f"{n}: hand-shortened name '{v}': give the full name, or a pattern with * (the build shortens long names "
            f"and keeps the full one in the hover tip)" for n, v in bad]


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def graph_folder():
    """The graph folder (.knowledge-graph pointer, else <repo>-knowledge-graph/) or None, and why it is missing."""
    return find_graph()


def graph_commit():
    g, _ = graph_folder()
    return meta_commit(graph_meta(g)) if g else ""


def stamp(spec, out_dir, files, stale_n):
    """Repo commit (+dirty) or "repo not in git" · graph commit or build date (+ stale files) · review."""
    parts = []
    head = git("rev-parse", "--short", "HEAD")
    if head:
        try:  # the docs being rebuilt must not make the repo look dirty
            rel_out = out_dir.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            rel_out = "."
        skip = [f":(exclude){rel_out}"] if rel_out != "." else []
        parts.append(f"repo {head}" + ("+dirty" if git("status", "--porcelain", "--", ".", *skip) else ""))
    elif files:
        parts.append("repo not in git")
    g, _ = graph_folder()
    if g and files:
        meta = graph_meta(g)
        c, d = meta_commit(meta), meta_date(meta)
        parts.append((f"graph {c}" if c else f"graph built {d}" if d else "graph") + (f" (stale: {stale_n} files changed since)" if stale_n else ""))
    if spec.get("review"):
        parts.append(f"review {spec['review']}")
    return f'<p class="sub1 stamp">{" &middot; ".join(esc(p) for p in parts)}</p>' if parts else ""


def review_files():
    """Every file in a reviews/ folder anywhere in the repo (tool and hidden folders skipped)."""
    out = []
    for d, dirs, fs in os.walk("."):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS - {"reviews"} and not x.startswith("."))
        if "reviews" in Path(d).parts:
            out += [Path(os.path.relpath(Path(d) / f)).as_posix() for f in sorted(fs) if not f.startswith(".")]
    return out


def review_time(p):
    """When a review was written: its last commit, else a YYYY-MM-DD date in its name or first 60 lines, else None."""
    t = git("log", "-1", "--format=%ct", "--", p)
    if t:
        return int(t)
    head = "\n".join(Path(p).read_text(encoding="utf-8", errors="ignore").splitlines()[:60])
    m = re.search(r"(?<!\d)(20\d\d)-(\d\d)-(\d\d)(?!\d)", Path(p).name + "\n" + head)
    if not m:
        return None
    try:
        return datetime(int(m[1]), int(m[2]), int(m[3]), 23, 59, 59, tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None


def code_time(files, root):
    """Last change to the code: the last commit outside reviews/ and the docs, else the newest repo file's mtime."""
    t = git("log", "-1", "--format=%ct", "--", ".", ":(glob,exclude)**/reviews/**", ":(glob,exclude)**/generated-docs/**")
    if t:
        return int(t)
    return max([(root / f).stat().st_mtime for f in files if (root / f).is_file()], default=None)


def review_warn(spec, files, root):
    """Known issues come from one code review, named in the spec. Code changed after the review → its findings may be
    fixed: the accuracy reviewer opens each Must/Should `where` and marks fixed ones "Fixed since review"."""
    named = spec.get("review")
    if named and not Path(named).is_file():
        return [f"review file not found: {named}"]
    if not named:
        found = sorted(review_files(), key=lambda f: (review_time(f) or 0, f))
        return [f'set "review" to the code review the known issues come from (newest: {found[-1]}; '
                f'{len(found)} files in reviews/ folders)'] if found else []
    rt, ct = review_time(named), code_time(files, root) if files else None
    fix = "open each Must/Should `where`; fixed in code → status 'Fixed since review' and out of Top issues"
    if rt is None:
        return [f"review {named} has no date (not in git, no YYYY-MM-DD in its name or head): {fix}"]
    if ct and ct > rt:
        return [f"review {named} is older than the last code change: {fix}"]
    return []


# ---------- checks against the repo and the graph ----------
MARKER = ".generated-by-darshan-singh-meel-docs"
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "reviews", "analysis"}
EXT = ("py|ipynb|sql|ya?ml|json|jsonl|md|toml|cfg|ini|conf|template|tpl|j2|ts|tsx|js|jsx|mjs|sh|ps1|java|kt|scala|go|rs|"
       "rb|cs|php|tf|hcl|xml|html|css|txt|csv|gradle|properties")
PATH_RE = re.compile(r"(?<![\w./*<>{}-])([\w./-]*\w\.(?:" + EXT + r"))(?!\.?[\w*(])(?::(\d+(?:\s?[-–,]\s?\d+)*))?")
SPACED = re.compile(r"`([^`]*\s[^`]*\w\.(?:" + EXT + r"))(?::(\d+(?:\s?[-–,]\s?\d+)*))?`")  # `Some Folder/app.py:12`
METHOD = re.compile(r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|WS|WEBSOCKET)\s+(/\S*)")


def paths_in(text, have):
    """(path, lines) cited in a text: a backticked repo path with spaces as a whole, then PATH_RE on the rest."""
    got = []
    for m in SPACED.finditer(text):
        if m[1] in have:
            got.append((m[1], m[2] or ""))
            text = text.replace(m[0], " ")
    return got + PATH_RE.findall(text)


def repo_files(spec_path, out_dir):
    """Repo files for the path and name checks, as paths from the repo root: git's list (tracked + untracked, not
    ignored), else every file under the cwd. Left out: the output and spec folders, folders holding the marker, the
    graph, reviews/, analysis/ and tool folders. None (e.g. an example built in an empty folder) → checks skipped."""
    top = git("rev-parse", "--show-toplevel")
    root = Path(top or ".").resolve()
    if top:
        rels = git("-C", str(root), "-c", "core.quotepath=off", "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    else:
        rels = []
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            rels += [(Path(d) / f).relative_to(root).as_posix() for f in fs]
    g, _ = graph_folder()
    blocked, memo = {p.resolve() for p in (out_dir, Path(spec_path).parent, g) if p}, {}

    def free(d):  # a blocked root drops only the files directly in it
        if d not in memo:
            memo[d] = d not in blocked and not (d / MARKER).exists() and (d.parent == root or d == root or free(d.parent))
        return memo[d]
    return root, [r for r in rels if not set(r.split("/")) & SKIP_DIRS and free((root / r).parent)]


def ticks(spec, names):
    """(section, text inside `backticks`) for every string in the doc, tabs included; an issue's suggested `fix` is
    left out (it may name what does not exist yet)."""
    for n, part in [("tabs", spec.get("tabs", {}))] + [(n, spec["sections"][n]) for n in names]:
        if n != "tabs":
            part = [dict(b, items=[{k: v for k, v in i.items() if k != "fix"} if isinstance(i, dict) else i for i in b["items"]])
                    if b.get("type") == "issues" else b for b in part]
        for s in strings(part):
            yield from ((n, m) for m in re.findall(r"`([^`]+)`", s))


def cite_texts(spec, names):
    """source, where and Where-column fields are read whole; any other text only inside `backticks`."""
    for n, m in ticks(spec, names):
        yield n, f"`{m}`"
    for n in names:
        for b in flat(spec["sections"][n]):
            items = [c for c in b.get("items", []) if isinstance(c, dict)]
            whole = [b.get("source")] + [c.get(k) for c in items for k in ("source", "where")]
            if b["type"] in TYPED and "Where" in TYPED[b["type"]]:
                k = TYPED[b["type"]].index("Where")
                whole += [r[k] for r in b["rows"] if len(r) > k]
            yield from ((n, w) for w in whole if isinstance(w, str))


def line_count(p):
    data = p.read_bytes()
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def cites(spec, names, root, files, err, warn):
    """Every cited path exists (from the repo root) and every cited line is inside its file."""
    base, seen, (graph, _) = {}, set(), graph_folder()
    for f in files:
        base.setdefault(f.rsplit("/", 1)[-1], []).append(f)
    have = set(files)
    for n, text in cite_texts(spec, names):
        for p, lines in paths_in(text, have):
            if (p, lines) in seen:
                continue
            seen.add((p, lines))
            if p.startswith("/") or ".." in p.split("/"):
                err.append(f"{n}: cited path `{p}` is absolute or leaves the repo: paths are from the repo root")
                continue
            q = p[2:] if p.startswith("./") else p
            if "/" not in q and q not in have:
                hits = base.get(q, [])
                if len(hits) != 1:
                    warn.append(f"{n}: file name `{q}` matches {len(hits)} repo files" + (f" ({', '.join(hits[:4])})" if hits else "")
                                + ": use the path from the repo root")
                    continue
                q = hits[0]
            path = next((x for x in [root / q] + ([graph / q] if graph else []) if x.is_file()), None)
            if not path:
                near = [f for f in files if f.endswith("/" + q) or f.endswith(" " + q)][:3]
                err.append(f"{n}: cited path `{p}` is not in the repo" + (f" (did you mean {', '.join(near)}?)" if near else "")
                           + (": a path with spaces goes in backticks, whole: `Some Folder/app.py:12`" if any(" " in x for x in near)
                              else ": paths are from the repo root"))
            elif lines and not secret(q):
                last, total = max(int(x) for x in re.findall(r"\d+", lines)), line_count(path)
                if last > total:
                    err.append(f"{n}: `{p}:{lines}` is past the end of the file ({total} lines)")


def cite_content(spec, names, root, files, warn):
    """Rules, issues and unused rows: a cited line range must hold at least one of the row's backticked names."""
    have = set(files)
    for n in names:
        for b in flat(spec["sections"][n]):
            if b["type"] not in ("rules", "issues", "unused"):
                continue
            for row in b.get("rows", []) + b.get("items", []):
                texts = list(strings({k: v for k, v in row.items() if k not in ("fix", "test")} if isinstance(row, dict) else row))
                toks = {t for x in texts for m in re.findall(r"`([^`]+)`", x) for t in re.findall(r"\w{3,}", m)
                        if not PATH_RE.fullmatch(m.split(":")[0]) and m.split(":")[0] not in have}
                for p, lines in {c for x in texts for c in paths_in(x, have) if c[1]}:
                    f = root / (p[2:] if p.startswith("./") else p)
                    if not toks or secret(p) or not f.is_file():
                        continue
                    nums = [int(x) for x in re.findall(r"\d+", lines)]
                    got = f.read_text(encoding="utf-8", errors="ignore").splitlines()[min(nums) - 1:max(nums)]
                    if not any(re.search(rf"(?<!\w){re.escape(t)}(?!\w)", "\n".join(got)) for t in toks):
                        warn.append(f"{n}: `{p}:{lines}` holds none of {sorted(toks)}: check the cited lines")


def identifiers(spec, names, root, files, warn, kind, inv=None):
    """Backticked names (with _, 8+ chars) must occur in the repo as a whole word, same case; in a technical doc so
    must the label of every code, data and entry box. Also accepted: a repo path, path suffix or folder, `METHOD /path`
    when every word of the path is in the repo, an ALL_CAPS name in any case (settings read from the environment), any
    inventory item or entry point name (graph commands like `npm run dev`), and an external system name in any case
    (`Postgres`); any other name keeps its case. An issue's `absent` names (what the issue says is missing)
    are not looked up; one that is in the repo -> WARN."""
    absent = {a for i in issue_items(spec) for a in i.get("absent", []) if isinstance(i, dict)}
    skip, toks = set(spec.get("ids_skip", [])) | absent, {}
    for n, m in ticks(spec, names):
        t = re.sub(r"\(.*\)$", "", m.strip())  # f(x) -> f
        if "_" in t and len(t) >= 8 and not re.search(r"[\s/<{*]", t) and not PATH_RE.search(t) and t not in skip:
            toks.setdefault(t, n)
    boxes = {}
    if kind == "technical":
        for n in names:
            for b in flat(spec["sections"][n]):
                for x in b.get("nodes", []) if b["type"] == "flow" else []:
                    lab = re.sub(r"\(.*\)$", "", str(x.get("label", "")).strip().strip("`"))
                    if x.get("kind") in ("code", "data", "entry") and lab and lab not in skip:
                        boxes.setdefault(lab, (n, b.get("id", ""), x["kind"]))
    if not toks and not boxes and not absent:
        return
    known = {x["name"] for v in (inv or {}).get("items", {}).values() for x in v} | {e["name"] for e in (inv or {}).get("entry_points", [])}
    known |= {f["name"] for f in (inv or {}).get("flows", [])}
    ext = {x["name"].lower() for x in (inv or {}).get("items", {}).get("external_system", [])}
    folders = {f.rsplit("/", k)[0] for f in files for k in range(1, f.count("/") + 1)}
    words, texts = {f.rsplit("/", 1)[-1].split(".")[0] for f in files}, []  # a file name counts too (module.func)
    names_ = set(files) | {f.rsplit("/", 1)[-1] for f in files}
    for f in files:
        p = root / f
        try:
            if secret(f) or p.stat().st_size > 2_000_000:
                continue
            data = p.read_bytes()
        except OSError:
            continue
        if b"\0" not in data[:8192]:
            texts.append(data.decode("utf-8", "ignore"))
            words.update(re.findall(r"\w+", texts[-1]))
    lower = {w.lower() for w in words}

    def found(t):  # module.func or schema.table: each part may stand alone in the code
        parts_ = t.split(".")
        m = METHOD.fullmatch(t)
        if m:
            return all(w in words for s in m[2].split("/") if s and s[0] not in "{<:[" for w in re.findall(r"\w+", s))
        return (t in names_ or t in known or t.rstrip("/") in folders or t.lower() in ext
                or ("/" in t and any(f.endswith("/" + t) for f in files))
                or (t in words if re.fullmatch(r"\w+", t) else any(re.search(rf"(?<!\w){re.escape(t)}(?!\w)", x) for x in texts))
                or (re.fullmatch(r"[A-Z0-9_]+", t) and t.lower() in lower)
                or len(parts_) > 1 and all(re.fullmatch(r"\w+", q) and q in words for q in parts_))
    for t, n in toks.items():
        if not found(t):
            warn.append(f"{n}: `{t}` not found in repo: fix the name (exact case), or add it to ids_skip if it is synthetic")
    for t in sorted(absent):
        if found(t):
            warn.append(f"known issues: `{t}` is listed as absent but is in the repo: check the issue")
    for t, (n, did, k) in boxes.items():
        if not found(t):
            warn.append(f"{n}: diagram {did}: {k} box '{t}' not found in repo: label it with the real name (file, function, "
                        f"table, `METHOD /path`, as in the code), or add it to ids_skip")


def visible(page):
    """The text a reader sees: no tags, no hover tips, no CSS; names joined again where the build put break points."""
    page = re.sub(r"<style>.*?</style>|<title>.*?</title>", " ", page, flags=re.S)
    page = re.sub(r'<wbr>|<span class="nw">([^<]*)</span>', lambda m: m[1] or "", page)
    return html.unescape(re.sub(r"<[^>]+>", " ", page))


def coverage(spec, page, inv, warn):
    """Technical docs: every inventory item of a covered type (plan.coverage), by its exact name, in visible text.
    A name defined in several places (N paths) is named N times, or with its count next to it."""
    arrows = lambda x: re.sub(r"\s*(?:->|→)\s*", " → ", x)  # a flow name's -> is written → in its h3
    page_text, skip = arrows(visible(page)), spec.get("coverage_skip", {})
    calls = " | ".join(str(r[0]) for b in flat(spec["sections"].get("Architecture", [])) if b["type"] == "api" for r in b["rows"] if r)
    for t in inv["plan"]["coverage"]:
        api = t == "api"  # library public API: each name in the Call column of the api table
        names = inv["tests"] if t == "test_file" else [x["name"] for x in (inv["plan"].get("api", []) if api else inv["items"].get(t, []))
                                                       if not x.get("ci")]
        text = calls.replace("`", "") if api else page_text
        defs = Counter(names)
        want = sorted({x for x in names if x and x not in skip and len(re.findall(r"\w", x)) >= 2})
        pat = lambda x: rf"(?<!\w){re.escape(arrows(x))}(?!\w)"
        miss = [x for x in want if not re.search(pat(x), text)]
        few = [f"{x} ({defs[x]} definitions, named {k} times)" for x in want if defs[x] > 1 and x not in miss
               for k in [len(re.findall(pat(x), text))]
               if k < defs[x] and not re.search(pat(x) + rf".{{0,40}}?(?<![\d.]){defs[x]}(?![\d.])", text)]
        if miss:
            warn.append(f"coverage: {len(miss)} of {len(want)} {t} items from inventory.json are not in the "
                        f"{'Call column of the Architecture api table' if api else 'visible text'}: "
                        f"{', '.join(x + (f' ({defs[x]} definitions)' if defs[x] > 1 else '') for x in miss)} "
                        f"(name each exactly in a table row, step or box label; hover tips do not count; or add coverage_skip {{name: why}})")
        if few:
            warn.append(f"coverage: {len(few)} {t} names are defined in several places but named fewer times: {', '.join(few)} "
                        f"(name each definition, or write the count next to the name: `var.region` (4 modules))")


def load_plan(spec_path, files, warn, kind):
    """inventory.json next to the spec (written by inventory.py), or None with a WARN saying what is not checked."""
    what = "coverage" if kind == "technical" else "plan"
    p = Path(spec_path).parent / "inventory.json"
    g, why = graph_folder()
    if not files:
        return None
    if not p.is_file():
        warn.append(f"{what} not checked: no {rel(p)}" + (f" ({why}: build the graph first)" if not g else f": run {HOW}"))
        return None
    try:
        inv = json.loads(p.read_text(encoding="utf-8"))
        inv["plan"]["coverage"], inv["items"]
    except (ValueError, KeyError, TypeError):
        warn.append(f"{what} not checked: {rel(p)} is not an inventory.py file: rerun {HOW}")
        return None
    if inv.get("templates") != version():
        warn.append(f"inventory.json was written by templates {inv.get('templates') or '(older, no version)'}, this build.py is "
                    f"{version()}: rerun {HOW} from the loaded skill's folder (never a copy inside the repo)")
    gc = graph_commit()
    if gc and inv.get("graph_commit") and gc != inv["graph_commit"]:
        warn.append(f"inventory.json is from graph {inv['graph_commit']}, the graph is now {gc}: rerun {HOW}")
    return inv


def freshness(warn):
    """Graph vs repo: the graph's commit against HEAD, and meta.json file hashes against the files. Returns the
    number of stale files (for the stamp)."""
    g, _ = graph_folder()
    if not g:
        return 0
    meta, head = graph_meta(g), git("rev-parse", "HEAD")
    gc = meta_commit(meta)
    if head and gc and not head.startswith(gc):
        warn.append(f"graph is from commit {gc}, the repo is at {head[:12]}: update the graph, then rerun {HOW}")
    old = stale(meta)
    if old:
        warn.append(f"graph is stale: {len(old)} files changed since it was built ({', '.join(old[:5])}"
                    f"{', ...' if len(old) > 5 else ''}): update the graph, then rerun {HOW}")
    return len(old)


def facts_warn(spec_path, root, files, warn):
    """facts.json next to the spec: every count with a `how` that reruns from the repo root (one POSIX shell line)."""
    p = Path(spec_path).parent / "facts.json"
    if not files:
        return
    if not p.is_file():
        warn.append(f"no {rel(p)}: run {HOW} (it writes the counts); add each other number in the doc with its `how`")
        return
    try:
        facts = json.loads(p.read_text(encoding="utf-8")).get("facts", [])
    except (ValueError, AttributeError):
        warn.append(f"{rel(p)} is not valid JSON {{facts: [{{fact, value, how}}]}}")
        return
    for f in facts:
        how = str(f.get("how", "")) if isinstance(f, dict) else ""
        try:
            toks = shlex.split(how)
        except ValueError:
            toks = how.split()
        # paths only in tokens with "/" and no backslash (a regex like a\.py is not a path); <skill>/… is fine
        cands = [q for x in toks if "\\" not in x and not x.startswith("<skill>") for q, _ in PATH_RE.findall(x) if "/" in q]
        bad = [q for q in cands if q.startswith(("/", "~")) or ".." in q.split("/") or not (root / q).exists()] + ABS.findall(how)
        if not how or bad:
            warn.append(f"facts.json: '{f.get('fact') if isinstance(f, dict) else f}': how {how!r} must rerun from the repo root "
                        f"(files outside the repo or missing: {bad})")


def fact_numbers(page, spec_path, warn):
    """A number the text gives with a fact's name ("12 test files") must be that fact's value in facts.json, or the
    value of another fact whose name holds that name (a sub-count: "6 views" with fact "views with deletion_time" = 6)."""
    try:
        facts = json.loads((Path(spec_path).parent / "facts.json").read_text(encoding="utf-8")).get("facts", [])
    except (OSError, ValueError, AttributeError):
        return
    text = re.sub(r"\s+", " ", visible(re.sub(r'<nav class="toc">.*?</nav>|<h2 .*?</h2>', " ", page, flags=re.S)))  # no section numbers
    nums = [f for f in facts if isinstance(f, dict) and re.fullmatch(r"\d+", str(f.get("value", "")))]
    plain = lambda f: re.sub(r"\s*\(.*?\)", "", str(f.get("fact", ""))).strip()
    for f in nums:
        name = plain(f)
        ok = {str(g["value"]) for g in nums if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", plain(g), re.I)} if name else set()
        got = {m[0] for m in re.finditer(rf"(?<![\w.,])(\d+) {re.escape(name)}(?!\w)", text, re.I) if m[1] not in ok} if name else set()
        warn += [f"text says '{x}' but facts.json '{f['fact']}' is {f['value']}: use the fact's value" for x in sorted(got)]


def synthetic_share(spec, names, tests, warn):
    """Tests exist → cases come from them first: card a of a main flow not synthetic, at most a third synthetic."""
    cards, h3 = [], ""
    for n in names:
        for b in flat(spec["sections"][n]):
            h3 = b["text"] if b["type"] == "h3" else h3
            if b["type"] == "examples":
                cards += b["items"]
                if n == "Main flows" and b["items"] and b["items"][0].get("synthetic"):
                    warn.append(f"Main flows: example a under '{h3}' is synthetic while the repo has {len(tests)} test files: "
                                f"take the typical case from a test or fixture")
    syn = sum(1 for c in cards if c.get("synthetic"))
    if cards and 3 * syn > len(cards):
        warn.append(f"examples: {syn} of {len(cards)} cards are synthetic while the repo has {len(tests)} test files: "
                    f"take cases from the tests first (at most a third synthetic)")


def main(spec_path, out_path):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; spec text can hold arrows
    sys.stderr.reconfigure(encoding="utf-8")
    ver = version()
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    kind, sections = spec.get("type"), spec.get("sections")
    if kind not in list(ORDER) + ["custom"]:
        die(f"type '{kind}' unknown: use one of {list(ORDER) + ['custom']}")
    if not spec.get("title") or not isinstance(sections, dict):
        die("the spec needs a title and sections {name: [blocks]}")
    if kind == "custom":  # README, runbook, design doc...: free section names, written order, same look
        ORDER["custom"], REQUIRED["custom"], ISSUE_COLS["custom"] = [n for n in sections if n != LAST], {"*": []}, ISSUE_COLS["technical"]
    allowed = ORDER[kind] + [LAST]
    bad = [n for n in sections if slot(kind, n) not in allowed]
    if bad:
        die(f"sections not allowed for {kind}: {bad}. Allowed, in order: {allowed}")
    names = sorted(sections, key=lambda n: allowed.index(slot(kind, n)))  # stable sort keeps "How to" order
    out = Path(out_path)
    if not out.parent.is_dir():
        die(f"output folder {out.parent.as_posix()} does not exist: create it (mkdir -p {out.parent.as_posix()}), then rerun")
    root, files = repo_files(spec_path, out.parent)
    try:
        inside = Path(__file__).resolve().relative_to(root).as_posix() if files else ""
    except ValueError:
        inside = ""
    if inside:
        print(f"note: build.py runs from inside the documented repo ({inside}): use the loaded skill's folder, not a copy in the repo")
    pre = []
    inv = load_plan(spec_path, files, pre, kind)
    stale_n = freshness(pre) if files else 0
    ENTRIES.update(e["name"] for e in (inv or {}).get("entry_points", []))
    err, warn = check(spec, kind, names, inv and inv["plan"])
    if files:
        cites(spec, names, root, files, err, warn)
        cite_content(spec, names, root, files, warn)
        identifiers(spec, names, root, files, warn, kind, inv)
        facts_warn(spec_path, root, files, warn)
        if inv and inv.get("tests"):
            synthetic_share(spec, names, inv["tests"], warn)
    else:
        print(f"note: no repo files under {root.name or root}: path, name, plan, coverage and facts checks skipped")
    warn = list(dict.fromkeys(pre + warn + review_warn(spec, files, root)))
    for x in NOTES:
        print("note:", x)
    for w in warn:
        print("WARN", w)
    if err:
        sys.exit("\n".join(f"ERROR {e}" for e in err))
    title = lambda i, n: f"{i + 1} {n}"
    toc = "".join(f'<a href="#s{i}">{esc(title(i, n))}</a>' for i, n in enumerate(names))
    src = (f'<p class="src">Known issues from review <code>{esc(spec["review"])}</code></p>' if spec.get("review") else
           '<p class="src">No code review: severity by the fixed rubric; Confirmed only where a test or the code proves it</p>'
           if issue_items(spec) else "")
    body = ""
    for i, n in enumerate(names):
        POS.update(kind=kind, slot=slot(kind, n), sec=i + 1, h3=0, ex=0)
        body += (f'<section><h2 id="s{i}">{esc(title(i, n))}</h2>{src if n == LAST else ""}'
                 f'{"".join(block(b, kind) for b in sections[n])}</section>')
    css = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
    sub = f'<p class="sub1">{esc(spec["subtitle"])}</p>' if spec.get("subtitle") else ""
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-docs-v2 {ver}"><title>{esc(spec["title"])}</title><style>{css}</style></head><body><main>'
            f'<div class="eyebrow">{kind.replace("-", " ")}</div><h1>{esc(spec["title"])}</h1>{stamp(spec, out.parent, files, stale_n)}{sub}'
            f'{tabs(spec)}<nav class="toc">{toc}</nav>{body}</main></body></html>')
    ids = set(re.findall(r'id="ex-([^"]+)"', page))
    dangling = sorted(set(EXREF.findall(visible(page))) - ids)
    if dangling:
        sys.exit(f"ERROR text names Example {', '.join(dangling)}, which the doc does not have (ids are <section>.<h3><letter>, "
                 f"as the build numbers the cards)")
    late = list(dict.fromkeys(LATE))
    if kind == "technical" and inv:
        coverage(spec, page, inv, late)
    if files:
        fact_numbers(page, spec_path, late)
    for w in late:
        print("WARN", w)
    out.write_bytes(page.encode("ascii", "xmlcharrefreplace"))  # pure ASCII: every non-ASCII character as an entity
    (out.parent / MARKER).touch()  # the graph skill skips folders holding this
    print(f"built {out_path}: {len(names)} sections, {len(warn) + len(late)} WARN (templates {ver})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
