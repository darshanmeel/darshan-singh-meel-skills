"""Data family types for the darshan-singh-meel-diagrams engine: er, star-schema, lineage, dbt-lineage, airflow-dag,
airflow-overview, dfd, medallion, orchestration, cdc-streaming, data-mesh.
Loaded by ../../darshan-singh-meel-diagrams/scripts/diagram.py through its registry. Spec fields: references/*.md."""
import math
import re

import diagram as core

MONO = '"IBM Plex Mono",Consolas,monospace'
_STYLE_OK = ("plain", "dbt", "airflow")

# ---------- kind and state maps (our palette; tone names from the base) ----------
LIN_KINDS = {"source": {"tone": "green", "label": "source system", "shape": "cylinder"},
             "table": {"tone": "blue", "label": "table", "shape": "cylinder"},
             "view": {"tone": "teal", "label": "view", "shape": "cylinder", "dashed": True},
             "file": {"tone": "soft", "label": "file", "shape": "document"},
             "job": {"tone": "plain", "label": "job", "shape": "rounded"},
             "stream": {"tone": "ink", "label": "stream / topic", "shape": "pill"},
             "api": {"tone": "ink", "label": "API", "shape": "hexagon"},
             "ml_model": {"tone": "lav", "label": "ML model", "shape": "hexagon"},
             "report": {"tone": "amber", "label": "report / dashboard", "shape": "document"}}
STREAM_KINDS = {"db": {"tone": "green", "label": "source database", "shape": "cylinder"},
                "connector": {"tone": "plain", "label": "CDC connector", "shape": "hexagon"},
                "topic": {"tone": "teal", "label": "topic", "shape": "pill"},
                "processor": {"tone": "blue", "label": "stream processor", "shape": "rounded"},
                "sink": {"tone": "lav", "label": "sink", "shape": "cylinder"},
                "registry": {"tone": "soft", "label": "schema registry", "shape": "box", "dashed": True},
                "dlq": {"tone": "red", "label": "dead-letter topic", "shape": "pill"},
                "app": {"tone": "amber", "label": "consumer app", "shape": "rounded"}}
MESH_KINDS = {"system": {"tone": "soft", "label": "operational system", "shape": "cylinder"},
              "source_aligned": {"tone": "blue", "label": "source-aligned product"},
              "aggregate": {"tone": "teal", "label": "aggregate product"},
              "consumer_aligned": {"tone": "lav", "label": "consumer-aligned product"},
              "consumer": {"tone": "amber", "label": "consumer", "shape": "document"}}
DFD_KINDS = {"external": {"tone": "soft", "label": "external entity", "shape": "box"},
             "process": {"tone": "blue", "label": "process", "shape": "rounded"},
             "store": {"tone": "plain", "label": "data store", "shape": "box"}}
ORCH_STATES = {"failed": {"tone": "red"}, "cancelled": {"tone": "soft", "dashed": True},
               "in_progress": {"tone": "teal", "label": "in progress"}, "queued": {"tone": "soft"},
               "skipped": {"tone": "lav"}, "succeeded": {"tone": "green"}}
ORCH_EDGES = {"on_succeeded": {"label": "on success"}, "on_failed": {"tone": "red", "label": "on failure"},
              "on_completed": {"style": "dashed", "tone": "blue", "label": "on completion"},
              "on_skipped": {"style": "dotted", "tone": "muted", "label": "on skip"},
              "trigger": {"style": "dashed", "tone": "blue", "label": "starts run"}}
NO_STATUS = {"no_status": {"tone": "plain", "dashed": True, "label": "no status"}}
FLOW_EDGES = {"outlet": {"style": "dashed", "tone": "lav", "label": "updates asset"},
              "sensor": {"style": "dotted", "tone": "muted", "label": "waits for (sensor)"},
              "lookup": {"style": "dotted", "tone": "muted", "label": "schema lookup"},
              "snapshot": {"style": "dashed", "label": "initial snapshot"}}
DBT_LAYERS = ("sources", "seeds", "snapshots", "staging", "intermediate", "marts", "semantic", "metrics", "saved_queries",
              "exposures")
CARD = {"1": "only-one", "0..1": "zero-one", "0..N": "zero-many", "1..N": "one-many"}
MM_LEFT = {"0..1": "|o", "1": "||", "0..N": "}o", "1..N": "}|"}
MM_RIGHT = {"0..1": "o|", "1": "||", "0..N": "o{", "1..N": "|{"}
HEAD_TONE = {"plain": "soft", "soft": "soft", "blue": "blue-bg", "teal": "teal", "amber": "amber", "lav": "lav",
             "green": "green-bg", "red": "red-bg"}
ER_CSS = ("".join(f"#S .er-hd.t-{t}{{fill:var(--dg-{v})}}" for t, v in HEAD_TONE.items())
          + "#S .er-div{stroke:var(--dg-ink);stroke-width:1}"
          f"#S .er-k{{font-family:{MONO};font-size:10px;font-weight:600;fill:var(--dg-muted)}}"
          f"#S .er-n{{font-family:{MONO};font-size:12px;fill:var(--dg-ink)}}#S .er-n.pk{{font-weight:600}}"
          f"#S .er-ty{{font-family:{MONO};font-size:11px;fill:var(--dg-muted)}}"
          "#S .er-more{font-size:11px;font-style:italic;fill:var(--dg-muted)}")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_") or "x"


def _plural(n, w):
    return f"{n} {w}" + ("" if n == 1 else "s")


# ---------- entity tables (er, star-schema) ----------
def _columns(ent):
    out = []
    for c in ent.get("columns") or []:
        if isinstance(c, str):  # "order_id bigint PK" or "customer_id bigint FK"
            p = c.split()
            iskey = lambda x: all(k in ("PK", "FK", "UK") for k in x.upper().split(",") if k)  # noqa: E731
            keys = [k for x in p[1:] if iskey(x) for k in x.upper().split(",") if k]
            c = {"name": p[0], "type": " ".join(x for x in p[1:] if not iskey(x)), "key": ",".join(keys)}
        out.append(c)
    return out


def _ent_layout(e, max_w):
    """Size and text rows of an entity table: header (name, sub), then one row per column (key, name, type)."""
    cols = _columns(e)
    kw = 36 if any(c.get("key") for c in cols) else 0
    tw = lambda s, z, b=False: core.text_width(s, z, True, b)  # noqa: E731
    need = [tw(e.get("label") or e["id"], 12.5, True) + 20, core.text_width(e.get("sub") or "", 11) + 20]
    for c in cols:
        need.append(8 + kw + tw(c["name"], 12, bool(c.get("key"))) + (16 + tw(c.get("type") or "", 11) if c.get("type") else 0) + 8)
    w = math.ceil(min(max_w, max(need + [150])))
    head = core.wrap(e.get("label") or e["id"], w - 20, 12.5, True, True)
    sub = core.wrap(e["sub"], w - 20, 11) if e.get("sub") else []
    hh = 8 + 17 * len(head) + 14 * len(sub) + 6
    rows, y = [], hh + 5
    for c in cols:
        names = core.wrap(c["name"], w - 16 - kw, 12, True, bool(c.get("key")))
        ty = c.get("type") or ""
        one = len(names) == 1 and (not ty or 8 + kw + tw(names[0], 12) + 16 + tw(ty, 11) + 8 <= w)
        lines = [(s, 8 + kw, y + 17 * i) for i, s in enumerate(names)]
        if ty and not one:
            lines.append((ty, 8 + kw, y + 17 * len(names)))
        rh = 17 * len(lines) + 2
        rows.append({"key": c.get("key") or "", "names": lines if one or not ty else lines[:-1],
                     "type": (ty, y, True) if ty and one else ((ty, y + 17 * len(names), False) if ty else None),
                     "pk": "PK" in (c.get("key") or "").upper(), "y": y})
        y += rh
    more = e.get("more")
    if more:
        rows.append({"more": f"+ {more} more columns", "y": y})
        y += 19
    h = y + 5 if rows else hh
    return {"w": w, "h": math.ceil(h), "head": head, "sub": sub, "hh": hh, "rows": rows, "kw": kw}


