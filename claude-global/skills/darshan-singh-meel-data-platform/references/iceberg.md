# Apache Iceberg tables (Athena, Spark, Snowflake, others)

- One catalog per environment (Glue, REST, or the platform's); every engine must use the same catalog for a table.
- Hidden partitioning with transforms (`days(event_ts)`, `bucket(16, id)`); evolve partitions instead of rewriting tables.
- Schema evolution is by column ID: add/rename safely; never reuse a dropped column name for different data.
- Upserts with `MERGE INTO`; choose copy-on-write (read-heavy) or merge-on-read (write-heavy) deliberately.
- Maintenance on a schedule: compact data files, rewrite manifests, expire old snapshots, remove orphan files.
- Snapshot retention long enough for time travel and rollback needs; document it.
- Concurrent writers use optimistic commits — retry on commit conflicts; avoid many writers on one partition.
- Reads/writes via engine roles with catalog + storage permissions; no keys in jobs.
