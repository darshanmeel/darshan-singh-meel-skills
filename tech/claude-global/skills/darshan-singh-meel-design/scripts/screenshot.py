"""Screenshots of local HTML files or loopback pages at several viewports and themes, with layout and accessibility measurements.
Usage: python screenshot.py <file.html | folder | http://localhost:PORT/...> [...] --out shots/
       [--viewports 1280x800,390x844] [--themes light,dark] [--full] [--keyboard 12] [--hover "button"] [--no-js]
Prints SHOT <path> per image, WARN <target> <viewport> <theme> | <measurement>, KEYS ... for the tab walk, FAIL for a page that could not be
shot; exit 0, or 2 when any target failed or was not found. Needs Python Playwright; launches the installed Chrome or Edge, then Playwright's
own Chromium. Every request that is not a local file, data: or loopback http is aborted: nothing leaves the machine."""
import argparse
import pathlib
import re
import sys
from urllib.parse import urlsplit

LOOPBACK = ("localhost", "127.0.0.1", "::1")
MEASURE = """() => {
  const de = document.documentElement, out = {};
  out.overflow = de.scrollWidth > de.clientWidth ? `${de.scrollWidth} > ${de.clientWidth}` : null;
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const name = (el) => (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ' "' + (el.getAttribute('aria-label') || el.textContent || el.value || el.placeholder || '').trim().slice(0, 30) + '"');
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d');
  const rgb = (s) => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = s; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data;
    return { r: d[0], g: d[1], b: d[2], a: d[3] / 255 }; };  /* any CSS colour, including oklch() computed values */
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.a > 0) return c; } return { r: 255, g: 255, b: 255, a: 1 }; };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return ((Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05)).toFixed(2); };
  out.small = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[role=button],[tabindex]:not([tabindex="-1"])')]
    .filter(vis).map((el) => [el, el.getBoundingClientRect()]).filter(([, r]) => r.width < 24 || r.height < 24)
    .map(([el, r]) => `${name(el)} ${Math.round(r.width)}x${Math.round(r.height)}`).slice(0, 8);
  out.tiny = [...document.querySelectorAll('body *')].filter((el) => vis(el) && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
    .filter((el) => parseFloat(getComputedStyle(el).fontSize) < 12).map((el) => `${name(el)} ${getComputedStyle(el).fontSize}`).slice(0, 8);
  out.noalt = [...document.querySelectorAll('img:not([alt])')].length;
  out.unlabelled = [...document.querySelectorAll('input:not([type=hidden]),select,textarea')].filter(vis).filter((el) =>
    !el.labels?.length && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby')).map(name).slice(0, 8);
  out.placeholder = [...document.querySelectorAll('input[placeholder],textarea[placeholder]')].filter(vis).map((el) => {
    const r = ratio(rgb(getComputedStyle(el, '::placeholder').color), bgOf(el)); return r < 4.5 ? `${name(el)} ${r}:1` : null; }).filter(Boolean).slice(0, 6);
  out.accent = [...document.querySelectorAll('input[type=checkbox],input[type=radio],input[type=range],progress')].filter(vis)
    .filter((el) => getComputedStyle(el).accentColor === 'auto').length;
  out.h1 = document.querySelectorAll('h1').length;
  return out;
}"""

FOCUS = """() => { const el = document.activeElement; if (!el || el === document.body) return null;
  const s = getComputedStyle(el); const visible = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none';
  return { name: el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ' "' + (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 30) + '"', visible }; }"""


def is_local(url):
    u = urlsplit(url)
    return u.scheme in ("file", "data", "about", "blob") or (u.scheme == "http" and u.hostname in LOOPBACK)


def stem_of(text, used):
    stem = re.sub(r"[^\w.-]+", "_", text).strip("_.")[:80] or "page"
    n, base = 2, stem
    while stem in used:
        stem, n = f"{base}-{n}", n + 1
    used.add(stem)
    return stem


def targets(args, used):
    for t in args:
        if t.startswith(("http://", "https://")):
            if is_local(t):
                u = urlsplit(t)
                yield t, stem_of((u.path.rsplit("/", 1)[-1] or "index") + ("-" + u.query if u.query else ""), used)
            else:
                print(f"SKIP {t} | only local files and loopback http are opened")
                yield None, t
        elif pathlib.Path(t).is_dir():
            for p in sorted(pathlib.Path(t).glob("*.html")):
                if not p.name.startswith("canvas"):
                    yield p.resolve().as_uri(), stem_of(p.stem, used)
        elif pathlib.Path(t).is_file():
            yield pathlib.Path(t).resolve().as_uri(), stem_of(pathlib.Path(t).stem, used)
        else:
            print(f"SKIP {t} | not found")
            yield None, t


def launch(p):
    last = None
    for channel in ("chrome", "msedge", None):
        try:
            return p.chromium.launch(channel=channel) if channel else p.chromium.launch()
        except Exception as e:  # noqa: BLE001 - try the next browser
            last = e
    sys.exit(f"ERROR no browser: Chrome, Edge and Playwright's Chromium all failed ({str(last).splitlines()[0]}). "
             "Install Chrome or Edge, or run: python -m playwright install chromium")


