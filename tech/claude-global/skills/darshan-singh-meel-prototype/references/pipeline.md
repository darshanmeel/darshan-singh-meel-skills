# Pipeline branch

Prototype the task flow of an Airflow Dag - what runs, in which order, what is skipped, retried, and what a rerun does - with stub tasks. Follow `darshan-singh-meel-data-platform` (`airflow.md`). Template: `templates/pipeline/flow.py`.

## Stubs only
- A task body prints, sleeps, writes to an in-memory dict that stands in for the target, returns a small value, or raises on purpose. Nothing else.
- No provider operator, hook, connection, variable, `BashOperator`, HTTP or cloud client. The check script fails on these.
- Planned failures are explicit and named: `raise RuntimeError("source timeout (planned failure on try 1)")`.
- The logical date is an argument; never `datetime.now()` in a stub (same rule as real tasks).

## Which runner
| Situation | Runner |
|---|---|
| Airflow is not installed in the project's environment, or the machine is Windows without WSL2 (Airflow runs on POSIX systems only) | stand-in `flow.py` |
| The question is about flow semantics that are simple to state: order, a branch, a join, retry count, rerun | stand-in `flow.py` (starts in a second, nothing to set up) |
| The question depends on Airflow's own behaviour: trigger rules beyond the two below, dynamic task mapping, task groups, setup/teardown, XCom passing, scheduling arguments | `dag.test()` |

Never install Airflow for a prototype without asking; never use the project's or the user's Airflow home, database or connections.

## Stand-in (`flow.py`, stdlib)
- `TASKS = {id: (stub, upstream ids, retries, trigger rule)}`: the task graph as data, the part that is absorbed.
- Runs tasks in topological order (`graphlib.TopologicalSorter(...).static_order()`), one process, no scheduler.
- Rules it implements, stated in `NOTES.md` under Assumptions because they are a simplification:
  - a task with a failed upstream becomes `upstream_failed`;
  - a stub that returns a list of task ids is a branch: its other direct downstream tasks become `skipped`;
  - `all_success`: a skipped upstream skips the task; `none_failed_min_one_success`: runs when at least one upstream succeeded and none failed;
  - `retries` = extra tries, without delay.
- After every task it prints the state of all tasks; after every run, the store.
- Rerun check: the same logical date runs twice; the store must be equal after the second run. A second date exercises the other branch.
- Anything the stand-in does not model is not answered by it: say so in "Answer", or switch to `dag.test()`.

## `dag.test()` (Airflow 3)
Read on airflow.apache.org for Airflow 3.4.0; not executed while writing this skill - run it and read the output before trusting it.

```python
"""Pipeline prototype. Run: python prototypes/<name>/run.py"""
from airflow.sdk import dag, task


@dag(schedule=None, default_args={"retries": 1}, tags=["prototype"])
def orders_flow_prototype():
    @task
    def extract():
        print("extract: 3 synthetic rows")
        return 3

    @task.branch
    def choose(rows):
        return "full_load" if rows > 100 else "delta_load"   # a task id, a list of ids, or None

    @task
    def full_load():
        print("full_load")

    @task
    def delta_load():
        print("delta_load")

    @task(trigger_rule="none_failed_min_one_success")       # join after a branch
    def publish():
        print("publish")

    picked = choose(extract())
    picked >> [full_load(), delta_load()] >> publish()


flow = orders_flow_prototype()

if __name__ == "__main__":
    flow.test()
```

- Imports come from `airflow.sdk` (`DAG`, `dag`, `task`, `TaskGroup`, `chain`, …), not from internal modules.
- `dag.test()` runs every task in one Python process, without an executor. Arguments read on the page: `logical_date`, `use_executor`, `mark_success_pattern` (a regular expression of task ids marked successful without running).
- **It needs** an initialised metadata database (`airflow db migrate`) and the Dag file inside a configured Dag bundle (by default the Dags folder); a Dag built outside it fails with "… the dag is not serialized".
- **Keep it inside the prototype folder.** `run.py` (shell) sets, before anything imports Airflow, then runs `airflow db migrate` once and the Dag file:
  - `AIRFLOW_HOME` = `<abs path>/prototypes/<name>/.airflow` (default is `~/airflow`; the SQLite metadata database defaults to `{AIRFLOW_HOME}/airflow.db`);
  - `AIRFLOW__CORE__DAGS_FOLDER` = `<abs path>/prototypes/<name>` (must be absolute);
  - `AIRFLOW__CORE__LOAD_EXAMPLES` = `False`.
  - Compute the absolute paths at run time from `__file__`; never write them into a file.
- Retries: `default_args={"retries": n}` is inherited by every task. Whether `dag.test()` waits for `retry_delay` between tries - check: airflow.apache.org, Debugging Airflow Dags; keep delays at seconds.
- Downstream of a branch use `none_failed_min_one_success` on the join; `all_success` (the default) skips it.
- Project pins Airflow 2.x → its imports and decorators differ - check: the docs for that version (version selector).
- State to show: after the run, print every task instance's state from the returned Dag run - check: Debugging Airflow Dags, the example with `run.get_task_instance(...)`.

## What to try (hand-over)
The runs that probe the question: the normal date, the date that takes the other branch, a planted failure with and without retries left, the same date again.

## Absorb
- What moves: the task ids, dependencies, trigger rules, retry settings and the rerun rule, rebuilt with real operators under `darshan-singh-meel-code` + `airflow.md`.
- What never moves: stub bodies, the store dict, the stand-in runner, `.airflow/`.
