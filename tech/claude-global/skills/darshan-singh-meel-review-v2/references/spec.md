# Review spec — input to build.py
`<skill>` = this skill's folder. Run from the repo root:
`python <skill>/references/templates/build.py reviews/_spec/review-v2-<YYYY-MM-DD-HHMM>.json reviews/review-v2-<YYYY-MM-DD-HHMM>.html`
- Optional: `darshan-singh-meel-docs-v2` beside this skill (diagram renderer, style, layout check). Missing or incompatible → `note:`, built-in style, each diagram as a text list, `Layout not checked` in the terminal block.
- Prints the terminal reply (verdict, Must/Should one-liners, report path), then `built <out>: N files, N findings, N WARN`.
- Layout (docs-v2 only): `python <docs-v2>/references/templates/check.py <out.html> <shots_dir>` → 0 `LAYOUT` lines.
- Start from `examples/review-v2-example.json`. Builder tests: `python <skill>/tests/run.py`.

## Fields
```json
{"title": "Review: <change>", "date": "YYYY-MM-DD HH:MM",
 "verdict": "Approve | Approve with changes | Request changes",
 "scope": {"reviewed": "diff main...branch: 5 files, +142 -18", "goal": "what the change should do"},
 "checks": [["tests (changed)", "6 passed"], ["full suite", "not run (why)"]],
 "files": [{"path": "src/a.py", "what": "one line: what changed / what it does",
            "findings": [{"sev": "Must", "area": "Security", "lines": "31-34",
                          "summary": "problem · fix", "problem": "…", "why": "…", "fix": "…", "effort": "S | M | L (Tech debt, optional)",
                          "code": "short fix snippet (optional)", "evidence": "probe input → result (optional)",
                          "also": ["src/c.py:8-9"],
                          "diagram": {flow}}]}],
 "checked": ["src/b.py"],
 "questions": ["…"],
 "impact": {flow},
 "unused": [["path", "why it looks unused", "evidence", "High | Medium | Check", "suggestion"]],
 "net_size": "could drop ~20 of 142 added lines",
 "other": [{"area": "Tests", "path": "tests/t.py", "lines": "8", "what": "…", "why": "…", "impact": "…"}]}
```
| Field | Rule |
|---|---|
| `files` | only files with ≥1 Must or Should finding; the build sorts them (Must first, then path) and numbers findings |
| `sev` | `Must` · `Should` (review skill, Severity). Minor/nit → `other` |
| `area` | Correctness · Security · Performance · Design · Complexity · Size · Slop · Tests · Obvious · Data · Tech debt |
| `effort` | optional, `S` · `M` · `L`: fix effort, shown for Tech debt (findings and `other`); `why` = cost of keeping it |
| `lines` | `N` or `N-M`, inside the file; required except for secret files |
| `summary` | the Main list line: `problem · fix`; whole line `[Area] path:lines — summary` ≤ 25 words; its fix uses the words of `fix` |
| `problem` ≤ 25 · `why` ≤ 20 · `what` ≤ 20 · `evidence` ≤ 25 words | `what`: what changed (diff) or what the file does (whole repo) |
| `evidence` | optional: probe or repro, input → observed result |
| `also` | optional: same problem in other files, `path` or `path:lines`; shown as `(+N files)` in Main and listed in the finding |
| secrets | never a value in any field: key name + `path:line`, value `<redacted>` |
| `code` | optional, ≤ 12 lines, only the fix |
| `diagram` | optional, ≤ 1 per file, only when it shows what words can't: before/after flow, join fan-out, call path to a vulnerable sink, race timeline; never a straight chain |
| `checked` | other reviewed code, config, tests and docs (no lockfiles, LICENSE, generated files); one line, > 10 grouped by folder; Minor count added from `other` |
| `impact` | optional: what the change touches (callers, readers, downstream) from the graph, or code search without one; ≥ 3 affected boxes. Diff → changed box(es) `tag: "changed"`; whole repo → the box the top Must's fix changes, `tag: "fix"` |
| `unused` | only if the user asked (section 11); `[]` → "None found"; rows `[path, why, evidence, High · Medium · Check, suggestion]` |
| `net_size` | diff: lines that could go of those added; whole repo: lines that could go |
| `other` | ≤ 10, CLAUDE.md format: what · why · impact; `lines` optional; numbered, linked from the file's section |

Main lists, counts, links, finding numbers and the `Tech debt: N items, biggest: …` line (highest severity, then effort; none → `none found`) are generated from `files`, so they always match.

## Diagrams
docs-v2 flow blocks (docs-v2 `spec.md` → Flow nodes, Edges, Groups, Layout): `nodes [{id, label, col, row, kind?, tag?, sub?}]`, `edges [{from, to, label?, dashed?, fail?}]`, `lanes?` (≤ 12 characters each), `numbered?`, `key?`, `notice?`, plus a required `title` (no "Diagram" prefix). Ids A, B… are added by the build in page order. Unnumbered unless `numbered: true` (only for a real step order; never a race or a comparison).

## Checks
**ERROR** (no output): path not in the repo, absolute, with `\` or `..` · lines malformed or past the file end · missing `lines` · secret file cited with lines or a snippet (path only; never opened) · `sev`, `area`, `verdict`, `unused` confidence, `effort` outside the fixed sets · Must/Should without `summary`, `problem`, `why` or `fix` · file section without findings · file both in `files` and `checked` · `other` > 10 · scope without `reviewed`/`goal` · diagram without title · impact without a `changed` or `fix` box · `also` path or lines invalid, or the finding's own file · likely secret literal in any string (`key: value`, `key = "value"`, `scheme://user:pw@`; not `<redacted>`/`${VAR}`) · absolute or machine path in any string (drive, `~/`, `/Users/`) · verdict: any Must → `Request changes`; Should and no Must → not `Approve` · diagram layout the docs-v2 renderer cannot draw · missing output folder.
**WARN**: word budgets · summary without `·` · summary fix sharing no word with `fix` · lane name > 12 characters · snippet > 12 lines · diagram < 3 boxes, no arrows, or only words already in the finding (duplicates the text) · diagram a straight chain (no lanes, no decision, ≤ 1 arrow in and out per box) · two findings in different files with near-identical summary (→ one finding + `also`) · `other` on a file in neither `files`, `checked` nor `also` · `checked` path twice · `effort` on a non-Tech-debt item · `/home/`, `/root/`, `/tmp/`, `/var/` not after an HTTP verb · > 1 diagram per file · impact < 3 affected boxes · `Request changes` without Must · no findings and verdict not `Approve` · empty `checks` (no tests or linters → `["tests", "none in repo"]`).
**note** (never a failure): no repo files under the cwd (example built in an empty folder) → path and line checks skipped · report not git-ignored · docs-v2 missing or incompatible. Not a git repo → stamp `repo not in git`, no ignore check.
