"""Layout checker for a diagram geometry record (written by diagram.py --geometry, or built from a spec).
Usage: python check.py [--routes] geometry.json|spec.json [...]
Prints `LAYOUT <id> | <problem> | <text>` per problem and `WARN <id> | ...` per warning; exit 1 on any problem.
Problems: canvas over 1000px, boxes overlapping, a box across a group border, arrow through a box, two arrows on one
line (a shared trunk only when both lines look the same), label on a box / foreign line / another label / group
border, text outside its box, decision with fewer than 2 exits.
Warning: node with no arrow (skipped when geometry "connected" is false or the node is "free").
--routes also prints `ROUTE <id> | <issue> | <text>` from route_issues (advisory, no effect on the exit code)."""
import json
import sys
from pathlib import Path

MAX_W = 1000


def seg_hits_rect(p, q, r):
    """True when segment p-q passes through the open rectangle r = (x, y, w, h) (Liang-Barsky clip)."""
    x0, y0, x1, y1 = r[0], r[1], r[0] + r[2], r[1] + r[3]
    if x1 <= x0 or y1 <= y0:
        return False
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pp == 0:
            if qq <= 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 >= t1:
                return False
    return t1 - t0 > 1e-6


def straddles(r, g, pad=2.0):
    """True when rect r = (x, y, w, h) lies partly inside and partly outside rect g (it sits on g's border)."""
    hit = r[0] < g[0] + g[2] + pad and g[0] < r[0] + r[2] + pad and r[1] < g[1] + g[3] + pad and g[1] < r[1] + r[3] + pad
    inside = r[0] >= g[0] + pad and r[1] >= g[1] + pad and r[0] + r[2] <= g[0] + g[2] - pad and r[1] + r[3] <= g[1] + g[3] - pad
    return hit and not inside


def _ov(a, b, pad=0.0):
    return (a["x"] < b["x"] + b["w"] - pad and b["x"] < a["x"] + a["w"] - pad
            and a["y"] < b["y"] + b["h"] - pad and b["y"] < a["y"] + a["h"] - pad)


def _inside(a, b, tol=0.5):
    return (a["x"] >= b["x"] - tol and a["y"] >= b["y"] - tol and a["x"] + a["w"] <= b["x"] + b["w"] + tol
            and a["y"] + a["h"] <= b["y"] + b["h"] + tol)


def _shrink(b, d):
    return (b["x"] + d, b["y"] + d, b["w"] - 2 * d, b["h"] - 2 * d)


def _own(b):
    """A box's own arrows may end on its outline: pill and hexagon ends curve or slope inside the rectangle."""
    x, y, w, h = _shrink(b, 2)
    d = {"pill": b["h"] / 2, "hexagon": b["h"] / 4}.get(b.get("shape"), 0)
    return (x + d, y, w - 2 * d, h)


def _segs(e):
    pts = e["points"]
    return list(zip(pts, pts[1:]))


