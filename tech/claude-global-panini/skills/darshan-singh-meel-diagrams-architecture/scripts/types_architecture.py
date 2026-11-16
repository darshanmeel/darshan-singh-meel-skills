"""Architecture diagram types for the darshan-singh-meel-diagrams engine: C4 context / container / component,
deployment, network topology, integration map, event-driven, service map, layered architecture, request path,
trust boundaries. Loaded by the engine's registry; defines TYPES and runs nothing at import."""
import itertools

import diagram as core

# ---------- kinds: node look per kind (our palette; C4 prescribes no colours) ----------
C4_KINDS = {
    "person": {"tone": "plain", "shape": "actor", "label": "person"},
    "person_ext": {"tone": "soft", "shape": "actor", "label": "external person"},
    "system": {"tone": "ink", "shape": "box", "label": "software system"},
    "system_ext": {"tone": "soft", "shape": "box", "label": "external system"},
    "container": {"tone": "blue", "shape": "box", "label": "container"},
    "database": {"tone": "blue", "shape": "cylinder", "label": "database"},
    "queue": {"tone": "blue", "shape": "pill", "label": "queue / topic"},
    "component": {"tone": "teal", "shape": "box", "label": "component"},
}
for _k in ("container", "database", "queue", "component"):
    C4_KINDS[_k + "_ext"] = dict(C4_KINDS[_k], tone="soft", label="external " + C4_KINDS[_k]["label"])
C4_TAG = {"person": "Person", "system": "Software System", "container": "Container", "database": "Container",
          "queue": "Container", "component": "Component"}
C4_LEVEL = {"c4-context": {"person", "system"}, "c4-container": {"person", "system", "container", "database", "queue"},
            "c4-component": {"person", "system", "container", "database", "queue", "component"}}
C4_BOUNDARY = {"c4-context": "Enterprise", "c4-container": "Software System", "c4-component": "Container"}

INFRA_KINDS = {  # deployment and network topology
    "user": {"tone": "plain", "shape": "actor", "label": "user"},
    "internet": {"tone": "soft", "shape": "cloud", "label": "internet"},
    "dns": {"tone": "soft", "shape": "box", "label": "dns"},
    "cdn": {"tone": "lav", "shape": "box", "label": "cdn"},
    "gateway": {"tone": "lav", "shape": "hexagon", "label": "gateway"},
    "firewall": {"tone": "lav", "shape": "box", "label": "firewall / waf", "solid": False},
    "lb": {"tone": "lav", "shape": "pill", "label": "load balancer"},
    "endpoint": {"tone": "teal", "shape": "pill", "label": "private endpoint"},
    "compute": {"tone": "blue", "shape": "box", "label": "compute"},
    "container": {"tone": "blue", "shape": "box", "label": "container instance"},
    "function": {"tone": "blue", "shape": "rounded", "label": "function"},
    "database": {"tone": "green", "shape": "cylinder", "label": "database"},
    "storage": {"tone": "green", "shape": "cylinder", "label": "storage"},
    "queue": {"tone": "amber", "shape": "pill", "label": "queue"},
    "secret": {"tone": "soft", "shape": "box", "label": "key vault / secrets"},
    "server": {"tone": "plain", "shape": "box", "label": "server"},
    "external": {"tone": "soft", "shape": "box", "label": "external service", "dashed": True},
}
INFRA_ZONES = {  # frame look per group kind: frame "boundary" (grey dashed) or "group" (tinted)
    "cloud": {"frame": "boundary", "label": "cloud account"}, "region": {"frame": "boundary", "label": "region"},
    "onprem": {"frame": "boundary", "label": "on-premises"}, "zone": {"frame": "boundary", "label": "availability zone"},
    "environment": {"frame": "boundary", "label": "environment"},
    "network": {"frame": "group", "tone": "blue", "label": "VPC / VNet"},
    "subnet_public": {"frame": "group", "tone": "amber", "label": "public subnet"},
    "subnet_private": {"frame": "group", "tone": "teal", "label": "private subnet"},
    "cluster": {"frame": "group", "tone": "lav", "label": "cluster"},
    "node": {"frame": "group", "tone": "soft", "label": "node / VM"},
    "namespace": {"frame": "group", "tone": "lav", "label": "namespace"},
}
TRUST_ZONES = {
    "untrusted": {"frame": "group", "tone": "red", "label": "untrusted"},
    "dmz": {"frame": "group", "tone": "amber", "label": "DMZ / edge"},
    "internal": {"frame": "group", "tone": "blue", "label": "internal"},
    "restricted": {"frame": "group", "tone": "green", "label": "restricted data"},
    "third_party": {"frame": "boundary", "label": "third party"},
}
TRUST_KINDS = {
    "actor": {"tone": "plain", "shape": "actor", "label": "actor"},
    "process": {"tone": "plain", "shape": "rounded", "label": "process"},
    "store": {"tone": "plain", "shape": "cylinder", "label": "data store"},
    "external": {"tone": "soft", "shape": "box", "label": "external entity", "dashed": True},
    "control": {"tone": "lav", "shape": "hexagon", "label": "control"},
}
INTEG_KINDS = {
    "system": {"tone": "blue", "shape": "box", "label": "our system"},
    "external": {"tone": "soft", "shape": "box", "label": "external system", "dashed": True},
    "hub": {"tone": "lav", "shape": "hexagon", "label": "integration hub"},
    "store": {"tone": "green", "shape": "cylinder", "label": "data store"},
    "file": {"tone": "amber", "shape": "document", "label": "file drop"},
}
INTEG_VIA = {"api": {"label": "sync API"}, "event": {"style": "dashed", "tone": "lav", "label": "event / message"},
             "file": {"style": "dotted", "tone": "amber", "label": "file transfer"},
             "batch": {"style": "dashed", "tone": "blue", "label": "scheduled batch"},
             "db": {"style": "thick", "label": "shared database"}}
EVENT_KINDS = {
    "producer": {"tone": "blue", "shape": "box", "label": "producer"},
    "topic": {"tone": "lav", "shape": "rounded", "label": "topic / queue"},
    "consumer": {"tone": "teal", "shape": "box", "label": "consumer"},
    "dlq": {"tone": "red", "shape": "rounded", "label": "dead-letter queue"},
    "store": {"tone": "green", "shape": "cylinder", "label": "store"},
    "external": {"tone": "soft", "shape": "box", "label": "external", "dashed": True},
}
SERVICE_KINDS = {
    "gateway": {"tone": "lav", "label": "gateway / BFF"},
    "service": {"tone": "blue", "label": "service"},
    "worker": {"tone": "teal", "label": "worker"},
    "datastore": {"tone": "green", "shape": "cylinder", "label": "datastore"},
    "cache": {"tone": "green", "label": "cache"},
    "queue": {"tone": "amber", "label": "queue / topic"},
    "external": {"tone": "soft", "label": "external", "dashed": True},
}
SERVICE_STATES = {"down": {"tone": "red", "label": "down"}, "degraded": {"tone": "amber", "label": "degraded"},
                  "healthy": {"tone": "green", "label": "healthy"}}
