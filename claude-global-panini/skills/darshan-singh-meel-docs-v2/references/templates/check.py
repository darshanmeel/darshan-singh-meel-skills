"""Render a built doc and list layout problems: overflow, overlaps, cut-off values, sideways scroll.

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
  });
  document.querySelectorAll('.journey td, .card td, .card p, .stage .h').forEach(c => { if (c.scrollWidth > c.clientWidth + 1) add(c, 'value cut off'); });
  document.querySelectorAll('.journey').forEach(j => { if (j.scrollWidth > j.clientWidth + 1) add(j, 'journey wider than page'); });
  return out;
}"""


def main(path, shot=None):
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
