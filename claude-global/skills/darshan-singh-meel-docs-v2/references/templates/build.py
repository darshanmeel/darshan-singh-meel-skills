"""Build one document from a JSON spec: fixed sections, one look, diagrams laid out here.

Usage: python build.py <spec.json> <out.html>
The model writes only the spec (content, boxes, arrows, examples). Spec format: spec.md.
"""
import html
import json
import re
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
    "user-guide": {"*": ["How to *", "Problems and fixes", "Who to contact"], "pipeline": ["What answers what", "When data is fresh"],
                   "ui": ["Screens"], "api": ["What answers what"]},
}
EXAMPLE_BLOCKS = {"examples", "io", "journey"}
ISSUE_COLS = {
    "overview": [("Issue", "issue"), ("What it means", "impact"), ("Status", "status")],
    "technical": [("Issue", "issue"), ("Where", "where"), ("Impact", "impact"), ("Status", "status"), ("Suggested fix", "fix")],
    "user-guide": [("If you see", "see"), ("Do this", "do"), ("Status", "status")],
}
SEV = ["Must", "Should", "Question", "Other"]
INK, RED = "#17191D", "#A12D2D"
PAD, GX, GY = 20, 44, 44
_ids = [0]


def uid():
    _ids[0] += 1
    return f"m{_ids[0]}"


def esc(text):
    """Escape; `code` → <code>, **bold** → <b>, [synthetic] → badge."""
    t = html.escape(str(text))
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("[synthetic]", '<span class="chip syn">synthetic</span>')


def status(s):
    cls = "ok" if str(s).lower().startswith("confirmed") else "nv"
    return f'<span class="chip {cls}">{esc(s)}</span>'