def _ent_draw(c, e, x, y, L):
    w, h, hh = L["w"], L["h"], L["hh"]
    core.node(c, {"id": e["id"], "label": "", "shape": "box", "dim": e.get("dim"), "tip": e.get("tip"),
                  "free": e.get("free")}, x, y, w, h)
    tone = e.get("tone") or "plain"
    out, lines = [f'<g{" class=dg-dim" if e.get("dim") else ""}>'], []
    F = core.F
    if L["rows"]:
        out.append(f'<path class="er-hd t-{tone}" d="M{F(x + .6)},{F(y + hh)} V{F(y + 3.6)} Q{F(x + .6)},{F(y + .6)} '
                   f'{F(x + 3.6)},{F(y + .6)} H{F(x + w - 3.6)} Q{F(x + w - .6)},{F(y + .6)} {F(x + w - .6)},{F(y + 3.6)} '
                   f'V{F(y + hh)} Z"/><path class="er-div" d="M{F(x)},{F(y + hh)} H{F(x + w)}"/>')
    else:
        out.append(f'<rect class="er-hd t-{tone}" x="{F(x + .6)}" y="{F(y + .6)}" width="{F(w - 1.2)}" height="{F(h - 1.2)}" rx="2.5"/>')

    def put(s, tx, ty, cls, size, lh, anchor="start", mono=True, bold=False):
        lw = core.text_width(s, size, mono, bold)
        out.append(f'<text class="{cls}" x="{F(tx)}" y="{F(ty + (lh - size) / 2 + size * .78)}" text-anchor="{anchor}">'
                   f'{core.esc(s)}</text>')
        lines.append({"text": s, "x": tx - (lw if anchor == "end" else lw / 2 if anchor == "middle" else 0),
                      "y": ty, "w": lw, "h": lh})

    ty = y + 8
    for s in L["head"]:
        put(s, x + w / 2, ty, "dg-lm", 12.5, 17, "middle", bold=True)
        ty += 17
    for s in L["sub"]:
        put(s, x + w / 2, ty, "dg-s", 11, 14, "middle", mono=False)
        ty += 14
    for r in L["rows"]:
        if r.get("more"):
            put(r["more"], x + 8, y + r["y"], "er-more", 11, 17, mono=False)
            continue
        if r["key"]:
            put(r["key"], x + 8, y + r["y"], "er-k", 10, 17, bold=True)
        for s, ox, oy in r["names"]:
            put(s, x + ox, y + oy, "er-n pk" if r["pk"] else "er-n", 12, 17, bold=r["pk"])
        if r["type"]:
            s, oy, right = r["type"]
            if right:
                put(s, x + w - 8, y + oy, "er-ty", 11, 17, "end")
            else:
                put(s, x + 8 + L["kw"], y + oy, "er-ty", 11, 17)
    out.append("</g>")
    core.add(c, "".join(out), 2)
    g = c["geo"]["nodes"][-1]
    g.update(text=e.get("label") or e["id"], lines=lines, inner=[x + 1, y + 1, w - 2, h - 2])


def _card(v, default):
    return CARD.get(str(v or default), "zero-many")


def _rel_edge(r):
    a, b = (r.get("card") or "1:0..N").split(":")
    return {"from": r["from"], "to": r["to"], "label": r.get("label"), "tail": _card(a, "1"), "head": _card(b, "0..N"),
            "style": "dashed" if r.get("identifying") is False else "solid", "dim": r.get("dim"),
            "from_side": r.get("from_side"), "to_side": r.get("to_side")}


def _check_entities(ents, where="entities"):
    err, seen = [], set()
    if not ents:
        err.append(f"{where}: at least one entity {{id, label, columns}}")
    for e in ents:
        if not e.get("id"):
            err.append(f"{where}: entity without id")
            continue
        if e["id"] in seen:
            err.append(f"entity {e['id']}: duplicate id")
        seen.add(e["id"])
        if (e.get("tone") or "plain") not in HEAD_TONE:
            err.append(f"entity {e['id']}: tone '{e['tone']}' is not one of {', '.join(HEAD_TONE)}")
        for col in _columns(e):
            if not col.get("name"):
                err.append(f"entity {e['id']}: column without name")
            for k in filter(None, str(col.get("key") or "").replace(" ", "").split(",")):
                if k.upper() not in ("PK", "FK", "UK"):
                    err.append(f"entity {e['id']}.{col.get('name')}: key '{k}' is not PK, FK or UK")
    return err, seen


def _check_card(r):
    parts = str(r.get("card") or "1:0..N").split(":")
    if len(parts) != 2 or any(p not in CARD for p in parts):
        return [f"relation {r.get('from')} -> {r.get('to')}: card '{r.get('card')}' must be <from>:<to>, each one of "
                f"{', '.join(CARD)} (e.g. '1:0..N')"]
    return []


def validate_er(spec):
    err, ids = _check_entities(spec.get("entities") or [])
    areas = {a.get("id") for a in spec.get("areas") or []}
    for e in spec.get("entities") or []:
        if e.get("area") and e["area"] not in areas:
            err.append(f"entity {e.get('id')}: area '{e['area']}' is not in areas")
    for r in spec.get("relations") or []:
        for k in ("from", "to"):
            if r.get(k) not in ids:
                err.append(f"relation {r.get('from')} -> {r.get('to')}: unknown entity '{r.get(k)}'")
        err += _check_card(r)
        if len(str(r.get("label") or "")) > 36:
            err.append(f"relation {r.get('from')} -> {r.get('to')}: label over 36 characters")
    if spec.get("direction", "LR") not in ("LR", "TB"):
        err.append("direction: LR or TB")
    return err


