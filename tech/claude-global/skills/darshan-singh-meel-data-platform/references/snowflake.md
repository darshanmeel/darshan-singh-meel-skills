# Snowflake

## Queries & storage
- Check the query profile before scaling a warehouse: spilling, poor pruning, exploding joins.
- No `SELECT *` on wide tables — columnar storage: fewer columns = less I/O and runtime.
- `MERGE` for upserts; `QUALIFY` for dedupe; VARIANT paths cast explicitly (`col:field::string`), `FLATTEN` for arrays.
- Clustering keys only on very large tables with measured pruning gain — they cost credits.
- Transient tables for staging/scratch (no Fail-safe cost).
- `COPY INTO` with an explicit file format and a deliberate `ON_ERROR`.
- `CREATE OR REPLACE TABLE` drops data and grants — avoid in prod; use `ALTER` or swap.
- Zero-copy clones for dev/test copies of prod data (respecting masking).

## RBAC
- Two-layer roles: **access roles** (e.g. `SALES_RO`, `SALES_RW` — privileges on objects) granted to **functional roles** (e.g. `ANALYST`, `ETL_LOADER` — granted to users/groups).
- Object owner = a dedicated owner role (under `SYSADMIN`), not individuals.
- `USERADMIN` creates users/roles; `SECURITYADMIN` manages grants; `ACCOUNTADMIN` only for account-level tasks, never pipelines or daily use.
- Future grants so new objects inherit access: `GRANT SELECT ON FUTURE TABLES IN SCHEMA … TO ROLE …`.
- Managed access schemas when grants must be centrally controlled.
- Service users: `TYPE = SERVICE`, key-pair auth, one per pipeline, default role and warehouse set.
- Masking policies for PII columns; row access policies for row-level restrictions.
- Network policies for service users where possible.

## Cost
- Warehouse `AUTO_SUSPEND` ~60s, `AUTO_RESUME` on; separate warehouses per workload (load, transform, BI).
- Resource monitors with notify + suspend thresholds.
- Right-size: start small; scale up only for proven spilling; multi-cluster only for concurrency.

## Deploy & access (what docs must state)
- Account, databases/schemas per environment, warehouses, roles to request, how access is requested.
