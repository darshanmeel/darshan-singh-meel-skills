"""AI / ML diagram types for darshan-singh-meel-diagrams: RAG pipeline, agent loop, multi-agent orchestration,
ML lifecycle, feature store, eval pipeline, model serving, context assembly, neural-network block.
Loaded by the base registry; nothing runs at import. Spec fields: references/<topic>.md of this skill."""
import diagram as core

# node kinds -> look; our palette mapping, named in the legend
AI_KINDS = {
    "data": {"tone": "green", "label": "data", "shape": "document"},
    "step": {"tone": "plain", "label": "step"},
    "model": {"tone": "lav", "label": "model"},
    "agent": {"tone": "blue", "label": "agent"},
    "store": {"tone": "blue", "label": "store", "shape": "cylinder"},
    "tool": {"tone": "teal", "label": "tool"},
    "guard": {"tone": "amber", "label": "guardrail", "shape": "hexagon"},
    "gate": {"tone": "amber", "label": "gate", "shape": "diamond"},
    "human": {"tone": "amber", "label": "human", "shape": "actor"},
    "client": {"tone": "soft", "label": "client"},
    "gateway": {"tone": "ink", "label": "gateway"},
    "router": {"tone": "teal", "label": "router", "shape": "diamond"},
    "cache": {"tone": "teal", "label": "cache", "shape": "cylinder"},
    "monitor": {"tone": "soft", "label": "monitoring", "dashed": True},
    "output": {"tone": "soft", "label": "output", "shape": "pill"},
    "pass": {"tone": "green", "label": "meets gate"},
    "fail": {"tone": "red", "label": "misses gate"},
}
NN_KINDS = {
    "input": {"tone": "soft", "label": "input / output", "shape": "pill"},
    "output": {"tone": "soft", "label": "input / output", "shape": "pill"},
    "embed": {"tone": "green", "label": "embedding"},
    "attention": {"tone": "lav", "label": "attention"},
    "ffn": {"tone": "teal", "label": "feed-forward"},
    "norm": {"tone": "soft", "label": "add / norm"},
    "linear": {"tone": "blue", "label": "projection / head"},
    "activation": {"tone": "amber", "label": "activation"},
    "conv": {"tone": "teal", "label": "convolution"},
    "pool": {"tone": "soft", "label": "pooling"},
}
AI_EDGES = {
    "feedback": {"style": "dashed", "tone": "blue", "label": "feedback loop"},
    "fallback": {"style": "dashed", "tone": "amber", "label": "fallback"},
    "return": {"style": "dashed", "tone": "muted", "label": "returns result"},
    "handoff": {"style": "thick", "label": "handoff"},
    "approval": {"style": "dashed", "tone": "amber", "label": "human approval"},
    "telemetry": {"style": "dotted", "tone": "muted", "label": "telemetry"},
    "residual": {"tone": "muted", "label": "residual (skip) connection"},
}
DBT_TONES = {"step": "blue", "store": "teal", "client": "amber", "output": "amber", "monitor": "lav",
             "norm": "lav", "input": "amber", "pool": "lav"}
SEGMENTS = {  # context-assembly segment kinds
    "system": {"tone": "soft", "label": "system / policy"}, "tools": {"tone": "teal", "label": "tool schemas"},
    "memory": {"tone": "blue", "label": "memory"}, "retrieved": {"tone": "green", "label": "retrieved context"},
    "history": {"tone": "lav", "label": "conversation history"}, "user": {"tone": "amber", "label": "user input"},
    "reserved": {"tone": "plain", "label": "reserved for output", "dashed": True},
}


# ---------- shared helpers ----------
def _n(x, kind, group=None):
    n = dict(x)
    n.setdefault("kind", kind)
    if group and not n.get("group"):
        n["group"] = group
    return n


def _chain(nodes, **e):
    return [dict(e, **{"from": a["id"], "to": b["id"]}) for a, b in zip(nodes, nodes[1:])]


def _sp(spec, **dflt):
    """Spec copy with the family edge kinds and the type's defaults (only where the author set nothing)."""
    s = dict(spec, edge_kinds=dict(AI_EDGES, **(spec.get("edge_kinds") or {})))
    for k, v in dflt.items():
        if v is not None:
            s.setdefault(k, v)
    return s


def _list(spec, key, need=1, what="node"):
    v = spec.get(key)
    if not isinstance(v, list) or len(v) < need:
        return [f"{key}: at least {need} {what}{'s' if need > 1 else ''} {{id, label, ...}}"]
    return []


def _kinds_ok(nodes, kinds):
    allowed = set(kinds) | set(core.DBT_KINDS)
    return [f"node {n.get('id')}: kind '{n['kind']}' is not one of {', '.join(kinds)}"
            for n in nodes if n.get("kind") and n["kind"] not in allowed]


def _check(spec, p):
    flat = dict(p["spec"], nodes=p["nodes"], edges=p["edges"], groups=p["groups"])
    km = dict(p["kinds"], **(spec.get("kinds") or {}))
    err = core.check_graph(flat) + core.check_style(flat) + _kinds_ok(p["nodes"], km)
    for e in p["edges"]:
        if e.get("kind") and e["kind"] not in flat["edge_kinds"]:
            err.append(f"edge {e['from']} -> {e['to']}: kind '{e['kind']}' is not one of {', '.join(flat['edge_kinds'])}")
    return err


def _ids(nodes):
    return {n["id"] for n in nodes if "id" in n}


