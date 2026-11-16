"""Flow family for darshan-singh-meel-diagrams: flowchart, swimlane (BPMN-lite), decision-tree, state-machine,
activity (UML fork/join), retry-flow, approval-workflow. The base registry loads TYPES from this file; spec fields are
in ../references/*.md. Own shapes (parallelogram, BPMN events and gateways, UML pseudostates, fork bars) are drawn
over a hidden base box, so the base checker still sees every box and label."""
import diagram as core

F = core.F
CSS = ("#S .fx-own>.dg-sh:not(.fx-o){fill:none!important;stroke:none!important}"
       "#S .fx-ink{fill:var(--dg-ink);stroke:var(--dg-ink)}"
       "#S .fx-ln{fill:none;stroke:var(--dg-ink);stroke-width:1.4}"
       "#S .fx-mk{fill:none;stroke:var(--dg-ink);stroke-width:3;stroke-linecap:round}"
       "#S .fx-inv{fill:none;stroke:var(--dg-card);stroke-width:1.3}"
       "#S .dg-sh.fx-thick{stroke-width:3.4}#S .dg-sh.fx-thin{stroke-width:1.4}"
       "#S .fx-ol{font-size:11.5px;fill:var(--dg-ink)}")
OUT_SIZE, OUT_LH, OUT_W = 11.5, 15, 100  # labels drawn outside events and gateways


# ---------- own shapes (svg drawn inside the node group, over the hidden base box) ----------
def _circle(cx, cy, r, cls):
    return f'<circle class="{cls}" cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}"/>'


def _para(x, y, w, h):
    s = 12
    return f'<polygon class="dg-sh fx-o" points="{F(x + s)},{F(y)} {F(x + w)},{F(y)} {F(x + w - s)},{F(y + h)} {F(x)},{F(y + h)}"/>'


def _subproc(x, y, w, h):
    return (f'<rect class="dg-sh fx-o" x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="3"/>'
            f'<path class="dg-sh2" d="M{F(x + 8)},{F(y)} V{F(y + h)} M{F(x + w - 8)},{F(y)} V{F(y + h)}"/>')


def _dot(x, y, w, h):
    return _circle(x + w / 2, y + h / 2, min(w, h) / 2, "fx-ink")


def _bullseye(x, y, w, h):
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) / 2
    return _circle(cx, cy, r, "dg-sh fx-o fx-thin") + _circle(cx, cy, r - 5, "fx-ink")


def _flow_final(x, y, w, h):
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) / 2
    k = r * 0.62
    return (_circle(cx, cy, r, "dg-sh fx-o fx-thin") +
            f'<path class="fx-ln" d="M{F(cx - k)},{F(cy - k)} L{F(cx + k)},{F(cy + k)} M{F(cx + k)},{F(cy - k)} L{F(cx - k)},{F(cy + k)}"/>')


def _bar(x, y, w, h):
    return f'<rect class="fx-ink" x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="1.5"/>'


def _diamond(x, y, w, h):
    return (f'<polygon class="dg-sh fx-o" points="{F(x + w / 2)},{F(y)} {F(x + w)},{F(y + h / 2)} '
            f'{F(x + w / 2)},{F(y + h)} {F(x)},{F(y + h / 2)}"/>')


def _gateway(x, y, w, h, kind):
    cx, cy = x + w / 2, y + h / 2
    out = _diamond(x, y, w, h)
    if kind == "exclusive":
        k = 6.5
        out += f'<path class="fx-mk" d="M{F(cx - k)},{F(cy - k)} L{F(cx + k)},{F(cy + k)} M{F(cx + k)},{F(cy - k)} L{F(cx - k)},{F(cy + k)}"/>'
    elif kind == "parallel":
        k = 9
        out += f'<path class="fx-mk" d="M{F(cx - k)},{F(cy)} H{F(cx + k)} M{F(cx)},{F(cy - k)} V{F(cy + k)}"/>'
    elif kind == "inclusive":
        out += f'<circle class="fx-mk" stroke-width="2.6" cx="{F(cx)}" cy="{F(cy)}" r="8.5" style="stroke-width:2.6"/>'
    return out


def _event(x, y, w, h, kind, trigger):
    """BPMN event: start = single thin circle, intermediate = double thin, end = single thick. Catching markers are
    unfilled, throwing (end) markers filled."""
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) / 2
    out = _circle(cx, cy, r, "dg-sh fx-o " + ("fx-thick" if kind == "end" else "fx-thin"))
    if kind == "intermediate":
        out += _circle(cx, cy, r - 3.5, "fx-ln")
    throw = kind == "end"
    if trigger == "message":
        ex, ey, ew, eh = cx - 8, cy - 5.5, 16, 11
        out += (f'<rect class="{"fx-ink" if throw else "fx-ln"}" x="{F(ex)}" y="{F(ey)}" width="{ew}" height="{eh}"/>'
                f'<path class="{"fx-inv" if throw else "fx-ln"}" d="M{F(ex)},{F(ey)} L{F(cx)},{F(cy + 1)} L{F(ex + ew)},{F(ey)}"/>')
    elif trigger == "timer":
        out += _circle(cx, cy, 9.5, "fx-ln") + f'<path class="fx-ln" d="M{F(cx)},{F(cy - 6.5)} V{F(cy)} L{F(cx + 5)},{F(cy + 3)}"/>'
    elif trigger == "error":
        pts = [(-7, 7), (-3, -7), (2, 1), (7, -7), (3, 7), (-2, -1)]
        out += f'<polygon class="{"fx-ink" if throw else "fx-ln"}" points="' + " ".join(
            f"{F(cx + a)},{F(cy + b)}" for a, b in pts) + '"/>'
    elif trigger == "signal":
        out += (f'<polygon class="{"fx-ink" if throw else "fx-ln"}" points="{F(cx)},{F(cy - 8)} {F(cx + 8)},{F(cy + 6)} '
                f'{F(cx - 8)},{F(cy + 6)}"/>')
    elif trigger == "terminate":
        out += _circle(cx, cy, r - 7, "fx-ink")
    return out


OWN = {"io": _para, "subprocess": _subproc, "initial": _dot, "final": _bullseye, "flow_final": _flow_final,
       "bar": _bar, "choice": _diamond}


# ---------- shared drawing pipeline ----------
def _own_node(c, n, x, y, w, h, svg):
    """Draw base node n as a hidden box (keeps text, checks and routing), then put svg in its group, under the text."""
    core.node(c, dict(n, shape="box", cls=" ".join(x for x in (n.get("cls"), "fx-own") if x)), x, y, w, h)
    s = c["parts"][2][-1]
    i = s.index(">", s.index('<g class="dg-n')) + 1
    c["parts"][2][-1] = s[:i] + svg + s[i:]


def _out_lines(label):
    return core.wrap(label, OUT_W, OUT_SIZE) if label else []


def prep(n, max_w):
    """Sizing record for one node: shape box (w, h), layout item (iw, ih) with room for an outside label, the own
    shape painter and the outside label lines."""
    p = {"n": n, "paint": n.pop("_paint", None), "out": [], "where": n.pop("_out_where", "below")}
    fixed = n.pop("_box", None)
    out_label = n.pop("_out", None)
    pad = n.pop("_pad", 0)  # room above and below (LR) for a self-loop and its label
    padx = n.pop("_padx", 0)  # room left and right (TB)
    if fixed:
        w, h = fixed
    else:
        w, h = core.size(n, n.get("max_w", max_w))
        w += n.pop("_extra_w", 0)
        n["min_w"] = w
    p["w"], p["h"] = w, h
    p["out"] = _out_lines(out_label)
    if p["out"]:
        lw = max(core.text_width(s, OUT_SIZE) for s in p["out"])
        lh = len(p["out"]) * OUT_LH
        if p["where"] in ("left", "right"):  # symmetric room, so the shape stays centred on its slot
            p["iw"], p["ih"] = w + 2 * (lw + 8), max(h, lh)
        elif p["where"] == "nw":  # above, ending left of the top corner
            p["iw"], p["ih"] = w + 2 * max(0, lw + 6 - w / 2), h + 2 * (lh + 2)
        else:
            p["iw"], p["ih"] = max(w, lw + 4), h + 2 * (lh + 4)
    else:
        p["iw"], p["ih"] = w, h
    p["ih"] += 2 * pad
    p["iw"] += 2 * padx
    return p


def place(c, p, rect):
    """Draw prepared node p centred in its layout item rect; returns the shape rect."""
    x, y, iw, ih = rect
    w, h = p["w"], p["h"]
    sx, sy = x + (iw - w) / 2, y + (ih - h) / 2
    if p["paint"]:
        _own_node(c, p["n"], sx, sy, w, h, p["paint"](sx, sy, w, h))
    else:
        core.node(c, p["n"], sx, sy, w, h)
    if p["out"]:
        th = len(p["out"]) * OUT_LH
        lw = max(core.text_width(s, OUT_SIZE) for s in p["out"])
        wh = p["where"]
        if wh == "nw":
            lx, ty = sx + w / 2 - 6 - lw, sy - 2 - th
        elif wh in ("left", "right"):
            lx = sx - 6 - lw if wh == "left" else sx + w + 6
            ty = sy + h / 2 - th / 2
        else:
            lx = sx + w / 2 - lw / 2
            ty = sy + h + 4 if wh == "below" else sy - 4 - th
        for i, s in enumerate(p["out"]):
            core.text(c, lx, ty + i * OUT_LH, s, cls="fx-ol", size=OUT_SIZE)
        core.obstacle(c, lx, ty, lw, th, 4)  # edges route around the outside label
    return sx, sy, w, h


