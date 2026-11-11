"""Recompute the numeric answers and the points of maths material.

Usage: python check_rechnung.py <file-or-folder>      (a folder is searched with all its subfolders)

Answers: reads data-check="expr; expr; ..." on every element that has data-aufgabe (sections in loesung.html, rows in
erwartungshorizont.html, example and practice tasks in erklaerung.html). Every expr must be true. data-check="-" marks
a task without a numeric answer. A solution task without data-check is listed with "?".
Points (files with data-gesamt): data-teilpunkte="2+1+1" must add up to data-punkte ("?" when a marking-scheme row of
2 or more points has none); printed AFB shares = points : total; grade key data-ab = printed percentage x total
(16 rows: exact; otherwise exact or rounded up by less than one point); test.html and erwartungshorizont.html of one
folder agree in ids, points and AFB.
Exit code 1 when a check is false or broken, or when no .html file is found. A passing run shows that the material
agrees with itself, not that an answer is right: each task needs a check that puts the answer back into the given data.

Expressions are Python arithmetic, evaluated by a small whitelist evaluator (no eval, no attributes, no imports):
  1/2 + 1/3 == 5/6              int / int is an exact fraction
  runde(32/3, 2) == 10.67       school rounding (half up)
  nah(a, b) / nah(a, b, 0.01)   equal within a tolerance (default 1e-6)
  wert('-x**2+4*x', 2)          value of a term          integral('-x**2+4*x', 0, 4)   definite integral (Simpson)
  ableitung('x**3', 2)          derivative at a point    nullstelle('x**2-2', 1, 2)    zero in [a, b] (bisection)
  sqrt exp ln log10 sin cos tan (radians) grad(x) bogen(x) pi e abs min max sum
  ggt kgv fak binko(n, k) mittel(list) median(list)
  binom(n, p, k) = P(X = k)     binomsum(n, p, k) = P(X <= k)     normal(x, mu, sigma) = P(X <= x)
  skalar(u, v) betrag(v) kreuz(u, v)   with vectors written [1, 2, 3]
Decimal point, not comma. In HTML write < as &lt;.
"""
import ast
import math
import operator
import re
import statistics
import sys
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

EXACT = (int, Fraction)


def div(a, b):
    return Fraction(a, b) if isinstance(a, EXACT) and isinstance(b, EXACT) else a / b


def power(a, b):
    if abs(b) > 200 or abs(a) > 1e9:
        raise ValueError("power too large")
    return a ** b


def runde(x, n=0):
    d = Decimal(x.numerator) / Decimal(x.denominator) if isinstance(x, Fraction) else Decimal(repr(x))
    r = d.quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP)
    return int(r) if n <= 0 else float(r)


def nah(a, b, tol=1e-6):
    return abs(float(a) - float(b)) <= tol


def term(text):
    """Compile a term in one variable into a function of that variable."""
    tree = ast.parse(text, mode="eval")
    free = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id not in NAMES})
    if len(free) > 1:
        raise ValueError(f"term has more than one variable: {free}")
    return lambda x: ev(tree, {**NAMES, **({free[0]: x} if free else {})})


def wert(text, x):
    return term(text)(x)


def integral(text, a, b, n=2000):
    f, h = term(text), (float(b) - float(a)) / n
    s = f(float(a)) + f(float(b)) + sum((4 if k % 2 else 2) * f(float(a) + k * h) for k in range(1, n))
    return s * h / 3


def ableitung(text, x, h=1e-5):
    f = term(text)
    return (f(float(x) + h) - f(float(x) - h)) / (2 * h)


def nullstelle(text, a, b):
    f, a, b = term(text), float(a), float(b)
    if f(a) * f(b) > 0:
        raise ValueError("no sign change in the interval")
    for _ in range(100):
        m = (a + b) / 2
        a, b = (a, m) if f(a) * f(m) <= 0 else (m, b)
    return (a + b) / 2


def binom(n, p, k):
    return math.comb(n, k) * float(p) ** k * (1 - float(p)) ** (n - k)


def binomsum(n, p, k):
    return sum(binom(n, p, i) for i in range(0, k + 1))


def normal(x, mu=0, sigma=1):
    return 0.5 * (1 + math.erf((float(x) - float(mu)) / (float(sigma) * math.sqrt(2))))


def skalar(u, v):
    return sum(a * b for a, b in zip(u, v))


def kreuz(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


NAMES = {
    "runde": runde, "nah": nah, "wert": wert, "integral": integral, "ableitung": ableitung, "nullstelle": nullstelle,
    "sqrt": math.sqrt, "exp": math.exp, "ln": math.log, "log10": math.log10, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "grad": math.degrees, "bogen": math.radians, "pi": math.pi, "e": math.e,
    "abs": abs, "min": min, "max": max, "sum": sum, "ggt": math.gcd, "kgv": math.lcm, "fak": math.factorial,
    "binko": math.comb, "mittel": statistics.mean, "median": statistics.median,
    "binom": binom, "binomsum": binomsum, "normal": normal,
    "skalar": skalar, "betrag": lambda v: math.sqrt(skalar(v, v)), "kreuz": kreuz,
}
BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: div,
       ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: power}
CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
       ast.Gt: operator.gt, ast.GtE: operator.ge}


