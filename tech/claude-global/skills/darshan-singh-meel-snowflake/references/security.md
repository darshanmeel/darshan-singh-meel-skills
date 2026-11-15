# Security and access

## Facts
- Grant views keep revoked rows: live grants need `DELETED_ON IS NULL`. A re-grant adds a new row. `GRANTS_TO_ROLES` skips grants on dropped objects; an empty `GRANTED_BY` = granted by the system.
- Role tree: `GRANTS_TO_ROLES` rows with `GRANTED_ON IN ('ROLE', 'DATABASE_ROLE') AND PRIVILEGE = 'USAGE'`: `NAME` = role granted (child), `GRANTEE_NAME` = role that inherits it (parent). `GRANTED_TO` reads `'ROLE'` or `'ACCOUNT ROLE'`: match both. check: grants_to_roles.
- `ROLES` also lists database, application and instance roles (`ROLE_TYPE`).
- `USERS`: `TYPE` (`PERSON`, `SERVICE`, `LEGACY_SERVICE`, NULL); service users have NULL password and MFA columns. `DISABLED` is VARIANT. MFA: `HAS_MFA`, `EXT_AUTHN_DUO`, and `CREDENTIALS` rows with `DOMAIN = 'MFA_METHOD'`. `LAST_SUCCESS_LOGIN` covers 1 year. check: users (`TYPE` values).
- `LOGIN_HISTORY.IS_SUCCESS` is `'YES'`/`'NO'`; `USER_NAME` can be NULL on early failures; `FIRST_AUTHENTICATION_FACTOR` / `SECOND_AUTHENTICATION_FACTOR` show password, key pair, SSO, OAuth, PAT and MFA use.
- `POLICY_REFERENCES` lists masking, row access, aggregation, projection, network and some other kinds; not authentication, password or session policies (use `SHOW ... POLICIES` and `INFORMATION_SCHEMA.POLICY_REFERENCES(REF_ENTITY_DOMAIN => 'USER' | 'ACCOUNT', ...)`). Role-filtered.
- `NETWORK_POLICIES` does not show attachment: account level = `SHOW PARAMETERS LIKE 'NETWORK_POLICY' IN ACCOUNT`; users = `POLICY_REFERENCES` (`POLICY_KIND = 'NETWORK_POLICY'`). Rules attached via `NETWORK_RULE_REFERENCES` are not in `ALLOWED_IP_LIST`.
- `TAG_REFERENCES`: direct assignments only (tag inheritance from schema or database is not expanded): for effective tags of one object use `TABLE(<db>.INFORMATION_SCHEMA.TAG_REFERENCES('<fqn>', 'table'))`.

## Catalogue

### X1. Who holds admin roles
```sql
SELECT g.role, g.grantee_name AS user_name, u.type, u.has_mfa, u.last_success_login, g.created_on
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS g
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON u.name = g.grantee_name AND u.deleted_on IS NULL
WHERE g.deleted_on IS NULL AND g.role IN ('ACCOUNTADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN', 'ORGADMIN', 'GLOBALORGADMIN')
ORDER BY g.role, user_name;
```
- Read: direct holders only; people who reach admin through a custom role need X2. More than 2-3 `ACCOUNTADMIN` holders, holders without MFA, or service users with admin → risk.

### X2. Role hierarchy: every role a user ends up with
```sql
WITH RECURSIVE edges AS (
  SELECT name AS child, grantee_name AS parent
  FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
  WHERE deleted_on IS NULL AND privilege = 'USAGE' AND granted_on = 'ROLE'
    AND granted_to IN ('ROLE', 'ACCOUNT ROLE')
),
user_roles AS (
  SELECT grantee_name AS user_name, role FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
  WHERE deleted_on IS NULL AND grantee_name = '<USER>'
),
reach (user_name, role, path, depth) AS (
  SELECT user_name, role, role::VARCHAR, 0 FROM user_roles
  UNION ALL
  SELECT r.user_name, e.child, r.path || ' > ' || e.child, r.depth + 1
  FROM reach r JOIN edges e ON e.parent = r.role
  WHERE r.depth < 15
)
SELECT role, MIN(depth) AS depth, MIN_BY(path, depth) AS shortest_path
FROM reach GROUP BY role ORDER BY depth, role;
```
- Read: every account role the user inherits, with one path. For "who can reach role R", reverse the walk (start from R, follow `child = role` up to parents, then `GRANTS_TO_USERS`).
- Pitfall: database roles live under a database (`NAME` may lack the database prefix); this walk covers account roles only.

