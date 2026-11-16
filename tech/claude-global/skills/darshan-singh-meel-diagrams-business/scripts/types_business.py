"""Business diagram types for the darshan-singh-meel-diagrams engine (registered through TYPES).
org-chart, team-topology, capability-map, value-stream, value-chain, sipoc, quadrant, stakeholder-map, swot, funnel,
mind-map, fishbone, business-model-canvas, kpi-tree, decision-matrix. Spec fields: references/types.md."""
import diagram as core

PX, PY, M = 12, 10, core.MARGIN
BG = {"plain": "card", "soft": "soft", "teal": "teal", "amber": "amber", "lav": "lav", "green": "green-bg",
      "red": "red-bg", "blue": "blue-bg", "ink": "soft"}
INK = {"plain": "ink", "soft": "muted", "teal": "teal-ink", "amber": "amber-ink", "lav": "lav-ink", "green": "green",
       "red": "red", "blue": "blue", "ink": "ink"}
CSS = ("#S .bz-i{font-size:12px;fill:var(--dg-ink)}#S .bz-b{font-size:12px;fill:var(--dg-muted)}"
       "#S .bz-op{fill:var(--dg-card);stroke:var(--dg-edge);stroke-width:1.2}"
       "#S .bz-opt{font-size:12px;font-weight:600;fill:var(--dg-ink)}"
       "#S .bz-lad{fill:none;stroke:var(--dg-ink);stroke-width:1.4}#S .bz-lead{fill:none;stroke:var(--dg-muted);stroke-width:1}"
       "#S .bz-warn{font-family:" + core.MONO + ";font-size:11px;font-weight:600;fill:var(--dg-amber-ink)}"
       "#S .bz-pt>.dg-sh{stroke:var(--dg-muted);stroke-width:1}#S .bz-fun{fill:var(--dg-blue-bg)}#S .bz-axl{stroke:var(--dg-ink);stroke-width:1.3;fill:none}"
       + "".join(f"#S .bz-q-{t}{{fill:var(--dg-{v})}}" for t, v in BG.items())
       + "".join(f"#S .bz-d-{t}{{fill:var(--dg-{v});stroke:var(--dg-card);stroke-width:1.5}}" for t, v in INK.items()))
BRANCH_TONES = ("teal", "amber", "lav", "green", "blue", "soft")


# ---------- shared helpers ----------
def _clean(pts):
    """Drop repeated and collinear middle points of an orthogonal polyline."""
    out = []
    for p in pts:
        if out and abs(out[-1][0] - p[0]) < .01 and abs(out[-1][1] - p[1]) < .01:
            continue
        if len(out) >= 2 and ((abs(out[-2][0] - out[-1][0]) < .01 and abs(out[-1][0] - p[0]) < .01) or
                              (abs(out[-2][1] - out[-1][1]) < .01 and abs(out[-1][1] - p[1]) < .01)):
            out[-1] = p
            continue
        out.append(p)
    return out


def _link(c, a, b, pts, **kw):
    core.arrow(c, _clean(pts), dict({"from": a, "to": b, "head": "none"}, **kw))


def _rows(title, items, w, sub=None, bullet=True):
    """Text rows of a panel: (text, indent, css class, size, bold, line height, bullet first)."""
    iw = w - 2 * PX
    rows = [(s, 0, "dg-l", 13, True, 17, False) for s in core.wrap(title, iw, 13, bold=True)] if title else []
    rows += [(s, 0, "dg-s", 12, False, 15, False) for s in core.wrap(sub, iw, 12)] if sub else []
    if items and rows:
        rows.append(None)
    ind = 12 if bullet else 0
    for it in items or []:
        rows += [(s, ind, "bz-i", 12, False, 16, bullet and k == 0) for k, s in enumerate(core.wrap(it, iw - ind, 12))]
    return rows


def panel_h(title, items, w, sub=None, bullet=True):
    return 2 * PY + sum(6 if r is None else r[5] for r in _rows(title, items, w, sub, bullet))


def panel(c, pid, title, items, x, y, w, h, tone="plain", sub=None, bullet=True, strong=False):
    """Box with a bold title and top-aligned bullet items; registered like a node so check.py checks its text."""
    cls = f"dg-n dg-t-{tone or 'plain'}" + (" dg-strong" if strong else "")
    out = [f'<g class="{cls}" data-id="{core.esc(pid)}">', core.shape_svg("box", x, y, w, h)]
    lines, ty = [], y + PY
    for r in _rows(title, items, w, sub, bullet):
        if r is None:
            ty += 6
            continue
        s, ind, kls, sz, bold, lh, bul = r
        by = ty + (lh - sz) / 2 + sz * .78
        if bul:
            out.append(f'<text class="bz-b" x="{core.F(x + PX)}" y="{core.F(by)}">•</text>')
        out.append(f'<text class="{kls}" x="{core.F(x + PX + ind)}" y="{core.F(by)}">{core.esc(s)}</text>')
        lines.append({"text": s, "x": x + PX + ind, "y": ty, "w": core.text_width(s, sz, bold=bold), "h": lh})
        ty += lh
    add_node_geo(c, pid, x, y, w, h, title or pid, lines)
    core.add(c, "".join(out) + "</g>", 2)


def add_node_geo(c, nid, x, y, w, h, text, lines, inner=None):
    c["rects"][nid] = (x, y, w, h)
    c["shapes"][nid] = "box"
    core.obstacle(c, x, y, w, h)
    c["geo"]["nodes"].append({"id": nid, "x": x, "y": y, "w": w, "h": h, "shape": "box", "text": text, "decision": False,
                              "free": True, "inner": inner or [x + PX, y + PY, w - 2 * PX, h - 2 * PY], "lines": lines})


def _too_wide(w, fix):
    if w > core.MAX_W:
        raise core.LayoutError(f"canvas would be {int(w)}px wide (max {core.MAX_W}): {fix}")


def _need(spec, *keys):
    return [f"{k}: required" for k in keys if not spec.get(k)]


def _tone_err(where, t):
    return [] if (t or "plain") in core.TONES else [f"{where}: tone '{t}' is not one of {', '.join(core.TONES)}"]


def _items(x):
    return [str(v) for v in (x or [])]


def _kind_look(spec, defaults, k):
    v = dict(defaults, **(spec.get("kinds") or {})).get(k)
    return {"tone": v} if isinstance(v, str) else dict(v or {})


def _legend_kinds(c, spec, defaults, used, solid=False):
    if spec.get("legend", True):
        core.legend(c, [{"label": lk.get("label", k).replace("_", " "), "tone": lk.get("tone"), "dashed": lk.get("dashed"),
                         "solid": solid} for k in dict.fromkeys(used) for lk in [_kind_look(spec, defaults, k)]])


def _mm_plain(spec, kind, nodes, edges, direction):
    return core.mermaid_flowchart(spec, nodes, edges, direction, {})


def _check_tree(items, name):
    err, ids = [], set()
    for n in items:
        if not n.get("id") or not n.get("label"):
            err.append(f"{name}: every entry needs id and label")
        elif n["id"] in ids:
            err.append(f"{name} {n['id']}: duplicate id")
        ids.add(n.get("id"))
        err += _tone_err(f"{name} {n.get('id')}", n.get("tone"))
    for n in items:
        if n.get("parent") and n["parent"] not in ids:
            err.append(f"{name} {n['id']}: parent '{n['parent']}' is not an id")
    if items and not any(not n.get("parent") for n in items):
        err.append(f"{name}: needs a root (an entry without parent)")
    return err


def _htree(c, sized, kids, roots, x0, side, gapx=48, gapy=14, top=M):
    """Horizontal tree: roots and their subtrees stacked from top, depth columns going right (side 1) or left
    (side -1) from x0. sized {id: (node, w, h)}. Returns ({id: rect}, column edges [(near, far)], height)."""
    depth, order = {}, []

    def walk(v, d):
        depth[v] = d
        order.append(v)
        for k in kids.get(v, []):
            walk(k, d + 1)

    for r in roots:
        walk(r, 0)
    nd = max(depth.values()) + 1 if depth else 0
    colw = [max(sized[v][1] for v in order if depth[v] == d) for d in range(nd)]
    cols, x = [], x0
    for d in range(nd):
        cols.append((x, x + side * colw[d]))
        x += side * (colw[d] + gapx)
    ext = {}

    def height(v):
        ks = kids.get(v, [])
        ext[v] = max(sized[v][2], sum(height(k) for k in ks) + gapy * (len(ks) - 1) if ks else 0)
        return ext[v]

    pos = {}

    def place(v, yt):
        n, w, h = sized[v]
        a, _ = cols[depth[v]]
        px = a if side > 0 else a - w
        pos[v] = (px, yt + (ext[v] - h) / 2, w, h)
        ks = kids.get(v, [])
        inner = sum(ext[k] for k in ks) + gapy * (len(ks) - 1)
        y = yt + (ext[v] - inner) / 2
        for k in ks:
            place(k, y)
            y += ext[k] + gapy

    y = top
    for r in roots:
        height(r)
        place(r, y)
        y += ext[r] + gapy * 2
    return pos, cols, y - gapy * 2 - top