def _styled(p):
    """dbt style: filled pills get a readable fill per kind. airflow style: the run state carries colour and
    legend, so family kinds are left out (task boxes)."""
    if p["spec"].get("style") == "dbt":  # plain and soft would fill black or grey
        p = dict(p, kinds={k: dict(v, tone=DBT_TONES.get(k, v.get("tone")),  # white text on a stick figure vanishes
                                   shape=None if v.get("shape") == "actor" else v.get("shape"))
                           for k, v in p["kinds"].items()})
    if p["spec"].get("style") == "airflow":
        # a human gate keeps its stick figure (state colour on the outline); other kinds become task boxes
        p = dict(p, kinds={}, nodes=[dict({k: v for k, v in n.items() if k != "kind"},
                                          **({"shape": n.get("shape", "actor")} if n.get("kind") == "human" else {}))
                                     for n in p["nodes"]])
    return p


def _graph_type(parts, rules, doc):
    """Register a node-edge type: parts(spec) -> {spec, nodes, edges, groups, kinds}; rules(spec, parts) -> [str]."""
    def svg(spec, core_):
        p = _styled(parts(spec))
        if p.get("cells") and spec.get("view") != "overview" and not spec.get("collapse"):
            return _grid(spec, p, core_)  # collapsed groups change the boxes, so they take the layered layout
        try:
            return core_.graph(p["spec"], p["nodes"], p["edges"], p["groups"], kinds=p["kinds"])
        except core_.LayoutError as ex:  # dbt / airflow styles fix LR; too wide and no direction set -> top-down
            if spec.get("direction") or "canvas would be" not in str(ex):
                raise
            return core_.graph(dict(p["spec"], direction="TB"), p["nodes"], p["edges"], p["groups"], kinds=p["kinds"])

    def mermaid(spec):
        p = _styled(parts(spec))
        nodes = p["nodes"]
        if p["spec"].get("style") not in ("dbt", "airflow"):  # those styles join the lines already
            # model names, dims and top-k live in sub; Mermaid would drop them
            nodes = [dict(n, label=" · ".join(str(x) for x in (n["label"], n.get("tag"), n.get("sub")) if x))
                     for n in nodes]
        return core.mermaid_graph(p["spec"], nodes, p["edges"], p["groups"], kinds=p["kinds"])

    def validate(spec):
        try:
            p = parts(spec)
        except (KeyError, TypeError, AttributeError) as ex:
            return [f"spec shape: {type(ex).__name__} {ex} - see references for this type's fields"]
        err = _check(spec, p)
        return err or rules(spec, p)

    return {"svg": svg, "mermaid": mermaid, "validate": validate, "doc": doc}


def _grid_place(p, st, cells, mw, core_):
    """Cell positions {id: (x, y, w, h)} and canvas width with box text wrapped at mw."""
    sz = {n["id"]: (n,) + core_.size(n, n.get("max_w", mw)) for n in st["nodes"]}
    cols, rows = sorted({v[0] for v in cells.values()}), sorted({v[1] for v in cells.values()})
    colw = {k: max(sz[i][1] for i, v in cells.items() if v[0] == k) for k in cols}
    rowh = {k: max(sz[i][2] for i, v in cells.items() if v[1] == k) for k in rows}
    glab = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    lab_h = max([len(core_.label_lines(glab[g], 220)) * 15 + 10 for g in glab] or [0])
    gx = {}
    for e in st["edges"]:
        a, b = cells[e["from"]][0], cells[e["to"]][0]
        if e.get("label") and a != b:
            for k in range(min(a, b), max(a, b)):
                gx[k] = max(gx.get(k, 0), min(140, core_.text_width(str(e["label"]), 11, True) + 44))
    padr, padl = {}, {}  # pad_r / pad_l widen a group's frame (room for a loop arrow, its label) and the gap
    for g in st["groups"]:
        mc = [cells[n["id"]][0] for n in st["nodes"] if n.get("group") == g["id"]]
        if mc:
            padr[max(mc)] = max(padr.get(max(mc), 0), g.get("pad_r", 0) + core_.GP)
            padl[min(mc)] = max(padl.get(min(mc), 0), g.get("pad_l", 0) + core_.GP)
    x, cx = core_.MARGIN + p.get("margin_l", 0), {}
    for k in cols:
        x += padl.get(k, 0)
        cx[k] = x
        x += colw[k] + max(60, gx.get(k, 0)) + padr.get(k, 0)
    starts, ends, busy = set(), set(), set()  # rows where a frame opens (its label sits above) or closes
    gof = {n["id"]: n.get("group") for n in st["nodes"]}
    for g in st["groups"]:
        mr = [cells[n["id"]][1] for n in st["nodes"] if n.get("group") == g["id"]]
        if mr:
            starts.add(min(mr))
            ends.add(max(mr))
            # a labelled arrow entering the frame's first row from outside needs its label clear of the border
            if any(e.get("label") and gof.get(e["to"]) == g["id"] and gof.get(e["from"]) != g["id"]
                   and cells[e["to"]][1] == min(mr) for e in st["edges"]):
                busy.add(min(mr))
    # arrows that change column below a row cross there: room for two channels clear of the frame borders
    jog = {cells[e["from"]][1] for e in st["edges"] if cells[e["from"]][0] != cells[e["to"]][0]
           and cells[e["from"]][1] < cells[e["to"]][1]}
    y, ry = core_.MARGIN, {}
    for k in rows:
        y += (lab_h + core_.GP) * (2 if k in busy and k != rows[0] else 1) if k in starts else 0
        ry[k] = y
        y += rowh[k] + 44 + (core_.GP if k in ends else 0) + (24 if k in jog and k in ends else 0)
    pos = {i: (cx[v[0]] + (colw[v[0]] - sz[i][1]) / 2, ry[v[1]] + (rowh[v[1]] - sz[i][2]) / 2, sz[i][1], sz[i][2])
           for i, v in cells.items()}
    return pos, max(r[0] + r[2] for r in pos.values()) + core_.MARGIN + core_.GP