def ev(node, names):
    """Evaluate an expression tree; anything outside the whitelist raises."""
    if isinstance(node, ast.Expression):
        return ev(node.body, names)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float, str, bool):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [ev(x, names) for x in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
        v = ev(node.operand, names)
        return not v if isinstance(node.op, ast.Not) else (-v if isinstance(node.op, ast.USub) else v)
    if isinstance(node, ast.BinOp) and type(node.op) in BIN:
        return BIN[type(node.op)](ev(node.left, names), ev(node.right, names))
    if isinstance(node, ast.BoolOp):
        vals = [ev(v, names) for v in node.values]
        return all(vals) if isinstance(node.op, ast.And) else any(vals)
    if isinstance(node, ast.Compare) and all(type(o) in CMP for o in node.ops):
        left = ev(node.left, names)
        for op, right in zip(node.ops, node.comparators):
            right = ev(right, names)
            if not CMP[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names and not node.keywords:
        return names[node.func.id](*[ev(a, names) for a in node.args])
    raise ValueError(f"not allowed in a check: {ast.dump(node)[:50]}")


class Tasks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []   # attributes of every element with data-aufgabe
        self.total = None
        self.rows = []    # (attributes of <tr>, row header text, [text of each <td>])
        self.row = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-aufgabe" in a:
            self.found.append(a)
        if "data-gesamt" in a:
            self.total = num(a["data-gesamt"])
        if tag == "tr":
            self.row = (a, [])
        elif tag in ("td", "th") and self.row:
            self.row[1].append([tag, ""])

    def handle_data(self, data):
        if self.row and self.row[1]:
            self.row[1][-1][1] += data

    def handle_endtag(self, tag):
        if tag == "tr" and self.row:
            a, cells = self.row
            self.rows.append((a, "".join(x for k, x in cells if k == "th").strip(), [x for k, x in cells if k == "td"]))
            self.row = None


def num(text):
    return float(text.replace(",", "."))


def percent(cells):
    for c in cells:
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", c)
        if m:
            return num(m.group(1))


def check_answers(p, name, solution):
    """Evaluate data-check; return (lines to print, failed, missing)."""
    out, bad, missing = [], 0, 0
    if name.endswith("erklaerung.html") and not p.found:
        return [f"?    {name}: no data-aufgabe / data-check on the example and the practice tasks"], 0, 1
    for a in p.found:
        task, checks = a["data-aufgabe"], a.get("data-check")
        if checks is None:
            if solution:
                out.append(f"?    {name}  {task}: no data-check (numeric answer not recomputed; use \"-\" if there is none)")
                missing += 1
            continue
        exprs = [x.strip() for x in checks.split(";") if x.strip() and x.strip() != "-"]
        wrong = []
        for x in exprs:
            try:
                if ev(ast.parse(x, mode="eval"), NAMES) is not True:
                    wrong.append(f"false: {x}")
            except Exception as err:  # a broken check must fail the run, whatever broke
                wrong.append(f"error: {x} ({err})")
        out.append(f"{'FAIL' if wrong else 'OK  '} {name}  {task}: {len(exprs)} check(s)")
        out += [f"     - {w}" for w in wrong]
        bad += len(wrong)
    return out, bad, missing


def check_points(p, name, scheme):
    """Sub-points, AFB shares and grade key of a file with data-gesamt; return (lines to print, failed, missing)."""
    out, missing = [], 0
    parts = [a for a in p.found if "data-punkte" in a]
    if p.total is None or not parts:
        return out, 0, 0
    for a in parts:
        pt, sub = num(a["data-punkte"]), a.get("data-teilpunkte")
        if sub is None:
            if scheme and pt >= 2:
                out.append(f"?    {name}  {a['data-aufgabe']}: no data-teilpunkte (sub-points not added up)")
                missing += 1
        elif abs(sum(num(x) for x in sub.split("+")) - pt) > 1e-9:
            out.append(f"FAIL {name}  {a['data-aufgabe']}: sub-points {sub} do not add up to {pt:g}")
    rows16 = sum("data-ab" in a for a, _, _ in p.rows) == 16
    for a, th, cells in p.rows:
        pc = percent(cells)
        if pc is None:
            continue
        if th in ("I", "II", "III"):
            want = 100 * sum(num(x["data-punkte"]) for x in parts if x.get("data-afb") == th) / p.total
            if abs(pc - want) > 0.05:
                out.append(f"FAIL {name}  AFB {th}: {pc:g} % is printed, the tasks give {want:g} %")
        elif "data-ab" in a:
            ab, want = num(a["data-ab"]), pc * p.total / 100
            if not (abs(ab - want) < 1e-9 if rows16 else -1e-9 <= ab - want < 1):
                out.append(f"FAIL {name}  grade key row {a.get('data-note', '?')}: data-ab {ab:g}, but {pc:g} % of {p.total:g} = {want:g}")
    return out, sum(x.startswith("FAIL") for x in out), missing


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
    root = Path(sys.argv[1])
    files = sorted(root.rglob("*.html")) if root.is_dir() else [root]
    if not files:
        sys.exit(f"no .html files in or below {root}")
    bad = missing = 0
    parts = {}
    for f in files:
        name = f.relative_to(root).as_posix() if root.is_dir() else f.name
        p = Tasks()
        p.feed(f.read_text(encoding="utf-8"))
        parts[f] = {a["data-aufgabe"]: (num(a["data-punkte"]), a.get("data-afb")) for a in p.found if "data-punkte" in a}
        for out, b, m in (check_answers(p, name, f.name.startswith(("loesung", "erwartungshorizont", "erklaerung"))),
                          check_points(p, name, f.name.startswith("erwartungshorizont"))):
            if out:
                print("\n".join(out))
            bad, missing = bad + b, missing + m
    for f in files:
        other = f.with_name("erwartungshorizont.html")
        if f.name == "test.html" and other in parts:
            for task in sorted(set(parts[f]) | set(parts[other])):
                if parts[f].get(task) != parts[other].get(task):
                    print(f"FAIL {f.parent.name}  {task}: test {parts[f].get(task)}, erwartungshorizont {parts[other].get(task)} (points, AFB)")
                    bad += 1
    print(f"{len(files)} file(s), {bad} failed check(s), {missing} task(s) without check")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
