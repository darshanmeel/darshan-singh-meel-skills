# Minimal tests for data work

- **dbt:** see `dbt.md` Tests.
- **SQL / Spark logic:** one tiny fixture (4–6 rows) covering main case, a duplicate, a NULL, and a late/boundary row — one test.
- **Python transforms:** one parametrized test per function with the key cases.
- **Airflow:** one DAG integrity test for all DAGs (imports cleanly, no cycles).
- **Terraform:** `fmt`, `validate`, reviewed `plan`; no unit tests unless the module is shared.
- **Reconciliation:** source vs target row counts / sums — often worth more than many column tests.
- Never weaken or delete a failing test to pass; downgrade to warn only with a reason.
