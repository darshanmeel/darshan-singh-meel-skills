---
name: darshan-singh-meel-diagrams-review
description: Strict reviewer for diagrams made with darshan-singh-meel-diagrams and its family skills, standalone or embedded in pages, docs v1 and v3, tech summaries, reviews, briefs and blogs. Re-derives the picture from the source first, then checks the right type for the question, notation per type (UML sequence and state, C4 levels not mixed, crow's foot, BPMN-lite, acyclic DAGs, dbt layer order, Airflow state legend, Gantt dates and dependencies, quadrant axes), every box and arrow traceable with nothing invented, real names, 7 plus or minus 2 per level, key and Notice; runs the layout checker plus its own checks (0 LAYOUT, Mermaid parity, contrast, title and desc, unique ids on a page, no secrets), renders light and dark PNGs and looks at each. Writes reviews/diagrams-review-<YYYY-MM-DD-HHMM>.md with verdict and Must / Should / Other. Reviews; fixes only when asked. Triggers - "review this diagram", "check the diagrams in this doc", "is this lineage right", "diagram review", "review my C4 / sequence / ER diagram".
argument-hint: [spec JSON, page, Markdown file or folder]
---

# Diagrams review

Find what makes a diagram wrong, misleading or unreadable: a box or arrow the source does not have, the wrong type for the question, notation that says something else than meant, a layout defect, a picture that fails in dark mode or for a screen reader. CLAUDE.md applies. Loads `darshan-singh-meel-diagrams` (`<base>` below) and the family skill of every type under review for their references and scripts; never copies them.

## Setup - one prompt (skip what the arguments already say)
| Header | Question | Options (rec first) |
|---|---|---|
| Scope | What to review? | Diagrams in changed files vs main (Recommended) · A page, spec or folder I name · The diagrams made in this session |
| Source | Check facts against? | The repo code and configs (Recommended) · A document I name · Layout and notation only |
| Mermaid | Do the diagrams also go to Markdown or Confluence? | Yes, check Mermaid parity (Recommended) · No, HTML only |

## Process (fixed)
1. **Inventory by script:** find the specs (`*.json` with `id` and `type`) and the pages that embed diagrams. Run `python scripts/review_diagrams.py <specs> <pages> --png <scratch>/review` - it rebuilds each spec with the engine (so `check.py` runs: every `LAYOUT` line is a Must), checks DAGs, dbt layer order, Gantt dates, placeholders, secrets, machine paths, legend, palette contrast, Mermaid parity, and on pages duplicate ids, `<title>`/`<desc>`, external resources, Notice text. Paste the counts into the report. A diagram on a page with no spec → Must "no spec: layout unproven".
2. **Re-derive first, then compare:** before reading the diagram, write from the source the question it should answer, the type you would pick (`<base>/SKILL.md` "Pick the type") and the boxes and arrows you expect, each with `path:line` (imports, calls, `ref()`/`source()`, `>>` and `upstream`, Terraform resources, manifest via the data family's `scripts/dbt_manifest.py`). Then diff: invented, missing, misnamed, wrong direction. Differences are findings.
3. **Check every area** of `references/checklist.md` (type, facts, notation per type, density, title/key/Notice, look, accessibility, embedding, Mermaid). Notation facts come from the family's references; anything not there → official page in `references/sources.md`, else "unverified - check: <page>".
4. **Look:** Read every PNG, light and dark. Read each label; follow each arrow end to end; confirm the Notice is visible in the picture. Findings from looking cite the PNG and the element.
5. **Write** `reviews/diagrams-review-<YYYY-MM-DD-HHMM>.md` from `references/templates/review-skeleton.md` (example: `references/examples/review-orders-page.md`); add `/reviews/` to `.gitignore` on first creation.
6. **Reply:** verdict + Must count + report path; then CLAUDE.md endings.

## Severity
- **Must:** a box, arrow, state or cardinality the source does not have, or a missing one the Notice depends on; wrong type for the question; notation that changes meaning (sync drawn async, C4 levels mixed, wrong crow's foot end, cycle in a DAG, edge against dbt layer order, Gantt bar before its dependency ends); any script `MUST` line (LAYOUT, duplicate id, no title/desc, secret, machine path, placeholder name, Mermaid missing a node, legend off while colour carries meaning); text unreadable in light or dark.
- **Should:** more than 7 ± 2 on one level; arrows merged into one trunk so a reader cannot tell which source feeds which target; key missing a used colour or line style; weak Notice (restates the title); a fact neither in the family references nor marked `check:`.
- **Other:** wording, label length, order of boxes.

## Rules
- **Independent:** trust no count, name or claim in the diagram; re-derive from the source or mark "Not checked".
- **Style choice is the author's:** plain, dbt or airflow look is a finding only when it misleads (a dbt look on a graph with loops, airflow states on something that never runs).
- **Never open secret files** or data rows (CLAUDE.md list). A secret in a label → path + rule, value `<redacted>`.
- **Review, not fix.** Fixes go in the report as spec changes; files change only when asked, then add a "Fixed" line per finding and rerun step 1 and step 4.
- **Brief, not gentle:** no praise section, no summary of the diagrams, no taste-only findings.
- PNGs stay in the scratch folder; report and replies use relative paths only; output stays local.