def svg_er(spec, core):
    ents = spec["entities"]
    L = {e["id"]: _ent_layout(e, spec.get("max_w", 260)) for e in ents}
    areas = {a["id"]: a["label"] for a in spec.get("areas") or []}
    edges = [_rel_edge(r) for r in spec.get("relations") or []]
    items = [{"id": e["id"], "w": L[e["id"]]["w"], "h": L[e["id"]]["h"], "group": e.get("area"), "rank": e.get("rank")}
             for e in ents]
    lab = max([core.text_width(str(e["label"]), 11, True) + 10 for e in edges if e.get("label")] + [0])
    gap = max(96, lab + 64)
    # left to right, then top-down, then top-down with one area per row; a field the author set is kept
    tries = [(d, al) for d in ([spec["direction"]] if spec.get("direction") else ["LR", "TB"])
             for al in ([spec["area_layout"]] if spec.get("area_layout") else ["auto"] + (["columns"] if d == "TB" and areas else []))]
    widths = []

    def make(d, al, fan=False):
        lay = core.layout_layered(items, edges, d, areas, gap=gap, cross_gap=40 if d == "TB" else None, group_layout=al)
        if lay["width"] > core.MAX_W:
            widths.append(int(lay["width"]))
            raise core.LayoutError("too wide")
        c = core.canvas(spec)
        for g, r in lay["groups"].items():
            core.container(c, g, areas[g], *r, members=[e["id"] for e in ents if e.get("area") == g], label_w=lay.get("label_w"))
        for e in ents:
            _ent_draw(c, e, *lay["pos"][e["id"]][:2], L[e["id"]])
        ee = [dict(x) for x in edges]
        if fan:  # a table with 3+ relations sends the ones to tables beside it out of its sides, so each line has room for its label
            P = lay["pos"]
            for x in ee:
                if sum(1 for y in ee if x["from"] in (y["from"], y["to"])) >= 3 and not x.get("from_side"):
                    a, b = P[x["from"]], P[x["to"]]
                    m = b[0] + b[2] / 2 if d == "TB" else b[1] + b[3] / 2
                    lo, hi = (a[0], a[0] + a[2]) if d == "TB" else (a[1], a[1] + a[3])
                    if m < lo or m > hi:
                        x["from_side"] = ("left" if m < lo else "right") if d == "TB" else ("top" if m < lo else "bottom")
        core.route(c, ee, d, spread=True)  # crow's feet need their own port each, never one shared trunk
        body, geo = core.finish(c)
        geo["direction"] = d
        return body, geo, [ER_CSS]
    try:
        return _pick([[(lambda d=d, al=al, f=f: make(d, al, f), None) for f in (False, True)] for d, al in tries])
    except core.LayoutError:
        fixes = ["split by area into one diagram each (a header-only er of all tables as the overview)",
                 "list key columns only (more: n)"]
        if not spec.get("direction"):
            fixes.append("set direction TB")
        raise core.LayoutError(f"canvas would be {min(widths)}px wide (max {core.MAX_W}): " + ", ".join(fixes)) from None


def _mm_type(t):
    t = re.sub(r"[^A-Za-z0-9_\-()\[\]]", "_", str(t or "string"))
    return t if t[:1].isalpha() else "t_" + t


def _mm_entity(e):
    name = re.sub(r"\W", "_", str(e.get("label") or e["id"]))
    out = [f"  {name} {{"] if e.get("columns") else []
    for c in _columns(e):
        keys = ", ".join(k for k in str(c.get("key") or "").replace(" ", "").upper().split(",") if k)
        out.append(f"    {_mm_type(c.get('type'))} {re.sub(r'[^A-Za-z0-9_-]', '_', c['name'])}" + (f" {keys}" if keys else ""))
    return name, out + (["  }"] if out else [])


def _mm_er(spec, ents, rels, direction=None):
    out = core.mermaid_head(spec, "erDiagram")
    if direction == "TB":
        out.append("  direction TB")
    names = {}
    for e in ents:
        names[e["id"]], block = _mm_entity(e)
        out += block
    for r in rels:
        a, b = (r.get("card") or "1:0..N").split(":")
        line = "--" if r.get("identifying") is not False else ".."
        out.append(f"  {names[r['from']]} {MM_LEFT[a]}{line}{MM_RIGHT[b]} {names[r['to']]} : {core.mm_text(r.get('label') or '')}")
    for a in spec.get("areas") or []:
        out.append(f"  %% area {a['label']}: " + ", ".join(names[e["id"]] for e in ents if e.get("area") == a["id"]))
    return "\n".join(out) + "\n"


def mermaid_er(spec):
    return _mm_er(spec, spec["entities"], spec.get("relations") or [], _drawn_direction(svg_er, spec))


# ---------- star / snowflake schema ----------
def _star_rels(spec):
    """Relations dimension -> fact (or outrigger -> its dimension) with the 'one' end at the dimension."""
    fact = spec["fact"]["id"]
    return [{"from": d["id"], "to": d.get("parent") or fact, "card": d.get("card") or "1:0..N", "label": d.get("via"),
             "identifying": d.get("identifying")} for d in spec["dimensions"]]


def validate_star(spec):
    f = spec.get("fact")
    if not isinstance(f, dict):
        return ["fact: one entity {id, label, columns}"]
    dims = spec.get("dimensions") or []
    err, ids = _check_entities([f] + dims, "fact/dimensions")
    if not dims:
        err.append("dimensions: at least one")
    for d in dims:
        if d.get("parent") and (d["parent"] not in ids or d["parent"] == f["id"]):
            err.append(f"dimension {d.get('id')}: parent '{d['parent']}' must be another dimension (snowflake outrigger)")
        if d.get("side") not in (None, "left", "right"):
            err.append(f"dimension {d.get('id')}: side left or right")
        err += _check_card(d)
    return err


def svg_star(spec, core):
    c = core.canvas(spec)
    mw = spec.get("max_w", 200)
    fact = dict(spec["fact"], tone=spec["fact"].get("tone") or "blue")
    dims = [dict(d, tone=d.get("tone") or ("soft" if d.get("parent") else "teal")) for d in spec["dimensions"]]
    D = {d["id"]: d for d in dims}
    L = {e["id"]: _ent_layout(e, mw) for e in [fact] + dims}
    side, k = {}, 0
    for d in dims:
        if not d.get("parent"):
            side[d["id"]] = d.get("side") or ("left" if k % 2 == 0 else "right")
            k += 1
    kids = {}
    for d in dims:
        if d.get("parent"):
            kids.setdefault(d["parent"], []).append(d["id"])

    def chain(i):  # a dimension, then its outriggers stacked under it
        return [i] + [x for kid in kids.get(i, []) for x in chain(kid)]
    col = {s_: [x for d in dims if side.get(d["id"]) == s_ for x in chain(d["id"])] for s_ in ("left", "right")}
    for s_ in col:
        for i in col[s_]:
            side[i] = s_
    gap, ogap = 24, 64  # an outrigger needs room for two crow's-foot ends between it and its parent

    def height(ids):
        return sum(L[i]["h"] for i in ids) + sum(ogap if D[i].get("parent") else gap for i in ids[1:])

    def gap_to_fact(ids):  # wide enough for the 'via' labels of the relations that cross it
        labs = [core.text_width(str(D[i]["via"]), 11, True) + 10 for i in ids if D[i].get("via") and not D[i].get("parent")]
        return max([84] + [w + 64 for w in labs])
    cw = {s_: max([L[i]["w"] for i in ids] or [0]) for s_, ids in col.items()}
    fw = L[fact["id"]]["w"]
    xl = core.MARGIN
    xf = xl + (cw["left"] + gap_to_fact(col["left"]) if col["left"] else 0)
    xr = xf + fw + gap_to_fact(col["right"])
    W = (xr + cw["right"] if col["right"] else xf + fw) + core.MARGIN
    if W > core.MAX_W:
        raise core.LayoutError(f"canvas would be {int(W)}px wide (max {core.MAX_W}): shorter via labels (the join key "
                               f"name only), max_w below {mw} (long names wrap), list key columns only (more: n), "
                               "or put all dimensions on one side")
    H = max(height(col["left"]), height(col["right"]), L[fact["id"]]["h"])
    pos = {fact["id"]: (xf, core.MARGIN + (H - L[fact["id"]]["h"]) / 2)}
    for s_, x0 in (("left", xl), ("right", xr)):
        ids = col[s_]
        y = core.MARGIN + (H - height(ids)) / 2
        for j, i in enumerate(ids):
            if j:
                y += ogap if D[i].get("parent") else gap
            pos[i] = (x0 + (cw[s_] - L[i]["w"]) / 2, y)
            y += L[i]["h"]
    for e in [fact] + dims:
        _ent_draw(c, e, *pos[e["id"]], L[e["id"]])
    edges = []
    for r, d in zip(_star_rels(spec), dims):
        e = _rel_edge(r)
        if d.get("parent"):
            e["from_side"], e["to_side"] = "top", "bottom"
        else:
            e["from_side"], e["to_side"] = ("right", "left") if side[d["id"]] == "left" else ("left", "right")
        edges.append(e)
    core.route(c, edges, "LR", spread=True)
    body, geo = core.finish(c)
    return body, geo, [ER_CSS]