def check(geo):
    """geometry dict -> (problems [(problem, text)], warnings [(problem, text)])."""
    P, W = [], []
    nodes, conts, edges, labels = geo.get("nodes", []), geo.get("containers", []), geo.get("edges", []), geo.get("labels", [])
    if geo.get("width", 0) > MAX_W:
        P.append(("canvas too wide", f"{geo['width']}px > {MAX_W}px: set direction TB, shorten labels or split the diagram"))
    for b in nodes + conts + labels:
        if b["x"] < -0.5 or b["y"] < -0.5 or b["x"] + b["w"] > geo.get("width", 1e9) + 0.5 or \
                b["y"] + b["h"] > geo.get("height", 1e9) + 0.5:
            P.append(("outside canvas", b.get("text") or b.get("id", "")))
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if _ov(a, b, 0.5):
                P.append(("boxes overlap", f"{a['text'] or a['id']} / {b['text'] or b['id']}"))
    for g in conts:
        for n in nodes:
            member = n["id"] in g.get("members", [])
            if member and not _inside(n, g):
                P.append(("member outside its group", f"{n['text'] or n['id']} / {g['text'] or g['id']}"))
            elif not member and _ov(n, g, 0.5):
                P.append(("box inside foreign group" if _inside(n, g) else "box across group border",
                          f"{n['text'] or n['id']} / {g['text'] or g['id']}"))
    for i, a in enumerate(conts):
        for b in conts[i + 1:]:
            if _ov(a, b, 0.5) and not _inside(a, b) and not _inside(b, a):
                P.append(("groups overlap", f"{a['text'] or a['id']} / {b['text'] or b['id']}"))
    for k, e in enumerate(edges):
        name = f"{e.get('from')} -> {e.get('to')}"
        for p, q in _segs(e):
            for n in nodes:
                if n["id"] in (e.get("from"), e.get("to")):
                    if seg_hits_rect(p, q, _own(n)):
                        P.append(("arrow through its own box", f"{name} / {n['text'] or n['id']}"))
                elif seg_hits_rect(p, q, _shrink(n, 0.5)):
                    P.append(("arrow through box", f"{name} / {n['text'] or n['id']}"))
        for f in edges[k + 1:]:
            ends = {e.get("from"), e.get("to")} & {f.get("from"), f.get("to")}
            if ends and e.get("look") == f.get("look"):
                continue  # a shared trunk is fine only when both lines look the same (kind, style, tone, dim)
            if _shared(e, f, 12 if ends else 8):  # different looks from one corner (diamond) share only the stub
                P.append(("two arrows share a line", f"{name} / {f.get('from')} -> {f.get('to')}"))
    for i, lb in enumerate(labels):
        r = (lb["x"] + 1, lb["y"] + 1, lb["w"] - 2, lb["h"] - 2)
        for n in nodes:
            if _ov(lb, n, 1):
                P.append(("label on box", f"{lb['text']} / {n['text'] or n['id']}"))
        for k, e in enumerate(edges):
            if k == lb.get("edge"):
                continue
            if any(seg_hits_rect(p, q, r) for p, q in _segs(e)):
                P.append(("label on foreign line", f"{lb['text']} / {e.get('from')} -> {e.get('to')}"))
        if lb.get("kind") != "container":
            for g in conts:
                if straddles((lb["x"], lb["y"], lb["w"], lb["h"]), (g["x"], g["y"], g["w"], g["h"]), 0.5):
                    P.append(("label across group border", f"{lb['text']} / {g['text'] or g['id']}"))
        for o in labels[i + 1:]:
            if _ov(lb, o, 1):
                P.append(("labels overlap", f"{lb['text']} / {o['text']}"))
    for n in nodes:
        ix, iy, iw, ih = n["inner"]
        box = {"x": ix - 1, "y": iy - 1, "w": iw + 2, "h": ih + 2}
        for ln in n.get("lines", []):
            if not _inside(ln, box, 0.5):
                P.append(("text overflows box", f"{ln['text']} / {n['text'] or n['id']}"))
    outs = {}
    touched = set()
    for e in edges:
        outs[e.get("from")] = outs.get(e.get("from"), 0) + 1
        touched |= {e.get("from"), e.get("to")}
    for n in nodes:
        if n.get("decision") and outs.get(n["id"], 0) < 2:
            P.append(("decision with fewer than 2 exits", n["text"] or n["id"]))
        if geo.get("connected", True) and not n.get("free") and n["id"] not in touched:
            W.append(("unconnected node", n["text"] or n["id"]))
    return P, W


def collinear_overlap(a, b, min_len=8):
    """True when axis-parallel segments a and b lie on one line and overlap by more than min_len px."""
    (p, q), (r, s) = a, b
    if abs(p[0] - q[0]) < .5 and abs(r[0] - s[0]) < .5 and abs(p[0] - r[0]) < .5:
        return min(max(p[1], q[1]), max(r[1], s[1])) - max(min(p[1], q[1]), min(r[1], s[1])) > min_len
    if abs(p[1] - q[1]) < .5 and abs(r[1] - s[1]) < .5 and abs(p[1] - r[1]) < .5:
        return min(max(p[0], q[0]), max(r[0], s[0])) - max(min(p[0], q[0]), min(r[0], s[0])) > min_len
    return False


def _shared(e, f, min_len=8):
    return any(collinear_overlap(a, b, min_len) for a in _segs(e) for b in _segs(f))


def _near(a, b, min_len=8, tol=5):
    """True when axis-parallel segments a and b run on (nearly) one line, within tol px, for more than min_len px."""
    (p, q), (r, t) = a, b
    for i in (0, 1):  # i = the axis both segments keep constant
        if abs(p[i] - q[i]) < .5 and abs(r[i] - t[i]) < .5 and abs(p[i] - r[i]) < tol:
            j = 1 - i
            return min(max(p[j], q[j]), max(r[j], t[j])) - max(min(p[j], q[j]), min(r[j], t[j])) > min_len
    return False


