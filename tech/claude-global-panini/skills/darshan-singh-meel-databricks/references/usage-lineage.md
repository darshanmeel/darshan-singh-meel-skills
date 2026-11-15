# Usage, joins, lineage, dependencies

## Rules
- `access.table_lineage`: one row per read or write event. Read-only = `source_type` set, `target_type` NULL; write-only = the reverse; both = read and write. `direct_access = false` = reached through a view.
- `access.column_lineage`: source column → target column; a column read is recorded whether or not the output is written; events with no source (literal inserts) are skipped. Join and filter keys may not appear as lineage when they do not flow into an output column (check: lineage page) → use EXPLAIN or the statement text for join columns.
- Coverage gaps: rows exist only when lineage can be inferred; path-based access carries `source_path`/`target_path` and no table name; JDBC or the sample-data tab have no entity (`entity_type` NULL). A table with no lineage reads is a **candidate** for unused, never proof.
- Entities: `entity_type` `NOTEBOOK`, `JOB`, `PIPELINE`, `DASHBOARD_V3`, `DBSQL_QUERY` (`DBSQL_DASHBOARD` deprecated); `entity_id` + `entity_run_id`; `entity_metadata.job_info.job_id`, `.dlt_pipeline_info.dlt_pipeline_id`, `.dashboard_id`, `.genie_space_id`, `.alert_id`.
- Lineage is regional and kept 395 days in system tables; older lineage (captured after 2024-09-01) only via Catalog Explorer or the lineage API.
- Filter on `event_date` (partition column) for speed.