def mermaid_star(spec):
    return _mm_er(spec, [spec["fact"]] + spec["dimensions"], _star_rels(spec))


# ---------- node-edge helpers ----------
_SEL = re.compile(r"^(@)?(?:(\d*)\+)?([^+@\s]+?)(?:\+(\d*))?$")


def _reach(start, adj, depth):
    seen, front, d = {start}, {start}, 0
    while front and (depth is None or d < depth):
        front = {v for u in front for v in adj.get(u, ())} - seen
        seen |= front
        d += 1
    return seen


def _adj(edges):
    down, up = {}, {}
    for e in edges:
        down.setdefault(e["from"], []).append(e["to"])
        up.setdefault(e["to"], []).append(e["from"])
    return down, up


def select_ids(expr, ids, edges):
    """dbt graph operators on node ids: 'x', '+x', 'x+', '2+x+1', '@x'; space-separated terms are a union."""
    down, up = _adj(edges)
    keep = set()
    for term in str(expr).split():
        m = _SEL.match(term)
        at, a, name, b = m.group(1), m.group(2), m.group(3), m.group(4)
        hit = {name}
        if at:
            ds = _reach(name, down, None)
            hit = set(ds).union(*[_reach(v, up, None) for v in ds])
        else:
            if a is not None:
                hit |= _reach(name, up, int(a) if a else None)
            if b is not None:
                hit |= _reach(name, down, int(b) if b else None)
        keep |= hit & set(ids)
    return keep


def _check_select(spec, ids):
    err = []
    for term in str(spec.get("select") or "").split():
        m = _SEL.match(term)
        if not m:
            err.append(f"select '{term}': use dbt graph operators - name, +name, name+, 2+name+1, @name")
        elif m.group(3) not in ids:
            err.append(f"select '{term}': no node '{m.group(3)}'")
    if spec.get("impact") and spec["impact"] not in ids:
        err.append(f"impact: no node '{spec['impact']}'")
    if spec.get("impact_dir", "down") not in ("down", "up"):
        err.append("impact_dir: down (what breaks) or up (what feeds it)")
    return err


def _focus(spec, nodes, edges, groups):
    """Apply select (keep a sub-graph) and impact (dim what is not affected) to mapped nodes and edges."""
    if spec.get("select"):
        keep = select_ids(spec["select"], [n["id"] for n in nodes], edges)
        nodes = [n for n in nodes if n["id"] in keep]
        edges = [e for e in edges if e["from"] in keep and e["to"] in keep]
        used = {n.get("group") for n in nodes}
        groups = [g for g in groups if g["id"] in used]
    if spec.get("impact"):
        down, up = _adj(edges)
        src, dn = spec["impact"], spec.get("impact_dir", "down") == "down"
        hit = _reach(src, down if dn else up, None)
        for n in nodes:
            if n["id"] not in hit:
                n["dim"] = True
            elif n["id"] == src:
                n.update(tone="red", strong=True, kind=None) if dn else n.update(strong=True)
        for e in edges:
            if e["from"] in hit and e["to"] in hit:
                if dn:
                    e["tone"] = "red"
            else:
                e["dim"] = True
    return nodes, edges, groups


def _kinds(s, km):
    if s.get("style") == "dbt":  # dbt look: every node a pill filled with its kind colour
        return {k: {x: v for x, v in m.items() if x not in ("shape", "dashed")} for k, m in km.items()}
    return km


def _spec(spec, style, **dflt):
    s = dict(spec)
    s["style"] = spec.get("style") or style
    for k, v in dflt.items():
        if k == "edge_kinds":
            s[k] = dict(v, **(spec.get(k) or {}))
        elif spec.get(k) is None:
            s[k] = v
    return s


def _part_kinds(edges, tb, alt=0):
    """Edges of different kinds leaving (or reaching) one box get their own side, so a dashed asset trigger never
    shares a trunk line with a solid dependency: the less common kind leaves at the bottom and arrives at the top.
    alt 1: the opposite side; alt 2, 3: the more common kind moves instead (the layout picks the cleanest)."""
    for end, side in (("from", "right" if tb else "bottom"), ("to", "left" if tb else "top")):
        if alt % 2:
            side = {"right": "left", "left": "right", "bottom": "top", "top": "bottom"}[side]
        by = {}
        for x in edges:
            by.setdefault(x[end], []).append(x)
        for lst in by.values():
            ks = [x.get("kind") or "" for x in lst]
            if len(set(ks)) > 1:
                rank = lambda k: (ks.count(k), k in ("", "on_succeeded"))  # noqa: E731
                main = sorted(sorted(set(ks)), key=rank, reverse=True)[1 if alt >= 2 else 0]
                for x in lst:
                    if (x.get("kind") or "") != main and not x.get(end + "_side"):
                        x[end + "_side"] = side
                        x["_parted"] = True
    return edges


def _clashes(geo, styled):
    """Pairs of arrows that touch one box, look different (kind, style, tone) and still run along one line: the
    reader would take one meaning for the other."""
    look = [(e.get("kind"), e.get("style") or "solid", e.get("tone")) for e in styled]
    ge = geo.get("edges") or []
    return [f"{ge[i]['from']} -> {ge[i]['to']}" for i in range(len(ge)) for j in range(i + 1, len(ge))
            if {ge[i]["from"], ge[i]["to"]} & {ge[j]["from"], ge[j]["to"]} and look[i] != look[j]
            and core.checker._shared(ge[i], ge[j])]