TIER_KINDS = {
    "user": {"tone": "plain", "shape": "actor", "label": "user"},
    "client": {"tone": "plain", "shape": "rounded", "label": "client app"},
    "edge": {"tone": "lav", "shape": "box", "label": "edge"},
    "app": {"tone": "blue", "shape": "box", "label": "application"},
    "cache": {"tone": "green", "shape": "rounded", "label": "cache"},
    "store": {"tone": "green", "shape": "cylinder", "label": "store"},
    "external": {"tone": "soft", "shape": "box", "label": "external", "dashed": True},
}
LAYER_KINDS = {"component": {"tone": "blue", "label": "component"}, "store": {"tone": "green", "shape": "cylinder",
               "label": "store"}, "cross": {"tone": "lav", "label": "cross-cutting"}}
EDGE_SYNC = {"sync": {"label": "sync call"}, "async": {"style": "dashed", "label": "async message"}}


# ---------- shared helpers ----------
def flat(spec, nodes, edges, groups, kinds=None, states=None):
    """core.graph with one port per arrow (no shared trunk), so every labelled arrow keeps its own line and label;
    crowded ports are sent out sideways when that removes a defect (search_layout)."""
    def draw(_, sides):
        return core.graph(spec, nodes, _with_sides(edges, sides), groups, kinds, states, spread=True)
    return search_layout(draw, [None], edges)


def _trim(pts, a, b):
    """Polyline pts with a px cut from the start and b px from the end."""
    def cut(p, n):
        while n > 0 and len(p) > 1:
            (x0, y0), (x1, y1) = p[0], p[1]
            d = abs(x1 - x0) + abs(y1 - y0)
            if d > n:
                f = n / d
                return [(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)] + p[1:]
            p, n = p[1:], n - d
        return p
    return cut(cut(list(pts), a)[::-1], b)[::-1]


def _near(a, b, min_len=8, tol=5):
    """True when axis-parallel segments a and b run on (nearly) one line, within tol px, for more than min_len px."""
    (p, q), (r, t) = a, b
    for i in (0, 1):  # i = the axis both segments keep constant
        if abs(p[i] - q[i]) < .5 and abs(r[i] - t[i]) < .5 and abs(p[i] - r[i]) < tol:
            j = 1 - i
            return min(max(p[j], q[j]), max(r[j], t[j])) - max(min(p[j], q[j]), min(r[j], t[j])) > min_len
    return False


def route_issues(geo, frames=True):
    """Defects the base check.py does not count yet: arrows sharing (or running within 5px of) a line although they
    share an end (beyond the first or last 14px there), arrows crossing, arrows drawn along a frame border, and arrows
    running through a frame that holds neither end.
    -> [(problem, text)]. Used to pick the cleanest layout variant and in tests."""
    edges, out = geo.get("edges", []), []
    segs = lambda pts: list(zip(pts, pts[1:]))  # noqa: E731
    for k, e in enumerate(edges):
        for f in edges[k + 1:]:
            same_from, same_to = e["from"] == f["from"], e["to"] == f["to"]
            a = _trim(e["points"], 14 * same_from, 14 * same_to)
            b = _trim(f["points"], 14 * same_from, 14 * same_to)
            ml = 24 if {e["from"], e["to"]} & {f["from"], f["to"]} else 8  # a short join next to a shared box reads fine
            if any(_near(s, t, ml) for s in segs(a) for t in segs(b)):
                out.append(("arrows share a line", f"{e['from']} -> {e['to']} / {f['from']} -> {f['to']}"))
        for f in edges[k + 1:]:
            for (p, q) in segs(e["points"]):
                for (r, s) in segs(f["points"]):
                    h, v = ((p, q), (r, s)) if abs(p[1] - q[1]) < .5 else ((r, s), (p, q))
                    if abs(h[0][1] - h[1][1]) > .5 or abs(v[0][0] - v[1][0]) > .5:
                        continue
                    x, y = v[0][0], h[0][1]
                    if (min(h[0][0], h[1][0]) + 3 < x < max(h[0][0], h[1][0]) - 3
                            and min(v[0][1], v[1][1]) + 3 < y < max(v[0][1], v[1][1]) - 3):
                        out.append(("arrows cross", f"{e['from']} -> {e['to']} / {f['from']} -> {f['to']}"))
    for e in edges:  # a line drawn on a frame border reads as part of the frame
        for g in geo.get("containers", []):
            if g.get("kind") not in ("group", "boundary"):
                continue
            x0, y0, x1, y1 = g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"]
            sides = [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))]
            if any(_near(s, b, 20) for s in segs(e["points"]) for b in sides):
                out.append(("arrow along frame border", f"{e['from']} -> {e['to']} / {g.get('text') or g['id']}"))
    for e in edges if frames else []:
        for g in geo.get("containers", []):
            if g.get("kind") not in ("group", "boundary") or {e["from"], e["to"]} & set(g.get("members", [])):
                continue
            r = (g["x"] + 2, g["y"] + 2, g["w"] - 4, g["h"] - 4)
            if any(core.checker.seg_hits_rect(p, q, r) for p, q in segs(e["points"])):
                out.append(("arrow through foreign frame", f"{e['from']} -> {e['to']} / {g.get('text') or g['id']}"))
    return out


def _issues(res, frames):
    return core.checker.check(res[1])[0], route_issues(res[1], frames)


def _score(res, frames):
    probs, extra = _issues(res, frames)
    return (len(probs), sum(p != "arrows cross" for p, _ in extra), len(extra))


