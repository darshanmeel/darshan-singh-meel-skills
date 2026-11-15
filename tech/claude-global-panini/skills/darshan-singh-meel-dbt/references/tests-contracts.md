# Tests, unit tests, contracts, constraints

## Data tests
- Generic (YAML): `unique`, `not_null`, `accepted_values`, `relationships`; packages add more (`dbt_utils.unique_combination_of_columns`, `expression_is_true`).
- Arguments under `arguments:` (dbt 1.10.5+); older form = top-level keys (docs: resource-properties/data-tests).
```yaml
models:
  - name: fct_order_lines
    description: One row per order line.
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          arguments:
            combination_of_columns: [order_id, line_no]
    columns:
      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: [placed, shipped, returned]
              config:
                severity: warn
                where: "order_date >= dateadd(day, -30, current_date)"
```
- Config: `severity`, `error_if` / `warn_if` (`">10"`), `where`, `limit`, `store_failures`, `store_failures_as` (check: docs.getdbt.com/reference/data-test-configs).
- Singular test: `tests/<name>.sql` returning failing rows; zero rows = pass. Good for reconciliations (model total vs source total within a tolerance).
- Custom generic test: `tests/generic/test_<name>.sql` with `{% test name(model, column_name) %}`; severity from a var lets dev warn and CI error.
- Minimum per model: PK `unique` + `not_null` (or combination test); `relationships` on critical FKs; `accepted_values` on status columns that drive logic; one or two tests on the riskiest business rule; not a test on every column.
- Never delete or weaken a failing test to pass; `where:` / `warn` only with a reason in the description.
- `store_failures` writes failing rows to the warehouse: avoid on tables with personal data.

## Unit tests (dbt 1.8+, docs: unit-tests)
```yaml
unit_tests:
  - name: order_status_maps_returns
    model: fct_order_lines
    given:
      - input: ref('stg_erp__order_lines')
        rows:
          - {order_id: 1, line_no: 1, raw_status: 'R'}
      - input: ref('dim_status')
        format: csv
        rows: |
          code,status
          R,returned
    expect:
      rows:
        - {order_id: 1, line_no: 1, status: returned}
  - name: incremental_branch_keeps_late_rows
    model: fct_order_lines
    overrides:
      macros: {is_incremental: true}
    given:
      - input: this
        rows: [{order_line_id: 1, updated_at: '2025-01-01'}]
      - input: ref('stg_erp__order_lines')
        rows: [{order_line_id: 2, updated_at: '2024-12-30'}]
    expect:
      rows: [{order_line_id: 2, updated_at: '2024-12-30'}]
```
- YAML lives under `models/`. Only the columns that matter; every `ref`/`source` input listed.
- Runs against the warehouse by default (upstream relations must exist; `dbt run --select <parents> --empty` builds them empty). Local DuckDB compute is experimental (check: docs.getdbt.com/docs/build/unit-tests).
- Unit tests check the select output, not how merge applied it.
- Exclude in prod: `--exclude-resource-type unit_test`; run only them: `dbt test --select "test_type:unit"`.

## Contracts and constraints (docs: resource-properties/constraints)
```yaml
models:
  - name: dim_customer
    config:
      materialized: table
      contract: {enforced: true}
    columns:
      - name: customer_id
        data_type: number
        constraints: [{type: not_null}, {type: primary_key}]
```
- Contract = every column with `data_type`; the build fails on missing, extra or retyped columns.
- Constraints only on `table` and `incremental`.

| Constraint | Snowflake | Databricks |
|---|---|---|
| not_null | Enforced | Enforced |
| check | Not supported (skipped, warning) | Enforced |
| unique | Metadata only | Not supported |
| primary_key / foreign_key | Metadata only (`rely` for the optimizer) | Metadata only |
- Databricks creates the table without a schema and adds constraints with `ALTER`: the contract checks column names and order but not data types, and a failing constraint leaves the table with the bad data.
- Metadata-only PK → still add a `unique` data test.
- Public / versioned models (mesh) should be contracted (mesh-docs-semantic.md).

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| Which models have no tests? | `dbt_inventory.py health` → `untested_models` | One row per model | Ephemeral models can't be tested directly |
| Which models lack a PK test? | `health` → `no_pk_test` (no unique / combination test) | One row per model | A `unique` on a non-key column counts; check the column |
| Which tests only warn? | `health` → `warn_tests` | Test name, model | Warn forever = noise |
| Which tests fail most / take longest? | `dbt_inventory.py timing run_results.json --type test` | Status, seconds | Only the last invocation is in the file |
| How expensive are my tests on the warehouse? | performance-cost.md S1 / D1 with `node_id like 'test.%'` | Credits per test | `relationships` on big tables = two full scans |
| Is the model's total still equal to the source? | Singular reconciliation test or the notebook check below | Diff ≥ tolerance = FAIL | Compare same window and as-of date |
| Does the contract match the SQL? | Compare YAML columns with the model's final select | Any missing / extra column | Snowflake types: `varchar` vs `text` are aliases |
| What does this unit test actually prove? | Read given/expect | Only the listed columns | Incremental: override `is_incremental` |

```sql
-- Reconciliation verdict: model total vs source total, one as-of date
with s as (select sum(amount) as v from raw.erp.order_lines where order_date < :as_of),
     m as (select sum(amount) as v from analytics.marts.fct_order_lines where order_date < :as_of)
select s.v as source_total, m.v as model_total,
       iff(abs(s.v - m.v) < 0.005, 'PASS', 'FAIL') as verdict   -- Databricks: if(...)
from s cross join m;
```
