---
name: darshan-singh-meel-prototype
description: Throwaway code that answers one design question before the real code is written - four branches picked from the question. Logic (terminal app over a pure module, full state redrawn after every key), UI (2-5 structurally different variants behind ?variant= in React, Streamlit or one HTML file), Data (a model, SQL or transformation on synthetic rows in local DuckDB; dbt on DuckDB only for dbt-structure questions), Pipeline (an Airflow task flow with stub tasks - dependencies, branching, retries, reruns). Lives in git-ignored prototypes/<name>/ with a NOTES.md (question, run command, answer, what to keep), runs with one command, is checked by a script, then deleted or absorbed. Use when asked to prototype, spike, mock up or compare layouts. Triggers - "prototype this", "quick spike", "let me play with it", "try a few designs", "mock up", "try the SQL locally first", "dry-run the DAG flow". Not for production code, queries on real data (darshan-singh-meel-notebook), or reviewing a prototype.
---

# Prototype
Throwaway code that answers one question; question → shape; answer = only thing kept. CLAUDE.md applies.

## Branch = the question
| Question about | Branch | Shape | Read |
|---|---|---|---|
| State · rules · transitions · an API's feel: "what happens when X then Y?" | **Logic** | terminal app over a pure module | `references/logic.md` |
| Screen layout: "what should this look like?" | **UI** | 2-5 variants behind `?variant=` | `references/ui.md` |
| Data model · SQL · transformation · dbt structure: "does this grain / join / incremental rule hold?" | **Data** | synthetic rows in local DuckDB | `references/data.md` |
| Orchestration flow: "what runs, skips, retries, reruns?" | **Pipeline** | stub tasks, `dag.test()` or plain-Python stand-in | `references/pipeline.md` |

- Two questions → two prototypes. Question names real data ("how many duplicates do we have?") → not a prototype: `darshan-singh-meel-notebook`.
- Branch unclear + user unreachable → branch matching the code around the request (module → Logic · page → UI · model → Data · DAG → Pipeline); reason → `NOTES.md` Assumptions, as a fact about the code ("The change sits in a state module").

## Works with
| Need | Skill |
|---|---|
| UI: look · layout · states | `darshan-singh-meel-frontend` + build skill: `darshan-singh-meel-frontend-react` or `darshan-singh-meel-streamlit` |
| Data + Pipeline: SQL · dbt · Airflow rules · pinned versions · official docs | `darshan-singh-meel-data-platform` (`sql.md` · `dbt.md` · `airflow.md` as needed) |
| Real data needed to answer | stop → `darshan-singh-meel-notebook` |
| Question itself unclear | `darshan-singh-meel-ask-me` |
| Absorbing the answer into real code | `darshan-singh-meel-code` (tests + error handling start there) |
| Independent check | `darshan-singh-meel-prototype-review` |

## Rules
- **Question first:** one sentence ending "?" in `NOTES.md` before any code; code not helping answer it → not written.
- **One command to run**, from project root, in `NOTES.md`; project's runtime + task runner, no new package manager.
- **In memory:** no files · tables · services, unless persistence is the question → then a file inside the prototype folder.
- **Full state** shown after every action · variant switch · query · task: user reads the answer off the screen.
- **Pure core, thin shell:** part under test (reducer · SQL file · task graph · variant component) holds no I/O, no shell code → liftable. Shell (terminal loop · switcher · runner) is deleted.
- **No polish:** no tests · no error handling beyond running · no options · no abstractions · no "later we might". `darshan-singh-meel-frontend` design rules still apply to UI variants: they are what is judged.
- **Synthetic + local only:** rows by hand or generated in code; no warehouse · cloud · API · real rows · secrets · secret files opened (CLAUDE.md data rules); stubs replace every real system.
- **Never promoted as is:** answer absorbed by rewriting under `darshan-singh-meel-code`; prototype files never move into the real tree.
- **Local files only:** no hosted preview · shared link.

