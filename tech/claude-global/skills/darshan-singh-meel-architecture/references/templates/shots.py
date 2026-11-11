"""Screenshots for the layout read, after docs-v2 check.py: one PNG per section at 1280 px (readable at native size,
unlike the downscaled full page) and again at 390 px (phone; a full phone page is too tall to read).

Usage: python shots.py <doc.html> <shots_dir>   → s1.png … s8.png, p1.png … p8.png. Needs Playwright (as check.py).
"""
import sys
from pathlib import Path


def main(path, shots):
    from playwright.sync_api import sync_playwright
    out = Path(shots)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1280, "height": 900})
        page.goto(Path(path).resolve().as_uri())
        page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
        secs = page.locator("section")
        n = secs.count()
        for i in range(n):
            secs.nth(i).screenshot(path=str(out / f"s{i + 1}.png"))
        page.set_viewport_size({"width": 390, "height": 900})
        for i in range(n):
            secs.nth(i).screenshot(path=str(out / f"p{i + 1}.png"))
        b.close()
    print(f"shots: {out.as_posix()}/s1..s{n}.png (1280 px) and p1..p{n}.png (390 px): read every one")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