def _grid(spec, p, core_):
    """Draw a node-edge type on fixed cells {id: (col, row)}: column gaps sized by the labels that cross them,
    group frames around their members, orthogonal routing, legend. For types whose reading order is fixed."""
    st = core_.style_graph(p["spec"], p["nodes"], p["edges"], p["groups"], kinds=p["kinds"])
    c, cells = core_.canvas(spec), p["cells"]
    for mw in (spec["max_w"],) if spec.get("max_w") else (200, 160, 130):  # too wide: wrap box text narrower
        pos, W = _grid_place(p, st, cells, mw, core_)
        if W <= core_.MAX_W:
            break
    if W > core_.MAX_W:
        raise core_.LayoutError(f"canvas would be {int(W)}px wide (max {core_.MAX_W}): shorten edge labels "
                                "(they widen the column gaps), use shorter box labels or split the diagram")
    glab = {g["id"]: g.get("label", g["id"]) for g in st["groups"]}
    for g in st["groups"]:
        rs = [pos[n["id"]] for n in st["nodes"] if n.get("group") == g["id"]]
        if rs:
            x0 = min(r[0] for r in rs) - core_.GP - g.get("pad_l", 0)
            x1 = max(r[0] + r[2] for r in rs) + core_.GP + g.get("pad_r", 0)
            ls = core_.label_lines(glab[g["id"]], x1 - x0)
            y0 = min(r[1] for r in rs) - core_.GP - len(ls) * 15 - 10
            core_.container(c, g["id"], glab[g["id"]], x0, y0, x1 - x0, max(r[1] + r[3] for r in rs) + core_.GP - y0,
                            members=[n["id"] for n in st["nodes"] if n.get("group") == g["id"]], tone=g.get("tone"))
    for n in st["nodes"]:
        core_.node(c, n, *pos[n["id"]])
    outer = [e for e in st["edges"] if e.get("outside") == "left"]
    core_.route(c, [e for e in st["edges"] if e not in outer], p.get("route", "LR"))
    lane = min([b["x"] for b in c["geo"]["containers"] + c["geo"]["nodes"]]) - 18
    for e in outer:  # a long loop back runs round the outside, clear of frames and their labels
        a, b = pos[e["from"]], pos[e["to"]]
        ya, yb = a[1] + a[3] / 2, b[1] + b[3] / 2
        core_.arrow(c, [(a[0], ya), (lane, ya), (lane, yb), (b[0], yb)], e, label_xy=None)
    core_.legend(c, st["legend"])
    return core_.finish(c)


# ---------- rag-pipeline ----------
def _rag(spec):
    ing = [_n(x, "step", "ingest") for x in spec.get("ingest") or []]
    qry = [_n(x, "step", "query") for x in spec.get("query") or []]
    sto = [_n(x, "store", "stores") for x in spec.get("stores") or []]
    edges = list(spec.get("edges") or [])
    # line the bands up: the store sits one layer after the last ingest step, level with the step that reads it
    sids = _ids(sto)
    hit = [j for j, q in enumerate(qry) if any(e.get("from") in sids and e.get("to") == q.get("id") for e in edges)]
    if hit and ing and not any("rank" in n for n in ing + qry + sto):
        base = max(len(ing), hit[0])
        ing = [dict(n, rank=i + base - len(ing)) for i, n in enumerate(ing)]
        sto = [dict(n, rank=base) for n in sto]
        qry = [dict(n, rank=j + base - hit[0]) for j, n in enumerate(qry)]
    groups = [{"id": "ingest", "label": spec.get("ingest_label", "Ingest (offline)")},
              {"id": "stores", "label": spec.get("store_label", "Index"), "tone": "blue"},
              {"id": "query", "label": spec.get("query_label", "Query (per request)")}]
    extra = list(spec.get("nodes") or [])
    p = {"spec": _sp(spec, group_layout="bands"), "nodes": ing + sto + qry + extra,
         "edges": _chain(ing) + _chain(qry) + [dict(e) for e in edges], "groups": groups, "kinds": AI_KINDS}
    if all("rank" in n for n in ing + sto + qry) and not extra and spec.get("layout", "columns") == "columns":
        # three columns (ingest | index | query), rows = layers; column gaps sized by the arrow labels
        cells = {n["id"]: (col, n["rank"]) for col, ns in enumerate((ing, sto, qry)) for n in ns}
        for k, n in enumerate(sto):
            cells[n["id"]] = (1, n["rank"] + k)
        p.update(cells=cells, route="TB")
        for e in p["edges"]:
            a, b = cells.get(e["from"]), cells.get(e["to"])
            if a and b and a[0] == b[0]:
                e.setdefault("from_side", "bottom")
                e.setdefault("to_side", "top")
            elif a and b and b[0] == a[0] + 1:  # ingest -> index -> query: sideways, never on the chain's trunk
                e.setdefault("from_side", "right")
                e.setdefault("to_side", "left")
    return p