def search_layout(draw, starts, edges, frames=True, limit=4):
    """Cleanest drawing: draw(start, sides) for each start (e.g. with and without default ranks), then one or two of
    up to limit arrows (in a defect or leaving a crowded port, defects first; edges without from_side) sent out of
    another side, as {edge index: side}. Ranks base LAYOUT problems first, then shared lines and foreign frames, then
    crossings; stops at the first clean result. -> draw()'s result."""
    best, score, start = None, None, None
    for st in starts:
        try:
            res = draw(st, {})
        except core.LayoutError:
            continue
        sc = _score(res, frames)
        if score is None or sc < score:
            best, score, start = res, sc, st
        if sc == (0, 0, 0):
            return res
    if best is None:
        return draw(starts[0], {})  # raises the layout error with its fix
    outs = {}
    for e in edges:
        outs[e["from"]] = outs.get(e["from"], 0) + 1
    probs, extra = _issues(best, frames)
    worst = " ".join(x for p, x in probs + extra if p != "arrows cross")
    cross = " ".join(x for p, x in extra if p == "arrows cross")
    tier = [0 if f"{e['from']} -> {e['to']}" in worst else 1 if f"{e['from']} -> {e['to']}" in cross else 2
            for e in edges]
    ks = sorted((k for k, e in enumerate(edges) if not e.get("from_side") and (tier[k] < 2 or outs[e["from"]] > 1)),
                key=lambda k: tier[k])[:limit]
    combos = sorted((c for c in itertools.product((None, "left", "right", "top", "bottom"), repeat=len(ks))
                     if 0 < sum(map(bool, c)) <= 2), key=lambda c: sum(map(bool, c)))  # at most two changes
    for combo in combos:
        try:
            res = draw(start, {k: v for k, v in zip(ks, combo) if v})
        except core.LayoutError:
            continue
        sc = _score(res, frames)
        if sc < score:
            best, score = res, sc
        if sc == (0, 0, 0):
            break
    return best


def _with_sides(edges, sides):
    return [dict(e, from_side=sides[k]) if k in sides else e for k, e in enumerate(edges)]


def _kinds_err(spec, allowed, what="kind", key="nodes", field="kind"):
    return [f"node {n.get('id')}: {what} '{n.get(field)}' is not one of {', '.join(allowed)}"
            for n in spec.get(key) or [] if n.get(field) and n[field] not in allowed]


def _style_err(spec, allowed, why):
    st = spec.get("style") or "plain"
    return [] if st in allowed else [f"style '{st}' does not fit {spec['type']}: use {' or '.join(allowed)} ({why})"]


def _edges_with(spec, field, table):
    """Copy edges, mapping a type field (via, sync) onto edge kinds the base styles and puts in the legend."""
    out = []
    for e in spec.get("edges") or []:
        e = dict(e)
        if e.get(field):
            e["kind"] = f"{field}_{e[field]}"
        out.append(e)
    ek = dict({f"{field}_{k}": v for k, v in table.items()}, **(spec.get("edge_kinds") or {}))
    return out, dict(spec, edge_kinds=ek)


def _tagged(nodes, kinds):
    """Copy nodes; a node without a tag shows its kind's label, so the meaning is in the text, not only the colour."""
    out = []
    for n in nodes:
        n = dict(n)
        if not n.get("tag") and n.get("kind") in kinds:
            n["tag"] = kinds[n["kind"]]["label"]
        out.append(n)
    return out


# ---------- C4: context, container, component ----------
def _c4_key(n):
    return n.get("kind", "") + ("_ext" if n.get("external") else "")


def _c4_parts(spec, auto_rank=True):
    nodes, groups = [], []
    for g in spec.get("groups") or []:
        kind = g.get("kind") or C4_BOUNDARY[spec["type"]]
        groups.append(dict(g, label=f"{g['label']} [{kind}]"))
    for n in spec["nodes"]:
        t = C4_TAG[n["kind"]]
        tag = f"[{t}: {n['tech']}]" if n.get("tech") else f"[{t}]"
        if n.get("external"):
            tag = tag.replace("[", "[External ", 1) if n["kind"] in ("person", "system") else tag
        nodes.append({"id": n["id"], "label": n["label"], "tag": tag, "sub": n.get("desc"), "kind": _c4_key(n),
                      "group": n.get("group"), "rank": n.get("rank"), "dim": n.get("dim"), "href": n.get("href"),
                      "tip": n.get("tip")})
    edges = [dict(e, label=" ".join(x for x in (e.get("label"), f"[{e['tech']}]" if e.get("tech") else None) if x))
             for e in spec.get("edges") or []]
    if auto_rank and not any(n.get("rank") is not None for n in nodes):
        _c4_ranks(spec, nodes, edges)
    return nodes, edges, groups


def _c4_ranks(spec, nodes, edges):
    """Default ranks when the spec sets none: people and externals that send anything in at the entry side, externals
    that only receive at the far side, the rest by flow. Keeps actors left and providers right instead of scattered."""
    kind = {n["id"]: n for n in spec["nodes"]}
    outs = {e["from"] for e in edges}
    first = {i for i, n in kind.items() if n["kind"] == "person" or (n.get("external") and i in outs)}
    last = {i for i, n in kind.items() if n.get("external") and i not in outs and i not in first}
    rank, _ = core.ranks([n["id"] for n in nodes], edges, fixed={i: 0 for i in first})
    end = max(rank.values() or [0])
    for n in nodes:
        n["rank"] = end if n["id"] in last else rank[n["id"]]


def svg_c4(spec, core):
    def draw(auto, sides):
        nodes, edges, groups = _c4_parts(spec, auto)
        return core.graph(spec, nodes, _with_sides(edges, sides), groups, C4_KINDS, spread=True)
    body, geo = search_layout(draw, [True, False], spec.get("edges") or [])
    return body, geo, ["#S .dg-grp>rect{fill:none;stroke:var(--dg-muted);stroke-dasharray:7 4}"
                       "#S .dg-grp>text{fill:var(--dg-muted)}"]


VAGUE = {"uses", "use", "calls", "call", "talks to", "connects to", "interacts with", "sends", "reads", "writes",
         "data", "request", "requests"}


def validate_c4(spec):
    err = core.check_graph(spec) + _style_err(spec, ("plain",), "C4 has its own notation")
    allowed = C4_LEVEL[spec["type"]]
    for n in spec.get("nodes") or []:
        i, k = n.get("id"), n.get("kind")
        if k not in allowed:
            err.append(f"node {i}: kind '{k}' is not one of {', '.join(sorted(allowed))} for {spec['type']}")
            continue
        if not n.get("desc"):
            err.append(f"node {i}: desc required (C4 - every element has a short description)")
        if k in ("container", "database", "queue", "component") and not n.get("tech"):
            err.append(f"node {i}: tech required (C4 - every container and component names its technology)")
    kind = {n.get("id"): n.get("kind") for n in spec.get("nodes") or []}
    for e in spec.get("edges") or []:
        lab = " ".join(x for x in (e.get("label"), f"[{e['tech']}]" if e.get("tech") else None) if x)
        name = f"edge {e.get('from')} -> {e.get('to')}"
        if not e.get("label"):
            err.append(f"{name}: label required (C4 - every line says what it does)")
        elif str(e["label"]).strip().lower() in VAGUE:
            err.append(f"{name}: label '{e['label']}' says nothing - name the action (\"Charges card\", "
                       "\"Reads orders\")")
        if not e.get("tech") and {kind.get(e.get("from")), kind.get(e.get("to"))} <= {"container", "database", "queue"}:
            err.append(f"{name}: tech required between containers (protocol, e.g. \"JSON/HTTPS\", \"SQL\")")
        elif len(lab) > 36:
            err.append(f"edge {e.get('from')} -> {e.get('to')}: label plus [tech] over 36 characters: shorten it")
    if spec["type"] != "c4-context" and not spec.get("groups"):
        err.append(f"groups: one boundary for the {C4_BOUNDARY[spec['type']].lower()} in scope")
    return [x for x in err if "over 36 characters: shorten it or" not in x]  # the label + [tech] check above covers it


