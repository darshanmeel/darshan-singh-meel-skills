---
name: darshan-singh-meel-prototype-review
description: Reviewer for throwaway prototypes (Logic, UI, Data, Pipeline) - runs the prototype independently with the run command from its NOTES.md and checks that it answers the stated question and only that, the branch fits, the logic sits in a pure module behind a thin shell, UI variants differ in structure, data is synthetic and local with no warehouse, pipeline tasks are stubs, one command starts it, NOTES.md is complete, the folder is git-ignored, and nothing leaked into real code beyond the listed UI files; runs check_prototype.py. Writes reviews/prototype-review-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews; fixes only when asked. Use when asked to review or check a prototype or spike, or after darshan-singh-meel-prototype built one. Triggers - "review the prototype", "check my spike", "does this prototype answer the question", "are these variants different enough", "did the prototype leak into the code". Not for code review (darshan-singh-meel-review).
context: fork
argument-hint: [prototypes/<name>]
---

# Prototype review
Find what makes the answer untrustworthy or clean-up unsafe: does not run · answers another question · touches real data or real code. CLAUDE.md applies. Loads `darshan-singh-meel-prototype` for checklist · branch rules · script; `<prototype skill dir>` = that skill's folder.

## Rules
- **Independent:** `context: fork` → subagent gets this file + arguments, not the building session. Trust nothing `NOTES.md` says about results: run it, read output.
- **Read before running:** read run command + every file it starts. Would reach warehouse · cloud service · API · real Airflow home · user's dbt profile → do not run; Must (areas 8, 9); run listed under "Not checked". Rest may run from a copy outside the project with those lines removed; say so in "Runs".
- **Never open secret files** (CLAUDE.md list, incl. any `profiles.yml`). dbt profile inside prototype → judged by script output only.
- **Never install:** missing runtime/package (DuckDB · dbt · Airflow · Node) → "Not checked" + command the user can run.
- **Judged as a prototype:** missing tests · error handling · structure · polish = correct. Findings = the answer · hard limits · containment.
- **Evidence per finding:** command + output · quoted line · the two variants compared. No evidence → question under "Not checked".
- **Review, not fix:** fixes proposed in report; files change only when user asks (arguments say "fix", or later request) → fix → rerun steps 2-4 → "Fixed" line per finding. Never delete a prototype or absorb its answer: builder's step, on user's word.
- **Brief, not gentle:** no praise section · no summary of the prototype · no taste-only findings.

## Process (fixed)
1. **Scope** - folder in arguments (`$ARGUMENTS`), else newest `prototypes/*/` with a `NOTES.md`. Read `NOTES.md`: question · branch · run command · assumptions · variants · outside files · answer · keep. None → Must (area 10); one AskUserQuestion for question + run command; cannot ask (forked run) → infer both from code, say so in report.
2. **Script** - `python <prototype skill dir>/scripts/check_prototype.py prototypes/<name>` (+ `--done` when `Status: done`). Every `FAIL` = Must candidate, read in context.
3. **Run** - run command exactly as written, from project root; record command · versions · exit code. Then drive per branch:
   - **Logic:** pipe key sequences (`echo aasq | <run command>`): each key once · deciding case of the question · action in wrong state · same action twice. Check each printed frame vs core's code.
   - **UI:** start app → request every `?variant=<key>` + an unknown key → screenshot each with headless browser if installed (`chrome --headless=new --screenshot=<file> <url>`); none → compare variants by reading code, "not rendered" under "Not checked". Stop server afterwards.
   - **Data:** run twice → outputs equal. Recompute by hand, from synthetic rows, result of every candidate for the deciding cases → compare with printed rows + verdicts.
   - **Pipeline:** run → derive from task graph which tasks must end `success` · `skipped` · `failed` · `upstream_failed` per run → compare with printed states; rerun leaves store equal.
4. **Question test** - before reading "Answer", write down what the run shows about the question → compare with "Answer" + "Keep".
5. **Checklist** - areas 1-12 of `<prototype skill dir>/references/review.md` + branch file (`logic.md` · `ui.md` · `data.md` · `pipeline.md`) for the branch's rules.
6. **Containment** - below.
7. **Report** - `reviews/prototype-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md` (name taken → append `-<name>`, never overwrite); folder first created → `/reviews/` + one-line comment into `.gitignore`. Reply: verdict · counts · Must lines · report path.

## Specific checks beyond the checklist
- **Deciding-case test:** name the one case separating the possible answers (tie · late row · wrong-state action · failed task · layout at real data density). Must be reachable + visible in output. Not reachable → Must (area 2).
- **Only-the-question test:** per file · function · key · variant · task: answer changes without it? No → Should (area 3) + lines to delete.
- **Purity test (Logic):** list core module's imports + calls: anything that prints · reads input · reads clock/random · opens a file · imports the shell → Must (area 6). `step` twice on one state: input unchanged.
- **Structure test (UI):** per variant one line each: layout · hierarchy (largest + first element) · primary action (what, where) · navigation model. Any pair equal in ≥3 of 4 → Must (area 7).
- **Synthetic test (Data):** every row traces to a literal in the prototype with a stated case. File read (`read_csv` · `read_parquet` · `COPY` · `ATTACH` · a seed not written in the prototype) → open only name + size, never rows; origin unclear → Must (area 8).
- **Stub test (Pipeline):** every task body, line by line: print · sleep · in-memory write · small return · planned raise. Anything else → Must (area 9).
- **Containment test:** git project → `git status --porcelain` + `git diff --stat`:
  - every path outside `prototypes/` listed under "Files outside prototypes/" (or the one mount line in host page);
  - exempt: `reviews/`, `.gitignore` lines for `/prototypes/` + `/reviews/`; other `prototypes/*` folders belong to their own `NOTES.md`;
  - `git check-ignore prototypes/<name>` must succeed;
  - search real tree for imports of `prototypes/` + `prototype` in file names;
  - dependency or lock files changed → Must (area 11).
  - No git → compare with `NOTES.md` list, say check was partial.
- **Clean-up test** (`Status: done`): "Keep" names a real target file for everything absorbed; following it leaves no file · mount line · switcher · dependency behind.

## References
| File | Read when |
|---|---|
| `<prototype skill dir>/references/review.md` | always: checklist · severity · verdict |
| `<prototype skill dir>/references/logic.md`, `ui.md`, `data.md`, `pipeline.md` | the prototype's branch |
| `references/format.md` | step 7: report format · run table |