def _rag_rules(spec, p):
    if spec.get("layout", "columns") not in ("columns", "flow"):
        return ["layout: 'columns' (default, ingest | index | query) or 'flow' (layered)"]
    err = _list(spec, "ingest", 2, "step") + _list(spec, "query", 2, "step") + _list(spec, "stores", 1, "store")
    if err:
        return err
    ing, qry = _ids(spec["ingest"]), _ids(spec["query"])
    for s in spec["stores"]:
        if not any(e["to"] == s["id"] and e["from"] in ing for e in p["edges"]):
            err.append(f"store {s['id']}: no edge from an ingest step - add edges [{{from: <embed step>, to: {s['id']}}}]")
        if not any(e["from"] == s["id"] and e["to"] in qry for e in p["edges"]):
            err.append(f"store {s['id']}: no edge to a query step - add edges [{{from: {s['id']}, to: <retrieve step>}}]")
    return err


# ---------- agent-loop ----------
def _agent(spec):
    steps = [_n(x, "step", "loop") for x in spec.get("steps") or []]
    others = [_n(x, "tool") for x in spec.get("nodes") or []]
    edges = _chain(steps)
    if len(steps) > 1:
        edges.append({"from": steps[-1]["id"], "to": steps[0]["id"], "from_side": "right", "to_side": "right"})
    extra = [dict(e) for e in spec.get("edges") or []]
    edges += extra
    name = " · ".join(x for x in (spec.get("agent", "Agent loop"), spec.get("loop_label")) if x)
    groups = [{"id": "loop", "label": name, "tone": "teal", "pad_r": 20}]
    p = {"spec": _sp(spec), "nodes": steps + others, "edges": edges, "groups": groups, "kinds": AI_KINDS}
    if steps and spec.get("layout", "loop") == "loop":
        p["cells"] = _agent_cells(steps, others, extra)
    return p


def _agent_cells(steps, others, edges):
    """Fixed reading order: entry chain left of the first step, the loop as a column, memory under the entry,
    tools and humans right of the step that calls them, the exit path above them on the first step's row."""
    S = [s["id"] for s in steps]
    O = {n["id"]: n for n in others}
    succ, pred = {}, {}
    for e in edges:
        succ.setdefault(e.get("from"), []).append(e.get("to"))
        pred.setdefault(e.get("to"), []).append(e.get("from"))

    def reach(start, nxt):  # {id: distance} over non-step nodes
        d, todo = {}, [(x, 1) for x in start]
        while todo:
            u, k = todo.pop(0)
            if u in O and u not in d:
                d[u] = k
                todo += [(v, k + 1) for v in nxt.get(u, [])]
        return d

    outs = [i for i, n in O.items() if n.get("kind") == "output"]
    exit_ = {}
    for s in S:
        for v in succ.get(s, []):
            d = reach([v], succ)
            if any(o in d for o in outs):
                exit_.update({u: k for u, k in d.items() if u not in exit_})
    entry = {u: k for u, k in reach(pred.get(S[0], []), pred).items()
             if u not in exit_ and O[u].get("kind") not in ("store", "cache")}
    E = max(entry.values() or [0])
    stores = [i for i in O if i not in entry and i not in exit_ and O[i].get("kind") in ("store", "cache")]
    cs = 1 if entry or stores else 0
    r0 = max(E - 1, 1 if exit_ else 0)
    cells = {s: (cs, r0 + k) for k, s in enumerate(S)}
    used = set(cells.values())

    def put(i, col, row):
        while (col, row) in used:
            row += 1
        cells[i] = (col, row)
        used.add((col, row))

    for u, k in sorted(entry.items(), key=lambda t: -t[1]):  # entry chain runs down into the first step's row
        put(u, 0, r0 - k + 1)
    for i in stores:
        put(i, 0, r0 + 1)
    for u, k in sorted(exit_.items(), key=lambda t: t[1]):
        put(u, cs + k, 0)
    rest = [i for i in O if i not in cells]
    for s in S:  # tools and humans: right of the calling step; a chain continues on its predecessor's row
        todo = [(v, 1, cells[s][1]) for v in succ.get(s, []) if v in rest]
        while todo:
            u, k, row = todo.pop(0)
            if u in rest and u not in cells:
                put(u, cs + k, max(row, r0))
                todo += [(v, k + 1, cells[u][1]) for v in succ.get(u, []) if v in rest]
    for _ in range(len(rest)):  # anything else sits under the box it links to
        for i in rest:
            near = [cells[j] for j in succ.get(i, []) + pred.get(i, []) if j in cells]
            if i not in cells and near:
                put(i, near[0][0], near[0][1] + 1)
    for i in rest:
        if i not in cells:
            put(i, cs + 1, r0 + len(S))
    sids = set(S)
    for e in edges:  # the exit leaves the first step upwards, keeping its right side for the loop arrow
        if e.get("from") in sids and e.get("to") in exit_ and cells[e["to"]][1] < cells[e["from"]][1]:
            e.setdefault("from_side", "top")
    return cells


def _agent_rules(spec, p):
    if spec.get("layout", "loop") not in ("loop", "flow"):
        return ["layout: 'loop' (default, entry left, loop column, tools right) or 'flow' (layered)"]
    err = _list(spec, "steps", 2, "step") + _list(spec, "nodes", 1, "node (tools, memory, guards, user)")
    if err:
        return err
    if not any(n.get("kind", "tool") == "tool" for n in spec["nodes"]):
        err.append("nodes: no tool - an agent loop acts through tools; add one {kind: tool} or draw it as flow")
    linked = {e["from"] for e in p["edges"]} | {e["to"] for e in p["edges"]}
    err += [f"node {n['id']}: not connected - link it to the step that uses it" for n in spec["nodes"]
            if n["id"] not in linked and not n.get("free")]
    return err


