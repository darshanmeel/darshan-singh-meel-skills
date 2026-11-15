"""Diagram engine: JSON spec -> static SVG (light + dark), Mermaid text and a geometry record for check.py.
Usage: python diagram.py spec.json -o out.svg [--mermaid out.mmd] [--page out.html] [--fragment out.html]
                         [--geometry out.json] [--png out.png] [--dark]
       python diagram.py --list
Graph styles for any node-edge type: plain, dbt (lineage look), airflow (DAG graph-view look); see references/spec.md.
Types: built-in boxes, layers, grid, plus the TYPES dict of every
../../darshan-singh-meel-diagrams-*/scripts/types_*.py next to this skill (and files or folders in $DIAGRAM_TYPES).
Python API: build(spec) -> {"svg", "html", "geometry", "mermaid", "errors", "warnings"}. Contract: references/engine.md."""
import sys

sys.dont_write_bytecode = True  # family modules load from skill folders: no __pycache__ there
import argparse, bisect, datetime, heapq, html, importlib.util, json, math, os, re, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.modules.setdefault("diagram", sys.modules[__name__])  # run as a script: `import diagram` in a family gets this module
import check as checker  # noqa: E402

MAX_W = 1000
PADX, PADY, MARGIN, CLEAR, GP = 12, 9, 16, 10, 14
LABEL_COL = 130  # top-down layouts: width of the group-label column left of the members
SANS_K = 1.08  # Helvetica metrics scaled up: covers IBM Plex Sans, Segoe UI and Arial
TONES = ("plain", "soft", "teal", "amber", "lav", "green", "red", "blue", "ink")
SHAPES = ("box", "rounded", "pill", "circle", "cylinder", "document", "actor", "cloud", "diamond", "hexagon", "note")
HEADS = ("filled", "open", "none", "tri", "diamond", "odiamond", "circle",
         "one", "only-one", "zero-one", "many", "one-many", "zero-many")
STYLES = ("solid", "dashed", "dotted", "thick")
EDGE_TONES = ("", "red", "blue", "green", "muted", "teal", "amber", "lav")
LIGHT = dict(ground="#F6F6F3", card="#FFFFFF", line="#D9DBDF", ink="#17191D", muted="#5B6068", soft="#EEEFEC",
             teal="#DDF0EE", teal_ink="#1C5C57", amber="#FCEBC8", amber_ink="#8A5A00", lav="#E7E2F5", lav_ink="#6B4FA8",
             green="#1E6B43", green_bg="#E2F1E8", blue="#1F5FA8", blue_bg="#E2ECF8", red="#A12D2D", red_bg="#F8E3E3",
             edge="#40454D")
DARK = dict(ground="#141619", card="#1C1F24", line="#3A3F47", ink="#E8EAED", muted="#A4AAB3", soft="#272B32",
            teal="#173A37", teal_ink="#83D3C9", amber="#3B2E12", amber_ink="#EEC065", lav="#2B2540", lav_ink="#BCA9F0",
            green="#6CCB95", green_bg="#16301F", blue="#86B2EE", blue_bg="#172A42", red="#F09090", red_bg="#3A1C1C",
            edge="#B7BCC4")
SANS = '"IBM Plex Sans","Segoe UI",Arial,sans-serif'
MONO = '"IBM Plex Mono",Consolas,monospace'
_TONE_CSS = {"soft": ("soft", "muted"), "teal": ("teal", "teal-ink"), "amber": ("amber", "amber-ink"),
             "lav": ("lav", "lav-ink"), "green": ("green-bg", "green"), "red": ("red-bg", "red"),
             "blue": ("blue-bg", "blue"), "ink": ("ink", "ink")}
_SOLID = {"plain": "ink", "soft": "muted", "teal": "teal-ink", "amber": "amber-ink", "lav": "lav-ink",
          "green": "green", "red": "red", "blue": "blue", "ink": "ink"}
BASE_CSS = ("#S{font-family:" + SANS + "}#S text{white-space:pre}#S .dg-bg{fill:var(--dg-card)}"
            "#S .dg-sh{fill:var(--dg-card);stroke:var(--dg-ink);stroke-width:1.2}"
            "#S .dg-sh2{fill:none;stroke:var(--dg-ink);stroke-width:1.2}"
            + "".join(f"#S .dg-t-{t}>.dg-sh{{fill:var(--dg-{f});stroke:var(--dg-{s})}}" for t, (f, s) in _TONE_CSS.items())
            + "#S .dg-t-ink .dg-l,#S .dg-t-ink .dg-s,#S .dg-t-ink .dg-g{fill:var(--dg-card)}"
            "#S .dg-dash>.dg-sh{stroke-dasharray:5 4}#S .dg-strong>.dg-sh{stroke-width:2.4}"
            + "".join(f"#S .dg-solid.dg-t-{t}>.dg-sh{{fill:var(--dg-{v});stroke:var(--dg-{v})}}" for t, v in _SOLID.items())
            + "#S .dg-solid .dg-l,#S .dg-solid .dg-lm,#S .dg-solid .dg-s,#S .dg-solid .dg-g{fill:var(--dg-card)}"
            "#S .dg-dim{opacity:.4}#S .dg-lg{font-family:" + MONO + ";font-size:11px;fill:var(--dg-muted)}"
            "#S .dg-act{fill:none;stroke:var(--dg-ink);stroke-width:1.4}"
            "#S .dg-l{font-size:13px;font-weight:600;fill:var(--dg-ink)}"
            "#S .dg-lm{font-family:" + MONO + ";font-size:12.5px;font-weight:600;fill:var(--dg-ink)}"
            "#S .dg-s{font-size:12px;fill:var(--dg-muted)}"
            "#S .dg-g{font-family:" + MONO + ";font-size:10.5px;letter-spacing:.04em;fill:var(--dg-muted)}"
            "#S .dg-e{fill:none;stroke:var(--dg-edge);stroke-width:1.3}#S .dg-e.dashed{stroke-dasharray:6 4}"
            "#S .dg-e.dotted{stroke-dasharray:1.5 3.5;stroke-linecap:round}#S .dg-e.thick{stroke-width:2.6}"
            + "".join(f"#S .dg-e.c-{t}{{stroke:var(--dg-{v})}}#S .dg-mk.c-{t}{{fill:var(--dg-{v});stroke:var(--dg-{v})}}"
                      f"#S .dg-mko.c-{t},#S .dg-mkl.c-{t}{{stroke:var(--dg-{v})}}"
                      for t, v in (("red", "red"), ("blue", "blue"), ("green", "green"), ("muted", "muted"),
                                   ("teal", "teal-ink"), ("amber", "amber-ink"), ("lav", "lav-ink")))
            + "#S .dg-mk{fill:var(--dg-edge);stroke:var(--dg-edge);stroke-width:1}"
            "#S .dg-mko{fill:var(--dg-card);stroke:var(--dg-edge);stroke-width:1.3}"
            "#S .dg-mkl{fill:none;stroke:var(--dg-edge);stroke-width:1.3}"
            "#S .dg-lb rect{fill:var(--dg-card)}#S .dg-lb text{font-family:" + MONO + ";font-size:11px;fill:var(--dg-muted)}"
            "#S .dg-grp>rect{fill:var(--dg-lav);fill-opacity:.35;stroke:var(--dg-lav-ink);stroke-dasharray:5 4}"
            "#S .dg-grp>text{font-family:" + MONO + ";font-size:11px;fill:var(--dg-lav-ink)}"
            + "".join(f"#S .dg-grp.dg-t-{t}>rect{{fill:var(--dg-{f});stroke:var(--dg-{s})}}#S .dg-grp.dg-t-{t}>text{{fill:var(--dg-{s})}}"
                      for t, (f, s) in _TONE_CSS.items() if t != "ink")
            + "#S .dg-bnd>rect{fill:none;stroke:var(--dg-muted);stroke-dasharray:7 4}"
            "#S .dg-bnd>text{font-family:" + MONO + ";font-size:11px;fill:var(--dg-muted)}"
            "#S .dg-lane>rect,#S .dg-band>rect{fill:var(--dg-soft);stroke:var(--dg-line)}"
            "#S .dg-lane>text,#S .dg-band>text{font-family:" + MONO + ";font-size:11px;letter-spacing:.06em;fill:var(--dg-muted)}"
            "#S .dg-hd{fill:var(--dg-soft);stroke:var(--dg-line)}"
            "#S .dg-ax{stroke:var(--dg-line);stroke-width:1;fill:none}#S .dg-ax2{stroke:var(--dg-muted);stroke-width:1;fill:none;stroke-dasharray:3 3}"
            "#S .dg-today{stroke:var(--dg-red);stroke-width:1.5;stroke-dasharray:4 3;fill:none}"
            "#S .dg-tx{font-size:11px;fill:var(--dg-muted)}#S .dg-txm{font-family:" + MONO + ";font-size:11px;fill:var(--dg-muted)}"
            "#S .dg-txb{font-size:12px;font-weight:600;fill:var(--dg-ink)}"
            "#S .dg-title{font-size:15px;font-weight:600;fill:var(--dg-ink)}"
            "#S .dg-key{font-family:" + MONO + ";font-size:11.5px;fill:var(--dg-muted)}#S .dg-notice{font-size:12.5px;fill:var(--dg-ink)}")


class LayoutError(Exception):
    """Raise from a type module when a spec cannot be laid out; the message (with its fix) becomes a build error."""


# ---------- text ----------
_HW = ("278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 556 556 556 556 556 556 556 556 556 556 278 278 "
       "584 584 584 556 1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 667 778 722 667 611 722 667 944 "
       "667 667 611 278 278 278 469 556 333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 556 556 333 500 "
       "278 556 500 722 500 500 500 334 260 334 584")
_WIDTH = {chr(32 + i): int(v) for i, v in enumerate(_HW.split())}


