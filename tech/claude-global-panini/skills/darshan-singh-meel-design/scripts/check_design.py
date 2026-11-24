"""Check a design folder: structure, no network, no absolute paths or private hosts, token use, contrast from the tokens, no filler text.
Usage: python check_design.py designs/<name> [--final] [--no-gitignore] [--project <root>]
Prints FAIL / WARN / OK lines and a summary; exit 1 on any FAIL. Standard library only."""
import argparse
import math
import pathlib
import re
import sys

TOKEN = re.compile(r"--([\w-]+)\s*:\s*([^;]+);")
VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*?))?\s*\)")
NAMED = ("red|blue|green|white|black|gray|grey|orange|purple|pink|yellow|brown|navy|teal|silver|gold|cyan|magenta|lime|olive|maroon|aqua|"
         "fuchsia|indigo|violet|coral|salmon|tomato|crimson|khaki|beige|ivory|tan|wheat|plum|orchid|turquoise|slategr[ae]y|dimgr[ae]y|"
         "lightgr[ae]y|darkgr[ae]y|whitesmoke|gainsboro|royalblue|steelblue|dodgerblue|skyblue|forestgreen|seagreen|firebrick|darkred")
COLOR_FN = r"(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb|color)\("
HEX = r"(?<![\w-])(?<!url\()#[0-9a-fA-F]{3,8}\b"
HARD = re.compile(rf"{HEX}|\b{COLOR_FN}|(?:^|[;{{\s])(?:color|background(?:-color)?|border(?:-\w+)?|outline(?:-color)?|fill|stroke|box-shadow|caret-color|accent-color|text-decoration-color)\s*:[^;}}]*?\b({NAMED})\b", re.I)
SVG_ATTR = re.compile(rf"""\b(?:fill|stroke|stop-color|flood-color)=["'](?!(?:none|currentColor|transparent|url\(|var\()[^"']*)""", re.I)
SIZE = re.compile(r"(?:font-size|border-radius|letter-spacing)\s*:\s*\d*\.?\d+(?:px|rem|em)|(?:transition|animation)[^;{}]*?\b\d*\.?\d+m?s\b", re.I)
EXTERNAL = re.compile(r"""(?<![\w+/=])(?:https?:)?//(?!(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:[/?#"'\s<)]|$))(?!www\.w3\.org/)([\w.-]+)[^\s"'<>)]*""", re.I)
INTERNAL_HOST = re.compile(r"^(?:[\w-]+|.*\.(?:local|internal|corp|lan|intranet|home|test))$", re.I)
PRIVATE_IP = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
ABS = re.compile(r"\b[A-Za-z]:[\\/](?![\\/])[\w.-]|(?<![\w.~/])/(?:Users|home)/[A-Za-z]")
LOREM = re.compile(r"lorem ipsum|dolor sit|placeholder text|\bfoo\b|\bxxx\b", re.I)
MARKERS = re.compile(r"\b(?:TODO|TBD|FIXME)\b")
SECRET_PREFIX = re.compile(r"\b(?:sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{12,}|ghp_[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{20,})|-----BEGIN [A-Z ]*PRIVATE KEY")
SECRET_KV = re.compile(r"(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9+/_\-]{12,})", re.I)
EMAIL = re.compile(r"[\w.+-]+@([\w-]+\.[\w.-]+)")
SPEC_HEADINGS = ["Layout", "Components", "Behaviour", "States", "Responsive", "Accessibility", "Copy", "Acceptance checks", "Maps to"]
TEXT_PAIRS = [("ink", "bg"), ("ink", "surface"), ("ink", "surface-2"), ("ink", "accent-soft"), ("ink-2", "bg"), ("ink-2", "surface"),
              ("ink-2", "surface-2"), ("accent-ink", "accent"), ("ok-ink", "ok"), ("warn-ink", "warn"), ("danger-ink", "danger"),
              ("info-ink", "info"), ("ok-text", "ok-soft"), ("warn-text", "warn-soft"), ("danger-text", "danger-soft"), ("info-text", "info-soft")]