def _elbow(c, a, b, ra, rb, side, bus):
    """Parent a -> child b of a horizontal tree: out of a's side, down the bus x, into b."""
    ya, yb = ra[1] + ra[3] / 2, rb[1] + rb[3] / 2
    xa = ra[0] + ra[2] if side > 0 else ra[0]
    xb = rb[0] if side > 0 else rb[0] + rb[2]
    _link(c, a, b, [(xa, ya), (bus, ya), (bus, yb), (xb, yb)])


# ---------- org-chart ----------
ORG_GX, ORG_GY, ORG_IND, ORG_SG = 20, 44, 26, 12


def validate_org(spec):
    return _need(spec, "units") or _check_tree(spec["units"], "units")


def _org_layout(units, sized, kids, roots, stack):
    stacked = lambda v: stack and kids[v] and all(not kids[k] for k in kids[v])  # noqa: E731
    depth, ext = {}, {}

    def meas(v, d):
        depth[v] = d
        _, w, h = sized[v]
        ks = kids[v]
        if stacked(v):
            for k in ks:
                depth[k] = d + 1
            ext[v] = max(w, ORG_IND + max(sized[k][1] for k in ks))
        elif ks:
            ext[v] = max(w, sum(meas(k, d + 1) for k in ks) + ORG_GX * (len(ks) - 1))
        else:
            ext[v] = w
        return ext[v]

    total = sum(meas(r, 0) for r in roots) + ORG_GX * (len(roots) - 1)
    lvl = {}
    for v, d in depth.items():
        par = next((p for p in kids if v in kids[p]), None)
        if not (par and stacked(par)):
            lvl[d] = max(lvl.get(d, 0), sized[v][2])
    ly, y = {}, M
    for d in sorted(lvl):
        ly[d] = y
        y += lvl[d] + ORG_GY
    pos = {}

    def place(v, x):
        _, w, h = sized[v]
        d = depth[v]
        if stacked(v):
            pos[v] = (x, ly[d], w, h)
            yy = ly[d] + h + ORG_SG
            for k in kids[v]:
                pos[k] = (x + ORG_IND, yy, sized[k][1], sized[k][2])
                yy += sized[k][2] + ORG_SG
            return
        pos[v] = (x + (ext[v] - w) / 2, ly[d], w, h)
        inner = sum(ext[k] for k in kids[v]) + ORG_GX * (len(kids[v]) - 1)
        xx = x + (ext[v] - inner) / 2
        for k in kids[v]:
            place(k, xx)
            xx += ext[k] + ORG_GX

    x = M
    for r in roots:
        place(r, x)
        x += ext[r] + ORG_GX
    return pos, total + 2 * M, stacked, ly, lvl, depth


def svg_org(spec, core_):
    c = core.canvas(spec)
    units = spec["units"]
    kinds_used = []
    sized, kids = {}, {u["id"]: [] for u in units}
    for u in units:
        lk = _kind_look(spec, {}, u.get("kind")) if u.get("kind") else {}
        if u.get("kind"):
            kinds_used.append(u["kind"])
        n = {"id": u["id"], "label": u["label"], "sub": u.get("sub"), "tag": u.get("tag"), "shape": "rounded",
             "tone": u.get("tone") or lk.get("tone"), "dashed": u.get("vacant") or lk.get("dashed"),
             "strong": not u.get("parent")}
        if u.get("vacant"):
            n["sub"] = " · ".join(x for x in ("vacant", u.get("sub")) if x)
        w, h = core.size(n, spec.get("max_w", 170))
        sized[u["id"]] = (n, w, h)
        if u.get("parent"):
            kids[u["parent"]].append(u["id"])
    roots = [u["id"] for u in units if not u.get("parent")]
    mode = spec.get("stack_leaves", "auto")
    lay = _org_layout(units, sized, kids, roots, mode is True)
    if lay[1] > core.MAX_W and mode == "auto":
        lay = _org_layout(units, sized, kids, roots, True)
    pos, W, stacked, ly, lvl, depth = lay
    _too_wide(W, "split the chart per unit (one chart per direct report), shorten labels, or set max_w lower")
    for v, (n, _, _) in sized.items():
        core.node(c, n, *pos[v])
    for v, ks in kids.items():
        if not ks:
            continue
        px, py, pw, ph = pos[v]
        if stacked(v):
            sx = px + 13
            for k in ks:
                r = pos[k]
                _link(c, v, k, [(sx, py + ph), (sx, r[1] + r[3] / 2), (r[0], r[1] + r[3] / 2)])
        else:
            bus = ly[depth[v]] + lvl[depth[v]] + ORG_GY / 2
            for k in ks:
                r = pos[k]
                _link(c, v, k, [(px + pw / 2, py + ph), (px + pw / 2, bus), (r[0] + r[2] / 2, bus), (r[0] + r[2] / 2, r[1])])
    _legend_kinds(c, spec, {}, kinds_used)
    if any(u.get("vacant") for u in units) and spec.get("legend", True):
        core.legend(c, [{"label": "vacant role", "dashed": True}])
    return core.finish(c) + ([CSS],)


def mermaid_org(spec):
    nodes = [{"id": u["id"], "label": " · ".join(x for x in (u["label"], u.get("sub"), "vacant" if u.get("vacant") else None) if x),
              "tone": u.get("tone") or _kind_look(spec, {}, u.get("kind")).get("tone")} for u in spec["units"]]
    edges = [{"from": u["parent"], "to": u["id"], "head": "none"} for u in spec["units"] if u.get("parent")]
    return core.mermaid_flowchart(spec, nodes, edges, "TB")


# ---------- team-topology (node-edge: plain | dbt | airflow styles) ----------
TEAM_KINDS = {"stream-aligned": {"tone": "amber", "label": "stream-aligned team"},
              "platform": {"tone": "blue", "label": "platform team"},
              "enabling": {"tone": "teal", "label": "enabling team"},
              "complicated-subsystem": {"tone": "lav", "label": "complicated-subsystem team"}}
TEAM_MODES = {"collaboration": {"style": "thick", "tone": "lav", "label": "collaboration"},
              "x-as-a-service": {"style": "solid", "label": "X-as-a-Service"},
              "facilitating": {"style": "dashed", "tone": "teal", "label": "facilitating"}}


def _team_map(spec):
    """Teams and interactions as base nodes and edges, plus the team-type kinds to colour by. In the airflow style
    the fill shows the run state when teams carry one, so the type moves into the tag and leaves the legend."""
    nodes = [{k: v for k, v in dict(t, kind=t.get("kind") or t.get("type")).items() if k != "type"} for t in spec["teams"]]
    edges = [dict({k: v for k, v in e.items() if k != "mode"}, kind=e.get("kind") or e.get("mode"))
             for e in spec.get("interactions") or []]
    kinds = TEAM_KINDS
    if spec.get("style") == "airflow":
        km = dict(TEAM_KINDS, **(spec.get("kinds") or {}))
        for n in nodes:
            if n.get("kind") and not n.get("operator"):
                n["operator"] = _kind_look({}, km, n["kind"]).get("label", n["kind"])
        if any(n.get("state") for n in nodes):
            kinds = None
            for n in nodes:
                n.pop("kind", None)
    s = dict(spec, nodes=nodes, edges=edges, edge_kinds=dict(TEAM_MODES, **(spec.get("edge_kinds") or {})))
    if not kinds:
        s.pop("kinds", None)
    return s, nodes, edges, kinds


def validate_team(spec):
    if not spec.get("teams"):
        return ["teams: required [{id, label, type, sub?, group?}]"]
    s, _, edges, _ = _team_map(spec)
    err = core.check_graph(s) + core.check_style(s)
    known = set(TEAM_KINDS) | set(spec.get("kinds") or {})
    err += [f"team {t['id']}: type '{t.get('type')}' is not one of {', '.join(sorted(known))}"
            for t in spec["teams"] if (t.get("type") or t.get("kind")) and (t.get("type") or t.get("kind")) not in known]
    err += [f"interaction {e['from']} -> {e['to']}: mode '{e['kind']}' is not one of {', '.join(TEAM_MODES)}"
            for e in edges if e.get("kind") and e["kind"] not in s["edge_kinds"]]
    return err


def svg_team(spec, core_):
    s, nodes, edges, kinds = _team_map(spec)
    # one port per arrow: a label on a shared trunk could belong to any branch
    return core.graph(s, nodes, edges, spec.get("groups"), kinds=kinds, spread=True)


def mermaid_team(spec):
    s, nodes, edges, kinds = _team_map(spec)
    return core.mermaid_graph(s, nodes, edges, spec.get("groups"), kinds=kinds)


# ---------- capability-map ----------
HEAT = {"strong": {"tone": "green", "label": "strong"}, "adequate": {"tone": "plain", "label": "adequate"},
        "weak": {"tone": "amber", "label": "weak"}, "missing": {"tone": "red", "dashed": True, "label": "missing"}}


