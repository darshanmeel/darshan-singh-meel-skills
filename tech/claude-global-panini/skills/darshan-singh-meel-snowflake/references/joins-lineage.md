# Joins, column usage, dependencies and lineage

## Which source answers what
| Question | Source | Limits |
|---|---|---|
| Exact join condition of a query (`a.id = b.a_id`) | `GET_QUERY_OPERATOR_STATS` → `Join.operator_attributes:equality_join_condition` | 14 days, one query per call, `OPERATE`/`MONITOR` on the warehouse |
| Which columns of a table queries join or filter on, and how often | `COLUMN_QUERY_PRUNING_HISTORY` (`ACCESS_TYPE` `WHERE` / `JOIN`) | only queries that scanned micro-partitions; no GROUP BY / SELECT columns; no hybrid tables; 4 h lag |
| Which tables and columns a query read | `ACCESS_HISTORY.BASE_OBJECTS_ACCESSED` (underlying tables) and `DIRECT_OBJECTS_ACCESSED` (what the SQL named, such as a view) | Enterprise; successful queries only; no AU reads, no `RESULT_SCAN`; 3 h lag, 365 days |
| Which tables were joined together | `ACCESS_HISTORY` objects' `joinObjects` (`joinObject`, `type`) | object level only, no columns; `joinObjects` sits in the objects of `base_objects_accessed`, `direct_objects_accessed` and `objects_modified` |
| Column lineage (target column built from source columns) | `ACCESS_HISTORY.OBJECTS_MODIFIED[].columns[].baseSources` / `directSources` | writes only; a WHERE-only column is not a source |
| Declared dependencies (view on table, MV, dynamic table, UDF) | `OBJECT_DEPENDENCIES` | no CTAS/INSERT/MERGE pipelines; backfilled from 2022-01-22; `REFERENCED_OBJECT_ID` NULL for shared objects |
| DDL history of an object | `ACCESS_HISTORY.OBJECT_MODIFIED_BY_DDL` (`operationType`, `objectDomain`, `objectId`) | Enterprise; `operationType`: ALTER, CREATE, DESCRIBE, DROP, REPLACE, UNDROP, REFRESH, SHOW, SUSPEND, RESUME, GRANT, REVOKE |
- `ACCESS_HISTORY` JSON: objects have `objectDomain`, `objectId` (unique only within its domain: match both), `objectName`, `columns[]` (`columnId`, `columnName`); modified columns add `baseSources[]` / `directSources[]` (same object fields + `columnName`). Upper-case names before comparing.
- A query that reads and writes the same table (MERGE, `INSERT ... SELECT` from itself) shows it as both read and write; drop the read for usage counts.

## Catalogue

### J1. Join columns per table
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT MAX(database_name || '.' || schema_name || '.' || table_name) AS table_fqn, column_name,
       SUM(num_queries) AS queries, COUNT(DISTINCT query_parameterized_hash) AS query_shapes,
       COUNT(DISTINCT warehouse_id) AS warehouses
FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMN_QUERY_PRUNING_HISTORY, p
WHERE access_type = 'JOIN'
  AND interval_start_time >= DATEADD(day, -p.days, p.end_date) AND interval_start_time < p.end_date
GROUP BY table_id, column_name
ORDER BY queries DESC
LIMIT 100;
```
- Read: the columns other tables join on = the table's real keys; a column joined by many shapes is an interface: changing its type or meaning breaks those queries. Swap to `access_type = 'WHERE'` for filter columns.
- Pitfall: a join answered without scanning partitions (cached, metadata-only) is not counted.

### J1b. Query shapes that join one table, with a sample query each (feeds J2)
```sql
WITH p AS (SELECT 13 AS days, CURRENT_DATE() AS end_date, 'DB.SCHEMA.TABLE' AS fqn),
t AS (SELECT table_id FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES, p
      WHERE table_catalog || '.' || table_schema || '.' || table_name = p.fqn AND deleted IS NULL),