def crossings(geo):
    """Number of points where two arrows cross at a right angle (not at a shared end)."""
    segs = [(k, p, q) for k, e in enumerate(geo.get("edges") or []) for p, q in zip(e["points"], e["points"][1:])]
    n = 0
    for i, (k, p, q) in enumerate(segs):
        for m, r, t in segs[i + 1:]:
            if m == k:
                continue
            h, v = ((p, q), (r, t)) if abs(p[1] - q[1]) < .5 else ((r, t), (p, q))
            if abs(h[0][1] - h[1][1]) > .5 or abs(v[0][0] - v[1][0]) > .5:
                continue
            x, y = v[0][0], h[0][1]
            if min(h[0][0], h[1][0]) + 1 < x < max(h[0][0], h[1][0]) - 1 and                     min(v[0][1], v[1][1]) + 1 < y < max(v[0][1], v[1][1]) - 1:
                n += 1
    return n


def _pick(groups):
    """groups: lists of (thunk -> (body, geo[, css]), styled edges or None), one list per layout try in order. The
    first try with a result free of LAYOUT problems and clashes wins (its variant with the fewest crossings); else
    the result with the fewest problems. LayoutError only when every build raised one."""
    best, first = None, None
    for builds in groups:
        clean = []
        for make, styled in builds:
            try:
                out = make()
            except core.LayoutError as ex:
                first = first or ex
                break  # too wide: the side variants of this try are no narrower
            bad = 100 * len(_clashes(out[1], styled) if styled is not None else []) + len(core.checker.check(out[1])[0])
            if not bad:
                clean.append((crossings(out[1]), len(clean), out))
            elif best is None or bad < best[0]:
                best = (bad, out)
        if clean:
            return min(clean, key=lambda x: x[:2])[2]
    if best is None:
        raise first
    return best[1]  # the build reports its LAYOUT lines


def _validate_graph(m, spec, kinds=None, styles=_STYLE_OK):
    """m = (s, nodes, edges, groups, kinds, states) from a mapper; checks ids, ends, style fields and kind names."""
    s, nodes, edges, groups, km, _ = m
    tmp = dict(s, nodes=nodes, edges=edges, groups=groups)
    err = core.check_graph(tmp) + core.check_style(tmp)
    if s.get("style") not in styles:
        err.append(f"style '{s.get('style')}': this type supports {', '.join(styles)}")
    if kinds is not None:
        known = set(kinds) | set(spec.get("kinds") or {})
        for n in nodes:
            if n.get("kind") and n["kind"] not in known:
                err.append(f"node {n['id']}: kind '{n['kind']}' is not one of {', '.join(sorted(known))}")
    return err


def _dir(out, d):
    out[1].setdefault("direction", d or "LR")
    return out


def _drawn_direction(svg, spec):
    """The direction the SVG layout ended up with (a too-wide picture falls back to TB), so Mermaid matches it."""
    try:
        return svg(spec, core)[1].get("direction")
    except core.LayoutError:
        return None


def _graph_type(mapper, kinds_ok=None, styles=_STYLE_OK, pre=None, spread_tb=False, svg_fn=None):
    """svg / mermaid / validate for a type that maps its spec onto the base graph(); svg_fn replaces the svg."""
    def svg(spec, core):
        s, n, e, g, k, st = mapper(spec)
        tries = [s]  # fallbacks the author did not rule out: groups as bands, then top-down
        if not spec.get("group_layout") and s.get("group_layout") == "columns":
            tries.append(dict(s, group_layout="bands"))
        if not spec.get("direction") and s.get("direction") != "TB":  # LR first, so sides are set for LR
            tries = [dict(t, direction="LR") for t in tries] + [dict(t, direction="TB") for t in tries]
        groups = []
        for t in tries:
            tb, builds = t.get("direction") == "TB", []
            for alt in range(4):
                ee = _part_kinds([dict(x, from_side=None) if tb and x.get("_side") else dict(x) for x in e], tb, alt)
                fan = spread_tb and tb  # top-down fan-in: each arrow its own slot on the target's top edge
                builds.append((lambda t=t, ee=ee, fan=fan: _dir(core.graph(t, n, ee, g, kinds=k, states=st, spread=fan),
                                                                t.get("direction")),
                               core.style_graph(t, n, ee, g, k, st)["edges"]))
                if not any(x.get("_parted") for x in ee):
                    break  # no edge was moved to a side: the variants are the same picture
            groups.append(builds)
        return _pick(groups)
    svg = svg_fn or svg

    def mermaid(spec):
        s, n, e, g, k, st = mapper(spec)
        d = _drawn_direction(svg, spec)
        return core.mermaid_graph(dict(s, direction=d) if d else s, n, e, g, kinds=k, states=st)

    def validate(spec):
        err = pre(spec) if pre else []
        if err:
            return err
        m = mapper(spec, raw=True)
        err = _validate_graph(m, spec, kinds_ok, styles)
        return err + _check_select(spec, [n["id"] for n in m[1]])
    return {"svg": svg, "mermaid": mermaid, "validate": validate}


def _need(spec, key, what):
    v = spec.get(key)
    if not isinstance(v, list) or not v:
        return [f"{key}: a list of {what}"]
    bad = [x for x in v if not isinstance(x, dict) or not x.get("id")]
    return [f"{key}: every item needs an id ({bad[0]})"] if bad else []


def _edges(spec, nodes, field="depends_on"):
    """spec edges plus per-node dependency lists (dbt depends_on, Airflow upstream)."""
    out = [dict(e) for e in spec.get("edges") or []]
    for n in nodes:
        for d in n.get(field) or []:
            out.append({"from": d, "to": n["id"]})
    return out


# ---------- lineage (generic) ----------
def map_lineage(spec, raw=False):
    s = _spec(spec, "dbt")
    nodes = [dict(n) for n in spec.get("nodes") or []]
    edges, groups = _edges(spec, nodes), [dict(g) for g in spec.get("groups") or []]
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
    if s["style"] == "airflow" and nodes and all(n.get("state") for n in nodes):
        return s, nodes, edges, groups, {}, None  # the state colours every box: a kind swatch would show empty
    return s, nodes, edges, groups, _kinds(s, dict(core.DBT_KINDS, **LIN_KINDS)), None


# ---------- dbt lineage ----------
def map_dbt(spec, raw=False):
    s = _spec(spec, "dbt", max_w=200 if spec.get("view") == "overview" else 128)
    nodes = []
    for n in spec.get("nodes") or []:
        m = dict(n, kind=n.get("resource_type") or n.get("kind") or "model", group=n.get("layer") or n.get("group"))
        m["label"] = n.get("label") or n.get("name") or n.get("id")
        nodes.append(m)
    groups = [dict(g) for g in spec.get("layers") or []]
    if not groups:
        seen = list(dict.fromkeys(n["group"] for n in nodes if n.get("group")))
        groups = [{"id": g, "label": g} for g in sorted(seen, key=lambda g: (DBT_LAYERS.index(g) if g in DBT_LAYERS
                                                                              else len(DBT_LAYERS), seen.index(g)))]
    edges = _edges(spec, nodes)
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
    if s.get("view") == "overview":  # a layer is a rounded box (resources stay pills), one count per line
        for g in groups:
            cnt = {}
            for n in nodes:
                if n.get("group") == g["id"]:
                    cnt[n["kind"]] = cnt.get(n["kind"], 0) + 1
            g.setdefault("shape", "rounded")
            if len(cnt) == 1 and "model" not in cnt:  # sources, seeds, exposures: a resource type, not a folder
                g.setdefault("tag", core.DBT_KINDS.get(next(iter(cnt)), {}).get("label", next(iter(cnt))))
            g.setdefault("sub", "\n".join(_plural(v, core.DBT_KINDS.get(k, {}).get("label", k))
                                          for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])))
    return s, nodes, edges, groups, dict(core.DBT_KINDS), None