def lines(text, per):
    return max(1, -(-len(str(text)) // int(per))) if text else 0


# ---------- diagrams ----------
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


def box_height(n, w):
    h = 16 + (14 if n.get("tag") else 0) + 18 * lines(n["label"], (w - 22) / 7.4) + 16 * lines(n.get("sub"), (w - 22) / 6.6)
    h += sum(16 * lines(b, (w - 40) / 6.4) for b in n.get("bullets", [])) + (6 if n.get("bullets") else 0)
    h += 17 if n.get("runs") else 0
    if n.get("in") or n.get("out"):
        h += 10 + sum(17 * lines(n.get(k), (w - 64) / 6.6) for k in ("in", "out") if n.get(k))
    return max(62, int(h + (18 if n.get("see") else 0)))


def flow(d, p):
    nodes = {n["id"]: n for n in d["nodes"]}
    for n in nodes.values():
        if "col" not in n or "row" not in n:
            sys.exit(f"node {n['id']} needs col and row")
    for e in d.get("edges", []):
        if e["from"] not in nodes or e["to"] not in nodes:
            sys.exit(f"edge {e['from']} -> {e['to']}: unknown node")
    w, lanes, groups = d.get("box_w", 180), d.get("lanes", []), d.get("groups", [])
    gy = GY + (16 if groups else 0)
    rows = max(n["row"] for n in nodes.values()) + 1
    rh = [max([box_height(n, w) for n in nodes.values() if n["row"] == r] or [40]) for r in range(rows)]
    top = PAD + (26 if any(nodes[i]["row"] == 0 for g in groups for i in g["nodes"]) else 0)
    ry = [top + sum(rh[:r]) + gy * r for r in range(rows)]
    x0 = PAD + (100 if lanes else 0)
    cols = max(n["col"] for n in nodes.values()) + 1
    room = (1020 - x0 - PAD - cols * w) // max(cols - 1, 1)
    need = max([GX] + [len(e["label"]) * 7 + 24 for e in d.get("edges", []) if e.get("label")
                       and nodes[e["from"]]["col"] != nodes[e["to"]]["col"]])
    gx = max(GX, min(need, room))  # widen gaps for arrow labels as far as the page allows; longer labels wrap
    pos = {i: (x0 + n["col"] * (w + gx), ry[n["row"]]) for i, n in nodes.items()}
    hh = {i: rh[n["row"]] for i, n in nodes.items()}
    width = max(x for x, _ in pos.values()) + w + PAD
    height = ry[-1] + rh[-1] + PAD
    if width > 1020:
        sys.exit(f"diagram {d.get('id', '')} is {width}px wide (max 1020): fewer columns, shorter arrow labels, smaller box_w, or split into a sub-flow")
    back, svg, front = [], [markers(p)], []
    for r, name in enumerate(lanes):
        back.append(f'<div class="lane" style="top:{ry[r] - gy // 2}px;height:{rh[r] + gy}px;width:{width}px"><span>{esc(name)}</span></div>')
    for g in groups:
        xs = [pos[i][0] for i in g["nodes"]]
        ys = [pos[i][1] for i in g["nodes"]]
        bot = max(pos[i][1] + hh[i] for i in g["nodes"])
        back.append(f'<div class="grp" style="left:{min(xs) - 12}px;top:{min(ys) - 30}px;width:{max(xs) + w - min(xs) + 24}px;'
                    f'height:{bot - min(ys) + 42}px"><span>{esc(g["label"])}</span></div>')
    for k, e in enumerate(d.get("edges", []), 1):
        (ax, ay), (bx, by) = pos[e["from"]], pos[e["to"]]
        ha, hb = hh[e["from"]], hh[e["to"]]
        if bx > ax and by != ay:  # leave from bottom/top centre, then turn right: no shared trunk with other edges
            sx = ax + w // 2
            pts = [(sx, ay + ha if by > ay else ay), (sx, by + hb // 2), (bx, by + hb // 2)]
        elif bx != ax:
            a = (ax + w, ay + ha // 2) if bx > ax else (ax, ay + ha // 2)
            b = (bx, by + hb // 2) if bx > ax else (bx + w, by + hb // 2)
            mx = (a[0] + b[0]) // 2
            pts = [a, b] if a[1] == b[1] else [a, (mx, a[1]), (mx, b[1]), b]
        else:
            down = by > ay
            pts = [(ax + w // 2, ay + (ha if down else 0)), (bx + w // 2, by + (0 if down else hb))]
        fail = e.get("fail")
        svg.append(poly(pts, e.get("dashed") or fail, RED if fail else INK, f"{p}{'r' if fail else 'h'}"))
        mid = ((pts[-2][0] + pts[-1][0]) // 2, pts[-1][1]) if len(pts) == 3 else \
              ((pts[1][0] + pts[2][0]) // 2, (pts[1][1] + pts[2][1]) // 2) if len(pts) > 2 else \
              ((pts[0][0] + pts[1][0]) // 2, (pts[0][1] + pts[1][1]) // 2)
        if d.get("numbered", True):
            front.append(f'<span class="num" style="left:{mid[0]}px;top:{mid[1]}px">{k}</span>')
        if e.get("label"):
            vertical = len(pts) == 2 and pts[0][0] == pts[1][0]
            lx, ly = (mid[0] + 14, mid[1]) if vertical else (mid[0], mid[1] - 17)
            wrap = "" if vertical or len(e["label"]) * 7 + 12 <= gx else f";white-space:normal;width:{gx - 6}px;text-align:center"
            if wrap:
                ly -= 8
            front.append(f'<span class="lbl{" l" if vertical else ""}" style="left:{lx}px;top:{ly}px{wrap}">{esc(e["label"])}</span>')
    boxes = []
    for i, n in nodes.items():
        x, y = pos[i]
        rich = n.get("bullets") or n.get("in") or n.get("out")
        inner = f'<span class="tag">{esc(n["tag"])}</span>' if n.get("tag") else ""
        inner += f'<span class="t">{esc(n["label"])}</span>'
        inner += f'<span class="s">{esc(n["sub"])}</span>' if n.get("sub") else ""
        inner += "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in n["bullets"]) + "</ul>" if n.get("bullets") else ""
        inner += f'<span class="run">{esc(n["runs"])}</span>' if n.get("runs") else ""
        if n.get("in") or n.get("out"):
            inner += '<div class="io">' + "".join(f'<span class="l {k}">{k.upper()}</span><span>{esc(n[k])}</span>'
                                                  for k in ("in", "out") if n.get(k)) + "</div>"
        inner += f'<a class="see" href="#d-{esc(n["see"])}">&#9656; Diagram {esc(n["see"])}</a>' if n.get("see") else ""
        tip = f' data-tip="{html.escape(n["tip"])}" tabindex="0"' if n.get("tip") else ""
        boxes.append(f'<div class="b {n.get("kind", "")}{" rich" if rich else ""}"{tip} '
                     f'style="left:{x}px;top:{y}px;width:{w}px;height:{hh[i]}px">{inner}</div>')
    return (f'<div class="map-wrap"><div class="map" style="width:{width}px;height:{height}px">{"".join(back)}'
            f'<svg width="{width}" height="{height}" aria-hidden="true">{"".join(svg)}</svg>{"".join(boxes + front)}</div></div>')


def er(d, p):
    ew, row, head, per = d.get("box_w", 260), 22, 48, 3
    ents = d["entities"]
    pos, y, tallest = {}, PAD, 0
    for i, e in enumerate(ents):
        if i and i % per == 0:
            y, tallest = y + tallest + 70, 0
        pos[e["id"]] = (PAD + (i % per) * (ew + 80), y)
        tallest = max(tallest, head + row * len(e["cols"]))
    width, height = PAD * 2 + min(len(ents), per) * (ew + 80) - 80, y + tallest + PAD
    cols = {e["id"]: [c[0] for c in e["cols"]] for e in ents}
    svg, parts = [markers(p)], []
    for r in d.get("rels", []):
        (ax, ay), (bx, by) = pos[r["from"]], pos[r["to"]]
        ya = ay + head + cols[r["from"]].index(r["from_col"]) * row + row // 2
        yb = by + head + cols[r["to"]].index(r["to_col"]) * row + row // 2
        if bx == ax:
            a, b, mx = (ax + ew, ya), (bx + ew, yb), ax + ew + 30
        else:
            a, b = ((ax + ew, ya), (bx, yb)) if bx > ax else ((ax, ya), (bx + ew, yb))
            mx = (a[0] + b[0]) // 2
        svg.append(poly([a, (mx, a[1]), (mx, b[1]), b], r.get("logical", True), INK, f"{p}many", f"{p}one"))
        if r.get("label"):
            parts.append(f'<span class="lbl" style="left:{mx}px;top:{(a[1] + b[1]) // 2}px">{esc(r["label"])}</span>')
    for e in ents:
        x, y = pos[e["id"]]
        trs = "".join(f'<tr><td>{esc(c)}</td><td>{"".join(f"<span class=k{k.lower()}>{k}</span> " for k in (t or "").split())}</td></tr>'
                      for c, t in e["cols"])
        parts.append(f'<div class="ent" style="left:{x}px;top:{y}px;width:{ew}px;height:{head + row * len(e["cols"])}px">'
                     f'<div class="eh"><span class="sch">{esc(e.get("schema", ""))}</span><b>{esc(e["name"])}</b>'
                     f'<small>{esc(e.get("grain", ""))}</small></div><table>{trs}</table></div>')
    return (f'<div class="map-wrap"><div class="map" style="width:{width}px;height:{height}px">'
            f'<svg width="{width}" height="{height}" aria-hidden="true">{"".join(svg)}</svg>{"".join(parts)}</div></div>')


def journey(d, p):
    out = []
    for i, s in enumerate(d["stages"]):
        if i:
            out.append('<div class="arrow">&rarr;</div>')
        trs = ""
        for r in s["rows"]:
            r = r if isinstance(r, dict) else {"field": r[0], "value": r[1]}
            sub = f'<small>{esc(r["sub"])}</small>' if r.get("sub") else ""
            if "old" in r:
                val, cls = f'<span class="old">{"NULL" if r["old"] is None else esc(r["old"])}</span><span class="new">{esc(r["value"])}</span>', "chg"
            else:
                val = '<span class="tc">NULL</span>' if r["value"] is None else esc(r["value"])
                cls = "calc" if r.get("calc") else "chg" if r.get("changed") else ""
            trs += f'<tr><td>{esc(r["field"])}{sub}</td><td class="{cls}">{val}</td></tr>'
        out.append(f'<div class="stage{" changed" if s.get("changed") else ""}"><div class="h"><b>{esc(s["title"])}</b>'
                   f'<small>{esc(s.get("sub", ""))}</small></div><table>{trs}</table><p class="what">{esc(s.get("what", ""))}</p></div>')
    return f'<div class="journey">{"".join(out)}</div>'


# ---------- other blocks ----------
KW = (r"\b(SELECT|FROM|WHERE|LEFT JOIN|INNER JOIN|JOIN|ON|AND|OR|GROUP BY|ORDER BY|HAVING|AS|CASE|WHEN|THEN|ELSE|END|IN|IS|"
      r"NOT|NULL|UNION ALL|LIMIT|WITH|DISTINCT|OVER|PARTITION BY|QUALIFY|MERGE|INTO|USING|MATCHED|UPDATE|SET|INSERT|VALUES)\b")


def highlight(code, lang):
    t = html.escape(code)
    if lang == "sql":
        t = re.sub(r"(&#x27;.*?&#x27;)", r'<span class="ts">\1</span>', t)
        return re.sub(KW, r'<span class="tb">\1</span>', t)
    if lang == "json":
        t = re.sub(r"(&quot;[^&]*?&quot;)(\s*:)", r'<span class="tk">\1</span>\2', t)
        t = re.sub(r"(:\s*)(&quot;[^&]*?&quot;)", r'\1<span class="ts">\2</span>', t)
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
    what = esc(b.get("label", "Input")) + (" · " + esc(b["title"]) if b.get("title") else "")
    inp = f'<div class="payload"><div class="h"><span class="in">IN</span><span>{what}</span></div><pre>{highlight(b["input"], b.get("lang", "text"))}</pre></div>'
    r = b.get("result")
    body = result_table(r) if isinstance(r, dict) else f'<pre>{highlight(r or "", b.get("result_lang", "text"))}</pre>'
    out = f'<div class="payload"><div class="h"><span class="out">OUT</span><span>{esc(b.get("result_title", "result"))}</span></div>{body}</div>'
    return f'<div class="payloads">{inp}{out}</div>'


def kv(v):
    if isinstance(v, list):
        return "<table>" + "".join(f"<tr><td>{esc(k)}</td><td>{esc(x)}</td></tr>" for k, x in v) + "</table>"
    return f'<p class="res-t">{esc(v)}</p>'


def examples(b):
    cards = []
    for c in b["items"]:
        syn = ' <span class="chip syn">synthetic</span>' if c.get("synthetic") else ""
        src = f'<p class="src">{esc(c["source"])}</p>' if c.get("source") else ""
        cards.append(f'<div class="card {c.get("case", "typical")}"><div class="h"><span class="tag">{esc(c.get("tag", c.get("case", "typical"))).upper()}</span>'
                     f'{syn}<b>{esc(c["title"])}</b></div><div class="lbl2">IN</div>{kv(c["in"])}<div class="lbl2">OUT</div>{kv(c["out"])}{src}</div>')
    return f'<div class="cards">{"".join(cards)}</div>'


def issues(b, kind):
    cols = ISSUE_COLS[kind]
    head = "<th>#</th>" + "".join(f"<th>{c}</th>" for c, _ in cols)
    items = b["items"]
    groups = [(s, [i for i in items if i.get("sev", "Other") == s]) for s in SEV] if kind != "overview" else [("", items)]
    used = [g for g in groups if g[1]]
    body, n = "", 0
    for sev, rows in used:
        if sev and len(used) > 1:
            body += f'<tr class="sev"><td colspan="{len(cols) + 1}">{sev}</td></tr>'
        for it in rows:
            n += 1
            body += f"<tr><td>{n}</td>" + "".join(
                f'<td{" class=m" if k == "where" else ""}>{status(it.get(k, "")) if k == "status" else esc(it.get(k, ""))}</td>' for _, k in cols) + "</tr>"
    return f'<div class="scroll"><table class="issues"><tr>{head}</tr>{body}</table></div>' if n else "<p>No known issues.</p>"


def block(b, kind):
    t = b["type"]
    if t == "text":
        out = f'<p class="lead">{esc(b["text"])}</p>'
    elif t == "h3":
        out = f'<h3>{esc(b["text"])}</h3>'
    elif t == "bullets":
        out = "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ul>"
    elif t == "table":
        head = "".join(f"<th>{esc(c)}</th>" for c in b["cols"])
        body = "".join("<tr>" + "".join(f"<td>{status(c) if b['cols'][j].lower() == 'status' else esc(c)}</td>"
                                        for j, c in enumerate(r)) + "</tr>" for r in b["rows"])
        out = f'<div class="scroll"><table><tr>{head}</tr>{body}</table></div>'
    elif t == "steps":
        cols = b.get("cols", ["Step", "In", "Out"])
        head = "<th>#</th>" + "".join(f"<th>{esc(c)}</th>" for c in cols)
        body = "".join(f'<tr><td><span class="n">{i}</span></td>' + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
                       for i, r in enumerate(b["rows"], 1))
        out = f'<table class="steps"><tr>{head}</tr>{body}</table>'
    elif t == "terms":
        out = '<ul class="terms">' + "".join(f"<li><b>{esc(a)}</b> — {esc(m)}</li>" for a, m in b["items"]) + "</ul>"
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
            out += f'<h3 id="d-{esc(b["id"])}">Diagram {esc(b["id"])} · {esc(b.get("title", ""))}</h3>'
        if b.get("parent"):
            pd, pb = b["parent"]
            out += f'<p class="key">Sub-flow of <b>{esc(pb)}</b> in <a href="#d-{esc(pd)}">Diagram {esc(pd)}</a></p>'
        out += {"flow": flow, "er": er, "journey": journey}[t](b, uid())
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


def check(spec, kind, names):
    have = {slot(kind, n) for n in names}
    want = REQUIRED[kind]["*"] + [s for a in spec.get("app_types", []) for s in REQUIRED[kind].get(a, [])]
    warn = [f"missing section: {w} (add it, or one line 'Not in source — confirm with owner')" for w in dict.fromkeys(want) if w not in have]
    for n in names:
        need = (kind == "technical" and n == "Main flows") or slot(kind, n) == "How to *" or (kind == "overview" and n == "Example")
        blocks = spec["sections"][n]
        types = {b["type"] for b in blocks} | {x["type"] for b in blocks if b["type"] == "details" for x in b["blocks"]}
        if need and not types & EXAMPLE_BLOCKS:
            warn.append(f"no example in: {n}")
    for w in warn:
        print("WARN", w)


def main(spec_path, out_path):
    spec = json.loads(Path(spec_path).read_text())
    kind, sections = spec["type"], spec["sections"]
    if kind == "custom":  # README, runbook, design doc…: free section names, written order, same look
        ORDER["custom"], REQUIRED["custom"], ISSUE_COLS["custom"] = [n for n in sections if n != LAST], {"*": []}, ISSUE_COLS["technical"]
    allowed = ORDER[kind] + [LAST]
    bad = [n for n in sections if slot(kind, n) not in allowed]
    if bad:
        sys.exit(f"sections not allowed for {kind}: {bad}. Allowed, in order: {allowed}")
    names = sorted(sections, key=lambda n: allowed.index(slot(kind, n)))  # stable sort keeps "How to" order
    check(spec, kind, names)
    title = (lambda i, n: f"{i + 1} {n}") if kind == "technical" else (lambda i, n: n)
    toc = "".join(f'<a href="#s{i}">{esc(title(i, n))}</a>' for i, n in enumerate(names))
    body = "".join(f'<section><h2 id="s{i}">{esc(title(i, n))}</h2>{"".join(block(b, kind) for b in sections[n])}</section>'
                   for i, n in enumerate(names))
    css = (Path(__file__).parent / "style.css").read_text()
    sub = f'<p class="sub1">{esc(spec["subtitle"])}</p>' if spec.get("subtitle") else ""
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="generator" content="darshan-singh-meel-docs-v2"><title>{esc(spec["title"])}</title><style>{css}</style></head><body><main>'
            f'<div class="eyebrow">{kind.replace("-", " ")}</div><h1>{esc(spec["title"])}</h1>{sub}'
            f'{tabs(spec.get("tabs", {}))}<nav class="toc">{toc}</nav>{body}</main></body></html>')
    Path(out_path).write_text(page)
    print(f"built {out_path}: {len(names)} sections")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