s AS (
  SELECT c.query_parameterized_hash AS shape, SUM(c.num_queries) AS queries,
         ARRAY_AGG(DISTINCT c.column_name) AS join_columns
  FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMN_QUERY_PRUNING_HISTORY c, p
  WHERE c.access_type = 'JOIN' AND c.table_id IN (SELECT table_id FROM t)
    AND c.interval_start_time >= DATEADD(day, -p.days, p.end_date) AND c.interval_start_time < p.end_date
  GROUP BY 1
),
h AS (
  SELECT qh.query_parameterized_hash AS shape, MAX_BY(qh.query_id, qh.execution_time) AS sample_query_id
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh, p
  WHERE qh.execution_status = 'SUCCESS'
    AND qh.start_time >= DATEADD(day, -p.days, p.end_date) AND qh.start_time < p.end_date
    AND qh.query_parameterized_hash IN (SELECT shape FROM s)
  GROUP BY 1
)
SELECT s.shape, s.queries, s.join_columns, h.sample_query_id
FROM s JOIN h ON h.shape = s.shape
ORDER BY s.queries DESC
LIMIT 20;
```
- Read: one row per query shape that joined on the table; `join_columns` = this table's side of the join; `sample_query_id` goes into J2 for the full condition, and the user opens its text in Snowsight.
- Pitfall: 13 days keeps the samples inside operator stats' 14 days; shapes without a successful `QUERY_HISTORY` row in the window drop out.

### J2. Exact join conditions of the heaviest queries (notebook, two cells, each with its note)
Cell 1 (for one table, use J1b's `sample_query_id` instead):
```python
ids = q("""
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT query_id
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
  AND execution_status = 'SUCCESS'
  AND query_type IN ('SELECT', 'INSERT', 'MERGE', 'CREATE_TABLE_AS_SELECT')
ORDER BY execution_time DESC
LIMIT 20
""")["QUERY_ID"].tolist()
```
Cell 2:
```python
import snowflake.connector.errors as sf_err

found, not_visible = [], []
for i in ids:
    try:
        found.append(q("""
SELECT query_id, operator_id, operator_type,
       operator_attributes:join_type::STRING AS join_type,
       operator_attributes:equality_join_condition::STRING AS equality_condition,
       operator_attributes:additional_join_condition::STRING AS extra_condition,
       operator_statistics:input_rows::NUMBER AS input_rows,
       operator_statistics:output_rows::NUMBER AS output_rows
FROM TABLE(GET_QUERY_OPERATOR_STATS(%s))
WHERE operator_type IN ('Join', 'CartesianJoin')
""", (i,)))
    except sf_err.ProgrammingError:
        not_visible.append(i)
joins = pd.concat(found) if found else pd.DataFrame()
print("not visible:", len(not_visible))
joins
```
- Read: one row per join operator; the condition text names table aliases and columns as written in the plan. Group by `equality_condition` to see the same join across queries; `output_rows` ≫ `input_rows` → fan-out.
- Pitfall: 14-day limit; queries on warehouses the role cannot `MONITOR` raise an error: caught per id and listed in `not_visible` (not assessed, not "no joins"). The function takes a literal, a session variable or `LAST_QUERY_ID()` only, so it is called once per id. Snowflake Notebook: placeholders are `?`, not `%s`. The condition can name internal aliases; map them with the `TableScan` operators' `table_name` / `table_alias` of the same query.

### J3. Who reads a table, and through what
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date, 'DB.SCHEMA.TABLE' AS fqn)
SELECT ah.user_name, d.value:objectName::STRING AS named_in_same_query, d.value:objectDomain::STRING AS named_domain,
       COUNT(DISTINCT ah.query_id) AS queries, MAX(ah.query_start_time) AS last_read
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p,
     LATERAL FLATTEN(input => ah.base_objects_accessed) b,
     LATERAL FLATTEN(input => ah.direct_objects_accessed) d
WHERE UPPER(b.value:objectName::STRING) = p.fqn
  AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
GROUP BY 1, 2, 3
ORDER BY queries DESC
LIMIT 200;
```
- Read: `named_in_same_query` = an object the SQL named in a query that read the table; a view here may be how the table is reached.
- Pitfall: the double FLATTEN pairs every base object with every direct object of the same query: a pairing, not a path; confirm with J7. A query that names the table and an unrelated view lists that view too. For "through which view", add `AND UPPER(d.value:objectDomain::STRING) IN ('VIEW', 'MATERIALIZED VIEW')`. Count `DISTINCT query_id`. Users are personal data.