def mermaid_c4(spec):
    head = {"c4-context": "C4Context", "c4-container": "C4Container", "c4-component": "C4Component"}[spec["type"]]
    fn = {"person": "Person", "system": "System", "container": "Container", "database": "ContainerDb",
          "queue": "ContainerQueue", "component": "Component"}
    q = lambda s: '"' + str(s or "").replace('"', "'") + '"'  # noqa: E731
    out = [head, f"  title {spec['title']}", f"  %% Key: {spec['key']}", f"  %% Notice: {spec['notice']}"]

    def el(n, ind):
        f = fn[n["kind"]] + ("_Ext" if n.get("external") else "")
        args = [core.mm_id(n["id"]), q(n["label"])]
        if n["kind"] not in ("person", "system"):
            args.append(q(n.get("tech")))
        args.append(q(n.get("desc")))
        return f"{ind}{f}({', '.join(args)})"

    bfn = {"c4-context": "Enterprise_Boundary", "c4-container": "System_Boundary", "c4-component": "Container_Boundary"}
    for g in spec.get("groups") or []:
        out.append(f"  {bfn[spec['type']]}({core.mm_id('g_' + g['id'])}, {q(g['label'])}) {{")
        out += [el(n, "    ") for n in spec["nodes"] if n.get("group") == g["id"]]
        out.append("  }")
    out += [el(n, "  ") for n in spec["nodes"] if not n.get("group")]
    for e in spec.get("edges") or []:
        args = [core.mm_id(e["from"]), core.mm_id(e["to"]), q(e.get("label"))] + ([q(e["tech"])] if e.get("tech") else [])
        out.append(f"  Rel({', '.join(args)})")
    return "\n".join(out) + "\n"


# ---------- nested frames: deployment, network topology, trust boundaries ----------
def _tree(groups):
    kids = {None: []}
    for g in groups:
        kids.setdefault(g.get("parent"), []).append(g["id"])
        kids.setdefault(g["id"], [])
    return kids


def nest_layout(nodes, edges, groups, direction="LR", gap=None, cross_gap=24):
    """Nested frames (groups with parent) holding sized nodes [(n, w, h)]. Inside each frame the children (nodes and
    child frames) sit in columns by flow rank (LR; rows when TB); a group's "layout": "row" (side by side) or
    "column" (one under another) overrides that. Returns {"pos": {id: rect}, "groups": {gid: rect},
    "order": [gid outer first], "width", "height"}."""
    lr = direction != "TB"
    gs = {g["id"]: g for g in groups}
    kids = _tree(groups)
    child_nodes = {}
    for n, w, h in nodes:
        child_nodes.setdefault(n.get("group"), []).append(n["id"])
    size = {n["id"]: (w, h) for n, w, h in nodes}
    ids = [n["id"] for n, _, _ in nodes]
    rank, _ = core.ranks(ids, [e for e in edges if e["from"] in size and e["to"] in size])
    labs = [core.text_width(str(e["label"]), 11, True) + 40 for e in edges if e.get("label")]
    base_gap = gap or (56 if lr else (64 if labs else 56))

    def _gap(a, b):
        """Gap between two neighbouring columns: in LR wide enough for the labels of the arrows that cross it."""
        if gap or not lr:
            return base_gap
        sa = {x for k, i in a for x in (leaves(i) if k == "g" else [i])}
        sb = {x for k, i in b for x in (leaves(i) if k == "g" else [i])}
        w = [core.text_width(str(e["label"]), 11, True) + 28 for e in edges if e.get("label") and
             ((e["from"] in sa and e["to"] in sb) or (e["from"] in sb and e["to"] in sa))]
        return max([base_gap] + w)

    def _cross_gap(col):
        """Wider gap across the flow when an arrow links two members of one column (room for the line and label)."""
        sets = [set(leaves(i)) if k == "g" else {i} for k, i in col]
        inner = [e for e in edges if any(e["from"] in a and e["to"] in b for a in sets for b in sets if a is not b)]
        if not inner:
            return cross_gap
        lab = max([core.text_width(str(e["label"]), 11, True) + 30 for e in inner if e.get("label") and not lr] +
                  [44 if lr and any(e.get("label") for e in inner) else 0] + [40])
        return max(cross_gap, lab)

    def leaves(g):
        return child_nodes.get(g, []) + [x for k in kids.get(g, []) for x in leaves(k)]

    def _passes(g, inner):
        """True when an arrow leaves frame g from a box that is not inside one of its inner frames."""
        own = set(leaves(g)) - {x for k in inner for x in leaves(k)}
        return bool(inner) and any((e["from"] in own) != (e["to"] in own) and not
                                   (e["from"] in leaves(g) and e["to"] in leaves(g)) for e in edges)

    def crank(ch):
        kind, i = ch
        return rank[i] if kind == "n" else min(rank[x] for x in leaves(i))

    def box(g):
        """(w, h, [(kind, id, dx, dy)]) for frame g (None = canvas), offsets from its top-left."""
        chs = sorted([("g", k) for k in kids.get(g, [])] + [("n", i) for i in child_nodes.get(g, [])],
                     key=crank)  # source before target, also in row and column layout
        sub = {k: box(k) for kind, k in chs if kind == "g"}
        dims = {ch: (size[ch[1]] if ch[0] == "n" else sub[ch[1]][:2]) for ch in chs}
        mode = (gs.get(g) or {}).get("layout") or "flow"
        if mode == ("row" if lr else "column"):  # one line along the flow
            cols = [[ch] for ch in chs]
        elif mode in ("row", "column"):  # one line across the flow
            cols = [chs]
        else:
            byr = {}
            for ch in chs:
                byr.setdefault(crank(ch), []).append(ch)
            cols = [byr[r] for r in sorted(byr)]
        cgs = [_cross_gap(col) for col in cols]
        mains = [max((dims[ch][0] if lr else dims[ch][1]) for ch in col) for col in cols]
        crosses = [sum((dims[ch][1] if lr else dims[ch][0]) for ch in col) + cg * (len(col) - 1)
                   for col, cg in zip(cols, cgs)]
        gaps = [_gap(a, b) for a, b in zip(cols, cols[1:])] + [0]
        M = sum(mains) + sum(gaps)
        C = max(crosses or [0])
        lane = 48 if g and _passes(g, [i for k, i in chs if k == "g"]) else 0  # a free lane on the far side, so a
        # line leaving this frame need not cut through its inner frame
        pad = core.GP + 10 if g else 0  # room for a line between a box and its frame border
        lines = core.label_lines(gs[g]["label"], (M if lr else C) + 2 * pad) if g else []
        lab_w = max([core.text_width(x, 11, True) for x in lines] + [0])
        head = (len(lines) * 15 + 14) if g else 0
        shift = 0
        if g and not lr and cols:  # top-down: arrows enter the first row from above, so keep it clear of the label
            first = cols[0]
            x0 = (C - crosses[0]) / 2 + dims[first[0]][0] / 2
            shift = max(0, lab_w + 22 - (pad + x0))
        cw, ch_ = (M, C + shift + lane) if lr else (C + shift + lane, M)
        W, H = cw + 2 * pad, ch_ + pad * 2 + head
        if g:  # a frame is at least as wide as its label
            W = max(W, lab_w + 24)
        place, m = [], 0
        for col, mw, cs, cg, gp in zip(cols, mains, crosses, cgs, gaps):
            cpos = (C - cs) / 2 + (0 if lr else shift)
            for chh in col:
                w, h = dims[chh]
                if lr:
                    dx, dy = pad + m + (mw - w) / 2, head + pad + cpos
                    cpos += h + cg
                else:
                    dx, dy = pad + cpos, head + pad + m + (mw - h) / 2
                    cpos += w + cg
                place.append((chh[0], chh[1], dx, dy))
            m += mw + gp
        return W, H, place, sub

    pos, grect, order = {}, {}, []

    def put(g, x, y, b):
        W, H, place, sub = b
        if g:
            grect[g] = (x, y, W, H)
            order.append(g)
        for kind, i, dx, dy in place:
            if kind == "n":
                pos[i] = (x + dx, y + dy) + size[i]
            else:
                put(i, x + dx, y + dy, sub[i])

    root = box(None)
    put(None, core.MARGIN, core.MARGIN, root)
    return {"pos": pos, "groups": grect, "order": order, "width": root[0] + 2 * core.MARGIN,
            "height": root[1] + 2 * core.MARGIN}