def _trim(pts, a, b):
    """Polyline pts with a px cut from the start and b px from the end."""
    def cut(p, n):
        while n > 0 and len(p) > 1:
            (x0, y0), (x1, y1) = p[0], p[1]
            d = abs(x1 - x0) + abs(y1 - y0)
            if d > n:
                return [(x0 + (x1 - x0) * n / d, y0 + (y1 - y0) * n / d)] + list(p[1:])
            p, n = p[1:], n - d
        return list(p)
    return cut(cut(list(pts), a)[::-1], b)[::-1]


def route_issues(geo):
    """Advisory routing issues check() does not count (a same-look trunk stays fine):
    arrows of different looks running within 5px of each other beyond 14px from a shared box, unrelated arrows
    within 5px, arrows crossing, and arrows through a group or boundary frame that holds neither end.
    Families use it to pick the cleanest layout variant; reviewers read it. -> [(issue, text)]"""
    edges, conts, out = geo.get("edges", []), geo.get("containers", []), []
    for k, e in enumerate(edges):
        for f in edges[k + 1:]:
            ends = {e.get("from"), e.get("to")} & {f.get("from"), f.get("to")}
            if ends and e.get("look") == f.get("look"):
                continue
            sf, st = e.get("from") == f.get("from"), e.get("to") == f.get("to")
            a, b = _trim(e["points"], 14 * sf, 14 * st), _trim(f["points"], 14 * sf, 14 * st)
            if any(_near(s, t, 24 if ends else 8) for s in zip(a, a[1:]) for t in zip(b, b[1:])):
                out.append(("arrows run on one line", f"{e.get('from')} -> {e.get('to')} / {f.get('from')} -> {f.get('to')}"))
            hit = False
            for p, q in _segs(e):
                for r, s in _segs(f):
                    h, v = ((p, q), (r, s)) if abs(p[1] - q[1]) < .5 else ((r, s), (p, q))
                    if hit or abs(h[0][1] - h[1][1]) > .5 or abs(v[0][0] - v[1][0]) > .5:
                        continue
                    x, y = v[0][0], h[0][1]
                    hit = (min(h[0][0], h[1][0]) + 3 < x < max(h[0][0], h[1][0]) - 3
                           and min(v[0][1], v[1][1]) + 3 < y < max(v[0][1], v[1][1]) - 3)
            if hit:
                out.append(("arrows cross", f"{e.get('from')} -> {e.get('to')} / {f.get('from')} -> {f.get('to')}"))
    for e in edges:
        for g in conts:
            if g.get("kind") not in ("group", "boundary") or {e.get("from"), e.get("to")} & set(g.get("members", [])):
                continue
            r = (g["x"] + 2, g["y"] + 2, g["w"] - 4, g["h"] - 4)
            if any(seg_hits_rect(p, q, r) for p, q in _segs(e)):
                out.append(("arrow through foreign frame", f"{e.get('from')} -> {e.get('to')} / {g.get('text') or g['id']}"))
    return out


def main(paths):
    sys.stdout.reconfigure(encoding="utf-8")
    routes = "--routes" in paths
    paths = [p for p in paths if p != "--routes"]
    bad = 0
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if "nodes" in d and "edges" in d and "width" in d and all("inner" in n for n in d["nodes"]):
            probs, warns = check(d)
            lines = [f"LAYOUT {d.get('id', '?')} | {a} | {b}" for a, b in probs]
            lines += [f"WARN {d.get('id', '?')} | {a} | {b}" for a, b in warns]
        else:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import diagram
            r = diagram.build(d)
            lines = [x if x.startswith(("LAYOUT", "WARN")) else f"ERROR {d.get('id', '?')} | {x}"
                     for x in r["errors"] + r["warnings"]]
            probs = [x for x in lines if not x.startswith("WARN")]
            d = r["geometry"] or {}
        if routes and d.get("edges") is not None:
            lines += [f"ROUTE {d.get('id', '?')} | {a} | {b}" for a, b in route_issues(d)]
        for x in lines:
            print(x)
        bad += len(probs)
        print(f"{'FAIL' if probs else 'OK'} {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