### J4. Which columns of a table are read, and which never
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date, 'DB.SCHEMA.TABLE' AS fqn),
used AS (
  SELECT c.value:columnId::NUMBER AS column_id, COUNT(DISTINCT ah.query_id) AS queries,
         MAX(ah.query_start_time) AS last_read
  FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p,
       LATERAL FLATTEN(input => ah.base_objects_accessed) b,
       LATERAL FLATTEN(input => b.value:columns) c
  WHERE UPPER(b.value:objectName::STRING) = p.fqn
    AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
  GROUP BY 1
)
SELECT col.column_name, col.data_type, COALESCE(u.queries, 0) AS queries, u.last_read
FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMNS col
CROSS JOIN p
LEFT JOIN used u ON u.column_id = col.column_id
WHERE col.table_catalog || '.' || col.table_schema || '.' || col.table_name = p.fqn AND col.deleted IS NULL
ORDER BY queries;
```
- Read: `queries = 0` over 90 days = no successful query read the column (candidate to drop, after checking J7 views and jobs outside Snowflake that may run rarely).
- Pitfall: `SELECT *` marks every column as read; columns used only in a WHERE clause count as accessed for reads. check: access_history (whether WHERE-only columns of a SELECT are listed).

### J5. Tables read together (co-access pairs)
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
o AS (
  SELECT DISTINCT ah.query_id, UPPER(b.value:objectName::STRING) AS obj
  FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p,
       LATERAL FLATTEN(input => ah.base_objects_accessed) b
  WHERE UPPER(b.value:objectDomain::STRING) = 'TABLE'
    AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
)
SELECT a.obj AS table_a, b.obj AS table_b, COUNT(*) AS queries
FROM o a JOIN o b ON a.query_id = b.query_id AND a.obj < b.obj
GROUP BY 1, 2
ORDER BY queries DESC
LIMIT 100;
```
- Read: pairs read in the same query, usually joined (or unioned). Combine with J1 for the join columns of each side.
- Pitfall: compare `objectDomain` upper-cased. A query reading 20 tables makes 190 pairs: cap with `HAVING` or filter to one table.

### J6. Column lineage: where does a column come from?
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date, 'DB.SCHEMA.TARGET' AS fqn)
SELECT UPPER(c.value:columnName::STRING) AS target_column,
       UPPER(s.value:objectName::STRING) AS source_object, UPPER(s.value:columnName::STRING) AS source_column,
       COUNT(DISTINCT ah.query_id) AS writes, MAX(ah.query_start_time) AS last_write
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p,
     LATERAL FLATTEN(input => ah.objects_modified) m,
     LATERAL FLATTEN(input => m.value:columns) c,
     LATERAL FLATTEN(input => c.value:baseSources, OUTER => TRUE) s
WHERE UPPER(m.value:objectName::STRING) = p.fqn
  AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