def nested(spec, nodes, edges, groups, kinds, zones, direction=None):
    """Style nodes through the base (kinds, legend), lay out nested frames, draw, route. -> (body, geometry)."""
    st = core.style_graph(dict(spec, style="plain", view=None, collapse=None), nodes, edges, groups, kinds)
    sized = [(n, *core.size(n, n.get("max_w", spec.get("max_w", 200)))) for n in st["nodes"]]
    direction = direction or spec.get("direction")
    lay = nest_layout(sized, st["edges"], groups, direction or "LR")
    if lay["width"] > core.MAX_W and not direction:
        direction = "TB"
        lay = nest_layout(sized, st["edges"], groups, "TB")
    if lay["width"] > core.MAX_W:
        raise core.LayoutError(f"canvas would be {int(lay['width'])}px wide (max {core.MAX_W}): set direction TB, "
                               "give a wide group \"layout\": \"column\", shorten labels or split per zone")
    kids, members = _tree(groups), {}
    gs = {g["id"]: g for g in groups}

    def mem(g):
        if g not in members:
            members[g] = [n["id"] for n, _, _ in sized if n.get("group") == g] + [x for k in kids.get(g, []) for x in mem(k)]
        return members[g]

    def draw(_, sides):
        c = core.canvas(spec)
        used = []
        for g in lay["order"]:
            z = zones.get(gs[g].get("kind"), {})
            frame = gs[g].get("frame") or z.get("frame") or "group"
            tone = gs[g].get("tone") or z.get("tone")
            core.container(c, g, gs[g]["label"], *lay["groups"][g], members=mem(g), kind=frame,
                           tone=tone if frame == "group" else None)
            if gs[g].get("kind") in zones:
                used.append(gs[g]["kind"])
        for n, _, _ in sized:
            core.node(c, n, *lay["pos"][n["id"]])
        core.route(c, _with_sides(st["edges"], sides), direction or "LR", spread=True)
        leg = [{"label": zones[k]["label"], "tone": zones[k].get("tone") if zones[k].get("frame") != "boundary" else None,
                "dashed": True} for k in dict.fromkeys(used)]
        core.legend(c, leg + st["legend"])
        return core.finish(c)
    return search_layout(draw, [None], st["edges"])


def validate_nested(spec, kinds, zones, why):
    err = core.check_graph(spec) + _kinds_err(spec, kinds)
    err += _style_err(spec, ("plain",), why)
    gids = [g.get("id") for g in spec.get("groups") or []]
    if spec.get("view") or spec.get("collapse"):
        err.append(f"{spec['type']}: view and collapse do not apply to nested frames - split per zone instead")
    for g in spec.get("groups") or []:
        if g.get("parent") and g["parent"] not in gids:
            err.append(f"group {g.get('id')}: parent '{g['parent']}' is not a group id")
        if g.get("kind") and g["kind"] not in zones:
            err.append(f"group {g.get('id')}: kind '{g['kind']}' is not one of {', '.join(zones)}")
        if (g.get("layout") or "flow") not in ("flow", "row", "column"):
            err.append(f"group {g.get('id')}: layout '{g['layout']}' is not flow, row or column")
        if not g.get("label"):
            err.append(f"group {g.get('id')}: needs a label")
    par = {g.get("id"): g.get("parent") for g in spec.get("groups") or []}
    for g in par:
        seen, p = {g}, par.get(g)
        while p:
            if p in seen:
                err.append(f"group {g}: parent chain loops back to '{p}'")
                break
            seen.add(p)
            p = par.get(p)
    has = {n.get("group") for n in spec.get("nodes") or []}
    for g in gids:
        def any_leaf(x):
            return x in has or any(any_leaf(k) for k, v in par.items() if v == x)
        if not any_leaf(g):
            err.append(f"group {g}: holds no node - add one or drop the group")
    return err


