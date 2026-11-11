"""Check, run, extract and build a blog post written with darshan-singh-meel-tech-blog.

Usage: python blog_post.py blog/<slug>.md [--run] [--extract DIR] [--html]
  (no flag)      check the post; FAIL lines fail the run (exit 1), ? lines need a human look
  --run          also run every .py in blog/_code/<slug>/ and compare stdout with <file>.out
                 (first run writes the .out file - read it before quoting it)
  --extract DIR  write every fenced block of the post to DIR (independent rerun by a reviewer)
  --html         also write blog/<slug>.html (self-contained; local images are inlined)
"""
import base64
import html
import re
import subprocess
import sys
from pathlib import Path

BANNED = [
    "delve", "in today's", "ever-evolving", "ever-changing", "fast-paced", "game-changer", "game changer",
    "unlock the", "unleash", "revolutioni", "seamless", "cutting-edge", "supercharge", "worth noting",
    "important to note", "needless to say", "in conclusion", "let's dive", "dive into", "without further ado",
    "look no further", "buckle up", "in this article", "in this post", "in this blog", "tapestry", "testament to",
    "the landscape of", "the world of", "the realm of", "blazing", "best-in-class", "world-class", "next-level",
    "ultimate guide", "comprehensive guide", "everything you need to know", "happy coding", "stay tuned",
    "hope this helps", "at the end of the day", "when it comes to", "to the next level", "like a pro",
]
SUSPECT = [
    "leverage", "utilize", "robust", "powerful", "simply", "easily", "easy", "just", "obviously", "of course",
    "basically", "actually", "really", "very", "quite", "elevate", "empower", "harness", "streamline", "crucial",
    "essential", "magic", "elegant", "modern", "state-of-the-art", "best practice", "in order to",
    "a number of", "it turns out", "the fact that", "we will", "we'll", "let's", "note that", "significantly",
    "dramatically", "massively", "countless", "myriad", "plethora", "journey", "whether you're",
]
PATTERNS = [
    (r"\bnot (just|only|merely)\b[^.?!]*\bbut\b", "not just X but Y"),
    (r"\b(isn't|is not|aren't) (just |only )?(about )?[^.?!]{3,40}[;,—-]+ ?(it's|it is|they're)\b", "it's not X, it's Y"),
    (r"(^|[.!?] )(The \w+|But why|So what|Why|The catch|The best part)\? ", "question-then-answer"),
    (r"\b(is|are|was|were|be|been|being|gets?|got) (\w+ed|built|written|done|made|run|sent|kept|shown|given|"
     r"taken|thrown|chosen|known|seen|set|read)\b", "passive voice"),
]
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐]")
PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|XXX|lorem ipsum)\b|\{\{.*?\}\}", re.I)
MACHINE_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)|(?<![\w/.])~/|/Users/|/home/|file://")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml"}
MERMAID = {"flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "stateDiagram-v2",
           "erDiagram", "gantt", "pie", "timeline", "gitGraph", "mindmap", "quadrantChart", "xychart-beta"}
FENCE = re.compile(r"^(```+|~~~+)\s*([\w+-]*)\s*$")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)[^)]*\)")
BRIEF = re.compile(r"<!--\s*brief:(.*?)-->", re.S)
ITEM = re.compile(r"\s*([-*]|\d+\.) ")


def parse(text):
    """-> meta, brief, prose [(line, text)], blocks [(line, lang, code, not_run)], headings [(line, level, text)]"""
    lines = text.split("\n")
    meta, start = {}, 0
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        for line in lines[1:end]:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip("\"'")
        start = end + 1
    m = BRIEF.search(text)
    brief = dict((k.strip(), v.strip()) for k, v in
                 (p.split("=", 1) for p in m.group(1).split(";") if "=" in p)) if m else {}
    prose, blocks, headings = [], [], []
    fence, not_run, comment = None, "", False
    for n, line in enumerate(lines[start:], start + 1):
        if fence:
            if line.strip() == fence[0]:
                blocks.append((fence[1], fence[2], "\n".join(fence[3]), fence[4]))
                fence = None
            else:
                fence[3].append(line)
            continue
        if comment or line.lstrip().startswith("<!--"):
            comment = "-->" not in line
            r = re.search(r"not-run:(.*?)(-->|$)", line)
            not_run = r.group(1).strip() if r else not_run
            continue
        f = FENCE.match(line)
        if f:
            fence = [f.group(1), n, f.group(2), [], not_run]
            not_run = ""
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            headings.append((n, level, line[level:].strip()))
        elif line.strip():
            prose.append((n, line))
            not_run = ""
    if fence:
        blocks.append((fence[1], "UNCLOSED", "", ""))
    return meta, brief, prose, blocks, headings