def shot(page, path):
    page.screenshot(path=str(path), full_page=path.name.endswith("-full.png"))
    if not path.is_file() or path.stat().st_size == 0:
        print(f"FAIL {path.as_posix()} | screenshot not written")
        return False
    print(f"SHOT {path.as_posix()}")
    return True


def shoot(page, url, stem, vp, theme, a, out):
    page.set_viewport_size({"width": vp[0], "height": vp[1]})
    page.emulate_media(color_scheme=theme)
    where = f"{stem} {vp[0]}x{vp[1]} {theme}"
    try:
        page.goto(url, wait_until="load", timeout=20000)
        page.evaluate("t => document.documentElement.dataset.theme = t", theme)
        page.wait_for_timeout(250)
    except Exception as e:  # noqa: BLE001 - report and move on
        print(f"FAIL {where} | could not open: {str(e).splitlines()[0][:120]}")
        return False
    tag = f"{stem}-{vp[0]}-{theme}"
    ok = shot(page, out / f"{tag}{'-full' if a.full else ''}.png")
    try:
        m = page.evaluate(MEASURE)
    except Exception as e:  # noqa: BLE001 - a page that navigated away or has no DOM
        print(f"FAIL {where} | could not measure: {str(e).splitlines()[0][:120]}")
        return False
    if m["overflow"]:
        print(f"WARN {where} | horizontal overflow {m['overflow']}")
    if m["small"]:
        print(f"WARN {where} | {len(m['small'])}+ targets under 24px: {'; '.join(m['small'][:4])}")
    if m["tiny"]:
        print(f"WARN {where} | {len(m['tiny'])}+ elements with text under 12px: {'; '.join(m['tiny'][:4])}")
    if m["noalt"]:
        print(f"WARN {where} | {m['noalt']} img without alt")
    for s in m["unlabelled"]:
        print(f"WARN {where} | input without label: {s}")
    for s in m["placeholder"]:
        print(f"WARN {where} | placeholder under 4.5:1: {s}")
    if m["accent"]:
        print(f"WARN {where} | {m['accent']} native controls with accent-color auto (browser blue): set accent-color: var(--accent)")
    if m["h1"] != 1:
        print(f"WARN {where} | {m['h1']} h1 elements")
    if a.hover:
        seen, n = set(), 0
        for el in page.locator(a.hover).all():
            sig = el.evaluate("e => e.tagName + '|' + e.className + '|' + (e.getAttribute('aria-label') || e.textContent || e.placeholder || '').trim().slice(0, 20)")
            if sig in seen or not el.is_visible():
                continue
            seen.add(sig)
            n += 1
            el.hover()
            page.wait_for_timeout(150)
            ok &= shot(page, out / f"{tag}-hover{n}.png")
            if n == 3:
                break
        if not n:
            print(f"WARN {where} | hover selector not found: {a.hover}")
    if a.keyboard:
        seen = []
        for n in range(a.keyboard):
            page.keyboard.press("Tab")
            f = page.evaluate(FOCUS)
            if not f:
                break
            seen.append(f"{n + 1}:{f['name']}" + ("" if f["visible"] else " (focus not visible)"))
            if not f["visible"]:
                print(f"WARN {where} | focus not visible on stop {n + 1}: {f['name']}")
            if n in (0, a.keyboard // 2):
                ok &= shot(page, out / f"{tag}-kbd{n + 1}.png")
        print(f"KEYS {where} | " + " → ".join(seen))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--viewports", default="1280x800,390x844")
    ap.add_argument("--themes", default="light,dark")
    ap.add_argument("--full", action="store_true", help="full-page screenshots")
    ap.add_argument("--keyboard", type=int, default=0, help="tab through N stops and report focus visibility")
    ap.add_argument("--hover", help="CSS selector; up to 3 distinct matches are hovered and shot")
    ap.add_argument("--no-js", action="store_true", help="for untrusted HTML (imports)")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("ERROR Python Playwright is not installed: pip install playwright (Chrome or Edge is enough to run it)")
    try:
        vps = [tuple(int(x) for x in v.lower().split("x")) for v in a.viewports.split(",")]
    except ValueError:
        sys.exit(f"ERROR --viewports must look like 1280x800,390x844 (got {a.viewports})")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    failed, done, used = 0, 0, set()
    with sync_playwright() as p:
        browser = launch(p)
        ctx = browser.new_context(java_script_enabled=not a.no_js, reduced_motion="reduce")
        ctx.route("**/*", lambda route: route.continue_() if is_local(route.request.url) else route.abort())
        page = ctx.new_page()
        for url, stem in targets(a.targets, used):
            if not url:
                failed += 1
                continue
            for vp in vps:
                for theme in a.themes.split(","):
                    if shoot(page, url, stem, vp, theme, a, out):
                        done += 1
                    else:
                        failed += 1
        browser.close()
    if not done:
        print("ERROR nothing was shot")
    sys.exit(2 if failed or not done else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
