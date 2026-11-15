# Storage, Time Travel, Fail-safe, clones, stages

## Facts
- Billed on average daily bytes per TB-month: active + Time Travel + Fail-safe + internal stages + hybrid tables, plus archive tiers (cool/cold) at their own rates.
- Time Travel: `DATA_RETENTION_TIME_IN_DAYS` (0-1 on Standard, up to 90 on Enterprise for permanent tables). Fail-safe: 7 days after Time Travel for permanent tables; transient and temporary tables have no Fail-safe and at most 1 day of Time Travel.
- High churn (frequent full reloads, `CREATE OR REPLACE`, large updates) makes Time Travel and Fail-safe bytes larger than active bytes.
- Clones share micro-partitions; bytes a clone keeps alive show as `RETAINED_FOR_CLONE_BYTES` on the source. `CLONE_GROUP_ID = ID` → not a clone.
- `TABLE_STORAGE_METRICS`: key `ID`; `DELETED` BOOLEAN; Fail-safe rows can have NULL names and `DELETED = FALSE` → live tables need all of `NOT COALESCE(deleted, FALSE)`, `table_dropped IS NULL`, `schema_dropped IS NULL`, `catalog_dropped IS NULL`, `table_name IS NOT NULL`, `table_entered_failsafe IS NULL`. Hybrid tables not tracked.

## Catalogue

### S1. Storage per database over time
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date)
SELECT DATE_TRUNC(week, usage_date) AS week, database_name,
       AVG(average_database_bytes) / POWER(1024, 4) AS avg_tb_incl_time_travel,
       AVG(average_failsafe_bytes) / POWER(1024, 4) AS avg_failsafe_tb
FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY, p
WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
GROUP BY 1, 2
ORDER BY 1, avg_tb_incl_time_travel DESC;
```
- Read: growth per database per week; Fail-safe share above about 30% → churn (S3).
- Pitfall: database id, not name, survives a rename; dropped databases keep rows with `DELETED` set.

### S2. Biggest live tables and their storage split
```sql
SELECT m.id AS table_id, m.table_catalog || '.' || m.table_schema || '.' || m.table_name AS fqn,
       m.active_bytes / POWER(1024, 3) AS active_gb, m.time_travel_bytes / POWER(1024, 3) AS time_travel_gb,
       m.failsafe_bytes / POWER(1024, 3) AS failsafe_gb, m.retained_for_clone_bytes / POWER(1024, 3) AS clone_gb,
       m.is_transient, t.retention_time
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS m
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TABLES t ON t.table_id = m.id AND t.deleted IS NULL
WHERE NOT COALESCE(m.deleted, FALSE) AND m.table_dropped IS NULL AND m.schema_dropped IS NULL
  AND m.catalog_dropped IS NULL AND m.table_name IS NOT NULL AND m.table_entered_failsafe IS NULL
ORDER BY m.active_bytes + m.time_travel_bytes + m.failsafe_bytes + m.retained_for_clone_bytes DESC
LIMIT 50;
```
- Read: `time_travel_gb + failsafe_gb` ≫ `active_gb` → churn; `clone_gb` large → an old clone (S5) keeps data alive.

### S3. Churn: Time Travel and Fail-safe heavy tables
```sql
SELECT m.table_catalog || '.' || m.table_schema || '.' || m.table_name AS fqn, m.is_transient,
       m.active_bytes / POWER(1024, 3) AS active_gb,
       (m.time_travel_bytes + m.failsafe_bytes) / POWER(1024, 3) AS history_gb,
       ROUND((m.time_travel_bytes + m.failsafe_bytes) / NULLIF(m.active_bytes, 0), 1) AS history_x_active
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS m
WHERE NOT COALESCE(m.deleted, FALSE) AND m.table_dropped IS NULL AND m.table_name IS NOT NULL
  AND m.table_entered_failsafe IS NULL AND m.time_travel_bytes + m.failsafe_bytes > POWER(1024, 3)
