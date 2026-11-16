"""Page layout for a generated HTML doc: left menu, one section at a time, step tables folded under their diagram,
and journey examples rendered from JSON. Safe to rerun: everything it adds sits between <!--layout--> markers.

python layout.py <doc.html> [--examples <examples.json>]

examples.json: {"<section id>": [example, ...]}, max 3 per section; they replace the section's example cards
(.exset) or fill <div class="exjs" data-section="<id>"></div>. One example:
  {"outcome": "Loads" | "Warns, still loads" | "Needs a tick" | "Blocked" | "Refused" | "Fails safely",
   "headline": "the point, one plain sentence",
   "stages": [  # 2-3, drawn left to right
     {"title": "The uploaded file", "sub": "", "kind": "grid", "headers": ["", "Region", "Amount"], "rows": [["2", "North", "-5"]], "highlight": [[0, 2]]},
     {"title": "What the app shows", "sub": "", "kind": "msg", "msg_kind": "warn", "text": "exact message"},
     {"title": "What is stored", "sub": "", "kind": "kv", "rows": [["Rows loaded", "3"]], "highlight": [[0, 1]]}],
   "why": "why it matters, one line", "source": "path:line"}
A grid whose first header is "" shows its first column as row numbers. highlight = [row, column] cells that cause the outcome."""
import html
import json
import re
import sys

CSS = """<style>
/* left menu: wide screens only; nothing clicked = the whole page, a menu click = that section only */
.side { display:none; }
@media (min-width:1024px) {
  body.withnav main { margin-left:250px; }
  .side { display:block; position:fixed; top:0; left:0; bottom:0; width:230px; overflow-y:auto; padding:24px 10px 24px 16px;
          border-right:1px solid var(--line); background:var(--card); font-size:13px; }
  .side a { display:block; color:var(--ink); text-decoration:none; padding:3px 6px; border-radius:4px; }
  .side a:hover { background:var(--soft); }
  .side .t { font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:0 6px 6px; }
  .side .sub { display:none; }
  .side .sub a { padding-left:18px; font-family:"IBM Plex Mono",Consolas,monospace; font-size:12px; color:var(--muted); }
  SUBOPEN
  body:has(main section:target, main section details[id]:target) main > section:not(:target):not(:has(:target)),
  body:has(main section:target, main section details[id]:target) main > :not(section):not(h1):not(.eyebrow) { display:none; }
  main section:has(> details[id]:target) > details[id]:not(:target),
  main section:has(> details[id]:target) > :not(details):not(h2) { display:none; }
}
section[id], details[id] { scroll-margin-top:12px; }
details.fold { margin:6px 0 14px; } details.fold > summary { cursor:pointer; font-weight:600; color:var(--blue); }
.purpose { margin:8px 0 10px; padding:9px 12px; border-left:4px solid var(--teal-ink, #1C5C57); background:var(--teal, #DDF0EE); border-radius:6px; font-size:15px; line-height:1.5; }
.purpose b { display:block; font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--teal-ink, #1C5C57); }
.fd { margin:10px 0 14px; overflow-x:auto; } .fd svg { display:block; max-width:100%; height:auto; }
/* journey examples */
.exj { margin:12px 0 18px; border:1px solid var(--line); border-left:4px solid var(--green); border-radius:8px; background:var(--card); padding:10px 12px 8px; }
.exj.warn { border-left-color:var(--amber-ink); } .exj.block { border-left-color:var(--red); }
.exj .hd { display:flex; gap:10px; align-items:baseline; flex-wrap:wrap; margin-bottom:8px; }
.exj .hd b { font-size:14.5px; }
.exj .oc { font-family:"IBM Plex Mono",Consolas,monospace; font-size:10.5px; font-weight:600; letter-spacing:.05em; text-transform:uppercase; color:var(--green); white-space:nowrap; }
.exj.warn .oc { color:var(--amber-ink); } .exj.block .oc { color:var(--red); }
.exj .js { display:flex; align-items:stretch; }
.exj .st { flex:1 1 0; min-width:0; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.exj .st .h { padding:5px 9px; background:var(--soft); border-bottom:1px solid var(--line); }
.exj .st .h b { display:block; font-size:12.5px; } .exj .st .h small { font-size:11px; color:var(--muted); }
.exj .ar { flex:0 0 26px; display:flex; align-items:center; justify-content:center; color:var(--muted); font-size:17px; }
.exj .tw { overflow-x:auto; }
.exj table { margin:0; border:0; font-size:11.5px; border-collapse:collapse; width:100%; }
.exj th, .exj td { border:0; border-bottom:1px solid var(--line); padding:3px 8px; font-family:"IBM Plex Mono",Consolas,monospace; white-space:nowrap; text-align:left; }
.exj th { color:var(--muted); font-weight:600; font-size:11px; }
.exj td.rn { color:var(--muted); }
.exj td.kv { color:var(--muted); font-size:11px; width:1%; } .exj td.kv + td { white-space:normal; }
.exj td.hl { background:var(--amber); color:var(--amber-ink); font-weight:600; }
.exj .msg { margin:8px; border-radius:6px; padding:7px 9px; font-size:12.5px; line-height:1.45; background:#E4F2E9; color:var(--green); }
.exj .msg.warn { background:var(--amber); color:var(--amber-ink); } .exj .msg.block { background:#F6DCDC; color:var(--red); } .exj .msg.plain { background:var(--soft); color:var(--ink); }
.tblwrap { overflow-x:auto; } .src { overflow-wrap:anywhere; }
.exj .why { margin:8px 0 0; font-size:13px; } .exj .why b { color:var(--muted); font-weight:600; }
@media (max-width:820px) { .exj .js { flex-direction:column; } .exj .ar { transform:rotate(90deg); height:24px; } }
@media print { .side { display:none !important; } body.withnav main { margin-left:0; } main > *, main section > * { display:revert !important; } details.fold > * { display:block; } }
</style>"""

