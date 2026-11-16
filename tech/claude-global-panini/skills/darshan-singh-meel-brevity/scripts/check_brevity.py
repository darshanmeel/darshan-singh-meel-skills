"""Heuristic brevity advice for .md and .html files.
Usage: python scripts/check_brevity.py <file-or-folder> [...] [--strict]
Prints BREVITY <file> | <issue> | <text>; exit 0 unless --strict and something was found."""
import html
import re
import sys
from pathlib import Path

# Internal judgement threshold for "clearly long" prose blocks; not a rule for writers.
LONG_BLOCK = 7
OVERLAP = 0.6
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

BOILERPLATE = re.compile(
    r"^(this (document|doc|page|report|section|post|article|guide) (describes|explains|covers|provides|is about|gives)"
    r"|in this (document|report|section|post|article|guide)|the purpose of this|introduction\b|overview of\b"
    r"|welcome to|dieses dokument (beschreibt|erklärt)|in diesem (dokument|bericht|abschnitt|beitrag)"
    r"|im folgenden|einleitung\b|einführung\b)", re.I)

FILLER = [
    "it is important to note", "it should be noted", "it is worth noting", "needless to say", "basically",
    "in order to", "as mentioned above", "as stated above", "at the end of the day", "in today's",
    "it goes without saying", "the fact that", "for all intents and purposes", "please note that",
    "grundsätzlich", "im folgenden", "es ist wichtig zu erwähnen", "es sei darauf hingewiesen",
    "wie oben erwähnt", "an dieser stelle", "im grunde genommen", "im prinzip", "sozusagen",
]
# a quoted phrase is a mention (e.g. a list of what to avoid), not a use
FILLER_RE = re.compile(r"(?<![\w\"'`„“])(" + "|".join(re.escape(f) for f in FILLER) + r")(?![\w\"'`“”])", re.I)
SUMMARY_HEAD = re.compile(r"^#+\s*(summary|tl;?dr|conclusion|bottom line|recap|in short|zusammenfassung|fazit|kurz gesagt)\b", re.I)
# a lede made only of history or method buries the point when a later block holds it
HISTORY = re.compile(
    r"\b(was|were) (first )?(written|built|created|started|developed|designed|introduced)\b|\bstarted in (19|20)\d\d\b"
    r"|\bwe (first )?(looked at|investigated|examined|analy[sz]ed|reviewed|spent)\b|\bback in (19|20)\d\d\b"
    r"|\bwurde (\w+ ){0,2}(geschrieben|entwickelt|gebaut|erstellt)\b|\bbegann (19|20)\d\d\b"
    r"|\bwir haben (zuerst )?\w+ (untersucht|angesehen|analysiert)\b", re.I)
VERDICT = re.compile(
    r"\b(verdict|recommend\w*|the answer|result|decision|conclusion|root cause|safe to (merge|deploy)|request changes"
    r"|approve[sd]?|empfehl\w*|ergebnis|entscheidung|ursache|fazit)\b", re.I)
SENTENCE_END = re.compile(r"[.!?](?=\s+[A-ZÄÖÜ0-9\"'(`*]|\s*$)")


# page chrome around the title (eyebrow, subtitle, stamp, verdict badge, tab labels) is not the lede
CHROME = re.compile(r"(?is)<(\w+)\b[^>]*\bclass=\"[^\"]*\b(eyebrow|sub1|stamp|verdict)\b[^\"]*\"[^>]*>.*?</\1>")


