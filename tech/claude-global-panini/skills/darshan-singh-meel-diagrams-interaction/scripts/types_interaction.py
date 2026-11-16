"""Interaction and time diagram types for the darshan-singh-meel-diagrams engine: sequence, timeline, gantt,
journey, service-blueprint, raci, handoff. Loaded by the engine's registry; nothing runs at import."""
import datetime
import re

import diagram as core

M = core.MARGIN
SEQ_KINDS = ("sync", "async", "reply")
FRAMES = {"alt": "else", "opt": None, "loop": None, "par": "and", "break": None, "critical": "option"}
LETTERS = {"A": ("ink", "A accountable"), "R": ("blue", "R responsible"), "C": ("teal", "C consulted"),
           "I": ("soft", "I informed")}
STATUS = {"done": {"tone": "green", "label": "done"}, "active": {"tone": "teal", "label": "in progress"},
          "planned": {"tone": "plain", "dashed": True, "label": "planned"},
          "crit": {"tone": "red", "label": "critical path"}, "risk": {"tone": "amber", "label": "at risk"}}
FEEL = {5: "delighted", 4: "pleased", 3: "neutral", 2: "frustrated", 1: "angry"}
BP_LANES = (("evidence", "Physical evidence", "soft"), ("customer", "Customer actions", "blue"),
            ("frontstage", "Frontstage", "teal"), ("backstage", "Backstage", "plain"),
            ("support", "Support processes", "soft"))
BP_LINES = {1: "line of interaction", 2: "line of visibility", 3: "line of internal interaction"}
CSS = ("#S .ia-act{fill:var(--dg-card);stroke:var(--dg-ink);stroke-width:1.1}"
       "#S .ia-life{stroke:var(--dg-muted);stroke-width:1;stroke-dasharray:4 4;fill:none}"
       "#S .ia-frame{fill:none;stroke:var(--dg-muted);stroke-width:1.1}"
       "#S .ia-sep{fill:none;stroke:var(--dg-muted);stroke-width:1;stroke-dasharray:5 4}"
       "#S .ia-tab{fill:var(--dg-soft);stroke:var(--dg-muted);stroke-width:1.1}"
       "#S .ia-axis{stroke:var(--dg-ink);stroke-width:2;fill:none}"
       "#S .ia-emo{stroke:var(--dg-ink);stroke-width:1.8;fill:none}"
       "#S .ia-pt{stroke:var(--dg-card);stroke-width:2}#S .ia-pt.g{fill:var(--dg-green)}"
       "#S .ia-pt.a{fill:var(--dg-amber-ink)}#S .ia-pt.r{fill:var(--dg-red)}"
       "#S .ia-bpl{stroke:var(--dg-ink);stroke-width:1.4;stroke-dasharray:8 4;fill:none}"
       "#S .ia-ms{fill:var(--dg-ink);stroke:var(--dg-card);stroke-width:1.5}#S .ia-hide>.dg-sh{display:none}"
       "#S .ia-nbg{fill:var(--dg-soft)}#S .ia-mark{stroke:var(--dg-lav-ink);stroke-width:1.2;stroke-dasharray:3 3;fill:none}")


def _err(cond, msg, out):
    if cond:
        out.append(msg)


def _mm(s):
    """Text for Mermaid sequence/gantt/timeline/journey lines: no ':' ';' '#' that break those parsers."""
    return re.sub(r"[#;:]", lambda m: {"#": "#35;", ";": "#59;", ":": "∶"}[m.group()], str(s).replace("\n", " "))


def _look(style, item, spec, own=None):
    """Tone/dashed/solid/strong for a bar or step plus its legend entry: status (plain), kind (dbt), state (airflow)."""
    if style == "dbt":
        m, k = dict(core.DBT_KINDS, **(spec.get("kinds") or {})), item.get("kind")
    elif style == "airflow":
        m, k = dict(core.AIRFLOW_STATES, **(spec.get("states") or {})), item.get("state")
    else:
        m, k = dict(own or {}, **(spec.get("kinds") or {})), item.get("status") or item.get("kind")
    v = m.get(k)
    v = {"tone": v} if isinstance(v, str) else dict(v or {})
    look = {"tone": item.get("tone") or v.get("tone") or "plain", "dashed": v.get("dashed", False),
            "solid": style == "dbt", "strong": style == "airflow" and bool(k)}
    leg = None
    if k and v:
        leg = {"label": v.get("label", str(k).replace("_", " ")), "tone": look["tone"], "dashed": look["dashed"],
               "solid": look["solid"], "strong": look["strong"]}
    return look, leg


# ---------- sequence ----------
def _walk(steps, depth=0):
    for s in steps:
        yield s, depth
        if s.get("frame"):
            yield from _walk(s.get("steps") or [], depth + 1)
            for b in s.get("else") or []:
                yield from _walk(b.get("steps") or [], depth + 1)


def validate_sequence(spec):
    err = []
    ps = spec.get("participants") or []
    ids = [p.get("id") for p in ps]
    _err(len(ps) < 2, "participants: at least two {id, label}", err)
    _err(len(set(ids)) != len(ids), "participants: duplicate id", err)
    for p in ps:
        _err(not p.get("label"), f"participant {p.get('id')}: needs a label", err)
        _err((p.get("shape") or "box") not in core.SHAPES, f"participant {p.get('id')}: unknown shape", err)
    _err(not spec.get("steps"), "steps: at least one message", err)
    for s, _ in _walk(spec.get("steps") or []):
        if s.get("frame"):
            _err(s["frame"] not in FRAMES, f"frame '{s['frame']}': one of {', '.join(FRAMES)}", err)
            _err(not s.get("steps"), f"frame {s['frame']}: needs steps", err)
            _err(bool(s.get("else")) and not FRAMES.get(s["frame"]),
                 f"frame {s['frame']}: 'else' operands only for alt, par, critical", err)
        elif "note" in s:
            on = s.get("over") or s.get("right_of") or s.get("left_of")
            on = on if isinstance(on, list) else [on]
            _err(not on or any(o not in ids for o in on), f"note '{s['note'][:30]}': over / right_of / left_of a participant", err)
        else:
            for k in ("from", "to"):
                _err(s.get(k) not in ids, f"message {s.get('from')} -> {s.get('to')}: unknown participant '{s.get(k)}'", err)
            _err((s.get("kind") or "sync") not in SEQ_KINDS, f"message '{s.get('label')}': kind one of {', '.join(SEQ_KINDS)}", err)
            _err(len(str(s.get("label", ""))) > 36, f"message '{s.get('label')}': over 36 characters - move detail into a note", err)
    return err


def _mlabel(s, n):
    return (f"{n}. " if n else "") + str(s.get("label", ""))