KIND = {"Loads": "", "Warns, still loads": "warn", "Needs a tick": "warn", "Blocked": "block", "Refused": "block", "Fails safely": "block"}
DIAGRAM = re.compile(r'<svg\b|class="(?:map|journey|ipo|exj)\b')
e = lambda t: html.escape(str(t))


def mark(text):
    return f"<!--layout-->{text}<!--/layout-->"


def strip(s):
    """Undo an earlier run: added blocks go, folded tables come back out of their <details>."""
    s = re.sub(r"<!--layout-->.*?<!--/layout-->", "", s, flags=re.S)
    return s.replace('<body class="withnav">', "<body>")


def ids(s):
    """Every section gets an id (s1, s2, ... where missing), so the menu can link to it."""
    n = iter(range(1, 1000))
    return re.sub(r"<section(?![^>]*\bid=)", lambda m: f'<section id="x{next(n)}"', s)


def fold(sec):
    """A step table after a diagram in the same section is closed until clicked; a 'Steps' heading right before it goes."""
    out, pos = [], 0
    for m in re.finditer(r'(<h3>Steps</h3>\s*)?(<div class="tblwrap"><table class="steps.*?</table></div>)', sec, re.S):
        if not DIAGRAM.search(sec, 0, m.start()) or sec.rfind('<details class="fold"', 0, m.start()) > sec.rfind("</details>", 0, m.start()):
            continue  # no diagram above it, or already inside a folded block
        n = m.group(2).count('<span class="n">') or m.group(2).count("<tr>") - 1
        out += [sec[pos:m.start()], mark(f'<details class="fold"><summary>Show the steps ({n})</summary>'), m.group(2), mark("</details>")]
        pos = m.end()
    return "".join(out) + sec[pos:]


def stage(st):
    hl = {tuple(x) for x in st.get("highlight", [])}
    if st["kind"] == "msg":
        inner = f'<div class="msg {st.get("msg_kind") or "plain"}">{e(st["text"])}</div>'
    elif st["kind"] == "kv":
        hc = ' class="hl"'
        inner = '<div class="tw"><table>' + "".join(
            f'<tr><td class="kv">{e(k)}</td><td{hc if (r, 1) in hl else ""}>{e(v)}</td></tr>' for r, (k, v) in enumerate(st["rows"])) + "</table></div>"
    else:
        rn = st["headers"][:1] == [""]
        cell = lambda v: e(v).replace(" ", "&nbsp;") if v.startswith(" ") or "  " in v else e(v)
        inner = ('<div class="tw"><table><tr>' + "".join(f"<th>{e(h)}</th>" for h in st["headers"]) + "</tr>" + "".join(
            "<tr>" + "".join(f'<td class="{"hl" if (r, c) in hl else ("rn" if rn and c == 0 else "")}">{cell(v)}</td>' for c, v in enumerate(row)) + "</tr>"
            for r, row in enumerate(st["rows"])) + "</table></div>")
    sub = f"<small>{e(st['sub'])}</small>" if st.get("sub") else ""
    return f'<div class="st"><div class="h"><b>{e(st["title"])}</b>{sub}</div>{inner}</div>'


