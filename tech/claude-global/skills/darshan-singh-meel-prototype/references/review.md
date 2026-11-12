# Review checklist for a prototype

Used by `darshan-singh-meel-prototype-review` (all columns) and by the builder before hand-over (Must column). Judge against `NOTES.md`: the question, the branch, the run command.

| # | Area | Check | Must when |
|---|---|---|---|
| 1 | Runs | the run command from `NOTES.md`, typed as written from the project root, starts the prototype; exit code 0 (or a clean quit); every key, variant, query or task produces output | it does not start; a key, variant or task crashes; the command needs steps `NOTES.md` does not name |
| 2 | Answers the question | the question is one sentence, answerable by watching the prototype; the cases that decide it can be reached (the edge, the tie, the failure, the rerun); "Answer", when filled, follows from what the run shows | the deciding case cannot be produced; the answer contradicts the output; the question is a topic, not a question |
| 3 | Only the question | no second question, no feature, option, config, test suite, logging, generalisation or persistence the question does not need | - (Should: each extra, with the lines to delete) |
| 4 | Branch fits | Logic for state and rules · UI for layout · Data for model, SQL, transformation · Pipeline for task flow | the shape cannot answer the question (a UI mock-up for a rule question, a terminal app for a layout question) |
| 5 | Full state shown | Logic: whole frame redrawn after every key · UI: variant key and name visible, URL updated · Data: input rows and each candidate's rows and verdicts · Pipeline: every task's state after every task, the store after every run | the user cannot see the state that answers the question |
| 6 | Pure core, thin shell | Logic: core has no print, input, file, clock, random, terminal code; `step` does not mutate · Data: candidate SQL in its own files · Pipeline: task graph as data or decorators, stub bodies trivial · UI: one component or function per variant, no shared layout | core and shell are mixed so the core cannot be lifted out |
| 7 | UI variants | 2-5; any two differ in at least two of layout, hierarchy, primary action, navigation model; same synthetic data; switcher writes `?variant=`, survives reload, wraps, arrow keys, hidden outside development | fewer than 2 or more than 5; two variants differ only in colour, type, spacing or copy; the switcher can reach production |
| 8 | Data: synthetic and local | every row written in the prototype, each for a named case; no real row, export or sample; no warehouse or cloud client, remote URL, MotherDuck, remote extension; DuckDB in memory or a file in the folder; dbt only for a dbt-structure question, as a separate project with the template profile and `--profiles-dir .` on every command; dialect differences listed | any real data; any non-local connection; the real dbt profile or project used; a profile with more than `type: duckdb` and a local path |
| 9 | Pipeline: stubs | bodies only print, sleep, write the in-memory store, return a small value or raise on purpose; no provider operator, hook, connection, variable, network client; logical date passed in; `dag.test()` runs with Airflow home and Dags folder inside the prototype folder; stand-in simplifications listed under Assumptions | a task touches a real system; the user's Airflow home, database or connections are used |
| 10 | Notes | `NOTES.md` has question, branch, run command, assumptions; UI: variants; outside files or "none"; `Status: done` → answer with what was observed, and keep (delete all, or what goes into which file); written as the engineer's notes, no chat references (CLAUDE.md "Author voice") - a leak is a Should | question, branch or run command missing; done without answer or keep |
| 11 | Contained | `/prototypes/` in the project's `.gitignore`; nothing outside `prototypes/<name>/` added or changed except the files listed in `NOTES.md`, each named `*prototype*`, plus one mount line in the host page; real code does not import from `prototypes/`; no task-runner entry, dependency or config added to the project | an unlisted file outside the folder; real code depends on the prototype; a project dependency or lock file changed without the user's yes |
| 12 | Secrets and privacy | no secret file, key, token, password or connection string; no personal data, employer or client names in rows, labels or notes; paths relative to the project root | a secret or real personal data anywhere |

## Severity
| Level | Meaning |
|---|---|
| Must | the prototype cannot be trusted to answer its question, breaks a hard limit (real data, real systems, secrets, leak into real code), or meets a "Must when" above |
| Should | it answers, but carries weight a throwaway should not have, or hides part of the state |
| Other | optional; at most 5 |

- Every finding: place (file and line, or the key / variant / task) · what · why · fix.
- No finding without evidence: the command and its output, the quoted line, the two variants compared.
- Missing polish is never a finding: no tests, no error handling, rough code are correct for a prototype.
- A `FAIL` line of `check_prototype.py` is a Must candidate: read it in context first.

## Verdict
| Verdict | When |
|---|---|
| Usable | no Must: the answer can be read off this prototype |
| Usable after Must fixes | 1-3 Must, none in area 2 or 4, none involving real data, real systems or secrets |
| Redo | more than 3 Must, or a Must in area 2 or 4 (wrong question or shape), or in area 8, 9 or 12 that involved real data, real systems or secrets |