SIDE = {"below": "bottom", "above": "top", "left": "left", "right": "right"}
_N = {"right": (1, 0), "left": (-1, 0), "bottom": (0, 1), "top": (0, -1)}


def side_toward(a, b, avoid):
    """Side of rect a that faces rect b best, skipping the sides in avoid."""
    dx = (b[0] + b[2] / 2) - (a[0] + a[2] / 2)
    dy = (b[1] + b[3] / 2) - (a[1] + a[3] / 2)
    for s in sorted(_N, key=lambda s: -(dx * _N[s][0] + dy * _N[s][1])):
        if s not in avoid:
            return s
    return "right"


def fix_sides(c, edges, avoid):
    """Give edges touching a node with an outside label a side away from that label (avoid: {id: {sides}})."""
    R = c["rects"]
    for e in edges:
        if e["from"] in avoid and not e.get("from_side") and e["from"] != e["to"]:
            e["from_side"] = side_toward(R[e["from"]], R[e["to"]], avoid[e["from"]])
        if e["to"] in avoid and not e.get("to_side") and e["from"] != e["to"]:
            e["to_side"] = side_toward(R[e["to"]], R[e["from"]], avoid[e["to"]])


def split_exits(c, edges, ids, direction):
    """Two or three exits of a small diamond (choice, decision) leave from its side corners, ordered across the flow,
    instead of bunching at the corner that faces the flow."""
    R = c["rects"]
    tb = direction == "TB"
    for i in ids:
        outs = [e for e in edges if e["from"] == i and e["to"] != i and not e.get("from_side")]
        if len(outs) not in (2, 3):
            continue
        across = 0 if tb else 1
        outs.sort(key=lambda e: R[e["to"]][across] + R[e["to"]][across + 2] / 2)
        sides = ["left", "right"] if tb else ["top", "bottom"]
        main = "bottom" if tb else "right"
        if len(outs) == 3:
            sides.insert(1, main)
        else:  # a target level with the diamond keeps the straight exit; the other takes the side it lies on
            mid = R[i][across] + R[i][across + 2] / 2
            off = [R[e["to"]][across] + R[e["to"]][across + 2] / 2 - mid for e in outs]
            if abs(off[0]) < 12:
                sides = [main, sides[1]]
            elif abs(off[1]) < 12:
                sides = [sides[0], main]
        for e, sd in zip(outs, sides):
            e["from_side"] = sd


def back_sides(c, edges, direction):
    """An edge that runs against the flow leaves and enters on the same outer side (top or bottom in LR, left or right
    in TB), chosen by where the target lies, so it does not ride on the forward edges between the two boxes."""
    R = c["rects"]
    tb = direction == "TB"
    for e in edges:
        if e["from"] == e["to"] or e.get("from_side") or e.get("to_side"):
            continue
        a, b = R[e["from"]], R[e["to"]]
        k = 1 if tb else 0
        if b[k] + b[k + 2] / 2 >= a[k] + a[k + 2] / 2 - 1:
            continue
        j = 1 - k
        up = a[j] + a[j + 2] / 2 <= b[j] + b[j + 2] / 2
        side = ("left" if up else "right") if tb else ("top" if up else "bottom")
        e["from_side"] = e["to_side"] = side


def split_arrivals(c, edges, direction):
    """Labelled edges from different sources into one box arrive on different sides, so each label stays on its own
    line instead of a shared trunk (state machines: several events lead to one state)."""
    R = c["rects"]
    into = {}
    for e in edges:
        if e.get("label") and e["from"] != e["to"]:
            into.setdefault(e["to"], []).append(e)
    flow = "top" if direction == "TB" else "left"
    for t, es in into.items():
        if len(es) < 2:
            continue
        used = {e["to_side"] for e in es if e.get("to_side")}
        for e in sorted(es, key=lambda e: core.text_width(e["label"], 11, True)):
            if e.get("to_side"):
                continue
            want = side_toward(R[t], R[e["from"]], used)
            if want not in used:
                e["to_side"] = want if used or want != flow else flow
                used.add(e["to_side"])


def _ahead(c, e, direction, straight=False):
    """True when e's target lies further along the flow than its source (a forward edge); straight: and its centre
    lies within the source's span across the flow."""
    a, b = c["rects"][e["from"]], c["rects"][e["to"]]
    k = 1 if direction == "TB" else 0
    j = 1 - k
    inline = a[j] <= b[j] + b[j + 2] / 2 <= a[j] + a[j + 2]
    return b[k] + b[k + 2] / 2 > a[k] + a[k + 2] / 2 + 1 and (inline or not straight)


def too_wide(width, fix):
    raise core.LayoutError(f"canvas would be {int(width)}px wide (max {core.MAX_W}): {fix}")


def layered(spec, preps, edges, groups=None, gtones=None, direction="LR", group_layout="bands", legend=(),
            composites=(), spread=False, auto_tb=True, side_kinds=(), split_in=False):
    """Layered layout of prepared nodes plus group frames, own shapes, outside labels and orthogonal edges.
    composites: group ids that edges may start or end on (UML composite states). Returns (body, geometry, [css])."""
    groups = groups or {}
    gtones = gtones or {}
    first = {}
    last = {}
    for p in preps:
        g = p["n"].get("group")
        if g:
            first.setdefault(g, p["n"]["id"])
            last[g] = p["n"]["id"]
    rank_edges = [dict(e, **{"from": last.get(e["from"], e["from"]) if e["from"] in composites else e["from"],
                             "to": first.get(e["to"], e["to"]) if e["to"] in composites else e["to"]}) for e in edges]
    items = [{"id": p["n"]["id"], "w": p["iw"], "h": p["ih"], "group": p["n"].get("group"), "rank": p["n"].get("rank")}
             for p in preps]
    lay = core.layout_layered(items, rank_edges, direction, groups, group_layout=group_layout)
    switched = lay["width"] > core.MAX_W and auto_tb and direction != "TB" and not spec.get("direction")
    if switched:
        direction = "TB"
        lay = core.layout_layered(items, rank_edges, direction, groups, group_layout=group_layout)
    if lay["width"] > core.MAX_W:
        too_wide(lay["width"], "set direction TB, shorten labels or max_w, collapse groups, or split at a hand-off")
    c = core.canvas(spec)
    for g, r in lay["groups"].items():
        core.container(c, g, groups[g], *r, members=[p["n"]["id"] for p in preps if p["n"].get("group") == g],
                       tone=gtones.get(g), label_w=lay.get("label_w"))
    avoid = {}
    for p in preps:
        place(c, p, lay["pos"][p["n"]["id"]])
        if p["out"] and p["where"] in SIDE:
            avoid[p["n"]["id"]] = {SIDE[p["where"]]}
    for g in composites:
        if g in lay["groups"]:
            c["rects"][g] = lay["groups"][g]
    edges = [dict(e) for e in edges]
    fix_sides(c, edges, avoid)
    split_exits(c, edges, [p["n"]["id"] for p in preps if p["paint"] is _diamond or p["n"].get("shape") == "diamond"], direction)
    back_sides(c, edges, direction)
    if split_in:
        split_arrivals(c, edges, direction)
    main = "bottom" if direction == "TB" else "right"
    entry = "top" if direction == "TB" else "left"
    looped = {e["from"] for e in edges if e["from"] == e["to"]}
    for e in edges:  # failure, rejection, escalation leave from a side: the main path keeps the flow direction
        if e.get("kind") in side_kinds and e["from"] != e["to"] and any(
                f["from"] == e["from"] and f.get("kind") not in side_kinds and f["to"] != f["from"] for f in edges):
            if not e.get("from_side"):
                e["from_side"] = side_toward(c["rects"][e["from"]], c["rects"][e["to"]], {main, entry})
            if not e.get("to_side") and e["from_side"] not in (main, entry) and _ahead(c, e, direction, True):
                e["to_side"] = e["from_side"]  # target straight ahead: stay in the side lane, clear of the main path
            e["own_port"] = True  # its own line out, never a trunk shared with the main path
    pair = ("right", "left") if direction == "TB" else ("top", "bottom")
    loop_side = {}
    for n in looped:  # the self-loop takes a side no side exit uses; a drawn edge back into it arrives opposite
        used = {e.get("from_side") for e in edges if e["from"] == n and e["to"] != n}
        loop_side[n] = next((sd for sd in pair if sd not in used), pair[0])
        other = pair[1] if loop_side[n] == pair[0] else pair[0]
        for e in edges:
            if e["to"] == n and e["from"] != n and not _ahead(c, e, direction):
                e["to_side"], e["own_port"] = other, True
    core.route(c, [e for e in edges if e["from"] != e["to"]], direction, spread=spread)
    for e in edges:
        if e["from"] == e["to"]:
            loop(c, e, direction, loop_side[e["from"]])
    core.legend(c, list(legend))
    body, geo = core.finish(c)
    if switched:
        geo["direction"] = direction  # LR ran out of width: the Mermaid header and the base checker read this
    return body, geo, [CSS]