def mermaid_nested(spec, nodes, edges, groups, kinds, zones=None):
    st = core.style_graph(dict(spec, style="plain", view=None, collapse=None), nodes, edges, groups, kinds)
    out = core.mermaid_head(spec, f"flowchart {spec.get('direction') or 'LR'}")
    kids = _tree(groups)
    gs = {g["id"]: g for g in groups}
    by = {}
    for n in st["nodes"]:
        by.setdefault(n.get("group"), []).append(n)

    def nd(n, ind):
        a, b = core.MM_SHAPE.get(n.get("shape") or "rounded", ("(", ")"))
        lab = " · ".join(str(x) for x in (n["label"], n.get("tag"), n.get("sub")) if x)
        return f"{ind}{core.mm_id(n['id'])}{a}{core.mm_text(lab)}{b}"

    def sg(g, ind):
        out.append(f"{ind}subgraph {core.mm_id('g_' + g)} [{core.mm_text(gs[g]['label'])}]")
        for k in kids.get(g, []):
            sg(k, ind + "  ")
        out.extend(nd(n, ind + "  ") for n in by.get(g, []))
        out.append(f"{ind}end")

    for g in kids[None]:
        sg(g, "  ")
    out.extend(nd(n, "  ") for n in by.get(None, []))
    for e in st["edges"]:
        link = {"solid": "-->", "dashed": "-.->", "dotted": "-.->", "thick": "==>"}[e.get("style") or "solid"]
        lab = f"|{core.mm_text(e['label'])}|" if e.get("label") else ""
        out.append(f"  {core.mm_id(e['from'])} {link}{lab} {core.mm_id(e['to'])}")
    used = {}
    for n in st["nodes"]:
        if (n.get("tone") or "plain") in core.MM_TONE:
            used.setdefault(n["tone"], []).append(core.mm_id(n["id"]))
    for t, ids in used.items():
        f, s = core.MM_TONE[t]
        out.append(f"  classDef {t} fill:{f},stroke:{s}" + (",color:#FFFFFF" if t == "ink" else ""))
        out.append(f"  class {','.join(ids)} {t}")
    for g in groups:  # frames tinted as in the SVG, so the key holds for Markdown readers too
        z = (zones or {}).get(g.get("kind"), {})
        frame, tone = g.get("frame") or z.get("frame") or "group", g.get("tone") or z.get("tone")
        if frame == "boundary":
            out.append(f"  style {core.mm_id('g_' + g['id'])} fill:none,stroke:#5B6068,stroke-dasharray:6 4")
        elif tone in core.MM_TONE:
            f, s = core.MM_TONE[tone]
            out.append(f"  style {core.mm_id('g_' + g['id'])} fill:{f},stroke:{s},stroke-dasharray:6 4")
    return "\n".join(out) + "\n"


def _infra(spec):
    return _tagged(spec["nodes"], INFRA_KINDS), spec.get("edges") or [], spec.get("groups") or []


def svg_infra(spec, core):
    return nested(spec, *_infra(spec), INFRA_KINDS, INFRA_ZONES)


def validate_infra(spec):
    return validate_nested(spec, INFRA_KINDS, INFRA_ZONES, "frames nest; graph styles need flat layer columns")


def mermaid_infra(spec):
    return mermaid_nested(spec, *_infra(spec), INFRA_KINDS, INFRA_ZONES)


def _trust(spec):
    """Number every arrow that crosses a zone border (T1, T2, ...) so the text can list the control per crossing."""
    zone = {n["id"]: n.get("group") for n in spec["nodes"]}
    edges, k = [], 0
    for e in spec.get("edges") or []:
        e = dict(e)
        if zone.get(e["from"]) != zone.get(e["to"]) and spec.get("number_crossings", True):
            k += 1
            e["label"] = f"T{k} " + (e.get("label") or "")
            e["label"] = e["label"].strip()
            e.setdefault("style", "thick")
        edges.append(e)
    return _tagged(spec["nodes"], TRUST_KINDS), edges, spec.get("groups") or []


def svg_trust(spec, core):
    return nested(spec, *_trust(spec), TRUST_KINDS, TRUST_ZONES)


def validate_trust(spec):
    err = validate_nested(spec, TRUST_KINDS, TRUST_ZONES, "zones nest; graph styles need flat layer columns")
    err += [f"edge {e.get('from')} -> {e.get('to')}: label over 33 characters (T-number added): shorten it"
            for e in spec.get("edges") or [] if len(str(e.get("label", ""))) > 33]
    return err


def mermaid_trust(spec):
    return mermaid_nested(spec, *_trust(spec), TRUST_KINDS, TRUST_ZONES)


# ---------- flat node-edge types on the base graph ----------
def svg_integ(spec, core):
    edges, s = _edges_with(spec, "via", INTEG_VIA)
    return flat(s, _tagged(spec["nodes"], INTEG_KINDS), edges, spec.get("groups"), kinds=INTEG_KINDS)


def validate_integ(spec):
    err = core.check_graph(spec) + core.check_style(spec) + _kinds_err(spec, INTEG_KINDS)
    err += [f"edge {e.get('from')} -> {e.get('to')}: via '{e['via']}' is not one of {', '.join(INTEG_VIA)}"
            for e in spec.get("edges") or [] if e.get("via") and e["via"] not in INTEG_VIA]
    return err


def mermaid_integ(spec):
    edges, s = _edges_with(spec, "via", INTEG_VIA)
    return core.mermaid_graph(s, _tagged(spec["nodes"], INTEG_KINDS), edges, spec.get("groups"), kinds=INTEG_KINDS)


def _events(spec):
    """Arrows into a topic are publishes (solid), out of a topic subscriptions (dashed); the label is the event."""
    kind = {n["id"]: n.get("kind") for n in spec["nodes"]}
    edges = []
    for e in spec.get("edges") or []:
        e = dict(e)
        if kind.get(e["from"]) in ("topic", "dlq") and "style" not in e:
            e["style"] = "dashed"
        if kind.get(e["to"]) == "dlq":
            e.setdefault("kind", "failure")
        edges.append(e)
    nodes, groups = _tagged(spec["nodes"], EVENT_KINDS), list(spec.get("groups") or [])
    tgs = {n.get("group") for n in nodes if n.get("kind") == "topic"}
    others = [n for n in nodes if n.get("kind") in ("producer", "consumer")]
    if len(tgs) == 1 and not any(n.get("group") for n in others):  # columns: producers | topics | consumers
        broker = tgs.pop() or "topics"
        auto = {"producer": "producers", "topic": broker, "consumer": "consumers"}
        nodes = [dict(n, group=auto[n["kind"]]) if n.get("kind") in auto else n for n in nodes]
        used = {n.get("group") for n in nodes}
        have = {g["id"]: g for g in groups}
        groups = [have.get(k, {"id": k, "label": k}) for k in ("producers", broker, "consumers")
                  if k in used] + [g for g in groups if g["id"] != broker]
        spec = dict(spec, group_layout=spec.get("group_layout") or "columns")
    return spec, nodes, edges, groups


