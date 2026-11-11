"""Check numbers and units in teaching-material HTML (physics, science, technology).

Usage: python check_einheiten.py <file-or-folder>
Every "?" line is a suspicion: fix it, or state why it is right. Exit code 1 when any line is printed.
Checks: decimal sign per language · number glued to unit · non-SI unit spellings · powers without <sup> ·
numbers that differ between a German line and its English line (.bi pair).
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SILENT = {"script", "style", "title"}
UNITS = r"(?:mm|cm|dm|km|m|ms|s|min|h|mg|kg|g|t|mN|kN|N|mJ|kJ|MJ|J|mW|kW|MW|W|mV|kV|V|mA|A|kHz|MHz|Hz|hPa|Pa|K|kWh|eV|nm|Ω|°C)"
GLUED = re.compile(r"(?<![\w.,^_])\d+(?:[.,]\d+)?" + UNITS + r"(?![\w^_])")
BAD_UNIT = re.compile(r"\d\s?(sec|sek|Sek|Std|std|qm|ccm|Kg|KG|gr|kmh|Km|KM|hz|HZ|KW|Kw|KWh|kwh|Kwh|mtr|ltr)\b\.?|°K\b")
NO_SUP = re.compile(r"\b(?:m|cm|mm|km|dm|s)[23]\b|\bs-[12]\b")
NUM = re.compile(r"\d+(?:[.,]\d+)?")
DE_POINT = re.compile(r"(?<![\w.,/])(?<!Nr\. )(?<!§ )(?<!§)(?<!Abs\. )(?<!Anlage )\d+\.\d+(?![\w.]*\.\d)(?!\w)")  # not numbering in legal citations
EN_COMMA = re.compile(r"(?<![\w.,])(?:0|\d+),\d+(?![\w,])")
THOUSANDS = re.compile(r"^[1-9]\d{0,2},\d{3}$")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # [tag, is_en, silent]
        self.pairs = []      # open .bi pairs: [depth, de_text, en_text, line]
        self.done = []       # closed pairs
        self.runs = []       # [is_en, line, text] per text block

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("sup", "sub"):
            self.text("^" if tag == "sup" else "_")
        if tag in VOID:
            return
        cls = (a.get("class") or "").split()
        up = self.stack[-1] if self.stack else [None, False, False]
        self.stack.append([tag, up[1] or a.get("lang") == "en" or "en" in cls, up[2] or tag in SILENT])
        if "bi" in cls:
            self.pairs.append([len(self.stack), "", "", self.getpos()[0]])

    def handle_endtag(self, tag):
        if tag in VOID or not self.stack:
            return
        if self.pairs and self.pairs[-1][0] == len(self.stack):
            self.done.append(self.pairs.pop())
        self.stack.pop()

    def handle_data(self, data):
        self.text(data)

    def text(self, data):
        if not self.stack or self.stack[-1][2]:
            return
        en = self.stack[-1][1]
        if self.runs and self.runs[-1][0] == en and self.runs[-1][1] == self.getpos()[0]:
            self.runs[-1][2] += data
        else:
            self.runs.append([en, self.getpos()[0], data])
        if self.pairs:
            self.pairs[-1][2 if en else 1] += data


def numbers(text):
    text = re.sub(r"[\^_]\S*", " ", text)          # exponents and indices are not compared
    return sorted(round(float(n.replace(",", ".")), 9) for n in NUM.findall(text))


def check(path):
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    out = []
    for en, line, text in p.runs:
        t = " ".join(text.split())
        for m in GLUED.finditer(t):
            out.append(f"line {line}: no space between number and unit: \"{m.group(0)}\"")
        for m in BAD_UNIT.finditer(t):
            out.append(f"line {line}: unit spelling: \"{m.group(0)}\"")
        for m in NO_SUP.finditer(t):
            out.append(f"line {line}: power without <sup>: \"{m.group(0).strip()}\"")
        if en:
            for m in EN_COMMA.finditer(t):
                if not THOUSANDS.match(m.group(0)):
                    out.append(f"line {line}: decimal comma in an English line: \"{m.group(0)}\"")
        else:
            for m in DE_POINT.finditer(t):
                out.append(f"line {line}: decimal point in a German line: \"{m.group(0)}\"")
    for _, de, en, line in p.done:
        if numbers(de) != numbers(en):
            out.append(f"line {line}: numbers differ: DE \"{' '.join(de.split())[:50]}\" / EN \"{' '.join(en.split())[:50]}\"")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(sys.argv[1])
    files = sorted(root.glob("*.html")) if root.is_dir() else [root]
    total = 0
    for f in files:
        found = check(f)
        total += len(found)
        print(f"{'?   ' if found else 'OK  '}{f.name}")
        for line in found:
            print(f"     ? {line}")
    print(f"{len(files)} file(s), {total} line(s) to check")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