def drawn_dir(svg_fn, spec, default):
    """Direction the SVG layout actually used, so the Mermaid text matches the picture."""
    try:
        return svg_fn(spec, core)[1].get("direction") or spec.get("direction") or default
    except core.LayoutError:
        return spec.get("direction") or default


LOOP = 24  # how far a self-loop stands off its box


def loop_room(label, direction):
    """Item padding that keeps a self-loop and its label clear of neighbours and group frames."""
    if direction == "TB":
        return {"_padx": LOOP + 8 + (core.text_width(label, 11, True) + 14 if label else 0)}
    return {"_pad": LOOP + (22 if label else 4)}


def loop(c, e, direction, side=None):
    """Self-loop drawn as a small rectangle on one side (default top in LR, right in TB), label beside it."""
    x, y, w, h = c["rects"][e["from"]]
    lw = core.text_width(str(e.get("label", "")), 11, True) + 10
    side = side or ("right" if direction == "TB" else "top")
    if side in ("right", "left"):
        y0, y1 = y + h * 0.3, y + h * 0.7
        bx, xr = (x + w, x + w + LOOP) if side == "right" else (x, x - LOOP)
        sx = 1 if side == "right" else -1
        pts, xy = [(bx, y0), (xr, y0), (xr, y1), (bx, y1)], (xr + sx * (lw / 2 + 6), (y0 + y1) / 2)
    else:
        x0, x1 = x + w * 0.35, x + w * 0.65
        by, yt = (y, y - LOOP) if side == "top" else (y + h, y + h + LOOP)
        sy = -1 if side == "top" else 1
        pts, xy = [(x1, by), (x1, yt), (x0, yt), (x0, by)], ((x0 + x1) / 2, yt + sy * 11)
    core.arrow(c, pts, e, xy if e.get("label") else None)


def mermaid_flow(spec, nodes, edges, direction, groups=None, own=None):
    """Mermaid flowchart via the base writer; own: {node id: (mermaid shape name, show label)} for the shapes the
    classic bracket syntax lacks (written as id@{ shape: ..., label: ... })."""
    own = own or {}
    base = [dict(n, shape="box" if n["id"] in own else n.get("shape"), label=n.get("label") or "") for n in nodes]
    txt = core.mermaid_flowchart(spec, base, edges, direction, groups)
    for n in base:
        if n["id"] in own:
            shape, show = own[n["id"]]
            mid = core.mm_id(n["id"])
            new = f"{mid}@{{ shape: {shape}" + (f", label: {core.mm_text(n['label'])}" if show and n["label"] else "") + " }"
            txt = txt.replace(f"{mid}[{core.mm_text(n['label'])}]", new, 1)
    hexes = {t: v[1] for t, v in core.MM_TONE.items()}
    hexes["muted"] = core.LIGHT["muted"]
    styles = [f"  linkStyle {k} stroke:{hexes[e['tone']]}" for k, e in enumerate(edges) if e.get("tone") in hexes]
    return txt + "".join(x + "\n" for x in styles)


def _ids(items, what):
    err, seen = [], set()
    for n in items:
        i = n.get("id")
        if not i:
            err.append(f"{what}: every item needs an id")
        elif i in seen:
            err.append(f"{what} {i}: duplicate id")
        seen.add(i)
    return err, seen


def _edges_ok(edges, ids, what="edge", label_keys=("label",)):
    err = []
    for e in edges:
        for k in ("from", "to"):
            if e.get(k) not in ids:
                err.append(f"{what} {e.get('from')} -> {e.get('to')}: unknown id '{e.get(k)}'")
        for k, allowed in (("head", core.HEADS), ("tail", core.HEADS), ("style", core.STYLES), ("tone", core.EDGE_TONES)):
            if e.get(k) and e[k] not in allowed:
                err.append(f"{what} {e.get('from')} -> {e.get('to')}: {k} '{e[k]}' is not one of "
                           + ", ".join(a for a in allowed if a))
    return err


def _deg(edges):
    din, dout = {}, {}
    for e in edges:
        dout[e["from"]] = dout.get(e["from"], 0) + 1
        din[e["to"]] = din.get(e["to"], 0) + 1
    return din, dout


def _no_style(spec, name):
    if (spec.get("style") or "plain") != "plain" or spec.get("view") or spec.get("collapse"):
        return [f"{name}: fixed notation, style/view/collapse do not apply: drop them (use flowchart, retry-flow or "
                "approval-workflow for the airflow or dbt look)"]
    return []


# ---------- flowchart family (flowchart, retry-flow, approval-workflow) ----------
FLOW_KINDS = {"start": "pill", "end": "pill", "step": "box", "decision": "diamond", "io": "io",
              "subprocess": "subprocess", "store": "cylinder", "document": "document", "note": "note",
              "wait": "hexagon", "manual": "rounded"}
RETRY_KINDS = dict(FLOW_KINDS, dlq="cylinder", alert="note", compensate="rounded", fallback="rounded")
RETRY_TONES = {"dlq": "red", "alert": "amber", "compensate": "amber"}
APPROVAL_KINDS = {"start": "pill", "end": "pill", "submit": "rounded", "review": "box", "approve": "box",
                  "auto": "box", "notify": "rounded", "decision": "diamond", "timer": "hexagon", "store": "cylinder"}
APPROVAL_OUTCOMES = {"approved": {"tone": "green", "label": "approved"},
                     "rejected": {"tone": "red", "label": "rejected"},
                     "changes": {"style": "dashed", "tone": "amber", "label": "changes requested"},
                     "escalate": {"style": "dashed", "tone": "blue", "label": "timeout / escalation"}}
RETRY_EDGES = {"retry": {"style": "dashed", "tone": "amber", "label": "retry"},
               "failure": {"tone": "red", "label": "failure path"},
               "compensate": {"style": "dashed", "tone": "amber", "label": "compensation"},
               "fallback": {"style": "dotted", "label": "fallback"}}


SINKS = ("end", "dlq", "alert", "compensate", "fallback", "note", "store", "document")  # may end a path


# dbt style: the flow kind becomes the pill colour and legend entry
DBT_FLOW = {"start": "green", "end": "soft", "step": "blue", "decision": "amber", "io": "teal", "subprocess": "blue",
            "store": "ink", "document": "soft", "note": "soft", "wait": "lav", "manual": "amber", "dlq": "red",
            "alert": "amber", "compensate": "amber", "fallback": "lav", "submit": "teal", "review": "blue",
            "approve": "blue", "auto": "ink", "notify": "soft", "timer": "lav"}


def _flow_nodes(spec, items, kinds, tones=None, max_w=180):
    """Map flow items {id, label, kind, ...} onto base nodes: shape by kind, own painters for io / subprocess."""
    out = []
    for it in items:
        n = {k: v for k, v in it.items() if k not in ("kind", "role", "sla", "retry", "timeout", "cat")}
        k = it.get("kind") or ("step" if "step" in kinds else next(iter(kinds)))
        dbt = spec.get("style") == "dbt"
        if dbt:
            n["kind"] = it.get("cat") or k  # the author's category (check, build, deploy ...) colours the pill
        shape = kinds.get(k, "box")
        if dbt and shape == "box" and not it.get("shape"):
            shape = None  # the base dbt look draws a plain step as a pill
        if k == "end" and not it.get("tone"):
            n["tone"] = "soft"
        if (tones or {}).get(k) and not it.get("tone"):
            n["tone"] = tones[k]
        if shape in ("io", "subprocess"):
            n["shape"] = "box"
            n["_extra_w"] = 24 if shape == "io" else 16
            n["_paint"] = OWN[shape]
        else:
            n["shape"] = it.get("shape") or shape
        if shape == "diamond" or k in ("review", "approve"):
            n["decision"] = True
        out.append(n)
    return out


CAT_TONES = ("blue", "teal", "amber", "lav", "green", "ink", "soft")  # red stays for failure


def _styled(spec, nodes, edges, groups, edge_kinds=None):
    s = dict(spec, edge_kinds=dict(edge_kinds or {}, **(spec.get("edge_kinds") or {})))
    if spec.get("style") != "dbt":
        return core.style_graph(s, nodes, edges, groups)
    kinds, k = dict(DBT_FLOW), 0
    for n in nodes:  # a category the spec's kinds does not name gets the next free tone
        c = n.get("kind")
        if c not in kinds and c not in (spec.get("kinds") or {}) and c not in core.DBT_KINDS:
            kinds[c] = CAT_TONES[k % len(CAT_TONES)]
            k += 1
    st = core.style_graph(s, nodes, edges, groups, kinds=kinds)
    tags = {n["id"]: n["tag"] for n in nodes if n.get("tag")}
    for n in st["nodes"]:  # the author's tag (role, operator, timeout) wins over the kind name
        if n["id"] in tags and not n.get("collapsed"):
            n["tag"] = tags[n["id"]]
    return st


