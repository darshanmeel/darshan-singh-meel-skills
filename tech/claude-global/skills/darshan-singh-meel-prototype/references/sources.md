# Sources and verification status

Official pages only. Status: **read** = the fact was read on the page (November 2026) · **ran** = executed while writing the skill · **own** = this skill's working default · **check** = not read or not run; verify on the page named.

## Pages used
| Rule in this skill | Page | Status |
|---|---|---|
| `st.query_params`: dict-like, since 1.30.0; keys and values are strings; `.get`, `get_all`, `to_dict`, `from_dict`, `clear`; page navigation in a multipage app clears query parameters except those bound with `bind="query-params"` | Streamlit docs 1.67.0, st.query_params - `https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params` | read |
| `st.segmented_control(label, options, *, selection_mode="single", default=None, required=False, format_func=None, key=None, …, bind=None, …)`; returns the option or `None`; `required=True` (single mode) prevents deselecting; `bind="query-params"` syncs the value with the URL and needs `key`, which is the parameter name | Streamlit docs 1.67.0, st.segmented_control - `https://docs.streamlit.io/develop/api-reference/widgets/st.segmented_control` | read |
| `useSearchParams` from `react-router` returns `[URLSearchParams, setSearchParams]`; setter takes a string, object, tuple array, `URLSearchParams` or a callback; setting causes a navigation | React Router docs 8.5.1, useSearchParams - `https://reactrouter.com/api/hooks/useSearchParams` | read |
| `dag.test()` runs all tasks in one process, no executor by default; `logical_date`, `use_executor`, `mark_success_pattern`; needs `airflow db migrate` and the Dag file inside a configured Dag bundle | Airflow docs 3.4.0, Debugging Airflow Dags - `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/debug.html` | read |
| `from airflow.sdk import DAG, dag, task, …` as the public authoring interface | Airflow Task SDK docs 1.4.0 - `https://airflow.apache.org/docs/task-sdk/stable/index.html` | read |
| `@task.branch` returns a task id, a list of ids, or `None`; trigger rules and default `all_success`; `none_failed_min_one_success` on a join after a branch; `default_args={"retries": 2}` inherited by tasks; `schedule=None` | Airflow docs 3.4.0, Dags - `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html` | read |
| `AIRFLOW__{SECTION}__{KEY}` environment variables; `AIRFLOW_HOME` default `~/airflow` | Airflow docs 3.4.0, Setting Configuration Options - `https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html` | read |
| `[core] dags_folder` (absolute path, default `{AIRFLOW_HOME}/dags`), `[core] load_examples` (default `True`), `[database] sql_alchemy_conn` default `sqlite:///{AIRFLOW_HOME}/airflow.db` | Airflow docs 3.4.0, Configuration Reference - `https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html` | read |
| Airflow runs on POSIX systems; Windows through WSL2 or Linux containers; tested with Python 3.11-3.14 | Airflow docs 3.4.0, Prerequisites - `https://airflow.apache.org/docs/apache-airflow/stable/installation/prerequisites.html` | read |
| DuckDB adapter built into dbt v2; profile needs `type: duckdb`; `path` to a local file, relative paths resolved from the `profiles.yml` location; no `path` or `:memory:` = in-memory, lost after the run; no authentication | dbt docs (v2), DuckDB setup - `https://docs.getdbt.com/docs/core/connect-data-platform/duckdb-setup` | read |
| `profiles.yml` search order: v2 `--profiles-dir` → project root → `~/.dbt/`; v1 (1.11+) `--profiles-dir` → `DBT_ENGINE_PROFILES_DIR` → `DBT_PROFILES_DIR` → current directory → `~/.dbt/` | dbt docs, About profiles.yml - `https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles` | read |
| Installing dbt gives v2 (`python -m pip install dbt` and other installers); `dbt`, `dbt-oss` and `dbt-core` use the same entry point and do not share an environment | dbt docs, Install dbt - `https://docs.getdbt.com/docs/local/install-dbt` · Install dbt OSS - `https://docs.getdbt.com/docs/local/install-dbt-v2` | read |
| `duckdb.connect(":memory:")` in-memory, a file path = persistent; `execute` + `fetchall`; `executemany`; parameters `?`, `$1`, `$name` | DuckDB docs 2.0, Python DB API - `https://duckdb.org/docs/2.0/clients/python/dbapi.html` | read |
| `graphlib.TopologicalSorter(graph)` with node → predecessors; `static_order()` (Python 3.9+); `CycleError` | Python docs, graphlib - `https://docs.python.org/3/library/graphlib.html` | read |

## Ran while writing
- `templates/logic/tui.py` with piped keys, `templates/pipeline/flow.py`: Python 3.14, exit 0.
- `examples/prototypes/order-dedup/run.py`: Python 3.14, `duckdb` 1.5.1, exit 0; output in `run.out`. `QUALIFY` and `executemany` with `?` worked on that version.
- dbt 2.0.11 on DuckDB (bundled driver), Windows: the template `profiles.yml`, `dbt seed` + `dbt snapshot --profiles-dir .` from the prototype folder; `prototype.duckdb`, `target/`, `logs/`, `.user.yml` stayed in the folder.
- `templates/ui/variants.html` served with `python -m http.server`, rendered in headless Chrome: `?variant=` per key, unknown key → first variant.
- `scripts/check_prototype.py` on the example (0 FAIL) and on prototypes with planted errors (each caught).

## Own defaults (not official)
- The four branches, `prototypes/<name>/`, the `NOTES.md` sections, 3 variants by default and 2-5 allowed, "differ in at least two of layout, hierarchy, primary action, navigation model".
- The stand-in's task-state rules in `pipeline.md`: a simplification of Airflow's trigger rules, not a copy.
- The key allow-list for the prototype's dbt profile and the secret and remote patterns in `check_prototype.py`.
- Serving a plain-HTML prototype with `python -m http.server --directory`.

## Not verified
- The `dag.test()` example in `pipeline.md` was not executed (no Airflow in the authoring environment): the decorator arguments `trigger_rule` and `default_args` are read, the whole file is not run - check: run it.
- Whether `dag.test()` honours `retry_delay`, and how to print all task states from its return value - check: Debugging Airflow Dags.
- The version that added `bind` and `required` to `st.segmented_control`, and whether a URL value overrides `default` on first load - check: the page's version selector; run it.
- A `replace` option on React Router's `setSearchParams`; Next.js and TanStack Router search-param hooks; Vite's `import.meta.env.DEV` - check: reactrouter.com, nextjs.org/docs, tanstack.com/router, vite.dev.
- `dbt-core` + `dbt-duckdb` install line and profile keys for dbt Core v1; where dbt-duckdb v1 resolves a relative `path` from - check: DuckDB setup page with the version selector on v1. Running dbt from the prototype folder with `--profiles-dir .` makes both readings give the same file.
- dbt Core v1 + `dbt-duckdb` was not run; arrow keys and the prev/next buttons of `variants.html` were not clicked in a browser.

## How to re-check
Open the page in the table, find the API named, compare with the rule. Streamlit, Airflow, dbt and React Router change between releases: re-read for the version the project pins.