# ---------- multi-agent ----------
def _multi(spec):
    return {"spec": _sp(spec), "nodes": [_n(x, "agent") for x in spec.get("nodes") or []],
            "edges": list(spec.get("edges") or []), "groups": list(spec.get("groups") or []), "kinds": AI_KINDS}


def _multi_rules(spec, p):
    if sum(1 for n in p["nodes"] if n.get("kind") == "agent") < 2:
        return ["nodes: at least 2 {kind: agent} - one agent is an agent-loop diagram"]
    return []


# ---------- ml-lifecycle ----------
def _ml(spec):
    st = [_n(x, "step") for x in spec.get("stages") or []]
    extra = [_n(x, "store") for x in spec.get("nodes") or []]
    loops = [dict(e, kind=e.get("kind", "feedback")) for e in spec.get("loops") or []]
    edges = _chain(st) + [dict(e) for e in spec.get("edges") or []] + loops
    p = {"spec": _sp(spec), "nodes": st + extra, "edges": edges, "groups": list(spec.get("groups") or []),
         "kinds": AI_KINDS}
    if spec.get("layout", "ring") == "ring" and len(st) >= 4:
        p["cells"] = _ring_cells(st, extra, edges)
        p["margin_l"] = 40
    return p


def _ring_cells(st, extra, edges):
    """Stages as a racetrack: first half left to right on the top row, second half right to left below, so the
    loop back to the start is short. Extra nodes sit above (top row) or below (bottom row) the stage they link to."""
    k = (len(st) + 1) // 2
    cells = {n["id"]: (i, 1) if i < k else (len(st) - 1 - i, 2) for i, n in enumerate(st)}
    for a, b in zip(st, st[1:]):  # chain edges leave towards the next stage on the racetrack
        for e in edges:
            if e["from"] != a["id"] or e["to"] != b["id"]:
                continue
            if cells[a["id"]][1] != cells[b["id"]][1]:
                e.setdefault("from_side", "bottom")
                e.setdefault("to_side", "top")
            elif cells[a["id"]][1] == 2:  # bottom row runs right to left: straight across, not under the frame
                e.setdefault("from_side", "left")
                e.setdefault("to_side", "right")
    for e in edges:  # a loop back to the first column runs round the outside on the left
        a, b = cells.get(e["from"]), cells.get(e["to"])
        if a and b and a[0] == b[0] == 0 and a[1] > b[1]:
            e.setdefault("outside", "left")
        elif a and b and a[1] == 2 and b[1] == 1:  # other loops go straight up; the sides carry the chain
            e.setdefault("from_side", "top")
            e.setdefault("to_side", "bottom")
        elif a and b and a[1] == b[1] == 1 and b[0] < a[0] and e.get("kind") == "feedback":
            e.setdefault("from_side", "top")  # a loop back along the top row: over the chain, not on its exit
            e.setdefault("to_side", "top")
    used = set(cells.values())
    for n in extra:
        near = [cells[e["to"] if e["from"] == n["id"] else e["from"]] for e in edges
                if n["id"] in (e["from"], e["to"]) and (e["to"] if e["from"] == n["id"] else e["from"]) in cells]
        col, row = near[0] if near else (0, 2)
        row = 0 if row == 1 else 3
        while (col, row) in used:
            col += 1
        cells[n["id"]] = (col, row)
        used.add((col, row))
    return cells


def _ml_rules(spec, p):
    if spec.get("layout", "ring") not in ("ring", "flow"):
        return ["layout: 'ring' (default, racetrack) or 'flow' (layered, honours style and groups)"]
    err = _list(spec, "stages", 3, "stage") + _list(spec, "loops", 1, "loop {from, to, label}")
    if err and "loops" in err[-1]:
        err[-1] += " - a lifecycle closes the loop (monitor -> retrain); without one use boxes"
    return err


# ---------- feature-store ----------
def _fs(spec):
    labels = spec.get("labels") or {}
    groups = [{"id": "pipelines", "label": labels.get("pipelines", "Feature pipelines (one definition)")},
              {"id": "training", "label": labels.get("training", "Training (offline, point-in-time)")},
              {"id": "serving", "label": labels.get("serving", "Serving (online, low latency)")}]
    nodes = ([_n(x, "data") for x in spec.get("sources") or []] +
             [_n(x, "step", "pipelines") for x in spec.get("pipelines") or []] +
             [_n(x, "store", "training") for x in spec.get("offline") or []] +
             [_n(x, "step", "training") for x in spec.get("training") or []] +
             [_n(x, "store", "serving") for x in spec.get("online") or []] +
             [_n(x, "step", "serving") for x in spec.get("serving") or []])
    p = {"spec": _sp(spec, group_layout="bands"), "nodes": nodes, "edges": [dict(e) for e in spec.get("edges") or []],
         "groups": groups, "kinds": AI_KINDS}
    if spec.get("layout", "split") == "split":
        cells = {}
        for row, key in enumerate(("sources", "pipelines")):
            for k, n in enumerate(spec.get(key) or []):
                cells[n["id"]] = (k, row)
        for col, keys in enumerate((("offline", "training"), ("online", "serving"))):
            ns = [n for key in keys for n in spec.get(key) or []]
            for k, n in enumerate(ns):
                cells[n["id"]] = (col, 2 + k)
        p.update(cells=cells, route="TB")
        for e in p["edges"]:  # top-down: arrows leave the bottom, enter the top
            if e.get("from") in cells and e.get("to") in cells and cells[e["from"]][1] < cells[e["to"]][1]:
                e.setdefault("from_side", "bottom")
                e.setdefault("to_side", "top")
    return p


