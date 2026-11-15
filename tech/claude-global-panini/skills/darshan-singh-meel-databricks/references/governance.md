# Governance and access

## Rules
- `information_schema` is **privilege-aware**: it lists only objects and grants the caller can see. Even an admin-run inventory is "what this principal sees"; for one object, `SHOW GRANTS ON TABLE <catalog>.<schema>.<table>` is the authoritative read.
- `system.information_schema` spans all catalogs of the metastore; `<catalog>.information_schema` only that catalog.
- `table_privileges` includes inherited grants (`inherited_from` set); catalog and schema privilege views do not say so → dedupe table rows already covered by a catalog or schema grant when counting "own" grants.
- Readers need `USE CATALOG` + `USE SCHEMA` + `SELECT`; a grant without the `USE` chain does nothing.
- `access.audit` (Public Preview): `service_name`, `action_name`, `request_params` (map), `response.status_code` (check: `DESCRIBE system.access.audit`; the docs example shows `statusCode`), `user_identity.email`, `identity_metadata.run_by` / `run_as`; account events have `workspace_id = '0'`. Filter on `event_date`. Some `request_params` keys are hidden unless account admin or in `databricks_pii_access`. Action names vary by service and release → list them before filtering (G4 step 1).
- Unity Catalog `getTable`-style audit events are metadata lookups (browsing fires them), not proof of a data read; data reads → lineage.
- `data_classification.results` holds detections only (`class_tag IS NOT NULL`); no row ≠ scanned and clean.
- Identities, IPs, emails are people's data → aggregate or mask in outputs; masked values need an unmasked key (hash) or two people collide.

## Questions
### G1 Who can access table X?
```sql
SELECT grantee, privilege_type, inherited_from, is_grantable, grantor
FROM system.information_schema.table_privileges
WHERE table_catalog = :catalog AND table_schema = :schema AND table_name = :table
ORDER BY grantee, privilege_type;
```
- Add catalog and schema grants (`catalog_privileges`, `schema_privileges`) and group membership (not in system tables: account console or SCIM API). Confirm with `SHOW GRANTS ON TABLE`.

### G2 Broad grants (all users)
- Grants in `catalog_privileges`, `schema_privileges`, `table_privileges` whose `grantee` is the built-in all-users group (`account users`; check: exact principal name on the account, matched case-insensitively), and `ALL PRIVILEGES` or `MODIFY` to large groups.

### G3 Grants to individual users instead of groups
- `grantee` containing `@` → a person; prefer groups. Service principals appear as application ids.

### G4 Permission changes in the last N days
```sql
-- 1) which actions exist
SELECT service_name, action_name, COUNT(*) AS events
FROM system.access.audit
WHERE event_date >= date_sub(current_date(), :days) AND service_name = 'unityCatalog'
GROUP BY ALL ORDER BY events DESC;
-- 2) the grant changes
SELECT event_time, workspace_id, sha2(concat(:k, user_identity.email), 256) AS actor_key, action_name,
       request_params['securable_type'] AS securable_type, request_params['securable_full_name'] AS securable,
       response.status_code
FROM system.access.audit
WHERE event_date >= date_sub(current_date(), :days) AND service_name = 'unityCatalog'
  AND action_name = 'updatePermissions'          -- check: action and key names from step 1
ORDER BY event_time DESC LIMIT 500;
```
- Read: `actor_key` = keyed hash (`k=PII_KEY`, system-tables.md people's data). Use an allow-list of actions, never "everything under the service" (reads and token vending share services).

### G5 Who read a sensitive table?
- Sensitive = `information_schema.table_tags` / `column_tags` with a sensitivity tag, or a `data_classification.results` row; readers = L1 (lineage) on those tables, grouped by the keyed hash of `created_by` (L1), excluding the owner and admin groups.

### G6 Classified columns without a mask
```sql
SELECT r.catalog_name, r.schema_name, r.table_name, r.column_name, r.class_tag
FROM system.data_classification.results r
LEFT JOIN system.information_schema.column_masks m
  ON m.catalog_name = r.catalog_name AND m.schema_name = r.schema_name
 AND m.table_name = r.table_name AND m.column_name = r.column_name
WHERE r.class_tag IS NOT NULL AND m.column_name IS NULL;
```
- Pitfall: `column_masks` and `row_filters` use `catalog_name`, `schema_name`, `table_name`, unlike most `information_schema` views (`table_catalog`, `table_schema`).

### G7 Masks and row filters inventory
- `information_schema.column_masks` (`column_name`, `mask_catalog`, `mask_schema`, `mask_name`, `mask_col_usage` = comma-separated extra columns) and `row_filters` (`filter_catalog`, `filter_schema`, `filter_name`, `filter_col_usage`); ABAC policies: `information_schema` policy views where enabled (check: ABAC page).

### G8 Tag coverage (owner, cost center, sensitivity)
- `information_schema.tables` LEFT JOIN `table_tags` on the three name columns for one `tag_name`; untagged share per catalog. Tag keys are case-sensitive: list distinct `tag_name` first.

### G9 Failed or denied access attempts
- `access.audit` with `response.status_code IN (401, 403)` (check: field name, see Rules) grouped by `service_name`, `action_name`, actor (masked) and day; a spike after a grant change points to it.

### G10 Logins and token use
- `access.audit` events of the accounts / token services (list actions as in G4 step 1; check: audit log reference for login and token action names), grouped by `user_agent`, day and `source_ip_address` (IP is people's data → count distinct only).

### G11 Who acts as someone else (run-as)
- `identity_metadata.run_by <> identity_metadata.run_as` in `access.audit`: humans running as service principals is normal for jobs; a service principal acting as a more privileged human is the case to look at. Volume alone is not escalation.

### G12 Delta Sharing exposure
- `information_schema.shares`, `share_recipient_privileges`, `table_share_usage` (check: views present on the metastore): what is shared, to whom, and whether sensitive tables (G5) are in a share.

### G13 Network policy denials
```sql
SELECT event_time, workspace_id, policy_outcome, rule_label, request_path
FROM system.access.inbound_network
WHERE event_time >= date_sub(current_date(), :days) AND policy_outcome = 'DENY'
ORDER BY event_time DESC LIMIT 500;
```
- The table holds denials only: `DENY` = blocked, `DENY_DRY_RUN` = a dry-run policy would have blocked it (count it separately before enforcing). Latency ≤ 1 h.
- Outbound: `access.outbound_network` (`destination_type`, `destination`, `access_type`) for serverless egress denials.

### G14 Owners of objects
- `information_schema.tables.table_owner`, `schemata.schema_owner`, `catalogs.catalog_owner`; objects owned by people who left → transfer to a group.

### G15 Workspaces in the account
- `access.workspaces_latest` (`workspace_id, workspace_name, workspace_url, status`); billed workspace ids missing here → deleted or outside the account view. Keep cost queries independent of this table (Public Preview).

## Build rules (Unity Catalog)
- Three-level names `catalog.schema.table`; no DBFS mounts or hard-coded workspace paths.
- Catalog per environment (e.g. `dev`, `prod`) or per domain: follow the project.
- Grants to groups: `GRANT SELECT ON SCHEMA prod.sales TO \`analysts\``, plus `USE CATALOG` and `USE SCHEMA` for readers.
- Jobs run as service principals, not personal accounts (`jobs-pipelines.md` J13).
- Cloud storage through storage credentials and external locations; no access keys in code.
- Row filters and column masks for sensitive data; cluster policies to limit size and cost (`compute.md` K3).
- Secrets from secret scopes (`dbutils.secrets.get()`) or app resources; names only in code and docs.
