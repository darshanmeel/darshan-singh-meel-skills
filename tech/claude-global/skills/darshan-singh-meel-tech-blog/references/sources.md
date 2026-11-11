# Sources and verification status

Official pages only. Status: **read** = the fact was read on the page (November 2026) · **own** = this skill's working default, no official source · **check** = not read; verify on the page named.

## Pages used
| Rule in this skill | Page | Status |
|---|---|---|
| Active voice; second person ("you" rather than "we"); sentence case for titles and headings; code font for code-related text; descriptive link text; numbered lists for sequences; do not pre-announce features | Google developer documentation style guide, Highlights - `https://developers.google.com/style/highlights` | read |
| Wrap code at 80 characters; omitted code marked with a comment, not `...`; introduce a code sample with a sentence | Google developer documentation style guide, Code samples - `https://developers.google.com/style/code-samples` | read |
| Titles: descriptive and concise, no repeated keywords, distinct per page; no length limit, long titles are shortened in results | Google Search Central, Influencing title links - `https://developers.google.com/search/docs/appearance/title-link` | read |
| Descriptions: unique, descriptive, no keyword lists; no length limit, snippets are truncated as needed | Google Search Central, Snippets and meta descriptions - `https://developers.google.com/search/docs/appearance/snippet` | read |
| Mermaid in Markdown: fenced block with the `mermaid` identifier renders on GitHub | GitHub Docs, Creating diagrams - `https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams` | read |
| Flowchart keyword, directions, shapes, link text, subgraph, traps (`end`, ids starting with `o`/`x`), quoting, `%%` comments | Mermaid docs, Flowcharts - `https://mermaid.js.org/syntax/flowchart.html` | read |
| Sequence diagram keyword, participants, arrows, `loop`/`alt`/`opt`, notes, the `end` trap | Mermaid docs, Sequence diagrams - `https://mermaid.js.org/syntax/sequenceDiagram.html` | read |
| Skill layout: `SKILL.md` front matter (`name`, `description`, `model` = model while the skill is active, same values as `/model`), `description` + `when_to_use` together cut at 1,536 characters in the skill listing, `context: fork` = the skill runs in a subagent that gets the skill content as its prompt and not the conversation history, `$ARGUMENTS` and `argument-hint`, supporting files loaded on demand, scripts executed not loaded | Claude Code docs, Skills - `https://code.claude.com/docs/en/skills` | read |
| Worked example (`examples/`): UPSERT since SQLite 3.24.0 (2018-06-04), `excluded.` qualifier, uniqueness constraints only, `WHERE` in `DO UPDATE`, PostgreSQL syntax origin, not standard SQL | SQLite docs, UPSERT - `https://sqlite.org/lang_upsert.html` | read |
| Worked example: `REPLACE` deletes the pre-existing rows that cause the violation, then inserts | SQLite docs, The ON CONFLICT clause - `https://sqlite.org/lang_conflict.html` | read |
| Worked example: connection as context manager commits or rolls back and does not close; named placeholders need a dict; `executemany`; `sqlite_version` | Python 3.12 docs, sqlite3 - `https://docs.python.org/3.12/library/sqlite3.html` | read |

## Own defaults (not official)
- Title 70 characters or fewer; description 70-160 characters; summary 80 words or fewer. Google states no limits; these keep titles and snippets from being cut in typical result widths - not a guarantee.
- Length bands (600-900, 1,200-1,800, 2,500-3,500 words); reading time = words / 200.
- Sentence 35 words, paragraph 120 words, one em dash per 300 words, 3-6 sections, 5-9 nodes per figure.
- The slop lists in `style.md` and `scripts/blog_post.py`.
- The front matter keys (`title`, `description`, `date`, `tags`) and the brief comment.

## Not verified
- Which keys a given site generator requires in front matter, and whether it ignores `_code/` - check: the generator's docs (Hugo, Jekyll, Astro, Docusaurus, MkDocs).
- Whether the target platform renders Mermaid (other than GitHub) - check: the platform's docs.
- Google style guide pages on tone words ("simply", "easy") and on command-line syntax were not read; the rules in `style.md` on these are own defaults.

## How to re-check
Open the page in the table, find the section named, compare with the rule. Style guides and Mermaid change between releases: re-read when a rule matters for a decision.