def _fs_rules(spec, p):
    err = [] if spec.get("layout", "split") in ("split", "flow") else [
        "layout: 'split' (default, training path left, serving path right) or 'flow' (layered)"]
    for k in ("sources", "pipelines", "offline", "online", "training", "serving"):
        err += _list(spec, k)
    if err:
        return err
    off, on, tr, sv = (_ids(spec[k]) for k in ("offline", "online", "training", "serving"))
    if not any(e["from"] in off and e["to"] in tr for e in p["edges"]):
        err.append("edges: no offline store -> training edge; training reads point-in-time features from the offline store")
    if not any(e["from"] in on and e["to"] in sv for e in p["edges"]):
        err.append("edges: no online store -> serving edge; serving reads features from the online store")
    return err


# ---------- eval-pipeline ----------
def _metric(m):
    m = dict(m)
    if "value" in m and "threshold" in m:
        hi = m.get("higher_is_better", True)
        ok = m["value"] >= m["threshold"] if hi else m["value"] <= m["threshold"]
        m.setdefault("kind", "pass" if ok else "fail")
        m.setdefault("state", "success" if ok else "failed")  # read by the airflow style only
        m.setdefault("sub", f"{m['value']} (gate {'>=' if hi else '<='} {m['threshold']})")
    else:
        m.setdefault("kind", "step")
    return m


def _eval(spec):
    ds = [_n(x, "data", "datasets") for x in spec.get("datasets") or []]
    run = [_n(x, "model", "run") for x in spec.get("run") or []]
    gr = [_n(x, {"code": "step", "model": "model", "human": "human"}.get(x.get("grader"), "step"), "graders")
          for x in spec.get("graders") or []]
    me = [_n(_metric(x), "step", "metrics") for x in spec.get("metrics") or []]
    gate = [_n(dict(spec["gate"], shape=spec["gate"].get("shape", "diamond")), "guard", "gate")] if spec.get("gate") else []
    out = [_n(x, "output") for x in spec.get("outcomes") or []]
    edges = [{"from": d["id"], "to": run[0]["id"]} for d in ds if run] + _chain(run)
    edges += [{"from": run[-1]["id"], "to": g["id"]} for g in gr if run]
    edges += [{"from": g["id"], "to": m} for g in gr for m in g.get("metrics") or []]
    edges += [{"from": m["id"], "to": gate[0]["id"]} for m in me if gate]
    edges += [{"from": gate[0]["id"], "to": o["id"], "label": o.get("when"), "tone": "red" if o.get("fail") else None}
              for o in out if gate]
    edges = [{k: v for k, v in e.items() if v is not None} for e in edges] + list(spec.get("edges") or [])
    labels = spec.get("labels") or {}
    groups = [{"id": g, "label": labels.get(g, d)} for g, d in
              (("datasets", "Datasets"), ("run", "System under test"), ("graders", "Graders"),
               ("metrics", "Metrics vs gate"), ("gate", "Release gate"))]
    return {"spec": _sp(spec, group_layout="columns"), "nodes": ds + run + gr + me + gate + out, "edges": edges,
            "groups": groups, "kinds": AI_KINDS}


def _eval_rules(spec, p):
    err = (_list(spec, "datasets") + _list(spec, "run") + _list(spec, "graders") + _list(spec, "metrics")
           + _list(spec, "outcomes", 2, "outcome"))
    if not isinstance(spec.get("gate"), dict):
        err.append("gate: one node {id, label} that decides pass / fail")
    if err:
        return err
    mids = _ids(spec["metrics"])
    for g in spec["graders"]:
        for m in g.get("metrics") or []:
            if m not in mids:
                err.append(f"grader {g['id']}: metric '{m}' is not in metrics")
    fed = {m for g in spec["graders"] for m in g.get("metrics") or []}
    err += [f"metric {m}: no grader lists it - add it to a grader's metrics" for m in sorted(mids - fed)]
    return err


# ---------- model-serving ----------
def _serve(spec):
    nodes = [_n(x, "step") for x in spec.get("nodes") or []]
    edges = [dict(e) for e in spec.get("edges") or []]
    p = {"spec": _sp(spec), "nodes": nodes, "edges": edges, "groups": list(spec.get("groups") or []),
         "kinds": AI_KINDS}
    if spec.get("layout", "fan") == "fan" and not any("rank" in n for n in nodes):
        p["cells"] = _fan_cells(nodes, edges, p["groups"])
    return p


