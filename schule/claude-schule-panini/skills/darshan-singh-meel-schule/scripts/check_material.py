"""Check teaching-material HTML: well-formed, self-contained, accessible basics, bilingual pairs, sums that add up,
printed points equal to the data-* values (.punkte labels, total, AFB table, grade key).

Usage: python check_material.py <file-or-folder> [--template]
--template: placeholders {{...}} are allowed (for references/templates/).
Errors fail the run (exit code 1). Warnings (German text without an English line) are listed and do not fail it.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
URL_ATTRS = {"src", "href", "xlink:href", "action", "poster", "data", "srcset"}
REMOTE = re.compile(r"^\s*(https?:)?//", re.I)
SCRIPT_NET = re.compile(r"https?://|\b(fetch|XMLHttpRequest|importScripts|WebSocket|EventSource)\b|\bimport\s*\(")
CSS_NET = re.compile(r"@import|url\(\s*['\"]?(?!data:|#)", re.I)
MACHINE_PATH = re.compile(r"[A-Za-z]:\\\\?[A-Za-z]|/Users/|/home/|file://")
NO_EN_NEEDED = {"script", "style", "title", "svg", "button", "label", "select", "option", "noscript"}
TEXT_TAGS = {"p", "li", "td", "th", "h2", "h3", "figcaption", "dd", "dt", "blockquote"}
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]{3,}")
NUMBER = r"\d+(?:[.,]\d+)?"
POINTS = re.compile(rf"({NUMBER})\s*(?:P\b|Punkte|BE\b)|({NUMBER})")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.warnings, self.tags = [], [], [], []
        self.raw = {"script": [], "style": [], "title": []}
        self.svgs = []   # [line, labelled]
        self.skip = []   # per open element: True = no English line expected here (already paired, English, German-only, UI)
        self.own = []    # per open element: its own direct text
        self.hasen = []  # per open element: has a direct child with class "en" (inline label pair)
        self.bis = []    # open .bi pairs: {depth, line, kids: [[is_en, text], ...]}
        self.pairs = 0
        self.tasks = []  # open elements with data-punkte: (depth, attrs)
        self.caps = []   # printed numbers to compare with a data-* value: [depth, wanted, what, text]
        self.row = None  # open <tr>: {a: attrs, cells: [[tag, text], ...]}
        self.afb_printed = {}

    def err(self, msg):
        self.errors.append(f"line {self.getpos()[0]}: {msg}")

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.seen(tag, a)
        if tag in VOID:
            return
        cls = (a.get("class") or "").split()
        if self.bis and len(self.stack) == self.bis[-1]["depth"]:
            self.bis[-1]["kids"].append(["en" in cls and a.get("lang") == "en", ""])
        if "en" in cls and self.hasen:
            self.hasen[-1] = True
        if "bi" in cls:
            self.bis.append({"depth": len(self.stack) + 1, "line": self.getpos()[0], "kids": []})
        parent = self.skip[-1] if self.skip else False
        self.skip.append(parent or tag in NO_EN_NEEDED or bool({"bi", "en", "kein-druck"} & set(cls))
                         or "data-nur-de" in a or a.get("lang") == "en")
        self.own.append("")
        self.hasen.append(False)
        self.stack.append(tag)
        depth = len(self.stack)
        if "data-punkte" in a:
            self.tasks.append((depth, a))
        if "punkte" in cls and self.tasks:
            t = self.tasks[-1][1]
            self.caps.append([depth, t["data-punkte"], f"task {t.get('data-aufgabe', '?')}: printed points", ""])
        if "data-gesamt" in a:
            self.caps.append([depth, a["data-gesamt"], "printed total", ""])
        if tag == "tr":
            self.row = {"a": a, "cells": []}
        elif tag in ("td", "th") and self.row:
            self.row["cells"].append([tag, ""])

    def printed(self, text, wanted, what):
        m = POINTS.search(text)
        if m and num(m.group(1) or m.group(2)) != num(wanted):
            self.err(f"{what}: {m.group(1) or m.group(2)} is printed, the data attribute says {wanted}")

    def end_row(self):
        a = self.row["a"]
        tds = [t.strip() for k, t in self.row["cells"] if k == "td"]
        ths = [t.strip() for k, t in self.row["cells"] if k == "th"]
        self.row = None
        if not tds:
            return
        if "data-ab" in a:
            self.printed(tds[0], a["data-ab"], f"grade key row {a.get('data-note', '?')}: printed points")
        if "data-punkte" in a and re.fullmatch(NUMBER, tds[-1]):
            self.printed(tds[-1], a["data-punkte"], f"task {a.get('data-aufgabe', '?')}: printed points")
        if ths and ths[0] in ("I", "II", "III") and re.fullmatch(NUMBER, tds[0]):
            self.afb_printed[ths[0]] = num(tds[0])

    def handle_startendtag(self, tag, attrs):
        self.seen(tag, dict(attrs))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.err(f"</{tag}> does not close <{self.stack[-1] if self.stack else 'nothing'}>")
            while tag in self.stack and self.stack[-1] != tag:
                self.close_top()
            if not self.stack:
                return
        self.close_top()

    def close_top(self):
        tag, skip, own, hasen = self.stack.pop(), self.skip.pop(), self.own.pop(), self.hasen.pop()
        depth = len(self.stack) + 1
        if self.tasks and self.tasks[-1][0] == depth:
            self.tasks.pop()
        while self.caps and self.caps[-1][0] == depth:
            _, wanted, what, text = self.caps.pop()
            self.printed(text, wanted, what)
        if tag == "tr" and self.row:
            self.end_row()
        if self.bis and len(self.stack) + 1 == self.bis[-1]["depth"]:
            b = self.bis.pop()
            k = b["kids"]
            if len(k) != 2 or k[0][0] or not k[1][0] or not k[0][1].strip() or not k[1][1].strip():
                self.errors.append(f"line {b['line']}: .bi needs two children with text: German first, then class=\"en\" lang=\"en\"")
            else:
                self.pairs += 1
        words = [w for w in WORD.findall(re.sub(r"\{\{.*?\}\}", "", own)) if not w.isupper()]
        # "Stopp / stop" is already a pair; all-caps tokens are sequences or symbols, not German text
        if tag in TEXT_TAGS and not skip and not hasen and " / " not in own and len(words) >= 2:
            self.warnings.append(f"line {self.getpos()[0]}: no English line: \"{' '.join(own.split())[:60]}\"")

    def handle_data(self, data):
        if not self.stack:
            return
        if self.stack[-1] in self.raw:
            self.raw[self.stack[-1]].append(data)
        self.own[-1] += data
        for c in self.caps:
            c[3] += data
        if self.row and self.row["cells"]:
            self.row["cells"][-1][1] += data
        if self.bis and len(self.stack) >= self.bis[-1]["depth"] and self.bis[-1]["kids"]:
            self.bis[-1]["kids"][-1][1] += data

    def seen(self, tag, a):
        self.tags.append((tag, a))
        if tag == "svg":
            self.svgs.append([self.getpos()[0], bool(a.get("aria-label") or a.get("aria-hidden") == "true")])
        if tag == "title" and "svg" in self.stack and self.svgs:
            self.svgs[-1][1] = True
        if tag in ("iframe", "object", "embed", "link"):
            self.err(f"<{tag}> is not allowed (self-contained file)")
        if tag == "script" and "src" in a:
            self.err("<script src> is not allowed (inline scripts only)")
        if tag == "img":
            if "alt" not in a:
                self.err("<img> without alt")
            if not (a.get("src") or "").startswith("data:"):
                self.err("<img src> must be a data: URI (or use inline SVG)")
        for k, v in a.items():
            if k in URL_ATTRS and v and REMOTE.match(v):
                self.err(f"external URL in <{tag} {k}>")
            if k == "style" and v and CSS_NET.search(v):
                self.err(f"external resource in style attribute of <{tag}>")


def num(text):
    return float(text.replace(",", "."))


def check(path, template):
    text = path.read_text(encoding="utf-8")
    p = Page()
    p.feed(text)
    p.close()
    errors = list(p.errors)
    if p.stack:
        errors.append(f"unclosed tags: {', '.join(p.stack)}")
    tags = p.tags
    first = {t: a for t, a in reversed(tags)}
    ids = {a.get("id") for _, a in tags}

    if not text.lstrip().lower().startswith("<!doctype html>"):
        errors.append("missing <!doctype html>")
    lang = first.get("html", {}).get("lang")
    if not lang:
        errors.append("<html> without lang")
    if not any(t == "meta" and a.get("charset") for t, a in tags):
        errors.append("missing <meta charset>")
    if not any(t == "meta" and a.get("name") == "viewport" for t, a in tags):
        errors.append("missing <meta name=viewport>")
    if not "".join(p.raw["title"]).strip():
        errors.append("empty or missing <title>")
    if sum(t == "h1" for t, _ in tags) != 1:
        errors.append("need exactly one <h1>")
    if any(t == "table" for t, _ in tags) and not any(t == "th" for t, _ in tags):
        errors.append("table without <th>")
    for line, labelled in p.svgs:
        if not labelled:
            errors.append(f"line {line}: <svg> needs aria-label, <title> or aria-hidden=\"true\"")
    css = "".join(p.raw["style"])
    if CSS_NET.search(css):
        errors.append("external resource in <style> (@import or url())")
    if "@media print" not in css:
        errors.append("no @media print rules")
    js = "".join(p.raw["script"])
    if SCRIPT_NET.search(js):
        errors.append("script loads or names a network resource")
    if MACHINE_PATH.search(text):
        errors.append("absolute or machine-specific path in file")
    if not template and "{{" in text:
        left = sorted(set(re.findall(r"\{\{\s*([^}]+?)\s*\}\}", text)))
        errors.append(f"unfilled placeholders: {', '.join(left[:8])}{' ...' if len(left) > 8 else ''}")

    # bilingual: German line + English line, toggle
    mode = first.get("body", {}).get("data-sprache", "de-en")
    warnings = []
    if mode not in ("de-en", "de", "en"):
        errors.append("body data-sprache must be de-en, de or en")
    if mode == "en" and lang != "en":
        errors.append("data-sprache=\"en\" needs <html lang=\"en\">")
    if mode == "de-en":
        warnings = p.warnings
        if not p.pairs:
            errors.append("no bilingual .bi pairs (data-sprache=\"de-en\")")
        if "en-toggle" not in ids:
            errors.append("missing id=\"en-toggle\" (show/hide English)")
        if "ohne-en" not in css:
            errors.append("no CSS rule for html.ohne-en (English lines cannot be hidden)")

    # points, AFB, grade key
    info = {"pairs": p.pairs}
    parts = [(a.get("data-aufgabe", "?"), num(a["data-punkte"]), a.get("data-afb")) for _, a in tags if "data-punkte" in a]
    totals = [num(a["data-gesamt"]) for _, a in tags if "data-gesamt" in a]
    if parts or totals:
        if len(totals) != 1:
            errors.append(f"need exactly one data-gesamt, found {len(totals)}")
        elif abs(sum(pt for _, pt, _ in parts) - totals[0]) > 1e-9:
            errors.append(f"points add up to {sum(pt for _, pt, _ in parts):g}, data-gesamt says {totals[0]:g}")
        for name, _, afb in parts:
            if afb not in ("I", "II", "III"):
                errors.append(f"task {name}: data-afb must be I, II or III")
        total = sum(pt for _, pt, _ in parts) or 1
        info["afb"] = {k: round(100 * sum(pt for _, pt, afb in parts if afb == k) / total) for k in ("I", "II", "III")}
        info["parts"] = {name: pt for name, pt, _ in parts}
        info["total"] = totals[0] if totals else None
        for k, printed in p.afb_printed.items():
            want = sum(pt for _, pt, afb in parts if afb == k)
            if printed != want:
                errors.append(f"AFB table: row {k} prints {printed:g} points, the tasks add up to {want:g}")
    key = [num(a["data-ab"]) for _, a in tags if "data-ab" in a]
    if key:
        if any(x <= y for x, y in zip(key, key[1:])) or key[-1] != 0:
            errors.append("grade key: data-ab must fall strictly and end at 0")
        if totals and key[0] > totals[0]:
            errors.append("grade key: best grade needs more points than the total")
    # lesson plan minutes
    plan = [num(a["data-dauer"]) for _, a in tags if "data-dauer" in a]
    mins = [num(a["data-min"]) for _, a in tags if "data-min" in a]
    if plan and sum(mins) != plan[0]:
        errors.append(f"phases add up to {sum(mins):g} min, data-dauer says {plan[0]:g}")
    info["tasks"] = sorted(a["data-aufgabe"] for _, a in tags if "data-aufgabe" in a)

    if path.name.startswith("animation"):
        for need in ("buehne", "btn-play", "btn-back", "btn-next", "tempo", "cap-de", "cap-en", "bilder"):
            if need not in ids:
                errors.append(f"animation: missing id=\"{need}\"")
        if "prefers-reduced-motion" not in js + css:
            errors.append("animation: no prefers-reduced-motion fallback")
        if "STEPS" not in js:
            errors.append("animation: no STEPS list")
        steps = re.findall(r"\{\s*de:\s*'((?:[^'\\]|\\.)*)',\s*en:\s*'((?:[^'\\]|\\.)*)'", js)
        if mode == "de-en" and (not steps or any(not de.strip() or not en.strip() for de, en in steps)):
            errors.append("animation: every STEPS entry needs a de and an en caption")
    return errors, warnings, info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    template = "--template" in sys.argv
    sys.stdout.reconfigure(encoding="utf-8")  # cp1252 consoles cannot print the arrows and umlauts in the report
    if not args:
        sys.exit(__doc__)
    root = Path(args[0])
    files = sorted(root.glob("*.html")) if root.is_dir() else [root]
    if not files:
        sys.exit(f"no .html files in {root}")
    bad, warned, infos = 0, 0, {}
    for f in files:
        errors, warnings, info = check(f, template)
        infos[f.name] = info
        afb = info.get("afb")
        note = f"  {info['pairs']} DE/EN pairs"
        if afb and info.get("total") is not None:
            note += f", {info['total']:g} P, AFB I/II/III = {afb['I']}/{afb['II']}/{afb['III']} %"
        print(f"{'FAIL' if errors else 'OK  '} {f.name}{note}")
        for e in errors:
            print(f"     - {e}")
        for w in warnings:
            print(f"     ? {w}")
        bad += len(errors)
        warned += len(warnings)
    # pairs must describe the same tasks
    for a, b, what in (("test", "erwartungshorizont", "parts"), ("arbeitsblatt", "loesung", "tasks")):
        for suffix in (".html", ".en.html"):
            x, y = infos.get(a + suffix), infos.get(b + suffix)
            if x and y and x.get(what) != y.get(what):
                print(f"FAIL {a}{suffix} and {b}{suffix}: tasks or points differ")
                bad += 1
    print(f"{len(files)} file(s), {bad} error(s), {warned} warning(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