# ---------- Airflow DAG ----------
def map_airflow(spec, raw=False):
    s = _spec(spec, "airflow", edge_kinds=FLOW_EDGES, group_layout="columns")
    nodes, assets, edges = [], {}, []
    run = any(t.get("state") for t in spec.get("tasks") or [])
    for t in spec.get("tasks") or []:
        n = dict(t, label=t.get("label") or t["id"])
        if run and t.get("state") in (None, "none"):
            n["state"] = "no_status"  # in a run, a task without a state shows as "no status"
        if t.get("trigger_rule") and t["trigger_rule"] != "all_success":
            n["sub"] = " · ".join(x for x in (t.get("sub"), "rule " + t["trigger_rule"]) if x)
        nodes.append(n)
        for a in t.get("outlets") or []:
            aid = "asset_" + _slug(a)
            assets.setdefault(aid, {"id": aid, "label": a, "tag": "asset", "shape": "box", "tone": "lav", "dashed": True,
                                    "group": t.get("group") if spec.get("assets_in_group") else None})
            edges.append({"from": t["id"], "to": aid, "kind": "outlet", "from_side": "top", "_side": True})
    edges = _edges(spec, nodes, "upstream") + edges
    groups = [dict(g) for g in spec.get("groups") or []]
    nodes += list(assets.values())
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
    return s, nodes, edges, groups, None, NO_STATUS


def pre_airflow(spec):
    err = _need(spec, "tasks", "tasks {id, operator, state, group, upstream}")
    for g in spec.get("groups") or []:
        if g.get("parent"):
            err.append(f"group {g.get('id')}: nested task groups are not drawn - flatten it or collapse the outer group")
    for t in spec.get("tasks") or []:
        if t.get("state") and t["state"] not in core.AIRFLOW_STATES and t["state"] not in (spec.get("states") or {}):
            err.append(f"task {t.get('id')}: state '{t['state']}' is not an Airflow task state ({', '.join(core.AIRFLOW_STATES)})")
    return err


# ---------- Airflow multi-DAG overview ----------
def _assets(sch):
    if isinstance(sch, list):
        return list(sch), "all"
    if isinstance(sch, dict):
        return list(sch.get("any") or sch.get("all") or []), "any" if sch.get("any") else "all"
    return [], None


def map_dags(spec, raw=False):
    s = _spec(spec, "airflow", edge_kinds=FLOW_EDGES)
    dags = spec.get("dags") or []
    prod = {}
    for d in dags:
        for a in d.get("outlets") or []:
            prod.setdefault(a, []).append(d["id"])
    nodes, edges, ext = [], {}, {}
    for d in dags:
        names, mode = _assets(d.get("schedule"))
        if mode:
            when = "on asset" if len(names) == 1 else (f"on {len(names)} assets" if mode == "all" else "on any asset")
        else:
            when = str(d.get("schedule")) if d.get("schedule") else "manual"
        sub = [x for x in (_plural(d["tasks"], "task") if d.get("tasks") else None, d.get("sub")) if x]
        nodes.append({"id": d["id"], "label": d.get("label") or d["id"], "tag": f"DAG · {when}", "state": d.get("state"),
                      "sub": " · ".join(sub), "group": d.get("group")})
        for a in names:
            src = prod.get(a) or []
            if spec.get("show_assets") or not src:
                aid = "asset_" + _slug(a)
                ext.setdefault(aid, {"id": aid, "label": a, "tag": "asset" if src else "asset · external",
                                     "shape": "box", "tone": "lav", "dashed": True})
                for p in src:
                    edges.setdefault((p, aid, "outlet"), [])
                edges.setdefault((aid, d["id"], "asset"), [])
            else:
                for p in src:
                    edges.setdefault((p, d["id"], "asset"), []).append(a)
    out = []
    for (a, b, k), ls in edges.items():
        lab = ", ".join(ls)
        out.append({"from": a, "to": b, "kind": k, "label": lab if len(lab) <= 36 else _plural(len(ls), "asset")})
    out += [dict(e) for e in spec.get("links") or []]
    nodes += list(ext.values())
    groups = [dict(g) for g in spec.get("groups") or []]
    if not raw:
        nodes, out, groups = _focus(spec, nodes, out, groups)
    return s, nodes, out, groups, None, None


def pre_dags(spec):
    err = _need(spec, "dags", "DAGs {id, schedule, tasks, state, outlets}")
    for d in spec.get("dags") or []:
        if d.get("state") and d["state"] not in core.AIRFLOW_STATES:
            err.append(f"dag {d.get('id')}: state '{d['state']}' - use a DAG run state: queued, running, success, failed")
    for e in spec.get("links") or []:
        if e.get("kind") not in (None, "asset", "trigger", "sensor"):
            err.append(f"link {e.get('from')} -> {e.get('to')}: kind asset, trigger or sensor")
    return err


# ---------- data flow diagram ----------
def map_dfd(spec, raw=False):
    s = _spec(spec, "plain", legend=False)
    nodes = []
    for n in spec.get("nodes") or []:
        m = dict(n, kind=n.get("role"))
        if n.get("ref") and not n.get("tag"):
            m["tag"] = n["ref"]
        if n.get("role") == "external":
            m.setdefault("strong", True)
        nodes.append(m)
    return s, nodes, [dict(e) for e in spec.get("edges") or []], [dict(g) for g in spec.get("groups") or []], DFD_KINDS, None


def pre_dfd(spec):
    err = _need(spec, "nodes", "nodes {id, label, role: external|process|store, ref}")
    role = {n.get("id"): n.get("role") for n in spec.get("nodes") or []}
    for n in spec.get("nodes") or []:
        if n.get("role") not in DFD_KINDS:
            err.append(f"node {n.get('id')}: role external, process or store")
    for e in spec.get("edges") or []:
        if not e.get("label"):
            err.append(f"flow {e.get('from')} -> {e.get('to')}: name the data it carries (label)")
        if "process" not in (role.get(e.get("from")), role.get(e.get("to"))):
            err.append(f"flow {e.get('from')} -> {e.get('to')}: every data flow starts or ends at a process")
    return err


def _graph_spread(spec, nodes, edges, groups, kinds, states, direction):
    """core.graph() with one port per arrow: every data flow keeps its own arrowhead."""
    tall = direction == "TB" and any(e.get("label") for e in edges)  # room for flow names to stack
    return core.graph(spec, nodes, edges, groups, kinds, states, direction=direction, spread=True,
                      gap=84 if tall else None)


