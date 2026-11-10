"""Render a built doc and list layout problems: overflow, overlaps, edges through boxes or on top of each other,
cut-off values, too-wide diagrams and tables, sideways scroll.

Usage: python check.py <doc.html> [screenshot.png]
Exit 0 = clean. Needs Playwright (pip install playwright; playwright install chromium).
"""
import sys
from pathlib import Path

JS = r"""() => {
  const out = [], R = e => e.getBoundingClientRect();
  const hit = (a, b, pad = 1) => a.left < b.right - pad && b.left < a.right - pad && a.top < b.bottom - pad && b.top < a.bottom - pad;
  const where = e => { const s = e.closest('section'); return s ? s.querySelector('h2').innerText : 'top'; };
  const name = e => (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  const add = (e, what) => out.push(`${where(e)} | ${what} | ${name(e)}`);
  if (document.documentElement.scrollWidth > innerWidth + 1) out.push('page | scrolls sideways | ');
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
    // (ER: one key to two tables) may share their first part: that is a branch, not an overlap.
    const segs = lines.map(pts => pts.slice(1).map((q, i) => [pts[i], q, i]));
    segs.forEach((sa, k) => segs.slice(k + 1).forEach((sb, d) => sa.forEach(([p1, p2, i]) => sb.forEach(([q1, q2, j]) => {
      const ax = p1[1] === p2[1] ? 0 : p1[0] === p2[0] ? 1 : -1, bx = q1[1] === q2[1] ? 0 : q1[0] === q2[0] ? 1 : -1;
      if (ax < 0 || ax !== bx || Math.abs(p1[1 - ax] - q1[1 - ax]) >= 19) return;
      if (!i && !j && p1[0] === q1[0] && p1[1] === q1[1]) return;
      const lo = Math.max(Math.min(p1[ax], p2[ax]), Math.min(q1[ax], q2[ax])), hi = Math.min(Math.max(p1[ax], p2[ax]), Math.max(q1[ax], q2[ax]));
      if (hi - lo > 2) out.push(`${where(m)} | edges ${k + 1} and ${k + d + 2} run on top of each other (${Math.abs(p1[1 - ax] - q1[1 - ax])}px apart) | `);
    }))));
  });
  document.querySelectorAll('main table:not(.res)').forEach(t => {
    if (t.closest('.map')) return;
    const box = t.parentElement.classList.contains('scroll') ? t.parentElement : t;
    if (box.scrollWidth > box.clientWidth + 1) add(t, 'table wider than page');
    t.querySelectorAll('td, th').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off'); });
  });
  document.querySelectorAll('.journey td, .card td, .card p, .stage .h').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off'); });
  document.querySelectorAll('.journey').forEach(j => { if (j.scrollWidth > j.clientWidth + 1) add(j, 'journey wider than page'); });
  return out;
}"""


def main(path, shot=None):
    sys.stdout.reconfigure(encoding="utf-8")  # box text can hold arrows; Windows consoles default to cp1252
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright missing: pip install playwright && playwright install chromium")
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 900})
        page.goto(Path(path).resolve().as_uri())
        problems = list(dict.fromkeys(page.evaluate(JS)))
        if shot:
            page.screenshot(path=shot, full_page=True)
        b.close()
    for x in problems:
        print("LAYOUT", x)
    print(f"{path}: {len(problems)} layout problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
