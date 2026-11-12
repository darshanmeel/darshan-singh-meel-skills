"""Render a built tech summary and list layout problems: sideways page scroll, a diagram shrunk below 80 %, text outside
the diagram, box text outside its box, an edge label on a box or on another label, a line through a box that is not its end.
Widths: 1280 px (everything) and 390 px (sideways scroll only; wide diagrams scroll inside their frame).

Usage: python shots.py <doc.html> <shots_dir>   → page-1280.png, page-390.png, map-<n>.png per diagram (n from 1)
Each problem: `LAYOUT <section> | diagram <n> | problem | text`. Exit 0 = clean. Needs Playwright (pip install playwright; playwright install chromium).
"""
import sys
from pathlib import Path

JS = r"""() => {
  const out = [], maps = [...document.querySelectorAll('.dg')];
  const sec = e => { const s = e.closest('section'); return s ? s.querySelector('h2').innerText : 'top'; };
  const inside = (a, b, pad) => a.x >= b.x - pad && a.y >= b.y - pad && a.x + a.width <= b.x + b.width + pad && a.y + a.height <= b.y + b.height + pad;
  const hit = (a, b, pad) => a.x < b.x + b.width - pad && b.x < a.x + a.width - pad && a.y < b.y + b.height - pad && b.y < a.y + a.height - pad;
  // a segment crosses a box when a point well inside the segment lies inside the box (shrunk by 3 px)
  const cuts = (p, q, r) => { for (let t = 0.08; t < 0.93; t += 0.04) { const x = p[0] + (q[0] - p[0]) * t, y = p[1] + (q[1] - p[1]) * t;
    if (x > r.x + 3 && x < r.x + r.width - 3 && y > r.y + 3 && y < r.y + r.height - 3) return true; } return false; };
  maps.forEach((m, i) => {
    const svg = m.querySelector('svg'), at = `${sec(m)} | diagram ${i + 1}`;
    const vb = svg.viewBox.baseVal, scale = svg.getBoundingClientRect().width / vb.width;
    if (scale < 0.8) out.push(`${at} | shrunk to ${Math.round(scale * 100)} %: split it or cut columns | ${svg.getAttribute('aria-label')}`);
    svg.querySelectorAll('text').forEach(t => { const r = t.getBBox();
      if (r.x < vb.x - 1 || r.y < vb.y - 1 || r.x + r.width > vb.x + vb.width + 1 || r.y + r.height > vb.y + vb.height + 1)
        out.push(`${at} | text outside the diagram | ${t.textContent}`); });
    const boxes = [...svg.querySelectorAll('g.n')].map(g => ({g, r: g.querySelector('rect').getBBox()}));
    boxes.forEach(({g, r}) => g.querySelectorAll('text').forEach(t => {
      if (!inside(t.getBBox(), r, 1)) out.push(`${at} | text outside its box | ${t.textContent}`); }));
    const labels = [...svg.querySelectorAll('rect.bg')].map(r => ({r: r.getBBox(), t: r.nextElementSibling.textContent}));
    labels.forEach((l, k) => {
      boxes.forEach(({g, r}) => { if (hit(l.r, r, 1)) out.push(`${at} | label on a box | ${l.t} / ${g.textContent.slice(0, 30)}`); });
      labels.slice(k + 1).forEach(o => { if (hit(l.r, o.r, 1)) out.push(`${at} | labels overlap | ${l.t} / ${o.t}`); });
    });
    svg.querySelectorAll('line:not(.life), polyline').forEach(e => {
      const pts = e.tagName === 'line' ? [[+e.getAttribute('x1'), +e.getAttribute('y1')], [+e.getAttribute('x2'), +e.getAttribute('y2')]]
        : e.getAttribute('points').trim().split(/\s+/).map(p => p.split(',').map(Number));
      for (let k = 0; k + 1 < pts.length; k++) boxes.forEach(({g, r}) => {
        if (cuts(pts[k], pts[k + 1], r)) out.push(`${at} | line through a box | ${g.textContent.slice(0, 30)}`); });
    });
  });
  return out;
}"""
SCROLL = "() => document.scrollingElement.scrollWidth > window.innerWidth + 1"


def main(doc, shots):
    from playwright.sync_api import sync_playwright
    sys.stdout.reconfigure(encoding="utf-8")
    shots = Path(shots)
    shots.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in (1280, 390):
            page = browser.new_page(viewport={"width": width, "height": 900})
            page.goto(Path(doc).resolve().as_uri())
            if page.evaluate(SCROLL):
                problems.append(f"top | page | sideways scroll at {width} px | ")
            page.screenshot(path=str(shots / f"page-{width}.png"), full_page=True)
            if width == 1280:
                problems += page.evaluate(JS)
                for n, m in enumerate(page.query_selector_all(".dg"), 1):
                    m.screenshot(path=str(shots / f"map-{n}.png"))
            page.close()
        browser.close()
    for line in dict.fromkeys(problems):
        print("LAYOUT", line)
    print(f"checked {Path(doc).as_posix()}: {len(set(problems))} LAYOUT, shots in {shots.as_posix()}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