def _dfd_grid(core, s, nodes, edges, kinds):
    """Level-1 grid: processes in one middle row in spec order, externals above and stores below, each under or over
    the process it exchanges most flows with, so a process and its store face each other and the two flows of a pair
    run side by side on their own ports."""
    st = core.style_graph(s, nodes, edges, [], kinds, None)
    c = core.canvas(s)
    sized = {n["id"]: (n, w, h) for n, w, h in core._sized(s, st["nodes"])}
    role = {x["id"]: x.get("role") for x in nodes}
    procs = [x["id"] for x in nodes if role[x["id"]] == "process"]
    lab = max([core.text_width(str(e["label"]), 11, True) + 10 for e in edges if e.get("label")] + [40])
    pitch = max(sized[p][1] for p in procs) + lab + 48
    cx = {p: i * pitch for i, p in enumerate(procs)}
    rows = {0: [], 2: []}
    for x in nodes:
        if role[x["id"]] != "process":
            ends = [o for e in edges for a, o in ((e["from"], e["to"]), (e["to"], e["from"])) if a == x["id"] and o in cx]
            home = max(procs, key=lambda p: (ends.count(p), -procs.index(p)))  # the process it trades most flows with
            rows[0 if role[x["id"]] == "external" else 2].append((cx[home], x["id"]))
    for r, lst in rows.items():
        lst.sort()
        if lst:
            for (_, i), v in zip(lst, core._pav([d for d, _ in lst], [sized[i][1] for _, i in lst], lab + 24, -1e9, 1e9)):
                cx[i] = v
    rh = {r: max([sized[i][2] for i in ids] or [0]) for r, ids in
          ((0, [i for _, i in rows[0]]), (1, procs), (2, [i for _, i in rows[2]]))}
    band = {0: 0, 1: 0}  # flows crossing the gap below row 0 and below row 1: each needs room for its name
    for e in edges:
        rs = {role.get(e["from"]), role.get(e["to"])}
        if "external" in rs:
            band[0] += 1
        elif "store" in rs:
            band[1] += 1
    y, ry = core.MARGIN, {}
    for r in (0, 1, 2):
        if rh[r]:
            ry[r] = y
            y += rh[r] + max(96, 40 + 26 * band.get(r, 0))
    x0 = core.MARGIN + lab / 2 - min(cx[i] - sized[i][1] / 2 for i in cx)  # room for a flow name beside the outer line
    if max(cx[i] + sized[i][1] / 2 for i in cx) + x0 + core.MARGIN > core.MAX_W:
        raise core.LayoutError("grid too wide")
    for i, (n, w, h) in sized.items():
        r = 1 if role[i] == "process" else 0 if role[i] == "external" else 2
        core.node(c, n, x0 + cx[i] - w / 2, ry[r] + (rh[r] - h) / 2, w, h)
    face = {"external": ("bottom", "top"), "store": ("top", "bottom")}  # (its side, the process's side)
    for e in st["edges"]:  # rows face each other: no flow enters a store through its open ends
        for me, other in (("from", "to"), ("to", "from")):
            if role.get(e[me]) in face and role.get(e[other]) == "process":
                e.setdefault(me + "_side", face[role[e[me]]][0])
                e.setdefault(other + "_side", face[role[e[me]]][1])
    core.route(c, st["edges"], "TB", spread=True)
    core.legend(c, st["legend"])
    return core.finish(c)


def svg_dfd(spec, core):
    s, n, e, g, k, st = map_dfd(spec)
    tries = [spec["direction"]] if spec.get("direction") else ["LR", "grid", "TB"]
    builds = []
    for d in tries:
        if d == "grid":
            if not g and sum(1 for x in n if x.get("role") == "process") > 1:
                builds.append([(lambda: _dfd_grid(core, s, n, e, k), None)])
        else:
            builds.append([(lambda d=d: _graph_spread(s, n, e, g, k, st, d), None)])
    body, geo = _pick(builds)[:2]
    stores = {x["id"] for x in n if x.get("role") == "store"}
    css, r = [], 3  # store = two parallel lines: dash the rect stroke so only top and bottom show
    arc = math.pi * r / 2
    for b in geo["nodes"]:
        if b["id"] in stores:
            css.append(f'#S g[data-id="{b["id"]}"]>.dg-sh{{stroke-dasharray:{b["w"] - 2 * r:.1f} {2 * arc + b["h"] - 2 * r:.1f};'
                       'stroke-width:1.6}')
    return body, geo, css


# ---------- medallion / layers ----------
def map_medallion(spec, raw=False):
    s = _spec(spec, "plain", group_layout="columns")
    groups = [{"id": l["id"], "label": " · ".join(x for x in (l.get("label") or l["id"], l.get("sub")) if x),
               "tone": l.get("tone"), "tag": l.get("tag")} for l in spec.get("layers") or []]
    nodes = [dict(n, group=n.get("layer") or n.get("group")) for n in spec.get("nodes") or []]
    edges = _edges(spec, nodes)
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
    return s, nodes, edges, groups, _kinds(s, dict(core.DBT_KINDS, **LIN_KINDS)), None


def pre_medallion(spec):
    return _need(spec, "layers", "layers {id, label, sub}") + _need(spec, "nodes", "datasets {id, label, layer, kind}")


# ---------- orchestration (ADF or generic) ----------
def map_orch(spec, raw=False):
    s = _spec(spec, "airflow", edge_kinds=ORCH_EDGES)
    conts = {g["id"]: g for g in spec.get("containers") or []}
    shut = set(spec.get("collapse") or []) | (set(conts) if spec.get("view") == "overview" else set())
    groups = [{"id": g["id"], "tag": g.get("type"),  # a frame names its type; a collapsed box has it in the tag
               "label": g.get("label") or g["id"] if g["id"] in shut else
               " · ".join(x for x in (g.get("type"), g.get("label") or g["id"]) if x)} for g in conts.values()]
    nodes, extra, edges = [], {}, []
    for a in spec.get("activities") or []:
        nodes.append(dict(a, label=a.get("label") or a["id"], operator=a.get("type") or a.get("operator")))
        for d in a.get("depends_on") or []:
            d = {"activity": d} if isinstance(d, str) else d
            edges.append({"from": d["activity"], "to": a["id"], "on": d.get("on", "succeeded")})
        if a.get("calls"):
            pid = "pl_" + _slug(a["calls"])
            extra[pid] = {"id": pid, "label": a["calls"], "tag": "pipeline", "shape": "box", "dashed": True}
            edges.append({"from": a["id"], "to": pid, "kind": "trigger"})
    edges += [dict(e) for e in spec.get("edges") or []]
    for e in edges:
        if not e.get("kind"):
            e["kind"] = "on_" + e.pop("on", "succeeded")
    trig = []
    for t in spec.get("triggers") or []:
        trig.append({"id": t["id"], "label": t.get("label") or t["id"], "tag": "trigger · " + (t.get("type") or "schedule"),
                     "shape": "pill", "tone": "soft", "mono": False})
        for a in t.get("starts") or []:
            edges.append({"from": t["id"], "to": a, "kind": "trigger"})
    # an edge to or from a container activity attaches to its first or last inner activities
    mem = {g: [n["id"] for n in nodes if n.get("group") == g] for g in conts}
    out = []
    for e in edges:
        srcs, dsts = [e["from"]], [e["to"]]
        if e["from"] in conts:
            inner = mem[e["from"]]
            srcs = [i for i in inner if not any(x["from"] == i and x["to"] in inner for x in edges)] or inner
        if e["to"] in conts:
            inner = mem[e["to"]]
            dsts = [i for i in inner if not any(x["to"] == i and x["from"] in inner for x in edges)] or inner
        out += [dict(e, **{"from": a, "to": b}) for a in srcs for b in dsts]
    nodes = trig + nodes + list(extra.values())
    if not raw:
        nodes, out, groups = _focus(spec, nodes, out, groups)
    return s, nodes, out, groups, None, ORCH_STATES