def _draw_flow(spec, nodes, edges, groups, edge_kinds=None, default_dir="TB", max_w=180, spread=False, side_kinds=()):
    st = _styled(spec, nodes, edges, groups, edge_kinds)
    paints = {n["id"]: (n.get("_paint"), n.get("_extra_w")) for n in nodes}
    gl = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    gt = {g["id"]: g.get("tone") for g in st["groups"]}
    first = spec.get("direction") or default_dir
    tries = [first] + (["TB"] if first != "TB" and not spec.get("direction") else [])
    for k, direction in enumerate(tries):  # self-loop room depends on the direction: prepare per try
        loops = {e["from"]: loop_room(e.get("label"), direction) for e in st["edges"] if e["from"] == e["to"]}
        preps = []
        for n in st["nodes"]:
            n = dict(n)
            pt, xw = paints.get(n["id"], (None, None))
            if pt:
                n["_paint"], n["_extra_w"] = pt, xw
            n.update(loops.get(n["id"], {}))
            preps.append(prep(n, max_w))
        try:
            out = layered(spec, preps, st["edges"], gl, gt, direction, st["group_layout"], st["legend"],
                          spread=spread, auto_tb=False, side_kinds=side_kinds)
            if k:
                out[1]["direction"] = direction  # LR ran out of width: the Mermaid header and the base checker read this
            return out
        except core.LayoutError as ex:
            if k == len(tries) - 1 or "canvas would be" not in str(ex):
                raise


def _mm_flow_type(spec, nodes, edges, groups, edge_kinds=None, default_dir="TB", direction=None):
    st = _styled(spec, nodes, edges, groups, edge_kinds)
    own = {n["id"]: ("lean-r" if n.get("_paint") is _para else "subproc", True) for n in nodes if n.get("_paint")}
    ns = st["nodes"]
    if spec.get("style") in ("dbt", "airflow"):
        ns = [dict(n, label=" · ".join(str(x) for x in (n["label"], n.get("tag"), n.get("sub")) if x)) for n in ns]
    gs = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    return mermaid_flow(spec, ns, st["edges"], direction or spec.get("direction") or default_dir, gs, own)


def _check_flow(spec, items_key, edges_key, kinds):
    items, edges = spec.get(items_key) or [], spec.get(edges_key) or []
    err, ids = _ids(items, items_key[:-1])
    if not items:
        err.append(f"{items_key}: at least one item")
    gids = {g.get("id") for g in spec.get("groups") or []}
    for it in items:
        if not it.get("label"):
            err.append(f"{items_key[:-1]} {it.get('id')}: needs a label")
        if it.get("kind") and it["kind"] not in kinds:
            err.append(f"{items_key[:-1]} {it.get('id')}: kind '{it['kind']}' is not one of {', '.join(kinds)}")
        if (it.get("tone") or "plain") not in core.TONES:
            err.append(f"{items_key[:-1]} {it.get('id')}: tone '{it['tone']}' is not one of {', '.join(core.TONES)}")
        if it.get("cat") is not None and (spec.get("style") != "dbt" or not isinstance(it["cat"], str)):
            err.append(f"{items_key[:-1]} {it.get('id')}: cat is the dbt-style colour key: a short text, with style 'dbt'")
        if it.get("group") and it["group"] not in gids:
            err.append(f"{items_key[:-1]} {it.get('id')}: group '{it['group']}' is not in groups")
        if it.get("id") in gids:
            err.append(f"{items_key[:-1]} {it.get('id')}: id also used by a group")
    err += _edges_ok(edges, ids)
    for e in edges:
        if len(str(e.get("label", ""))) > 36:
            err.append(f"edge {e.get('from')} -> {e.get('to')}: label over 36 characters: shorten it or move it into a box sub")
    din, dout = _deg([e for e in edges if e.get("from") != e.get("to")])
    what = items_key[:-1]
    kind = {it.get("id"): it.get("kind") for it in items}
    has_end = "end" in kind.values()  # with explicit ends, every other step must lead somewhere
    for it in items:
        i = it.get("id")
        if it.get("kind") == "end" and dout.get(i):
            err.append(f"{what} {i}: an end has no outgoing arrow")
        if has_end and din.get(i) and not dout.get(i) and (it.get("kind") or "step") not in SINKS:
            err.append(f"{what} {i}: dead end (arrows in, none out): add its next step, or make it kind 'end'"
                       + (", 'dlq' or 'alert'" if "dlq" in kinds else ""))
    if sum(1 for k in kind.values() if k == "start") > 1 and spec.get("view") != "overview":
        err.append(f"{items_key}: more than one 'start': one process has one start; draw two diagrams, or one start "
                   "and a decision")
    for e in edges:
        if kind.get(e.get("from")) == "decision" and not (e.get("label") or e.get("outcome") or e.get("kind")):
            err.append(f"edge {e.get('from')} -> {e.get('to')}: an exit of a decision needs a label (the answer)")
    return err + core.check_style(spec)


# flowchart
def svg_flowchart(spec, core_):
    return _draw_flow(spec, _flow_nodes(spec, spec["nodes"], FLOW_KINDS), spec.get("edges") or [], spec.get("groups"))


def mermaid_flowchart(spec):
    return _mm_flow_type(spec, _flow_nodes(spec, spec["nodes"], FLOW_KINDS), spec.get("edges") or [], spec.get("groups"),
                         direction=drawn_dir(svg_flowchart, spec, "TB"))


def validate_flowchart(spec):
    err = _check_flow(spec, "nodes", "edges", FLOW_KINDS)
    if not err and not any(n.get("kind") == "start" for n in spec["nodes"]) and spec.get("view") != "overview":
        err.append("flowchart: needs one node with kind 'start' (where the process begins)")
    return err


# retry-flow
def _retry_edges(spec):
    edges = [dict(e) for e in spec.get("edges") or []]
    for s in spec.get("steps") or []:
        r = s.get("retry")
        if r:
            lab = f"retry ≤{r.get('max')}" + (f" · {r['delay']}" if r.get("delay") else "")
            edges.append({"from": s["id"], "to": s["id"], "kind": "retry", "label": lab})
    return edges


def _retry_nodes(spec):
    nodes = _flow_nodes(spec, spec.get("steps") or [], RETRY_KINDS, RETRY_TONES)
    by = {s["id"]: s for s in spec.get("steps") or []}
    for n in nodes:
        s = by[n["id"]]
        if s.get("timeout"):
            n["tag"] = " · ".join(x for x in (n.get("tag"), f"timeout {s['timeout']}") if x)
            if n.get("operator"):  # airflow style shows the operator as the tag
                n["operator"] = f"{n['operator']} · timeout {s['timeout']}"
    return nodes


def svg_retry(spec, core_):
    return _draw_flow(spec, _retry_nodes(spec), _retry_edges(spec), spec.get("groups"), RETRY_EDGES, "LR", 170, True,
                      ("failure", "compensate", "fallback"))


def mermaid_retry(spec):
    return _mm_flow_type(spec, _retry_nodes(spec), _retry_edges(spec), spec.get("groups"), RETRY_EDGES, "LR",
                         drawn_dir(svg_retry, spec, "LR"))


def validate_retry(spec):
    err = _check_flow(spec, "steps", "edges", RETRY_KINDS)
    if err:
        return err
    steps = {s["id"]: s for s in spec["steps"]}
    for s in spec["steps"]:
        r = s.get("retry")
        if r is not None and (not isinstance(r, dict) or not isinstance(r.get("max"), int) or r["max"] < 1):
            err.append(f"step {s['id']}: retry needs {{\"max\": n ≥ 1}} (unbounded retries hide outages)")
    edges = spec.get("edges") or []
    fails = [e for e in edges if e.get("kind") in ("failure", "compensate", "fallback")]
    if not fails:
        err.append("retry-flow: no failure path: add an edge with kind 'failure' to show where exhausted retries go")
    ends = {i for i, s in steps.items() if s.get("kind") in ("dlq", "alert", "end", "compensate", "fallback")}
    if fails and not any(e["to"] in ends for e in fails):
        err.append("retry-flow: no failure path ends in a dlq, alert, compensate, fallback or end step")
    if not any(s.get("retry") for s in spec["steps"]) and not any(e.get("kind") == "retry" for e in edges):
        err.append("retry-flow: no retry: set retry {max, delay} on a step, or use flowchart")
    return err


# approval-workflow
def _approval_nodes(spec):
    nodes = _flow_nodes(spec, spec.get("steps") or [], APPROVAL_KINDS)
    by = {s["id"]: s for s in spec.get("steps") or []}
    for n in nodes:
        s = by[n["id"]]
        if s.get("role"):
            n["tag"] = " · ".join(x for x in (s["role"], n.get("tag")) if x)
        if s.get("sla"):
            n["sub"] = " · ".join(x for x in (n.get("sub"), f"SLA {s['sla']}") if x)
    return nodes


