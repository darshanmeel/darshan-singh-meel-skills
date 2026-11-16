"""Tests for check_brevity.py. Usage: python tests/run.py (prints PASS/FAIL per test, exit 1 on any)."""
import sys

sys.dont_write_bytecode = True
import subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
import check_brevity as cb  # noqa: E402

FAILS = []
GOOD = "# Review: pipeline safe to merge\n\nThe change is correct and adds one test.\n\n## Should\n- rename `dt`.\n"


def test(fn):
    try:
        fn()
        print("PASS", fn.__name__)
    except AssertionError as ex:
        FAILS.append(fn.__name__)
        print("FAIL", fn.__name__, "|", ex)
    return fn


def issues(text, is_html=False):
    return [i for i, _ in cb.check_text(text, is_html)]


@test
def clean_text_has_no_issues():
    assert issues(GOOD) == [], cb.check_text(GOOD)


@test
def lede_missing_when_heading_follows_title():
    assert "missing lede" in issues("# Title\n\n## Details\n\nSome text.\n")


@test
def lede_missing_when_list_follows_title():
    assert "missing lede" in issues("# Title\n\n- one\n- two\n")


@test
def lede_missing_when_opening_is_boilerplate_en():
    assert "missing lede" in issues("# Guide\n\nThis document describes the loader.\n")


@test
def lede_missing_when_opening_is_boilerplate_de():
    assert "missing lede" in issues("# Anleitung\n\nIm Folgenden wird der Ablauf erklärt.\n")


@test
def lede_missing_when_nothing_after_title():
    assert "missing lede" in issues("# Only a title\n")


@test
def frontmatter_and_code_are_ignored():
    text = "---\nname: x\n---\n# T\n\nThe loader retries twice.\n\n```\nbasically in order to\n```\n"
    assert issues(text) == [], cb.check_text(text)


@test
def filler_en_and_de():
    found = cb.check_text(GOOD + "\nIt is important to note that we basically retry, basically.\n\nGrundsätzlich gilt das.\n")
    fill = [m for i, m in found if i == "filler"]
    # one line per block, each phrase named once
    assert len(fill) == 2, fill
    assert fill[0].startswith('"it is important to note", "basically" in:'), fill
    assert fill[1].startswith('"grundsätzlich" in:'), fill


@test
def filler_needs_word_boundary():
    assert "filler" not in issues(GOOD + "\nThe basicallyness word is odd.\n")


@test
def quoted_filler_is_a_mention():
    assert "filler" not in issues(GOOD + '\nAvoid "basically" and `in order to`.\n')


@test
def history_lede_before_verdict_flagged():
    text = "# Review: loader\n\nThe loader was written in 2019 and we looked at its retry path.\n\nVerdict: request changes, retries never stop.\n"
    assert "buried point" in issues(text), cb.check_text(text)
    de = "# Bericht\n\nDas Skript wurde 2021 geschrieben.\n\nErgebnis: Der Import verliert Zeilen.\n"
    assert "buried point" in issues(de), cb.check_text(de)


@test
def history_lede_without_later_verdict_or_with_own_not_flagged():
    plain = "# Loader\n\nThe loader was written in 2019.\n\nIt reads orders hourly.\n"
    assert "buried point" not in issues(plain), cb.check_text(plain)
    led = "# Review\n\nVerdict: request changes; the loader was written without a retry cap.\n\nThe decision rests on one test.\n"
    assert "buried point" not in issues(led), cb.check_text(led)


@test
def metadata_subtitle_before_lede_is_skipped():
    text = "# csvtrim\n\n*Python CLI · on demand · CSV → trimmed CSV*\n\nThis document describes csvtrim.\n"
    assert "missing lede" in issues(text), cb.check_text(text)
    good = "# csvtrim\n\n*Python CLI · on demand · CSV → trimmed CSV*\n\ncsvtrim drops rows with an empty key.\n"
    assert issues(good) == [], cb.check_text(good)


@test
def list_after_prose_line_is_not_a_long_paragraph():
    items = "\n".join(f"{i}. Step {i} does one thing." for i in range(1, cb.LONG_BLOCK + 3))
    assert "long paragraph" not in issues(GOOD + "\nThe steps:\n" + items + "\n")


@test
def long_paragraph_flagged():
    block = " ".join(f"Sentence number {i} says one thing." for i in range(cb.LONG_BLOCK + 1))
    assert "long paragraph" in issues(GOOD + "\n" + block + "\n")