### X3. Who can read this table (privilege paths)
```sql
WITH RECURSIVE edges AS (
  SELECT name AS child, grantee_name AS parent
  FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
  WHERE deleted_on IS NULL AND privilege = 'USAGE' AND granted_on = 'ROLE' AND granted_to IN ('ROLE', 'ACCOUNT ROLE')
),
direct AS (
  SELECT DISTINCT grantee_name AS role
  FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
  WHERE deleted_on IS NULL AND granted_on IN ('TABLE', 'VIEW') AND privilege IN ('SELECT', 'OWNERSHIP')
    AND table_catalog = '<DB>' AND table_schema = '<SCHEMA>' AND name = '<TABLE>'
),
up (role, depth) AS (
  SELECT role, 0 FROM direct
  UNION ALL
  SELECT e.parent, u.depth + 1 FROM up u JOIN edges e ON e.child = u.role WHERE u.depth < 15
)
SELECT g.grantee_name AS user_name, MIN(up.depth) AS hops, ARRAY_AGG(DISTINCT up.role) AS via_roles
FROM up JOIN SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS g ON g.role = up.role AND g.deleted_on IS NULL
GROUP BY 1 ORDER BY hops, user_name;
```
- Read: users who hold SELECT through some role. Also needed: USAGE on the database and schema (same walk); future grants (`SHOW FUTURE GRANTS IN SCHEMA <db.schema>`) and `MANAGE GRANTS` holders can grant themselves access; masking and row policies (X9) can still hide rows or values.
- Pitfall: grants to database roles and shares are not followed here; `SELECT` on a view does not need SELECT on its base table (owner's rights).

### X4. Users without MFA
```sql
SELECT u.name, u.type, u.has_password, u.has_mfa, u.ext_authn_duo, u.has_rsa_public_key, u.last_success_login
FROM SNOWFLAKE.ACCOUNT_USAGE.USERS u
LEFT JOIN (SELECT DISTINCT user_name FROM SNOWFLAKE.ACCOUNT_USAGE.CREDENTIALS
           WHERE domain = 'MFA_METHOD' AND status IN ('ACTIVE', 'ENROLLED')) c ON c.user_name = u.name
WHERE u.deleted_on IS NULL AND NOT COALESCE(u.disabled::BOOLEAN, FALSE)
  AND COALESCE(u.type, 'PERSON') = 'PERSON' AND u.has_password
  AND NOT COALESCE(u.has_mfa, FALSE) AND NOT COALESCE(u.ext_authn_duo, FALSE) AND c.user_name IS NULL
ORDER BY u.last_success_login DESC NULLS LAST;
```
- Read: people who can log in with a password and have no MFA method. SSO-only users (no password) are covered by the identity provider's MFA.
- Pitfall: NULL `TYPE` behaves like a person; `CREDENTIALS` excludes Duo and deleted credentials.

### X5. Failed logins and new sources
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT COALESCE(user_name, '(unknown)') AS user_name, error_message, reported_client_type,
       COUNT(*) AS failures, COUNT(DISTINCT client_ip) AS ips, MAX(event_timestamp) AS last_failure
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY, p
WHERE is_success = 'NO'
  AND event_timestamp >= DATEADD(day, -p.days, p.end_date) AND event_timestamp < p.end_date
GROUP BY 1, 2, 3
ORDER BY failures DESC
LIMIT 50;
```
- Read: many failures from many IPs → password spraying; one service user failing all day → an expired key or rotated password in a job. Client IPs are personal data: count them, do not list them to the model.

### X6. How people and services authenticate
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT first_authentication_factor, second_authentication_factor, reported_client_type,
       COUNT(DISTINCT user_name) AS users, COUNT(*) AS logins
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY, p
WHERE is_success = 'YES'
  AND event_timestamp >= DATEADD(day, -p.days, p.end_date) AND event_timestamp < p.end_date
GROUP BY 1, 2, 3
ORDER BY logins DESC;
```
- Read: password logins without a second factor, and service users on password instead of key pair, OAuth or workload identity, are the ones to move.

### X7. Stale and dormant users
```sql
SELECT name, type, created_on, last_success_login, default_role
FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
WHERE deleted_on IS NULL AND NOT COALESCE(disabled::BOOLEAN, FALSE)
  AND (last_success_login < DATEADD(day, -90, CURRENT_TIMESTAMP())
       OR (last_success_login IS NULL AND created_on < DATEADD(day, -30, CURRENT_TIMESTAMP())))
ORDER BY last_success_login NULLS FIRST;
```
- Read: enabled users unused for 90 days (or never) → disable (user-run `ALTER USER`). Service users that run through key pair also update `LAST_SUCCESS_LOGIN`.

### X8. Network policy coverage
```sql
SHOW PARAMETERS LIKE 'NETWORK_POLICY' IN ACCOUNT;
```
```sql
SELECT ref_entity_name AS user_name, policy_name
FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES
WHERE policy_kind = 'NETWORK_POLICY' AND ref_entity_domain = 'USER';
```
- Read: no account-level value and service users without their own policy → reachable from any IP. Allowed lists: `NETWORK_POLICIES.ALLOWED_IP_LIST` plus rules in `NETWORK_RULE_REFERENCES`; `0.0.0.0/0` allows everyone.

### X9. Masking and row access policies per column and table
```sql
SELECT r.ref_database_name || '.' || r.ref_schema_name || '.' || r.ref_entity_name AS object_fqn,
       r.ref_column_name, r.policy_kind, r.policy_db || '.' || r.policy_schema || '.' || r.policy_name AS policy,
       r.tag_name, r.policy_status
FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES r
WHERE r.policy_kind IN ('MASKING_POLICY', 'ROW_ACCESS_POLICY')
ORDER BY 1, 2;
```
- Read: `tag_name` set = attached through a tag (tag-based masking). Columns tagged sensitive (X10) without a row here → unprotected. Never read `POLICY_BODY`.
- Pitfall: Enterprise; role-filtered; filter `policy_status = 'ACTIVE'` for effective ones.

### X10. Sensitive columns: tagged vs protected
```sql
WITH t AS (
  SELECT object_database || '.' || object_schema || '.' || object_name AS object_fqn, column_name, tag_name, tag_value
  FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
  WHERE domain = 'COLUMN' AND object_deleted IS NULL
    AND tag_name IN ('SEMANTIC_CATEGORY', 'PRIVACY_CATEGORY', '<YOUR_PII_TAG>')
),
m AS (
  SELECT ref_database_name || '.' || ref_schema_name || '.' || ref_entity_name AS object_fqn, ref_column_name AS column_name
  FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES WHERE policy_kind = 'MASKING_POLICY'
)
SELECT t.object_fqn, t.column_name, t.tag_name, t.tag_value, m.column_name IS NOT NULL AS masked
FROM t LEFT JOIN m ON m.object_fqn = t.object_fqn AND m.column_name = t.column_name
ORDER BY masked, t.object_fqn;
```
- Read: `masked = FALSE` on a privacy category → exposure. Tag inheritance is not expanded (see Facts).

### X11. Who read sensitive columns
- `joins-lineage.md` J4 per table, or ACCESS_HISTORY `base_objects_accessed[].columns[]` joined to X10's column list by `columnId` = `COLUMNS.COLUMN_ID`; `POLICIES_REFERENCED` shows which masking or row policy applied to each read. Count users and queries; do not list user names to the model.

### X12. Grant changes and privileged actions
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT start_time, user_name, role_name, query_type, query_id
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE query_type IN ('GRANT', 'REVOKE', 'CREATE_USER', 'ALTER_USER', 'DROP_USER', 'CREATE_ROLE', 'DROP_ROLE',
                     'ALTER_ACCOUNT', 'CREATE_NETWORK_POLICY', 'ALTER_NETWORK_POLICY')
  AND execution_status = 'SUCCESS'
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
ORDER BY start_time DESC
LIMIT 500;
```
- Read: who changed access and when; follow `query_id` in Snowsight for the statement. Also: role used for daily work - `role_name = 'ACCOUNTADMIN'` on SELECTs is a smell. check: query_history (`QUERY_TYPE` values).

### X13. Shares: what leaves the account
```sql
SELECT s.name AS share_name, s.target_accounts, g.privilege, g.granted_on,
       g.object_database || '.' || COALESCE(g.object_schema || '.', '') || g.object_name AS object
FROM SNOWFLAKE.ACCOUNT_USAGE.SHARES s
JOIN SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_SHARES g ON g.share_name = s.name AND g.deleted_on IS NULL
WHERE s.deleted_on IS NULL
ORDER BY 1, 5;
```
- Read: outbound shares and the objects in them; cross-check objects with X10. Inbound shares: `SHOW SHARES` (`kind = 'INBOUND'`). `TARGET_ACCOUNTS` is a comma-separated string. check: grants_to_shares (`SHARE_NAME` format may include the account prefix).

### X14. PUBLIC role and broad grants
```sql
SELECT granted_on, privilege, table_catalog, table_schema, name
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE deleted_on IS NULL AND grantee_name = 'PUBLIC' AND granted_on NOT IN ('ROLE')
ORDER BY 1, 3, 4, 5;
```
- Read: everything every user can reach. Also flag `GRANT_OPTION = TRUE` grants and `MANAGE GRANTS` held outside `SECURITYADMIN`.

### X15. Keys, tokens and secrets hygiene
- `CREDENTIALS` (`TYPE`, `STATUS`, `CREATED_ON`, `LAST_USED_ON`, `EXPIRATION_DATE`) for programmatic access tokens and passkeys: unused or never-expiring tokens → revoke. `USERS.HAS_RSA_PUBLIC_KEY` plus key age from `ALTER USER` history (X12). `SECRETS` lists secret objects (never values). Trust Center: `TRUST_CENTER_FINDINGS` (severity, state; details in `SNOWFLAKE.TRUST_CENTER.FINDINGS` with the Trust Center viewer role).