def _seq_needs(spec, col, heads):
    """Minimum distance between neighbouring lifelines from heads, labels, self calls and notes."""
    n = len(col)
    gap = [(heads[i][0] + heads[i + 1][0]) / 2 + 24 for i in range(n - 1)] + [heads[-1][0] / 2 + 8]
    num = 0
    for s, _ in _walk(spec["steps"]):
        if s.get("frame") or "note" in s:
            if "note" in s and not s.get("frame"):
                w = core.size({"label": s["note"], "shape": "note"}, 220)[0]
                if s.get("right_of"):
                    i = col[s["right_of"]]
                    gap[i] = max(gap[i], w + 26)
                elif s.get("left_of") and col[s["left_of"]] > 0:
                    i = col[s["left_of"]] - 1
                    gap[i] = max(gap[i], w + 26)
            continue
        num += 1
        lw = core.text_width(_mlabel(s, num if spec.get("autonumber") else 0), 11, True) + 10
        a, b = sorted((col[s["from"]], col[s["to"]]))
        if a == b:
            gap[a] = max(gap[a], 44 + lw + 14)
        elif b - a == 1:
            gap[a] = max(gap[a], lw + 34)
        else:
            have = sum(gap[a:b])
            if have < lw + 34:
                gap[b - 1] += lw + 34 - have
    return gap


def svg_sequence(spec, core):
    c = core.canvas(spec)
    ps = spec["participants"]
    col = {p["id"]: i for i, p in enumerate(ps)}
    actor = {p["id"]: bool(p.get("actor")) or p.get("shape") == "actor" for p in ps}
    hn = [dict(p, shape=p.get("shape") or ("actor" if p.get("actor") else "box"), free=True) for p in ps]
    heads = [core.size(n, 150) for n in hn]
    hh = max(h for _, h in heads)
    depth = max([d + 1 for s, d in _walk(spec["steps"]) if s.get("frame")] + [0])
    gap = _seq_needs(spec, col, heads)
    x = M + max(heads[0][0] / 2, 14 + 10 * depth + 4)
    cx = []
    for i in range(len(ps)):
        cx.append(x)
        x += gap[i]
    right = x + max(0, 10 * depth)
    if right + M > core.MAX_W:
        raise core.LayoutError(f"canvas would be {int(right + M)}px wide (max {core.MAX_W}): fewer participants (<= 6), "
                               "shorter message labels, or split into two sequences")
    for i, n in enumerate(hn):
        core.node(c, n, cx[i] - heads[i][0] / 2, M + hh - heads[i][1], *heads[i])
    top = M + hh
    st = {"y": top + 18, "num": 0, "act": {p["id"]: [] for p in ps}, "bars": [], "frames": []}

    def edge_x(p, toward):
        lv = len(st["act"][p])
        if not lv:
            return cx[col[p]]
        off = 4 * (lv - 1)
        return cx[col[p]] + off + (5 if toward > cx[col[p]] + off else -5)

    def reset(snap, y):
        """Activation is per operand: back to the stacks of `snap`; bars opened since close at y, closed ones reopen at y."""
        for p, stack in st["act"].items():
            base, keep = snap[p], 0
            while keep < min(len(stack), len(base)) and stack[keep] == base[keep]:
                keep += 1
            while len(stack) > keep:
                st["bars"].append((p, len(stack), stack.pop(), y))
            stack.extend([y] * (len(base) - keep))

    def run(steps):
        """Draw steps from st['y']; return [xmin, xmax] of what was drawn."""
        ext = [1e9, -1e9]

        def grow(a, b):
            ext[0], ext[1] = min(ext[0], a), max(ext[1], b)

        for s in steps:
            if s.get("frame"):
                y0 = st["y"]
                op = s["frame"]
                tw = core.text_width(op, 11, True, True) + 18
                st["y"] += 30
                snap = {p: list(v) for p, v in st["act"].items()}
                inner = [run(s["steps"])]
                seps = []
                for b in s.get("else") or []:
                    st["y"] += 4
                    seps.append((st["y"], b.get("label", "")))
                    reset(snap, st["y"])
                    st["y"] += 24
                    inner.append(run(b.get("steps") or []))
                st["y"] += 8
                if op == "break":  # the rest of the enclosing fragment is skipped: back to the state before it
                    reset(snap, st["y"])
                lo = min(e[0] for e in inner) - 16
                hi = max(e[1] for e in inner) + 16
                guard = s.get("label", "")
                hi = max(hi, lo + tw + 12 + core.text_width(guard, 11, True) + 12,
                         *[lo + core.text_width(g, 11, True) + 24 for _, g in seps])
                st["frames"].append((op, guard, lo, y0, hi - lo, st["y"] - y0, tw, seps))
                grow(lo, hi)
                st["y"] += 10
            elif "note" in s:
                n = {"id": f"note{len(c['geo']['nodes'])}", "label": s["note"], "shape": "note", "free": True,
                     "tone": s.get("tone")}
                w, h = core.size(n, 220)
                if s.get("over"):
                    on = s["over"] if isinstance(s["over"], list) else [s["over"]]
                    xs = [cx[col[o]] for o in on]
                    w = max(w, max(xs) - min(xs) + 40)
                    x0 = (min(xs) + max(xs)) / 2 - w / 2
                elif s.get("right_of"):
                    x0 = cx[col[s["right_of"]]] + 12 + 4 * len(st["act"][s["right_of"]])
                else:
                    x0 = cx[col[s["left_of"]]] - 12 - w
                n["min_w"] = w
                core.node(c, n, x0, st["y"], w, h)
                grow(x0, x0 + w)
                st["y"] += h + 14
            else:
                st["num"] += 1
                kind = s.get("kind") or "sync"
                a, b = s["from"], s["to"]
                e = {"from": a, "to": b, "label": _mlabel(s, st["num"] if spec.get("autonumber") else 0),
                     "style": "dashed" if kind == "reply" else "solid", "head": "filled" if kind == "sync" else "open",
                     "tone": s.get("tone")}
                lw = core.text_width(e["label"], 11, True) + 10
                if a == b:
                    y = st["y"] + 20
                    x0 = edge_x(a, 1e9)
                    pts = [(x0, y), (x0 + 30, y), (x0 + 30, y + 16), (x0 + 2, y + 16)]
                    core.arrow(c, pts, e, (x0 + 38 + lw / 2, y + 8))
                    grow(cx[col[a]] - 6, x0 + 38 + lw)
                    st["y"] += 46
                else:
                    y = st["y"] + 22
                    act = s.get("activate", kind == "sync" and not actor[b])
                    if act:
                        st["act"][b].append(y)
                    xa, xb = edge_x(a, cx[col[b]]), edge_x(b, cx[col[a]])
                    core.arrow(c, [(xa, y), (xb, y)], e, ((xa + xb) / 2, y - 11))
                    grow(min(xa, xb), max(xa, xb))
                    if (kind == "reply" or s.get("deactivate")) and st["act"][a]:
                        lv = len(st["act"][a])
                        st["bars"].append((a, lv, st["act"][a].pop(), y))
                    st["y"] += 34
        return ext if ext[0] < 1e9 else [cx[0], cx[0]]

    run(spec["steps"])
    end = st["y"] + 8
    for p, stack in st["act"].items():
        while stack:
            st["bars"].append((p, len(stack), stack.pop(), end - 4))
    for i in range(len(ps)):
        core.line(c, [(cx[i], top), (cx[i], end)], "ia-life", 0)
    for p, lv, y0, y1 in st["bars"]:
        core.rect(c, cx[col[p]] - 5 + 4 * (lv - 1), y0, 10, max(8, y1 - y0), "ia-act", 0, 1)
    for k, (op, guard, x, y, w, h, tw, seps) in enumerate(st["frames"]):
        core.rect(c, x, y, w, h, "ia-frame", 2, 0)
        # tab and guards sit above lifelines and activation bars (z 1), on their own background
        core.add(c, f'<path class="ia-tab" d="M{core.F(x)},{core.F(y)} H{core.F(x + tw)} V{core.F(y + 13)} '
                    f'L{core.F(x + tw - 6)},{core.F(y + 20)} H{core.F(x)} Z"/>', 1)
        core.text(c, x + 6, y + 3, op, "dg-txm", mono=True, bold=True)
        for gx, gy, g in [(x + tw + 6, y + 3, guard)] + [(x + 6, sy + 4, g) for sy, g in seps]:
            if g:
                core.rect(c, gx, gy, core.text_width(g, 11, True) + 6, 16, "dg-bg", 2, 1)
                core.text(c, gx + 3, gy + 1, g, "dg-txm", mono=True)
        for sy, g in seps:
            core.line(c, [(x, sy), (x + w, sy)], "ia-sep", 0)
        mem = [n["id"] for n in c["geo"]["nodes"] if n["id"].startswith("note") and x <= n["x"] and n["x"] + n["w"] <= x + w
               and y <= n["y"] and n["y"] + n["h"] <= y + h]
        c["geo"]["containers"].append({"id": f"frame{k}", "x": x, "y": y, "w": w, "h": h, "kind": "group",
                                       "text": f"{op} {guard}".strip(), "members": mem, "header_w": 0})
    return core.finish(c, max(right, *[f[2] + f[4] for f in st["frames"]], *[n["x"] + n["w"] for n in c["geo"]["nodes"]]) + M,
                       end + M) + ([CSS],)


