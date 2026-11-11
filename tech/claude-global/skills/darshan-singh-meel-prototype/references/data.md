# Data branch

Try a data model, a query or a transformation on synthetic rows in local DuckDB before it is built in the warehouse. Follow `darshan-singh-meel-data-platform` (`sql.md`; `dbt.md` when dbt is used). Example: `examples/prototypes/order-dedup/`.

## Hard limits
- **Synthetic rows only**, written in the prototype (a Python list, `VALUES`, a dbt seed of made-up rows). Never a real row, never an export, never a sample "just to be realistic".
- **Local only.** No warehouse, no cloud storage, no MotherDuck, no `httpfs` or other remote DuckDB extension, no URL in prototype code (doc links go in `NOTES.md`), no file or database opened outside the prototype folder. The check script fails on these.
- **The global query rule is not weakened:** it covers the user's data and metadata; this branch never touches either. The answer needs real data (volumes, real duplicates, real skew) → stop and hand off to `darshan-singh-meel-notebook`.
- Column names and types may be copied from the project's models, DDL or `schema.yml` (structure, not data).

## Synthetic rows
- State the grain of every table first, in `NOTES.md` under Assumptions.
- 5-30 rows per table, each row there for a reason, with a comment naming the case: the normal row, the duplicate, the late arrival, the null key, the boundary date, the orphan foreign key, the tie.
- Write the expected result next to the rows (`WANT = {...}`): the run prints PASS or FAIL per rule, the notebook skill's verdict style.
- Volume or performance questions are out of scope: DuckDB on a laptop says nothing about the warehouse's cost or speed.

## Plain DuckDB (default)
```
prototypes/<name>/
  NOTES.md
  run.py            shell: builds the rows, runs every file in rules/ (or models/ in order), prints rows + verdicts
  rules/*.sql       core: one candidate per file - the part that is absorbed
```
- `duckdb.connect(":memory:")`; a file (`prototypes/<name>/prototype.duckdb`) only when the question is about state between runs (incremental load, rerun, late data).
- Insert with parameters (`executemany` with `?`); read with `execute(sql).fetchall()`.
- Print after every step: the input rows once, then per candidate its rows and its verdicts. Full tables, they are small.
- Needs the `duckdb` Python package: use the project's environment if it has it; else ask before installing, into a virtual environment inside the prototype folder (`.venv`, skipped by the check script).
- **Dialect:** write the SQL the target warehouse will run wherever DuckDB accepts it; list every construct that differs under Assumptions (`QUALIFY`, `MERGE`, date functions, semi-structured types, case sensitivity of identifiers). DuckDB accepting it proves the logic, not the syntax on the target - check: the target engine's docs before absorbing.

## dbt on DuckDB (only for dbt-structure questions)
Use it when the question is about refs and layers, tests, snapshots, or incremental logic (`unique_key`, `is_incremental()`, strategy, late data, full refresh = same result). A question about one query's logic stays plain DuckDB.

- **Version:** the dbt version the project pins (`require-dbt-version`, requirements, lock file), so the answer transfers.
  - dbt v2: the DuckDB adapter is built in (docs.getdbt.com, DuckDB setup); install per "Install dbt".
  - dbt Core v1: `dbt-core` plus the `dbt-duckdb` adapter - check: docs.getdbt.com, DuckDB setup, version selector v1.
  - Nothing pinned → latest stable, pinned in the prototype's `requirements.txt`.
  - `dbt`, `dbt-oss` and `dbt-core` share one entry point: never install a second one into the project's environment. Use a virtual environment in the prototype folder, and ask before installing.
- **Layout:** a complete, separate dbt project inside `prototypes/<name>/` (`dbt_project.yml` with `profile: prototype`, `models/`, `seeds/` with synthetic CSV rows, `profiles.yml`). Never add models, seeds or targets to the project's real dbt project.
- **The prototype's own profile:**
  - Copy `templates/dbt/profiles.yml` to `prototypes/<name>/profiles.yml`. It holds one output: `type: duckdb`, `path: prototype.duckdb`. No account, user, password, token, `env_var()`, attach or extension keys.
  - It is written from the template, never edited by hand and never read back; `check_prototype.py` verifies it and prints key names only.
  - The user's real profile (`~/.dbt/profiles.yml`, or one in the real dbt project) is never opened, copied or used as a starting point (CLAUDE.md secret rule). Nothing in the prototype refers to it.
  - Every dbt command runs from the prototype folder with `--profiles-dir .`: the flag is first in dbt's search order in v1 and v2, so the real profile cannot be picked up; and the relative `path` resolves to the prototype folder in both.
- **Run command** (one line in `NOTES.md`): `cd prototypes/<name> && dbt build --profiles-dir .`
  - The shell reads the result with the `duckdb` package (`read_only=True`) after dbt has exited; dbt holds the file lock while it runs.
  - Incremental questions: the command runs the sequence that shows the answer, e.g. `python prototypes/<name>/run.py`, a shell that calls `dbt seed` / `dbt run` / `dbt run --full-refresh` with `--profiles-dir .`, swaps the seed for the "day 2" rows in between, and prints the target table after each step.
- `prototype.duckdb`, `target/`, `logs/`, `dbt_packages/`, `.user.yml` stay in the prototype folder; all are covered by the `/prototypes/` ignore line.
- dbt's own tests (`unique`, `not_null`, a singular test) are part of the answer when the question is "which test catches this?"; otherwise print verdicts and skip them.

## Absorb
- What moves: the chosen SQL (or model), rewritten for the target dialect, with the grain in the description and the minimal tests of `dbt.md`.
- What never moves: the synthetic rows as seeds, the DuckDB file, the prototype profile, the shell.
- First run against the warehouse is the user's, through `darshan-singh-meel-notebook`.