def _approval_edges(spec):
    out = []
    for e in spec.get("edges") or []:
        e = dict(e)
        o = e.pop("outcome", None)
        if o:
            e["kind"] = o
            e.setdefault("label", APPROVAL_OUTCOMES[o]["label"] if o != "changes" else "changes")
        out.append(e)
    return out


def svg_approval(spec, core_):
    return _draw_flow(spec, _approval_nodes(spec), _approval_edges(spec), spec.get("groups"), APPROVAL_OUTCOMES, "TB", 170, True,
                      ("rejected", "changes", "escalate"))


def mermaid_approval(spec):
    return _mm_flow_type(spec, _approval_nodes(spec), _approval_edges(spec), spec.get("groups"), APPROVAL_OUTCOMES, "TB",
                         drawn_dir(svg_approval, spec, "TB"))


def validate_approval(spec):
    err = _check_flow(spec, "steps", "edges", APPROVAL_KINDS)
    if err:
        return err
    steps = {s["id"]: s for s in spec["steps"]}
    for e in spec.get("edges") or []:
        if e.get("outcome") and e["outcome"] not in APPROVAL_OUTCOMES:
            err.append(f"edge {e['from']} -> {e['to']}: outcome '{e['outcome']}' is not one of {', '.join(APPROVAL_OUTCOMES)}")
    outs = {}
    for e in spec.get("edges") or []:
        outs.setdefault(e["from"], set()).add(e.get("outcome"))
    for i, s in steps.items():
        if s.get("kind") in ("review", "approve"):
            o = outs.get(i, set())
            if "approved" not in o or not o & {"rejected", "changes"}:
                err.append(f"step {i}: a {s['kind']} step needs an 'approved' exit and a 'rejected' or 'changes' exit")
            if not s.get("role"):
                err.append(f"step {i}: name the approving role (role)")
    sub = {s.get("role") for s in steps.values() if s.get("kind") == "submit" and s.get("role")}
    for i, s in steps.items():
        if s.get("kind") == "approve" and s.get("role") in sub:
            err.append(f"step {i}: approver role '{s['role']}' also submits: separate the roles (four-eyes rule)")
    return err


# ---------- decision tree ----------
def _tree_nodes(spec):
    items = spec.get("nodes") or []
    parents = {n.get("parent") for n in items}
    out = []
    for it in items:
        n = {k: v for k, v in it.items() if k not in ("parent", "answer", "outcome")}
        if it["id"] in parents:
            n.setdefault("shape", "box")
            n["strong"] = n.get("strong", True)
            n["decision"] = True
        else:
            n.setdefault("shape", "pill")
            n.setdefault("tone", "soft")
        out.append(n)
    edges = [{"from": it["parent"], "to": it["id"], "label": it.get("answer", "")} for it in items if it.get("parent")]
    return out, edges


def svg_tree(spec, core_):
    nodes, edges = _tree_nodes(spec)
    direction = spec.get("direction") or "TB"
    par = {n["id"]: n.get("parent") for n in spec["nodes"]}
    preps = {n["id"]: prep(dict(n), spec.get("max_w", 170)) for n in nodes}
    lab = max([core.text_width(e["label"], 11, True) + 24 for e in edges if e["label"]] or [40])
    gap = (28, 76) if direction == "TB" else (20, max(72, lab + 40))
    lay = core.layout_tree([{"id": i, "w": p["iw"], "h": p["ih"], "parent": par[i]} for i, p in preps.items()],
                           direction, gap)
    if lay["width"] > core.MAX_W:
        too_wide(lay["width"], "set direction LR, shorten labels or max_w, or split a subtree into its own diagram")
    c = core.canvas(spec)
    for i, p in preps.items():
        place(c, p, lay["pos"][i])
    tree_edges(c, edges, direction)
    body, geo = core.finish(c)
    return body, geo, [CSS]


def tree_edges(c, edges, direction):
    """Org-chart style connectors: trunk from the parent, a bus halfway to the children, a drop into each child.
    Each answer sits on the part of the bus only its own edge uses."""
    R = c["rects"]
    tb = direction == "TB"
    m = (lambda r: (r[1], r[3])) if tb else (lambda r: (r[0], r[2]))  # main axis start, size
    x = (lambda r: r[0] + r[2] / 2) if tb else (lambda r: r[1] + r[3] / 2)  # cross-axis centre
    pt = (lambda a, b: (a, b)) if tb else (lambda a, b: (b, a))  # (cross, main) -> (x, y)
    kids = {}
    for e in edges:
        kids.setdefault(e["from"], []).append(e)
    for par, es in kids.items():
        pr = R[par]
        pc, pe = x(pr), m(pr)[0] + m(pr)[1]
        bus = (pe + min(m(R[e["to"]])[0] for e in es)) / 2
        for e in es:
            cr = R[e["to"]]
            cc, ct = x(cr), m(cr)[0]
            if abs(cc - pc) < 1:
                core.arrow(c, [pt(pc, pe), pt(pc, ct)], e, pt(pc, (bus + ct) / 2) if e.get("label") else None)
                continue
            near = [x(R[f["to"]]) for f in es if f is not e and (x(R[f["to"]]) - pc) * (cc - pc) > 0
                    and abs(x(R[f["to"]]) - pc) < abs(cc - pc)]
            start = max(near, key=lambda v: abs(v - pc)) if near else pc
            core.arrow(c, [pt(pc, pe), pt(pc, bus), pt(cc, bus), pt(cc, ct)], e,
                       pt((start + cc) / 2, bus) if e.get("label") else None)


def mermaid_tree(spec):
    nodes, edges = _tree_nodes(spec)
    return mermaid_flow(spec, nodes, edges, spec.get("direction") or "TB")


def validate_tree(spec):
    items = spec.get("nodes") or []
    err, ids = _ids(items, "node")
    err += _no_style(spec, "decision-tree")
    roots = [n for n in items if not n.get("parent")]
    if len(roots) != 1:
        err.append(f"decision-tree: exactly one root (node without parent), found {len(roots)}")
    kids = {}
    for n in items:
        if not n.get("label"):
            err.append(f"node {n.get('id')}: needs a label")
        if n.get("parent"):
            if n["parent"] not in ids:
                err.append(f"node {n['id']}: parent '{n['parent']}' unknown")
            kids.setdefault(n["parent"], []).append(n)
            if not n.get("answer"):
                err.append(f"node {n['id']}: needs the answer that leads to it (answer)")
            elif len(n["answer"]) > 36:
                err.append(f"node {n['id']}: answer over 36 characters")
        if (n.get("tone") or "plain") not in core.TONES:
            err.append(f"node {n.get('id')}: tone '{n['tone']}' is not one of {', '.join(core.TONES)}")
    for p, ks in kids.items():
        if len(ks) < 2:
            err.append(f"node {p}: a question needs at least two answers")
    seen, cur = set(), [r["id"] for r in roots]
    while cur:
        seen |= set(cur)
        cur = [n["id"] for n in items if n.get("parent") in cur and n["id"] not in seen]
    if roots and len(seen) < len(ids):
        err.append("decision-tree: a parent chain loops back: every node must lead back to the root")
    return err


# ---------- state machine (UML) ----------
STATE_KINDS = ("state", "initial", "final", "choice")


def _state_label(t):
    s = t.get("event") or ""
    if t.get("guard"):
        s += f" [{t['guard']}]"
    if t.get("action"):
        s += f" / {t['action']}"
    return s.strip()


def _state_parts(spec):
    states = spec.get("states") or []
    comps = {s.get("parent") for s in states if s.get("parent")}
    groups, nodes = {}, []
    for s in states:
        if s["id"] in comps:
            groups[s["id"]] = s.get("label", s["id"])
            continue
        k = s.get("kind") or "state"
        n = {"id": s["id"], "label": s.get("label", ""), "group": s.get("parent"), "tone": s.get("tone"),
             "dim": s.get("dim"), "tip": s.get("tip")}
        if k == "initial":
            n.update(label="", _box=(18, 18), _paint=_dot, free=False)
        elif k == "final":
            n.update(label="", _box=(24, 24), _paint=_bullseye)
        elif k == "choice":
            n.update(label="", _box=(28, 28), _paint=_diamond, decision=True)
        else:
            sub = [f"{w} / {s[w]}" for w in ("entry", "do", "exit") if s.get(w)]
            if sub:
                n["sub"] = "\n".join(sub)
            n["shape"] = "rounded"
        nodes.append(n)
    edges = []
    for t in spec.get("transitions") or []:
        e = {k: t[k] for k in ("from", "to", "style", "tone", "dim", "from_side", "to_side") if k in t}
        lab = _state_label(t)
        if lab:
            e["label"] = lab
        edges.append(e)
    return nodes, edges, groups


def svg_state(spec, core_):
    nodes, edges, groups = _state_parts(spec)
    preps = [prep(n, spec.get("max_w", 180)) for n in nodes]
    return layered(spec, preps, edges, groups, {}, spec.get("direction") or "LR", "bands", composites=set(groups), split_in=True)