def _fan_cells(nodes, edges, groups):
    """Request path down the left column; grouped boxes (model endpoints, providers) fan out to the right of the
    box that calls them, in groups order."""
    grouped = {n["id"] for n in nodes if n.get("group")}
    path = [n["id"] for n in nodes if n["id"] not in grouped]
    depth = {i: 0 for i in path if not any(e["to"] == i and e["from"] in path for e in edges)}
    todo = list(depth)
    while todo:
        u = todo.pop(0)
        for e in edges:
            if e["from"] == u and e["to"] in path and e["to"] not in depth:
                depth[e["to"]] = depth[u] + 1
                todo.append(e["to"])
    cells, used = {}, set()
    for i in path:
        r = depth.get(i, max(depth.values() or [0]) + 1)
        while (0, r) in used:
            r += 1
        cells[i] = (0, r)
        used.add((0, r))
    order = {g["id"]: k for k, g in enumerate(groups)}
    rest = sorted((n for n in nodes if n["id"] in grouped), key=lambda n: order.get(n.get("group"), 99))
    parent = {n["id"]: next((cells[e["from"]] for e in edges if e["to"] == n["id"] and e["from"] in cells), (0, 0))
              for n in rest}
    if rest:
        r = parent[rest[0]["id"]][1]  # first endpoint level with its caller, the rest below: arrows run right or down
        for n in rest:
            cells[n["id"]] = (1, r)
            r += 1
    for e in edges:  # fan-out below the caller's row leaves from its bottom, so no arrow loops round the left
        a, b = cells.get(e["from"]), cells.get(e["to"])
        if a and b and a[0] == 0 and b[0] == 1 and b[1] > a[1]:
            e.setdefault("from_side", "bottom")
            e.setdefault("to_side", "left")
        if e["from"] in cells and e["to"] in cells and cells[e["from"]][0] == 0 and cells[e["to"]][0] == 0:
            e.setdefault("from_side", "bottom")
            e.setdefault("to_side", "top")
    return cells


def _serve_rules(spec, p):
    if spec.get("layout", "fan") not in ("fan", "flow"):
        return ["layout: 'fan' (default, request path left, endpoints right) or 'flow' (layered)"]
    ks = {n.get("kind") for n in p["nodes"]}
    err = [] if "model" in ks else ["nodes: no {kind: model} - serving topology needs the model endpoints"]
    if not ks & {"gateway", "router"}:
        err.append("nodes: no {kind: gateway} or {kind: router} - without one this is a plain boxes diagram")
    return err


# ---------- nn-block ----------
def _nn(spec):
    ls = [_n(x, "linear") for x in spec.get("layers") or []]
    edges = [dict({"from": a["id"], "to": b["id"]}, **({"label": a["out"]} if a.get("out") else {}))
             for a, b in zip(ls, ls[1:])]
    # residuals run down the right side of the column, inside the block frame (pad_r leaves room)
    edges += [dict(r, kind=r.get("kind", "residual"), from_side="right", to_side="right")
              for r in spec.get("residuals") or []]
    groups = [dict(b, pad_r=40, pad_l=60, label=f"{b.get('label', b['id'])} × {b['repeat']}" if b.get("repeat")
                   else b.get("label", b["id"])) for b in spec.get("blocks") or []]
    return {"spec": _sp(spec, direction="TB"), "nodes": ls, "edges": edges + list(spec.get("edges") or []),
            "groups": groups, "kinds": NN_KINDS, "route": "TB",
            "cells": {n["id"]: (0, k) for k, n in enumerate(ls)}}


def _nn_rules(spec, p):
    err = _list(spec, "layers", 2, "layer")
    ids = _ids(spec.get("layers") or [])
    for r in spec.get("residuals") or []:
        if r.get("from") not in ids or r.get("to") not in ids:
            err.append(f"residual {r.get('from')} -> {r.get('to')}: both ends must be layer ids")
    return err


# ---------- context-assembly (own layout) ----------
def _fmt(n):
    return f"{n:,}"


def _ctx_validate(spec):
    err = _list(spec, "segments", 2, "segment {id, label, tokens}")
    if not isinstance(spec.get("limit"), int) or spec["limit"] <= 0:
        err.append("limit: the context window size in tokens, e.g. 128000")
    if err:
        return err
    sids = set()
    for s in spec["segments"]:
        if not s.get("id") or not s.get("label"):
            err.append(f"segment {s}: needs id and label")
        if not isinstance(s.get("tokens"), int) or s["tokens"] < 0:
            err.append(f"segment {s.get('id')}: tokens must be a whole number >= 0")
        if s.get("kind") and s["kind"] not in SEGMENTS:
            err.append(f"segment {s.get('id')}: kind '{s['kind']}' is not one of {', '.join(SEGMENTS)}")
        sids.add(s.get("id"))
    src = _ids(spec.get("sources") or [])
    for s in spec["segments"]:
        if s.get("source") and s["source"] not in src:
            err.append(f"segment {s['id']}: source '{s['source']}' is not in sources")
    if sids & src:
        err.append(f"ids used for both a source and a segment: {', '.join(sorted(sids & src))}")
    if err:
        return err
    total = sum(s["tokens"] for s in spec["segments"])
    if total > spec["limit"]:
        err.append(f"segments add up to {_fmt(total)} tokens, over the limit of {_fmt(spec['limit'])}: "
                   "trim a segment (fewer chunks, shorter history) - the model would truncate or reject it")
    err += core.check_graph({"nodes": spec.get("sources") or [{"id": "_", "label": "_"}], "edges": []})
    return err