def F(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(str(s), quote=True)


def text_width(s, size=13, mono=False, bold=False):
    """Width in px of one line, a little over the real width of the fonts in SANS / MONO."""
    if mono:
        return len(s) * 0.6 * size * (1.04 if bold else 1.0)
    u = sum(_WIDTH.get(ch, 600 if ord(ch) < 0x2000 else 1000) for ch in s)
    return u / 1000 * size * SANS_K * (1.07 if bold else 1.0)


def _pieces(word, width, size, mono, bold):
    if text_width(word, size, mono, bold) <= width:
        return [word]
    out, cur = [], ""
    for p in re.findall(r"[^/._\-:]+[/._\-:]*|[/._\-:]+", word):  # long identifiers break after / . _ - :
        if cur and text_width(cur + p, size, mono, bold) > width:
            out.append(cur)
            cur = p
        else:
            cur += p
    return out + [cur]


def wrap(s, width, size=13, mono=False, bold=False):
    """Word-wrap to width px. Never cuts inside a word; a too-long identifier breaks after / . _ - : only."""
    lines = []
    for para in str(s).split("\n"):
        cur = ""
        for w in para.split():
            for k, p in enumerate(_pieces(w, width, size, mono, bold)):
                t = (cur + ("" if k else " ") + p) if cur else p
                if cur and text_width(t, size, mono, bold) > width:
                    lines.append(cur)
                    cur = p
                else:
                    cur = t
        lines.append(cur)
    return [x for x in lines if x] or [""]


def text_blocks(n, width):
    """[(lines, size, mono, bold, line_height, css_class)] for a node's label, tag and sub."""
    out = []
    if n.get("label"):
        mono = bool(n.get("mono"))
        size = 12.5 if mono else 13
        out.append((wrap(n["label"], width, size, mono, True), size, mono, True, 17, "dg-lm" if mono else "dg-l"))
    if n.get("tag"):
        out.append((wrap(n["tag"], width, 10.5, True), 10.5, True, False, 14, "dg-g"))
    if n.get("sub"):
        out.append((wrap(n["sub"], width, 12), 12, False, False, 15, "dg-s"))
    return out


def block_size(blocks):
    tw = max([text_width(s, b[1], b[2], b[3]) for b in blocks for s in b[0]] or [0])
    return tw, sum(len(b[0]) * b[4] for b in blocks)


# ---------- shapes ----------
def size(n, max_w=200, min_w=96):
    """Outer (w, h) of a node dict (label, tag, sub, shape, mono, min_w, min_h) with its text wrapped inside."""
    shape = n.get("shape") or "rounded"
    wrapw = {"diamond": 130, "circle": 84, "cloud": max_w * 0.68, "actor": max_w - 8}.get(shape, max_w - 2 * PADX)
    tw, th = block_size(text_blocks(n, wrapw))
    if shape == "diamond":
        h = max(50, 2 * th + 16)
        w = max(tw / (1 - th / h) + 16, h * 1.5)
    elif shape == "circle":
        w = h = max(36, max(tw, th) / 0.7 + 6)
    elif shape == "cloud":
        w, h = tw / 0.68 + 10, max(56, th / 0.6 + 8)
    elif shape == "actor":
        w, h = max(tw + 8, 64), 44 + th + 4
    else:
        h = max(40, th + 2 * PADY) + {"cylinder": 16, "document": 8}.get(shape, 0)
        extra = {"pill": h * 0.4, "hexagon": h / 2}.get(shape, 0)
        w = max(min_w, tw + 2 * PADX + extra + 2)  # +2: float slack so node() wraps the same way
    n["_wrap"] = max(wrapw, tw)
    return math.ceil(max(w, n.get("min_w", 0))), math.ceil(max(h, n.get("min_h", 0)))


def inner(shape, x, y, w, h, th=0):
    """Text area of a shape."""
    if shape == "diamond":
        iw = w * (1 - th / h) - 8 if h else w
        return x + (w - iw) / 2, y + (h - th) / 2, iw, th
    if shape == "circle":
        s = min(w, h) * 0.7
        return x + (w - s) / 2, y + (h - s) / 2, s, s
    if shape == "cloud":
        return x + w * 0.16, y + h * 0.2, w * 0.68, h * 0.6
    if shape == "actor":
        return x + 4, y + 44, w - 8, h - 46
    if shape == "pill":
        return x + PADX + h * 0.2, y + PADY, w - 2 * PADX - h * 0.4, h - 2 * PADY
    if shape == "hexagon":
        return x + h / 4 + PADX, y + PADY, w - h / 2 - 2 * PADX, h - 2 * PADY
    if shape == "cylinder":
        return x + PADX, y + 16, w - 2 * PADX, h - 16 - PADY
    if shape == "document":
        return x + PADX, y + PADY, w - 2 * PADX, h - 2 * PADY - 8
    return x + PADX, y + PADY, w - 2 * PADX, h - 2 * PADY


def shape_svg(shape, x, y, w, h):
    c = 'class="dg-sh"'
    if shape in ("box", "rounded", "pill"):
        r = {"box": 3, "rounded": 8, "pill": h / 2}[shape]
        return f'<rect {c} x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{F(r)}"/>'
    if shape == "circle":
        return f'<circle {c} cx="{F(x + w / 2)}" cy="{F(y + h / 2)}" r="{F(min(w, h) / 2)}"/>'
    if shape == "diamond":
        return f'<polygon {c} points="{F(x + w / 2)},{F(y)} {F(x + w)},{F(y + h / 2)} {F(x + w / 2)},{F(y + h)} {F(x)},{F(y + h / 2)}"/>'
    if shape == "hexagon":
        i = h / 4
        return (f'<polygon {c} points="{F(x + i)},{F(y)} {F(x + w - i)},{F(y)} {F(x + w)},{F(y + h / 2)} '
                f'{F(x + w - i)},{F(y + h)} {F(x + i)},{F(y + h)} {F(x)},{F(y + h / 2)}"/>')
    if shape == "cylinder":
        e, rx = 7, w / 2
        return (f'<path {c} d="M{F(x)},{F(y + e)} A{F(rx)},{e} 0 0 1 {F(x + w)},{F(y + e)} V{F(y + h - e)} '
                f'A{F(rx)},{e} 0 0 1 {F(x)},{F(y + h - e)} Z"/>'
                f'<path class="dg-sh2" d="M{F(x)},{F(y + e)} A{F(rx)},{e} 0 0 0 {F(x + w)},{F(y + e)}"/>')
    if shape == "document":
        return (f'<path {c} d="M{F(x)},{F(y)} H{F(x + w)} V{F(y + h - 6)} C{F(x + w * .75)},{F(y + h - 16)} '
                f'{F(x + w * .25)},{F(y + h + 4)} {F(x)},{F(y + h - 6)} Z"/>')
    if shape == "note":
        f = 10
        return (f'<path {c} d="M{F(x)},{F(y)} H{F(x + w - f)} L{F(x + w)},{F(y + f)} V{F(y + h)} H{F(x)} Z"/>'
                f'<path class="dg-sh2" d="M{F(x + w - f)},{F(y)} V{F(y + f)} H{F(x + w)}"/>')
    if shape == "cloud":
        cx, cy, rx, ry, k = x + w / 2, y + h / 2, w / 2 * .9, h / 2 * .82, 9
        pts = [(cx + rx * math.cos(2 * math.pi * i / k), cy + ry * math.sin(2 * math.pi * i / k)) for i in range(k)]
        d = f"M{F(pts[0][0])},{F(pts[0][1])}"
        for i in range(k):
            p, q = pts[i], pts[(i + 1) % k]
            r = math.dist(p, q) * .62
            d += f" A{F(r)},{F(r)} 0 0 1 {F(q[0])},{F(q[1])}"
        return f'<path {c} d="{d} Z"/>'
    if shape == "actor":
        cx = x + w / 2
        return (f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" fill="none"/>'
                f'<circle class="dg-act" cx="{F(cx)}" cy="{F(y + 8)}" r="7"/>'
                f'<path class="dg-act" d="M{F(cx)},{F(y + 15)} V{F(y + 30)} M{F(cx - 11)},{F(y + 20)} H{F(cx + 11)} '
                f'M{F(cx)},{F(y + 30)} L{F(cx - 9)},{F(y + 41)} M{F(cx)},{F(y + 30)} L{F(cx + 9)},{F(y + 41)}"/>')
    raise LayoutError(f"unknown shape '{shape}': use one of {', '.join(SHAPES)}")


# ---------- canvas ----------
def canvas(spec):
    """A drawing: z-ordered svg parts plus the geometry record that check.py reads."""
    did = spec["id"]
    return {"id": did, "parts": {0: [], 1: [], 2: [], 3: []}, "css": [], "markers": set(), "rects": {}, "shapes": {},
            "obst": [], "pending": [], "legend": [],
            "geo": {"id": did, "type": spec.get("type", ""), "width": 0, "height": 0, "connected": True,
                    "nodes": [], "containers": [], "edges": [], "labels": []}}


def add(c, svg, z=2):
    """Raw svg at layer z: 0 containers/axes, 1 edges, 2 nodes, 3 labels."""
    c["parts"][z].append(svg)


def add_css(c, rules):
    """Extra CSS for this diagram; write '#S' for the diagram's own scope, e.g. '#S .hot>.dg-sh{fill:var(--dg-red-bg)}'."""
    c["css"].append(rules)


def obstacle(c, x, y, w, h, margin=None):
    """Keep routed arrows margin px (default CLEAR) away from a rectangle that is not a node (a label column, a note)."""
    c["obst"].append((x, y, w, h, CLEAR if margin is None else margin))


def node(c, n, x, y, w, h, clear=None):
    """Draw node dict n (id, label, tag, sub, shape, tone, dashed, strong, mono, align, tip, href, cls) at x, y, w, h.
    clear: how far routed arrows stay from it (default CLEAR; a smaller value for dense rows such as Gantt bars)."""
    shape = n.get("shape") or "rounded"
    tone = n.get("tone") or ("amber" if shape == "note" else "plain")
    cls = " ".join(["dg-n", "dg-t-" + tone] + (["dg-dash"] if n.get("dashed") else [])
                   + (["dg-strong"] if n.get("strong") else []) + (["dg-solid"] if n.get("solid") else [])
                   + (["dg-dim"] if n.get("dim") else []) + ([n["cls"]] if n.get("cls") else []))
    ix, iy, iw, ih = inner(shape, x, y, w, h)
    blocks = text_blocks(n, min(n.get("_wrap", iw), iw))
    tw, th = block_size(blocks)
    if shape == "diamond":
        ix, iy, iw, ih = inner(shape, x, y, w, h, th)
        if tw > iw:
            blocks = text_blocks(n, iw)
            tw, th = block_size(blocks)
            ix, iy, iw, ih = inner(shape, x, y, w, h, th)
    left = n.get("align") == "left"
    out, lines = [f'<g class="{cls}" data-id="{esc(n["id"])}">', shape_svg(shape, x, y, w, h)], []
    if n.get("tip"):
        out.append(f"<title>{esc(n['tip'])}</title>")
    ty = iy + (ih - th) / 2 if shape != "actor" else iy
    for ls, sz, mono, bold, lh, kls in blocks:
        for s in ls:
            lw = text_width(s, sz, mono, bold)
            tx, anchor, lx = (ix, "start", ix) if left else (ix + iw / 2, "middle", ix + iw / 2 - lw / 2)
            out.append(f'<text class="{kls}" x="{F(tx)}" y="{F(ty + (lh - sz) / 2 + sz * .78)}" text-anchor="{anchor}">{esc(s)}</text>')
            lines.append({"text": s, "x": lx, "y": ty, "w": lw, "h": lh})
            ty += lh
    out.append("</g>")
    svg = "".join(out)
    if n.get("href"):
        svg = f'<a href="{esc(n["href"])}">{svg}</a>'
    add(c, svg, 2)
    c["rects"][n["id"]] = (x, y, w, h)
    c["shapes"][n["id"]] = shape
    obstacle(c, x, y, w, h, clear)
    c["geo"]["nodes"].append({"id": n["id"], "x": x, "y": y, "w": w, "h": h, "shape": shape, "text": n.get("label", ""),
                              "decision": shape == "diamond" or bool(n.get("decision")), "free": bool(n.get("free")),
                              "inner": [ix, iy, iw, ih], "lines": lines})
    return x, y, w, h


def label_lines(label, width):
    return wrap(label, max(40, width - 20), 11, mono=True) if label else []


def container(c, cid, label, x, y, w, h, members=(), kind="group", tone=None, header_w=0, label_w=None):
    """Group / boundary (dashed frame, label top-left, wrapped to label_w or w) or lane / band (soft band, label in a
    left header of header_w)."""
    k = {"group": "dg-grp", "boundary": "dg-bnd", "lane": "dg-lane", "band": "dg-band"}[kind]
    cls = k + (f" dg-t-{tone}" if tone and kind == "group" else "")
    r = 10 if kind in ("group", "boundary") else 0
    out = [f'<g class="{cls}" data-id="{esc(cid)}"><rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{r}"/>']
    if header_w:
        out.append(f'<line class="dg-ax" x1="{F(x + header_w)}" y1="{F(y)}" x2="{F(x + header_w)}" y2="{F(y + h)}"/>')
        ls = label_lines(label, header_w)
        ty = y + h / 2 - len(ls) * 15 / 2
        lx = x + 10
    else:
        ls = label_lines(label, label_w or w)
        ty, lx = y + 6, x + 10
    lab = None
    if ls:
        lw = max(text_width(s, 11, True) for s in ls)
        for i, s in enumerate(ls):
            out.append(f'<text x="{F(lx)}" y="{F(ty + i * 15 + 11.5)}">{esc(s)}</text>')
        lab = {"text": label, "x": lx, "y": ty, "w": lw, "h": len(ls) * 15, "edge": None, "kind": "container"}
        c["geo"]["labels"].append(lab)
        c["obst"].append((lx, ty, lw, len(ls) * 15, 6))
    add(c, "".join(out) + "</g>", 0)
    c["geo"]["containers"].append({"id": cid, "x": x, "y": y, "w": w, "h": h, "kind": kind, "text": label,
                                   "members": list(members), "header_w": header_w})
    return lab


def text(c, x, y, s, cls="dg-tx", anchor="start", size=11, mono=False, bold=False, check=True, z=3):
    """Free one-line text (axis ticks, headers). y is the top of the line; registered for overlap checks when check."""
    w = text_width(s, size, mono, bold)
    add(c, f'<text class="{cls}" x="{F(x)}" y="{F(y + size * .95)}" text-anchor="{anchor}">{esc(s)}</text>', z)
    lx = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
    if check:
        c["geo"]["labels"].append({"text": s, "x": lx, "y": y, "w": w, "h": size * 1.3, "edge": None, "kind": "text"})
    return lx, y, w, size * 1.3


def line(c, pts, cls="dg-ax", z=0):
    """Free polyline (axes, lifelines, today line); not checked."""
    add(c, f'<path class="{cls}" d="M' + " L".join(f"{F(a)},{F(b)}" for a, b in pts) + '"/>', z)


def rect(c, x, y, w, h, cls="dg-hd", rx=0, z=0):
    """Free rectangle (header cells, bars that hold no text); not checked."""
    add(c, f'<rect class="{cls}" x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{F(rx)}"/>', z)


def _path_d(pts, r=5):
    d = f"M{F(pts[0][0])},{F(pts[0][1])}"
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.dist(pts[i - 1], pts[i]), math.dist(pts[i], pts[i + 1])
        k = min(r, l1 / 2, l2 / 2)
        if k < 1:
            d += f" L{F(bx)},{F(by)}"
            continue
        p = (bx - (bx - ax) / l1 * k, by - (by - ay) / l1 * k)
        q = (bx + (cx - bx) / l2 * k, by + (cy - by) / l2 * k)
        d += f" L{F(p[0])},{F(p[1])} Q{F(bx)},{F(by)} {F(q[0])},{F(q[1])}"
    return d + f" L{F(pts[-1][0])},{F(pts[-1][1])}"


def arrow(c, pts, e, label_xy=None):
    """Draw edge dict e (from, to, label, style, head, tail, tone) along pts; the label is placed in finish()."""
    style = e.get("style") or "solid"
    tone = e.get("tone") or ""
    head, tail = e.get("head") or "filled", e.get("tail") or "none"
    attrs = ""
    for end, h in (("end", head), ("start", tail)):
        if h != "none":
            c["markers"].add((h, tone))
            attrs += f' marker-{end}="url(#dg-{c["id"]}-{h}-{tone or "n"})"'
    cls = f"dg-e {style}" + (f" c-{tone}" if tone else "") + (" dg-dim" if e.get("dim") else "")
    add(c, f'<path class="{cls}" d="{_path_d(pts)}"{attrs}/>', 1)
    c["geo"]["edges"].append({"from": e.get("from"), "to": e.get("to"), "points": [list(map(float, p)) for p in pts],
                              "label": None})
    k = len(c["geo"]["edges"]) - 1
    if e.get("label"):
        c["pending"].append((k, str(e["label"]), label_xy))
    return k


def _markers(c):
    out = []
    for h, tone in sorted(c["markers"]):
        t = f" c-{tone}" if tone else ""
        mid = f'dg-{c["id"]}-{h}-{tone or "n"}'
        if h in ("filled", "open", "tri", "diamond", "odiamond", "circle"):
            vb, ref, path = "0 0 12 10", 12, {
                "filled": f'<path class="dg-mk{t}" d="M1,1 L12,5 L1,9 Z"/>',
                "open": f'<path class="dg-mkl{t}" d="M1,1 L11,5 L1,9"/>',
                "tri": f'<path class="dg-mko{t}" d="M1,1 L11,5 L1,9 Z"/>',
                "diamond": f'<path class="dg-mk{t}" d="M0,5 L6,1 L12,5 L6,9 Z"/>',
                "odiamond": f'<path class="dg-mko{t}" d="M0.7,5 L6,1 L11.3,5 L6,9 Z"/>',
                "circle": f'<circle class="dg-mko{t}" cx="7" cy="5" r="4"/>'}[h]
            w, hh, refy = 12, 10, 5
        else:  # crow's foot: the toes meet the entity at x = 20
            toes = f'<path class="dg-mkl{t}" d="M8,6 L20,1 M8,6 L20,11 M8,6 L20,6"/>'
            path = {"one": f'<path class="dg-mkl{t}" d="M14,1 V11"/>',
                    "only-one": f'<path class="dg-mkl{t}" d="M10,1 V11 M14,1 V11"/>',
                    "zero-one": f'<path class="dg-mkl{t}" d="M14,1 V11"/><circle class="dg-mko{t}" cx="7" cy="6" r="3.5"/>',
                    "many": toes, "one-many": toes + f'<path class="dg-mkl{t}" d="M5,1 V11"/>',
                    "zero-many": toes + f'<circle class="dg-mko{t}" cx="4.5" cy="6" r="3.5"/>'}[h]
            vb, ref, w, hh, refy = "0 0 20 12", 20, 20, 12, 6
        out.append(f'<marker id="{mid}" viewBox="{vb}" refX="{ref}" refY="{refy}" markerWidth="{w}" markerHeight="{hh}" '
                   f'markerUnits="userSpaceOnUse" orient="auto-start-reverse">{path}</marker>')
    return "<defs>" + "".join(out) + "</defs>"


# ---------- routing ----------
_NEAR = 10  # px from a frame border where a channel starts to cost a little
_NORM = {"right": (1, 0), "left": (-1, 0), "top": (0, -1), "bottom": (0, 1)}
_SPREAD = ("box", "rounded", "note", "cylinder", "document", "pill", "hexagon")


def _sides(a, b, direction):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    gr, gl, gd, gu = bx - (ax + aw), ax - (bx + bw), by - (ay + ah), ay - (by + bh)
    horiz = direction in ("LR", "RL")
    order = (("h", "v") if horiz else ("v", "h"))
    for axis in order:
        if axis == "h":
            if gr >= 2 * CLEAR:
                return "right", "left"
            if gl >= 2 * CLEAR:
                return ("bottom", "bottom") if horiz and gu < 2 * CLEAR and gd < 2 * CLEAR else ("left", "right")
        else:
            if gd >= 2 * CLEAR:
                return "bottom", "top"
            if gu >= 2 * CLEAR:
                return ("right", "right") if not horiz and gr < 2 * CLEAR and gl < 2 * CLEAR else ("top", "bottom")
    dx, dy = (bx + bw / 2) - (ax + aw / 2), (by + bh / 2) - (ay + ah / 2)
    if abs(dx) >= abs(dy):
        return ("right", "left") if dx >= 0 else ("left", "right")
    return ("bottom", "top") if dy >= 0 else ("top", "bottom")


def _port(r, side, off=0.0, shape=None):
    x, y, w, h = r
    d = 0.0  # pill and hexagon ends curve or slope away: move a side port in onto the outline
    if off and side in ("left", "right"):
        if shape == "pill":
            d = h / 2 - math.sqrt(max(0.0, (h / 2) ** 2 - off ** 2))
        elif shape == "hexagon":
            d = abs(off) / 2
    return {"right": (x + w - d, y + h / 2 + off), "left": (x + d, y + h / 2 + off),
            "top": (x + w / 2 + off, y), "bottom": (x + w / 2 + off, y + h)}[side]


def route(c, edges, direction="LR", spread=None):
    """Route edges (from, to, label, style, head, tail, tone, from_side, to_side, own_port) orthogonally around every
    node and container label drawn so far, then draw them. Ports spread along a side; labels go on their own line in
    finish(). Arrows that all leave or all reach one side share a port (a trunk) unless spread=True (every arrow)
    or the edge sets own_port (that side)."""
    R = c["rects"]
    if spread is None:
        spread = bool(c.get("spread"))
    for e in edges:
        for k in ("from", "to"):
            if e[k] not in R:
                raise LayoutError(f"edge {e['from']} -> {e['to']}: node '{e[k]}' is not drawn yet")
    sides = []
    for e in edges:
        if e["from"] == e["to"]:
            sides.append([e.get("from_side") or "top", e.get("to_side") or "right"])
        else:
            s, t = _sides(R[e["from"]], R[e["to"]], direction)
            sides.append([e.get("from_side") or s, e.get("to_side") or t])
    # a decision diamond sends each exit from its own corner
    for nid, shape in c["shapes"].items():
        if shape != "diamond":
            continue
        outs = [k for k, e in enumerate(edges) if e["from"] == nid and not edges[k].get("from_side")]
        used = {sides[k][1] for k, e in enumerate(edges) if e["to"] == nid}
        used |= {sides[k][0] for k, e in enumerate(edges) if e["from"] == nid and e.get("from_side")}
        x, y, w, h = R[nid]
        cx, cy = x + w / 2, y + h / 2
        for k in sorted(outs, key=lambda k: abs(_ctr(R[edges[k]["to"]])[1] - cy) if direction in ("LR", "RL")
                        else abs(_ctr(R[edges[k]["to"]])[0] - cx)):
            s = sides[k][0]
            if s in used:
                tx, ty = _ctr(R[edges[k]["to"]])
                free = [v for v in ("right", "bottom", "top", "left") if v not in used]
                if free:
                    s = min(free, key=lambda v: -((tx - cx) * _NORM[v][0] + (ty - cy) * _NORM[v][1]))
                    sides[k][0] = s
            used.add(s)
    # spread ports along each side, ordered by where the other end lies
    slots = {}
    for k, e in enumerate(edges):
        slots.setdefault((e["from"], sides[k][0]), []).append((k, 0, e["to"]))
        slots.setdefault((e["to"], sides[k][1]), []).append((k, 1, e["from"]))
    ports = [[None, None] for _ in edges]
    stubs = [[None, None] for _ in edges]
    for (nid, side), lst in slots.items():
        r = R[nid]
        along = 1 if side in ("left", "right") else 0
        lst.sort(key=lambda t: (_ctr(R[t[2]])[along], t[0]))
        n = len(lst)
        span = (r[3] if along else r[2]) - 16
        trunk = (len({t[1] for t in lst}) == 1 and not spread  # all leave or all arrive: one shared port
                 and not any(edges[t[0]].get("own_port") for t in lst))
        shape = c["shapes"].get(nid)
        sp = min(18.0, span / max(n, 1)) if shape in _SPREAD and not trunk else 0.0
        for i, (k, end, _) in enumerate(lst):
            off = (i - (n - 1) / 2) * sp
            ports[k][end] = _port(r, side, off, shape)
            p = _port(r, side, off)  # the stub starts outside the box's clear margin, whatever the outline
            stubs[k][end] = (p[0] + _NORM[side][0] * CLEAR, p[1] + _NORM[side][1] * CLEAR)
    # orthogonal grid from obstacle borders, ports and the channels between them
    xs, ys = set(), set()
    for (x, y, w, h, m) in c["obst"]:
        xs |= {x - m, x + w + m}
        ys |= {y - m, y + h + m}
    for st in stubs:
        for p in st:
            xs.add(p[0])
            ys.add(p[1])
    lo_x, hi_x, lo_y, hi_y = min(xs) - 2 * CLEAR, max(xs) + 2 * CLEAR, min(ys) - 2 * CLEAR, max(ys) + 2 * CLEAR
    xs |= {max(2.0, lo_x), hi_x}
    ys |= {max(2.0, lo_y), hi_y}
    X, Y = sorted(xs), sorted(ys)
    X = sorted(set(X) | {(a + b) / 2 for a, b in zip(X, X[1:]) if b - a > 12})
    Y = sorted(set(Y) | {(a + b) / 2 for a, b in zip(Y, Y[1:]) if b - a > 12})
    X, Y = [round(v, 2) for v in X], [round(v, 2) for v in Y]
    bp, bh, bv = set(), set(), set()
    for (x, y, w, h, m) in c["obst"]:
        L, Rr, T, B = x - m, x + w + m, y - m, y + h + m
        i0, i1 = bisect.bisect_left(X, round(L, 2) - 0.01), bisect.bisect_right(X, round(Rr, 2) + 0.01) - 1
        j0, j1 = bisect.bisect_left(Y, round(T, 2) - 0.01), bisect.bisect_right(Y, round(B, 2) + 0.01) - 1
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                inx, iny = L + .01 < X[i] < Rr - .01, T + .01 < Y[j] < B - .01
                if inx and iny:
                    bp.add((i, j))
                if iny and i < i1:
                    bh.add((i, j))
                if inx and j < j1:
                    bv.add((i, j))
    usage, cross = {}, {}
    # a channel along a frame border costs like a foreign line: an arrow drawn on it reads as part of the frame
    # a channel near it costs a little, so an equal route further away wins
    def near(v, a, b):
        d = min(abs(v - a), abs(v - b))
        return [("__frame", "__frame")] if d < 4 else [("__near", "__near")] if d < _NEAR else []
    for g in c["geo"]["containers"]:
        gx0, gy0, gx1, gy1 = g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"]
        for j, yv in enumerate(Y):
            mark = near(yv, gy0, gy1)
            for i in range(len(X) - 1):
                if mark and X[i] >= gx0 - 1 and X[i + 1] <= gx1 + 1:
                    usage.setdefault(("h", i, j), []).extend(mark)
        for i, xv in enumerate(X):
            mark = near(xv, gx0, gx1)
            for j in range(len(Y) - 1):
                if mark and Y[j] >= gy0 - 1 and Y[j + 1] <= gy1 + 1:
                    usage.setdefault(("v", i, j), []).extend(mark)
    order = sorted(range(len(edges)), key=lambda k: -math.dist(*stubs[k]))  # long first: short siblings then join its trunk
    paths = [None] * len(edges)
    for k in order:
        e = edges[k]
        a, b = stubs[k]
        si, sj = X.index(round(a[0], 2)), Y.index(round(a[1], 2))
        gi, gj = X.index(round(b[0], 2)), Y.index(round(b[1], 2))
        sd = 0 if sides[k][0] in ("left", "right") else 1
        gd = 0 if sides[k][1] in ("left", "right") else 1
        cells = _astar(X, Y, (si, sj), (gi, gj), sd, gd, bp, bh, bv, usage, cross, (e["from"], e["to"]))
        if cells is None:
            raise LayoutError(f"no route for {e['from']} -> {e['to']}: move the boxes apart or split the diagram")
        for (i1, j1), (i2, j2) in zip(cells, cells[1:]):
            key = ("h", min(i1, i2), j1) if j1 == j2 else ("v", i1, min(j1, j2))
            usage.setdefault(key, []).append((e["from"], e["to"]))
            cross.setdefault((i2, j2), set()).add(key[0])
        pts = [ports[k][0]] + [(X[i], Y[j]) for i, j in cells] + [ports[k][1]]
        paths[k] = _simplify(pts)
    for k, e in enumerate(edges):
        arrow(c, paths[k], e)
    return paths


def _ctr(r):
    return r[0] + r[2] / 2, r[1] + r[3] / 2


def _simplify(pts):
    out = []
    for p in pts:
        p = (round(p[0], 2), round(p[1], 2))
        if out and p == out[-1]:
            continue
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                out[-1] = p
                continue
        out.append(p)
    return out


def _astar(X, Y, start, goal, sd, gd, bp, bh, bv, usage, cross, me):
    BEND = 28
    gx, gy = X[goal[0]], Y[goal[1]]
    heur = lambda i, j: abs(X[i] - gx) + abs(Y[j] - gy)  # noqa: E731
    pq = [(heur(*start), 0.0, start[0], start[1], sd)]
    best = {(start[0], start[1], sd): 0.0}
    prev = {}
    while pq:
        f, g, i, j, d = heapq.heappop(pq)
        if g > best.get((i, j, d), 1e18):
            continue
        if (i, j) == goal:
            if d == gd:
                break
            if best.get((i, j, gd), 1e18) > g + BEND:  # arriving across the stub costs one more bend
                best[(i, j, gd)] = g + BEND
                prev[(i, j, gd)] = (i, j, d)
                heapq.heappush(pq, (g + BEND, g + BEND, i, j, gd))
            continue
        for di, dj, nd in ((1, 0, 0), (-1, 0, 0), (0, 1, 1), (0, -1, 1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < len(X) and 0 <= nj < len(Y)):
                continue
            if nd == 0 and (min(i, ni), j) in bh or nd == 1 and (i, min(j, nj)) in bv:
                continue
            if (ni, nj) in bp and (ni, nj) != goal:
                continue
            ln = abs(X[ni] - X[i]) + abs(Y[nj] - Y[j])
            cost = ln + (BEND if nd != d else 0)
            key = ("h", min(i, ni), j) if nd == 0 else ("v", i, min(j, nj))
            shared = False
            for o in usage.get(key, ()):
                if o[0] == "__near":
                    cost += 6
                elif o[0] != me[0] and o[1] != me[1]:
                    cost += 40 + 4 * ln
                else:
                    shared = True
            if shared:  # follow an edge with the same source or target: one trunk, not two parallel lines
                cost -= 0.5 * ln
            if ("v" if nd == 0 else "h") in cross.get((ni, nj), ()):
                cost += 10
            ng = g + cost
            st = (ni, nj, nd)
            if ng < best.get(st, 1e18):
                best[st] = ng
                prev[st] = (i, j, d)
                heapq.heappush(pq, (ng + heur(ni, nj), ng, ni, nj, nd))
    else:
        return None
    st = (goal[0], goal[1], gd)
    if st not in prev and (goal[0], goal[1]) != (start[0], start[1]):
        return None
    cells = []
    while st in prev:
        if not cells or cells[-1] != st[:2]:
            cells.append(st[:2])
        st = prev[st]
    if not cells or cells[-1] != st[:2]:
        cells.append(st[:2])
    return cells[::-1]


# ---------- labels and finish ----------
def _hits(r, s, pad=0.0):
    x, y, w, h = r[0] - pad, r[1] - pad, r[2] + 2 * pad, r[3] + 2 * pad
    return checker.seg_hits_rect(s[0], s[1], (x, y, w, h))


def _overlap(a, b, pad=0.0):
    return a[0] < b[0] + b[2] + pad and b[0] < a[0] + a[2] + pad and a[1] < b[1] + b[3] + pad and b[1] < a[1] + a[3] + pad


def _place_labels(c):
    geo = c["geo"]
    segs = [(k, (p, q)) for k, e in enumerate(geo["edges"]) for p, q in zip(e["points"], e["points"][1:])]
    nodes = [(n["x"], n["y"], n["w"], n["h"]) for n in geo["nodes"]]
    for k, txt, xy in c["pending"]:
        lw, lh = text_width(txt, 11, True) + 10, 16
        pts = geo["edges"][k]["points"]
        cands = [xy] if xy else []
        segl = list(zip(pts, pts[1:]))
        mid = (len(segl) - 1) / 2
        own = [s for s in segl if not any(checker.collinear_overlap(s, t) for j, t in segs if j != k)]
        for p, q in sorted(segl, key=lambda s: (s not in own, -math.dist(*s) // 40, abs(segl.index(s) - mid))):
            ln = math.dist(p, q)
            horiz = abs(p[1] - q[1]) < .5
            for t in (.5, .35, .65, .2, .8):
                cx, cy = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
                if horiz:
                    if ln >= lw + 14:
                        cands.append((cx, cy))
                    cands += [(cx, cy - lh / 2 - 3), (cx, cy + lh / 2 + 3)]
                else:
                    if ln >= lh + 14:
                        cands.append((cx, cy))
                    cands += [(cx + lw / 2 + 4, cy), (cx - lw / 2 - 4, cy)]
        ends = (pts[0], pts[-1])
        pick = None
        for cx, cy in cands:
            r = (cx - lw / 2, cy - lh / 2, lw, lh)
            if r[0] < 2 or r[1] < 2:
                continue
            if any(_overlap(r, n, 2) for n in nodes) or any(_overlap(r, (o["x"], o["y"], o["w"], o["h"]), 2) for o in geo["labels"]):
                continue
            if any(checker.straddles(r, (g["x"], g["y"], g["w"], g["h"])) for g in geo["containers"]):
                continue
            if any(j != k and _hits(r, s, 1) for j, s in segs):
                continue
            if any(_overlap(r, (p[0] - 7, p[1] - 7, 14, 14)) for p in ends):
                continue
            pick = r
            break
        r = pick or ((cands[0][0] - lw / 2, cands[0][1] - lh / 2, lw, lh) if cands else (pts[0][0], pts[0][1], lw, lh))
        add(c, f'<g class="dg-lb"><rect x="{F(r[0])}" y="{F(r[1])}" width="{F(lw)}" height="{lh}" rx="3"/>'
               f'<text x="{F(r[0] + lw / 2)}" y="{F(r[1] + 11.8)}" text-anchor="middle">{esc(txt)}</text></g>', 3)
        geo["labels"].append({"text": txt, "x": r[0], "y": r[1], "w": lw, "h": lh, "edge": k, "kind": "edge"})
        geo["edges"][k]["label"] = len(geo["labels"]) - 1
    c["pending"] = []


def legend(c, entries):
    """Queue legend entries drawn under the diagram by finish(): [{"label", "tone"?, "solid"?, "dashed"?, "shape"?}]
    for a box swatch, or {"label", "edge": {"style", "tone"}} for a line swatch. Same labels are kept once."""
    seen = {e["label"] for e in c["legend"]}
    c["legend"] += [e for e in entries if e.get("label") and e["label"] not in seen and not seen.add(e["label"])]


def _draw_legend(c, width):
    geo = c["geo"]
    bottom = max([b["y"] + b["h"] for b in geo["nodes"] + geo["containers"] + geo["labels"]] +
                 [p[1] for e in geo["edges"] for p in e["points"]] + [0])
    x0, y, x = MARGIN, bottom + 18, MARGIN
    limit = max(width, 320) - MARGIN
    out = []
    for e in c["legend"]:
        tw = text_width(e["label"], 11, True)
        ew = 26 + tw
        if x > x0 and x + ew > limit:
            x, y = x0, y + 20
        if e.get("edge"):
            ed = e["edge"]
            cls = f"dg-e {ed.get('style') or 'solid'}" + (f" c-{ed['tone']}" if ed.get("tone") else "")
            out.append(f'<path class="{cls}" d="M{F(x)},{F(y + 7)} H{F(x + 20)}"/>')
        else:
            cls = " ".join(["dg-n", "dg-t-" + (e.get("tone") or "plain")] + (["dg-solid"] if e.get("solid") else [])
                           + (["dg-dash"] if e.get("dashed") else []) + (["dg-strong"] if e.get("strong") else []))
            rx = 6 if e.get("shape") == "pill" else 2
            out.append(f'<g class="{cls}"><rect class="dg-sh" x="{F(x + 1)}" y="{F(y + 1)}" width="18" height="12" rx="{rx}"/></g>')
        out.append(f'<text class="dg-lg" x="{F(x + 26)}" y="{F(y + 11)}">{esc(e["label"])}</text>')
        geo["labels"].append({"text": e["label"], "x": x, "y": y, "w": ew, "h": 14, "edge": None, "kind": "legend"})
        x += ew + 18
    add(c, "".join(out), 3)


def finish(c, w=None, h=None):
    """Place edge labels, draw the legend, size the canvas (or use w, h) and return (svg_body, geometry)."""
    _place_labels(c)
    geo = c["geo"]
    if c["legend"]:
        _draw_legend(c, w or max([b["x"] + b["w"] for b in geo["nodes"] + geo["containers"]] + [0]) + MARGIN)
    xm = [b["x"] + b["w"] for b in geo["nodes"] + geo["containers"] + geo["labels"]] + \
         [p[0] for e in geo["edges"] for p in e["points"]]
    ym = [b["y"] + b["h"] for b in geo["nodes"] + geo["containers"] + geo["labels"]] + \
         [p[1] for e in geo["edges"] for p in e["points"]]
    geo["width"] = math.ceil(w if w is not None else max(xm or [0]) + MARGIN)
    geo["height"] = math.ceil(h if h is not None else max(ym or [0]) + MARGIN)
    body = "".join("".join(c["parts"][z]) for z in sorted(c["parts"]))
    return _markers(c) + body, geo


# ---------- layouts ----------
def ranks(ids, edges, fixed=None, lower=None, pull=True):
    """Longest-path layer per id (cycles broken by DFS back edges, fixed {id: rank} kept, lower {id: min rank}
    respected, sources pulled right next to their first successor when pull). Returns (rank dict, back-edge indexes)."""
    fixed, lower = fixed or {}, lower or {}
    succ = {i: [] for i in ids}
    for k, e in enumerate(edges):
        if e["from"] != e["to"]:
            succ[e["from"]].append((e["to"], k))
    back, state = set(), {}

    def dfs(u):
        state[u] = 1
        for v, k in succ[u]:
            if state.get(v) == 1:
                back.add(k)
            elif not state.get(v):
                dfs(v)
        state[u] = 2

    sys.setrecursionlimit(max(1000, 4 * len(ids) + 100))
    for i in ids:
        if not state.get(i):
            dfs(i)
    back |= {k for k, e in enumerate(edges) if e["from"] == e["to"]}
    fwd = [(e["from"], e["to"]) for k, e in enumerate(edges) if k not in back]
    indeg = {i: 0 for i in ids}
    for u, v in fwd:
        indeg[v] += 1
    q = [i for i in ids if indeg[i] == 0]
    topo = []
    while q:
        u = q.pop(0)
        topo.append(u)
        for v, k in succ[u]:
            if k not in back:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
    rank = {}
    preds = {i: [u for u, v in fwd if v == i] for i in ids}
    for u in topo:
        rank[u] = fixed[u] if u in fixed else max([rank[p] + 1 for p in preds[u]] + [lower.get(u, 0)])
    for u in reversed(topo if pull else []):  # sources sit one layer before their nearest successor
        if u not in fixed and not preds[u]:
            nxt = [rank[v] for v, k in succ[u] if k not in back]
            if nxt:
                rank[u] = max(rank[u], min(nxt) - 1)
    return rank, back


def _pav(desired, sizes, gap, lo, hi):
    off = [0.0]
    for i in range(1, len(sizes)):
        off.append(off[-1] + (sizes[i - 1] + sizes[i]) / 2 + gap)
    blocks = []
    for v in (d - o for d, o in zip(desired, off)):
        blocks.append([v, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            s, n = blocks.pop()
            blocks[-1][0] += s
            blocks[-1][1] += n
    q = [s / n for s, n in blocks for _ in range(n)]
    qlo, qhi = lo + sizes[0] / 2, hi - sizes[-1] / 2 - off[-1]
    return [max(qlo, min(max(qlo, qhi), v)) + o for v, o in zip(q, off)]


def _crossings(order_a, order_b, links):
    pa, pb = {v: i for i, v in enumerate(order_a)}, {v: i for i, v in enumerate(order_b)}
    es = [(pa[u], pb[v]) for u, v in links if u in pa and v in pb]
    return sum(1 for i in range(len(es)) for j in range(i + 1, len(es))
               if (es[i][0] - es[j][0]) * (es[i][1] - es[j][1]) < 0)


def _column_ranks(ids, N, edges, fixed, order):
    """Ranks where every group of order owns its own run of layers, in that order (dbt layers, pipeline stages)."""
    lower = {}
    for k, g in enumerate(order[1:], 1):
        rank, _ = ranks(ids, edges, fixed, lower, pull=False)
        prev = [i for i in ids if N[i].get("group") in order[:k]]
        if prev:
            lb = max(rank[i] for i in prev) + 1
            for i in ids:
                if N[i].get("group") == g:
                    lower[i] = max(lower.get(i, 0), lb)
    rank, back = ranks(ids, edges, fixed, lower, pull=False)
    span = {}
    for i in ids:
        g = N[i].get("group")
        if g is not None:
            lo, hi = span.get(g, (rank[i], rank[i]))
            span[g] = (min(lo, rank[i]), max(hi, rank[i]))
    gs = [g for g in order if g in span]
    for a, b in zip(gs, gs[1:]):
        if span[a][1] >= span[b][0]:
            raise LayoutError(f"group '{b}' links back into '{a}': reorder groups or use group_layout 'bands'")
    return rank, back, span


def _sequential(ids, N, edges, fixed, order):
    """True when the groups follow one another along the flow: their layer ranges do not overlap, in groups order."""
    if len(order) < 2:
        return False
    rank, _ = ranks(ids, edges, fixed, pull=False)
    span = {}
    for i in ids:
        g = N[i].get("group")
        if g is not None:
            lo, hi = span.get(g, (rank[i], rank[i]))
            span[g] = (min(lo, rank[i]), max(hi, rank[i]))
    gs = sorted((g for g in order if g in span), key=lambda g: span[g])
    return all(span[a][1] < span[b][0] for a, b in zip(gs, gs[1:])) and gs == [g for g in order if g in span]


def layout_layered(items, edges, direction="LR", groups=None, gap=None, cross_gap=None, group_layout="bands"):
    """Layered DAG layout with crossing reduction. items: [{id, w, h, group?, rank?}], edges: [{from, to, label?}],
    groups: {gid: label} in order. group_layout "bands": members share a stripe across the flow (a frame never holds
    a foreign box); "columns": each group owns consecutive layers along the flow, in groups order (dbt layers);
    "auto": columns when the groups already follow one another in groups order, else bands.
    Returns {"pos": {id: (x, y, w, h)}, "groups": {gid: (x, y, w, h)}, "width", "height", "back": set}."""
    groups = groups or {}
    lr = direction in ("LR", "RL")
    ids = [n["id"] for n in items]
    N = {n["id"]: dict(n) for n in items}
    fixed = {n["id"]: n["rank"] for n in items if n.get("rank") is not None}
    if group_layout == "auto":
        group_layout = "columns" if _sequential(ids, N, edges, fixed, list(groups)) else "bands"
    cols = group_layout == "columns" and bool(groups)
    if cols:
        rank, back, span = _column_ranks(ids, N, edges, fixed, list(groups))
        cgroup = {i: N[i].get("group") for i in ids}
        for i, v in N.items():  # one stripe "_g" holds every group; an ungrouped box in a group's column goes below
            clash = cgroup[i] is None and any(lo <= rank[i] <= hi for lo, hi in span.values())
            v["group"] = None if clash else "_g"
    else:
        rank, back = ranks(ids, edges, fixed)
    mx = max(rank.values()) if rank else 0
    links = []  # (u, v) between consecutive layers, dummies included
    for k, e in enumerate(edges):
        u, v = e["from"], e["to"]
        if k in back:
            u, v = v, u
        if rank[v] - rank[u] < 1:
            continue
        chain = [u]
        for r in range(rank[u] + 1, rank[v]):
            d = f"_d{k}_{r}"
            mid = (rank[u] + rank[v]) / 2
            N[d] = {"id": d, "w": 12, "h": 12, "group": N[u].get("group") if r <= mid else N[v].get("group"), "dummy": True}
            rank[d] = r
            chain.append(d)
        chain.append(v)
        links += list(zip(chain, chain[1:]))
    layers = [[] for _ in range(mx + 1)]
    for i in N:
        layers[rank[i]].append(i)
    band = {i: N[i].get("group") for i in N}
    nb = {i: [] for i in N}
    for u, v in links:
        nb[u].append(v)
        nb[v].append(u)

    def sort_layer(l, ref):
        pos = {v: i / max(1, len(layers[r]) - 1) for r in ref for i, v in enumerate(layers[r])}
        cur = {v: i / max(1, len(layers[l]) - 1) for i, v in enumerate(layers[l])}
        bary = {v: (sum(pos[u] for u in nb[v] if u in pos) / len([u for u in nb[v] if u in pos]))
                if any(u in pos for u in nb[v]) else cur[v] for v in layers[l]}
        layers[l].sort(key=lambda v: (border[band[v]], bary[v]))

    def band_order():
        sc = {}
        for l in layers:
            for i, v in enumerate(l):
                sc.setdefault(band[v], []).append(i / max(1, len(l) - 1))
        keys = sorted(sc, key=lambda b: (sum(sc[b]) / len(sc[b]), str(b)))
        return {b: i for i, b in enumerate(keys)}

    border = band_order()
    total = lambda: sum(_crossings(layers[l], layers[l + 1], links) for l in range(mx))  # noqa: E731
    best, best_c = [list(l) for l in layers], total()
    for it in range(8):
        rng = range(1, mx + 1) if it % 2 == 0 else range(mx - 1, -1, -1)
        for l in rng:
            sort_layer(l, [l - 1] if it % 2 == 0 else [l + 1])
        border = band_order()
        for l in range(mx + 1):
            at = {v: i for i, v in enumerate(layers[l])}
            layers[l].sort(key=lambda v: (border[band[v]], at[v]))
        cc = total()
        if cc < best_c:
            best, best_c = [list(l) for l in layers], cc
    layers = best
    border = band_order()
    msize = lambda v: N[v]["w"] if lr else N[v]["h"]  # noqa: E731
    csize = lambda v: N[v]["h"] if lr else N[v]["w"]  # noqa: E731
    cg = cross_gap or (28 if lr else 32)
    lw = [max([msize(v) for v in l if not N[v].get("dummy")] or [12]) for l in layers]
    gaps = []
    lgroup = {}
    if cols:
        for i in ids:
            lgroup.setdefault(rank[i], set()).add(cgroup[i])
    for l in range(mx):
        labs = [text_width(str(e.get("label", "")), 11, True) + 10 for e in edges
                if e.get("label") and min(rank[e["from"]], rank[e["to"]]) == l]
        g = gap or (56 if lr else 48)
        if labs:
            g = max(g, (max(labs) + 40) if lr else 60)
            if lgroup and lgroup.get(l) != lgroup.get(l + 1):  # two frame borders eat 2 x GP of this gap
                g += 2 * GP
        gaps.append(g)
    # bands: cross extent per group (stack of its members in the fullest layer)
    bands = sorted(border, key=lambda b: border[b])
    stack = {b: max([sum(csize(v) for v in l if band[v] == b) + cg * (sum(1 for v in l if band[v] == b) - 1)
                     for l in layers if any(band[v] == b for v in l)] or [0]) for b in bands}
    glines = {}
    g0 = any(band[v] is not None and not N[v].get("dummy") for v in layers[0]) if layers else False
    if cols:
        for g in groups:
            ls = [rank[i] for i in ids if cgroup[i] == g]
            if ls:
                glines[g] = label_lines(groups[g], (max(lw[r] for r in ls) + 2 * GP) if lr else LABEL_COL)
        # one stripe holds every group: LR needs the most label rows, TB the widest label line
        glines = {"_g": max(glines.values(), key=len) if lr else sum(glines.values(), [])} if glines else {}
        main = [MARGIN + GP]
        for l in range(mx):
            main.append(main[-1] + lw[l] + gaps[l])
    elif lr:
        main = [MARGIN + (GP if g0 else 0)]
        for l in range(mx):
            main.append(main[-1] + lw[l] + gaps[l])
        for b in bands:
            if b is not None:
                ls = [rank[v] for v in N if band[v] == b and not N[v].get("dummy")]
                width = main[max(ls)] + lw[max(ls)] - main[min(ls)] + 2 * GP
                glines[b] = label_lines(groups.get(b, b), width)
    else:
        for b in bands:
            if b is not None:
                glines[b] = label_lines(groups.get(b, b), LABEL_COL)
        main = [MARGIN + (GP if g0 else 0)]
        for l in range(mx):
            main.append(main[-1] + lw[l] + gaps[l])
    # cross ranges per band
    lo, cur = {}, MARGIN
    for b in bands:
        if b is None:
            pad_a = 0
        elif lr:
            pad_a = len(glines.get(b, [])) * 15 + 22
        else:  # top-down: the label sits in a column left of the members, clear of arrows entering from above
            pad_a = max([text_width(x, 11, True) for x in glines.get(b, [])] + [0]) + 22
        pad_b = 12 if b is not None else 0
        lo[b] = (cur, cur + pad_a, cur + pad_a + stack[b])
        cur = cur + pad_a + stack[b] + pad_b + 20
    ctr = {}
    for l in layers:
        for b in bands:
            mem = [v for v in l if band[v] == b]
            if mem:
                s = [csize(v) for v in mem]
                ctr.update(zip(mem, _pav([(lo[b][1] + lo[b][2]) / 2] * len(mem), s, cg, lo[b][1], lo[b][2])))
    for it in range(10):
        rng = range(1, mx + 1) if it % 2 == 0 else range(mx - 1, -1, -1)
        for l in rng:
            ref = (l - 1) if it % 2 == 0 else (l + 1)
            for b in bands:
                mem = [v for v in layers[l] if band[v] == b]
                if not mem:
                    continue
                des = []
                for v in mem:
                    ns = [ctr[u] for u in nb[v] if rank[u] == ref] or [ctr[u] for u in nb[v]]
                    des.append(sum(ns) / len(ns) if ns else ctr[v])
                ctr.update(zip(mem, _pav(des, [csize(v) for v in mem], cg, lo[b][1], lo[b][2])))
    for l in range(1, mx + 1):  # straighten chains: a box with one box before it lines up with that box
        for b in bands:
            mem = [v for v in layers[l] if band[v] == b]
            if not mem:
                continue
            des = []
            for v in mem:
                ps = [ctr[u] for u in nb[v] if rank[u] == l - 1]
                des.append(ps[0] if len(ps) == 1 else ctr[v])
            ctr.update(zip(mem, _pav(des, [csize(v) for v in mem], cg, lo[b][1], lo[b][2])))
    pos = {}
    for v, n in N.items():
        if n.get("dummy"):
            continue
        m0 = main[rank[v]] + (lw[rank[v]] - msize(v)) / 2
        c0 = ctr[v] - csize(v) / 2
        pos[v] = (m0, c0, n["w"], n["h"]) if lr else (c0, m0, n["w"], n["h"])
    grect = {}
    if cols:
        c_a, c_b = lo["_g"][0], lo["_g"][2] + 12
        for g in groups:
            ls = [rank[i] for i in ids if cgroup[i] == g]
            if not ls:
                continue
            m_a, m_b = main[min(ls)] - GP, main[max(ls)] + lw[max(ls)] + GP
            grect[g] = (m_a, c_a, m_b - m_a, c_b - c_a) if lr else (c_a, m_a, c_b - c_a, m_b - m_a)
    for b in bands:
        if b is None or cols:
            continue
        ls = [rank[v] for v in N if band[v] == b and not N[v].get("dummy")]
        if not ls:
            continue
        m_a, m_b = main[min(ls)] - GP, main[max(ls)] + lw[max(ls)] + GP
        c_a, c_b = lo[b][0], lo[b][2] + 12
        grect[b] = (m_a, c_a, m_b - m_a, c_b - c_a) if lr else (c_a, m_a, c_b - c_a, m_b - m_a)
    allr = list(pos.values()) + list(grect.values())
    W = max(r[0] + r[2] for r in allr) + MARGIN if allr else 0
    H = max(r[1] + r[3] for r in allr) + MARGIN if allr else 0
    return {"pos": pos, "groups": grect, "width": W, "height": H, "back": back, "label_w": None if lr else LABEL_COL}


def layout_grid(sizes, cols, gap=(32, 28), start=(MARGIN, MARGIN), uniform=True):
    """Row-major grid of [(w, h)] in cols columns; uniform widens every cell to the widest. Returns [(x, y, w, h)]."""
    rows = [sizes[i:i + cols] for i in range(0, len(sizes), cols)]
    cw = [max([r[j][0] for r in rows if j < len(r)]) for j in range(cols)]
    if uniform:
        cw = [max(cw)] * cols
    out, y = [], start[1]
    for r in rows:
        rh = max(h for _, h in r)
        x = start[0]
        for j, (w, h) in enumerate(r):
            ww, hh = (cw[j], rh) if uniform else (w, h)
            out.append((x + (cw[j] - ww) / 2, y + (rh - hh) / 2, ww, hh))
            x += cw[j] + gap[0]
        y += rh + gap[1]
    return out


def layout_lanes(lanes, items, edges, header_w=120, gap=None, row_gap=16):
    """Swimlanes: lanes [{id, label}] as rows, items [{id, w, h, lane, col?}] in columns (col from ranks() when
    missing). Returns {"pos": {id: rect}, "lanes": {lane_id: rect}, "cols": [x per column], "width", "height"}."""
    col = {n["id"]: n["col"] for n in items if n.get("col") is not None}
    if len(col) < len(items):
        r, _ = ranks([n["id"] for n in items], edges, col)
        col = {i: col.get(i, r[i]) for i in r}
    nc = max(col.values()) + 1 if col else 0
    cw = [max([n["w"] for n in items if col[n["id"]] == j] or [40]) for j in range(nc)]
    gaps = []
    for j in range(nc):
        labs = [text_width(str(e["label"]), 11, True) + 10 for e in edges if e.get("label") and
                min(col[e["from"]], col[e["to"]]) == j]
        gaps.append(max(gap or 48, (max(labs) + 40) if labs else 0))
    xs = [MARGIN + header_w + 24]
    for j in range(nc - 1):
        xs.append(xs[-1] + cw[j] + gaps[j])
    W = (xs[-1] + cw[-1] + 24 if nc else MARGIN + header_w + 40) - MARGIN
    pos, lrect, y = {}, {}, MARGIN
    for ln in lanes:
        mem = [n for n in items if n.get("lane") == ln["id"]]
        cells = {}
        for n in mem:
            cells.setdefault(col[n["id"]], []).append(n)
        hl = max([sum(n["h"] for n in v) + row_gap * (len(v) - 1) for v in cells.values()] or [24])
        lh = max(len(label_lines(ln.get("label", ""), header_w)) * 15 + 16, hl + 2 * row_gap)
        for j, v in cells.items():
            yy = y + (lh - (sum(n["h"] for n in v) + row_gap * (len(v) - 1))) / 2
            for n in v:
                pos[n["id"]] = (xs[j] + (cw[j] - n["w"]) / 2, yy, n["w"], n["h"])
                yy += n["h"] + row_gap
        lrect[ln["id"]] = (MARGIN, y, W, lh)
        y += lh
    return {"pos": pos, "lanes": lrect, "cols": xs, "width": W + 2 * MARGIN, "height": y + MARGIN}


def layout_tree(items, direction="TB", gap=(24, 48), start=(MARGIN, MARGIN)):
    """Tidy tree: items [{id, w, h, parent?}] (one root). Returns {"pos": {id: rect}, "width", "height"}."""
    kids = {n["id"]: [] for n in items}
    N = {n["id"]: n for n in items}
    roots = [n["id"] for n in items if not n.get("parent")]
    for n in items:
        if n.get("parent"):
            kids[n["parent"]].append(n["id"])
    tb = direction in ("TB", "BT")
    cs = lambda v: N[v]["w"] if tb else N[v]["h"]  # noqa: E731
    ms = lambda v: N[v]["h"] if tb else N[v]["w"]  # noqa: E731
    depth = {}

    def walk(v, d):
        depth[v] = d
        for k in kids[v]:
            walk(k, d + 1)

    for r in roots:
        walk(r, 0)
    md = [0] * (max(depth.values()) + 1 if depth else 1)
    for v, d in depth.items():
        md[d] = max(md[d], ms(v))
    mpos = [start[1] if tb else start[0]]
    for d in range(len(md) - 1):
        mpos.append(mpos[-1] + md[d] + gap[1])
    ext = {}

    def extent(v):
        ext[v] = max(cs(v), sum(extent(k) for k in kids[v]) + gap[0] * (len(kids[v]) - 1) if kids[v] else 0)
        return ext[v]

    pos = {}

    def place(v, a):
        c = a + ext[v] / 2
        m = mpos[depth[v]] + (md[depth[v]] - ms(v)) / 2
        pos[v] = (c - cs(v) / 2, m, N[v]["w"], N[v]["h"]) if tb else (m, c - cs(v) / 2, N[v]["w"], N[v]["h"])
        inner_w = sum(ext[k] for k in kids[v]) + gap[0] * (len(kids[v]) - 1)
        b = a + (ext[v] - inner_w) / 2
        for k in kids[v]:
            place(k, b)
            b += ext[k] + gap[0]

    a = start[0] if tb else start[1]
    for r in roots:
        extent(r)
        place(r, a)
        a += ext[r] + gap[0]
    W = max(r[0] + r[2] for r in pos.values()) + MARGIN if pos else 0
    H = max(r[1] + r[3] for r in pos.values()) + MARGIN if pos else 0
    return {"pos": pos, "width": W, "height": H}


def layout_radial(center, items, gap=24, child_gap=10):
    """Radial: center {id, w, h}; items [{id, w, h, parent?}] where parent is center (ring) or a ring item
    (stacked beside it, outward). The ring radius grows until no blocks overlap. Returns {"pos", "width", "height"}."""
    ring = [n for n in items if n.get("parent") in (None, center["id"])]
    kids = {n["id"]: [m for m in items if m.get("parent") == n["id"]] for n in ring}
    k = len(ring)
    blocks = {}
    for n in ring:
        ch = kids[n["id"]]
        cw = max([m["w"] for m in ch] or [0])
        chh = sum(m["h"] for m in ch) + child_gap * max(0, len(ch) - 1)
        blocks[n["id"]] = (n["w"] + (cw + 28 if ch else 0), max(n["h"], chh))
    R = max(center["w"], center["h"]) / 2 + 60
    for _ in range(200):
        pos, rects = {}, []
        for i, n in enumerate(ring):
            a = -math.pi / 2 + 2 * math.pi * i / max(k, 1)
            bw, bh = blocks[n["id"]]
            right = math.cos(a) >= -1e-9
            cx, cy = R * math.cos(a), R * math.sin(a)
            nx = cx if right else cx - n["w"]
            ny = cy - n["h"] / 2
            pos[n["id"]] = (nx, ny, n["w"], n["h"])
            bx = nx if right else cx - bw
            rects.append((bx, cy - bh / 2, bw, bh))
            yy = cy - (sum(m["h"] for m in kids[n["id"]]) + child_gap * max(0, len(kids[n["id"]]) - 1)) / 2
            for m in kids[n["id"]]:
                mx_ = nx + n["w"] + 28 if right else nx - 28 - m["w"]
                pos[m["id"]] = (mx_, yy, m["w"], m["h"])
                yy += m["h"] + child_gap
        crect = (-center["w"] / 2, -center["h"] / 2, center["w"], center["h"])
        clash = any(_overlap(a, b, gap) for i, a in enumerate(rects) for b in rects[i + 1:]) or \
            any(_overlap(a, crect, gap) for a in rects)
        if not clash:
            break
        R *= 1.08
    pos[center["id"]] = (-center["w"] / 2, -center["h"] / 2, center["w"], center["h"])
    minx = min(r[0] for r in pos.values())
    miny = min(r[1] for r in pos.values())
    pos = {i: (r[0] - minx + MARGIN, r[1] - miny + MARGIN, r[2], r[3]) for i, r in pos.items()}
    return {"pos": pos, "width": max(r[0] + r[2] for r in pos.values()) + MARGIN,
            "height": max(r[1] + r[3] for r in pos.values()) + MARGIN}


def layout_matrix(row_heads, col_heads, cell_w=None, cell_h=40, head_w=None, head_h=None, start=(MARGIN, MARGIN), gap=4):
    """Matrix of cells under column headers with row headers on the left. Sizes come from the header texts.
    Returns {"cells": {(r, c): rect}, "rows": [rect], "cols": [rect], "width", "height"}."""
    hw = head_w or min(220, max([text_width(s, 12, bold=True) for s in row_heads] or [60]) + 24)
    cw = cell_w or max(90, min(180, max([text_width(s, 11, True) for s in col_heads] or [60]) + 20))
    hh = head_h or max(len(wrap(s, cw - 12, 11, True)) for s in col_heads) * 15 + 14 if col_heads else 0
    rows, cols, cells = [], [], {}
    x0, y0 = start
    for j, _ in enumerate(col_heads):
        cols.append((x0 + hw + gap + j * (cw + gap), y0, cw, hh))
    for i, _ in enumerate(row_heads):
        y = y0 + hh + gap + i * (cell_h + gap)
        rows.append((x0, y, hw, cell_h))
        for j in range(len(col_heads)):
            cells[(i, j)] = (cols[j][0], y, cw, cell_h)
    W = x0 + hw + gap + len(col_heads) * (cw + gap) + MARGIN
    H = y0 + hh + gap + len(row_heads) * (cell_h + gap) + MARGIN
    return {"cells": cells, "rows": rows, "cols": cols, "width": W, "height": H}


def time_axis(start, end, x0, x1):
    """Map ISO dates onto [x0, x1]. Returns (to_x(date_str), ticks [(x, label)]): weeks up to 10 weeks,
    months up to two years, else quarters."""
    d0, d1 = datetime.date.fromisoformat(start), datetime.date.fromisoformat(end)
    span = max(1, (d1 - d0).days)
    to_x = lambda s: x0 + (datetime.date.fromisoformat(s) - d0).days / span * (x1 - x0)  # noqa: E731
    ticks = []
    if span <= 70:
        d = d0 + datetime.timedelta(days=(7 - d0.weekday()) % 7)
        while d <= d1:
            ticks.append((to_x(d.isoformat()), d.strftime("%d %b")))
            d += datetime.timedelta(days=7)
    else:
        step = 1 if span <= 730 else 3
        y, m = d0.year, d0.month
        while True:
            d = datetime.date(y, m, 1)
            if d > d1:
                break
            if d >= d0:
                ticks.append((to_x(d.isoformat()), d.strftime("%b %y") if step == 1 else f"Q{(m - 1) // 3 + 1} {y}"))
            m += step
            y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return to_x, ticks


# ---------- mermaid ----------
MM_SHAPE = {"box": ("[", "]"), "rounded": ("(", ")"), "pill": ("([", "])"), "circle": ("((", "))"),
            "cylinder": ("[(", ")]"), "diamond": ("{", "}"), "hexagon": ("{{", "}}"), "document": ("[", "]"),
            "note": ("[", "]"), "cloud": ("(", ")"), "actor": ("([", "])")}
MM_TONE = {"soft": ("#EEEFEC", "#5B6068"), "teal": ("#DDF0EE", "#1C5C57"), "amber": ("#FCEBC8", "#8A5A00"),
           "lav": ("#E7E2F5", "#6B4FA8"), "green": ("#E2F1E8", "#1E6B43"), "red": ("#F8E3E3", "#A12D2D"),
           "blue": ("#E2ECF8", "#1F5FA8"), "ink": ("#17191D", "#17191D")}


def mm_text(s):
    """A quoted Mermaid label with the characters that break the parser written as entity codes."""
    s = str(s).replace("\n", " ")
    for a, b in (("#", "#35;"), ('"', "#quot;"), ("|", "#124;"), ("<", "#60;"), (">", "#62;")):
        s = s.replace(a, b)
    return f'"{s}"'


def mm_id(s):
    """A Mermaid-safe node id (never 'end', never a leading o/x after a link)."""
    return "n_" + re.sub(r"\W", "_", str(s))


def mermaid_head(spec, kind):
    t = str(spec.get("title", "")).replace('"', "'")
    return ["---", f'title: "{t}"', "---", kind, f"  %% Key: {spec.get('key', '')}", f"  %% Notice: {spec.get('notice', '')}"]


def mermaid_flowchart(spec, nodes, edges, direction="LR", groups=None):
    """Mermaid flowchart text: nodes [{id, label, shape, tone, group}], edges [{from, to, label, style, head}],
    groups {gid: label}. Families with a box-and-arrow type reuse this."""
    out = mermaid_head(spec, f"flowchart {direction}")
    groups = groups or {}

    def nd(n):
        a, b = MM_SHAPE.get(n.get("shape") or "rounded", ("(", ")"))
        return f"  {mm_id(n['id'])}{a}{mm_text(n.get('label', n['id']))}{b}"

    for g, lab in groups.items():
        out.append(f"  subgraph {mm_id('g_' + g)} [{mm_text(lab)}]")
        out += ["  " + nd(n) for n in nodes if n.get("group") == g]
        out.append("  end")
    out += [nd(n) for n in nodes if n.get("group") not in groups]
    for e in edges:
        style, head = e.get("style") or "solid", e.get("head") or "filled"
        link = {"solid": "-->", "dashed": "-.->", "dotted": "-.->", "thick": "==>"}[style]
        if head == "none":
            link = {"-->": "---", "-.->": "-.-", "==>": "==="}[link]
        if (e.get("tail") or "none") != "none" and head != "none":
            link = "<" + link
        lab = f"|{mm_text(e['label'])}|" if e.get("label") else ""
        out.append(f"  {mm_id(e['from'])} {link}{lab} {mm_id(e['to'])}")
    used = {}
    for n in nodes:
        t = n.get("tone") or "plain"
        if n.get("solid"):
            used.setdefault("solid_" + t, []).append(mm_id(n["id"]))
        elif t in MM_TONE:
            used.setdefault(t, []).append(mm_id(n["id"]))
    for t, ids in used.items():
        if t.startswith("solid_"):
            s = MM_TONE.get(t[6:], MM_TONE["ink"])[1]
            out.append(f"  classDef {t} fill:{s},stroke:{s},color:#FFFFFF")
        else:
            f, s = MM_TONE[t]
            out.append(f"  classDef {t} fill:{f},stroke:{s}" + (",color:#FFFFFF" if t == "ink" else ""))
        out.append(f"  class {','.join(ids)} {t}")
    return "\n".join(out) + "\n"


# ---------- validation helpers for type modules ----------
def check_graph(spec, nodes_key="nodes", edges_key="edges"):
    """Errors for a nodes/edges spec: unique ids, known shapes, tones, heads, styles, edge ends that exist."""
    err, seen = [], set()
    nodes = spec.get(nodes_key) or []
    if not nodes:
        err.append(f"{nodes_key}: at least one node")
    for n in nodes:
        i = n.get("id")
        if not i:
            err.append(f"node without id: {n}")
            continue
        if i in seen:
            err.append(f"node {i}: duplicate id")
        seen.add(i)
        if (n.get("shape") or "rounded") not in SHAPES:
            err.append(f"node {i}: shape '{n['shape']}' is not one of {', '.join(SHAPES)}")
        if (n.get("tone") or "plain") not in TONES:
            err.append(f"node {i}: tone '{n['tone']}' is not one of {', '.join(TONES)}")
        if not n.get("label"):
            err.append(f"node {i}: needs a label")
    for e in spec.get(edges_key) or []:
        for k in ("from", "to"):
            if e.get(k) not in seen:
                err.append(f"edge {e.get('from')} -> {e.get('to')}: unknown node '{e.get(k)}'")
        for k, allowed in (("head", HEADS), ("tail", HEADS), ("style", STYLES), ("tone", EDGE_TONES)):
            if e.get(k) and e[k] not in allowed:
                err.append(f"edge {e.get('from')} -> {e.get('to')}: {k} '{e[k]}' is not one of {', '.join(a for a in allowed if a)}")
        if len(str(e.get("label", ""))) > 36:
            err.append(f"edge {e.get('from')} -> {e.get('to')}: label over 36 characters: shorten it or move it into a box")
    gids = {g["id"] for g in spec.get("groups") or []}
    for n in nodes:
        if n.get("group") and n["group"] not in gids:
            err.append(f"node {n.get('id')}: group '{n['group']}' is not in groups")
    return err


# ---------- graph styles: plain, dbt, airflow ----------
GRAPH_STYLES = ("plain", "dbt", "airflow")
# kind -> look; our palette, not dbt's own colours (dbt does not document them)
DBT_KINDS = {"source": {"tone": "green", "label": "source"}, "seed": {"tone": "teal", "label": "seed"},
             "model": {"tone": "blue", "label": "model"}, "snapshot": {"tone": "ink", "label": "snapshot"},
             "semantic_model": {"tone": "lav", "label": "semantic model"}, "metric": {"tone": "lav", "label": "metric"},
             "exposure": {"tone": "amber", "label": "exposure"}, "analysis": {"tone": "soft", "label": "analysis"},
             "test": {"tone": "soft", "label": "test"}, "saved_query": {"tone": "lav", "label": "saved query"},
             "function": {"tone": "soft", "label": "function"}}
# task instance states (airflow.apache.org core-concepts/tasks), worst first: a collapsed group shows its worst state
AIRFLOW_STATES = {"failed": {"tone": "red"}, "upstream_failed": {"tone": "amber"},
                  "up_for_retry": {"tone": "amber", "dashed": True}, "up_for_reschedule": {"tone": "teal", "dashed": True},
                  "running": {"tone": "teal"}, "restarting": {"tone": "teal", "dashed": True},
                  "deferred": {"tone": "lav", "dashed": True}, "awaiting_input": {"tone": "lav"},
                  "queued": {"tone": "soft"}, "scheduled": {"tone": "soft", "dashed": True},
                  "skipped": {"tone": "lav"}, "removed": {"tone": "soft", "dashed": True},
                  "success": {"tone": "green"}, "none": {"tone": "plain", "dashed": True, "label": "no status"}}
EDGE_KINDS = {"asset": {"style": "dashed", "tone": "lav", "label": "asset trigger"},
              "dataset": {"style": "dashed", "tone": "lav", "label": "dataset trigger"},
              "trigger": {"style": "dashed", "tone": "blue", "label": "triggers run"},
              "async": {"style": "dashed", "label": "async"},
              "failure": {"tone": "red", "label": "failure path"}}
VIEWS = ("detail", "overview")
GROUP_LAYOUTS = ("auto", "bands", "columns")


def _look(m, name):
    v = (m or {}).get(name)
    return {"tone": v} if isinstance(v, str) else dict(v or {})


def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 or word.endswith("s") else "s")


def collapse(nodes, edges, groups, ids, kinds=None, states=None):
    """Replace each group in ids by one node counting its members by state (when states) or kind; edges between
    groups merge (label kept when all agree, else 'n links'). groups: [{id, label, tag?, sub?, kind?, state?}].
    Returns (nodes, edges, groups)."""
    ids = set(ids)
    where = {n["id"]: (n.get("group") if n.get("group") in ids else n["id"]) for n in nodes}
    order = list(AIRFLOW_STATES) + [s for s in (states or {}) if s not in AIRFLOW_STATES]
    out = [n for n in nodes if n.get("group") not in ids]
    for g in groups:
        if g["id"] not in ids:
            continue
        mem = [n for n in nodes if n.get("group") == g["id"]]
        counts = {}
        by_state = bool(states) and any(n.get("state") for n in mem)
        for n in mem:
            k = (n.get("state") or "none") if by_state else (n.get("kind") or "node")
            counts[k] = counts.get(k, 0) + 1
        names = states if by_state else (kinds or {})
        parts = [(f"{v} {lb}" if by_state else _plural(v, lb))  # states read "2 upstream failed", kinds "2 models"
                 for k, v in sorted(counts.items(), key=lambda kv: -kv[1])
                 for lb in [_look(names, k).get("label", k).replace("_", " ")]]
        sub = " · ".join(parts)
        if text_width(sub, 12) > 170:  # one count per line rather than a break inside "1 upstream failed"
            sub = "\n".join(parts)
        st = [n.get("state") for n in mem if n.get("state") in order]
        kd = [n.get("kind") for n in mem if n.get("kind")]
        out.append({"id": g["id"], "label": g.get("label", g["id"]), "tag": g.get("tag"), "sub": g.get("sub") or sub,
                    "kind": g.get("kind") or (max(kd, key=kd.count) if kd else None),
                    "state": g.get("state") or (min(st, key=order.index) if st else None), "collapsed": True,
                    "shape": g.get("shape"), "count": len(mem), "group": g.get("parent")})
    merged = {}
    for e in edges:
        a, b = where.get(e["from"], e["from"]), where.get(e["to"], e["to"])
        if a == b and a in ids:
            continue
        m = merged.setdefault((a, b, e.get("kind"), e.get("style")), dict(e, **{"from": a, "to": b, "_l": [], "_n": 0}))
        if e.get("label"):
            m["_l"].append(str(e["label"]))
        m["_n"] += 1
    new = []
    for m in merged.values():
        ls, n = set(m.pop("_l")), m.pop("_n")
        m.pop("label", None)
        if len(ls) == 1:
            m["label"] = ls.pop()
        elif len(ls) > 1:
            m["label"] = f"{n} links"
        new.append(m)
    return out, new, [g for g in groups if g["id"] not in ids]


def style_graph(spec, nodes=None, edges=None, groups=None, kinds=None, states=None):
    """Apply spec["style"] (plain | dbt | airflow), spec["view"] (detail | overview) and spec["collapse"] to a
    node-edge spec. kinds / states: the calling type's {name: tone or {tone, label, shape, solid, dashed}}, overridden
    by spec["kinds"] / spec["states"]. Returns {"nodes", "edges", "groups", "legend", "group_layout", "direction"}:
    nodes ready for node(), edges for route(), legend entries for legend()."""
    style = spec.get("style") or "plain"
    nodes = [dict(n) for n in (spec.get("nodes") if nodes is None else nodes) or []]
    edges = [dict(e) for e in (spec.get("edges") if edges is None else edges) or []]
    groups = [dict(g) for g in (spec.get("groups") if groups is None else groups) or []]
    km = dict(DBT_KINDS if style == "dbt" else {}, **(kinds or {}), **(spec.get("kinds") or {}))
    sm = dict(AIRFLOW_STATES if style == "airflow" else {}, **(states or {}), **(spec.get("states") or {}))
    em = dict(EDGE_KINDS, **(spec.get("edge_kinds") or {}))
    ids = [g["id"] for g in groups] if spec.get("view") == "overview" else list(spec.get("collapse") or [])
    if ids:
        nodes, edges, groups = collapse(nodes, edges, groups, ids, km, sm or None)
    leg, used_k, used_s = [], [], []
    for n in nodes:
        k, st = n.get("kind"), n.get("state")
        look = {}
        if k in km:
            look.update(_look(km, k))
            used_k.append(k)
        if st in sm:
            look.update({x: v for x, v in _look(sm, st).items() if x != "label"})
            used_s.append(st)
        tags = []
        if style == "dbt":
            n.setdefault("mono", True)
            n["shape"] = n.get("shape") or look.get("shape") or "pill"
            n["solid"] = n.get("solid", look.get("solid", True))
            tags = [look.get("label", k)] if k else []
            if n.get("materialized"):
                tags.append(n["materialized"])
            if n.get("tests") and not n.get("sub"):
                n["sub"] = _plural(n["tests"], "test")
        elif style == "airflow":
            n.setdefault("mono", True)
            n["shape"] = n.get("shape") or look.get("shape") or "box"
            n["strong"] = n.get("strong", bool(st))
            tags = [n["operator"]] if n.get("operator") else []
            if st and not n.get("collapsed"):
                n["sub"] = " · ".join(x for x in (st.replace("_", " "), n.get("sub")) if x)
        else:
            n["shape"] = n.get("shape") or look.get("shape")
            n["solid"] = n.get("solid", look.get("solid", False))
        if n.get("collapsed"):
            n["strong"] = True
            base = n.get("tag") or {"dbt": "folder", "airflow": "task group"}.get(style, "group")
            word = {"dbt": "node", "airflow": "task"}.get(style, "item")
            tags = [f"{base} · {_plural(n['count'], word)}"]
        if tags:
            n["tag"] = " · ".join(tags)
        n["tone"] = n.get("tone") or look.get("tone")
        n["dashed"] = n.get("dashed", look.get("dashed", False))
    for k in dict.fromkeys(used_k):
        lk = _look(km, k)
        leg.append({"label": lk.get("label", k).replace("_", " "), "tone": lk.get("tone"),
                    "solid": lk.get("solid", style == "dbt"), "shape": lk.get("shape") or ("pill" if style == "dbt" else None)})
    for s in [x for x in sm if x in used_s]:
        ls = _look(sm, s)
        leg.append({"label": ls.get("label", s.replace("_", " ")), "tone": ls.get("tone"), "dashed": ls.get("dashed"),
                    "strong": style == "airflow"})
    for e in edges:
        ek = em.get(e.get("kind")) if e.get("kind") else None
        if ek:
            e["style"] = e.get("style") or ek.get("style")
            e["tone"] = e.get("tone") or ek.get("tone")
            leg.append({"label": ek.get("label", e["kind"]), "edge": {"style": e.get("style"), "tone": e.get("tone")}})
        elif style == "dbt":
            e["tone"] = e.get("tone") or "muted"
    return {"nodes": nodes, "edges": edges, "groups": groups, "legend": leg if spec.get("legend", True) else [],
            "group_layout": spec.get("group_layout") or ("columns" if style == "dbt" else "auto"),
            "direction": spec.get("direction") or ("LR" if style != "plain" else None)}


def check_style(spec):
    """Errors for the style fields of a node-edge spec: style, view, collapse, group_layout, kinds, states."""
    err = []
    for key, allowed, dflt in (("style", GRAPH_STYLES, "plain"), ("view", VIEWS, "detail"),
                               ("group_layout", GROUP_LAYOUTS, "auto")):
        if (spec.get(key) or dflt) not in allowed:
            err.append(f"{key} '{spec[key]}' is not one of {', '.join(allowed)}")
    gids = {g.get("id") for g in spec.get("groups") or []}
    for g in spec.get("collapse") or []:
        if g not in gids:
            err.append(f"collapse: '{g}' is not a group id")
    if spec.get("view") == "overview" and not gids:
        err.append("view overview: needs groups to collapse")
    for key in ("kinds", "states"):
        for name, v in (spec.get(key) or {}).items():
            t = v if isinstance(v, str) else (v or {}).get("tone")
            if t and t not in TONES:
                err.append(f"{key}.{name}: tone '{t}' is not one of {', '.join(TONES)}")
    return err


def graph(spec, nodes=None, edges=None, groups=None, kinds=None, states=None, direction=None, max_w=None,
          spread=False, gap=None):
    """Draw any node-edge diagram in the spec's style: style_graph(), layered layout (or fixed col/row on every
    node), group frames, nodes, orthogonal edges, legend. Returns (svg_body, geometry) like a type's svg function.
    Families map their own fields onto nodes {id, label, sub, tag, shape, tone, kind, state, group, ...} first.
    spread=True: one port per arrow (no shared trunks), for labelled arrows that must keep their own line.
    gap: main-axis gap between layers for the first layout (a top-down retry uses the default)."""
    st = style_graph(spec, nodes, edges, groups, kinds, states)
    c = canvas(spec)
    sized = _sized(spec, st["nodes"], max_w)
    edges = st["edges"]
    groups = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    gt = {g["id"]: g.get("tone") for g in st["groups"]}
    direction = direction or st["direction"]
    if all(n.get("col") is not None and n.get("row") is not None for n, _, _ in sized):
        lay = _fixed_layout(sized, edges, groups)
        direction = direction or "LR"
    else:
        items = [{"id": n["id"], "w": w, "h": h, "group": n.get("group"), "rank": n.get("rank")} for n, w, h in sized]
        lay = layout_layered(items, edges, direction or "LR", groups, gap=gap, group_layout=st["group_layout"])
        if lay["width"] > MAX_W and not direction:
            direction = "TB"
            lay = layout_layered(items, edges, direction, groups, group_layout=st["group_layout"])
        direction = direction or "LR"
    if lay["width"] > MAX_W:
        raise LayoutError(f"canvas would be {int(lay['width'])}px wide (max {MAX_W}): set direction TB, shorten labels, "
                          "use view 'overview' (one box per group) or split into one detail diagram per group")
    for g, r in lay["groups"].items():
        container(c, g, groups[g], *r, members=[n["id"] for n, _, _ in sized if n.get("group") == g], tone=gt.get(g),
                  label_w=lay.get("label_w"))
    for n, _, _ in sized:
        node(c, n, *lay["pos"][n["id"]])
    route(c, edges, direction, spread=spread)
    legend(c, st["legend"])
    return finish(c)


def mermaid_graph(spec, nodes=None, edges=None, groups=None, kinds=None, states=None):
    """Mermaid flowchart of a node-edge spec after style_graph(): same collapse, tones and solid fills."""
    st = style_graph(spec, nodes, edges, groups, kinds, states)
    gs = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    ns = [dict(n, label=" · ".join(str(x) for x in (n["label"], n.get("tag"), n.get("sub")) if x))
          if spec.get("style") in ("dbt", "airflow") else n for n in st["nodes"]]
    return mermaid_flowchart(spec, ns, st["edges"], st["direction"] or "LR", gs)


# ---------- built-in types ----------
def _sized(spec, nodes, max_w=None):
    out = []
    for n in nodes:
        n = dict(n)
        w, h = size(n, n.get("max_w", max_w or spec.get("max_w", 200)))
        out.append((n, w, h))
    return out


def _fixed_layout(sized, edges, groups):
    colw, rowh = {}, {}
    for n, w, h in sized:
        colw[n["col"]] = max(colw.get(n["col"], 0), w)
        rowh[n["row"]] = max(rowh.get(n["row"], 0), h)
    lab = max([text_width(str(e["label"]), 11, True) + 50 for e in edges if e.get("label")] or [56])
    cx, x = {}, MARGIN + (GP if groups else 0)
    for k in sorted(colw):
        cx[k] = x
        x += colw[k] + max(56, lab)
    ry, y = {}, MARGIN + (GP + 24 if groups else 0)
    for k in sorted(rowh):
        ry[k] = y
        y += rowh[k] + (56 if groups else 40)
    pos = {n["id"]: (cx[n["col"]] + (colw[n["col"]] - w) / 2, ry[n["row"]] + (rowh[n["row"]] - h) / 2, w, h)
           for n, w, h in sized}
    grect = {}
    for g in groups:
        rs = [pos[n["id"]] for n, _, _ in sized if n.get("group") == g]
        if rs:
            ls = label_lines(groups[g], max(r[0] + r[2] for r in rs) - min(r[0] for r in rs) + 2 * GP)
            x0, y0 = min(r[0] for r in rs) - GP, min(r[1] for r in rs) - GP - len(ls) * 15 - 10
            grect[g] = (x0, y0, max(r[0] + r[2] for r in rs) + GP - x0, max(r[1] + r[3] for r in rs) + GP - y0)
    return {"pos": pos, "groups": grect, "width": max(r[0] + r[2] for r in pos.values()) + MARGIN}


def svg_boxes(spec, core):
    return graph(spec)


def validate_boxes(spec):
    return check_graph(spec) + check_style(spec)


def mermaid_boxes(spec):
    return mermaid_graph(spec)


def validate_layers(spec):
    err = []
    layers = spec.get("layers") or []
    if not layers:
        err.append("layers: at least one layer {id, label, items}")
    flat = {"nodes": [it for l in layers for it in l.get("items") or []], "edges": spec.get("edges") or []}
    for l in layers:
        if not l.get("items"):
            err.append(f"layer {l.get('id')}: needs items")
        if not l.get("label"):
            err.append(f"layer {l.get('id')}: needs a label")
    return err + check_graph(flat)


def svg_layers(spec, core):
    c = canvas(spec)
    c["geo"]["connected"] = bool(spec.get("edges"))
    hw = spec.get("header_w", 130)
    avail = MAX_W - 2 * MARGIN - hw - 32
    gx, gy = 24, 18
    rows = []
    for l in spec["layers"]:
        sized = _sized(spec, l["items"])
        lines, cur, cw = [], [], 0
        for s in sized:
            if cur and cw + gx + s[1] > avail:
                lines.append(cur)
                cur, cw = [], 0
            cw += (gx if cur else 0) + s[1]
            cur.append(s)
        lines.append(cur)
        rows.append((l, lines))
    inner_w = max(sum(s[1] for s in ln) + gx * (len(ln) - 1) for _, lines in rows for ln in lines)
    W = hw + inner_w + 48
    y, edges = MARGIN, spec.get("edges") or []
    band_gap = 40 if edges else 12
    for l, lines in rows:
        lh = sum(max(s[2] for s in ln) for ln in lines) + gy * (len(lines) - 1) + 32
        lh = max(lh, len(label_lines(l["label"], hw)) * 15 + 20)
        container(c, l.get("id", l["label"]), l["label"], MARGIN, y, W, lh, members=[s[0]["id"] for ln in lines for s in ln],
                  kind="band", header_w=hw)
        yy = y + 16
        for ln in lines:
            rh = max(s[2] for s in ln)
            tw = sum(s[1] for s in ln) + gx * (len(ln) - 1)
            x = MARGIN + hw + 24 + (inner_w - tw) / 2
            for n, w, h in ln:
                node(c, n, x, yy + (rh - h) / 2, w, h)
                x += w + gx
            yy += rh + gy
        y += lh + band_gap
    if W + 2 * MARGIN > MAX_W + 1:
        raise LayoutError(f"canvas would be {int(W + 2 * MARGIN)}px wide (max {MAX_W}): shorten item labels")
    route(c, edges, "TB")
    return finish(c)


def mermaid_layers(spec):
    out = mermaid_head(spec, "flowchart TB")
    for l in spec["layers"]:
        out.append(f"  subgraph {mm_id('l_' + str(l.get('id', l['label'])))} [{mm_text(l['label'])}]")
        out.append("    direction LR")
        for n in l["items"]:
            a, b = MM_SHAPE.get(n.get("shape") or "rounded", ("(", ")"))
            out.append(f"    {mm_id(n['id'])}{a}{mm_text(n['label'])}{b}")
        out.append("  end")
    ls = spec["layers"]
    if not spec.get("edges"):
        for a, b in zip(ls, ls[1:]):
            out.append(f"  {mm_id('l_' + str(a.get('id', a['label'])))} ~~~ {mm_id('l_' + str(b.get('id', b['label'])))}")
    for e in spec.get("edges") or []:
        lab = f"|{mm_text(e['label'])}|" if e.get("label") else ""
        out.append(f"  {mm_id(e['from'])} -->{lab} {mm_id(e['to'])}")
    return "\n".join(out) + "\n"


def validate_grid(spec):
    err = []
    cols, rows = spec.get("columns") or [], spec.get("rows") or []
    if not cols or not rows:
        err.append("grid: needs columns [..] and rows [{label, cells}]")
    for r in rows:
        if len(r.get("cells") or []) != len(cols):
            err.append(f"row '{r.get('label')}': {len(r.get('cells') or [])} cells for {len(cols)} columns")
        for x in r.get("cells") or []:
            if isinstance(x, dict) and (x.get("tone") or "plain") not in TONES:
                err.append(f"row '{r.get('label')}': tone '{x['tone']}' is not one of {', '.join(TONES)}")
    return err


def svg_grid(spec, core):
    c = canvas(spec)
    c["geo"]["connected"] = False
    cols, rows = spec["columns"], spec["rows"]
    cells = [[x if isinstance(x, dict) else {"label": str(x)} for x in r["cells"]] for r in rows]
    cw = max([size({"label": x["label"], "sub": x.get("sub")}, 170, 80)[0] for r in cells for x in r if x.get("label")] + [90])
    cw = max(cw, min(170, max(text_width(s, 11, True) for s in cols) + 20))
    ch = max([size({"label": x["label"], "sub": x.get("sub")}, cw, cw)[1] for r in cells for x in r if x.get("label")] + [40])
    m = layout_matrix([r["label"] for r in rows], cols, cell_w=cw, cell_h=ch)
    if m["width"] > MAX_W:
        raise LayoutError(f"grid would be {int(m['width'])}px wide (max {MAX_W}): fewer columns, shorter cells, or split it")
    for j, s in enumerate(cols):
        x, y, w, h = m["cols"][j]
        rect(c, x, y, w, h, "dg-hd", 4)
        ls = wrap(s, w - 12, 11, True)
        for k, t in enumerate(ls):
            text(c, x + w / 2, y + (h - len(ls) * 15) / 2 + k * 15, t, "dg-txm", "middle", mono=True)
    for i, r in enumerate(rows):
        x, y, w, h = m["rows"][i]
        rect(c, x, y, w, h, "dg-hd", 4)
        ls = wrap(r["label"], w - 16, 12, bold=True)
        for k, t in enumerate(ls):
            text(c, x + 10, y + (h - len(ls) * 16) / 2 + k * 16, t, "dg-txb", bold=True, size=12)
        for j, x_ in enumerate(cells[i]):
            if x_.get("label"):
                n = {"id": f"c{i}_{j}", "label": x_["label"], "sub": x_.get("sub"), "tone": x_.get("tone"), "shape": "box"}
                node(c, n, *m["cells"][(i, j)])
    return finish(c)


BUILTIN = {
    "boxes": {"svg": svg_boxes, "mermaid": mermaid_boxes, "validate": validate_boxes, "family": "base",
              "doc": "generic node-edge graph: style plain|dbt|airflow, view detail|overview, groups, fixed col/row"},
    "layers": {"svg": svg_layers, "mermaid": mermaid_layers, "validate": validate_layers, "family": "base",
               "doc": "stacked horizontal bands of boxes (layered architecture, medallion), optional arrows"},
    "grid": {"svg": svg_grid, "mermaid": lambda spec: None, "validate": validate_grid, "family": "base",
             "doc": "row headers x column headers with a short text per cell"},
}


# ---------- registry ----------
_REG = None
REG_ERRORS = []


def registry(refresh=False):
    """{type name: {"svg", "mermaid", "validate", "family", "doc"}}: built-ins, then every TYPES dict found in
    ../../darshan-singh-meel-diagrams-*/scripts/types_*.py and in $DIAGRAM_TYPES (files or folders, os.pathsep)."""
    global _REG
    if _REG is not None and not refresh:
        return _REG
    REG_ERRORS.clear()
    reg = dict(BUILTIN)
    files = sorted(HERE.parent.parent.glob("darshan-singh-meel-diagrams-*/scripts/types_*.py"))
    for p in filter(None, os.environ.get("DIAGRAM_TYPES", "").split(os.pathsep)):
        p = Path(p)
        files += sorted(p.glob("types_*.py")) if p.is_dir() else [p]
    for f in files:
        try:
            spec = importlib.util.spec_from_file_location(f"dgtypes_{f.parent.parent.name}_{f.stem}".replace("-", "_"), f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            types = getattr(mod, "TYPES")
        except Exception as ex:  # one broken family must not stop the others
            REG_ERRORS.append(f"{f.parent.parent.name}/{f.name}: {type(ex).__name__}: {ex}")
            continue
        for name, t in types.items():
            if name in reg:
                REG_ERRORS.append(f"{f.parent.parent.name}/{f.name}: type '{name}' already defined by {reg[name].get('family')}")
                continue
            if not callable(t.get("svg")):
                REG_ERRORS.append(f"{f.parent.parent.name}/{f.name}: type '{name}' has no svg function")
                continue
            reg[name] = {"mermaid": lambda s: None, "validate": lambda s: [], "family": f.parent.parent.name,
                         "doc": "", **t}
    _REG = reg
    return reg


# ---------- build ----------
def _common(spec):
    err = []
    if not isinstance(spec, dict):
        return ["spec must be a JSON object"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(spec.get("id", ""))):
        err.append("id: lowercase letters, digits and '-' (unique on the page), e.g. 'order-flow'")
    for k, mx in (("title", 90), ("key", 200), ("notice", 220)):
        v = spec.get(k)
        if not v or not str(v).strip():
            err.append(f"{k}: required, one line")
        elif "\n" in str(v) or len(str(v)) > mx:
            err.append(f"{k}: one line, at most {mx} characters")
    if not spec.get("type"):
        err.append("type: required (python diagram.py --list)")
    return err


def _chrome(spec, W):
    tl = wrap(spec["title"], W - 32, 15, bold=True)
    key = str(spec["key"])
    key = key if key.lower().startswith("key") else "Key: " + key
    kl = wrap(key, W - 32, 11.5, True)
    nl = wrap("Notice: " + str(spec["notice"]), W - 32, 12.5)
    return tl, kl, nl


def _root(spec, body, geo, chrome, extra_css=()):
    did = "dg-" + spec["id"]
    W, H = max(geo["width"], 320 if chrome else 0), geo["height"]
    top, foot = 0, []
    head = ""
    if chrome:
        tl, kl, nl = _chrome(spec, W)
        head = "".join(f'<text class="dg-title" x="16" y="{22 + i * 20}">{esc(s)}</text>' for i, s in enumerate(tl))
        top = 12 + len(tl) * 20
        y = top + H + 4
        for s in kl:
            foot.append(f'<text class="dg-key" x="16" y="{y + 12}">{esc(s)}</text>')
            y += 16
        y += 4
        for s in nl:
            foot.append(f'<text class="dg-notice" x="16" y="{y + 13}">{esc(s)}</text>')
            y += 18
        H = y + 10
    v = lambda p: ";".join(f"--dg-{k.replace('_', '-')}:{x}" for k, x in p.items())  # noqa: E731
    s = "#" + did
    css = (f"{s}{{{v(LIGHT)}}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]) {s},svg{s}:root{{{v(DARK)}}}}}"
           f":root[data-theme=dark] {s}{{{v(DARK)}}}" + BASE_CSS.replace("#S", s) + "".join(x.replace("#S", s) for x in extra_css))
    desc = f"{spec['key']} Notice: {spec['notice']}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" id="{did}" class="dg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="{did}-t {did}-d"><title id="{did}-t">{esc(spec["title"])}</title>'
            f'<desc id="{did}-d">{esc(desc)}</desc><style>{css}</style>'
            f'<rect class="dg-bg" width="{W}" height="{H}"/>{head}<g transform="translate(0,{top})">{body}</g>{"".join(foot)}</svg>')


def figure_html(spec, svg_plain):
    """The page fragment: HTML title, the svg in a frame that scrolls sideways on phones, key and Notice lines."""
    key = str(spec["key"])
    key = key if key.lower().startswith("key") else "Key: " + key
    return (f'<figure class="dg-fig" id="fig-{esc(spec["id"])}" style="margin:16px 0">'
            f'<figcaption class="dg-title" style="font-weight:600;font-size:15px;margin:0 0 8px">{esc(spec["title"])}</figcaption>'
            f'<div class="dg-frame" style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%">{svg_plain}</div>'
            f'<p class="dg-key" style="font:12px/1.5 {esc(MONO)};color:var(--muted,#5B6068);margin:8px 0 0">{esc(key)}</p>'
            f'<p class="dg-notice" style="font-size:13px;margin:4px 0 0">Notice: {esc(spec["notice"])}</p></figure>')


def build(spec, chrome=True):
    """spec dict -> {"svg": standalone svg (title, key, Notice drawn in when chrome), "html": figure fragment,
    "geometry", "mermaid": text or None, "errors": [str], "warnings": [str]}. Never raises on a bad spec."""
    res = {"svg": "", "html": "", "geometry": None, "mermaid": None, "errors": [], "warnings": []}
    reg = registry()
    res["warnings"] += [f"registry: {e}" for e in REG_ERRORS]
    res["errors"] = _common(spec)
    if not isinstance(spec, dict):
        return res
    t = reg.get(spec.get("type"))
    if spec.get("type") and not t:
        res["errors"].append(f"type '{spec.get('type')}' unknown: one of {', '.join(sorted(reg))}")
    if res["errors"]:
        return res
    try:
        res["errors"] += list(t["validate"](spec) or [])
    except Exception as ex:
        res["errors"].append(f"validate crashed: {type(ex).__name__}: {ex}")
    if res["errors"]:
        return res
    try:
        out = t["svg"](spec, sys.modules[__name__])
        body, geo = out[0], out[1]
        extra = out[2] if len(out) > 2 else ()
    except LayoutError as ex:
        res["errors"].append(f"layout: {ex}")
        return res
    except Exception as ex:
        res["errors"].append(f"layout crashed: {type(ex).__name__}: {ex}")
        return res
    geo["id"], geo["type"] = spec["id"], spec["type"]
    res["geometry"] = geo
    probs, warns = checker.check(geo)
    res["errors"] += [f"LAYOUT {spec['id']} | {p} | {x}" for p, x in probs]
    res["warnings"] += [f"WARN {spec['id']} | {p} | {x}" for p, x in warns]
    res["svg"] = _root(spec, body, geo, chrome, extra)
    res["html"] = figure_html(spec, _root(spec, body, geo, False, extra))
    try:
        res["mermaid"] = t["mermaid"](spec)
    except Exception as ex:
        res["warnings"].append(f"mermaid crashed: {type(ex).__name__}: {ex}")
    return res


def page(results, title="Diagrams"):
    """A standalone HTML page holding the figures of several build() results."""
    v = lambda p: ";".join(f"--{k.replace('_', '-')}:{x}" for k, x in p.items())  # noqa: E731
    figs = "".join(r["html"] for r in results if r.get("html"))
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" "
            f"content=\"width=device-width,initial-scale=1\"><title>{esc(title)}</title><style>"
            f":root{{{v(LIGHT)}}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{v(DARK)}}}}}"
            f":root[data-theme=dark]{{{v(DARK)}}}body{{margin:0;background:var(--ground);color:var(--ink);"
            f"font:15px/1.55 {SANS}}}main{{max-width:1104px;margin:0 auto;padding:24px 16px}}"
            ".dg-fig{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px}"
            f"</style></head><body><main>{figs}</main></body></html>")


def png(svg, out, dark=False, scale=1.5):
    """Render one standalone svg to PNG with Playwright (Chromium). Returns an error text or None."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "PNG needs Playwright: pip install playwright && playwright install chromium"
    bg = DARK["ground"] if dark else LIGHT["ground"]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "p.html"
        f.write_text(f'<!doctype html><meta charset="utf-8"><body style="margin:0;padding:12px;background:{bg}">{svg}</body>',
                     encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1100, "height": 900}, color_scheme="dark" if dark else "light",
                            device_scale_factor=scale)
            pg.goto(f.as_uri())
            pg.locator("svg").first.screenshot(path=str(out))
            b.close()
    return None


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("-o", "--out", help="standalone SVG (title, key and Notice drawn in)")
    ap.add_argument("--mermaid", help="Mermaid text; skipped with a note when the type has no Mermaid form")
    ap.add_argument("--page", help="standalone HTML page with the figure")
    ap.add_argument("--fragment", help="HTML figure fragment for pasting into a page")
    ap.add_argument("--geometry", help="geometry JSON for check.py")
    ap.add_argument("--png", help="PNG via Playwright, to look at")
    ap.add_argument("--dark", action="store_true", help="render the PNG in dark mode")
    ap.add_argument("--list", action="store_true", help="list the registered types")
    a = ap.parse_args(argv)
    if a.list:
        for name, t in sorted(registry().items(), key=lambda x: (x[1].get("family", ""), x[0])):
            print(f"{t.get('family', ''):42} {name:24} {t.get('doc', '')}")
        for e in REG_ERRORS:
            print("REGISTRY", e)
        return 0
    if not a.spec:
        ap.error("spec.json is required")
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    r = build(spec)
    for w in r["warnings"]:
        print(w)
    for e in r["errors"]:
        print(e if e.startswith("LAYOUT") else f"ERROR {spec.get('id', '?') if isinstance(spec, dict) else '?'} | {e}")
    if r["svg"]:
        if a.out:
            Path(a.out).write_text(r["svg"], encoding="utf-8")
        if a.page:
            Path(a.page).write_text(page([r], spec["title"]), encoding="utf-8")
        if a.fragment:
            Path(a.fragment).write_text(r["html"], encoding="utf-8")
        if a.geometry:
            Path(a.geometry).write_text(json.dumps(r["geometry"], indent=1), encoding="utf-8")
        if a.mermaid:
            if r["mermaid"]:
                Path(a.mermaid).write_text(r["mermaid"], encoding="utf-8")
            else:
                print(f"NOTE {spec['id']} | no Mermaid form | embed the SVG file instead")
        if a.png:
            err = png(r["svg"], a.png, a.dark)
            if err:
                print(f"NOTE {spec['id']} | {err}")
    print(f"{'FAIL' if r['errors'] else 'OK'} {spec.get('id', '?') if isinstance(spec, dict) else '?'} | "
          f"{len(r['errors'])} errors, {len(r['warnings'])} warnings"
          + (f" | {r['geometry']['width']}x{r['geometry']['height']}px" if r["geometry"] else ""))
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