UI_PAIRS = [("accent", "bg"), ("accent", "surface"), ("focus", "bg"), ("focus", "surface"), ("border-strong", "bg"), ("border-strong", "surface")]
STATUS = ["ok", "warn", "danger", "info"]
REQUIRED = ["bg", "surface", "ink", "ink-2", "border", "border-strong", "accent", "accent-ink", "focus"]
KNOBS = ["accent-h", "radius", "density", "font-size-base"]
SHOTS = ["1280-light", "390-light", "1280-dark"]
NAMES = {"white": (1, 1, 1, 1), "black": (0, 0, 0, 1), "transparent": (0, 0, 0, 0), "red": (1, 0, 0, 1), "blue": (0, 0, 1, 1), "green": (0, .5, 0, 1),
         "gray": (.5, .5, .5, 1), "grey": (.5, .5, .5, 1), "silver": (.75, .75, .75, 1), "navy": (0, 0, .5, 1), "orange": (1, .65, 0, 1)}
out = {"FAIL": 0, "WARN": 0}


def say(level, where, msg):
    out[level] = out.get(level, 0) + 1
    print(f"{level} {where} | {msg}")


def num(x, scale=1.0):
    return float(x.rstrip("%deg")) / 100 if x.endswith("%") else float(x) * scale


def srgb(c):
    """(r, g, b, a) in 0-1 from hex, rgb(), hsl(), oklch() or a few names; None when unparsed."""
    try:
        c = c.strip().lower()
        if c in NAMES:
            return NAMES[c]
        if m := re.fullmatch(r"#([0-9a-f]{3,8})", c):
            h = m[1]
            h = "".join(ch * 2 for ch in h) if len(h) in (3, 4) else h
            vals = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
            return (*vals[:3], vals[3] if len(vals) > 3 else 1)
        if m := re.fullmatch(r"(rgba?|hsla?|oklch)\((.+)\)", c):
            fn, body = m[1], m[2]
            body, _, alpha = body.partition("/")
            parts = body.replace(",", " ").split()
            a = num(alpha.strip()) if alpha.strip() else (num(parts[3]) if len(parts) > 3 else 1)
            p = parts[:3]
            if fn.startswith("rgb"):
                return (*[num(x) if x.endswith("%") else float(x) / 255 for x in p], a)
            if fn.startswith("hsl"):
                return (*hsl(float(p[0].rstrip("deg")), num(p[1]), num(p[2])), a)
            L = num(p[0]) if p[0].endswith("%") else float(p[0])
            return (*oklch(L, num(p[1], 1) * (0.4 if p[1].endswith("%") else 1), float(p[2].rstrip("deg"))), a)
    except (ValueError, IndexError):
        return None
    return None


def hsl(h, s, l):
    def f(n):
        k = (n + h / 30) % 12
        return l - s * min(l, 1 - l) * max(-1, min(k - 3, 9 - k, 1))
    return f(0), f(8), f(4)