def pre_orch(spec):
    err = _need(spec, "activities", "activities {id, type, state, group, depends_on}")
    cids = {g.get("id") for g in spec.get("containers") or []}
    for a in spec.get("activities") or []:
        if a.get("group") and a["group"] not in cids:
            err.append(f"activity {a.get('id')}: group '{a['group']}' is not in containers")
        for d in a.get("depends_on") or []:
            on = "succeeded" if isinstance(d, str) else d.get("on", "succeeded")
            if "on_" + str(on) not in ORCH_EDGES:
                err.append(f"activity {a.get('id')}: on '{on}' - use succeeded, failed, completed or skipped")
        if a.get("state") and a["state"] not in ORCH_STATES and a["state"] not in core.AIRFLOW_STATES:
            err.append(f"activity {a.get('id')}: state '{a['state']}' - use {', '.join(ORCH_STATES)}")
    return err


# ---------- CDC / streaming ----------
def map_stream(spec, raw=False):
    s = _spec(spec, "plain", edge_kinds=FLOW_EDGES)
    nodes = []
    for n in spec.get("nodes") or []:
        m = dict(n, kind=n.get("role") or n.get("kind"))
        bits = [x for x in (_plural(n["partitions"], "partition") if n.get("partitions") else None,
                            ("keep " + str(n["retention"])) if n.get("retention") else None) if x]
        if bits and not n.get("tag"):
            m["tag"] = " · ".join(bits)
        m.setdefault("mono", m["kind"] in ("topic", "dlq"))
        nodes.append(m)
    edges, groups = [dict(e) for e in spec.get("edges") or []], [dict(g) for g in spec.get("groups") or []]
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
    return s, nodes, edges, groups, _kinds(s, STREAM_KINDS), None


# ---------- data mesh ----------
def map_mesh(spec, raw=False):
    s = _spec(spec, "plain", group_layout="bands", max_w=150)
    groups = [{"id": d["id"], "label": " · ".join(x for x in (d.get("label") or d["id"], d.get("owner")) if x)}
              for d in spec.get("domains") or []]
    nodes = []
    for n in spec.get("nodes") or []:
        m = dict(n, group=n.get("domain") or n.get("group"))
        if m.get("kind") in ("source_aligned", "aggregate", "consumer_aligned"):
            m.setdefault("strong", True)
            m.setdefault("tag", "data product")
            if n.get("slo") and not n.get("sub"):
                m["sub"] = "SLO " + str(n["slo"])
        nodes.append(m)
    edges = [dict(e) for e in spec.get("edges") or []]
    if not raw:
        nodes, edges, groups = _focus(spec, nodes, edges, groups)
        if s.get("view") == "overview":  # one box per domain, counting its data products
            dom = {g["id"]: g for g in groups}
            kinds = _kinds(s, MESH_KINDS)
            nodes, edges, _ = core.collapse(nodes, edges, groups, list(dom), kinds)
            for n in nodes:
                if n.pop("collapsed", None):
                    k = sum(1 for x in spec["nodes"] if (x.get("domain") or x.get("group")) == n["id"]
                            and x.get("kind") in ("source_aligned", "aggregate", "consumer_aligned"))
                    d = next(x for x in spec["domains"] if x["id"] == n["id"])
                    n.update(label=d.get("label") or d["id"], tag="domain · " + _plural(k, "data product"),
                             sub=d.get("owner"), strong=True, kind=None, tone="blue")
                    n.pop("count", None)
            groups, s = [], dict(s, view="detail")
    return s, nodes, edges, groups, _kinds(s, MESH_KINDS), None


def pre_mesh(spec):
    return _need(spec, "domains", "domains {id, label, owner}") + _need(spec, "nodes", "nodes {id, label, kind, domain}")


TYPES = {
    "er": {"svg": svg_er, "mermaid": mermaid_er, "validate": validate_er,
           "doc": "entity-relationship (crow's foot): tables with PK/FK columns, cardinality, subject areas"},
    "star-schema": {"svg": svg_star, "mermaid": mermaid_star, "validate": validate_star,
                    "doc": "star / snowflake schema: fact in the middle, dimensions left and right, outriggers"},
    "lineage": dict(_graph_type(map_lineage, set(core.DBT_KINDS) | set(LIN_KINDS), spread_tb=True),
                    doc="generic lineage / dependency DAG by kind; select, impact; style dbt (default), plain, airflow"),
    "dbt-lineage": dict(_graph_type(map_dbt, set(core.DBT_KINDS), pre=lambda s: _need(s, "nodes", "dbt resources"),
                                    spread_tb=True),
                        doc="dbt lineage graph: resource types, layers as columns, tests, overview per layer"),
    "airflow-dag": dict(_graph_type(map_airflow, styles=("airflow", "plain"), pre=pre_airflow, spread_tb=True),
                        doc="Airflow Graph view: tasks, operators, states, task groups, collapse, asset outlets"),
    "airflow-overview": dict(_graph_type(map_dags, styles=("airflow", "plain"), pre=pre_dags),
                             doc="multi-DAG overview: schedules, asset-triggered DAGs, TriggerDagRun, sensors"),
    "dfd": dict(_graph_type(map_dfd, set(DFD_KINDS), styles=("plain",), pre=pre_dfd, svg_fn=svg_dfd),
                doc="data flow diagram: external entities, numbered processes, data stores, named flows"),
    "medallion": dict(_graph_type(map_medallion, set(core.DBT_KINDS) | set(LIN_KINDS), styles=("plain", "dbt"),
                                  pre=pre_medallion),
                      doc="medallion / layer view: datasets in bronze, silver, gold columns"),
    "orchestration": dict(_graph_type(map_orch, styles=("airflow", "plain"), pre=pre_orch),
                          doc="ADF or generic pipeline: triggers, activities, ForEach/If containers, run conditions"),
    "cdc-streaming": dict(_graph_type(map_stream, set(STREAM_KINDS), styles=("plain", "dbt"),
                                      pre=lambda s: _need(s, "nodes", "nodes {id, label, role}")),
                          doc="CDC / streaming topology: databases, connectors, topics, processors, sinks, DLQ"),
    "data-mesh": dict(_graph_type(map_mesh, set(MESH_KINDS), styles=("plain", "dbt"), pre=pre_mesh),
                      doc="data mesh: domains, data products with owners and SLOs, ports, consumers"),
}
