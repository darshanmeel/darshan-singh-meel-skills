"""True-to-scale timeline as inline SVG (equal time = equal length).

Usage: python zeitleiste.py START ENDE EVENTS.txt [--out datei.svg] [--anim]
  START, ENDE: YYYY, YYYY-MM or YYYY-MM-DD; years before Christ negative (-0753).
  EVENTS.txt: one event per line, `DATE|Beschriftung DE / EN`; `#` starts a comment.
  --anim: stage for the base animation.html - svg id="buehne", events hidden (opacity 0), progress line id="lauf".
Each event is a group `<g id="e1">`, `e2`, ... in date order, so an animation can fade them in.
Ticks sit on whole steps (1 January, first of a month), not on START.
Prints the SVG and, on stderr, date -> x position of every event (for animation steps and for checking).
There is no year 0: a span across the change of era is drawn one year too long.
"""
import html
import math
import re
import sys

W, H, X0, X1, Y = 760, 316, 60, 700, 170
STEPS = [1 / 12, 0.25, 1, 5, 10, 25, 50, 100, 250, 500, 1000]
LEVELS = [(40, 60), (232, 252), (95, 115), (282, 302)]  # (date line y, label line y), alternating above/below
NAH = {0: 2, 3: 1}  # far level -> near level on the same side, which its stem crosses


def jahr(text):
    """Date text -> decimal year."""
    m = re.fullmatch(r"(-?\d+)(?:-(\d\d))?(?:-(\d\d))?", text.strip())
    if not m:
        sys.exit(f"bad date: {text}")
    y, mo, d = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)
    return y + (mo - 1) / 12 + (d - 1) / 365


def datum(text):
    """2024-03-05 -> 5.3.2024; -0753 -> 753 v. Chr."""
    m = re.fullmatch(r"(-?\d+)(?:-(\d\d))?(?:-(\d\d))?", text.strip())
    y = int(m.group(1))
    jahrtext = f"{-y} v. Chr." if y < 0 else str(y)
    teile = [str(int(p)) for p in (m.group(3), m.group(2)) if p]
    return ".".join(teile + [jahrtext])


def zeitleiste(start, ende, events, anim=False):
    a, b = jahr(start), jahr(ende)
    x = lambda t: X0 + (t - a) / (b - a) * (X1 - X0)
    step = next((s for s in STEPS if (b - a) / s <= 24), STEPS[-1])
    events = sorted(events, key=lambda e: jahr(e[0]))
    buehne = ' id="buehne" class="buehne"' if anim else ""
    versteckt = ' opacity="0"' if anim else ""
    s = [f'<svg{buehne} viewBox="0 0 {W} {H}" role="img" aria-label="Zeitleiste von {datum(start)} bis {datum(ende)} mit {len(events)} Ereignissen / '
         f'timeline from {datum(start)} to {datum(ende)} with {len(events)} events" font-family="Segoe UI,Arial,sans-serif">',
         f'<line x1="{X0}" y1="{Y}" x2="{X1}" y2="{Y}" stroke="#111" stroke-width="2"/>']
    n = round((b - a) / step)
    jede = 1 if n <= 8 else 2 if n <= 16 else 4
    for i in range(math.ceil(a / step - 1e-6), math.floor(b / step + 1e-6) + 1):  # whole steps only
        t = i * step
        gross = i % jede == 0
        s.append(f'<line x1="{x(t):.1f}" y1="{Y - (10 if gross else 6)}" x2="{x(t):.1f}" y2="{Y + (10 if gross else 6)}" stroke="#111" stroke-width="2"/>')
        if gross:
            mon = round(t * 12)
            y = mon // 12
            text = f"{mon % 12 + 1}/{y}" if step < 1 else ("Chr. Geb." if y == 0 else f"{-y} v. Chr." if y < 0 else str(y))
            s.append(f'<text x="{x(t):.1f}" y="{Y + 30 if i // jede % 2 else Y - 18}" font-size="16" text-anchor="middle">{text}</text>')
    if anim:
        s.append(f'<line id="lauf" x1="{X0}" y1="{Y}" x2="{X0}" y2="{Y}" stroke="#1a4480" stroke-width="7" stroke-linecap="round"/>')
    pos, belegt = [], []  # belegt: (level, left, right, stem x) of every placed label

    def frei(lv, li, re_, px):
        for lv2, li2, re2, px2 in belegt:
            if lv2 == lv and li < re2 + 10 and li2 < re_ + 10:  # two labels on one line
                return False
            if NAH.get(lv) == lv2 and li2 - 6 < px < re2 + 6:  # own stem through a label
                return False
            if NAH.get(lv2) == lv and li - 6 < px2 < re_ + 6:  # own label over a stem
                return False
        return True

    for k, (d, label) in enumerate(events):
        px = x(jahr(d))
        if not X0 - 0.05 <= px <= X1 + 0.05:
            sys.exit(f"event outside the timeline: {d}")
        halb = 4.4 * max(len(label), len(datum(d))) + 8  # rough half width of the label: keeps it inside the picture
        tx = min(max(px, halb), W - halb)
        lv = next((c for c in ((k + j) % 4 for j in range(4)) if frei(c, tx - halb, tx + halb, px)), k % 4)
        belegt.append((lv, tx - halb, tx + halb, px))
        y1, y2 = LEVELS[lv]
        s.append(f'<g id="e{k + 1}"{versteckt}><line x1="{px:.1f}" y1="{y2 + 6 if y2 < Y else y1 - 19}" x2="{px:.1f}" y2="{Y}" stroke="#1a4480" stroke-width="2"/>'
                 f'<circle cx="{px:.1f}" cy="{Y}" r="8" fill="#fff" stroke="#1a4480" stroke-width="4"/>'
                 f'<text x="{tx:.1f}" y="{y1}" text-anchor="middle" font-size="17" font-weight="700">{datum(d)}</text>'
                 f'<text x="{tx:.1f}" y="{y2}" text-anchor="middle" font-size="16">{html.escape(label)}</text></g>')
        pos.append(f"e{k + 1}  {datum(d)}  x={px:.1f}  {label}")
    s.append("</svg>")
    return "\n".join(s), "\n".join(pos)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 == len(args):
            sys.exit("--out needs a file name")
        out = args[i + 1]
        del args[i:i + 2]
    anim = "--anim" in args
    args = [a for a in args if a != "--anim"]
    if len(args) != 3:
        sys.exit(__doc__)
    with open(args[2], encoding="utf-8") as f:
        zeilen = [z.strip() for z in f if z.strip() and not z.lstrip().startswith("#")]
    events = [tuple(p.strip() for p in z.split("|", 1)) for z in zeilen]
    svg, pos = zeitleiste(args[0], args[1], events, anim)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg)
    else:
        print(svg)
    print(pos, file=sys.stderr)


if __name__ == "__main__":
    main()
