"""Render a built doc (every <details> opened) and list layout problems: overflow, overlaps, edges through boxes or
on top of each other, more than 3 line crossings in one diagram, a crossing next to a label or number, a label or
number <6 px from a line that is not its own, an arrow that ends on no box (a frame border, empty space), a decision
box with fewer than 2 outgoing arrows, a name broken mid-word in a box or table, arrow ends crowding one box side
(<12 px), lines crossing a group border <20 px apart, cut-off values, too-wide diagrams, tables and ipo strips,
sideways scroll, an example trace row hidden on a desktop. Two widths: 1280 px (everything) and 390 px (sideways scroll, the ipo strip, example traces and tables).

Usage: python check.py <doc.html> [shots_dir]   (shots_dir: page.png plus one map-<n>.png per diagram, n from 1)
Each LAYOUT line: `<section> | diagram <id> (map-<n>) | problem | text` (no diagram part outside diagrams).
Exit 0 = clean. Needs Playwright (pip install playwright; playwright install chromium).
"""
import sys
from pathlib import Path

JS = r"""(narrow) => {
  const out = [], R = e => e.getBoundingClientRect();
  const hit = (a, b, pad = 1) => a.left < b.right - pad && b.left < a.right - pad && a.top < b.bottom - pad && b.top < a.bottom - pad;
  // section, plus "diagram X (map-n)" inside a diagram: X = its id from the "Diagram X" heading, n = its map-<n>.png
  const maps = [...document.querySelectorAll('.map')];
  const did = m => { let x = m.closest('.map-wrap'); while (x && !(x.matches('h3') && x.id.startsWith('d-'))) x = x.previousElementSibling; return x ? x.id.slice(2) : '?'; };
  const where = e => { const s = e.closest('section'), m = e.closest('.map'), h = s ? s.querySelector('h2').innerText : 'top';
    return m ? `${h} | diagram ${did(m)} (map-${maps.indexOf(m) + 1})` : h; };
  const name = e => (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  const add = (e, what) => out.push(`${where(e)} | ${what} | ${name(e)}`);
  // a name broken mid-word: inside one text node (the build puts <wbr> between the parts it may break) two
  // neighbouring letters on different lines; a break after a space or a hyphen is fine
  const broken = (el, at) => {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let t = w.nextNode(); t; t = w.nextNode()) {
      const s = t.textContent, r = document.createRange();
      let prev = null;
      for (let i = 0; i < s.length; i++) {
        r.setStart(t, i); r.setEnd(t, i + 1);
        const box = r.getClientRects()[0];
        if (!box || /\s/.test(s[i])) { prev = null; continue; }
        if (prev && box.top > prev.top + 4 && !/[-\s]/.test(s[i - 1])) { add(el, `name broken mid-word${at}: ${s.slice(Math.max(0, i - 12), i)}|${s.slice(i, i + 12)}`); break; }
        prev = box;
      }
    }
  };
  document.querySelectorAll('details').forEach(d => { d.open = true; });
  if (document.documentElement.scrollWidth > innerWidth + 1) out.push(`page | scrolls sideways${narrow ? ' at 390px' : ''} | `);
  if (narrow) {  // phone width: the page, the Main flows ipo strip and example traces (a column, then stacked rows), tables
    document.querySelectorAll('.ipo li, .trace td').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off at 390px'); broken(c, ' at 390px'); });
    document.querySelectorAll('.ipo, .trace').forEach(t => { if (t.scrollWidth > t.clientWidth + 1 || R(t).right > innerWidth)
      add(t, `${t.matches('.ipo') ? 'ipo strip' : 'example traces'} wider than page at 390px`); });
    document.querySelectorAll('main table:not(.res):not(.trace)').forEach(t => {  // tables: rows stack, nothing scrolls or is cut
      if (t.closest('.map, .card, .journey, .payload')) return;
      const box = t.parentElement.classList.contains('scroll') ? t.parentElement : t;
      if (box.scrollWidth > box.clientWidth + 1 || R(t).right > innerWidth) add(t, 'table wider than page at 390px');
      t.querySelectorAll('td').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off at 390px'); broken(c, ' at 390px'); });
    });
    return out;
  }
  document.querySelectorAll('.ipo').forEach(t => { if (t.scrollWidth > t.clientWidth + 1) add(t, 'ipo strip wider than page'); });
  // every example trace row shows on a desktop (details open): one hidden by CSS is an example nobody can read
  const exs = [...document.querySelectorAll('.trace tr[id]')], gone = exs.filter(r => !r.getClientRects().length);
  gone.forEach(r => add(r, `example ${r.id.slice(3)} hidden (${exs.length - gone.length} of ${exs.length} example rows shown)`));
  document.querySelectorAll('.map-wrap').forEach(w => { if (w.scrollWidth > w.clientWidth + 1) add(w, 'diagram wider than page'); });
  document.querySelectorAll('.map').forEach(m => {
    const boxes = [...m.querySelectorAll('.b, .ent')], marks = [...m.querySelectorAll('.lbl, .num')];
    boxes.forEach(b => { if (b.scrollHeight > b.clientHeight + 1 || b.scrollWidth > b.clientWidth + 1) add(b, 'text overflows box'); });
    boxes.forEach((a, i) => boxes.slice(i + 1).forEach(b => { if (hit(R(a), R(b))) add(a, 'boxes overlap: ' + name(b)); }));
    marks.forEach(l => boxes.forEach(b => { if (hit(R(l), R(b), 2)) add(l, 'label/number on box: ' + name(b)); }));
    marks.forEach((a, i) => marks.slice(i + 1).forEach(b => { if (hit(R(a), R(b), 2)) add(a, 'labels overlap: ' + name(b)); }));
    m.querySelectorAll('.grp span').forEach(g => boxes.forEach(b => { if (hit(R(g), R(b), 1)) add(g, 'group label on box: ' + name(b)); }));
    const frames = [...m.querySelectorAll('.grp.fan')];
    marks.forEach(l => frames.forEach(f => { if (hit(R(l), R(f), 2)) add(l, 'label/number on frame: ' + name(f)); }));
    // group label text (not its whole span): a range gives the boxes of the glyphs actually drawn
    const texts = [...m.querySelectorAll('.grp span')].flatMap(g => { const r = document.createRange(); r.selectNodeContents(g); return [...r.getClientRects()].map(x => [g, x]); });
    // edge through box, fan-out frame or group label: walk each polyline in 4px steps; skip 8px at both ends, where it meets its own boxes
    const svg = m.querySelector('svg'), o = svg && R(svg), solid = boxes.map(b => [b, R(b)]).concat(frames.map(f => [f, R(f)]), texts);
    const lines = (svg ? [...svg.querySelectorAll('polyline')] : []).map(pl => pl.getAttribute('points').trim().split(/\s+/).map(p => p.split(',').map(Number)));
    lines.forEach((pts, k) => {
      const a = pts[0], z = pts[pts.length - 1], seen = new Set();
      for (let i = 1; i < pts.length; i++) {
        const [x1, y1] = pts[i - 1], [x2, y2] = pts[i], n = Math.max(1, Math.ceil(Math.hypot(x2 - x1, y2 - y1) / 4));
        for (let s = 0; s <= n; s++) {
          const x = x1 + (x2 - x1) * s / n, y = y1 + (y2 - y1) * s / n;
          if (Math.hypot(x - a[0], y - a[1]) < 8 || Math.hypot(x - z[0], y - z[1]) < 8) continue;
          solid.forEach(([e, r], j) => {
            if (!seen.has(j) && o.left + x > r.left + 1 && o.left + x < r.right - 1 && o.top + y > r.top + 1 && o.top + y < r.bottom - 1) {
              seen.add(j); add(e, `edge ${k + 1} through ${e.matches('.grp span') ? 'group label' : e.matches('.grp') ? 'frame' : 'box'}`);
            }
          });
        }
      }
    });
    // edge on edge: parallel parts of two lines closer than 20px over more than 2px. Two lines leaving one point
    // (a fan-out, ER: one key to two tables) may share parts that start at one point: that is a branch, not an overlap.
    const segs = lines.map(pts => pts.slice(1).map((q, i) => [pts[i], q, i]));
    const same = (a, b) => a && b && a[0][0] === b[0][0] && a[0][1] === b[0][1];
    segs.forEach((sa, k) => segs.slice(k + 1).forEach((sb, d) => sa.forEach(([p1, p2, i]) => sb.forEach(([q1, q2, j]) => {
      const ax = p1[1] === p2[1] ? 0 : p1[0] === p2[0] ? 1 : -1, bx = q1[1] === q2[1] ? 0 : q1[0] === q2[0] ? 1 : -1;
      if (ax < 0 || ax !== bx || Math.abs(p1[1 - ax] - q1[1 - ax]) >= 19) return;
      if (p1[0] === q1[0] && p1[1] === q1[1] && same(lines[k], lines[k + d + 1])) return;
      const lo = Math.max(Math.min(p1[ax], p2[ax]), Math.min(q1[ax], q2[ax])), hi = Math.min(Math.max(p1[ax], p2[ax]), Math.max(q1[ax], q2[ax]));
      if (hi - lo > 2) out.push(`${where(m)} | edges ${k + 1} and ${k + d + 2} run on top of each other (${Math.abs(p1[1 - ax] - q1[1 - ax])}px apart) | `);
    }))));
    // lines crossing each other: a horizontal part of one line through a vertical part of another (ends excluded)
    let crossings = 0;
    const cpts = [];
    segs.forEach((sa, k) => segs.slice(k + 1).forEach(sb => sa.forEach(([p1, p2]) => sb.forEach(([q1, q2]) => {
      const [h, v] = p1[1] === p2[1] && q1[0] === q2[0] ? [[p1, p2], [q1, q2]] : q1[1] === q2[1] && p1[0] === p2[0] ? [[q1, q2], [p1, p2]] : [];
      if (!h) return;
      const y = h[0][1], x = v[0][0];
      if (Math.min(h[0][0], h[1][0]) < x - 1 && x + 1 < Math.max(h[0][0], h[1][0]) && Math.min(v[0][1], v[1][1]) < y - 1 && y + 1 < Math.max(v[0][1], v[1][1])) { crossings++; cpts.push([o.left + x, o.top + y]); }
    }))));
    if (crossings > 3) out.push(`${where(m)} | ${crossings} line crossings in one diagram (max 3): reorder boxes, or move part into a sub-flow | `);
    // a gap between a rectangle and a straight part of a line (page px)
    const gap = (r, [[x1, y1], [x2, y2]]) => Math.hypot(Math.max(0, Math.min(x1, x2) - r.right, r.left - Math.max(x1, x2)),
                                                        Math.max(0, Math.min(y1, y2) - r.bottom, r.top - Math.max(y1, y2)));
    // a crossing right next to a label or number reads as the label belonging to the other line
    cpts.forEach(([x, y]) => marks.forEach(l => { const r = R(l);
      if (gap(r, [[x, y], [x, y]]) < 12) add(l, `line crossing ${Math.round(gap(r, [[x, y], [x, y]]))}px from this label or number: move boxes so lines cross away from labels`); }));
    // a label or number close to another line (data-e = its own line, 1-based); lines leaving one point (a fan-out,
    // ER: one key to several tables) are one branch, not another line
    marks.forEach(l => { const own = +l.dataset.e - 1, r = R(l);
      segs.forEach((ss, k) => { if (k === own || same(lines[k], lines[own])) return;
        const d = Math.min(...ss.map(([p1, p2]) => gap(r, [[o.left + p1[0], o.top + p1[1]], [o.left + p2[0], o.top + p2[1]]])));
        if (d < 6) add(l, `label/number of line ${own + 1} is ${Math.round(d)}px from line ${k + 1}`); }); });
    // arrow ends crowding one side of a box or frame: two ends < 12px apart read as one (lines leaving one point branch)
    const sides = {}, P = ([x, y]) => [o.left + x, o.top + y];
    // every arrow ends on a box, a table or a fan-out frame: never on a group frame or in empty space
    const ends = boxes.concat(frames).map(R), on = ([x, y]) => ends.some(r =>
      (Math.abs(x - r.left) <= 2 || Math.abs(x - r.right) <= 2) && y > r.top - 2 && y < r.bottom + 2 ||
      (Math.abs(y - r.top) <= 2 || Math.abs(y - r.bottom) <= 2) && x > r.left - 2 && x < r.right + 2);
    lines.forEach((pts, k) => [pts[0], pts[pts.length - 1]].forEach((q, e) => { if (!on(P(q)))
      out.push(`${where(m)} | line ${k + 1} ${e ? 'ends' : 'starts'} on no box (a frame border or empty space) | `); }));
    // a decision needs one outgoing arrow per branch
    m.querySelectorAll('.b.decision').forEach(b => { const r = R(b);
      const n = lines.filter(pts => { const [x, y] = P(pts[0]); return x >= r.left - 2 && x <= r.right + 2 && y >= r.top - 2 && y <= r.bottom + 2; }).length;
      if (n < 2) add(b, `decision box with ${n} outgoing arrow${n === 1 ? '' : 's'} (want 2+, one per branch)`); });
    lines.forEach((pts, k) => [pts[0], pts[pts.length - 1]].map(P).forEach(([x, y]) => boxes.filter(b => b.matches('.b')).concat(frames).forEach((b, i) => {
      const r = R(b);
      const s = Math.abs(x - r.left) <= 2 || Math.abs(x - r.right) <= 2 ? (y > r.top - 2 && y < r.bottom + 2 ? (Math.abs(x - r.left) <= 2 ? 'l' : 'r') : '')
              : Math.abs(y - r.top) <= 2 || Math.abs(y - r.bottom) <= 2 ? (x > r.left - 2 && x < r.right + 2 ? (Math.abs(y - r.top) <= 2 ? 't' : 'b') : '') : '';
      if (s) (sides[i + s] = sides[i + s] || []).push([s === 'l' || s === 'r' ? y : x, k, b]);
    })));
    Object.values(sides).forEach(v => v.forEach(([a, k, b], i) => v.slice(i + 1).forEach(([c, j]) => {
      if (j !== k && Math.abs(a - c) < 12 && !same(lines[k], lines[j])) add(b, `arrows ${k + 1} and ${j + 1} end ${Math.round(Math.abs(a - c))}px apart on one side`);
    })));
    // lines crossing one border of a group frame closer than 20px (1px rounding allowed)
    [...m.querySelectorAll('.grp:not(.fan)')].forEach(g => {
      const r = R(g), cross = {t: [], b: [], l: [], r: []};
      segs.forEach((ss, k) => ss.forEach(([p1, p2]) => {
        const [x1, y1] = P(p1), [x2, y2] = P(p2);
        if (x1 === x2 && x1 > r.left && x1 < r.right) [['t', r.top], ['b', r.bottom]].forEach(([s, v]) => { if (Math.min(y1, y2) < v && v < Math.max(y1, y2)) cross[s].push([x1, k]); });
        if (y1 === y2 && y1 > r.top && y1 < r.bottom) [['l', r.left], ['r', r.right]].forEach(([s, v]) => { if (Math.min(x1, x2) < v && v < Math.max(x1, x2)) cross[s].push([y1, k]); });
      }));
      Object.values(cross).forEach(v => v.forEach(([a, k], i) => v.slice(i + 1).forEach(([c, j]) => {
        if (j !== k && Math.abs(a - c) < 19) add(g, `edges ${k + 1} and ${j + 1} cross the group border ${Math.round(Math.abs(a - c))}px apart`);
      })));
    });
  });
  document.querySelectorAll('.map .b, .map .ent, main td, .ipo li').forEach(el => broken(el, ''));
  document.querySelectorAll('main table:not(.res)').forEach(t => {
    if (t.closest('.map')) return;
    const box = t.parentElement.classList.contains('scroll') ? t.parentElement : t;
    if (box.scrollWidth > box.clientWidth + 1) add(t, 'table wider than page');
    t.querySelectorAll('td, th').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off'); });
  });
  document.querySelectorAll('.journey td, .card td, .card p, .stage .h, .ipo li').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off'); });
  document.querySelectorAll('.journey').forEach(j => { if (j.scrollWidth > j.clientWidth + 1) add(j, 'journey wider than page'); });
  return out;
}"""


def main(path, shots=None):
    sys.stdout.reconfigure(encoding="utf-8")  # box text can hold arrows; Windows consoles default to cp1252
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright missing: pip install playwright && playwright install chromium")
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1280, "height": 900})
        page.goto(Path(path).resolve().as_uri())
        problems = page.evaluate(JS, False)  # also opens every <details>
        if shots:
            Path(shots).mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(Path(shots) / "page.png"), full_page=True)
            maps = page.locator(".map")
            for i in range(maps.count()):
                maps.nth(i).screenshot(path=str(Path(shots) / f"map-{i + 1}.png"))
            print(f"shots: {Path(shots).as_posix()}/page.png and {maps.count()} map-<n>.png (read every one)")
        page.set_viewport_size({"width": 390, "height": 900})  # phone width, after the shots
        page.reload()
        problems = list(dict.fromkeys(problems + page.evaluate(JS, True)))
        b.close()
    for x in problems:
        print("LAYOUT", x)
    print(f"{path}: {len(problems)} layout problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
