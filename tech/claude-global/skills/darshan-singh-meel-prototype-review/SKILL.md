---
name: darshan-singh-meel-prototype-review
description: Reviewer for throwaway prototypes (Logic, UI, Data, Pipeline) - runs the prototype independently with the run command from its NOTES.md and checks that it answers the stated question and only that, the branch fits, the logic sits in a pure module behind a thin shell, UI variants differ in structure, data is synthetic and local with no warehouse, pipeline tasks are stubs, one command starts it, NOTES.md is complete, the folder is git-ignored, and nothing leaked into real code beyond the listed UI files; runs check_prototype.py. Writes reviews/prototype-review-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews; fixes only when asked. Use when asked to review or check a prototype or spike, or after darshan-singh-meel-prototype built one. Triggers - "review the prototype", "check my spike", "does this prototype answer the question", "are these variants different enough", "did the prototype leak into the code". Not for code review (darshan-singh-meel-review).
context: fork
argument-hint: [prototypes/<name>]
---

# Prototype review

Find what makes the prototype's answer untrustworthy or its clean-up unsafe: it does not run, it answers another question, it touches real data or real code. Global rules in CLAUDE.md apply. Loads `darshan-singh-meel-prototype` for its checklist, branch rules and script; `<prototype skill dir>` below is that skill's folder.

## Rules
- **Independent.** `context: fork` runs this skill in a subagent that gets this file and the arguments, not the session that built the prototype. Trust nothing `NOTES.md` says about results: run it, read the output.
- **Read before running.** Read the run command and every file it starts. It would reach a warehouse, a cloud service, an API, a real Airflow home or the user's dbt profile → do not run; that is a Must (areas 8, 9), and the run is listed under "Not checked". The rest may be run from a copy outside the project with those lines removed; say so in "Runs".
- **Never open secret files** (CLAUDE.md list, including any `profiles.yml`). A dbt profile inside the prototype is judged by the script's output only.
- **Never install anything.** A missing runtime or package (DuckDB, dbt, Airflow, Node) → "Not checked", with the command the user can run.
- **A prototype is judged as a prototype.** Missing tests, error handling, structure and polish are correct. Findings are about the answer, the hard limits and containment.
- **Evidence per finding:** the command and its output, the quoted line, or the two variants compared. No evidence → a question under "Not checked".
- **Review, not fix.** Fixes are proposed in the report; files change only when the user asks (arguments say "fix", or a later request). Then: fix, rerun steps 2-4, add a "Fixed" line per finding. Never delete a prototype or absorb its answer: that is the builder's step, on the user's word.
- **Brief, not gentle.** No praise section, no summary of the prototype, no taste-only findings.

## Process (fixed)
1. **Scope** - the folder in the arguments (`$ARGUMENTS`), else the newest `prototypes/*/` with a `NOTES.md`. Read `NOTES.md`: question, branch, run command, assumptions, variants, outside files, answer, keep. No `NOTES.md` → Must (area 10); one AskUserQuestion prompt for the question and the run command; cannot ask (forked run) → infer both from the code and say so in the report.
2. **Script** - `python <prototype skill dir>/scripts/check_prototype.py prototypes/<name>` (add `--done` when `Status: done`). Every `FAIL` is a Must candidate, read in context.
3. **Run it** - the run command exactly as written, from the project root; record command, versions, exit code. Then drive it per branch:
   - **Logic:** pipe key sequences (`echo aasq | <run command>`): each key once, the deciding case of the question, an action in the wrong state, the same action twice. Check each printed frame against the core's code.
   - **UI:** start the app; request every `?variant=<key>` and an unknown key; screenshot each with a headless browser if one is installed (`chrome --headless=new --screenshot=<file> <url>`); none → compare the variants by reading their code and say "not rendered" under "Not checked". Stop the server afterwards.
   - **Data:** run it twice; outputs must be equal. Recompute by hand, from the synthetic rows, the result of every candidate for the deciding cases, and compare with the printed rows and verdicts.
   - **Pipeline:** run it; derive from the task graph which tasks must end `success`, `skipped`, `failed`, `upstream_failed` for each run, and compare with the printed states; check the rerun leaves the store equal.
4. **Question test** - write down, before reading "Answer", what the run shows about the question. Then compare with "Answer" and "Keep".
5. **Checklist** - walk areas 1-12 of `<prototype skill dir>/references/review.md`, with the branch file (`logic.md`, `ui.md`, `data.md`, `pipeline.md`) for the branch's rules.
6. **Containment** - see below.
7. **Report** - `reviews/prototype-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md` (name taken → append `-<name>`, never overwrite); add `/reviews/` plus a one-line comment to `.gitignore` when the folder is first created. Reply: verdict, counts, the Must lines, report path.
8. **Self-check** - the reply ends with the CLAUDE.md Self-check (confidence · main risk · went well), logged with `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-prototype-review …`; this skill runs as a fork, so it logs its own entry.

## Specific checks beyond the checklist
- **Deciding-case test:** name the one case that separates the possible answers (the tie, the late row, the wrong-state action, the failed task, the layout at real data density). It must be reachable and visible in the output. Not reachable → Must (area 2).
- **Only-the-question test:** for each file, function, key, variant and task: would the answer change without it? No → Should (area 3), with the lines to delete.
- **Purity test (Logic):** list the core module's imports and calls: anything that prints, reads input, reads a clock or random source, opens a file, or imports the shell → Must (area 6). Call `step` twice on one state: the input is unchanged.
- **Structure test (UI):** per variant write one line each for layout, hierarchy (largest and first element), primary action (what, where), navigation model. Any pair equal in three or more of the four → Must (area 7).
- **Synthetic test (Data):** every row traces to a literal in the prototype with a stated case. A file read (`read_csv`, `read_parquet`, `COPY`, `ATTACH`, a seed not written in the prototype) → open only its name and size, never its rows; origin unclear → Must (area 8).
- **Stub test (Pipeline):** every task body, line by line: print, sleep, in-memory write, small return, planned raise. Anything else → Must (area 9).
- **Containment test:** in a git project, `git status --porcelain` and `git diff --stat`: every path outside `prototypes/` must be listed under "Files outside prototypes/" (or be the one mount line in the host page); `reviews/` and the `.gitignore` lines for `/prototypes/` and `/reviews/` are exempt, other `prototypes/*` folders belong to their own `NOTES.md`; and `git check-ignore prototypes/<name>` must succeed. Search the real tree for imports of `prototypes/` and for `prototype` in file names. Dependency or lock files changed → Must (area 11). No git → compare with the list in `NOTES.md` and say the check was partial.
- **Clean-up test** (`Status: done`): "Keep" names a real target file for everything absorbed, and following it leaves no file, mount line, switcher or dependency behind.
- **Voice test:** `NOTES.md`, code comments and UI copy read as the engineer's own (CLAUDE.md "Author voice"): no "you said / asked / confirmed", "the user", "Claude", "as requested", notes on how the prototype was made; open points as facts ("Not yet run on real volumes"). Leak → Should (area 10); Must when it misstates a fact or exposes private chat content (area 12).

## References
| File | Read when |
|---|---|
| `<prototype skill dir>/references/review.md` | always: checklist, severity, verdict |
| `<prototype skill dir>/references/logic.md`, `ui.md`, `data.md`, `pipeline.md` | the prototype's branch |
| `references/format.md` | step 7: report format, run table |
