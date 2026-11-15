# Databricks, Spark/PySpark, Delta

Databricks platform work — cost and DBUs, compute, warehouse and query tuning, jobs and pipelines, Unity Catalog grants, audit logs, system tables, audit-type apps — → `darshan-singh-meel-databricks` (review: `darshan-singh-meel-databricks-review`). Build rules there: `performance.md` (PySpark, Delta, tuning), `governance.md` (Unity Catalog), `compute.md` (clusters), `jobs-pipelines.md` (notebooks and deploy).

Kept here: the rules for Spark and Delta on any platform (EMR, Glue, Synapse, Databricks).

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

## Other cross-stack rules
- Iceberg tables: `iceberg.md`. Access model: `rbac.md`. dbt on Databricks → `darshan-singh-meel-dbt`.