def svg_events(spec, core):
    return flat(*_events(spec), kinds=EVENT_KINDS)


def validate_events(spec):
    err = core.check_graph(spec) + core.check_style(spec) + _kinds_err(spec, EVENT_KINDS)
    kind = {n.get("id"): n.get("kind") for n in spec.get("nodes") or []}
    if "topic" not in kind.values():
        err.append("nodes: at least one kind 'topic' (the channel events go through)")
    for e in spec.get("edges") or []:
        if kind.get(e.get("from")) not in ("topic", "dlq") and kind.get(e.get("to")) not in ("topic", "dlq"):
            err.append(f"edge {e.get('from')} -> {e.get('to')}: every arrow touches a topic - publish into one or "
                       "subscribe from one (direct calls belong in service-map)")
    return err


def mermaid_events(spec):
    return core.mermaid_graph(*_events(spec), kinds=EVENT_KINDS)


def _services(spec):
    edges, s = _edges_with(spec, "call", EDGE_SYNC)
    nodes = [dict(n, sub=" · ".join(x for x in (n.get("sub"), n["state"]) if x)) if n.get("state") else n
             for n in _tagged(spec["nodes"], SERVICE_KINDS)]  # the state word, not only its colour
    groups = [dict(g, tag=g.get("tag") or "tier") for g in spec.get("groups") or []]  # overview tag "tier · n items"
    return s, nodes, edges, groups


def svg_services(spec, core):
    s, n, e, g = _services(spec)
    return flat(s, n, e, g, kinds=SERVICE_KINDS, states=SERVICE_STATES)


def validate_services(spec):
    err = core.check_graph(spec) + core.check_style(spec) + _kinds_err(spec, SERVICE_KINDS)
    states = dict(SERVICE_STATES, **(core.AIRFLOW_STATES if spec.get("style") == "airflow" else {}),
                  **(spec.get("states") or {}))
    err += _kinds_err(spec, states, "state", field="state")
    err += [f"edge {e.get('from')} -> {e.get('to')}: call '{e['call']}' is not sync or async"
            for e in spec.get("edges") or [] if e.get("call") and e["call"] not in EDGE_SYNC]
    return err


def mermaid_services(spec):
    s, n, e, g = _services(spec)
    return core.mermaid_graph(s, n, e, g, kinds=SERVICE_KINDS, states=SERVICE_STATES)


def _path(spec):
    """Number the hops in spec order (1, 2, ...); a hop's label is protocol or what it does, plus an optional budget."""
    edges = []
    for k, e in enumerate(spec.get("edges") or [], 1):
        e = dict(e)
        bits = [f"{k}" if spec.get("numbered", True) else None, e.get("label"), e.get("ms") and f"{e['ms']} ms"]
        e["label"] = " ".join(str(b) for b in bits if b)
        if e.get("async"):
            e["style"] = "dashed"
        edges.append(e)
    nodes = []
    for n in _tagged(spec["nodes"], TIER_KINDS):
        if n.get("p95"):
            n["sub"] = " · ".join(x for x in (n.get("sub"), f"p95 {n['p95']}") if x)
        nodes.append(n)
    return nodes, edges, spec.get("groups")


def svg_path(spec, core):
    return flat(dict(spec, group_layout=spec.get("group_layout") or "columns"), *_path(spec), kinds=TIER_KINDS)


def validate_path(spec):
    err = core.check_graph(spec) + core.check_style(spec) + _kinds_err(spec, TIER_KINDS)
    err += _style_err(spec, ("plain",), "a request path is one numbered route, not a dependency graph")
    for k, e in enumerate(spec.get("edges") or [], 1):
        lab = " ".join(str(b) for b in (k, e.get("label"), e.get("ms") and f"{e['ms']} ms") if b)
        if len(lab) > 36:
            err.append(f"edge {e.get('from')} -> {e.get('to')}: hop label '{lab}' over 36 characters: shorten it")
    if not spec.get("groups"):
        err.append("groups: one group per tier (edge, web, app, data), in request order")
    return [x for x in err if "label over 36 characters: shorten it or" not in x]


def mermaid_path(spec):
    return core.mermaid_graph(spec, *_path(spec), kinds=TIER_KINDS)


# ---------- layered architecture: bands, optional cross-cutting column, layer-rule check ----------
def _layer_edges(spec):
    """Mark arrows that break the layer rule red: upward calls always, skipped layers when rule is strict."""
    at = {it["id"]: i for i, l in enumerate(spec["layers"]) for it in l["items"]}
    edges = []
    for e in spec.get("edges") or []:
        e = dict(e)
        a, b = at.get(e["from"]), at.get(e["to"])
        if a is not None and b is not None and (b < a or (spec.get("rule", "strict") == "strict" and b > a + 1)):
            e.setdefault("tone", "red")
            e["_bad"] = True
        edges.append(e)
    return edges