ORDER BY history_gb DESC
LIMIT 50;
```
- Read: `history_x_active` above 2 on a staging or reload table → make it transient (no Fail-safe) or lower retention (user-run DDL; transient needs recreating). Check row changes with `TABLE_DML_HISTORY` (rows added/removed/updated per hour).

### S4. Dropped tables still billed
```sql
SELECT m.id AS table_id,
       COALESCE(m.table_catalog || '.' || m.table_schema || '.' || m.table_name, 'Fail-safe table (' || m.id || ')') AS label,
       m.table_dropped, m.table_entered_failsafe,
       (m.time_travel_bytes + m.failsafe_bytes) / POWER(1024, 3) AS billed_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS m
WHERE (m.table_dropped IS NOT NULL OR m.table_entered_failsafe IS NOT NULL OR m.table_name IS NULL)
  AND m.time_travel_bytes + m.failsafe_bytes > 0
ORDER BY billed_gb DESC
LIMIT 50;
```
- Read: still billed until Time Travel and Fail-safe end; Fail-safe cannot be shortened. Names can be NULL: label by ID.

### S5. Clones keeping old data alive
```sql
SELECT src.table_catalog || '.' || src.table_schema || '.' || src.table_name AS source_fqn,
       src.retained_for_clone_bytes / POWER(1024, 3) AS retained_gb,
       COUNT(c.id) AS clones_in_group
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS src
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS c
  ON c.clone_group_id = src.clone_group_id AND c.id <> src.id AND NOT COALESCE(c.deleted, FALSE)
WHERE src.retained_for_clone_bytes > 0
GROUP BY 1, 2
ORDER BY retained_gb DESC
LIMIT 50;
```
- Read: dropping or recreating the clones frees `retained_gb` (after their own Time Travel and Fail-safe). Unused clones: `joins-lineage.md` J9 on their names.

### S6. Stage storage
```sql
SELECT usage_date, entity_name, stage_type, bytes / POWER(1024, 3) AS gb, file_count, min_last_modified
FROM SNOWFLAKE.ACCOUNT_USAGE.STAGE_STORAGE_USAGE_DETAILS
WHERE usage_date = (SELECT MAX(usage_date) FROM SNOWFLAKE.ACCOUNT_USAGE.STAGE_STORAGE_USAGE_DETAILS)
ORDER BY gb DESC
LIMIT 50;
```
- Read: big internal stages with old `min_last_modified` → files never cleaned after load (`PURGE = TRUE` or `REMOVE`, user-run). Account total per day: `STAGE_STORAGE_USAGE_HISTORY`.
- Pitfall: 90 days, AWS and Azure only, latency up to 2 days, days can be missing (unknown, not 0); `STAGE_TYPE` is `User`, `Internal Named` or `Table`.

### S7. Tables nobody reads or writes
- Reads: `joins-lineage.md` J9. Writes: `TABLE_DML_HISTORY` rows per table in the window; no reads and no writes for 90 days and not referenced (J7) → archive or drop candidate. Show size from S2 next to it so the saving is visible.

### S8. Retention settings that cost money
```sql
SELECT table_catalog || '.' || table_schema || '.' || table_name AS fqn, table_type, is_transient,
       retention_time, bytes / POWER(1024, 3) AS gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
WHERE deleted IS NULL AND retention_time > 1 AND table_type = 'BASE TABLE'
ORDER BY retention_time * bytes DESC NULLS LAST
LIMIT 50;
```
- Read: long retention on large, churning tables multiplies Time Travel bytes; keep it where recovery needs it (production facts), cut it on staging.

### S9. Archive tiers and retrieval
- Archived bytes: `TABLES.ARCHIVE_STORAGE_COOL_*` / `COLD_*`, `DATABASE_STORAGE_USAGE_HISTORY.AVERAGE_ARCHIVE_STORAGE_*`. Retrievals: `ARCHIVE_STORAGE_DATA_RETRIEVAL_USAGE_HISTORY` (`BYTES`, `ARCHIVE_STORAGE_TIER`; 12 months). Frequent retrieval from cold → the tier does not fit the access pattern. Prices differ per tier: leave unpriced without a rate.

### S10. Backups and snapshots
- `BACKUP_SETS`, `BACKUP_STORAGE_USAGE` (`SNAPSHOT_*` deprecated). Bytes repeat across sets: never sum `LOGICAL_BYTES` as storage or as the saving from deleting a set; use `INCREMENTAL_BYTES_FROM_PREVIOUS_BACKUP` for growth.