def html_to_md(text):
    text = re.sub(r"(?is)<(script|style|pre|svg|head|nav|label)\b.*?</\1>", "\n\n", text)
    text = CHROME.sub("", text)
    h1 = re.search(r"(?i)<h1\b", text)
    if h1:
        text = text[h1.start():]
    text = re.sub(r"(?is)<h([1-6])[^>]*>(.*?)</h\1>", lambda m: "\n\n" + "#" * int(m[1]) + " " + m[2] + "\n\n", text)
    text = re.sub(r"(?is)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?is)<tr[^>]*>", "\n| ", text)
    text = re.sub(r"(?is)</?(p|div|section|article|ul|ol|table|blockquote|header|footer|main|br|hr)\b[^>]*>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    return html.unescape(text)


def blocks(text):
    text = re.sub(r"(?s)\A---\n.*?\n---\n", "", text)
    text = re.sub(r"(?ms)^(```|~~~).*?^\1[^\n]*$", "", text)
    out = []
    for raw in re.split(r"\n\s*\n", text):
        lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
        # a heading glued to a paragraph is its own block
        while lines and lines[0].startswith("#") and len(lines) > 1:
            out.append(lines.pop(0))
        # prose lines before a list or table form their own block
        cut = next((i for i, ln in enumerate(lines) if is_structured(ln)), len(lines))
        if lines[:cut]:
            out.append(" ".join(lines[:cut]))
        if lines[cut:]:
            out.append("\n".join(lines[cut:]))
    return out


def is_structured(line):
    return bool(re.match(r"^(#|[-*+] |\d+[.)] |\||>|<)", line))


def kind(block):
    first = block.splitlines()[0]
    if first.startswith("#"):
        return "heading"
    if re.match(r"^([-*+] |\d+[.)] )", first):
        return "list"
    if first.startswith("|"):
        return "table"
    return "prose"


def words(text):
    return set(re.findall(r"\w{4,}", text.lower()))


def overlap(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / min(len(wa), len(wb)) if wa and wb else 0.0


def sentences(block):
    return len(SENTENCE_END.findall(block))


def short(text, n=80):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 3] + "..."


def check_text(text, is_html=False):
    """Return a list of (issue, text) pairs."""
    if is_html:
        text = html_to_md(text)
    bs = blocks(text)
    found = []
    start = 1 if bs and kind(bs[0]) == "heading" else 0
    # a one-line metadata subtitle (stack · schedule · source) may sit between title and lede
    if len(bs) > start + 1 and kind(bs[start]) == kind(bs[start + 1]) == "prose" and bs[start].count("·") >= 2 \
            and not SENTENCE_END.search(bs[start]):
        start += 1
    lede = bs[start] if len(bs) > start else ""
    if not lede:
        found.append(("missing lede", "no text after the title"))
    elif kind(lede) != "prose":
        found.append(("missing lede", "title is followed by a " + kind(lede) + ": " + short(lede)))
    elif BOILERPLATE.search(lede):
        found.append(("missing lede", "opening describes the text, not the point: " + short(lede)))
    elif HISTORY.search(lede) and not VERDICT.search(lede) and any(VERDICT.search(b) for b in bs[start + 1:] if kind(b) != "heading"):
        found.append(("buried point", "opening is history or method; lead with the verdict or answer below: " + short(lede)))
    for b in bs:
        hits = list(dict.fromkeys(m[1].lower() for m in FILLER_RE.finditer(b)))
        if hits:
            found.append(("filler", ", ".join(f'"{h}"' for h in hits) + " in: " + short(b, 60)))
        if kind(b) == "prose" and sentences(b) >= LONG_BLOCK:
            found.append(("long paragraph", "split into bullets, a table or a diagram: " + short(b)))
    summaries = [i for i, b in enumerate(bs) if SUMMARY_HEAD.match(b)]
    if len(summaries) > 1:
        found.append(("duplicate summary", "several summary sections: " + ", ".join(short(bs[i], 40) for i in summaries)))
    for i in summaries:
        body = next((b for b in bs[i + 1:] if kind(b) != "heading"), "")
        if lede and body and overlap(lede, body) >= OVERLAP:
            found.append(("duplicate summary", "summary repeats the lede: " + short(body)))
    return found


def files(args):
    for a in args:
        p = Path(a)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.suffix.lower() in (".md", ".html", ".htm") and not SKIP_DIRS & set(f.parts):
                    yield f
        elif p.is_file():
            yield p


def main(argv):
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if not args:
        print(__doc__)
        return 2
    total = 0
    for f in files(args):
        text = f.read_text(encoding="utf-8", errors="ignore")
        for issue, msg in check_text(text, f.suffix.lower() in (".html", ".htm")):
            print(f"BREVITY {f.as_posix()} | {issue} | {msg}")
            total += 1
    print(f"{total} BREVITY")
    return 1 if strict and total else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
