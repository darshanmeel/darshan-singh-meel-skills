---
name: darshan-singh-meel-review-v2
description: Version 2 of darshan-singh-meel-review — same checks, plus a fixed process and a fixed HTML report built from a JSON spec - main review (verdict, Must/Should one-liners, optional impact diagram), then a detailed section per file with a Must or Should finding (with a diagram only where it explains the issue), then one line for the other files. Use only when the user says "review v2", "detailed review v2", "per-file review v2" or names darshan-singh-meel-review-v2; otherwise use darshan-singh-meel-review.
---

# Review v2
Checks, severity, discipline, data stack: **`darshan-singh-meel-review` SKILL.md** (sections 1–12; 12 Tech debt is always checked) — load and follow it. This skill adds the process and the report, and replaces the review skill's Output format and HTML report: write only the v2 report. Global CLAUDE.md rules apply.
`<skill>` = this folder. Spec fields and every ERROR/WARN: `references/spec.md`.
Optional: docs-v2 (diagrams, layout check), knowledge graph (impact). Missing → review from the code; not a git repo, no tests or linters → notes, never failures.

## Process (fixed)
1. **Setup prompt** = review skill step 0, with these defaults:
   - Unused files: large review → Yes (Recommended); change review → No (Recommended) — still flag code the change itself made unused.
   - Graph (large review): built from the current commit, or no source changes since → Use as is (Recommended); else Update first; record it as in the review skill. `.knowledge-graph` may point outside the repo: use that path. No answer → use as is; `scope.reviewed` names the graph's commit (a fact, not the unanswered question).
2. **Goal:** PR description, commit message, or ask. Whole repo → what the repo is for.
3. **Review** = review skill steps 2–4: diff + callers/readers via the graph (none → code search), tests, every section. Secret files: path only, never opened.
   - No tests or linters → `["tests", "none in repo"]`. Full suite: deps missing → install into a scratch venv if it takes minutes; otherwise `["full suite", "not run (deps missing)"]`. Same for npm/tsc.
   - Confirm a Must with a throwaway probe when cheap (scratchpad or a temp test, deleted after); put input → result in `evidence`.
   - Graph `possible_issue` notes: one `checks` row, e.g. `["graph notes", "5 checked: 3 Should, 2 Minor, 0 dismissed"]`.
4. **Triage per file:**
   - ≥1 Must or Should → file section: one-line `what`, findings (`lines`, problem, why, fix, short `code` when it helps).
   - Only Minor or nothing → `checked`; Minor → `other` (≤10).
   - Obvious or trivial files never get a section. `checked` = code, config, tests and docs reviewed; leave out lockfiles, LICENSE, generated files.
   - Tech debt: `area: "Tech debt"`, `why` = cost of keeping it, optional `effort` S · M · L; severity per review §12.
   - Same problem in several files → one finding in the worst file, the others in `also` (`path:lines`), one severity.
5. **Diagrams, only when they beat words:** per file ≤1 (before/after flow, join fan-out, call path to a vulnerable sink, race timeline); `impact` in Main only with ≥3 affected callers/readers/downstream (graph or code search). Never a diagram that repeats the text; a straight chain is a sentence: write it. Unnumbered by default; `numbered: true` only for a real step order (never a race or a comparison). Lane names ≤12 characters.
6. **Spec** → `reviews/_spec/review-v2-<YYYY-MM-DD-HHMM>.json` (start from `references/examples/review-v2-example.json`).
7. **Build** from the repo root: `mkdir -p reviews/_spec` (first time, in a git repo: git-ignore `/reviews/` per CLAUDE.md), then
   `python <skill>/references/templates/build.py reviews/_spec/review-v2-<ts>.json reviews/review-v2-<ts>.html`. Fix every ERROR and WARN.
8. **Layout** (any diagram or table): `python <docs-v2 skill>/references/templates/check.py reviews/review-v2-<ts>.html reviews/_spec/shots` → 0 `LAYOUT`; open `page.png` and each `map-<n>.png`. No docs-v2 `check.py` → say "layout not checked" in the reply.
9. **Reply** = the build's terminal block (verdict, Must/Should one-liners, report path), plus the graph update question or the staleness note if the graph is out of date (knowledge-graph "Keep it updated").

## Report (built, never hand-written)
1. **Main review:** verdict · reviewed · goal · checks run · counts · tech debt (count, biggest) · Must fix · Should fix (each `[Area] path:lines — problem · fix`, linked to its detail) · Questions · impact diagram · Unused files (if asked) · net size.
2. **Files:** one section per file with Must/Should, Must first, then path; links to its Minor items in Other.
3. **Checked, no main findings:** one line of paths (+ Minor count); >10 → grouped by folder.
4. **Other findings** (if any), numbered.

## Writing
- Minimum words: problem ≤25, why ≤20, evidence ≤25, main line ≤25. One fact per line.
- Smallest complete fix: include what it breaks otherwise (test config, callers, imports). Snippet ≤12 lines, only the changed lines, pastes as is.
- Summary's fix = the `fix` field, same words.
- Secrets: never the value. Name the key, cite `path:line`, value as `<redacted>`.
- Performance: cost grows with one user's data → Should; with all rows, users or tenants → Must.
- Unsure → Questions, not findings. No praise, no summary of the code. Fields may address the reader; never quote the chat.
- Verdict: any Must → Request changes · Should only → Approve with changes · none → Approve.
