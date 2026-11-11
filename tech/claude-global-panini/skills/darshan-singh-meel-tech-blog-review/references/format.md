# Review file format

File: `reviews/tech-blog-review-<YYYY-MM-DD-HHMM>.md`. Paths relative to the project root. Omit empty sections except "Code run" and "Claims".

```markdown
# Review: <post title>
Date: <YYYY-MM-DD HH:MM> · Skill: darshan-singh-meel-tech-blog-review · File: blog/<slug>.md
Brief: reader <...> · type <...> · words <target> (actual <n>)
Verdict: <Publish | Publish after Must fixes | Rework>
Counts: Must <n> · Should <n> · Other <n> · Script: <n> errors, <n> warnings

## Must
- **[<area>] line <n> / "<heading>"** - what: <one line, quoted words> · why: <one line> · fix: <the corrected sentence, value or step>

## Should
- ...

## Other
- ...

## Code run
| Block (line) | Command | Version | Exit | Output = post |
|---|---|---|---|---|
| 31-58 | `python load.py` | Python 3.12.10, SQLite 3.49.1 | 0 | yes |
| 72 | - | - | not run: needs a cloud account | syntax checked against <page> |

## Claims
| # | Claim (line) | Source read | Result |
|---|---|---|---|
| 1 | "UPSERT since SQLite 3.24.0" (14) | sqlite.org, UPSERT | confirmed |
| 2 | "..." (40) | none given; searched <official site> | unsourced |

## Checked without findings
<areas 1-12 that passed, one line>

## Not checked
<what could not be verified and why: figure not rendered, tool not installed, page unreachable>
```

## Rules for the tables
- **Code run:** one row per block or per assembled file. "Output = post": `yes`, `no` (→ Must, show the difference in the finding), or `no output quoted`.
- **Claims:** one row per checkable statement, including those in the title, description, figure labels and takeaways. Results: `confirmed` · `wrong` (→ Must, with what the page says) · `not supported by the link` (→ Must) · `unsourced` (→ Must for numbers and versions, Should for common knowledge of the stated reader) · `not checked` (reason under "Not checked").
- Name the page by site and title; give the URL only for official pages.
- Area tags: Code, Code quality, Claims, Thesis, Title, Structure, Clarity, Style, Length, Figures, Form, Privacy.

## After fixes (only when the user asked for them)
Append:
```markdown
## Fixed <YYYY-MM-DD HH:MM>
- Must 1 - <what changed> · rerun: <command> exit 0
- Should 2 - not changed: <reason>
Verdict after fixes: <...>
```