def _ctx_svg(spec, core_):
    c = core_.canvas(spec)
    segs, limit = spec["segments"], spec["limit"]
    total = sum(s["tokens"] for s in segs)
    bar_w, gap, unit = 300, 6, spec.get("bar_h", 520) / limit
    srcs = [dict(s, kind=s.get("kind", "step")) for s in spec.get("sources") or []]
    # sources stay neutral (their shape names the kind): colour belongs to the segment kinds in the legend
    plain = {k: dict(v, tone="plain") for k, v in AI_KINDS.items()}
    st = core_.style_graph(dict(spec, style="plain", legend=False), srcs, [], [], kinds=plain)["nodes"]
    sized = [(n,) + core_.size(n, 210) for n in st]
    src_w = max([w for _, w, _ in sized] or [0])
    x_bar = core_.MARGIN + (src_w + 150 if srcs else 0)
    top = core_.MARGIN + 30
    head = f"Context window · {_fmt(total)} of {_fmt(limit)} tokens ({round(100 * total / limit)}%)"
    core_.text(c, x_bar, core_.MARGIN + 12, head, cls="dg-tx", mono=True, size=11.5)
    y, pos = top, {}
    for s in segs:
        k = SEGMENTS.get(s.get("kind"), {"tone": "soft"})
        n = {"id": s["id"], "label": s["label"], "sub": s.get("sub"), "tag": f"{_fmt(s['tokens'])} tokens",
             "shape": "box", "tone": s.get("tone") or k["tone"], "dashed": k.get("dashed", False), "align": "left",
             "max_w": bar_w}
        _, h = core_.size(n, bar_w, bar_w)
        h = max(h, round(s["tokens"] * unit))
        core_.node(c, n, x_bar, y, bar_w, h)
        pos[s["id"]] = (y, h)
        y += h + gap
    free = limit - total
    if free > 0:
        core_.node(c, {"id": "_free", "label": f"unused · {_fmt(free)} tokens", "shape": "box", "dashed": True,
                       "tone": "plain", "align": "left", "free": True}, x_bar, y, bar_w, max(32, round(free * unit)))
    # sources: centred on the first segment they feed, in segment order, no overlaps
    want, x_src = [], core_.MARGIN
    for n, w, h in sized:
        fed = [pos[s["id"]] for s in segs if s.get("source") == n["id"]]
        want.append((n, w, h, (fed[0][0] + fed[0][1] / 2) if fed else top))
    want.sort(key=lambda t: t[3])
    yy = top
    for n, w, h, cy in want:
        yy = max(yy, cy - h / 2)
        core_.node(c, n, x_src + (src_w - w) / 2, yy, w, h)
        yy += h + 18
    edges = [{"from": s["source"], "to": s["id"], "label": s.get("via")} for s in segs if s.get("source")]
    core_.route(c, [{k: v for k, v in e.items() if v} for e in edges], "LR")
    used = []
    for s in segs:
        k = s.get("kind")
        if k in SEGMENTS and k not in used:
            used.append(k)
    if spec.get("legend", True):
        core_.legend(c, ([{"label": "source", "tone": "plain"}] if srcs else []) +
                     [{"label": SEGMENTS[k]["label"], "tone": SEGMENTS[k]["tone"],
                       "dashed": SEGMENTS[k].get("dashed")} for k in used])
    c["geo"]["connected"] = False
    return core_.finish(c)


def _ctx_mermaid(spec):
    # TB at the root: Mermaid ignores a subgraph's own direction once its nodes link outside it
    out = core.mermaid_head(spec, "flowchart TB")
    total = sum(s["tokens"] for s in spec["segments"])
    head = f"Context window · {_fmt(total)} of {_fmt(spec['limit'])} tokens"
    out.append(f"  subgraph ctx [{core.mm_text(head)}]")
    for s in spec["segments"]:
        lab = " · ".join(x for x in (s["label"], f"{_fmt(s['tokens'])} tokens", s.get("sub")) if x)
        out.append(f"    {core.mm_id(s['id'])}[{core.mm_text(lab)}]")
    segs = spec["segments"]
    for a, b in zip(segs, segs[1:]):
        out.append(f"    {core.mm_id(a['id'])} ~~~ {core.mm_id(b['id'])}")
    out.append("  end")
    for n in spec.get("sources") or []:
        out.append(f"  {core.mm_id(n['id'])}({core.mm_text(' · '.join(x for x in (n['label'], n.get('sub')) if x))})")
    for s in segs:
        if s.get("source"):
            lab = f"|{core.mm_text(s['via'])}|" if s.get("via") else ""
            out.append(f"  {core.mm_id(s['source'])} -->{lab} {core.mm_id(s['id'])}")
    return "\n".join(out) + "\n"


TYPES = {
    "rag-pipeline": _graph_type(_rag, _rag_rules,
                                "RAG: ingest (load, chunk, embed, index) and query (retrieve, rerank, generate) bands"),
    "agent-loop": _graph_type(_agent, _agent_rules,
                              "LLM agent loop: plan / act / observe with tools, memory, guardrails, human approval"),
    "multi-agent": _graph_type(_multi, _multi_rules,
                               "multi-agent orchestration: supervisor, workers, handoffs, shared state; airflow style for runs"),
    "ml-lifecycle": _graph_type(_ml, _ml_rules,
                                "ML lifecycle / MLOps: data to monitor with feedback loops, registry, gates"),
    "feature-store": _graph_type(_fs, _fs_rules,
                                 "feature store: one definition, offline training path vs online serving path"),
    "eval-pipeline": _graph_type(_eval, _eval_rules,
                                 "eval pipeline: datasets, system under test, graders, metrics vs thresholds, release gate"),
    "model-serving": _graph_type(_serve, _serve_rules,
                                 "model serving topology: gateway, router, cache, primary and fallback models"),
    "nn-block": _graph_type(_nn, _nn_rules,
                            "neural network / transformer block: layer stack, repeated blocks, residuals, tensor shapes"),
    "context-assembly": {"svg": _ctx_svg, "mermaid": _ctx_mermaid, "validate": _ctx_validate,
                         "doc": "prompt / context assembly: sources into a token-budgeted context window"},
}