## Questions
### L1 Who reads and writes table X?
```sql
SELECT entity_type, entity_id, sha2(concat(:k, created_by), 256) AS principal_key,
       CASE WHEN source_table_full_name = :table THEN 'reads' ELSE 'writes' END AS direction,
       COUNT(*) AS events, MAX(event_time) AS last_seen
FROM system.access.table_lineage
WHERE event_date >= date_sub(current_date(), :days)
  AND (source_table_full_name = :table OR target_table_full_name = :table)
GROUP BY ALL ORDER BY events DESC;
```
- Read: `principal_key` = one principal (keyed hash, `k=PII_KEY`; system-tables.md people's data); `entity_type` NULL → ad hoc or external client. Names stay in user-run notebooks, out of outputs Claude reads. Path-based tables: also match `source_path`/`target_path` (location from `DESCRIBE DETAIL`).

### L2 Downstream of table X (blast radius)
```sql
WITH RECURSIVE e AS (
  SELECT DISTINCT source_table_full_name AS src, target_table_full_name AS tgt
  FROM system.access.table_lineage
  WHERE event_date >= date_sub(current_date(), :days)
    AND source_table_full_name IS NOT NULL AND target_table_full_name IS NOT NULL
    AND source_table_full_name <> target_table_full_name),
down (tbl, hop) AS (
  SELECT tgt, 1 FROM e WHERE src = :table
  UNION ALL
  SELECT e.tgt, d.hop + 1 FROM down d JOIN e ON e.src = d.tbl WHERE d.hop < :max_hops)
SELECT tbl, MIN(hop) AS hops
FROM down GROUP BY tbl ORDER BY hops, tbl;
```
- `WITH RECURSIVE` needs Databricks SQL or Runtime 17.0+; depth limit 100 by default (`MAX RECURSION LEVEL`), result capped at 1,000,000 rows; `:max_hops` (e.g. 5) stops cycles early. Older runtime → the two-hop self-join (`e e1 LEFT JOIN e e2 ON e2.src = e1.tgt WHERE e1.src = :table`) or a loop in a Python cell.
- Pitfall: GROUP BY with NULL names pools every path-based edge into one fake node; keep NULL-named rows separate.

### L3 Which columns of table X are used downstream?
```sql
SELECT source_column_name, target_table_full_name, target_column_name, entity_type,
       COUNT(*) AS events, MAX(event_time) AS last_seen
FROM system.access.column_lineage
WHERE event_date >= date_sub(current_date(), :days) AND source_table_full_name = :table
GROUP BY ALL ORDER BY source_column_name, events DESC;
```
- Read: columns of X absent from the result (compare with `information_schema.columns`) are not used by any inferred flow in the window.

### L4 What breaks if I drop or rename column X.c?
Lineage first (it sees views owned by anyone), then the catalog, then query text. `:table` = full name, `:catalog`, `:schema`, `:table_name` its parts.
1. **Downstream columns, views and entities** (lineage):
```sql
SELECT target_type, target_table_full_name, target_column_name, entity_type, entity_id,
       COUNT(*) AS events, MAX(event_time) AS last_seen
FROM system.access.column_lineage
WHERE event_date >= date_sub(current_date(), :days)
  AND source_table_full_name = :table AND source_column_name = :column
GROUP BY ALL ORDER BY events DESC;
```
   - `target_type IN ('VIEW', 'MATERIALIZED_VIEW', 'METRIC_VIEW', 'STREAMING_TABLE')` → objects defined on the column; other rows → tables it feeds, and the jobs, pipelines, dashboards that do it.
   - Readers through views: `table_lineage` on `source_table_full_name = :table AND direct_access = false`, grouped by `entity_type, entity_id`.
2. **View text** (only views this principal owns; `view_definition` is NULL for the rest):
```sql
SELECT table_catalog, table_schema, table_name
FROM system.information_schema.views
WHERE view_definition ILIKE concat('%', :table_name, '%') AND view_definition ILIKE concat('%', :column, '%');
```
```sql
SELECT COUNT_IF(view_definition IS NULL) AS views_not_readable, COUNT(*) AS views_visible
FROM system.information_schema.views;
```
   - `views_not_readable > 0` → those views are unchecked by text: "not visible" ≠ "none"; rely on step 1 or the owners.
3. **Objects on the column itself** (one statement each):
   - Keys: `information_schema.key_column_usage` and `constraint_column_usage` on `table_catalog = :catalog AND table_schema = :schema AND table_name = :table_name AND column_name = :column` (primary and foreign keys, also from other tables).
   - Masks and row filters: `column_masks` and `row_filters` on `catalog_name = :catalog AND schema_name = :schema AND table_name = :table_name` (these two views use `catalog_name`, `schema_name`), where `column_name = :column` or the comma-separated `mask_col_usage` / `filter_col_usage` lists it (`array_contains(split(regexp_replace(mask_col_usage, ' ', ''), ','), :column)`); tags: `column_tags`.
   - Layout: `DESCRIBE DETAIL <table>` → `partitionColumns`, `clusteringColumns`; a dropped clustering or partition column breaks the table layout.
   - Shares: governance G12 views for the table.
4. **Ad hoc and BI SQL** (likely): `query.history` where `statement_text ILIKE` both the table and the column name in `:days`; output only `COUNT(*)`, `COUNT(DISTINCT executed_by)`, `client_application`, `query_source.dashboard_id` (needs text access).
- Answer as: breaks for sure (lineage, keys, masks, layout, readable views) · likely (query text) · cannot see (views owned by others, path-based, other regions, outside retention).

### L5 Which queries join tables A and B, and on which columns?
```sql
-- statements that read both tables, and their ON clauses (heuristic parse), counted per clause
WITH both_tables AS (
  SELECT workspace_id, statement_id
  FROM system.access.table_lineage
  WHERE event_date >= date_sub(current_date(), :days) AND statement_id IS NOT NULL
    AND source_table_full_name IN (:table_a, :table_b)
  GROUP BY workspace_id, statement_id
  HAVING COUNT(DISTINCT source_table_full_name) = 2),
ons AS (
  SELECT h.statement_id, h.query_source.dashboard_id AS dashboard_id, h.query_source.job_info.job_id AS job_id,
         explode(regexp_extract_all(regexp_replace(lower(h.statement_text), '\\s+', ' '),
           '\\bon (.+?)(?= (?:inner |left |right |full |cross )?(?:outer )?join\\b| where\\b| group\\b| order\\b| qualify\\b| limit\\b|$)', 1)) AS on_clause
  FROM system.query.history h
  JOIN both_tables b ON b.workspace_id = h.workspace_id AND b.statement_id = h.statement_id
  WHERE h.start_time >= date_sub(current_date(), :days) AND h.statement_text <> '<REDACTED>')
SELECT regexp_replace(on_clause, "'[^']*'|\\b\\d+\\b", '?') AS on_clause,
       COUNT(DISTINCT statement_id) AS statements, COUNT(DISTINCT dashboard_id) AS dashboards, COUNT(DISTINCT job_id) AS jobs
FROM ons GROUP BY 1 ORDER BY statements DESC LIMIT 100;
```
- Read: one row = one ON-clause shape (literals → `?`); whitespace is flattened first so clauses that end at a line break are kept. Heuristic: a clause can carry a trailing `)` from a subquery; `USING (col)` joins are not matched.
- In a notebook: `q(r"""…""")` (raw string), or Python turns `\\b` into a backspace and the regex matches nothing.
- Exact keys: run `EXPLAIN FORMATTED` on one statement's text; the plan names the join keys and strategy. Or open its query profile.
- Pitfall: lineage carries `statement_id` only for SQL warehouse and serverless statements; statements via views list base tables with `direct_access = false`; `<REDACTED>` text (no admin or `databricks_pii_access`) drops out.

### L6 Most used columns of a table (filter and group candidates)
- L3 counts per `source_column_name`, plus a text scan of `query.history` for `WHERE`/`GROUP BY` mentions of each column name; the top filter columns are clustering candidates (performance P10).

### L7 Tables nobody reads (cleanup candidates)
```sql
SELECT t.table_catalog, t.table_schema, t.table_name, t.table_type, t.table_owner, t.last_altered
FROM system.information_schema.tables t
LEFT JOIN (SELECT DISTINCT source_table_full_name FROM system.access.table_lineage
           WHERE event_date >= date_sub(current_date(), :days)) r
  ON r.source_table_full_name = concat_ws('.', t.table_catalog, t.table_schema, t.table_name)
WHERE r.source_table_full_name IS NULL AND t.table_catalog <> 'system'
  AND t.table_schema <> 'information_schema' AND t.table_type IN ('MANAGED', 'EXTERNAL');
```
- Read: candidates only; add size from `table_metrics_history` and writers from L1 (written but never read is the strongest signal). `information_schema` is privilege-aware: the list covers what the principal sees.

### L8 Which tables does job J read and write?
- `table_lineage` where `entity_type = 'JOB' AND entity_id = :job_id` (same `workspace_id`), grouped by source and target; join `entity_run_id` to `job_run_timeline.run_id` for the run's outcome.

### L9 Which jobs or pipelines produce table X, and are they healthy?
- L1 `writes` rows with `entity_type IN ('JOB','PIPELINE')` → latest run state from jobs-pipelines.md J2 / J11.

### L10 Which dashboards depend on table X?
- `table_lineage` `entity_type = 'DASHBOARD_V3'` on X, or `query.history` `query_source.dashboard_id` for statements reading X (L5 first query with one table).

### L11 Upstream of a table (where its data comes from)
- L2 reversed (`target_table_full_name = :table`, walk `src`); include `source_path` for files and external locations.

### L12 Dependencies inside a job
```sql
SELECT workspace_id, job_id, task_key, depends_on_keys, timeout_seconds
FROM system.lakeflow.job_tasks
WHERE workspace_id = :workspace_id AND job_id = :job_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id, task_key ORDER BY change_time DESC) = 1
  AND delete_time IS NULL;
```

### L13 Cross-workspace or cross-catalog use
- `table_lineage` grouped by `workspace_id` and `source_table_catalog`: a catalog read from many workspaces is shared; check bindings and grants (governance.md).