def example(x):
    stages = '<div class="ar">&rarr;</div>'.join(stage(st) for st in x["stages"])
    src = f' <span class="src">{e(x["source"])}</span>' if x.get("source") else ""
    return (f'<div class="exj {KIND[x["outcome"]]}"><div class="hd"><span class="oc">{e(x["outcome"])}</span><b>{e(x["headline"])}</b></div>'
            f'<div class="js">{stages}</div><p class="why"><b>Why it matters:</b> {e(x["why"])}{src}</p></div>')


def examples(sec, sid, xs):
    """Replaces the section's first example-card set (or its exjs slot) with the journey examples."""
    new = '<div class="exjs">' + "".join(example(x) for x in xs[:3]) + "</div>"
    m = re.search(rf'<div class="exjs"(?: data-section="{sid}")?>', sec) or re.search(r'<div class="exset">', sec)
    if not m:
        return sec + new
    depth = 0
    for t in re.finditer(r"<div\b|</div>", sec[m.start():]):
        depth += -1 if t.group() == "</div>" else 1
        if depth == 0:
            return sec[:m.start()] + new + sec[m.start() + t.end():]
    return sec


def nav(s, title):
    links = []
    for sid, head in re.findall(r'<section id="([^"]+)"[^>]*>\s*<h2>(.*?)</h2>', s, re.S):
        if re.sub(r"<[^>]+>", "", head).strip() == "Contents":
            continue
        links.append(f'<a href="#{sid}">{head}</a>')
        a = s.find(f'<section id="{sid}"'); b = s.find("</section>", a)
        subs = re.findall(r'<details[^>]*\bid="([^"]+)"[^>]*>\s*<summary>(.*?)</summary>', s[a:b], re.S)
        if subs:
            links.append(f'<div class="sub" data-for="{sid}">' + "".join(f'<a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a>' for i, t in subs) + "</div>")
    return f'<nav class="side" aria-label="Sections"><div class="t">{e(title)}</div>' + "".join(links) + "</nav>"


def main(path, ex_path=None):
    s = ids(strip(open(path, encoding="utf-8", newline="").read()))
    # a step table must sit in a scroll wrapper, or it widens the page on a phone and is not folded
    s = re.sub(r'(?<!<div class="tblwrap">)(<table class="steps.*?</table>)', r'<div class="tblwrap"></div>', s, flags=re.S)
    xs = json.load(open(ex_path, encoding="utf-8")) if ex_path else {}
    for a, b, sid in [(m.start(), s.find("</section>", m.start()), m.group(1)) for m in re.finditer(r'<section id="([^"]+)"', s)][::-1]:
        sec = fold(s[a:b])
        if sid in xs:
            sec = examples(sec, sid, xs[sid])
        s = s[:a] + sec + s[b:]
    subs = re.findall(r'class="sub" data-for="([^"]+)"', nav(s, ""))
    opener = " ".join(f'body:has(#{i}:target, #{i} details:target) .side .sub[data-for="{i}"] {{ display:block; }}' for i in subs)
    title = re.sub(r"<[^>]+>", "", (re.search(r"<h1>(.*?)</h1>", s) or re.search(r"<title>(.*?)</title>", s)).group(1))
    s = s.replace("</style>", "</style>" + mark(CSS.replace("SUBOPEN", opener)), 1)
    s = s.replace("<body>", '<body class="withnav">' + mark(nav(s, title)), 1)
    # a menu click on a folded block opens it (without JS it shows closed, one click away)
    s = s.replace("</body>", mark("<script>function o(){var t=location.hash&&document.getElementById(location.hash.slice(1));"
                                  "if(t&&t.tagName==='DETAILS')t.open=true}addEventListener('hashchange',o);o()</script>") + "</body>", 1)
    open(path, "w", encoding="utf-8", newline="").write(s)
    folds, exs = s.count('<!--layout--><details class="fold"'), s.count('class="exj ')
    print(f"layout {path}: {s.count('<section id=')} sections, {folds} step tables folded, {exs} examples")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[a.index("--examples") + 1] if "--examples" in a else None)
