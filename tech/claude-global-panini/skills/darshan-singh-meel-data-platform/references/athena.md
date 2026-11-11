# Athena (and Glue Data Catalog)

- Cost is per data scanned: Parquet/ORC, compressed, partitioned; select only needed columns; filter on partition columns.
- Partition projection for date/hour partitions instead of `MSCK REPAIR TABLE` on large tables.
- Avoid many small files; compact (CTAS, or `OPTIMIZE` on Iceberg tables).
- Transforms with CTAS / `INSERT INTO` / dbt-athena; write to a separate location per table.
- Workgroups per team/workload: per-query scan limit, encrypted results location, engine version pinned.
- Permissions via Lake Formation or IAM scoped to databases/tables and S3 prefixes — not broad `s3:*`.
- Prefer Iceberg tables when you need `MERGE`, `UPDATE`, `DELETE`, or time travel (see `iceberg.md`).
- Docs state: workgroup, catalog database, S3 locations, roles to request.