@test
def short_paragraph_not_flagged():
    assert "long paragraph" not in issues(GOOD + "\nOne fact. Two facts.\n")


@test
def summary_repeating_lede_flagged():
    text = "# R\n\nLate orders are dropped by the incremental filter.\n\n## Summary\n\nThe incremental filter drops late orders.\n"
    assert "duplicate summary" in issues(text)


@test
def two_summary_sections_flagged():
    text = GOOD + "\n## Summary\n\nA.\n\n## Fazit\n\nB.\n"
    assert "duplicate summary" in issues(text)


@test
def distinct_summary_not_flagged():
    text = GOOD + "\n## Summary\n\nNext step: deploy Friday after the backfill.\n"
    assert "duplicate summary" not in issues(text)


@test
def html_lede_and_filler():
    page = "<html><head><style>p{}</style></head><body><h1>Doc</h1><h2>Intro</h2><p>In order to run it, start.</p></body></html>"
    found = issues(page, is_html=True)
    assert "missing lede" in found and "filler" in found, found


@test
def html_good_page():
    page = "<body><h1>Loader</h1><p>The loader moves orders hourly.</p><ul><li>retries twice</li></ul></body>"
    assert issues(page, is_html=True) == [], cb.check_text(page, True)


CHROME_PAGES = {
    "docs": '<body><nav class="side"><div class="t">csvtrim</div><a href="#s0">1</a></nav><main><div class="eyebrow">technical</div>'
            '<h1>csvtrim</h1><p class="sub1">Python CLI</p><div class="doclede"><p class="l1">{lede}</p></div></main></body>',
    "review": '<body><main><div class="eyebrow">code review</div><h1>Review: retry</h1><p><span class="verdict rc">Request changes</span></p>'
              '<p class="lede">{lede}</p><p class="sub1">2026-11-16</p><nav class="toc"><a href="#s0">1</a></nav></main></body>',
    "brief": '<body><main><p class="eyebrow">Requirements brief</p><h1>Fleet</h1><p class="lede">{lede}</p>'
             '<p class="stamp">2026-11-12</p></main></body>',
    "plain-nav": "<body><nav>Menu</nav><h1>T</h1><p>{lede}</p></body>",
}


@test
def html_builder_pages_find_the_real_lede():
    for name, page in CHROME_PAGES.items():
        bad = page.replace("{lede}", "This document describes the csvtrim tool.")
        assert "missing lede" in issues(bad, True), (name, cb.check_text(bad, True))
        good = page.replace("{lede}", "<code>csvtrim</code> drops rows with an empty key.")
        assert issues(good, True) == [], (name, cb.check_text(good, True))


@test
def html_builder_page_without_lede_flagged():
    page = CHROME_PAGES["docs"].replace('<div class="doclede"><p class="l1">{lede}</p></div>', 
        '<div class="tabs"><div class="bar"><label for="t1">Does</label></div><ul><li>a</li></ul></div>')
    assert "missing lede" in issues(page, True), cb.check_text(page, True)


@test
def html_inline_code_text_kept():
    md = cb.html_to_md("<h1>T</h1><p><code>csvtrim</code> trims cells.</p><pre>basically</pre>")
    assert "csvtrim trims" in md and "basically" not in md, md


@test
def cli_output_and_exit_codes():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "a.md"
        f.write_text("# T\n\nThis document describes X.\n", encoding="utf-8")
        script = str(SKILL / "scripts" / "check_brevity.py")
        run = lambda *a: subprocess.run([sys.executable, "-B", script, *a], capture_output=True, text=True, encoding="utf-8")
        r = run(d)
        assert r.returncode == 0 and "BREVITY " in r.stdout and "| missing lede |" in r.stdout, r.stdout
        assert run(d, "--strict").returncode == 1
        f.write_text(GOOD, encoding="utf-8")
        assert run(d, "--strict").returncode == 0


@test
def examples_after_parts_are_clean():
    # the "After" blocks of the examples must pass the checker
    for ex in sorted((SKILL / "references" / "examples").glob("*.md")):
        text = ex.read_text(encoding="utf-8")
        after = text.split("## After", 1)[-1] if "## After" in text else text.split("## Nachher", 1)[-1]
        body = after.split("```markdown", 1)[1].split("\n```\n", 1)[0]
        assert cb.check_text(body) == [], (ex.name, cb.check_text(body))


print(f"{len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