def mermaid_state(spec):
    states = spec.get("states") or []
    by = {s["id"]: s for s in states}
    kind = lambda i: by[i].get("kind") or "state"  # noqa: E731
    comps = {s.get("parent") for s in states if s.get("parent")}
    out = core.mermaid_head(spec, "stateDiagram-v2")
    out.insert(4, f"  direction {drawn_dir(svg_state, spec, spec.get('direction') or 'LR')}")
    sid = lambda i: "[*]" if kind(i) in ("initial", "final") else core.mm_id(i)  # noqa: E731

    def scope(parent, ind):
        for s in states:
            if s.get("parent") != parent:
                continue
            i = s["id"]
            if i in comps:
                out.append(f"{ind}{core.mm_id(i)} : {s.get('label', i)}")
                out.append(f"{ind}state {core.mm_id(i)} {{")
                scope(i, ind + "  ")
                out.append(f"{ind}}}")
            elif kind(i) == "choice":
                out.append(f"{ind}state {core.mm_id(i)} <<choice>>")
            elif kind(i) == "state":
                out.append(f'{ind}state "{str(s.get("label", i)).replace(chr(34), chr(39))}" as {core.mm_id(i)}')
        for t in spec.get("transitions") or []:
            pf, pt = by[t["from"]].get("parent"), by[t["to"]].get("parent")
            if (pf if pf == pt else None) == parent:
                lab = _state_label(t).replace(":", " -")
                out.append(f"{ind}{sid(t['from'])} --> {sid(t['to'])}" + (f" : {lab}" if lab else ""))

    scope(None, "  ")
    used = {}
    for s in states:
        if s.get("tone") and kind(s["id"]) == "state" and s["id"] not in comps and s["tone"] in core.MM_TONE:
            used.setdefault(s["tone"], []).append(core.mm_id(s["id"]))
    for t, ids in used.items():
        f, k = core.MM_TONE[t]
        out += [f"  classDef {t} fill:{f},stroke:{k}", f"  class {','.join(ids)} {t}"]
    return "\n".join(out) + "\n"


def validate_state(spec):
    states, trans = spec.get("states") or [], spec.get("transitions") or []
    err, ids = _ids(states, "state")
    err += _no_style(spec, "state-machine")
    by = {s.get("id"): s for s in states}
    comps = {s.get("parent") for s in states if s.get("parent")}
    for s in states:
        k = s.get("kind") or "state"
        if k not in STATE_KINDS:
            err.append(f"state {s.get('id')}: kind '{k}' is not one of {', '.join(STATE_KINDS)}")
        if k == "state" and not s.get("label"):
            err.append(f"state {s.get('id')}: needs a label")
        p = s.get("parent")
        if p:
            if p not in by:
                err.append(f"state {s['id']}: parent '{p}' unknown")
            elif by[p].get("parent"):
                err.append(f"state {s['id']}: composite inside a composite: draw the inner state machine as its own diagram")
            elif (by[p].get("kind") or "state") != "state":
                err.append(f"state {s['id']}: parent '{p}' must be a normal state")
        if s.get("id") in comps and k != "state":
            err.append(f"state {s['id']}: only a normal state can hold sub-states")
    err += _edges_ok(trans, ids, "transition")
    if err:
        return err
    din, dout = _deg(trans)
    tops = [s for s in states if (s.get("kind") == "initial") and not s.get("parent")]
    if len(tops) != 1:
        err.append(f"state-machine: exactly one top-level initial state, found {len(tops)}")
    for c in comps:
        if sum(1 for s in states if s.get("parent") == c and s.get("kind") == "initial") > 1:
            err.append(f"state {c}: at most one initial state per composite")
    for s in states:
        i, k = s["id"], s.get("kind") or "state"
        if k == "initial":
            if din.get(i):
                err.append(f"state {i}: nothing enters an initial state")
            if dout.get(i) != 1:
                err.append(f"state {i}: an initial state has exactly one outgoing transition")
        if k == "final" and dout.get(i):
            err.append(f"state {i}: a final state has no outgoing transition")
        if k == "choice":
            g = [t for t in trans if t["from"] == i]
            if len(g) < 2 or any(not t.get("guard") for t in g):
                err.append(f"state {i}: a choice needs two or more outgoing transitions, each with a guard ([else] for the rest)")
    for t in trans:
        if by[t["from"]].get("kind") == "initial" and t.get("event"):
            err.append(f"transition {t['from']} -> {t['to']}: the initial transition has no event")
        if len(_state_label(t)) > 36:
            err.append(f"transition {t['from']} -> {t['to']}: label '{_state_label(t)}' over 36 characters: "
                       "shorten, or move the action into the target state's entry")
    return err


# ---------- activity (UML, fork/join) ----------
ACT_KINDS = ("action", "initial", "final", "flow_final", "decision", "merge", "fork", "join", "object", "accept", "send")


def _act_parts(spec):
    direction = spec.get("direction") or "TB"
    edges = [dict(e, label=f"[{e['guard']}]" if e.get("guard") else e.get("label", "")) for e in spec.get("edges") or []]
    for e in edges:
        if not e["label"]:
            e.pop("label")
        for k in ("guard",):
            e.pop(k, None)
    din, dout = _deg(edges)
    nodes = []
    for a in spec.get("nodes") or []:
        k = a.get("kind") or "action"
        n = {x: a[x] for x in ("id", "label", "sub", "tag", "tone", "dim", "tip", "rank") if x in a}
        n["group"] = a.get("partition")
        if k == "initial":
            n.update(label="", _box=(20, 20), _paint=_dot)
        elif k == "final":
            n.update(label="", _box=(26, 26), _paint=_bullseye)
        elif k == "flow_final":
            n.update(label="", _box=(24, 24), _paint=_flow_final)
        elif k in ("decision", "merge"):
            n.update(label="", _box=(30, 30), _paint=_diamond, decision=k == "decision")
        elif k in ("fork", "join"):
            m = max(din.get(a["id"], 0), dout.get(a["id"], 0))
            ln = max(44, 22 * (m - 1) + 34)
            n.update(label="", _box=(ln, 7) if direction == "TB" else (7, ln), _paint=_bar)
        elif k == "object":
            n["shape"] = "box"
        elif k in ("accept", "send"):
            n["shape"] = "box"
            n["tag"] = n.get("tag") or ("accept event" if k == "accept" else "send signal")
        else:
            n["shape"] = "rounded"
        nodes.append(n)
    return nodes, edges, direction


def svg_activity(spec, core_):
    nodes, edges, direction = _act_parts(spec)
    groups = {p["id"]: p.get("label", p["id"]) for p in spec.get("partitions") or []}
    preps = [prep(n, spec.get("max_w", 180)) for n in nodes]
    return layered(spec, preps, edges, groups, {}, direction, spec.get("group_layout") or "bands", spread=True,
                   auto_tb=False)


def mermaid_activity(spec):
    nodes, edges, direction = _act_parts(spec)
    kinds = {a["id"]: a.get("kind") or "action" for a in spec.get("nodes") or []}
    shape = {"initial": "sm-circ", "final": "fr-circ", "flow_final": "cross-circ", "fork": "fork", "join": "fork",
             "decision": "diam", "merge": "diam"}
    own = {i: (shape[k], False) for i, k in kinds.items() if k in shape}
    groups = {p["id"]: p.get("label", p["id"]) for p in spec.get("partitions") or []}
    return mermaid_flow(spec, nodes, edges, direction, groups, own)


def validate_activity(spec):
    nodes, edges = spec.get("nodes") or [], spec.get("edges") or []
    err, ids = _ids(nodes, "node")
    err += _no_style(spec, "activity")
    pids = {p.get("id") for p in spec.get("partitions") or []}
    for a in nodes:
        k = a.get("kind") or "action"
        if k not in ACT_KINDS:
            err.append(f"node {a.get('id')}: kind '{k}' is not one of {', '.join(ACT_KINDS)}")
        if k in ("action", "object", "accept", "send") and not a.get("label"):
            err.append(f"node {a.get('id')}: needs a label")
        if a.get("partition") and a["partition"] not in pids:
            err.append(f"node {a.get('id')}: partition '{a['partition']}' is not in partitions")
    err += _edges_ok(edges, ids)
    if err:
        return err
    din, dout = _deg(edges)
    if not any((a.get("kind") == "initial") for a in nodes):
        err.append("activity: needs an initial node")
    for a in nodes:
        i, k = a["id"], a.get("kind") or "action"
        rules = {"initial": (0, 0, 1, 1), "final": (1, 99, 0, 0), "flow_final": (1, 99, 0, 0),
                 "fork": (1, 1, 2, 99), "join": (2, 99, 1, 1), "decision": (1, 1, 2, 99), "merge": (2, 99, 1, 1)}
        if k in rules:
            lo_i, hi_i, lo_o, hi_o = rules[k]
            if not (lo_i <= din.get(i, 0) <= hi_i and lo_o <= dout.get(i, 0) <= hi_o):
                err.append(f"node {i}: a {k} has {lo_i}-{hi_i if hi_i < 99 else 'n'} incoming and "
                           f"{lo_o}-{hi_o if hi_o < 99 else 'n'} outgoing flows (has {din.get(i, 0)} in, {dout.get(i, 0)} out)")
        if k == "decision" and any(not e.get("guard") for e in edges if e["from"] == i):
            err.append(f"node {i}: every flow out of a decision needs a guard ([else] for the rest)")
    for e in edges:
        if len(str(e.get("guard") or e.get("label") or "")) > 34:
            err.append(f"edge {e['from']} -> {e['to']}: guard over 34 characters")
    return err


