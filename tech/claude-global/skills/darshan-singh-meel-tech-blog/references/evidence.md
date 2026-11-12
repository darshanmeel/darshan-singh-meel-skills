# Evidence: code that ran, claims with a source

## Code
1. Write each example as a real file in `blog/_code/<slug>/` (`load.py`, `schema.sql`, `main.tf`). Smallest example that shows the point; synthetic data; no secrets, no account ids, no internal names.
2. Run it.
   - Python: `python <skill dir>/scripts/blog_post.py blog/<slug>.md --run` runs every `.py` in the folder and saves stdout as `<file>.out` on the first run; later runs fail when stdout changes. Code changed on purpose: delete `<file>.out`, rerun, read the new output, update every block that quotes it.
   - Other languages: run by hand in the folder, save stdout as `<file>.out` (`node app.js > app.out`).
   - Examples must be repeatable: fixed seeds, in-memory or temp storage, no dependence on the clock or the network. Output that varies (timings, ids) is not quoted verbatim - describe it with the measured range.
3. Read the output. It must show what the paragraph claims. If it does not, change the paragraph or the thesis.
4. Quote into the post: contiguous lines, copied from the file, indentation unchanged. Output: copied from `<file>.out`. The script fails any block it cannot find in the folder.
5. Record what ran: language and library versions in the post's "what you need" list, taken from the run (`python --version`), not from memory.

| Situation | What to do |
|---|---|
| Cannot run (needs a cloud account, a paid service, a cluster, hardware) | `<!-- not-run: <reason> -->` before the fence; say in the prose that it was not run; take syntax from the official reference and link it |
| Needs a tool that is not installed | ask before installing; otherwise not-run with the reason |
| Would change real systems or query real data | never run; CLAUDE.md rules on querying data apply; not-run |
| Shell command with machine-specific output | quote the command; trim the output to the lines that matter, with a comment line for what was cut |
| Pseudocode or a deliberately wrong example | label it in the prose and mark `not-run: pseudocode` / `not-run: shows the bug` - better: make the bug runnable and quote its real error |
| Config snippets (YAML, JSON, HCL) | validate with the tool (`terraform validate`, a JSON/YAML parse) and keep the file in `_code/<slug>/`; else not-run |

- Fence language on every block; `text` for output. Wrap code at 80 characters. Omitted code: a comment in the sample's language, never `...`.
- Introduce each block with a sentence that says what it does; after it, say what to notice in the output. Never "as you can see".
- Do not print prompts (`$`, `>>>`) in blocks the reader will copy.
- Pin versions in install commands when the behaviour shown depends on them.

## Claims
A claim is anything the reader could check: version numbers, release dates, defaults, limits, syntax, "X does Y", "X is faster/cheaper/safer", history, quotes.

1. List the claims of the outline before drafting: claim · official page · version it holds for.
2. Read the page now. Memory is a lead, not a source. Note the version or date the page states.
3. Link the claim where it is made, with descriptive link text (the page or section name), to the most specific official page.
4. State the version the claim holds for when behaviour changed over time ("since SQLite 3.24.0").

| Kind of claim | Accepted source |
|---|---|
| Syntax, defaults, limits, behaviour | the product's own reference docs for the version used |
| Release dates, what changed | official release notes or changelog |
| Language or protocol rules | the standard or spec (PEPs, RFCs, ISO SQL as quoted by vendor docs) |
| Pricing, quotas | the vendor's pricing or limits page, with the date read - these change |
| Performance, cost, "faster" | your own measurement in `_code/<slug>/` with setup, or the vendor's published benchmark named as theirs |
| Research results | the paper itself |
| Experience ("in our pipeline this cut reruns") | written as experience, first person, with the conditions - not as a general fact |

- Not accepted as a source for facts: other blogs, Q&A sites, forum posts, AI answers, memory. They can be credited for an idea, not cited for a fact.
- Official page silent or unreachable → cut the claim, or keep it marked in the reply as `check: <page>` and stated in the post as the author's open point ("not tested on 3.45 yet").
- Docs and observed behaviour disagree → say so, show the run, name the version.
- Superlatives and absolutes ("always", "never", "the fastest", "the only") need the same proof as numbers; usually cut.

## Measurements
- Report: machine or instance type, OS, versions, data size and shape, warm or cold, number of runs, the statistic (median of n), the command.
- Compare like with like: same data, same machine, each side configured as its docs recommend.
- Give the number and the ratio ("41 s → 6 s, median of 5 runs"), never "much faster".
- One measurement on one machine is an observation; word it that way.

## Privacy in examples
- Invented names, `example.com` domains, documentation IP ranges, fake ids.
- Nothing copied from a real project's code, schema, logs or tickets unless the user owns it and asked for it; then strip names and values.
