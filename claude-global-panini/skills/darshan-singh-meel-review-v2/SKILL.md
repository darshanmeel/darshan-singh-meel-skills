---
name: darshan-singh-meel-review-v2
description: Version 2 of darshan-singh-meel-review — same checks, plus a fixed process and a fixed HTML report built from a JSON spec - main review (verdict, Must/Should one-liners, optional impact diagram), then a detailed section per file with a Must or Should finding (with a diagram only where it explains the issue), then one line for the other files. Use only when the user says "review v2", "detailed review v2", "per-file review v2" or names darshan-singh-meel-review-v2; otherwise use darshan-singh-meel-review.
---

# Review v2
Checks · severity · discipline · data stack → **`darshan-singh-meel-review`** §1–11; load, follow. This = process + report; replaces review's Output format + HTML report → v2 report only. CLAUDE.md applies.
`<skill>` = this folder. Fields · ERROR/WARN → `references/spec.md`.
Optional: docs-v2 (diagrams, layout check), knowledge graph (impact). Missing → from code; no git · tests · linters → notes, never failures.

## Process
1. Setup = review step 0. Recs: unused files → large Yes · change No (still flag code the change made unused). Graph (large): built at HEAD / no source change since → Use as is; else Update first. `.knowledge-graph` may point outside repo → use it. No answer → as is, say so in `scope.reviewed`.
2. Goal: PR · commit · ask. Whole repo → what it's for.
3. Review = review steps 2–4; no graph → code search. Secret files: path only, never opened.
   - No tests/linters → `["tests", "none in repo"]`. Deps missing → scratch venv if minutes; else `not run (deps missing)`. Same npm/tsc.
   - Must + cheap probe → run, delete after; input → result in `evidence`.
   - Graph `possible_issue` notes → one `checks` row (`5 checked: 3 Should, 2 Minor, 0 dismissed`).
4. Triage per file:
   - Must/Should → section: `what` + findings (`lines`, problem, why, fix, `code`?).
   - Minor/none → `checked`; Minor → `other` ≤10. Trivial → never a section. `checked` = code · config · tests · docs; no lockfiles · LICENSE · generated.
   - Same problem, many files → one finding (worst file), others in `also` (`path:lines`), one severity.
5. Diagram only if it beats words: per file ≤1 (before/after · fan-out · path to sink · race); `impact` only ≥3 affected (graph or code search). Never repeats text; straight chain = sentence → write it. Unnumbered; `numbered: true` only for real step order. Lane ≤12 chars.
6. Spec → `reviews/_spec/review-v2-<YYYY-MM-DD-HHMM>.json` (from `references/examples/review-v2-example.json`).
7. Build, repo root: `mkdir -p reviews/_spec` (first, git repo: git-ignore `/reviews/`) →
   `python <skill>/references/templates/build.py reviews/_spec/review-v2-<ts>.json reviews/review-v2-<ts>.html`. 0 ERROR, 0 WARN.
8. Diagram/table → `python <docs-v2 skill>/references/templates/check.py reviews/review-v2-<ts>.html reviews/_spec/shots` → 0 `LAYOUT`; open `page.png` + each `map-<n>.png`. No `check.py` → reply "layout not checked".
9. Reply = build's terminal block + graph line if stale.

## Report (built, never by hand)
1. Main: verdict · reviewed · goal · checks · counts · Must · Should (`[Area] path:lines — problem · fix`, linked) · Questions · impact · Unused (if asked) · net size.
2. Files: Must first, then path; links to own Minors.
3. Checked: one line (+ Minor count); >10 → by folder.
4. Other, numbered.

## Writing
- problem ≤25 · why ≤20 · evidence ≤25 · main line ≤25 words. One fact per line.
- Smallest complete fix (test config, callers, imports). Snippet ≤12 lines, changed lines, pastes as is.
- Summary fix = `fix`, same words.
- Secrets: never the value. Key + `path:line`, value `<redacted>`.
- Perf: grows with one user's data → Should; all rows/users/tenants → Must.
- Unsure → Questions. No praise, no code summary.
- Verdict: Must → Request changes · Should → Approve with changes · none → Approve.
