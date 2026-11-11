"""Climate diagram (Walter/Lieth school form) as inline SVG.

Usage: python klimadiagramm.py NAME HOEHE_M T1,...,T12 N1,...,N12 [--out datei.svg] [--sued]
  T = monthly mean temperature in deg C, N = monthly precipitation in mm, January to December.
  --sued: southern hemisphere, months run July to June.
Scale: 10 deg C = 20 mm; above 100 mm the precipitation axis is compressed to 1/10 (marked); deg C labels end at 50.
Prints the SVG and, on stderr, the values a worksheet needs (annual mean, sum, range, arid months).
"""
import math
import sys

W, H = 600, 446
X0, X1, Y_TOP, Y_BOT = 70, 502, 70, 350
MONATE = "JFMAMJJASOND"
NAMEN = "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split()


def einheit(n):
    """Precipitation in mm -> height in temperature units (deg C)."""
    return n / 2 if n <= 100 else 50 + (n - 100) / 20


def mm(u):
    return 2 * u if u <= 50 else 100 + (u - 50) * 20


def de(x, stellen=1):
    return f"{x:.{stellen}f}".replace(".", ",")


def diagramm(name, hoehe, t, n, sued=False):
    if len(t) != 12 or len(n) != 12:
        sys.exit("need 12 temperatures and 12 precipitation values")
    mittel, summe = sum(t) / 12, sum(n)
    arid = [i for i in range(12) if n[i] < 2 * t[i]]
    order = list(range(6, 12)) + list(range(6)) if sued else list(range(12))
    unten = min(0, math.floor(min(t) / 10) * 10)
    oben = max(30, math.ceil(max(max(t), max(einheit(v) for v in n)) / 10) * 10)
    k = (Y_BOT - Y_TOP) / (oben - unten)
    y = lambda u: Y_BOT - (u - unten) * k
    bw = (X1 - X0) / 12
    label = (f"Klimadiagramm {name}: Jahresmittel {de(mittel)} °C, Jahresniederschlag {de(summe, 0)} mm / "
             f"climate diagram {name}: annual mean {mittel:.1f} °C, annual precipitation {summe:.0f} mm")
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{label}" font-family="Segoe UI,Arial,sans-serif" font-size="15">',
         f'<text x="{X0}" y="28" font-size="18" font-weight="700">{name} ({hoehe} m)</text>',
         f'<text x="{X1}" y="28" text-anchor="end" font-size="16">{de(mittel)} °C · {de(summe, 0)} mm</text>',
         f'<text x="{X0 - 8}" y="56" text-anchor="end">°C</text><text x="{X1 + 8}" y="56">mm</text>']
    for u in range(unten, oben + 1, 10):
        s.append(f'<line x1="{X0}" y1="{y(u):.1f}" x2="{X1}" y2="{y(u):.1f}" stroke="#b8b8b8" stroke-width="1"/>')
        if u <= 50:  # above the 100 mm line the left axis is compressed precipitation, not temperature
            s.append(f'<text x="{X0 - 8}" y="{y(u) + 5:.1f}" text-anchor="end">{u}</text>')
        if u >= 0:
            s.append(f'<text x="{X1 + 8}" y="{y(u) + 5:.1f}">{mm(u):.0f}</text>')
    if oben > 50:  # compressed part of the precipitation axis
        s.append(f'<line x1="{X0}" y1="{y(50):.1f}" x2="{X1}" y2="{y(50):.1f}" stroke="#111" stroke-width="1.5" stroke-dasharray="6 4"/>')
        s.append(f'<text x="{X0}" y="{H - 8}" font-size="14">- - -  ab 100 mm: Achse 1:10 gestaucht / above 100 mm: axis compressed 1:10</text>')
    for pos, i in enumerate(order):
        x = X0 + pos * bw
        top = y(einheit(n[i]))
        s.append(f'<rect x="{x + 4:.1f}" y="{top:.1f}" width="{bw - 8:.1f}" height="{y(0) - top:.1f}" fill="#a9c4e8" stroke="#1a4480" stroke-width="1.5"/>')
        if n[i] > 100:
            s.append(f'<rect x="{x + 4:.1f}" y="{top:.1f}" width="{bw - 8:.1f}" height="{y(50) - top:.1f}" fill="#1a4480"/>')
        s.append(f'<text x="{x + bw / 2:.1f}" y="{Y_BOT + 20}" text-anchor="middle">{MONATE[i]}</text>')
    pts = [(X0 + (pos + .5) * bw, y(t[i])) for pos, i in enumerate(order)]
    s.append('<polyline fill="none" stroke="#a11212" stroke-width="3" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    s += [f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4" fill="#fff" stroke="#a11212" stroke-width="2"/>' for a, b in pts]
    s.append(f'<line x1="{X0}" y1="{y(0):.1f}" x2="{X1}" y2="{y(0):.1f}" stroke="#111" stroke-width="2"/>')
    s.append(f'<line x1="{X0}" y1="{Y_TOP}" x2="{X0}" y2="{Y_BOT}" stroke="#111" stroke-width="2"/><line x1="{X1}" y1="{Y_TOP}" x2="{X1}" y2="{Y_BOT}" stroke="#111" stroke-width="2"/>')
    ly = H - 46
    s.append(f'<line x1="{X0}" y1="{ly}" x2="{X0 + 34}" y2="{ly}" stroke="#a11212" stroke-width="3"/><circle cx="{X0 + 17}" cy="{ly}" r="4" fill="#fff" stroke="#a11212" stroke-width="2"/>')
    s.append(f'<text x="{X0 + 42}" y="{ly + 5}">Temperatur / temperature</text>')
    s.append(f'<rect x="{X0 + 250}" y="{ly - 9}" width="20" height="18" fill="#a9c4e8" stroke="#1a4480" stroke-width="1.5"/>')
    s.append(f'<text x="{X0 + 278}" y="{ly + 5}">Niederschlag / precipitation</text>')
    s.append("</svg>")
    info = (f"Jahresmittel {de(mittel)} °C · Jahressumme {de(summe, 0)} mm · wärmster Monat {NAMEN[t.index(max(t))]} mit {de(max(t))} °C · "
            f"kältester Monat {NAMEN[t.index(min(t))]} mit {de(min(t))} °C · Jahresamplitude {de(max(t) - min(t))} K · "
            f"aride Monate (N < 2T): {', '.join(NAMEN[i] for i in arid) or 'keine'}")
    return "\n".join(s), info


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    out = None
    if "--out" in args:  # anywhere on the line; its value is not a positional argument
        i = args.index("--out")
        if i + 1 == len(args):
            sys.exit("--out needs a file name")
        out = args[i + 1]
        del args[i:i + 2]
    sued = "--sued" in args
    args = [a for a in args if a != "--sued"]  # negative temperatures start with "-", so only the known flags are removed
    if len(args) != 4:
        sys.exit(__doc__)
    zahlen = lambda text: [float(v) for v in text.replace(";", ",").split(",")]
    svg, info = diagramm(args[0], args[1], zahlen(args[2]), zahlen(args[3]), sued)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg)
    else:
        print(svg)
    print(info, file=sys.stderr)


if __name__ == "__main__":
    main()