def _heat(spec):
    return dict(HEAT, **{k: ({"tone": v} if isinstance(v, str) else v) for k, v in (spec.get("scale") or {}).items()})


def validate_cap(spec):
    err = _need(spec, "areas")
    sc = _heat(spec)
    for a in spec.get("areas") or []:
        if not a.get("label") or not a.get("caps"):
            err.append(f"area {a.get('id')}: needs label and caps")
        for cp in a.get("caps") or []:
            if not cp.get("label"):
                err.append(f"area {a.get('id')}: every cap needs a label")
            if cp.get("heat") and cp["heat"] not in sc:
                err.append(f"cap {cp.get('label')}: heat '{cp['heat']}' is not one of {', '.join(sc)} (or add it to scale)")
    if spec.get("layout", "auto") not in ("auto", "columns", "bands"):
        err.append("layout: auto, columns or bands")
    return err


def _cap_node(spec, a, i, cp):
    lk = _heat(spec).get(cp.get("heat"), {})
    sub = cp.get("sub") or (" · ".join(_items(cp.get("children"))) if cp.get("children") else None)
    return {"id": cp.get("id") or f"{a.get('id', 'a')}-{i}", "label": cp["label"], "sub": sub, "shape": "box",
            "tag": lk.get("label") if cp.get("heat") else None, "tone": cp.get("tone") or lk.get("tone"),
            "dashed": lk.get("dashed"), "heat": cp.get("heat")}


