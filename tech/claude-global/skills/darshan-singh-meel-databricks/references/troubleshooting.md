# Troubleshooting

Symptom → likely cause → the check. Run the visibility probe (system-tables.md Q0) before any of these.

## Results look empty or wrong
| Symptom | Likely cause | Check |
|---|---|---|
| Query returns 0 rows | schema not enabled, no grant, other region, window beyond retention, latency | Q0; `MIN`/`MAX` of the time column; region of the querying workspace |
| `SCHEMA_NOT_FOUND`, "not enabled" | system schema off for the metastore | account admin enables it (check: enable system tables page) |
| `TABLE_OR_VIEW_NOT_FOUND` | table not released on the account or invisible | Q0; Public Preview tables can be absent |
| `INSUFFICIENT_PERMISSIONS` | missing `USE CATALOG system` / `USE SCHEMA` / `SELECT` | `SHOW GRANTS ON SCHEMA system.<schema>` |
| One missing table fails a UNION of many | the engine resolves every table before running | one statement per source |
| Regex matches nothing in a notebook | Python ate the backslashes (`'\\b'` sent as backspace) | `q(r"""…""")` |
| `UNSUPPORTED_FEATURE.LATERAL_COLUMN_ALIAS_IN_GROUP_BY` | a select alias used in another expression with `GROUP BY ALL` | repeat the expression or name the GROUP BY columns |
| Dropped tables show as live | `table_dropped_time IS NULL` or `delete_time IS NULL` in WHERE, before the latest-row QUALIFY | put it after the QUALIFY |
| `statement_text` is `<REDACTED>` | caller not account admin nor in `databricks_pii_access` | group by `statement_id`, or ask for the group |
| Identities `__REDACTED__` | FedRAMP workspace | aggregate without identity |
| Serving tables empty | account admins only; usage tracking off | grant/role; endpoint setting |
| Today's numbers too low | ingestion latency (billing ≤ 12 h, most others ≤ 1 h) | cut at `current_date()` |
| Lineage misses a reader | not inferable, path-based, JDBC, other region | match `source_path`; query history text |
| Job durations are 0 | multi-task runs leave run-level phase columns 0 | task timeline or wall clock |
| Job has no name | `SUBMIT_RUN` / `WORKFLOW_RUN` have no `jobs` row | label as one-time run |
| Cluster missing for billed usage | deleted before 2023-10-23, or serverless | keep the id, label "not in clusters" |
| Old rows have NULL in new columns | column added later (e.g. Dec 2025) | treat NULL as "not reported" |
| Weekday off by one | `dayofweek()` is Sunday=1 | `weekday(d)` → Monday=0 |
| Regex error on `[` | Java regex | escape: `'\\['` |

## Totals do not match
| Symptom | Likely cause | Check |
|---|---|---|
| Dollars higher than the invoice | list price, not contract rate | label as list estimate |
| Dollars ≠ usage dashboard | promotions (`effective_list` vs `default`), corrections, UTC days | same price column, all record types, UTC |
| Cost doubled after a join | SCD table without latest-row filter; entities per endpoint; price rows overlap | `COUNT(*)` before and after each join |
| Sum of tag rows > total | rows with several tags counted per tag | one key at a time; tagged + untagged = total |
| Statement costs < warehouse cost | idle and start-up time belong to no statement | show the remainder as idle |
| Job total < SKU total for jobs | jobs on all-purpose clusters carry no `job_id`; rows without `job_run_id` dropped | cost C3 vs C4 |
| Trend jumps at window start | window longer than history or retention | `MIN(usage_date)` vs window start |
| Negative day | retraction landed without its restatement yet | net by original period; recheck next day |

## Platform issues (diagnose with the queries named)
- **Job suddenly slow:** jobs J5 → task J7 (setup vs execution) → compute K4 (memory pressure) → performance P1/P2 for its SQL (`query_source.job_info.job_id`).
- **Warehouse slow at 9 am:** compute K8 (queued vs cold start) → K6 config → jobs J15 (batch load overlapping BI).
- **Warehouse never stops:** compute K7 idle vs busy; activity outside query history (API or catalog calls) keeps it up → `access.audit` for the warehouse id between the last statement and the stop.
- **Job fails with cluster errors:** J3 `CLUSTER_ERROR`/`DRIVER_ERROR` → instance availability (`compute.instance_events`), pools, quotas; failed starts = task final row failed with setup time and no execution time.
- **Out of memory:** K4 swap and memory peak; P2 spill; skew (P6) on the failing stage in the Spark UI.
- **Permission denied for a job:** J3 `UNAUTHORIZED_ERROR` → G1 grants for the job's `run_as`; G4 recent grant changes.
- **Predictive optimization not running:** P11 `FAILED: PRIVATE_LINK_SETUP_ERROR` (storage firewall), table external, PO disabled on catalog (P12).
- **Streaming from system tables breaks:** stream > 7 days behind (7-day VACUUM); set `skipChangeCommits = true` (check: system tables page for the minimum runtime).
