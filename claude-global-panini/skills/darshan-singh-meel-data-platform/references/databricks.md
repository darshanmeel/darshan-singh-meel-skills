# Databricks, PySpark, Delta, Unity Catalog

## PySpark
- Built-in functions (`pyspark.sql.functions`) over Python UDFs; if unavoidable, pandas UDFs.
- No `collect()`, `toPandas()`, or `.count()` on large data to inspect or loop. No Python loops over rows.
- Explicit schemas for production reads; no `inferSchema`.
- Broadcast small dimension tables; watch for skewed join keys.
- `cache()`/`persist()` only for reused, expensive DataFrames; `unpersist()` after.
- No `repartition(1000)` or `coalesce(1)` without a reason.

## Delta
- `MERGE` for upserts; `replaceWhere` for partition overwrites; writes idempotent.
- Partition only on low-cardinality filter columns (e.g. date); never on IDs. Prefer liquid clustering for selective columns.
- `OPTIMIZE` to fix small files. `VACUUM` with default retention — shorter breaks time travel and concurrent readers.
- Schema changes deliberate (`mergeSchema` only when intended).

## Unity Catalog & RBAC
- Three-level names `catalog.schema.table`; no DBFS mounts or hardcoded workspace paths.
- Catalog per environment (e.g. `dev`, `prod`) or per domain — follow the project.
- Grants: `GRANT SELECT ON SCHEMA prod.sales TO \`analysts\``. Readers also need `USE CATALOG` and `USE SCHEMA`.
- Jobs run as **service principals**, not personal accounts.
- Cloud storage via storage credentials + external locations — no access keys in code.
- Cluster policies to limit size/cost; row filters and column masks for sensitive data.
- Secrets via secret scopes / `dbutils.secrets.get()`.

## Compute & cost
- Job compute for scheduled work; all-purpose clusters only for interactive use.
- Auto-termination on interactive clusters; autoscaling with sane max.
- Serverless or Photon where the project uses them.

## Notebooks & deploy
- No leftover `display()`, test cells, or hardcoded widget values in production.
- Reusable logic in Python modules, not copy-pasted cells.
- Deploy with Asset Bundles (`databricks bundle validate` / `deploy -t <env>`) or the project's CI — not by editing jobs in the UI.