def mermaid_sequence(spec):
    out = core.mermaid_head(spec, "sequenceDiagram")
    if spec.get("autonumber"):
        out.append("  autonumber")
    for p in spec["participants"]:
        kw = "actor" if p.get("actor") or p.get("shape") == "actor" else "participant"
        out.append(f"  {kw} {core.mm_id(p['id'])} as {_mm(p['label'])}")
    act = {p["id"]: 0 for p in spec["participants"]}
    actors = {p["id"] for p in spec["participants"] if p.get("actor") or p.get("shape") == "actor"}
    arrows = {"sync": "->>", "async": "-)", "reply": "-->>"}

    def reset(snap, ind):
        """Mermaid counts activations in line order: explicit (de)activate lines give each operand the pre-frame state."""
        for p in act:
            while act[p] > snap[p]:
                out.append(f"{ind}deactivate {core.mm_id(p)}")
                act[p] -= 1
            while act[p] < snap[p]:
                out.append(f"{ind}activate {core.mm_id(p)}")
                act[p] += 1

    def emit(steps, ind):
        for s in steps:
            if s.get("frame"):
                out.append(f"{ind}{s['frame']} {_mm(s.get('label', ''))}".rstrip())
                snap = dict(act)
                emit(s["steps"], ind + "  ")
                for b in s.get("else") or []:
                    out.append(f"{ind}{FRAMES[s['frame']]} {_mm(b.get('label', ''))}".rstrip())
                    reset(snap, ind + "  ")
                    emit(b.get("steps") or [], ind + "  ")
                out.append(f"{ind}end")
                if s["frame"] == "break":
                    reset(snap, ind)
            elif "note" in s:
                if s.get("over"):
                    on = s["over"] if isinstance(s["over"], list) else [s["over"]]
                    where = "over " + ",".join(core.mm_id(o) for o in on)
                else:
                    where = ("right of " + core.mm_id(s["right_of"])) if s.get("right_of") else ("left of " + core.mm_id(s["left_of"]))
                out.append(f"{ind}Note {where}: {_mm(s['note'])}")
            else:
                kind = s.get("kind") or "sync"
                a, b = s["from"], s["to"]
                mark = ""
                if a != b and s.get("activate", kind == "sync" and b not in actors):
                    mark, act[b] = "+", act[b] + 1
                elif (kind == "reply" or s.get("deactivate")) and act[a] and a != b:
                    mark, act[a] = "-", act[a] - 1
                out.append(f"{ind}{core.mm_id(a)}{arrows[kind]}{mark}{core.mm_id(b)}: {_mm(s.get('label', ''))}")

    emit(spec["steps"], "  ")
    return "\n".join(out) + "\n"


# ---------- timeline ----------
def validate_timeline(spec):
    err = []
    ps = spec.get("periods") or []
    _err(not ps, "periods: at least one {label, events: [{label, sub?, tone?}]}", err)
    secs = {s.get("id") for s in spec.get("sections") or []}
    for p in ps:
        _err(not p.get("label"), "period without label", err)
        _err(not p.get("events"), f"period {p.get('label')}: needs events", err)
        _err(bool(p.get("section")) and p.get("section") not in secs, f"period {p.get('label')}: unknown section", err)
        for e in p.get("events") or []:
            e = e if isinstance(e, dict) else {"label": e}
            _err((e.get("tone") or "plain") not in core.TONES, f"event {e.get('label')}: unknown tone", err)
    _err(len(ps) > 14, "periods: at most 14 per diagram - split by era", err)
    return err


def _events(p):
    return [e if isinstance(e, dict) else {"label": e} for e in p["events"]]