# ---------- swimlane / cross-functional process (BPMN-lite) ----------
SW_KINDS = ("task", "subprocess", "start", "intermediate", "end", "gateway", "data")
TRIGGERS = ("none", "message", "timer", "error", "signal", "terminate")
GATEWAYS = ("exclusive", "parallel", "inclusive")
FLOW_TYPES = ("sequence", "message", "default", "conditional")
POOL_W, LANE_W, POOL_GAP = 92, 104, 22


def _pool_of(spec):
    return {ln["id"]: ln.get("pool") for ln in spec.get("lanes") or []}


def _lane_label(spec, ln):
    """A lane named like its pool shows no second header (one-lane pool "Vendor / Vendor")."""
    plabel = {p.get("id"): p.get("label", p.get("id")) for p in spec.get("pools") or []}
    pl = plabel.get(ln.get("pool"))
    lab = ln.get("label", "")
    return "" if pl and lab.strip().lower() == str(pl).strip().lower() else lab


def _sw_edges(spec):
    out = []
    for f in spec.get("flows") or []:
        t = f.get("type") or "sequence"
        e = {k: f[k] for k in ("from", "to", "label", "tone", "dim", "from_side", "to_side") if k in f}
        if t == "message":
            e.update(style="dashed", tail="circle", head="tri")
        elif t == "default":
            e["label"] = e.get("label") or "default"
        elif t == "conditional":
            e["tail"] = "odiamond"
        out.append(e)
    return out


def _sw_node(it, max_w, tb):
    k = it.get("kind") or "task"
    n = {x: it[x] for x in ("id", "label", "sub", "tag", "tone", "dim", "tip", "href") if x in it}
    if k in ("start", "intermediate", "end"):
        trig = it.get("trigger") or "none"
        n.update(label="", _box=(34, 34), _paint=lambda x, y, w, h, k=k, t=trig: _event(x, y, w, h, k, t),
                 _out=it.get("label"), _out_where="right" if tb else "below")
    elif k == "gateway":
        g = it.get("gateway") or "exclusive"
        n.update(label="", _box=(40, 40), _paint=lambda x, y, w, h, g=g: _gateway(x, y, w, h, g),
                 _out=it.get("label"), _out_where="nw")
        if g != "parallel":
            n["decision"] = True
    elif k == "subprocess":
        n.update(shape="rounded", tag=" · ".join(x for x in (n.get("tag"), "sub-process ⊞") if x), strong=True)
    elif k == "data":
        n.update(shape="document")
    else:
        n["shape"] = "rounded"
    return prep(n, it.get("max_w", max_w))


def _sw_cols(spec, edges):
    """Step index along the flow: a sequence flow moves one step on, a message flow keeps the step (the receiver
    sits level with the sender), except a reply (the sender was itself reached by a message), which moves one step
    on so the flow never reads backwards; back edges (loops) are ignored; a node's own col wins."""
    items = spec["nodes"]
    ids = [n["id"] for n in items]
    _, back = core.ranks(ids, edges)
    col = {n["id"]: n.get("col") or 0 for n in items}
    fixed = {n["id"] for n in items if n.get("col") is not None}
    flows = spec.get("flows") or []
    replied = {f["to"] for f in flows if f.get("type") == "message"}
    for _ in range(len(ids)):
        moved = False
        for k, (f, e) in enumerate(zip(flows, edges)):
            if k in back or e["to"] in fixed:
                continue
            msg = (f.get("type") or "sequence") == "message"
            want = col[e["from"]] + (0 if msg and e["from"] not in replied else 1)
            if col[e["to"]] < want:
                col[e["to"]], moved = want, True
        if not moved:
            break
    return col


def _lanes_tb(spec, preps, col, lanes, pools):
    """Lanes as columns, flow top to bottom, pool name above its lanes: {pos, lanes, pools, width, head}."""
    lane_of = {it["id"]: it["lane"] for it in spec["nodes"]}
    gap_x, gap_y, pad = 22, 50, 18
    cell = {}
    for it in spec["nodes"]:
        cell.setdefault((lane_of[it["id"]], col[it["id"]]), []).append(it["id"])
    li = {ln["id"]: k for k, ln in enumerate(lanes)}
    succ = {}
    for f in spec.get("flows") or []:
        succ.setdefault(f["from"], []).append(li[lane_of[f["to"]]])
    for v in cell.values():  # side by side in one lane: the box whose next steps lie further right goes right
        v.sort(key=lambda i: sum(succ.get(i, [li[lane_of[i]]])) / len(succ.get(i, [0])))
    lw = {}
    for ln in lanes:
        need = [sum(preps[i]["iw"] for i in v) + gap_x * (len(v) - 1) for (lane, _), v in cell.items() if lane == ln["id"]]
        lw[ln["id"]] = max(need + [90]) + 2 * pad
    rows = sorted({r for _, r in cell})
    rh = {r: max(preps[i]["ih"] for (_, rr), v in cell.items() if rr == r for i in v) for r in rows}
    head = max([len(core.label_lines(_lane_label(spec, ln), lw[ln["id"]])) for ln in lanes] + [1]) * 15 + 12
    has_pool = any(pools.values())
    ptop = 30 if has_pool else 0
    x, prev, lrect, prect = core.MARGIN, None, {}, {}
    for ln in lanes:
        pid = pools[ln["id"]]
        if lrect and pid != prev:
            x += POOL_GAP
        prev = pid
        lrect[ln["id"]] = [x, core.MARGIN + ptop, lw[ln["id"]], 0]
        if has_pool:
            r = prect.setdefault(pid, [x, core.MARGIN, 0, 0])
            r[2] = x + lw[ln["id"]] - r[0]
        x += lw[ln["id"]]
    ry, y = {}, core.MARGIN + ptop + head + 18
    for r in rows:
        ry[r] = y
        y += rh[r] + gap_y
    bottom = y - gap_y + 18
    for r in list(lrect.values()) + list(prect.values()):
        r[3] = bottom - r[1]
    pos = {}
    for (lane, r), v in cell.items():
        lx, _, w, _ = lrect[lane]
        tot = sum(preps[i]["iw"] for i in v) + gap_x * (len(v) - 1)
        cx = lx + (w - tot) / 2
        for i in v:
            pos[i] = (cx, ry[r] + (rh[r] - preps[i]["ih"]) / 2, preps[i]["iw"], preps[i]["ih"])
            cx += preps[i]["iw"] + gap_x
    return {"pos": pos, "lanes": {k: tuple(v) for k, v in lrect.items()},
            "pools": {k: tuple(v) for k, v in prect.items()}, "width": x + core.MARGIN, "head": head}


def _lanes_lr(spec, preps, col, lanes, pools):
    """Lanes as rows, flow left to right, pool header column on the left: same record as _lanes_tb."""
    items = spec["nodes"]
    has_pool = any(pools.values())
    lay = core.layout_lanes([{"id": ln["id"], "label": _lane_label(spec, ln)} for ln in lanes],
                            [{"id": it["id"], "w": preps[it["id"]]["iw"], "h": preps[it["id"]]["ih"],
                              "lane": it["lane"], "col": col[it["id"]]} for it in items],
                            _sw_edges(spec), header_w=LANE_W, gap=44, row_gap=18)
    dx = POOL_W if has_pool else 0
    order, k, prev = {}, -1, object()
    for ln in lanes:
        if pools[ln["id"]] != prev:
            k += 1
            prev = pools[ln["id"]]
        order[ln["id"]] = k
    lane_of = {it["id"]: it["lane"] for it in items}
    lrect = {i: (r[0] + dx, r[1] + order[i] * POOL_GAP, r[2], r[3]) for i, r in lay["lanes"].items()}
    pos = {i: (r[0] + dx, r[1] + order[lane_of[i]] * POOL_GAP, r[2], r[3]) for i, r in lay["pos"].items()}
    prect = {}
    if has_pool:
        for pid in dict.fromkeys(pools.values()):
            ls = [ln["id"] for ln in lanes if pools[ln["id"]] == pid]
            y0, y1 = min(lrect[i][1] for i in ls), max(lrect[i][1] + lrect[i][3] for i in ls)
            prect[pid] = (core.MARGIN, y0, dx + lrect[ls[0]][2], y1 - y0)
    return {"pos": pos, "lanes": lrect, "pools": prect, "width": lay["width"] + dx}


