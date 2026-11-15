# Good practice: queries, storage, RBAC, cost, deploy notes

Advice to give with answers, and the rules for SQL and setups written on Snowflake.

## Queries and storage
- Check the query profile before scaling a warehouse: spilling, poor pruning, exploding joins (`performance.md`).
- No `SELECT *` on wide tables: storage is columnar, fewer columns = less I/O and runtime.
- `MERGE` for upserts; `QUALIFY` for dedupe; VARIANT paths cast explicitly (`col:field::string`); `FLATTEN` for arrays.
- Clustering keys only on very large tables with a measured pruning gain; they cost credits (`performance.md` P6, P7).
- Transient tables for staging and scratch (no Fail-safe cost).
- `COPY INTO` with an explicit file format and a deliberate `ON_ERROR`.
- `CREATE OR REPLACE TABLE` drops the data's history and the grants; avoid it in production, use `ALTER` or a swap (`ALTER TABLE ... SWAP WITH`). Use `COPY GRANTS` when replacing a view or table is the only option.
- Zero-copy clones for dev and test copies of production data, respecting masking; drop them when done (they retain storage, `storage.md` S5).

## RBAC
- Two layers: **access roles** (for example `SALES_RO`, `SALES_RW`: privileges on objects) granted to **functional roles** (for example `ANALYST`, `ETL_LOADER`: granted to users and groups).
- Object owner = a dedicated owner role (under `SYSADMIN`), not individuals.
- `USERADMIN` creates users and roles; `SECURITYADMIN` manages grants; `ACCOUNTADMIN` only for account-level tasks, never for pipelines or daily use (`security.md` X1, X12).
- Future grants so new objects inherit access: `GRANT SELECT ON FUTURE TABLES IN SCHEMA … TO ROLE …`.
- Managed access schemas when grants must be centrally controlled.
- Service users: `TYPE = SERVICE`, key-pair (or OAuth / workload identity) auth, one per pipeline, default role and warehouse set.
- Masking policies for PII columns; row access policies for row-level restrictions; tag-based masking to cover new columns automatically.
- Network policies for service users where possible.

## Cost guardrails
- Warehouse `AUTO_SUSPEND` about 60 s and `AUTO_RESUME` on for batch and ad hoc; longer only where cache warmth or resume latency is measured to matter. Separate warehouses per workload (load, transform, BI).
- Resource monitors with notify and suspend thresholds on every warehouse that matters, plus an account-level monitor; budgets for serverless spend.
- Right-size: start small; scale up only for proven spilling; multi-cluster only for concurrency (`warehouses.md`).
- Query tags on every pipeline and tool (`QUERY_TAG`) so cost can be attributed (`cost.md` C6).

## Deploy and access (what docs must state)
- Account (locator and region), databases and schemas per environment, warehouses, roles to request, and how access is requested.
- For apps reading system views: the read-only role and its grants (`audit-apps.md`), the warehouse it uses, and which views need which database role.