def svg_layered(spec, core):
    c = core.canvas(spec)
    hw, gx, gy = spec.get("header_w", 130), 24, 18
    side = spec.get("cross_cutting")
    side_sized = [(dict(n, kind=n.get("kind") or "cross", free=True), 0, 0) for n in (side or {}).get("items", [])]
    st = core.style_graph(dict(spec, style="plain", view=None, collapse=None),
                          [dict(it, kind=it.get("kind") or "component") for l in spec["layers"] for it in l["items"]]
                          + [n for n, _, _ in side_sized], _layer_edges(spec), [], kinds=LAYER_KINDS)
    look = {n["id"]: n for n in st["nodes"]}
    side_w = 0
    if side:
        ss = [(look[n["id"]], *core.size(look[n["id"]], 170)) for n, _, _ in side_sized]
        side_w = max(w for _, w, _ in ss) + 2 * core.GP
    avail = core.MAX_W - 2 * core.MARGIN - hw - 32 - (side_w + 20 if side else 0)
    rows = []
    for l in spec["layers"]:
        sized = [(look[it["id"]], *core.size(look[it["id"]], spec.get("max_w", 200))) for it in l["items"]]
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
    edges = st["edges"]
    y, band_gap = core.MARGIN, 44 if edges else 12
    for l, lines in rows:
        lh = sum(max(s[2] for s in ln) for ln in lines) + gy * (len(lines) - 1) + 32
        lh = max(lh, len(core.label_lines(l["label"], hw)) * 15 + 20)
        core.container(c, l["id"], l["label"], core.MARGIN, y, W, lh, members=[s[0]["id"] for ln in lines for s in ln],
                       kind="band", header_w=hw)
        yy = y + 16
        for ln in lines:
            rh = max(s[2] for s in ln)
            tw = sum(s[1] for s in ln) + gx * (len(ln) - 1)
            x = core.MARGIN + hw + 24 + (inner_w - tw) / 2
            for n, w, h in ln:
                core.node(c, n, x, yy + (rh - h) / 2, w, h)
                x += w + gx
            yy += rh + gy
        y += lh + band_gap
    total_h = y - band_gap - core.MARGIN
    if side:
        sx = core.MARGIN + W + 20
        lines = core.label_lines(side["label"], side_w)
        head = len(lines) * 15 + 14
        need = head + sum(h for _, _, h in ss) + gy * (len(ss) - 1) + 2 * core.GP
        hh = max(total_h, need)
        core.container(c, "cross-cutting", side["label"], sx, core.MARGIN, side_w, hh, members=[n["id"] for n, _, _ in ss])
        yy = core.MARGIN + head + core.GP + (hh - need) / 2
        for n, w, h in ss:
            core.node(c, n, sx + (side_w - w) / 2, yy, w, h)
            yy += h + gy
    if (core.MARGIN + W + (side_w + 20 if side else 0)) + core.MARGIN > core.MAX_W + 1:
        raise core.LayoutError("layers would exceed 1000px: shorten item labels, fewer items per layer, or drop "
                               "the cross-cutting column into its own band")
    core.route(c, [{k: v for k, v in e.items() if k != "_bad"} for e in edges], "TB", spread=True)  # own port: a red
    # rule break never shares its last segment with an allowed call
    leg = st["legend"] + ([{"label": "breaks the layer rule", "edge": {"tone": "red"}}] if any(e.get("_bad") for e in edges) else [])
    core.legend(c, leg)
    return core.finish(c)


def validate_layered(spec):
    err = []
    layers = spec.get("layers") or []
    if len(layers) < 2:
        err.append("layers: at least two layers [{id, label, items}], top layer first")
    items = [it for l in layers for it in l.get("items") or []] + list((spec.get("cross_cutting") or {}).get("items") or [])
    for l in layers:
        if not l.get("id") or not l.get("label") or not l.get("items"):
            err.append(f"layer {l.get('id')}: needs id, label and items")
    if spec.get("cross_cutting") and not (spec["cross_cutting"].get("label") and spec["cross_cutting"].get("items")):
        err.append("cross_cutting: needs label and items")
    if spec.get("rule", "strict") not in ("strict", "relaxed"):
        err.append("rule: strict (only the layer directly below) or relaxed (any layer below)")
    err += core.check_graph({"nodes": items, "edges": spec.get("edges") or []})
    err += _kinds_err({"nodes": items}, LAYER_KINDS)
    lids = [l.get("id") for l in layers]
    if len(set(lids)) != len(lids) or "cross-cutting" in lids:
        err.append("layers: ids must be unique and not 'cross-cutting'")
    return err


def mermaid_layered(spec):
    out = core.mermaid_head(spec, "flowchart TB")
    for l in spec["layers"] + ([dict(spec["cross_cutting"], id="cross-cutting")] if spec.get("cross_cutting") else []):
        out.append(f"  subgraph {core.mm_id('l_' + l['id'])} [{core.mm_text(l['label'])}]")
        out.append("    direction LR")
        for n in l["items"]:
            a, b = core.MM_SHAPE.get(n.get("shape") or "rounded", ("(", ")"))
            out.append(f"    {core.mm_id(n['id'])}{a}{core.mm_text(n['label'])}{b}")
        out.append("  end")
    bad = []
    for k, e in enumerate(_layer_edges(spec)):  # real edges first: linkStyle counts links in definition order
        lab = f"|{core.mm_text(e['label'])}|" if e.get("label") else ""
        out.append(f"  {core.mm_id(e['from'])} -->{lab} {core.mm_id(e['to'])}")
        if e.get("_bad"):
            bad.append(str(k))
    ls = spec["layers"]
    for a, b in zip(ls, ls[1:]):
        out.append(f"  {core.mm_id('l_' + a['id'])} ~~~ {core.mm_id('l_' + b['id'])}")
    if bad:
        out.append(f"  linkStyle {','.join(bad)} stroke:#A12D2D")
    return "\n".join(out) + "\n"


TYPES = {
    "c4-context": {"svg": svg_c4, "mermaid": mermaid_c4, "validate": validate_c4,
                   "doc": "C4 level 1: the system in scope, its people and the external systems it talks to"},
    "c4-container": {"svg": svg_c4, "mermaid": mermaid_c4, "validate": validate_c4,
                     "doc": "C4 level 2: apps and data stores inside one system boundary, with technology"},
    "c4-component": {"svg": svg_c4, "mermaid": mermaid_c4, "validate": validate_c4,
                     "doc": "C4 level 3: components inside one container boundary, with technology"},
    "deployment": {"svg": svg_infra, "mermaid": mermaid_infra, "validate": validate_infra,
                   "doc": "where instances run in one environment: nested deployment nodes (cluster, node, namespace)"},
    "network-topology": {"svg": svg_infra, "mermaid": mermaid_infra, "validate": validate_infra,
                         "doc": "VPC/VNet, subnets, gateways, firewalls, private endpoints as nested frames"},
    "integration-map": {"svg": svg_integ, "mermaid": mermaid_integ, "validate": validate_integ,
                        "doc": "systems and how they exchange data (API, event, file, batch, shared DB); plain or dbt"},
    "event-driven": {"svg": svg_events, "mermaid": mermaid_events, "validate": validate_events,
                     "doc": "producers, topics/queues, consumers, dead-letter queues; plain or dbt"},
    "service-map": {"svg": svg_services, "mermaid": mermaid_services, "validate": validate_services,
                    "doc": "microservice dependencies, sync/async calls, health or impact (dim); plain or dbt"},
    "layered-architecture": {"svg": svg_layered, "mermaid": mermaid_layered, "validate": validate_layered,
                             "doc": "layers top-down, cross-cutting column, arrows breaking the layer rule in red"},
    "request-path": {"svg": svg_path, "mermaid": mermaid_path, "validate": validate_path,
                     "doc": "one request through the tiers, numbered hops, optional latency budget"},
    "trust-boundaries": {"svg": svg_trust, "mermaid": mermaid_trust, "validate": validate_trust,
                         "doc": "trust zones (nested), flows crossing a boundary numbered T1, T2 with their control"},
}