## Location
```
prototypes/<name>/          git-ignored; <name> = lower case, hyphens, 2-4 words
  NOTES.md                  question, branch, run command, assumptions, answer, keep
  <core>                    logic.py · rules/*.sql or a dbt project · flow.py / dag.py · index.html / app.py
  <shell>                   tui.py · run.py
```
- First prototype in a project → `/prototypes/` + one-line comment into `.gitignore` at project root (create if missing).
- **Exception, UI on an existing page:** variants live on that page behind `?variant=`, in files whose names contain `prototype`; every added/changed file listed in `NOTES.md` under "Files outside prototypes/". `NOTES.md` stays in `prototypes/<name>/`.
- Paths in `NOTES.md` + replies relative to project root.

## Process (fixed)
1. **Setup** - one AskUserQuestion, rec first, skip what user said, no answer → rec + say which.

   | # | Question | Options |
   |---|---|---|
   | 1 | Question to answer | request restated as one sentence (rec) · 1-2 narrower readings · free text |
   | 2 | Branch | branch from table above (rec) · next closest |
   | 3 | Branch detail | UI: 3 variants on `<existing page>` (rec) · 3 on a new page · 2 / 4 / 5. Data: plain DuckDB (rec) · dbt on DuckDB (question = refs, tests, incremental logic). Pipeline: stand-in (rec when Airflow not installed) · `dag.test()`. Logic: none |
2. **Notes** - `prototypes/<name>/NOTES.md` from `references/templates/NOTES.md`: question · branch · run command · assumptions → engineer's own notes (CLAUDE.md "Author voice"). `.gitignore` line.
3. **Read** branch file + skills in "Works with". Check project's pinned versions before using an API.
4. **Core** - smallest pure module that can answer the question.
5. **Shell** - thinnest thing that drives the core + shows full state. Start from `references/templates/`.
6. **Run** with the run command; read output. Must start; every key · variant · task shows state.
7. **Check** - `python <skill dir>/scripts/check_prototype.py prototypes/<name>`; fix every `FAIL`.
8. **Hand over** - reply: run command · what to try (2-4 cases probing the question) · what was assumed. User drives; cases they ask for are added.
9. **Answer** - user has seen enough, or run itself decides → fill "Answer" + "Keep" in `NOTES.md`, `Status: done`, rerun check with `--done`. User away → leave both as placeholders, say so.
10. **Delete or absorb** - only on user's word: absorb what "Keep" names (rewritten under `darshan-singh-meel-code`) → delete `prototypes/<name>/` + every listed outside file. Before deleting, offer to copy the answer to where the project keeps decisions (ADR · issue · commit message).

## Check script
`scripts/check_prototype.py prototypes/<name> [--done] [--no-gitignore]`, stdlib, exit 1 on any `FAIL`:
- `NOTES.md`: branch · run command · question; `--done`: answer + keep filled;
- `/prototypes/` in project's `.gitignore` (`--no-gitignore` only for an example stored inside a repo that tracks it);
- no secret-looking file (reported by name, never opened), no secret-looking value (reported `<redacted>`);
- Data: no warehouse/cloud client import · remote URL · remote DuckDB extension or attach · file/database opened outside the folder; dbt `profiles.yml` in folder holds only `type: duckdb` + relative `.duckdb` path;
- Pipeline: no provider operator · connection · variable · network client;
- UI: 2-5 variants listed in `NOTES.md`, each key found in code; listed outside files exist + named `*prototype*`.

Does not judge whether the prototype answers its question → self-review vs `references/review.md`, or run reviewer skill.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/logic.md` | Logic: core shapes · frame · keys · piped input |
| `references/ui.md` | UI: host page or new page · what "structurally different" means · switcher per stack |
| `references/data.md` | Data: synthetic rows · DuckDB · when dbt · prototype's own dbt profile |
| `references/pipeline.md` | Pipeline: stand-in · `dag.test()` + its setup · stubs |
| `references/review.md` | self-review before step 8; reviewer skill's checklist |
| `references/templates/` | `NOTES.md` · `logic/logic.py`, `logic/tui.py` · `pipeline/flow.py` · `ui/variants.html` · `dbt/profiles.yml` |
| `references/examples/prototypes/order-dedup/` | one finished Data prototype with output (`run.out`): target for size + density |
| `references/sources.md` | official pages behind the API names; what was not verified |
