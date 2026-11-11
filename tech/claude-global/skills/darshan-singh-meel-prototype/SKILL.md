---
name: darshan-singh-meel-prototype
description: Throwaway code that answers one design question before the real code is written - four branches picked from the question. Logic (terminal app over a pure module, full state redrawn after every key), UI (2-5 structurally different variants behind ?variant= in React, Streamlit or one HTML file), Data (a model, SQL or transformation on synthetic rows in local DuckDB; dbt on DuckDB only for dbt-structure questions), Pipeline (an Airflow task flow with stub tasks - dependencies, branching, retries, reruns). Lives in git-ignored prototypes/<name>/ with a NOTES.md (question, run command, answer, what to keep), runs with one command, is checked by a script, then deleted or absorbed. Use when asked to prototype, spike, mock up or compare layouts. Triggers - "prototype this", "quick spike", "let me play with it", "try a few designs", "mock up", "try the SQL locally first", "dry-run the DAG flow". Not for production code, queries on real data (darshan-singh-meel-notebook), or reviewing a prototype.
---

# Prototype

A prototype is throwaway code that answers one question. The question decides the shape; the answer is the only thing kept. Global rules in CLAUDE.md apply.

## Branch = the question
| The question is about | Branch | Shape | Read |
|---|---|---|---|
| State, rules, transitions, an API's feel: "what happens when X then Y?" | **Logic** | terminal app over a pure module | `references/logic.md` |
| How a screen is laid out: "what should this look like?" | **UI** | 2-5 variants behind `?variant=` | `references/ui.md` |
| A data model, SQL, a transformation, dbt structure: "does this grain / join / incremental rule hold?" | **Data** | synthetic rows in local DuckDB | `references/data.md` |
| An orchestration flow: "what runs, skips, retries, reruns?" | **Pipeline** | stub tasks, `dag.test()` or a plain-Python stand-in | `references/pipeline.md` |

- Two questions → two prototypes. A question that names real data ("how many duplicates do we have?") is not a prototype: `darshan-singh-meel-notebook`.
- Branch unclear and the user not reachable → the branch that matches the code around the request (module → Logic, page → UI, model → Data, DAG → Pipeline); write the assumption in `NOTES.md`.

## Works with
| Need | Skill |
|---|---|
| UI branch: look, layout, states | `darshan-singh-meel-frontend` + the build skill: `darshan-singh-meel-frontend-react` or `darshan-singh-meel-streamlit` |
| Data and Pipeline branches: SQL, dbt, Airflow rules, pinned versions, official docs | `darshan-singh-meel-data-platform` (`sql.md`, `dbt.md`, `airflow.md` as needed) |
| Real data is needed to answer | stop; `darshan-singh-meel-notebook` |
| The question itself is unclear | `darshan-singh-meel-ask-me` |
| Absorbing the answer into real code | `darshan-singh-meel-code` (tests and error handling start there) |
| Independent check of the prototype | `darshan-singh-meel-prototype-review` |

## Rules
- **Question first.** One sentence ending in "?", written in `NOTES.md` before any code. Code that does not help answer it is not written.
- **One command to run**, from the project root, written in `NOTES.md`. The project's runtime and task runner; no new package manager.
- **In memory.** No files, tables or services, unless persistence is the question; then a file inside the prototype folder.
- **Show the full state** after every action, variant switch, query or task: the user reads the answer off the screen.
- **Pure core, thin shell.** The part under test (reducer, SQL file, task graph, variant component) holds no I/O and no shell code, so it can be lifted out. The shell (terminal loop, switcher, runner) is deleted.
- **No polish.** No tests, no error handling beyond running, no options, no abstractions, no "later we might". Design rules of `darshan-singh-meel-frontend` still apply to UI variants: they are what is being judged.
- **Synthetic only, local only.** Rows are written by hand or generated in code. No warehouse, no cloud, no API, no real rows, no secrets, no secret files opened (CLAUDE.md data rules). Stubs replace every real system.
- **Never promoted as is.** The answer is absorbed by rewriting it under `darshan-singh-meel-code`; prototype files do not move into the real tree.
- **Local files only.** No hosted preview, no shared link.