def svg_cap(spec, core_):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    areas = spec["areas"]
    layout = spec.get("layout", "auto")
    if layout == "auto":
        layout = "columns" if len(areas) <= 5 and max(len(a["caps"]) for a in areas) <= 8 else "bands"
    used = []
    if layout == "columns":
        cw = spec.get("max_w") or max(140, min(180, (core.MAX_W - 2 * M - (len(areas) - 1) * 12) // len(areas) - 2 * core.GP))
        cols = [[_cap_node(spec, a, i, cp) for i, cp in enumerate(a["caps"])] for a in areas]
        hs = [[core.size(n, cw, cw)[1] for n in col] for col in cols]
        heads = [len(core.label_lines(a["label"], cw + 2 * core.GP)) * 15 + 14 for a in areas]
        H = max(hd + sum(h) + 10 * (len(h) - 1) for hd, h in zip(heads, hs)) + core.GP
        x = M
        for a, col, h, hd in zip(areas, cols, hs, heads):
            gw = cw + 2 * core.GP
            core.container(c, a.get("id", a["label"]), a["label"], x, M, gw, H, members=[n["id"] for n in col])
            y = M + hd
            for n, hh in zip(col, h):
                core.node(c, n, x + core.GP, y, cw, hh)
                used += [n["heat"]] if n.get("heat") else []
                y += hh + 10
            x += gw + 12
        _too_wide(x - 12 + M, "use layout 'bands', fewer areas per map, or shorter capability names")
    else:
        hw = spec.get("header_w", 150)
        avail = core.MAX_W - 2 * M - hw - 24
        y = M
        for a in areas:
            ns = [_cap_node(spec, a, i, cp) for i, cp in enumerate(a["caps"])]
            sz = [core.size(n, 170, 130) for n in ns]
            per = max(1, min(len(ns), int((avail + 10) // (max(w for w, _ in sz) + 10))))
            cw = (avail - 10 * (per - 1)) / per
            rows = [ns[i:i + per] for i in range(0, len(ns), per)]
            rh = [max(core.size(n, cw, cw)[1] for n in r) for r in rows]
            bh = max(sum(rh) + 10 * (len(rh) - 1) + 24, len(core.label_lines(a["label"], hw)) * 15 + 20)
            core.container(c, a.get("id", a["label"]), a["label"], M, y, core.MAX_W - 2 * M, bh,
                           members=[n["id"] for n in ns], kind="band", header_w=hw)
            yy = y + 12
            for r, h in zip(rows, rh):
                xx = M + hw + 12
                for n in r:
                    core.node(c, n, xx, yy, cw, h)
                    used += [n["heat"]] if n.get("heat") else []
                    xx += cw + 10
                yy += h + 10
            y += bh + 10
    if spec.get("legend", True):
        sc = _heat(spec)
        core.legend(c, [{"label": sc[k].get("label", k), "tone": sc[k].get("tone"), "dashed": sc[k].get("dashed")}
                        for k in sc if k in used])
    return core.finish(c) + ([CSS],)


def mermaid_cap(spec):
    out = core.mermaid_head(spec, "flowchart TB")
    tones = {}
    for a in spec["areas"]:
        out.append(f"  subgraph {core.mm_id('a_' + str(a.get('id', a['label'])))} [{core.mm_text(a['label'])}]")
        out.append("    direction TB")
        for i, cp in enumerate(a["caps"]):
            n = _cap_node(spec, a, i, cp)
            lab = " · ".join(x for x in (n["label"], n.get("tag")) if x)
            out.append(f"    {core.mm_id(n['id'])}[{core.mm_text(lab)}]")
            if n.get("tone") in core.MM_TONE:
                tones.setdefault(n["tone"], []).append(core.mm_id(n["id"]))
        out.append("  end")
    for t, ids in tones.items():
        f, s = core.MM_TONE[t]
        out += [f"  classDef {t} fill:{f},stroke:{s}", f"  class {','.join(ids)} {t}"]
    return "\n".join(out) + "\n"


# ---------- value-stream ----------
def _num(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def validate_vs(spec):
    err = _need(spec, "stages")
    for s in spec.get("stages") or []:
        if not s.get("label"):
            err.append("stages: every stage needs a label")
        for k in ("time", "wait"):
            if k in s and not isinstance(s[k], (int, float)):
                err.append(f"stage {s.get('label')}: {k} must be a number in spec unit '{spec.get('unit', 'h')}'")
        err += _tone_err(f"stage {s.get('label')}", s.get("tone"))
    st = spec.get("stages") or []
    if st and st[0].get("wait") is not None and not spec.get("start"):
        err.append("stages[0].wait needs 'start' (the wait sits between start and stage 1): add start or drop the wait")
    return err


def svg_vs(spec, core_):
    c = core.canvas(spec)
    unit = spec.get("unit", "h")
    st = spec["stages"]
    ns = [{"id": s.get("id") or f"s{i}", "label": s["label"], "sub": s.get("sub"), "shape": "box", "strong": True,
           "tag": f"C&A {s['ca']}%" if s.get("ca") is not None else None, "tone": s.get("tone")} for i, s in enumerate(st)]
    if spec.get("start"):
        ns.insert(0, {"id": "start", "label": spec["start"], "shape": "pill", "tone": "soft"})
    if spec.get("end"):
        ns.append({"id": "end", "label": spec["end"], "shape": "pill", "tone": "soft"})
    sz = [core.size(n, spec.get("max_w", 150)) for n in ns]
    H = max(h for _, h in sz)
    gaps = [40] * (len(ns) - 1)
    # the wait before stage k sits in the gap left of it
    first = 1 if spec.get("start") else 0
    for k, s in enumerate(st):
        g = first + k - 1
        if g >= 0 and s.get("wait") is not None:
            gaps[g] = max(gaps[g], core.text_width(f"{_num(s['wait'])} {unit}", 11, True) + 20)
    for k, s in enumerate(st):
        if s.get("time") is not None and sz[first + k][0] < core.text_width(f"{_num(s['time'])} {unit}", 11, True) + 12:
            sz[first + k] = (int(core.text_width(f"{_num(s['time'])} {unit}", 11, True) + 12), sz[first + k][1])
    x, rects = M, []
    for (w, _), gp in zip(sz, gaps + [0]):
        rects.append((x, M, w, H))
        x += w + gp
    _too_wide(x + M, "fewer stages per diagram (split the stream), shorter stage names, or drop the start/end pills")
    for n, r in zip(ns, rects):
        core.node(c, n, *r)
    for a, b, ra, rb in zip(ns, ns[1:], rects, rects[1:]):
        core.arrow(c, [(ra[0] + ra[2], M + H / 2), (rb[0], M + H / 2)], {"from": a["id"], "to": b["id"]})
    hi, lo = M + H + 40, M + H + 66
    pts, tt, tw = [], 0.0, 0.0
    for k, s in enumerate(st):
        r = rects[first + k]
        left = rects[first + k - 1][0] + rects[first + k - 1][2] if first + k > 0 else r[0]
        if s.get("wait") is not None and first + k > 0:
            tw += s["wait"]
            t = f"{_num(s['wait'])} {unit}"
            core.text(c, (left + r[0]) / 2, hi - 17, t, "dg-txm", "middle", mono=True)
        pts += [(left, hi), (r[0], hi), (r[0], lo), (r[0] + r[2], lo), (r[0] + r[2], hi)]
        if s.get("time") is not None:
            tt += s["time"]
            core.text(c, r[0] + r[2] / 2, lo + 5, f"{_num(s['time'])} {unit}", "dg-txm", "middle", mono=True)
    core.line(c, _clean(pts), "bz-lad")
    lt = tt + tw
    eff = f" · flow efficiency {tt / lt * 100:.0f}%" if lt else ""
    summ = {"id": "summary", "label": f"Lead time {_num(round(lt, 2))} {unit} · process time {_num(round(tt, 2))} {unit}{eff}",
            "sub": "upper line = waiting · lower line = processing", "shape": "box", "tone": "soft", "free": True, "align": "left"}
    w, h = core.size(summ, 520)
    core.node(c, summ, M, lo + 34, w, h)
    return core.finish(c) + ([CSS],)


def mermaid_vs(spec):
    unit, st = spec.get("unit", "h"), spec["stages"]
    ns = [{"id": s.get("id") or f"s{i}", "label": " · ".join(x for x in (s["label"], s.get("sub"),
          f"{_num(s['time'])} {unit}" if s.get("time") is not None else None) if x), "tone": s.get("tone"), "shape": "box"}
          for i, s in enumerate(st)]
    es = [{"from": a["id"], "to": b["id"], "label": f"wait {_num(s['wait'])} {unit}" if s.get("wait") is not None else None}
          for a, b, s in zip(ns, ns[1:], st[1:])]
    if spec.get("start"):
        es.insert(0, {"from": "start", "to": ns[0]["id"],
                      "label": f"wait {_num(st[0]['wait'])} {unit}" if st[0].get("wait") is not None else None})
        ns.insert(0, {"id": "start", "label": spec["start"], "shape": "pill", "tone": "soft"})
    if spec.get("end"):
        es.append({"from": ns[-1]["id"], "to": "end"})
        ns.append({"id": "end", "label": spec["end"], "shape": "pill", "tone": "soft"})
    return core.mermaid_flowchart(spec, ns, es, "LR")


# ---------- value-chain ----------
def validate_vc(spec):
    err = _need(spec, "primary")
    for k in ("primary", "support"):
        for a in spec.get(k) or []:
            if not a.get("label"):
                err.append(f"{k}: every activity needs a label")
            err += _tone_err(f"{k} {a.get('label')}", a.get("tone"))
    return err


def _vc_sub(a):
    """Green marks a source of advantage; the word repeats it so greyscale (and teal next to green) still reads."""
    return " · ".join(x for x in (a.get("sub"), "advantage" if a.get("tone") == "green" else None) if x) or None


def svg_vc(spec, core_):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    W = spec.get("width", 940)
    mw = 110
    aw = W - mw - 12
    y = M
    sup = spec.get("support") or []
    if sup:
        core.text(c, M, y, "SUPPORT ACTIVITIES", "dg-txm", mono=True)
        y += 20
        for i, a in enumerate(sup):
            n = {"id": f"sup{i}", "label": a["label"], "sub": a.get("sub"), "shape": "box", "align": "left",
                 "tone": a.get("tone") or "soft", "free": True}
            h = core.size(n, aw, aw)[1]
            core.node(c, n, M, y, aw, h)
            y += h + 8
        y += 12
    core.text(c, M, y, "PRIMARY ACTIVITIES", "dg-txm", mono=True)
    y += 20
    pr = spec["primary"]
    pw = (aw - 8 * (len(pr) - 1)) / len(pr)
    if pw < 120:
        raise core.LayoutError(f"{len(pr)} primary activities leave {int(pw)}px each (min 120): merge activities")
    ph = max(panel_h(a["label"], _items(a.get("items")), pw, _vc_sub(a)) for a in pr)
    for i, a in enumerate(pr):
        panel(c, f"pri{i}", a["label"], _items(a.get("items")), M + i * (pw + 8), y, pw, ph, a.get("tone") or "teal", _vc_sub(a))
    bottom = y + ph
    mg = spec.get("margin") or {}
    n = {"id": "margin", "label": mg.get("label", "Margin"), "sub": mg.get("sub"), "shape": "box", "tone": mg.get("tone", "amber"),
         "strong": True, "free": True}
    core.node(c, n, M + aw + 12, M + 20, mw, bottom - M - 20)
    return core.finish(c, W + 2 * M) + ([CSS],)


# ---------- sipoc ----------
SIPOC = (("suppliers", "S · Suppliers"), ("inputs", "I · Inputs"), ("process", "P · Process"),
         ("outputs", "O · Outputs"), ("customers", "C · Customers"))


def validate_sipoc(spec):
    err = [f"{k}: required, a list of short items" for k, _ in SIPOC if not spec.get(k)]
    if len(spec.get("process") or []) > 8:
        err.append("process: at most 8 high-level steps (a SIPOC is a scope picture; detail goes in a flowchart)")
    return err


def svg_sipoc(spec, core_):
    c = core.canvas(spec)
    cw, gap, hh = 176, 10, 30
    y0 = M + hh + 8
    steps = [{"id": f"p{i}", "label": s, "shape": "rounded", "tone": "blue"} for i, s in enumerate(_items(spec["process"]))]
    ssz = [core.size(n, cw - 24, cw - 24)[1] for n in steps]
    ph = sum(ssz) + 18 * (len(steps) - 1) + 2 * 14
    H = max([ph] + [panel_h(None, _items(spec[k]), cw) for k, _ in SIPOC if k != "process"])
    for j, (k, head) in enumerate(SIPOC):
        x = M + j * (cw + gap)
        core.rect(c, x, M, cw, hh, "dg-hd", 4)
        core.text(c, x + cw / 2, M + (hh - 15.6) / 2, head, "dg-txb", "middle", size=12, bold=True)
        if k == "process":
            core.rect(c, x, y0, cw, H, "dg-hd", 3)
            y = y0 + 14 + (H - ph) / 2
            prev = None
            for n, h in zip(steps, ssz):
                core.node(c, n, x + 12, y, cw - 24, h)
                if prev:
                    core.arrow(c, [(x + cw / 2, prev), (x + cw / 2, y)], {"from": f"p{steps.index(n) - 1}", "to": n["id"]})
                prev = y + h
                y += h + 18
        else:
            panel(c, k, None, _items(spec[k]), x, y0, cw, H)
    if spec.get("scope"):
        core.text(c, M, y0 + H + 10, "Scope: " + spec["scope"], "dg-tx")
    return core.finish(c) + ([CSS],)


# ---------- quadrant and stakeholder-map ----------
QKEYS = ("top_left", "top_right", "bottom_left", "bottom_right")


def validate_quad(spec):
    err = _need(spec, "x", "y", "items")
    for a in ("x", "y"):
        if spec.get(a) and not isinstance(spec[a], dict):
            err.append(f"{a}: {{label, low, high}}")
    for k in (spec.get("quadrants") or {}):
        if k not in QKEYS:
            err.append(f"quadrants: '{k}' is not one of {', '.join(QKEYS)}")
    for it in spec.get("items") or []:
        if not it.get("label"):
            err.append("items: every item needs a label")
        for a in ("x", "y"):
            v = it.get(a)
            if not isinstance(v, (int, float)) or not 0 <= v <= 1:
                err.append(f"item {it.get('label')}: {a} must be a number from 0 to 1")
            elif v == 0.5:
                err.append(f"item {it.get('label')}: {a} = 0.5 is on the divider: pick a side (e.g. 0.45 or 0.55)")
        err += _tone_err(f"item {it.get('label')}", it.get("tone"))
    return err


def _ov(a, b, pad):
    return a[0] < b[0] + b[2] + pad and b[0] < a[0] + a[2] + pad and a[1] < b[1] + b[3] + pad and b[1] < a[1] + a[3] + pad


def _quad_draw(spec, kinds=None):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    PW, PH = spec.get("size", [600, 440])
    ax, ay = spec["x"], spec["y"]
    ylw = max(core.text_width(str(ay.get(k, "")), 11) for k in ("low", "high")) + 12
    x0, y0 = M + max(ylw, 40), M + 22
    q = spec.get("quadrants") or {}
    blocked = []
    for k in QKEYS:
        v = q.get(k) or {}
        v = {"label": v} if isinstance(v, str) else v
        right, bottom = k.endswith("right"), k.startswith("bottom")
        qx, qy = x0 + (PW / 2 if right else 0), y0 + (PH / 2 if bottom else 0)
        core.rect(c, qx, qy, PW / 2, PH / 2, f"bz-q-{v.get('tone', 'soft')}")
        if v.get("label"):
            tx = qx + PW / 2 - 10 if right else qx + 10
            ty = qy + PH / 2 - 26 if bottom else qy + 8
            blocked.append(core.text(c, tx, ty, v["label"], "dg-txb", "end" if right else "start", size=12, bold=True))
    core.line(c, [(x0 + PW / 2, y0), (x0 + PW / 2, y0 + PH)], "dg-ax2")
    core.line(c, [(x0, y0 + PH / 2), (x0 + PW, y0 + PH / 2)], "dg-ax2")
    core.add(c, f'<path class="bz-axl" d="M{core.F(x0)},{core.F(y0 - 6)} V{core.F(y0 + PH)} H{core.F(x0 + PW + 6)}"/>', 1)
    core.text(c, x0, y0 - 22, "↑ " + ay.get("label", ""), "dg-txb", size=12, bold=True)
    core.text(c, x0 - 8, y0 + PH - 14, str(ay.get("low", "")), "dg-tx", "end")
    core.text(c, x0 - 8, y0, str(ay.get("high", "")), "dg-tx", "end")
    core.text(c, x0, y0 + PH + 6, str(ax.get("low", "")), "dg-tx")
    core.text(c, x0 + PW, y0 + PH + 6, str(ax.get("high", "")), "dg-tx", "end")
    core.text(c, x0 + PW / 2, y0 + PH + 6, ax.get("label", "") + " →", "dg-txb", "middle", size=12, bold=True)
    items = sorted(spec["items"], key=lambda it: (-it["y"], it["x"]))
    dots, used = [], []
    for it in items:
        dx, dy = x0 + it["x"] * PW, y0 + (1 - it["y"]) * PH
        dots.append((dx - 7, dy - 7, 14, 14))
    for i, it in enumerate(items):
        lk = _kind_look(spec, kinds or {}, it.get("kind")) if it.get("kind") else {}
        if it.get("kind"):
            used.append(it["kind"])
        tone = it.get("tone") or lk.get("tone") or "ink"
        dx, dy = x0 + it["x"] * PW, y0 + (1 - it["y"]) * PH
        n = {"id": it.get("id") or f"i{i}", "label": it["label"], "sub": it.get("sub"), "shape": "rounded",
             "tone": "plain", "free": True, "cls": "bz-pt"}
        w, h = core.size(n, spec.get("max_w", 150), 40)
        cands = []
        for dist in (13, 24, 40, 64):
            cands += [(dx + dist, dy - h / 2), (dx - dist - w, dy - h / 2), (dx - w / 2, dy - dist - h),
                      (dx - w / 2, dy + dist), (dx + dist, dy - dist - h), (dx + dist, dy + dist),
                      (dx - dist - w, dy - dist - h), (dx - dist - w, dy + dist)]
        pick = None
        mx, my = x0 + PW / 2, y0 + PH / 2
        for cx, cy in cands:  # the label stays inside the dot's own quadrant, or the reader misplaces it
            r = (cx, cy, w, h)
            if r[0] < x0 + 2 or r[1] < y0 + 2 or r[0] + w > x0 + PW - 2 or r[1] + h > y0 + PH - 2:
                continue
            if ((r[0] < mx < r[0] + w) or (r[1] < my < r[1] + h) or (r[0] >= mx) != (dx >= mx)
                    or (r[1] >= my) != (dy >= my)):
                continue
            if any(_ov(r, b, 4) for b in blocked + dots):
                continue
            pick = r
            break
        if not pick:
            raise core.LayoutError(f"no free place inside its quadrant for the label of '{it['label']}': shorten labels "
                                   "or drop sub, move the item, or set a larger size [w, h] (e.g. [720, 500])")
        blocked.append(pick)
        core.node(c, n, *pick)
        near_x = min(max(dx, pick[0]), pick[0] + w)
        near_y = min(max(dy, pick[1]), pick[1] + h)
        if abs(near_x - dx) + abs(near_y - dy) > 18:
            core.line(c, [(dx, dy), (near_x, near_y)], "bz-lead", 1)
        core.add(c, f'<circle class="bz-d-{tone}" cx="{core.F(dx)}" cy="{core.F(dy)}" r="6"/>', 2)
        c["geo"]["labels"].append({"text": "point " + it["label"], "x": dx - 6, "y": dy - 6, "w": 12, "h": 12,
                                   "edge": None, "kind": "text"})
    _legend_kinds(c, spec, kinds or {}, used, solid=True)
    return core.finish(c) + ([CSS],)


def svg_quad(spec, core_):
    return _quad_draw(spec)


def _mm_q(s):
    return str(s).replace(":", " -").replace("[", "(").replace("]", ")").replace("\n", " ")


def _mm_axis(a, end):
    return _mm_q(f"{a.get(end, end.title())} {a.get('label', '')}".strip())


def mermaid_quad(spec):
    t = str(spec.get("title", "")).replace('"', "'")
    ax, ay, q = spec["x"], spec["y"], spec.get("quadrants") or {}
    out = ["---", f'title: "{t}"', "---", "quadrantChart", f"  %% Key: {spec.get('key', '')}",
           f"  %% Notice: {spec.get('notice', '')}",
           f"  x-axis {_mm_axis(ax, 'low')} --> {_mm_axis(ax, 'high')}",
           f"  y-axis {_mm_axis(ay, 'low')} --> {_mm_axis(ay, 'high')}"]
    for num, k in ((1, "top_right"), (2, "top_left"), (3, "bottom_left"), (4, "bottom_right")):
        v = q.get(k)
        v = v.get("label") if isinstance(v, dict) else v
        if v:
            out.append(f"  quadrant-{num} {_mm_q(v)}")
    for it in spec["items"]:
        out.append(f"  {_mm_q(it['label'])}: [{it['x']:.2f}, {it['y']:.2f}]")
    return "\n".join(out) + "\n"


STANCE = {"supporter": {"tone": "green", "label": "supporter"}, "neutral": {"tone": "ink", "label": "neutral"},
          "critic": {"tone": "amber", "label": "critic"}, "blocker": {"tone": "red", "label": "blocker"}}


def _stake_spec(spec):
    sc = spec.get("scale", 5)
    q = {"top_right": "Manage closely", "top_left": "Keep satisfied", "bottom_left": "Monitor", "bottom_right": "Keep informed"}
    q.update(spec.get("quadrants") or {})
    items = [{"id": s.get("id"), "label": s["label"], "sub": s.get("sub"), "kind": s.get("stance"), "tone": s.get("tone"),
              "x": 0.05 + 0.9 * (s["interest"] - 1) / (sc - 1), "y": 0.05 + 0.9 * (s["power"] - 1) / (sc - 1)}
             for s in spec["stakeholders"]]
    return dict(spec, x={"label": "Interest", "low": "low", "high": "high"}, y={"label": "Power", "low": "low", "high": "high"},
                quadrants=q, items=items)


def validate_stake(spec):
    err = _need(spec, "stakeholders")
    sc = spec.get("scale", 5)
    for s in spec.get("stakeholders") or []:
        for k in ("power", "interest"):
            if not isinstance(s.get(k), (int, float)) or not 1 <= s[k] <= sc:
                err.append(f"stakeholder {s.get('label')}: {k} must be a number from 1 to {sc}")
            elif s[k] == (1 + sc) / 2:
                err.append(f"stakeholder {s.get('label')}: {k} {s[k]:g} is the middle of 1-{sc} and sits on the divider: "
                           "pick a side (lower or higher), or use an even scale")
        if s.get("stance") and s["stance"] not in dict(STANCE, **(spec.get("kinds") or {})):
            err.append(f"stakeholder {s.get('label')}: stance '{s['stance']}' is not one of {', '.join(STANCE)}")
        if not s.get("label"):
            err.append("stakeholders: every entry needs a label")
    return err


def svg_stake(spec, core_):
    return _quad_draw(_stake_spec(spec), STANCE)


def mermaid_stake(spec):
    return mermaid_quad(_stake_spec(spec))


# ---------- swot ----------
SWOT = (("strengths", "Strengths", "green"), ("weaknesses", "Weaknesses", "amber"),
        ("opportunities", "Opportunities", "blue"), ("threats", "Threats", "red"))


def validate_swot(spec):
    return [f"{k}: required, a list of short points" for k, _, _ in SWOT if not spec.get(k)]


def svg_swot(spec, core_):
    c = core.canvas(spec)
    hw, cw, gap = 74, spec.get("cell_w", 400), 10
    x0, y0 = M + hw, M + 26
    core.text(c, x0 + cw / 2, M + 4, "Helpful", "dg-txm", "middle", mono=True)
    core.text(c, x0 + cw + gap + cw / 2, M + 4, "Harmful", "dg-txm", "middle", mono=True)
    y = y0
    for r, row in enumerate((SWOT[:2], SWOT[2:])):
        h = max(panel_h(t, _items(spec[k]), cw) for k, t, _ in row)
        core.text(c, M, y + h / 2 - 7, ("Internal", "External")[r], "dg-txm", mono=True)
        for j, (k, t, tone) in enumerate(row):
            panel(c, k, t, _items(spec[k]), x0 + j * (cw + gap), y, cw, h, tone)
        y += h + gap
    _too_wide(x0 + 2 * cw + gap + M, "set a smaller cell_w")
    return core.finish(c) + ([CSS],)


# ---------- funnel ----------
def validate_funnel(spec):
    err = _need(spec, "stages")
    for s in spec.get("stages") or []:
        if not s.get("label") or not isinstance(s.get("value"), (int, float)) or s["value"] < 0:
            err.append("stages: every stage needs a label and a value >= 0")
    vs = [s.get("value") for s in spec.get("stages") or [] if isinstance(s.get("value"), (int, float))]
    if vs and any(b > a for a, b in zip(vs, vs[1:])):
        err.append("stages: values must not grow from one stage to the next (a funnel narrows)")
    if spec.get("scale", "steps") not in ("steps", "value"):
        err.append("scale: steps (even narrowing, default) or value (width proportional to the value)")
    if vs and not vs[0]:
        err.append("stages: the first stage needs a value above 0")
    return err


def _fmt(v, unit=""):
    s = f"{v:,.0f}" if float(v).is_integer() or v >= 100 else f"{v:,.1f}"
    return f"{s} {unit}".strip()


def svg_funnel(spec, core_):
    c = core.canvas(spec)
    st = spec["stages"]
    unit = spec.get("unit", "")
    lw = min(200, max(core.text_width(s["label"], 12, bold=True) for s in st) + 4)
    BW, RW, bh, gap = spec.get("bar_w", 440), 190, 38, 30
    bx = M + lw + 20
    v0 = st[0]["value"]
    convs = [b["value"] / a["value"] * 100 if a["value"] else 0 for a, b in zip(st, st[1:])]
    worst = convs.index(min(convs)) if convs else -1
    y, prev = M, None
    for i, s in enumerate(st):
        lab = _fmt(s["value"], unit)
        minw = core.text_width(lab, 13, bold=True) + 28
        share = s["value"] / v0 if spec.get("scale") == "value" else 1 - 0.7 * i / max(1, len(st) - 1)
        w = max(minw, BW * share)
        x = bx + (BW - w) / 2
        n = {"id": f"st{i}", "label": lab, "shape": "box", "tone": s.get("tone") or "blue", "solid": True, "free": True}
        core.node(c, n, x, y, w, bh)
        ls = core.wrap(s["label"], lw, 12, bold=True)
        ty = y + (bh - 16 * len(ls) - (14 if s.get("sub") else 0)) / 2
        for k, t in enumerate(ls):
            core.text(c, bx - 20, ty + k * 16, t, "dg-txb", "end", size=12, bold=True)
        if s.get("sub"):
            core.text(c, bx - 20, ty + len(ls) * 16, s["sub"], "dg-tx", "end")
        if prev:
            px, pw = prev
            core.add(c, f'<polygon class="bz-fun" points="{core.F(px)},{core.F(y - gap)} {core.F(px + pw)},{core.F(y - gap)} '
                        f'{core.F(x + w)},{core.F(y)} {core.F(x)},{core.F(y)}"/>', 0)
            cv = convs[i - 1]
            t = f"{cv:.0f}% of previous" if cv >= 10 else f"{cv:.1f}% of previous"
            if i - 1 == worst and len(convs) > 1:
                core.text(c, bx + BW + 20, y - gap / 2 - 7, t + " · biggest drop", "bz-warn", mono=True, bold=True)
            else:
                core.text(c, bx + BW + 20, y - gap / 2 - 7, t, "dg-txm", mono=True)
        prev = (x, w)
        y += bh + gap
    ov = st[-1]["value"] / v0 * 100
    core.text(c, bx + BW + 20, y - gap - bh / 2 - 7, f"{ov:.1f}% of first stage", "dg-txm", mono=True)
    _too_wide(bx + BW + 20 + RW + M, "shorten stage labels or set a smaller bar_w")
    return core.finish(c, bx + BW + 20 + RW + M) + ([CSS],)


# ---------- mind-map ----------
def validate_mind(spec):
    err = _need(spec, "root", "branches")
    for b in spec.get("branches") or []:
        if not isinstance(b, dict) or not b.get("label"):
            err.append("branches: every branch is {label, children?, tone?}")
            continue
        err += _tone_err(f"branch {b['label']}", b.get("tone"))
    return err


def _mind_items(spec, compact=None):
    """(items {id: node}, kids {id: [ids]}); compact folds level 3 into the sub text of level 2."""
    items, kids = {"root": {"id": "root", "label": spec["root"], "tone": "ink", "shape": "rounded", "strong": True}}, {"root": []}
    compact = spec.get("compact") if compact is None else compact

    def add(parent, x, depth, tone, k):
        x = {"label": x} if isinstance(x, str) else x
        i = f"{parent}-{k}"
        ch = [({"label": v} if isinstance(v, str) else v) for v in x.get("children") or []]
        sub = x.get("sub")
        if ch and (compact and depth >= 2 or depth >= 3):
            sub = " · ".join(v["label"] for v in ch)
            ch = []
        items[i] = {"id": i, "label": x["label"], "sub": sub, "shape": "rounded",
                    "tone": tone if depth == 1 else x.get("tone") or "plain", "strong": depth == 1}
        kids[parent].append(i)
        kids[i] = []
        for j, v in enumerate(ch):
            add(i, v, depth + 1, tone, j)

    for k, b in enumerate(spec["branches"]):
        add("root", b, 1, b.get("tone") or BRANCH_TONES[k % len(BRANCH_TONES)], k)
    return items, kids


def svg_mind(spec, core_):
    if spec.get("compact") is None:  # auto: full depth when it fits, else fold the deepest level into sub text
        try:
            return _mind_draw(spec, False)
        except core.LayoutError:
            return _mind_draw(spec, True)
    return _mind_draw(spec, spec["compact"])


def _mind_draw(spec, compact):
    c = core.canvas(spec)
    items, kids = _mind_items(spec, compact)
    mw = spec.get("max_w", 160)
    sized = {i: (n, *core.size(n, mw if i != "root" else 180)) for i, n in items.items()}
    br = kids["root"]
    leaves = {}

    def wt(v):
        leaves[v] = max(1, sum(wt(k) for k in kids[v]))
        return leaves[v]

    wt("root")
    total, acc, right = leaves["root"], 0, []
    for b in br:
        if acc < total / 2 or not right:
            right.append(b)
            acc += leaves[b]
    left = [b for b in br if b not in right]
    _, rw, rh = sized["root"]
    gap = 44
    side_w = lambda ids: sum(  # noqa: E731
        max([sized[v][1] for v in ids_at] or [0]) + gap for ids_at in _levels(ids, kids))
    lw_, rw_ = side_w(left), side_w(right)
    rx = M + lw_
    posR, colsR, hR = _htree(c, sized, kids, right, rx + rw + gap, 1, gap) if right else ({}, [], 0)
    posL, colsL, hL = _htree(c, sized, kids, left, rx - gap, -1, gap) if left else ({}, [], 0)
    H = max(hR, hL, rh)
    sh = lambda pos, h: {k: (r[0], r[1] + (H - h) / 2, r[2], r[3]) for k, r in pos.items()}  # noqa: E731
    pos = dict(sh(posR, hR), **sh(posL, hL))
    pos["root"] = (rx, M + (H - rh) / 2, rw, rh)
    W = (max(r[0] + r[2] for r in pos.values()) + M)
    _too_wide(W, "shorten labels, set a lower max_w, or draw one map per branch")
    for i, (n, _, _) in sized.items():
        core.node(c, n, *pos[i])
    for side, ids, cols in ((1, right, colsR), (-1, left, colsL)):
        for b in ids:
            bus = rx + rw + gap / 2 if side > 0 else rx - gap / 2
            _elbow(c, "root", b, pos["root"], pos[b], side, bus)
            stack = [(b, 0)]
            while stack:
                v, d = stack.pop()
                for k in kids[v]:
                    bus = cols[d][1] + side * gap / 2
                    _elbow(c, v, k, pos[v], pos[k], side, bus)
                    stack.append((k, d + 1))
    return core.finish(c) + ([CSS],)


def _levels(ids, kids):
    out, cur = [], list(ids)
    while cur:
        out.append(cur)
        cur = [k for v in cur for k in kids[v]]
    return out


def mermaid_mind(spec):
    items, kids = _mind_items(spec)

    def lab(s):
        s = str(s).replace("\n", " ")
        return f'["`{s}`"]' if any(ch in s for ch in "()[]{}`\"") else s

    t = str(spec.get("title", "")).replace('"', "'")
    out = ["---", f'title: "{t}"', "---", "mindmap", f"  %% Key: {spec.get('key', '')}",
           f"  %% Notice: {spec.get('notice', '')}", f"  root(({str(spec['root']).replace(')', '').replace('(', '')}))"]

    def walk(v, d):
        for k in kids[v]:
            n = items[k]
            text = n["label"] + (f" - {n['sub']}" if n.get("sub") else "")
            out.append("  " * (d + 2) + (f"{core.mm_id(k)}{lab(text)}" if lab(text) != text else text))
            walk(k, d + 1)

    walk("root", 0)
    return "\n".join(out) + "\n"


# ---------- fishbone ----------
def validate_fish(spec):
    err = _need(spec, "problem", "categories")
    cats = spec.get("categories") or []
    if len(cats) > 8:
        err.append("categories: at most 8 (group causes; the classic set is 6)")
    for k in cats:
        if not k.get("label") or not k.get("causes"):
            err.append("categories: every category needs a label and causes")
    return err


def _cause_rows(causes, tw=170):
    rows = []
    for cz in causes:
        cz = {"label": cz} if isinstance(cz, str) else cz
        blk = [(s, "bz-i", 12, False) for s in core.wrap(cz["label"], tw, 12)]
        blk += [(s, "dg-tx", 11, False) for sc in _items(cz.get("causes")) for s in core.wrap("– " + sc, tw - 10, 11)]
        rows.append(blk)
    return rows


def svg_fish(spec, core_):
    c = core.canvas(spec)
    cats = spec["categories"]
    half = (len(cats) + 1) // 2
    sides = [cats[:half], cats[half:]]
    LH, CG, PADB = 16, 6, 14
    cat_rows = [[_cause_rows(k["causes"]) for k in s] for s in sides]
    hs = [max([sum(len(b) * LH for b in r) + CG * (len(r) - 1) + 2 * PADB for r in s] or [0]) for s in cat_rows]
    labs = [[{"id": f"cat{si}{j}", "label": k["label"], "shape": "box", "tone": k.get("tone") or "soft", "strong": True}
             for j, k in enumerate(s)] for si, s in enumerate(sides)]
    lsz = [[core.size(n, 160) for n in s] for s in labs]
    tws = [[max(core.text_width(t, sz) for b in r for t, _, sz, _ in b) for r in s] for s in cat_rows]
    slope = 0.42
    D = [h * slope for h in hs]
    lh_top = max([h for _, h in lsz[0]] or [0])
    sy = M + lh_top + hs[0]
    xs = []
    for j in range(half):
        need = 0
        for si in (0, 1):
            if j < len(sides[si]):
                need = max(need, D[si] + 12 + tws[si][j], D[si] + lsz[si][j][0] / 2)
        if j == 0:
            xs.append(M + need)
        else:
            sp = max([tws[si][j] + 40 for si in (0, 1) if j < len(sides[si])] +
                     [(lsz[si][j][0] + lsz[si][j - 1][0]) / 2 + 24 for si in (0, 1) if j < len(sides[si])])
            xs.append(xs[-1] + sp)
    head = {"id": "head", "label": spec["problem"], "sub": spec.get("sub"), "shape": "box", "tone": "red", "strong": True}
    hw_, hh_ = core.size(head, 180)
    hx = xs[-1] + 36
    _too_wide(hx + hw_ + M, "fewer categories, shorter cause texts, or one fishbone per area")
    core.node(c, head, hx, sy - hh_ / 2, hw_, hh_)
    core.arrow(c, [(M, sy), (hx, sy)], {"from": "spine", "to": "head", "style": "thick"})
    for si, s in enumerate(sides):
        sgn = -1 if si == 0 else 1
        for j, k in enumerate(s):
            bx, n = xs[j], labs[si][j]
            lw, lh = lsz[si][j]
            ex, ey = bx - D[si], sy + sgn * hs[si]
            core.node(c, n, ex - lw / 2, ey - lh if si == 0 else ey, lw, lh)
            _link(c, n["id"], "head", [(ex, ey), (bx, sy)])
            bone = lambda yy: bx - D[si] * abs(yy - sy) / hs[si]  # noqa: E731,B023
            blocks = cat_rows[si][j]
            tot = sum(len(b) * LH for b in blocks) + CG * (len(blocks) - 1)
            y = (ey + PADB) if si == 0 else (sy + PADB)
            if si == 0:
                y = sy - PADB - tot
            for b in blocks:
                yb = y + len(b) * LH
                xr = bone(y if si == 0 else yb) - 12
                for t, cls, sz, _ in b:
                    core.text(c, xr, y + (LH - sz * 1.3) / 2, t, cls, "end", size=sz)
                    y += LH
                ym = yb - len(b) * LH + LH / 2
                core.line(c, [(xr + 3, ym), (bone(ym) - 1, ym)], "bz-lead", 1)
                y += CG
    return core.finish(c) + ([CSS],)


def mermaid_fish(spec):
    t = str(spec.get("title", "")).replace('"', "'")
    out = ["---", f'title: "{t}"', "---", "ishikawa-beta", f"  %% Key: {spec.get('key', '')}",
           f"  %% Notice: {spec.get('notice', '')}", "  %% ishikawa-beta needs Mermaid 11.12.3 or later",
           f"  {spec['problem']}"]
    for k in spec["categories"]:
        out.append(f"    {k['label']}")
        for cz in k["causes"]:
            cz = {"label": cz} if isinstance(cz, str) else cz
            out.append(f"      {cz['label']}")
            out += [f"        {s}" for s in _items(cz.get("causes"))]
    return "\n".join(out) + "\n"


# ---------- business-model-canvas ----------
BMC = (("key_partners", "Key partners"), ("key_activities", "Key activities"), ("key_resources", "Key resources"),
       ("value_propositions", "Value propositions"), ("customer_relationships", "Customer relationships"),
       ("channels", "Channels"), ("customer_segments", "Customer segments"), ("cost_structure", "Cost structure"),
       ("revenue_streams", "Revenue streams"))


def validate_bmc(spec):
    return [f"{k}: required, a list of short points" for k, _ in BMC if not spec.get(k)]


def svg_bmc(spec, core_):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    W = spec.get("width", 968)
    g = 6
    cw = (W - 4 * g) / 5
    T = dict(BMC)
    tone = spec.get("tones") or {}
    ph = lambda k, w=cw: panel_h(T[k], _items(spec[k]), w)  # noqa: E731
    top = max(ph("key_partners"), ph("value_propositions"), ph("customer_segments"),
              ph("key_activities") + g + ph("key_resources"), ph("customer_relationships") + g + ph("channels"))
    xs = [M + i * (cw + g) for i in range(5)]
    for k, x in (("key_partners", xs[0]), ("value_propositions", xs[2]), ("customer_segments", xs[4])):
        panel(c, k, T[k], _items(spec[k]), x, M, cw, top, tone.get(k))
    for a, b, x in (("key_activities", "key_resources", xs[1]), ("customer_relationships", "channels", xs[3])):
        ha = max(ph(a), top - g - ph(b))
        panel(c, a, T[a], _items(spec[a]), x, M, cw, ha, tone.get(a))
        panel(c, b, T[b], _items(spec[b]), x, M + ha + g, cw, top - ha - g, tone.get(b))
    bw = (W - g) / 2
    bh = max(ph("cost_structure", bw), ph("revenue_streams", bw))
    panel(c, "cost_structure", T["cost_structure"], _items(spec["cost_structure"]), M, M + top + g, bw, bh,
          tone.get("cost_structure"))
    panel(c, "revenue_streams", T["revenue_streams"], _items(spec["revenue_streams"]), M + bw + g, M + top + g, bw, bh,
          tone.get("revenue_streams"))
    _too_wide(W + 2 * M, "set a smaller width")
    return core.finish(c, W + 2 * M) + ([CSS],)


# ---------- kpi-tree ----------
STATUS = {"on_track": {"tone": "green", "label": "on track"}, "at_risk": {"tone": "amber", "label": "at risk"},
          "off_track": {"tone": "red", "label": "off track"}}
TREND = {"up": "↑", "down": "↓", "flat": "→"}


def validate_kpi(spec):
    err = _need(spec, "metrics") or _check_tree(spec["metrics"], "metrics")
    for m in spec.get("metrics") or []:
        if m.get("status") and m["status"] not in STATUS:
            err.append(f"metric {m.get('id')}: status '{m['status']}' is not one of {', '.join(STATUS)}")
        if m.get("trend") and m["trend"] not in TREND:
            err.append(f"metric {m.get('id')}: trend '{m['trend']}' is not one of {', '.join(TREND)}")
    if len([m for m in spec.get("metrics") or [] if not m.get("parent")]) > 1:
        err.append("metrics: exactly one root (the north-star metric)")
    return err


def _kpi_node(m):
    st = STATUS.get(m.get("status"), {})
    tag = " · ".join(x for x in (str(m["value"]) if m.get("value") is not None else None,
                                 f"target {m['target']}" if m.get("target") is not None else None) if x)
    sub = " ".join(x for x in (TREND.get(m.get("trend")), st.get("label"), m.get("sub")) if x)
    return {"id": m["id"], "label": m["label"], "tag": tag or None, "sub": sub or None, "shape": "rounded",
            "tone": m.get("tone") or st.get("tone"), "strong": not m.get("parent")}


def svg_kpi(spec, core_):
    c = core.canvas(spec)
    ms = spec["metrics"]
    sized = {m["id"]: (n, *core.size(n, spec.get("max_w", 180))) for m in ms for n in [_kpi_node(m)]}
    kids = {m["id"]: [x["id"] for x in ms if x.get("parent") == m["id"]] for m in ms}
    root = next(m["id"] for m in ms if not m.get("parent"))
    gap = 60
    pos, cols, _ = _htree(c, sized, kids, [root], M, 1, gap, 12)
    _too_wide(max(r[0] + r[2] for r in pos.values()) + M, "fewer levels per tree (one tree per driver), or a smaller max_w")
    depth = {root: 0}
    order = [root]
    for v in order:
        for k in kids[v]:
            depth[k] = depth[v] + 1
            order.append(k)
    for i, (n, _, _) in sized.items():
        core.node(c, n, *pos[i])
    op = {m["id"]: m.get("op") for m in ms}
    for v in order:
        if not kids[v]:
            continue
        bus = cols[depth[v]][1] + gap / 2
        for k in kids[v]:
            _elbow(c, v, k, pos[v], pos[k], 1, bus)
        if op.get(v):
            cy = pos[v][1] + pos[v][3] / 2
            core.add(c, f'<circle class="bz-op" cx="{core.F(bus)}" cy="{core.F(cy)}" r="9"/>'
                        f'<text class="bz-opt" x="{core.F(bus)}" y="{core.F(cy + 4.3)}" text-anchor="middle">{core.esc(op[v])}</text>', 3)
    used = [m["status"] for m in ms if m.get("status")]
    if spec.get("legend", True):
        core.legend(c, [{"label": STATUS[k]["label"], "tone": STATUS[k]["tone"]} for k in STATUS if k in used])
    return core.finish(c) + ([CSS],)


def mermaid_kpi(spec):
    ns = []
    for m in spec["metrics"]:
        n = _kpi_node(m)
        lab = " · ".join(x for x in (n["label"], n.get("tag"), n.get("sub")) if x)
        if m.get("op"):
            lab += f" (children combine with {m['op']})"
        ns.append(dict(n, label=lab))
    es = [{"from": m["parent"], "to": m["id"], "head": "none"} for m in spec["metrics"] if m.get("parent")]
    return core.mermaid_flowchart(spec, ns, es, "LR")


# ---------- decision-matrix ----------
def validate_dm(spec):
    err = _need(spec, "options", "criteria")
    no = len(spec.get("options") or [])
    sc = spec.get("scale", 5)
    for cr in spec.get("criteria") or []:
        if not cr.get("label") or not isinstance(cr.get("weight"), (int, float)) or cr["weight"] <= 0:
            err.append(f"criterion {cr.get('label')}: needs a label and a weight > 0")
        s = cr.get("scores") or []
        if len(s) != no:
            err.append(f"criterion {cr.get('label')}: {len(s)} scores for {no} options")
        for v in s:
            v = v.get("score") if isinstance(v, dict) else v
            if not isinstance(v, (int, float)) or not 0 <= v <= sc:
                err.append(f"criterion {cr.get('label')}: score {v} is not a number from 0 to {sc}")
    if no > 6:
        err.append("options: at most 6 (shortlist first)")
    return err


def _dm_totals(spec):
    tw = sum(cr["weight"] for cr in spec["criteria"])
    sc = lambda v: v.get("score") if isinstance(v, dict) else v  # noqa: E731
    return [sum(cr["weight"] * sc(cr["scores"][j]) for cr in spec["criteria"]) / tw for j in range(len(spec["options"]))], tw


def svg_dm(spec, core_):
    c = core.canvas(spec)
    c["geo"]["connected"] = False
    opts, crit, scale = spec["options"], spec["criteria"], spec.get("scale", 5)
    tot, tw = _dm_totals(spec)
    best = tot.index(max(tot))
    hw = 220
    ow = max(110, min(170, (core.MAX_W - 2 * M - hw - 6 * len(opts)) / len(opts)))
    heads = [{"id": f"o{j}", "label": o if isinstance(o, str) else o["label"],
              "sub": None if isinstance(o, str) else o.get("sub"), "shape": "box", "tone": "soft"} for j, o in enumerate(opts)]
    hh = max(core.size(n, ow, ow)[1] for n in heads)
    rows = [{"id": f"c{i}", "label": cr["label"], "tag": f"weight {cr['weight'] / tw * 100:.0f}%", "sub": cr.get("sub"),
             "shape": "box", "tone": "soft", "align": "left"} for i, cr in enumerate(crit)]
    cells = [[{"id": f"s{i}_{j}", "label": f"{v.get('score') if isinstance(v, dict) else v}",
               "sub": v.get("note") if isinstance(v, dict) else None, "shape": "box"}
              for j, v in enumerate(cr["scores"])] for i, cr in enumerate(crit)]
    for r in cells:
        for n in r:
            f = float(n["label"]) / scale
            n["tone"] = "green" if f >= .8 else "amber" if f <= .4 else "plain"
    x0, y = M + hw + 6, M
    core.text(c, M, M + hh / 2 - 7, spec.get("corner", "criterion · weight"), "dg-txm", mono=True)
    for j, n in enumerate(heads):
        core.node(c, n, x0 + j * (ow + 6), y, ow, hh)
    y += hh + 6
    for i, rn in enumerate(rows):
        h = max([core.size(rn, hw, hw)[1]] + [core.size(n, ow, ow)[1] for n in cells[i]])
        core.node(c, rn, M, y, hw, h)
        for j, n in enumerate(cells[i]):
            core.node(c, n, x0 + j * (ow + 6), y, ow, h)
        y += h + 6
    tr = {"id": "total", "label": "Weighted score", "tag": f"out of {scale}", "shape": "box", "tone": "soft", "align": "left",
          "strong": True}
    tn = [{"id": f"t{j}", "label": f"{t:.2f}", "tag": "highest" if j == best else None, "shape": "box",
           "tone": "blue" if j == best else "plain", "strong": True} for j, t in enumerate(tot)]
    h = max(core.size(n, ow, ow)[1] for n in tn + [tr])
    y += 6
    core.node(c, tr, M, y, hw, h)
    for j, n in enumerate(tn):
        core.node(c, n, x0 + j * (ow + 6), y, ow, h)
    _too_wide(x0 + len(opts) * (ow + 6) + M, "fewer options or shorter option names")
    if spec.get("legend", True):
        core.legend(c, [{"label": f"score ≥ {0.8 * scale:g}", "tone": "green"}, {"label": f"score ≤ {0.4 * scale:g}", "tone": "amber"},
                        {"label": "highest weighted score", "tone": "blue", "strong": True}])
    return core.finish(c) + ([CSS],)


NONE = lambda spec: None  # noqa: E731
TYPES = {
    "org-chart": {"svg": svg_org, "mermaid": mermaid_org, "validate": validate_org,
                  "doc": "reporting lines as a top-down tree; leaves stack under their manager when wide"},
    "team-topology": {"svg": svg_team, "mermaid": mermaid_team, "validate": validate_team,
                      "doc": "teams by type and their interaction modes; style plain|dbt|airflow"},
    "capability-map": {"svg": svg_cap, "mermaid": mermaid_cap, "validate": validate_cap,
                       "doc": "L1 areas holding L2 capabilities (L3 as sub), heat colour per capability"},
    "value-stream": {"svg": svg_vs, "mermaid": mermaid_vs, "validate": validate_vs,
                     "doc": "stages left to right with a wait/process time ladder, lead time and flow efficiency"},
    "value-chain": {"svg": svg_vc, "mermaid": NONE, "validate": validate_vc,
                    "doc": "support activities over primary activities, margin at the end"},
    "sipoc": {"svg": svg_sipoc, "mermaid": NONE, "validate": validate_sipoc,
              "doc": "suppliers, inputs, process steps, outputs, customers in five columns"},
    "quadrant": {"svg": svg_quad, "mermaid": mermaid_quad, "validate": validate_quad,
                 "doc": "2x2 with named quadrants and labelled points at x, y from 0 to 1"},
    "stakeholder-map": {"svg": svg_stake, "mermaid": mermaid_stake, "validate": validate_stake,
                        "doc": "power / interest grid, stance colour per stakeholder"},
    "swot": {"svg": svg_swot, "mermaid": NONE, "validate": validate_swot,
             "doc": "strengths, weaknesses, opportunities, threats in a 2x2"},
    "funnel": {"svg": svg_funnel, "mermaid": NONE, "validate": validate_funnel,
               "doc": "stage bars narrowing top to bottom (scale steps|value), step and overall conversion, biggest drop marked"},
    "mind-map": {"svg": svg_mind, "mermaid": mermaid_mind, "validate": validate_mind,
                 "doc": "central topic with branches left and right, up to three levels"},
    "fishbone": {"svg": svg_fish, "mermaid": mermaid_fish, "validate": validate_fish,
                 "doc": "Ishikawa cause and effect: problem head, category bones, causes and sub-causes"},
    "business-model-canvas": {"svg": svg_bmc, "mermaid": NONE, "validate": validate_bmc,
                              "doc": "the nine building blocks in the canvas layout"},
    "kpi-tree": {"svg": svg_kpi, "mermaid": mermaid_kpi, "validate": validate_kpi,
                 "doc": "north-star metric left, drivers to the right, operator, value, target, status"},
    "decision-matrix": {"svg": svg_dm, "mermaid": NONE, "validate": validate_dm,
                        "doc": "weighted criteria x options, score heat, weighted total, highest marked"},
}