def oklch(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    gam = lambda v: 1.055 * v ** (1 / 2.4) - 0.055 if v > 0.0031308 else 12.92 * v
    return tuple(min(1, max(0, gam(max(0, v)))) for v in lin)


def over(fg, bg):
    """fg composited over an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1,)


def luminance(rgb):
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def split_top(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    return parts + [cur]


def parse_tokens(css):
    """{name: (light value, dark value)}: the :root block, light-dark() split, then [data-theme=dark] / .dark and light blocks as overrides."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    themed = {}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        mode = 1 if re.search(r"dark", sel) else 0 if re.search(r"light", sel) else None
        if mode is None and not re.search(r":root|^html\b", sel):
            continue
        for m in TOKEN.finditer(body):
            name, val = m[1], m[2].strip()
            ld = re.fullmatch(r"light-dark\((.+)\)", val)
            pair = tuple(x.strip() for x in split_top(ld[1])) if ld and len(split_top(ld[1])) == 2 else (val, val)
            if mode is None:
                themed[name] = pair
            else:
                cur = list(themed.get(name, pair))
                cur[mode] = pair[mode]
                themed[name] = tuple(cur)

    def resolve(text, mode, depth=0):
        def sub(m):
            ref = m[1][2:]
            return resolve(themed[ref][mode], mode, depth + 1) if ref in themed and depth < 8 else (m[2] or m[0])
        return VAR.sub(sub, text)
    return {n: (resolve(v[0], 0), resolve(v[1], 1)) for n, v in themed.items()}


def check_tokens(path):
    css = path.read_text(encoding="utf-8")
    toks = parse_tokens(css)
    where = path.as_posix()
    for n in REQUIRED:
        if n not in toks:
            say("FAIL", where, f"token --{n} missing (needed by the contrast pairs and the canvas)")
    for n in KNOBS:
        if n not in toks:
            say("WARN", where, f"knob --{n} missing: the canvas slider for it stays disabled")
    if "light-dark(" not in css and not re.search(r"data-theme=.dark|\.dark\b", css):
        say("FAIL", where, "no dark theme: use light-dark() per colour token, or a [data-theme=dark] block")
    needed = {t for pair in TEXT_PAIRS + UI_PAIRS for t in pair} | set(STATUS) | {"ink-3"}
    rgb = {}
    for n in needed & set(toks):
        pair = (srgb(toks[n][0]), srgb(toks[n][1]))
        if None in pair:
            say("FAIL", where, f"--{n} not parsed for contrast: {toks[n][0] if pair[0] is None else toks[n][1]}")
        else:
            rgb[n] = pair

    def solid(fg, bg, mode):
        b = rgb[bg][mode]
        if b[3] < 1:
            b = over(b, rgb["bg"][mode]) if bg != "bg" and "bg" in rgb and rgb["bg"][mode][3] == 1 else None
        if b is None:
            return None
        return contrast(over(rgb[fg][mode], b), b)
    for mode, label in ((0, "light"), (1, "dark")):
        if "bg" in rgb and rgb["bg"][mode][3] < 1:
            say("FAIL", where, f"{label}: --bg has alpha; the page background must be opaque")
        for fg, bg, limit, kind in [(f, b, 4.5, "text") for f, b in TEXT_PAIRS] + [(f, b, 3, "controls and focus") for f, b in UI_PAIRS]:
            if fg in rgb and bg in rgb:
                ratio = solid(fg, bg, mode)
                if ratio is not None and ratio < limit:
                    say("FAIL", where, f"{label}: --{fg} on --{bg} = {ratio:.2f}:1, {kind} need {limit}:1")
        for s in STATUS:
            if s in rgb and "bg" in rgb and (ratio := solid(s, "bg", mode)) is not None:
                if ratio < 3:
                    say("FAIL", where, f"{label}: --{s} on --bg = {ratio:.2f}:1, unusable even as an icon (3:1)")
                elif ratio < 4.5:
                    say("WARN", where, f"{label}: --{s} on --bg = {ratio:.2f}:1, not for text; use a fill with --{s}-ink or --{s}-text on --{s}-soft")
        if "ink-3" in rgb and "bg" in rgb and (ratio := solid("ink-3", "bg", mode)) is not None and ratio < 3:
            say("WARN", where, f"{label}: --ink-3 on --bg = {ratio:.2f}:1; disabled text only, and even that should stay legible")
    return toks


def check_text(path, kind):
    text = path.read_text(encoding="utf-8", errors="ignore")
    where = path.as_posix()
    if m := ABS.search(text):
        say("FAIL", where, f"absolute path '{m[0]}…'")
    if m := PRIVATE_IP.search(text):
        say("FAIL", where, f"private address {m[0]}: no internal hosts in a design")
    for m in SECRET_PREFIX.finditer(text):
        say("FAIL", where, f"secret-looking value near '{m[0][:8]}…' <redacted>")
    for m in SECRET_KV.finditer(text):
        if re.search(r"\d", m[1]) and re.search(r"[A-Za-z]", m[1]):
            say("FAIL", where, f"secret-looking value near '{m[0][:10]}…' <redacted>")
    for m in EMAIL.finditer(text):
        if not re.search(r"example\.\w+$|\.test$|\.invalid$", m[1]):
            say("WARN", where, f"e-mail with a real-looking domain {m[1]}: synthetic content only")
    for m in EXTERNAL.finditer(re.sub(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+", "data:…", text)):
        if kind in ("html", "css"):
            say("FAIL", where, f"external URL {m[0][:60]}: no network, no CDN, no webfont")
        elif INTERNAL_HOST.match(m[1]):
            say("FAIL", where, f"internal host {m[1]}: nothing company-specific in a design")
        else:
            say("WARN", where, f"URL {m[0][:60]} in a design document: keep references local, official docs pages are fine")
    if kind in ("html", "css"):
        visible = re.sub(r"<[^>]+>", " ", re.sub(r"<(style|script)[^>]*>.*?</(?:style|script)>", " ", text, flags=re.S | re.I))
        for word in sorted({m[0].lower() for m in LOREM.finditer(visible)} | {m[0] for m in MARKERS.finditer(visible)}):
            say("FAIL", where, f"filler text '{word}'")
    return text


def structure_key(html):
    body = re.sub(r"<(style|script)[^>]*>.*?</(?:style|script)>", "", html, flags=re.S | re.I)
    return tuple(t.lower() for t in re.findall(r"<(header|nav|main|aside|section|article|footer|table|form|ul|ol|dialog|details|canvas|svg|h[1-6]|button|input|select|textarea)\b", body, re.I))


def check_direction(path, final=False):
    html = check_text(path, "html")
    where = path.as_posix()
    body = re.search(r"<body[^>]*>", html, re.I)
    attrs = {m[1]: m[2] if m[2] is not None else m[3]
             for m in re.finditer(r"""data-(direction|name|screen|pitch)=(?:"([^"]*)"|'([^']*)')""", body[0])} if body else {}
    if "direction" not in attrs or "name" not in attrs:
        say("WARN" if final else "FAIL", where, "body needs data-direction and data-name (data-screen when several screens, data-pitch optional)")
    if not re.search(r"tokens\.css", html):
        say("FAIL", where, "no <link rel=stylesheet href=…tokens.css>: every colour, size and radius comes from the tokens")
    styles = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I) + re.findall(r"""style=["']([^"']*)["']""", html))
    hard = [m[0].strip() for m in HARD.finditer(styles)] + [m[0] for m in SVG_ATTR.finditer(html)]
    if hard:
        say("FAIL", where, f"{len(hard)} colour literals outside tokens.css, e.g. {', '.join(h[:30] for h in hard[:3])}: use var(--…)")
    sizes = [m[0].strip() for m in SIZE.finditer(styles)]
    if sizes:
        say("WARN", where, f"{len(sizes)} size or duration literals, e.g. {', '.join(sizes[:3])}: prefer --text-*, --radius-*, --motion*")
    if not re.search(r"<meta[^>]+viewport", html, re.I):
        say("WARN", where, "no viewport meta: the mobile frame renders at desktop width")
    h1 = len(re.findall(r"<h1\b", html, re.I))
    if h1 != 1:
        say("WARN", where, f"{h1} h1 elements, one expected")
    if not re.search(r"<main\b", html, re.I):
        say("WARN", where, "no <main> landmark")
    if re.search(r"transition|animation", styles) and "prefers-reduced-motion" not in html:
        say("WARN", where, "motion without a prefers-reduced-motion rule")
    for state in ("hover", "focus-visible"):
        if f":{state}" not in styles:
            say("WARN", where, f"no :{state} style")
    return attrs.get("direction", path.stem[:1].upper()), structure_key(html)


def wanted_shots(folder):
    brief = next((d / "brief.md" for d in folder.resolve().parents if (d / "brief.md").is_file()), None)
    m = re.search(r"^- Devices:\s*(desktop|phone|both)\s*$", brief.read_text(encoding="utf-8"), re.M) if brief else None
    device = m.group(1) if m else "both"
    return [s for s in SHOTS if device == "both" or s.startswith("390") == (device == "phone")]


def check_shots(folder, files):
    missing = [f"{p.stem}-{s}" for p in files for s in wanted_shots(folder) if not (folder / "shots" / f"{p.stem}-{s}.png").is_file()]
    if missing:
        say("WARN", (folder / "shots").as_posix(), f"required screenshots missing ({len(missing)}): {', '.join(missing[:4])}… run screenshot.py")


def check_round(rnd):
    files = [p for p in sorted(rnd.glob("*.html")) if not p.name.startswith("canvas")]
    if not files:
        say("FAIL", rnd.as_posix(), "no direction files (<key>-<slug>.html)")
        return
    keys = {}
    for p in files:
        key, sk = check_direction(p)
        keys.setdefault(key, []).append((p.name, sk))
    say("OK", rnd.as_posix(), f"{len(keys)} direction(s) {', '.join(sorted(keys))} in {len(files)} file(s)")
    names = sorted(keys)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for fa, fb in [(fa, fb) for fa, ka in keys[a] for fb, kb in keys[b] if ka == kb]:
                say("WARN", rnd.as_posix(), f"{fa} and {fb} have the same element structure: are they structurally different directions?")
    if not (rnd / "canvas.html").is_file():
        say("WARN", rnd.as_posix(), "no canvas.html: run build_canvas.py")
    else:
        check_text(rnd / "canvas.html", "html")
    check_shots(rnd, files)


def section(md, heading):
    m = re.search(rf"^#+\s*{re.escape(heading)}\b[^\n]*\n(.*?)(?=^#+\s|\Z)", md, re.M | re.S)
    return m[1] if m else ""


def check_final(final, project, root_tokens):
    for name in ("index.html", "tokens.css", "spec.md", "handoff-prompt.md"):
        if not (final / name).is_file():
            say("FAIL", final.as_posix(), f"{name} missing")
    if not (final / "states.html").is_file():
        say("WARN", final.as_posix(), "states.html missing: every loading, empty, error and interactive state drawn on one page")
    pages = [p for p in sorted(final.glob("*.html")) if not p.name.startswith("canvas")]
    for p in pages:
        check_direction(p, final=True)
    check_shots(final, [p for p in pages if p.name != "states.html"])
    if (final / "tokens.css").is_file():
        check_tokens(final / "tokens.css")
        check_text(final / "tokens.css", "css")
        if root_tokens and (final / "tokens.css").read_text(encoding="utf-8").split() != root_tokens.split():
            say("FAIL", (final / "tokens.css").as_posix(), "differs from designs/<name>/tokens.css: one source of truth, copy the root file or update both")
    if (final / "spec.md").is_file():
        spec = check_text(final / "spec.md", "md")
        for h in SPEC_HEADINGS:
            if not re.search(rf"^#+\s*{re.escape(h)}\b", spec, re.M | re.I):
                say("FAIL", (final / "spec.md").as_posix(), f"section '{h}' missing")
        for p in re.findall(r"`([^`\n]+\.[a-z]{1,5})`", section(spec, "Maps to")):
            if not (project / p).exists():
                say("WARN", (final / "spec.md").as_posix(), f"Maps to: {p} not found under the project root; mark it 'to create' without backticks")
    if (final / "handoff-prompt.md").is_file():
        hp = check_text(final / "handoff-prompt.md", "md")
        if not all(x in hp.lower() for x in ("job", "```", "deliver", "synthetic")):
            say("FAIL", (final / "handoff-prompt.md").as_posix(), "not self-contained: needs the job, a tokens block, synthetic-content rule and what to deliver")


def gitignored(gi):
    lines = [l.split("#", 1)[0].strip() for l in gi.read_text(encoding="utf-8").splitlines()] if gi.is_file() else []
    return any(re.fullmatch(r"/?designs/?", l) for l in lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--final", action="store_true", help="require the final/ deliverables")
    ap.add_argument("--no-gitignore", action="store_true", help="skip the .gitignore check (example inside a tracked repo)")
    ap.add_argument("--project", help="project root; default: the parent of designs/")
    a = ap.parse_args()
    d = pathlib.Path(a.folder)
    if not d.is_dir():
        sys.exit(f"ERROR not a folder: {d}")
    project = pathlib.Path(a.project) if a.project else d.resolve().parent.parent
    for name in ("brief.md", "tokens.css"):
        if not (d / name).is_file():
            say("FAIL", d.as_posix(), f"{name} missing")
    if (d / "brief.md").is_file():
        check_text(d / "brief.md", "md")
    root_tokens = ""
    if (d / "tokens.css").is_file():
        check_tokens(d / "tokens.css")
        root_tokens = check_text(d / "tokens.css", "css")
    rounds = sorted(p for p in d.glob("round-*") if p.is_dir())
    if not rounds:
        say("FAIL", d.as_posix(), "no round-N/ folder")
    for rnd in rounds:
        check_round(rnd)
        for md in rnd.glob("*.md"):
            check_text(md, "md")
    if a.final or (d / "final").is_dir():
        check_final(d / "final", project, root_tokens)
    if (d / "before").is_dir():
        say("OK", (d / "before").as_posix(), f"{len([p for p in (d / 'before').iterdir() if p.is_file()])} image(s)")
    if (d / "imports").is_dir():
        for p in sorted((d / "imports").glob("*.htm*")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            urls = len(EXTERNAL.findall(text))
            scripts = len(re.findall(r"<script\b", text, re.I))
            say("WARN", p.as_posix(), f"untrusted import: {urls} external URL(s), {scripts} script(s); render with screenshot.py --no-js, rebuild ideas, copy no text")
    if not a.no_gitignore and not gitignored(project / ".gitignore"):
        say("FAIL", (project / ".gitignore").as_posix(), "add '/designs/' with a one-line comment")
    print(f"{out['FAIL']} FAIL, {out['WARN']} WARN")
    sys.exit(1 if out["FAIL"] else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