## Location
```
prototypes/<name>/          git-ignored; <name> = lower case, hyphens, 2-4 words
  NOTES.md                  question, branch, run command, assumptions, answer, keep
  <core>                    logic.py · rules/*.sql or a dbt project · flow.py / dag.py · index.html / app.py
  <shell>                   tui.py · run.py
```
- First prototype in a project: add `/prototypes/` plus a one-line comment to `.gitignore` at the project root (create the file if missing).
- **Exception, UI on an existing page:** the variants live on that page behind `?variant=`, in files whose names contain `prototype`; every added or changed file is listed in `NOTES.md` under "Files outside prototypes/". `NOTES.md` stays in `prototypes/<name>/`.
- Paths in `NOTES.md` and replies are relative to the project root.

## Process (fixed)
1. **Setup questions** - one AskUserQuestion prompt, recommended first, skip what the user already said. No answer → recommended options, and say which.

   | # | Question | Options |
   |---|---|---|
   | 1 | The question to answer | the request restated as one sentence (Recommended) · 1-2 narrower readings · free text |
   | 2 | Branch | the branch from the table above (Recommended) · the next closest |
   | 3 | Branch detail | UI: 3 variants on `<existing page>` (Recommended) · 3 on a new page · 2 / 4 / 5. Data: plain DuckDB (Recommended) · dbt on DuckDB (question is about refs, tests, incremental logic). Pipeline: stand-in (Recommended when Airflow is not installed) · `dag.test()`. Logic: none |
2. **Notes** - `prototypes/<name>/NOTES.md` from `references/templates/NOTES.md`: question, branch, run command, assumptions. `.gitignore` line.
3. **Read the branch file** and the skills in "Works with". Check the project's pinned versions before using an API.
4. **Core** - the smallest pure module that can answer the question.
5. **Shell** - the thinnest thing that drives the core and shows the full state. Start from `references/templates/`.
6. **Run it** with the run command; read the output. It must start, and every key, variant or task must show state.
7. **Check** - `python <skill dir>/scripts/check_prototype.py prototypes/<name>`; fix every `FAIL`.
8. **Hand over** - reply: run command, what to try (the 2-4 cases that probe the question), what was assumed. The user drives; new cases they ask for are added.
9. **Answer** - when the user has seen enough, or the run itself decides it: fill "Answer" and "Keep" in `NOTES.md`, set `Status: done`, rerun the check with `--done`. User away → leave both sections as placeholders and say so.
10. **Delete or absorb** - only on the user's word: absorb what "Keep" names (rewritten under `darshan-singh-meel-code`), then delete `prototypes/<name>/` and every listed outside file. Before deleting, offer to copy the answer to where the project keeps decisions (ADR, issue, commit message).

## Check script
`scripts/check_prototype.py prototypes/<name> [--done] [--no-gitignore]`, stdlib, exit 1 on any `FAIL`:
- `NOTES.md`: branch, run command, question; `--done`: answer and keep filled;
- `/prototypes/` in the project's `.gitignore` (`--no-gitignore` only for an example stored inside a repo that tracks it);
- no secret-looking file (reported by name, never opened) and no secret-looking value (reported as `<redacted>`);
- Data: no warehouse or cloud client import, remote URL, remote DuckDB extension or attach, or file or database opened outside the folder; a dbt `profiles.yml` in the folder holds only `type: duckdb` and a relative `.duckdb` path;
- Pipeline: no provider operator, connection, variable or network client;
- UI: 2-5 variants listed in `NOTES.md`, each key found in the code; listed outside files exist and are named `*prototype*`.

It does not judge whether the prototype answers its question: self-review against `references/review.md`, or run the reviewer skill.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/logic.md` | Logic branch: core shapes, the frame, keys, piped input |
| `references/ui.md` | UI branch: host page or new page, what "structurally different" means, switcher per stack |
| `references/data.md` | Data branch: synthetic rows, DuckDB, when dbt, the prototype's own dbt profile |
| `references/pipeline.md` | Pipeline branch: stand-in, `dag.test()` and its setup, stubs |
| `references/review.md` | self-review before step 8; the reviewer skill's checklist |
| `references/templates/` | `NOTES.md` · `logic/logic.py`, `logic/tui.py` · `pipeline/flow.py` · `ui/variants.html` · `dbt/profiles.yml` |
| `references/examples/prototypes/order-dedup/` | one finished Data prototype with its output (`run.out`): the target for size and density |
| `references/sources.md` | official pages behind the API names; what was not verified |