def plain(line):
    line = re.sub(r"`[^`]*`", " ", line)
    return LINK.sub(lambda m: m.group(2), line)


def check(path):
    meta, brief, prose, blocks, headings = parse(path.read_text(encoding="utf-8"))
    slug, fails, warns = path.stem, [], []
    fail, warn = fails.append, warns.append

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        fail(f"file name '{path.name}': slug must be lower-case words joined by hyphens")
    for key in ("title", "description", "date", "tags"):
        if not meta.get(key):
            fail(f"front matter: '{key}' missing")
    if meta.get("date") and not re.fullmatch(r"\d{4}-\d\d-\d\d", meta["date"]):
        fail("front matter: date must be YYYY-MM-DD")
    for key in ("reader", "goal", "thesis", "type", "words"):
        if not brief.get(key):
            fail(f"brief comment: '{key}' missing")
    title, desc = meta.get("title", ""), meta.get("description", "")
    if len(title) > 70:
        warn(f"title has {len(title)} characters (default: 70 or fewer)")
    if desc and not 70 <= len(desc) <= 160:
        warn(f"description has {len(desc)} characters (default: 70-160)")

    h1 = [h for h in headings if h[1] == 1]
    if len(h1) != 1 or h1[0][2] != title:
        fail("exactly one '# ' heading, equal to the front matter title")
    last = 1
    for n, level, htext in headings:
        if level > last + 1:
            fail(f"line {n}: heading level jumps from {last} to {level}")
        if htext[-1:] in ".:!":
            warn(f"line {n}: heading ends with '{htext[-1]}'")
        last = level
    names = [h[2].lower() for h in headings]
    for name in sorted({x for x in names if names.count(x) > 1}):
        warn(f"heading used twice: '{name}'")
    h2 = [h for h in headings if h[1] == 2]
    if not h2 or h2[-1][2].lower() != "takeaways":
        fail("last '## ' section must be 'Takeaways'")
    first_h2 = h2[0][0] if h2 else 10 ** 9
    lead = " ".join(plain(t) for n, t in prose if n < first_h2)
    if not lead:
        fail("no summary paragraph between the title and the first section")
    elif len(lead.split()) > 80:
        warn(f"summary before the first section has {len(lead.split())} words (default: 80 or fewer)")

    code_dir = path.parent / "_code" / slug
    proof = [p.read_text(encoding="utf-8", errors="replace") for p in sorted(code_dir.glob("*")) if p.is_file()]
    proof = ["\n".join(x.rstrip() for x in t.split("\n")) for t in proof]
    for n, lang, code, not_run in blocks:
        if lang == "UNCLOSED":
            fail(f"line {n}: code fence never closed")
            continue
        if not lang:
            fail(f"line {n}: code fence without a language")
        if lang == "mermaid":
            first = (code.strip().split() or [""])[0]
            if first not in MERMAID:
                fail(f"line {n}: mermaid block starts with '{first}', not a diagram type")
            continue
        body = "\n".join(x.rstrip() for x in code.split("\n")).strip("\n")
        if not not_run and not any(body in t for t in proof):
            fail(f"line {n}: {lang or 'code'} block is not in _code/{slug}/ and has no <!-- not-run: reason --> line")
        for i, cl in enumerate(code.split("\n")):
            if len(cl) > 80:
                warn(f"line {n + 1 + i}: code line has {len(cl)} characters (wrap at 80)")
            if MACHINE_PATH.search(cl):
                fail(f"line {n + 1 + i}: machine-specific path in a code block")
            if re.fullmatch(r"\s*(\.\.\.|…)\s*", cl):
                warn(f"line {n + 1 + i}: '...' for omitted code - use a comment in the sample's language")

    if brief.get("type", "").startswith("tutorial"):
        shown = {x.strip() for b in blocks for x in b[2].splitlines()}
        for p in sorted(code_dir.glob("*")):
            if p.is_file() and p.suffix != ".out":
                try:
                    lines = p.read_text(encoding="utf-8").splitlines()
                except UnicodeDecodeError:  # a file the example writes or reads (.db, image)
                    continue
                gap = [x.strip() for x in lines if x.strip() not in shown | {""}]
                if gap:
                    fail(f"tutorial: {len(gap)} lines of _code/{slug}/{p.name} are not in the post, first: {gap[0]}")

    words = 0
    for n, line in prose:
        for bang, label, target in LINK.findall(line):
            if bang and not label.strip():
                fail(f"line {n}: image without alt text")
            if not bang and label.strip().lower() in {"here", "click here", "this", "this link", "link", "this page"}:
                warn(f"line {n}: link text '{label}' says nothing - name the target")
            if target.startswith("http://"):
                warn(f"line {n}: http:// link")
            if not re.match(r"https?://|#|mailto:", target) and not (path.parent / target.split("#")[0]).exists():
                fail(f"line {n}: local target '{target}' not found")
        text_line = plain(line)
        if re.search(r"(?<![(<\w])https?://\S+", LINK.sub("", line)):
            warn(f"line {n}: bare URL - link a descriptive phrase")
        if PLACEHOLDER.search(text_line):
            fail(f"line {n}: placeholder left in the text")
        if MACHINE_PATH.search(line):
            fail(f"line {n}: machine-specific path")
        if EMOJI.search(text_line):
            fail(f"line {n}: emoji")
        if "!" in text_line.replace("![", ""):
            warn(f"line {n}: exclamation mark")
        low = text_line.lower()
        for phrase in BANNED:
            if phrase in low:
                fail(f"line {n}: slop phrase '{phrase}'")
        for phrase in SUSPECT:
            if re.search(rf"\b{re.escape(phrase)}\b", low):
                warn(f"line {n}: '{phrase}' - cut it or replace it with the fact")
        for pattern, name in PATTERNS:
            if re.search(pattern, text_line, re.I):
                warn(f"line {n}: {name}")
        if not line.lstrip().startswith("|"):
            if len(text_line.split()) > 120:
                warn(f"line {n}: paragraph has {len(text_line.split())} words (default: 120 or fewer)")
            for s in re.split(r"(?<=[.?!])\s+", text_line):
                if len(s.split()) > 35:
                    warn(f"line {n}: sentence has {len(s.split())} words (default: 35 or fewer)")
        words += len(LINK.sub(lambda m: m.group(2), line).replace("`", "").split())
    dashes = sum(t.count("—") for _, t in prose)
    if dashes > max(2, words // 300):
        warn(f"{dashes} em dashes in {words} words - use commas, colons or two sentences")
    target = [int(x) for x in re.findall(r"\d+", brief.get("words", ""))]
    if target and not min(target) * 0.9 <= words <= max(target) * 1.1:
        warn(f"{words} words, brief says {brief['words']}")

    for line in fails:
        print("FAIL", line)
    for line in warns:
        print("?   ", line)
    links = [m for _, x in prose for m in LINK.findall(x)]
    domains = sorted({re.sub(r"https?://([^/]+).*", r"\1", t) for _, _, t in links if t.startswith("http")})
    figures = sum(b[1] == "mermaid" for b in blocks) + sum(bool(m[0]) for m in links)
    print(f"{path.name}: {words} words (about {max(1, round(words / 200))} min), {len(blocks)} code blocks, "
          f"{figures} figures, links to: {', '.join(domains) or 'none'}")
    print(f"{len(fails)} errors, {len(warns)} warnings")
    return len(fails)


def run(path):
    code_dir, bad = path.parent / "_code" / path.stem, 0
    scripts = sorted(code_dir.glob("*.py"))
    if not scripts:
        print(f"?    no .py files in _code/{path.stem}/ - run other languages by hand, save stdout as <file>.out")
    for script in scripts:
        r = subprocess.run([sys.executable, script.name], cwd=code_dir, capture_output=True, text=True, timeout=300)
        out, saved = r.stdout.replace("\r\n", "\n"), script.with_suffix(".out")
        if r.returncode:
            bad += 1
            print(f"FAIL {script.name}: exit {r.returncode}\n{r.stderr.strip()}")
        elif not saved.exists():
            saved.write_text(out, encoding="utf-8", newline="\n")
            print(f"?    {script.name}: ran; wrote {saved.name} - read it before quoting it")
        elif saved.read_text(encoding="utf-8") != out:
            bad += 1
            print(f"FAIL {script.name}: stdout differs from {saved.name}\n{out.strip()}")
        else:
            print(f"ok   {script.name}: exit 0, stdout = {saved.name}")
    return bad


def extract(path, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = {"python": "py", "bash": "sh", "sh": "sh", "powershell": "ps1", "javascript": "js", "typescript": "ts",
           "yaml": "yml", "text": "txt", "console": "txt", "mermaid": "mmd"}
    for i, (n, lang, code, not_run) in enumerate(parse(path.read_text(encoding="utf-8"))[3], 1):
        name = f"block-{i:02d}-line-{n}.{ext.get(lang, lang or 'txt')}"
        (out_dir / name).write_text(code + "\n", encoding="utf-8", newline="\n")
        print(name, f"(not-run: {not_run})" if not_run else "")


def inline(text):
    codes = []
    text = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\0{len(codes) - 1}\0", text)
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\0(\d+)\0", lambda m: f"<code>{html.escape(codes[int(m.group(1))])}</code>", text)


def to_html(path):
    text = path.read_text(encoding="utf-8")
    meta = parse(text)[0]
    lines = text.split("\n")
    if lines[0].strip() == "---":
        lines = lines[lines.index("---", 1) + 1:]
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    while i < len(lines):
        line = lines[i]
        f = FENCE.match(line)
        image = re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+\.svg)\)", line.strip())
        if f:
            flush()
            j = next((k for k in range(i + 1, len(lines)) if lines[k].strip() == f.group(1)), len(lines))
            if f.group(2) == "mermaid":
                print("?    mermaid block is shown as source in the HTML - draw it as .svg for HTML output")
            code = html.escape("\n".join(lines[i + 1:j]))
            out.append(f'<pre><code class="language-{f.group(2)}">{code}</code></pre>')
            i = j
        elif line.lstrip().startswith("<!--"):
            flush()
            while "-->" not in lines[i]:
                i += 1
        elif line.startswith("#"):
            flush()
            level = len(line) - len(line.lstrip("#"))
            if level > 1:  # the template prints the title
                out.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
        elif ITEM.match(line):
            flush()
            tag, items = ("ol" if re.match(r"\s*\d", line) else "ul"), []
            while i < len(lines) and (ITEM.match(lines[i]) or (lines[i].startswith("  ") and lines[i].strip())):
                if ITEM.match(lines[i]):
                    items.append(ITEM.sub("", lines[i], count=1))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        elif line.startswith("|") and i + 1 < len(lines) and re.match(r"\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            rows = "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells(line)) + "</tr>"
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(lines[i])) + "</tr>"
                i += 1
            out.append(f"<table>{rows}</table>")
            continue
        elif line.startswith(">"):
            flush()
            out.append(f"<blockquote><p>{inline(line.lstrip('> '))}</p></blockquote>")
        elif image:
            flush()
            svg = re.sub(r"<\?xml.*?\?>", "", (path.parent / image.group(2)).read_text(encoding="utf-8")).strip()
            out.append(f'<figure role="img" aria-label="{html.escape(image.group(1))}">{svg}</figure>')
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    page = (Path(__file__).parent.parent / "references" / "templates" / "post.html").read_text(encoding="utf-8")
    for key in ("title", "description", "date", "tags"):
        page = page.replace("{{" + key + "}}", html.escape(meta.get(key, "").strip("[]")))

    def embed(m):  # raster images, and .svg inside a paragraph
        src = path.parent / m.group(1)
        if re.match(r"https?://|data:", m.group(1)) or src.suffix.lower() not in MIME:
            print(f"?    image '{m.group(1)}' is not inlined - the HTML is not self-contained")
            return m.group(0)
        data = base64.b64encode(src.read_bytes()).decode("ascii")
        return f'<img src="data:{MIME[src.suffix.lower()]};base64,{data}"'

    body = re.sub(r'<img src="([^"]+)"', embed, "\n".join(out))
    target = path.with_suffix(".html")
    target.write_text(page.replace("{{body}}", body), encoding="utf-8", newline="\n")
    print(f"wrote {target.name}")


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    path, bad = Path(args[0]), 0
    if "--extract" in args:
        extract(path, Path(args[args.index("--extract") + 1]))
        return
    if "--run" in args:
        bad += run(path)
    bad += check(path)
    if "--html" in args and not bad:
        to_html(path)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