def svg_timeline(spec, core):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    ps = spec["periods"]
    secs = {s["id"]: s for s in spec.get("sections") or []}
    n = len(ps)
    has_sec = any(p.get("section") for p in ps)
    gap = 16
    cw = min(180, (core.MAX_W - 2 * M - (n - 1) * gap - (16 if has_sec else 0) - 2) // n)
    lr = spec.get("direction", "LR" if cw >= 120 else "TB") == "LR"
    pills = [dict(id=f"p{i}", label=p["label"], shape="pill", tone="ink", solid=True, free=True) for i, p in enumerate(ps)]
    if lr:
        top = M + (28 if has_sec else 0)
        ph = max(core.size(p, cw)[1] for p in pills)
        boxes, col_h = [], []
        for i, p in enumerate(ps):
            y, lst = top + ph + 18, []
            for j, e in enumerate(_events(p)):
                nd = dict(id=f"e{i}_{j}", label=e["label"], sub=e.get("sub"), tone=e.get("tone"), free=True, max_w=cw)
                w, h = core.size(nd, cw, cw)
                lst.append((nd, y, cw, h))
                y += h + 10
            boxes.append(lst)
            col_h.append(y - 10)
        bottom = max(col_h)
        x = M + (8 if has_sec else 0)
        xs = []
        for i in range(n):
            xs.append(x)
            x += cw + gap
        _sections(c, ps, secs, [(xs[i] - 6, M, cw + 12, bottom - M + 10) for i in range(n)])
        core.line(c, [(xs[0], top + ph / 2), (xs[-1] + cw, top + ph / 2)], "ia-axis", 0)
        for i in range(n):
            pw = core.size(pills[i], cw)[0]
            core.node(c, pills[i], xs[i] + (cw - pw) / 2, top, pw, ph)
            for nd, y, w, h in boxes[i]:
                core.node(c, nd, xs[i], y, w, h)
        _fill_members(c)
    else:
        pw = max(core.size(p, 150)[0] for p in pills)
        x0 = M + (8 if has_sec else 0)
        ex = x0 + pw + 24
        ew = min(200, (core.MAX_W - M - ex) / max(len(_events(p)) for p in ps) - 10)
        y = M + (26 if has_sec else 0)
        rows = []
        for i, p in enumerate(ps):
            evs = [dict(id=f"e{i}_{j}", label=e["label"], sub=e.get("sub"), tone=e.get("tone"), free=True)
                   for j, e in enumerate(_events(p))]
            sz = [core.size(e, ew, ew) for e in evs]
            ph = core.size(pills[i], pw)[1]
            rh = max([h for _, h in sz] + [ph])
            rows.append((y, rh, evs, sz, ph))
            nxt = ps[i + 1].get("section") if i + 1 < n else None
            y += rh + (40 if nxt != p.get("section") else 14)
        lab = 26 if has_sec else 0
        right = ex + max(sum(w for w, _ in r[3]) + 10 * (len(r[3]) - 1) for r in rows) + 8
        _sections(c, ps, secs, [(x0 - 8, r[0] - lab, right - x0 + 8, r[1] + lab) for r in rows], tb=True)
        core.line(c, [(x0 + pw / 2, rows[0][0]), (x0 + pw / 2, rows[-1][0] + rows[-1][1])], "ia-axis", 0)
        for i, (y, rh, evs, sz, ph) in enumerate(rows):
            core.node(c, pills[i], x0, y + (rh - ph) / 2, pw, ph)
            xx = ex
            for e, (w, h) in zip(evs, sz):
                core.node(c, e, xx, y, w, h)
                xx += w + 10
        _fill_members(c)
    return core.finish(c) + ([CSS],)


def _sections(c, ps, secs, cells, tb=False):
    """Soft band behind the consecutive periods of each section, its label at the top-left."""
    i = 0
    while i < len(ps):
        sid = ps[i].get("section")
        j = i
        while j + 1 < len(ps) and ps[j + 1].get("section") == sid:
            j += 1
        if sid:
            x, y = cells[i][0], cells[i][1]
            if tb:
                w, h = cells[i][2], cells[j][1] + cells[j][3] - y + 10
            else:
                w, h = cells[j][0] + cells[j][2] - x, cells[i][3]
            core.container(c, sid, secs[sid].get("label", sid), x, y, w, h, kind="band")
            c.setdefault("_bands", []).append(len(c["geo"]["containers"]) - 1)  # members filled once nodes are drawn
        i = j + 1


def _fill_members(c):
    for k in c.get("_bands", []):
        g = c["geo"]["containers"][k]
        g["members"] = [n["id"] for n in c["geo"]["nodes"] if g["x"] <= n["x"] and n["x"] + n["w"] <= g["x"] + g["w"]
                        and g["y"] <= n["y"] and n["y"] + n["h"] <= g["y"] + g["h"]]


def mermaid_timeline(spec):
    out = core.mermaid_head(spec, "timeline")
    secs = {s["id"]: s.get("label", s["id"]) for s in spec.get("sections") or []}
    cur = None
    for p in spec["periods"]:
        if p.get("section") and p["section"] != cur:
            cur = p["section"]
            out.append(f"  section {_mm(secs[cur])}")
        out.append(f"    {_mm(p['label'])} : " + " : ".join(_mm(e["label"]) for e in _events(p)))
    return "\n".join(out) + "\n"


# ---------- gantt ----------
def _is_time(v):
    return bool(re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", str(v)))


def _num(v):
    """ISO date -> day number, HH:MM[:SS] -> minutes."""
    if _is_time(v):
        p = [int(x) for x in str(v).split(":")] + [0]
        return p[0] * 60 + p[1] + p[2] / 60
    return datetime.date.fromisoformat(str(v)).toordinal()


def _fmt(v, timed):
    if timed:
        v = round(v * 60)
        return f"{v // 3600:02d}:{v % 3600 // 60:02d}" + (f":{v % 60:02d}" if v % 60 else "")
    return datetime.date.fromordinal(int(v)).isoformat()


def _resolve(spec):
    """{task id: (start, end)} in days (dates; end exclusive) or minutes (times)."""
    timed = _is_time(spec["start"])
    T = {t["id"]: t for t in spec["tasks"]}
    out = {}

    def get(i, seen=()):
        if i in out:
            return out[i]
        if i in seen:
            raise core.LayoutError(f"task {i}: circular 'after'")
        t = T[i]
        if t.get("start"):
            s = _num(t["start"])
        else:
            s = max(get(a, seen + (i,))[1] for a in t["after"])
        if t.get("milestone"):
            e = s
        elif t.get("end"):
            e = _num(t["end"]) + (0 if timed else 1)
        elif t.get("days"):
            e = s + t["days"]
        else:
            e = s + t["minutes"]
        out[i] = (s, e)
        return out[i]

    for i in T:
        get(i)
    return out, timed


def validate_gantt(spec):
    err = []
    for k in ("start", "end"):
        v = spec.get(k)
        try:
            _num(v)
        except (TypeError, ValueError):
            err.append(f"{k}: an ISO date (2026-01-05) or a time (02:15 or 02:15:30)")
    ts = spec.get("tasks") or []
    _err(not ts, "tasks: at least one {id, label, start|after, end|days|minutes|milestone}", err)
    ids = [t.get("id") for t in ts]
    _err(len(set(ids)) != len(ids), "tasks: duplicate id", err)
    secs = {s.get("id") for s in spec.get("sections") or []}
    style = spec.get("style") or "plain"
    _err(style not in core.GRAPH_STYLES, f"style '{style}' is not one of {', '.join(core.GRAPH_STYLES)}", err)
    for t in ts:
        i = t.get("id")
        _err(not t.get("label"), f"task {i}: needs a label", err)
        _err(not t.get("start") and not t.get("after"), f"task {i}: needs start or after", err)
        _err(not (t.get("milestone") or t.get("end") or t.get("days") or t.get("minutes")),
             f"task {i}: needs end, days, minutes or milestone: true", err)
        for a in t.get("after") or []:
            _err(a not in ids, f"task {i}: after '{a}' is not a task id", err)
        _err(bool(t.get("section")) and t.get("section") not in secs, f"task {i}: section '{t.get('section')}' unknown", err)
        _err(bool(t.get("status")) and t.get("status") not in STATUS, f"task {i}: status one of {', '.join(STATUS)}", err)
        _err(style == "airflow" and bool(t.get("state")) and t.get("state") not in core.AIRFLOW_STATES and
             t.get("state") not in (spec.get("states") or {}), f"task {i}: state '{t.get('state')}' is not an Airflow state", err)
    if not err:  # 'after' is finish-to-start: an explicit start may not come before a dependency ends
        try:
            se, timed = _resolve(spec)
        except core.LayoutError as ex:
            return [str(ex)]
        for t in ts:
            for a in t.get("after") or []:
                if t.get("start") and se[t["id"]][0] < se[a][1]:
                    end = se[a][1] - (0 if timed else 1)
                    err.append(f"task {t['id']}: start {_fmt(se[t['id']][0], timed)} is before '{a}' ends ({_fmt(end, timed)})")
    return err


def _ticks(lo, hi, timed):
    span = hi - lo
    out = []
    if timed:
        step = next(s for s in (1, 2, 5, 10, 15, 30, 60, 120, 240) if span / s <= 10)
        v = -(-lo // step) * step
        while v <= hi:
            out.append((v, _fmt(v, True)[:5]))
            v += step
        return out
    d0, d1 = datetime.date.fromordinal(int(lo)), datetime.date.fromordinal(int(hi))
    if span <= 70:
        d = d0 + datetime.timedelta(days=(7 - d0.weekday()) % 7)
        while d <= d1:
            out.append((d.toordinal(), d.strftime("%d %b")))
            d += datetime.timedelta(days=7)
        return out
    step = 1 if span <= 400 else 3 if span <= 1100 else 12
    y, m = d0.year, d0.month
    while datetime.date(y, m, 1) <= d1:
        d = datetime.date(y, m, 1)
        if d >= d0 and (m - 1) % step == 0:
            out.append((d.toordinal(), d.strftime("%b %Y" if m == 1 or not out else "%b") if step == 1 else f"Q{(m - 1) // 3 + 1} {y}" if step == 3 else str(y)))
        m += 1
        y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return out


def svg_gantt(spec, core):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    style = spec.get("style") or "plain"
    se, timed = _resolve(spec)
    lo, hi = _num(spec["start"]), _num(spec["end"]) + (0 if _is_time(spec["end"]) else 1)
    for t in spec["tasks"]:
        s, e = se[t["id"]]
        if s < lo or e > hi:
            raise core.LayoutError(f"task {t['id']} runs {_fmt(s, timed)} to {_fmt(e, timed)}, outside start/end: widen them")
    secs = spec.get("sections") or []
    order = []  # rows: ("sec", section) | ("task", task)
    for sdef in secs + [{"id": None}]:
        mem = [t for t in spec["tasks"] if t.get("section") == sdef["id"]]
        if mem and sdef["id"]:
            order.append(("sec", sdef))
        order += [("task", t) for t in mem]
    mono = style in ("dbt", "airflow")
    arrows = spec.get("arrows", True)
    sources = {a for t in spec["tasks"] for a in t.get("after") or []} if arrows else set()
    ind = 12 if secs else 0
    wide = max(spec["tasks"], key=lambda t: core.text_width(t["label"], 12.5 if mono else 12, mono, mono))
    lab_w = core.text_width(wide["label"], 12.5 if mono else 12, mono, mono) + ind + 8
    lab_w = max(lab_w, *[core.text_width(s.get("label", ""), 12, bold=True) + 8 for s in secs] or [0])
    if lab_w > 260:
        raise core.LayoutError(f"label column would be {int(lab_w)}px (max 260): shorten the longest task or section "
                               f"label (e.g. '{wide['label'][:40]}')")
    notes, looks, legend = {}, {}, []
    for t in spec["tasks"]:
        look, leg = _look(style, t, spec, STATUS)
        looks[t["id"]] = look
        if leg:
            legend.append(leg)
        s, e = se[t["id"]]
        nt = t.get("note")
        if nt is None and style == "airflow" and t.get("state"):
            nt = t["state"].replace("_", " ") + (f" · {_dur(e - s)}" if timed and e > s else "")
        elif nt is None and style == "dbt" and timed and e > s:
            nt = _dur(e - s)
        notes[t["id"]] = nt
    x0 = M + lab_w + 14
    x1 = core.MAX_W - M - int(spec.get("right_pad", 8))
    k = (x1 - x0) / (hi - lo)
    X = lambda v: x0 + (v - lo) * k  # noqa: E731
    ticks = _ticks(lo, hi, timed)
    marks = [(_num(m["date"]), m["label"]) for m in spec.get("markers") or []]
    if spec.get("today"):
        marks.append((_num(spec["today"]), "today"))
    # marker labels: rows above the tick labels, bumped when they would touch
    mrows, placed = [], []
    for v, lb in sorted(marks):
        w = core.text_width(lb, 11, True)
        xl = min(max(X(v) - w / 2, x0), x1 - w)
        r = 0
        while any(rr == r and not (xl > a + aw + 8 or xl + w + 8 < a) for rr, a, aw in placed):
            r += 1
        placed.append((r, xl, w))
        mrows.append((v, lb, xl, r))
    nmr = max([r + 1 for *_, r in mrows] + [0])
    ty = M + nmr * 16
    for v, lb in ticks:
        core.text(c, X(v), ty, lb, "dg-txm", "middle", mono=True)
    y = ty + 22
    row_h, bar_h = 34, 18
    bars, band_rows = {}, []
    for kind, it in order:
        if kind == "sec":
            y += 8 if band_rows else 0
            band_rows.append([it, y, y])
            core.text(c, M, y + 7, it.get("label", it["id"]), "dg-txb", size=12, bold=True)
            y += 26
            continue
        t = it
        core.text(c, M + ind, y + (row_h - 16) / 2, t["label"], "dg-txm" if mono else "dg-tx", size=12.5 if mono else 12, mono=mono,
                  bold=False)
        s, e = se[t["id"]]
        cy = y + row_h / 2
        if t.get("milestone"):
            n = {"id": t["id"], "label": "", "shape": "box", "cls": "ia-hide", "free": True}
            core.node(c, n, X(s) - 8, cy - 8, 16, 16)
            core.add(c, f'<polygon class="ia-ms" points="{core.F(X(s))},{core.F(cy - 9)} {core.F(X(s) + 9)},{core.F(cy)} '
                        f'{core.F(X(s))},{core.F(cy + 9)} {core.F(X(s) - 9)},{core.F(cy)}"/>', 2)
            bars[t["id"]] = (X(s) - 8, cy - 8, 16, 16)
        else:
            if t.get("queued") and timed:
                q = _num(t["queued"])
                if X(s) - X(q) >= 10:
                    core.node(c, {"id": t["id"] + "__q", "label": "", "shape": "box", "tone": "soft", "dashed": True,
                                  "free": True}, X(q), cy - bar_h / 2 + 3, X(s) - X(q), bar_h - 6, clear=4)
                    legend.append({"label": "queued", "tone": "soft", "dashed": True})
            lk = looks[t["id"]]
            n = {"id": t["id"], "label": "", "shape": "box", "tone": lk["tone"], "dashed": lk["dashed"],
                 "solid": lk["solid"], "strong": lk["strong"] or t.get("strong"), "free": True, "tip": t["label"]}
            w = max(3, X(e) - X(s))
            core.node(c, n, X(s), cy - bar_h / 2, w, bar_h, clear=4)
            bars[t["id"]] = (X(s), cy - bar_h / 2, w, bar_h)
        if notes[t["id"]]:
            r = bars[t["id"]]
            left = c["rects"].get(t["id"] + "__q", r)[0]
            nw = core.text_width(notes[t["id"]], 11)
            # arrows leave a bar's right end and enter its left end: keep a channel free there
            gr, gl = (26 if t["id"] in sources else 6), (26 if t.get("after") and arrows else 6)
            cands = [r[0] + r[2] + gr, left - gl - nw]
            if t["id"] in sources:
                cands.reverse()
            ok = [x for x in cands if x0 <= x and x + nw <= core.MAX_W - M - 2]
            clear = [x for x in ok if not any(x - 3 <= X(v) <= x + nw + 3 for v, _ in marks)]
            nx = (clear or ok or cands)[0]
            if not clear:  # a marker line runs under the note: give it a background
                core.rect(c, nx - 2, cy - 8, nw + 4, 16, "ia-nbg" if secs else "dg-bg", 2, 2)
            core.text(c, nx, cy - 7, notes[t["id"]], "dg-tx")
            core.obstacle(c, nx, cy - 7, nw, 14, 3)
        if band_rows:
            band_rows[-1][2] = y + row_h
        y += row_h
    bottom = y + 4
    for v, _ in ticks:
        core.line(c, [(X(v), ty + 18), (X(v), bottom)], "dg-ax", 0)
    for v, lb, xl, r in mrows:
        core.text(c, xl, M + r * 16, lb, "dg-txm", mono=True)
        core.line(c, [(X(v), ty + 17), (X(v), bottom)], "dg-today" if lb == "today" else "ia-mark", 1)
    for sdef, a, b in band_rows:
        core.container(c, "sec_" + str(sdef["id"]), "", M - 6, a - 2, x1 - M + 12, b - a + 4, kind="band")
        c.setdefault("_bands", []).append(len(c["geo"]["containers"]) - 1)
    _fill_members(c)
    core.obstacle(c, M, ty + 18, lab_w, bottom - ty - 18, 2)
    edges = []
    for t in spec["tasks"]:
        for a in t.get("after") or []:
            tgt = t["id"] + "__q" if t["id"] + "__q" in c["rects"] else t["id"]
            edges.append({"from": a, "to": tgt, "style": "solid", "tone": "muted", "from_side": "right",
                          "to_side": "top" if t.get("milestone") else "left"})
    if edges and spec.get("arrows", True):
        core.route(c, edges, "LR")
    seen = set()
    core.legend(c, [x for x in legend if x["label"] not in seen and not seen.add(x["label"])] if spec.get("legend", True) else [])
    return core.finish(c, core.MAX_W - M + M if x1 + 8 + M >= core.MAX_W else None) + ([CSS],)


def _hms(minutes):
    v = round(minutes * 60)
    return f"{v // 3600:02d}:{v % 3600 // 60:02d}:{v % 60:02d}"


def _dur(minutes):
    s = round(minutes * 60)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m" + (f" {s % 60}s" if s % 60 else "")
    return f"{s // 3600}h" + (f" {s % 3600 // 60}m" if s % 3600 // 60 else "")


def mermaid_gantt(spec):
    se, timed = _resolve(spec)
    out = core.mermaid_head(spec, "gantt")
    out += ["  dateFormat " + ("HH:mm:ss" if timed else "YYYY-MM-DD"), "  axisFormat " + ("%H:%M" if timed else "%d %b")]
    if spec.get("today"):
        out.append(f"  %% today line at {spec['today']} (Mermaid draws today's real date)")
    for m in spec.get("markers") or []:
        at, length = (_hms(_num(m["date"])), "1s") if timed else (m["date"], "1d")
        out.append(f"  {_mm(m['label'])} : vert, {core.mm_id('v_' + m['label'])}, {at}, {length}")
    ids = {t["id"]: core.mm_id(t["id"]) for t in spec["tasks"]}
    secs = spec.get("sections") or []
    groups = [(s.get("label", s["id"]), [t for t in spec["tasks"] if t.get("section") == s["id"]]) for s in secs]
    groups.append(("Other", [t for t in spec["tasks"] if not t.get("section")]))
    if spec.get("style") == "airflow" and any(t.get("queued") for t in spec["tasks"]):
        out.append("  %% queued time is in the SVG only")
    for name, ts in groups:
        if not ts:
            continue
        out.append(f"  section {_mm(name)}")
        for t in ts:
            s, e = se[t["id"]]
            tags = [x for x in ("done", "active", "crit") if t.get("status") == x]
            if spec.get("style") == "airflow":
                tags = [{"success": "done", "running": "active", "failed": "crit"}[t["state"]]] \
                    if t.get("state") in ("success", "running", "failed") else []
            if t.get("milestone"):
                tags.append("milestone")
            # Mermaid has one start: 'after' when the task starts as its dependencies end, else the time and a comment
            deps = t.get("after") or []
            if deps and s > max(se[a][1] for a in deps):
                out.append(f"    %% {t['id']} starts after {', '.join(deps)} end, later than the latest of them")
            start = "after " + " ".join(ids[a] for a in deps) if deps and s == max(se[a][1] for a in deps) \
                else (_hms(s) if timed else _fmt(s, False))
            length = "0d" if t.get("milestone") else (f"{round((e - s) * 60)}s" if timed else f"{int(e - s)}d")
            out.append(f"    {_mm(t['label'])} :" + ", ".join(tags + [ids[t['id']], start, length]))
    return "\n".join(out) + "\n"


# ---------- journey ----------
J_ROWS = (("actions", "Actions", "plain"), ("touchpoints", "Touchpoints", "teal"), ("thoughts", "Thinks", "amber"),
          ("score", "Emotion", None), ("pains", "Pain points", "red"), ("opportunities", "Opportunities", "green"))


def validate_journey(spec):
    err = []
    st = spec.get("stages") or []
    _err(not 2 <= len(st) <= 6, "stages: 2 to 6 {id, label, actions, touchpoints?, score?, pains?, ...} - split longer journeys", err)
    for s in st:
        _err(not s.get("label"), f"stage {s.get('id')}: needs a label", err)
        _err(not s.get("actions"), f"stage {s.get('id')}: needs actions", err)
        sc = s.get("score")
        _err(sc is not None and sc not in (1, 2, 3, 4, 5), f"stage {s.get('id')}: score is 1 (angry) to 5 (delighted)", err)
    scores = [s.get("score") is not None for s in st]
    _err(any(scores) and not all(scores), "score: give every stage a score or none", err)
    return err


def svg_journey(spec, core):
    c = core.canvas(spec)
    st = spec["stages"]
    n = len(st)
    hw, gap = 118, 26
    x0 = M + hw + 14
    cw = min(200, (core.MAX_W - M - x0 - 8 - gap * (n - 1)) / n)
    xs = [x0 + i * (cw + gap) for i in range(n)]
    W = xs[-1] + cw + 8 - M
    heads = [dict(id=f"s_{s['id']}", label=s["label"], sub=s.get("sub"), shape="box", tone="ink", solid=True) for s in st]
    hh = max(core.size(h, cw, cw)[1] for h in heads)
    if spec.get("persona"):
        core.text(c, M, M + (hh - 14) / 2, spec["persona"][:20], "dg-txb", size=12, bold=True)
        if core.text_width(spec["persona"][:20], 12, bold=True) > hw:
            raise core.LayoutError("persona: at most ~16 characters (it sits left of the stage headers)")
    for i, h in enumerate(heads):
        core.node(c, h, xs[i], M, cw, hh)
    core.route(c, [{"from": heads[i]["id"], "to": heads[i + 1]["id"]} for i in range(n - 1)], "LR")
    y = M + hh + 12
    for key, title, tone in J_ROWS:
        if key == "score":
            if st[0].get("score") is None:
                continue
            lh, pad = 112, 24
            core.container(c, "row_score", title, M, y, W, lh, kind="lane", header_w=hw)
            pts = []
            for i, s in enumerate(st):
                py = y + pad + (5 - s["score"]) / 4 * (lh - 2 * pad)
                pts.append((xs[i] + cw / 2, py))
            core.line(c, pts, "ia-emo", 1)
            for i, (px, py) in enumerate(pts):
                sc = st[i]["score"]
                k = "g" if sc >= 4 else "a" if sc == 3 else "r"
                core.add(c, f'<circle class="ia-pt {k}" cx="{core.F(px)}" cy="{core.F(py)}" r="6"/>', 2)
                lb = f"{sc} {st[i].get('feeling') or FEEL[sc]}"
                lw = core.text_width(lb, 11)
                segs = list(zip(pts, pts[1:]))
                for yy in (py - 24, py + 10):
                    r = (px - lw / 2 - 2, yy, lw + 4, 14)
                    if not any(core.checker.seg_hits_rect(p, q, r) for p, q in segs) and y + 2 < yy and yy + 14 < y + lh - 2:
                        break
                core.text(c, px, yy, lb, "dg-tx", "middle")
            y += lh
            continue
        if not any(s.get(key) for s in st):
            continue
        cells, lh = [], 0
        for i, s in enumerate(st):
            vals = s.get(key) or []
            vals = [vals] if isinstance(vals, str) else vals
            items, hsum = [], 0
            for j, v in enumerate(vals):
                nd = dict(id=f"{key}_{s['id']}_{j}", label=v, tone=tone, free=True, shape="note" if key == "thoughts" else "box",
                          dashed=key == "opportunities")
                w, h = core.size(nd, cw, cw)
                items.append((nd, h))
                hsum += h + 8
            cells.append(items)
            lh = max(lh, hsum - 8)
        lh += 24
        core.container(c, f"row_{key}", title, M, y, W, lh, members=[nd["id"] for it in cells for nd, _ in it],
                       kind="lane", header_w=hw)
        for i, items in enumerate(cells):
            yy = y + 12
            for nd, h in items:
                core.node(c, nd, xs[i], yy, cw, h)
                yy += h + 8
        y += lh
    return core.finish(c) + ([CSS],)


def mermaid_journey(spec):
    out = core.mermaid_head(spec, "journey")
    who = _mm(spec.get("persona") or "User")
    for s in spec["stages"]:
        out.append(f"  section {_mm(s['label'])}")
        for a in s.get("actions") or []:
            out.append(f"    {_mm(a)}: {s.get('score', 3)}: {who}")
    out.append("  %% touchpoints, pain points and opportunities are in the SVG only")
    return "\n".join(out) + "\n"


# ---------- service blueprint ----------
def validate_blueprint(spec):
    err = []
    lanes = {k for k, _, _ in BP_LANES}
    its = spec.get("items") or []
    _err(not its, "items: at least one {id, lane, col, label}", err)
    ids = [i.get("id") for i in its]
    _err(len(set(ids)) != len(ids), "items: duplicate id", err)
    for i in its:
        _err(i.get("lane") not in lanes, f"item {i.get('id')}: lane one of {', '.join(sorted(lanes))}", err)
        _err(not isinstance(i.get("col"), int), f"item {i.get('id')}: col = step number 0, 1, 2 ...", err)
        _err(not i.get("label"), f"item {i.get('id')}: needs a label", err)
    _err(not any(i.get("lane") == "customer" for i in its), "a blueprint needs customer actions", err)
    return err + core.check_graph({"nodes": its, "edges": spec.get("edges") or []}, "nodes", "edges")


def svg_blueprint(spec, core):
    c = core.canvas(spec)
    hw = 148
    tone = {k: t for k, _, t in BP_LANES}
    nodes = []
    for i in spec["items"]:
        n = dict(i, tone=i.get("tone") or ("red" if i.get("fail") else tone[i["lane"]]),
                 shape=i.get("shape") or ("document" if i["lane"] == "evidence" else "rounded"),
                 strong=i.get("fail", False), free=i["lane"] in ("evidence", "customer"))
        if i.get("fail"):
            n["tag"] = "fail point"
        nodes.append(n)
    sized = [(n, *core.size(n, spec.get("max_w", 170))) for n in nodes]
    lanes = [{"id": k, "label": lb} for k, lb, _ in BP_LANES]
    edges = spec.get("edges") or []
    lay = core.layout_lanes(lanes, [{"id": n["id"], "w": w, "h": h, "lane": n["lane"], "col": n["col"]} for n, w, h in sized],
                            edges, header_w=hw, gap=40, row_gap=18)
    if lay["width"] > core.MAX_W:
        mw = spec.get("max_w", 170)
        raise core.LayoutError(f"blueprint would be {int(lay['width'])}px wide (max {core.MAX_W}): "
                               + (f"max_w {max(110, mw - 20)}, " if mw > 110 else "")
                               + "shorter labels, <= 4 steps, or split by journey stage")
    for lid, lb, _ in BP_LANES:
        core.container(c, lid, lb, *lay["lanes"][lid], members=[n["id"] for n in nodes if n["lane"] == lid],
                       kind="lane", header_w=hw)
    for k, name in BP_LINES.items():  # the line's name sits in the header of the lane above it
        x, y, w, h = lay["lanes"][BP_LANES[k][0]]
        core.line(c, [(x, y + h), (x + w, y + h)], "ia-bpl", 1)
        core.text(c, x + 8, y + h - 17, name, "dg-tx")
    for n, w, h in sized:
        core.node(c, n, *lay["pos"][n["id"]])
    core.route(c, [_bp_sides(e, spec["items"]) for e in edges], "TB")
    leg = [{"label": "fail point", "tone": "red", "strong": True}] if any(i.get("fail") for i in spec["items"]) else []
    core.legend(c, leg)
    return core.finish(c) + ([CSS],)


def _bp_sides(e, items):
    """Leave sideways and enter from above or below, so no arrow runs along a blueprint line between lanes."""
    it = {i["id"]: i for i in items}
    a, b = it[e["from"]], it[e["to"]]
    order = [k for k, _, _ in BP_LANES]
    da, db = order.index(a["lane"]), order.index(b["lane"])
    e = dict(e)
    if da == db or a["col"] == b["col"]:
        return e
    e.setdefault("from_side", "right" if b["col"] > a["col"] else "left")
    e.setdefault("to_side", "top" if db > da else "bottom")
    return e


# ---------- RACI ----------
def _letters(v):
    return [x for x in re.split(r"[/, ]+", str(v or "").upper()) if x]


def validate_raci(spec):
    err = []
    roles, tasks = spec.get("roles") or [], spec.get("tasks") or []
    _err(not roles or not tasks, "raci: needs roles [..] and tasks [{label, cells}]", err)
    _err(len(roles) > 8, "roles: at most 8 columns - split by area", err)
    for t in tasks:
        cells = t.get("cells") or []
        lb = t.get("label")
        if len(cells) != len(roles):
            err.append(f"task '{lb}': {len(cells)} cells for {len(roles)} roles")
            continue
        ls = [_letters(x) for x in cells]
        bad = {x for l in ls for x in l if x not in LETTERS}
        _err(bool(bad), f"task '{lb}': letters R, A, C, I only (got {', '.join(sorted(bad))})", err)
        _err(sum("A" in l for l in ls) != 1, f"task '{lb}': exactly one A (accountable) per task", err)
        _err(not any("R" in l for l in ls), f"task '{lb}': at least one R (responsible)", err)
    return err


def svg_raci(spec, core):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    roles, tasks = spec["roles"], spec["tasks"]
    cw = max(84, min(130, (core.MAX_W - 2 * M - 230) / len(roles) - 4))
    m = core.layout_matrix([t["label"] for t in tasks], roles, cell_w=cw, cell_h=34,
                           head_w=min(240, max(core.text_width(t["label"], 12, bold=True) for t in tasks) + 24))
    if m["width"] > core.MAX_W:
        raise core.LayoutError(f"matrix would be {int(m['width'])}px wide (max {core.MAX_W}): fewer roles or shorter task names")
    for j, s in enumerate(roles):
        x, y, w, h = m["cols"][j]
        core.rect(c, x, y, w, h, "dg-hd", 4)
        ls = core.wrap(s, w - 12, 11, True)
        for k, t in enumerate(ls):
            core.text(c, x + w / 2, y + (h - len(ls) * 15) / 2 + k * 15, t, "dg-txm", "middle", mono=True)
    used = set()
    for i, t in enumerate(tasks):
        x, y, w, h = m["rows"][i]
        core.rect(c, x, y, w, h, "dg-hd", 4)
        if core.text_width(t["label"], 12, bold=True) > w - 16:
            raise core.LayoutError(f"task '{t['label']}': too long for one row - shorten it")
        core.text(c, x + 10, y + (h - 16) / 2, t["label"], "dg-txb", size=12, bold=True)
        for j, v in enumerate(t["cells"]):
            ls = _letters(v)
            if not ls:
                core.rect(c, *m["cells"][(i, j)], "dg-ax", 3)
                continue
            top = next(k for k in "ARCI" if k in ls)
            used |= set(ls)
            core.node(c, {"id": f"c{i}_{j}", "label": "/".join(ls), "shape": "box", "tone": LETTERS[top][0],
                          "free": True}, *m["cells"][(i, j)])
    core.legend(c, [{"label": LETTERS[k][1], "tone": LETTERS[k][0]} for k in "ARCI" if k in used])
    return core.finish(c)


# ---------- handoff timeline ----------
HANDOFF = {"handoff": {"style": "solid", "tone": "amber", "label": "handoff to another team"}}


def _handoff_parts(spec):
    lane_of = {s["id"]: s["lane"] for s in spec["steps"]}
    edges = [dict(e, kind=e.get("kind") or ("handoff" if lane_of[e["from"]] != lane_of[e["to"]] else None))
             for e in spec.get("handoffs") or []]
    for e in edges:  # a handoff gets its own port, so it never merges with an in-lane arrow into the same step
        if e["kind"] == "handoff":
            e.setdefault("own_port", True)
    sp = dict(spec, edge_kinds=dict(HANDOFF, **(spec.get("edge_kinds") or {})), view="detail", collapse=[])
    nodes = [dict(s, group=s["lane"]) for s in spec["steps"]]
    groups = [{"id": l["id"], "label": l["label"]} for l in spec["lanes"]]
    return sp, nodes, edges, groups


def validate_handoff(spec):
    err = []
    lanes = [l.get("id") for l in spec.get("lanes") or []]
    _err(len(lanes) < 2, "lanes: at least two {id, label} (teams, roles or systems)", err)
    _err(spec.get("view") == "overview" or bool(spec.get("collapse")),
         "handoff: view overview / collapse not supported - lanes are the grouping; draw one lane per team instead", err)
    for s in spec.get("steps") or []:
        _err(s.get("lane") not in lanes, f"step {s.get('id')}: lane '{s.get('lane')}' unknown", err)
        _err(not isinstance(s.get("col"), int), f"step {s.get('id')}: col = time slot 0, 1, 2 ...", err)
    cols = spec.get("columns")
    if cols:
        _err(max([s.get("col", 0) for s in spec.get("steps") or []] + [0]) >= len(cols),
             "columns: one heading per time slot used by the steps", err)
    sp = dict(spec, nodes=spec.get("steps") or [], edges=spec.get("handoffs") or [], groups=[])
    sp.pop("collapse", None)
    sp.pop("view", None)
    return err + core.check_graph(sp) + core.check_style(sp)


def svg_handoff(spec, core):
    c = core.canvas(spec)
    sp, nodes, edges, groups = _handoff_parts(spec)
    st = core.style_graph(sp, nodes, edges, groups)
    sized = [(n, *core.size(n, spec.get("max_w", 130))) for n in st["nodes"]]
    hw = 110
    lay = core.layout_lanes(spec["lanes"], [{"id": n["id"], "w": w, "h": h, "lane": n["lane"], "col": n["col"]}
                                            for n, w, h in sized], st["edges"], header_w=hw, gap=44, row_gap=18)
    if lay["width"] > core.MAX_W:
        raise core.LayoutError(f"canvas would be {int(lay['width'])}px wide (max {core.MAX_W}): fewer time slots, "
                               "shorter step labels or wait labels, or split the timeline")
    top = 26 if spec.get("columns") else 0
    sh = lambda r: (r[0], r[1] + top, r[2], r[3])  # noqa: E731
    if spec.get("columns"):
        cwid = {}
        for n, w, h in sized:
            cwid[n["col"]] = max(cwid.get(n["col"], 0), w)
        for j, lb in enumerate(spec["columns"]):
            if j < len(lay["cols"]):
                core.text(c, lay["cols"][j] + cwid.get(j, 0) / 2, M, lb, "dg-txm", "middle", mono=True)
    for l in spec["lanes"]:
        core.container(c, l["id"], l["label"], *sh(lay["lanes"][l["id"]]),
                       members=[n["id"] for n in st["nodes"] if n["lane"] == l["id"]], kind="lane", header_w=hw)
    for n, w, h in sized:
        core.node(c, n, *sh(lay["pos"][n["id"]]))
    core.route(c, st["edges"], "LR")
    core.legend(c, st["legend"])
    return core.finish(c)


def mermaid_handoff(spec):
    sp, nodes, edges, groups = _handoff_parts(spec)
    return core.mermaid_graph(sp, nodes, edges, groups)


TYPES = {
    "sequence": {"svg": svg_sequence, "mermaid": mermaid_sequence, "validate": validate_sequence,
                 "doc": "UML sequence: lifelines, sync/async/reply, activation, alt/opt/loop/par/break/critical, notes"},
    "timeline": {"svg": svg_timeline, "mermaid": mermaid_timeline, "validate": validate_timeline,
                 "doc": "periods in order on an axis, events per period, optional sections (LR, or TB when long)"},
    "gantt": {"svg": svg_gantt, "mermaid": mermaid_gantt, "validate": validate_gantt,
              "doc": "Gantt / roadmap / run timing: sections, bars, milestones, dependencies, markers, today; style plain|dbt|airflow"},
    "journey": {"svg": svg_journey, "mermaid": mermaid_journey, "validate": validate_journey,
                "doc": "user / customer journey: stages x actions, touchpoints, thoughts, emotion line, pains, opportunities"},
    "service-blueprint": {"svg": svg_blueprint, "mermaid": lambda spec: None, "validate": validate_blueprint,
                          "doc": "service blueprint: evidence, customer, frontstage, backstage, support lanes with the three lines"},
    "raci": {"svg": svg_raci, "mermaid": lambda spec: None, "validate": validate_raci,
             "doc": "RACI matrix: tasks x roles, one A per task, at least one R"},
    "handoff": {"svg": svg_handoff, "mermaid": mermaid_handoff, "validate": validate_handoff,
                "doc": "swimlane handoff timeline: team lanes x time slots, handoff arrows with waits; style plain|dbt|airflow"},
}