GROUP BY 1, 2, 3
ORDER BY 1, writes DESC;
```
- Read: `source_object` NULL = the column was written from a literal, a stage or a function, not from a table column. Reverse it (downstream) by filtering `s.value:objectName = <source>`.
- Pitfall: copies through a stage or an external tool break the chain; only the window's writes are seen (a monthly job needs a 35+ day window).

### J7. What breaks if I drop or change this object (declared dependents, recursive)
```sql
WITH RECURSIVE edges AS (
  SELECT referenced_object_id AS src_id, referenced_object_domain AS src_domain,
         referencing_object_id AS dep_id, referencing_object_domain AS dep_domain,
         referencing_database || '.' || referencing_schema || '.' || referencing_object_name AS dep_fqn
  FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
),
reach (dep_id, dep_domain, dep_fqn, depth) AS (
  SELECT dep_id, dep_domain, dep_fqn, 1 FROM edges
  WHERE src_domain = 'TABLE'
    AND src_id = (SELECT table_id FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
                  WHERE table_catalog || '.' || table_schema || '.' || table_name = 'DB.SCHEMA.TABLE'
                    AND deleted IS NULL)
  UNION ALL
  SELECT e.dep_id, e.dep_domain, e.dep_fqn, r.depth + 1
  FROM reach r JOIN edges e ON e.src_id = r.dep_id AND e.src_domain = r.dep_domain
  WHERE r.depth < 10
)
SELECT dep_fqn, dep_domain, MIN(depth) AS depth
FROM reach
GROUP BY 1, 2
ORDER BY depth, dep_fqn
LIMIT 1000;
```
- Read: every view, MV, dynamic table and function that would break, by distance. Then add the pipelines: writers and readers from J3/J6, and tasks or dynamic tables that read it (`pipelines.md` L6).
- Pitfall: role-filtered for objects; a view's dependency on a dropped and recreated table by name stays `BY_NAME`; IDs are unique only within a domain, so every step matches `src_domain` too; for a view as the start, anchor on `src_domain = 'VIEW'`. `TABLES` only resolves tables and views: for a function source, use `FUNCTIONS.FUNCTION_ID`.

### J8. What breaks if I change one column
Two answers, each 1-4 queries:
- **Who uses the column:** 1) queries that read it: J4 (`queries`, last read, users); 2) columns built from it: J6 reversed; 3) join and filter use: J1 (with `access_type`); 4) masking or row policies on it: `security.md` X9.
- **Objects that may break:** J7. J7 lists dependents of the table; it cannot say which use the column. Open each definition in Snowsight, or rank them by ACCESS_HISTORY queries whose `direct_objects_accessed` holds the view and whose `base_objects_accessed` holds the column.
- Report each list with its window and lag; anything outside Snowflake (BI extracts, exports) is invisible here.

### J9. Unused tables and views
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date),
r AS (
  SELECT b.value:objectId::NUMBER AS object_id, MAX(ah.query_start_time) AS last_read
  FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p,
       LATERAL FLATTEN(input => ARRAY_CAT(COALESCE(ah.direct_objects_accessed, []),
                                          COALESCE(ah.base_objects_accessed, []))) b
  WHERE UPPER(b.value:objectDomain::STRING) IN ('TABLE', 'VIEW', 'MATERIALIZED VIEW', 'EXTERNAL TABLE', 'DYNAMIC TABLE')
    AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
  GROUP BY 1
)
SELECT t.table_catalog || '.' || t.table_schema || '.' || t.table_name AS fqn, t.table_type,
       t.bytes / POWER(1024, 3) AS gb, t.created, t.last_ddl, r.last_read
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES t
CROSS JOIN p
LEFT JOIN r ON r.object_id = t.table_id
WHERE t.deleted IS NULL AND t.created < DATEADD(day, -p.days, p.end_date) AND r.object_id IS NULL
ORDER BY gb DESC NULLS LAST
LIMIT 200;
```
- Read: not read by any successful query in 90 days, neither named in the SQL nor read through a view (both arrays). The domain filter keeps IDs of other domains from matching a table id. Before dropping: J7 (other objects depend on it?), writes (J6 target = it), shares (`security.md` X13).
- Pitfall: ACCESS_HISTORY needs Enterprise; reads by provider-side share consumers are not visible to the consumer, and vice versa.

### J10. Broken views (dependency on a dropped object)
```sql
SELECT d.referencing_database || '.' || d.referencing_schema || '.' || d.referencing_object_name AS view_fqn,
       d.referenced_database || '.' || d.referenced_schema || '.' || d.referenced_object_name AS missing_source
FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES d
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TABLES t ON t.table_id = d.referenced_object_id AND t.deleted IS NULL
WHERE d.referenced_object_domain IN ('TABLE', 'VIEW') AND d.referenced_object_id IS NOT NULL
  AND t.table_id IS NULL;
```
- Read: views whose source no longer exists under that id. Confirm with `DESCRIBE VIEW <fqn>` before reporting it broken (recreated sources, shared objects).
- Pitfall: `REFERENCED_OBJECT_ID` NULL for shared objects (excluded); domain strings may differ by kind (`MATERIALIZED VIEW`, `DYNAMIC TABLE`).

### J11. DDL timeline of an object
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date)
SELECT ah.query_start_time, ah.user_name,
       ah.object_modified_by_ddl:operationType::STRING AS operation,
       ah.object_modified_by_ddl:objectDomain::STRING AS domain,
       ah.object_modified_by_ddl:objectName::STRING AS object_name, ah.query_id
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p
WHERE ah.object_modified_by_ddl IS NOT NULL
  AND UPPER(ah.object_modified_by_ddl:objectName::STRING) LIKE '%<TABLE>%'
  AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
ORDER BY ah.query_start_time DESC
LIMIT 200;
```
- Read: who created, altered, replaced or dropped it and when; `properties` holds the changed settings; `operationType` values are in the table above.