def svg_swimlane(spec, core_):
    max_w = spec.get("max_w", 130)
    lanes, items = spec["lanes"], spec["nodes"]
    pools = _pool_of(spec)
    edges = _sw_edges(spec)
    col = _sw_cols(spec, edges)
    for d in [spec["direction"]] if spec.get("direction") else ["LR", "TB"]:
        tb = d == "TB"
        preps = {it["id"]: _sw_node(dict(it), max_w, tb) for it in items}
        lay = (_lanes_tb if tb else _lanes_lr)(spec, preps, col, lanes, pools)
        if lay["width"] <= core.MAX_W:
            break
    if lay["width"] > core.MAX_W:
        too_wide(lay["width"], "set direction TB (lanes as columns), use fewer lanes, shorten labels or max_w, "
                               "or split the process at a hand-off into two diagrams")
    c = core.canvas(spec)
    plabel = {p.get("id"): p.get("label", p.get("id")) for p in spec.get("pools") or []}
    for pid, r in lay["pools"].items():
        core.container(c, f"pool-{pid}", plabel.get(pid, pid or ""), *r, kind="lane", header_w=0 if tb else POOL_W,
                       members=[it["id"] for it in items if pools[it["lane"]] == pid])
    for ln in lanes:
        r = lay["lanes"][ln["id"]]
        core.container(c, ln["id"], _lane_label(spec, ln), *r, kind="lane", header_w=0 if tb else LANE_W,
                       members=[it["id"] for it in items if it["lane"] == ln["id"]])
        if tb:
            core.line(c, [(r[0], r[1] + lay["head"]), (r[0] + r[2], r[1] + lay["head"])])
    avoid = {}
    for i, p in preps.items():
        place(c, p, lay["pos"][i])
        if p["out"] and p["where"] in SIDE:
            avoid[i] = {SIDE[p["where"]]}
    fix_sides(c, edges, avoid)
    split_exits(c, edges, [it["id"] for it in items if (it.get("kind") or "task") == "gateway"], "TB" if tb else "LR")
    back_sides(c, edges, "TB" if tb else "LR")
    core.route(c, edges, "TB" if tb else "LR")
    types = {f.get("type") or "sequence" for f in spec.get("flows") or []}
    leg = [{"label": "sequence flow", "edge": {"style": "solid"}}]
    if "message" in types:
        leg.append({"label": "message flow", "edge": {"style": "dashed"}})
    if spec.get("legend", True):
        core.legend(c, leg)
    body, geo = core.finish(c)
    return body, geo, [CSS]


def mermaid_swimlane(spec):
    pools = _pool_of(spec)
    nodes, own = [], {}
    for it in spec["nodes"]:
        k = it.get("kind") or "task"
        n = {"id": it["id"], "label": it.get("label") or "", "group": it["lane"], "tone": it.get("tone")}
        if k in ("start", "intermediate", "end"):
            own[it["id"]] = ({"start": "circle", "intermediate": "dbl-circ", "end": "fr-circ"}[k], True)
        elif k == "gateway":
            n["shape"] = "diamond"
            n["label"] = n["label"] or {"exclusive": "X", "parallel": "+", "inclusive": "O"}[it.get("gateway") or "exclusive"]
        elif k == "subprocess":
            own[it["id"]] = ("subproc", True)
        elif k == "data":
            n["shape"] = "document"
        nodes.append(n)
    plabel = {p.get("id"): p.get("label", p.get("id")) for p in spec.get("pools") or []}
    groups = {ln["id"]: " / ".join(x for x in (plabel.get(pools.get(ln["id"]), pools.get(ln["id"])), _lane_label(spec, ln)) if x)
              for ln in spec["lanes"]}
    edges = [dict(e, tail="none") for e in _sw_edges(spec)]  # Mermaid has no circle tail: one-way dashed arrow
    return mermaid_flow(spec, nodes, edges, "LR", groups, own)


def validate_swimlane(spec):
    lanes, items, flows = spec.get("lanes") or [], spec.get("nodes") or [], spec.get("flows") or []
    err = _no_style(spec, "swimlane")
    e1, lids = _ids(lanes, "lane")
    e2, ids = _ids(items, "node")
    err += e1 + e2
    if not lanes:
        err.append("lanes: at least one lane {id, label}")
    if lids & ids:
        err.append(f"lane and node ids clash: {', '.join(sorted(lids & ids))}")
    pools = _pool_of(spec)
    for it in items:
        k = it.get("kind") or "task"
        if k not in SW_KINDS:
            err.append(f"node {it.get('id')}: kind '{k}' is not one of {', '.join(SW_KINDS)}")
        if it.get("lane") not in lids:
            err.append(f"node {it.get('id')}: lane '{it.get('lane')}' unknown")
        if k in ("task", "subprocess", "data") and not it.get("label"):
            err.append(f"node {it.get('id')}: needs a label")
        if (it.get("trigger") or "none") not in TRIGGERS:
            err.append(f"node {it.get('id')}: trigger '{it['trigger']}' is not one of {', '.join(TRIGGERS)}")
        if it.get("trigger") == "terminate" and k != "end":
            err.append(f"node {it.get('id')}: terminate is an end-event trigger")
        if it.get("trigger") == "timer" and k == "end":
            err.append(f"node {it.get('id')}: an end event cannot wait for a timer: use an intermediate event")
        if (it.get("gateway") or "exclusive") not in GATEWAYS:
            err.append(f"node {it.get('id')}: gateway '{it['gateway']}' is not one of {', '.join(GATEWAYS)}")
    err += _edges_ok(flows, ids, "flow")
    if err:
        return err
    lane = {it["id"]: it["lane"] for it in items}
    kind = {it["id"]: it.get("kind") or "task" for it in items}
    seq = [f for f in flows if (f.get("type") or "sequence") != "message"]
    din, dout = _deg(seq)
    for f in flows:
        t = f.get("type") or "sequence"
        if t not in FLOW_TYPES:
            err.append(f"flow {f['from']} -> {f['to']}: type '{t}' is not one of {', '.join(FLOW_TYPES)}")
        same = pools[lane[f["from"]]] == pools[lane[f["to"]]]
        if t == "message" and same:
            err.append(f"flow {f['from']} -> {f['to']}: a message flow connects two pools; inside one pool use a sequence flow")
        if t != "message" and not same:
            err.append(f"flow {f['from']} -> {f['to']}: a sequence flow stays inside its pool; between pools use type 'message'")
        if t == "message" and kind[f["from"]] == "start":
            err.append(f"flow {f['from']} -> {f['to']}: a start event only catches: send the message from a task or "
                       "a message end event")
        if t == "message" and kind[f["to"]] == "end":
            err.append(f"flow {f['from']} -> {f['to']}: an end event only throws: let a task, a start or an "
                       "intermediate event receive the message")
        if t == "conditional" and kind[f["from"]] == "gateway":
            err.append(f"flow {f['from']} -> {f['to']}: flows out of a gateway carry no condition marker: use a label")
        if len(str(f.get("label", ""))) > 36:
            err.append(f"flow {f['from']} -> {f['to']}: label over 36 characters")
    for i, k in kind.items():
        if k == "start" and din.get(i):
            err.append(f"node {i}: no sequence flow enters a start event")
        if k == "end" and dout.get(i):
            err.append(f"node {i}: no sequence flow leaves an end event")
        if k == "gateway" and dout.get(i, 0) < 2 and din.get(i, 0) < 2:
            err.append(f"node {i}: a gateway splits (2+ out) or merges (2+ in)")
    if not any(k == "start" for k in kind.values()):
        err.append("swimlane: needs a start event")
    if not any(k == "end" for k in kind.values()):
        err.append("swimlane: needs an end event")
    return err


TYPES = {
    "flowchart": {"svg": svg_flowchart, "mermaid": mermaid_flowchart, "validate": validate_flowchart,
                  "doc": "steps, decisions, I/O, sub-process; style plain|airflow|dbt, groups, overview"},
    "swimlane": {"svg": svg_swimlane, "mermaid": mermaid_swimlane, "validate": validate_swimlane,
                 "doc": "cross-functional process, BPMN-lite: lanes, pools, events, tasks, gateways, message flows"},
    "decision-tree": {"svg": svg_tree, "mermaid": mermaid_tree, "validate": validate_tree,
                      "doc": "questions with answer-labelled branches down to outcomes"},
    "state-machine": {"svg": svg_state, "mermaid": mermaid_state, "validate": validate_state,
                      "doc": "UML states, event [guard] / action transitions, initial/final, choice, composite"},
    "activity": {"svg": svg_activity, "mermaid": mermaid_activity, "validate": validate_activity,
                 "doc": "UML activity: actions, decision/merge, fork/join bars, partitions, final and flow final"},
    "retry-flow": {"svg": svg_retry, "mermaid": mermaid_retry, "validate": validate_retry,
                   "doc": "bounded retries, timeouts, failure paths to DLQ / alert / compensation; style plain|airflow"},
    "approval-workflow": {"svg": svg_approval, "mermaid": mermaid_approval, "validate": validate_approval,
                          "doc": "submit, review, approve with roles, SLAs, approved/rejected/changes/escalate exits"},
}
