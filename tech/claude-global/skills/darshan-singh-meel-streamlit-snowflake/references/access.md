# Privileges, session, rights, external access, secrets, sharing

- Role design (access roles → functional roles, future grants, service users): `darshan-singh-meel-data-platform` → `rbac.md`, `snowflake.md`.
- All SQL here goes in a setup script the user runs.
- Docs paths are under docs.snowflake.com/en/developer-guide/streamlit/.

## Roles
| Role | Holds |
|---|---|
| `<app>_owner` — dedicated, owns the app | Create privileges below + read-only access to exactly the data the app shows |
| `<app>_viewer` | `USAGE` on database, schema, app — nothing on the data |
| Deploy service user (CI) | `<app>_owner` only |

## Privileges
Docs: `object-management/privileges`

| To | Needs |
|---|---|
| Create | `USAGE` on database + schema · `CREATE STREAMLIT` on schema · `USAGE` on query warehouse · `USAGE` on compute pool (container) · `USAGE` on each external access integration (container: also to install from PyPI) · `READ` on each secret · `READ` on the source stage (SQL route) |
| View | Signed-in Snowflake user · `USAGE` on database, schema, app |
| Edit | Owner role. Viewers never get edit mode |
| Embed | `EMBED` on the app — not implicit, even for the owner |

```sql
GRANT USAGE ON DATABASE my_db TO ROLE my_app_owner;
GRANT USAGE ON SCHEMA my_db.my_schema TO ROLE my_app_owner;
GRANT CREATE STREAMLIT ON SCHEMA my_db.my_schema TO ROLE my_app_owner;
GRANT USAGE ON WAREHOUSE my_app_wh TO ROLE my_app_owner;
GRANT USAGE ON COMPUTE POOL my_app_pool TO ROLE my_app_owner;
```
- Managed-access schema: the schema owner (or a role with `MANAGE GRANTS`) grants `USAGE` on the app.
- Workspaces: creating also needs an account default compute pool and a default warehouse.

## Sharing
```sql
GRANT USAGE ON DATABASE my_db TO ROLE my_app_viewer;
GRANT USAGE ON SCHEMA my_db.my_schema TO ROLE my_app_viewer;
GRANT USAGE ON STREAMLIT my_db.my_schema.my_app TO ROLE my_app_viewer;
```
- CLI equivalent: `snow streamlit share my_app my_app_viewer` (`--grant-location-usage` adds the database and schema grants).
- Grant to roles, never users. Every viewer needs a Snowflake login — no public access.
- Viewer cannot open the app → live version missing (`deploy.md`, SQL route).

## Session
Docs: `app-development/secrets-and-configuration`
```python
import streamlit as st

conn = st.connection("snowflake")
df = conn.query(
    "select region, sum(amount) as amount from my_db.my_schema.sales where year = ? group by region",
    params=[year], ttl=600,
)
session = conn.session()   # Snowpark, when needed
```
- Same code locally and deployed, both runtimes.
- Bind user input with `params`; never build SQL with f-strings.
- Fully qualify objects; do not rely on a session default database or schema.
- `get_active_session()`: warehouse runtime only, not thread-safe, fails on the container runtime.

## Owner's rights (default)
Docs: `object-management/owners-rights`
- The app runs as the **owner role** on the app's warehouse, for every viewer. A viewer with no grants on a table still sees whatever the app displays from it.
- Therefore: owner role narrow and read-only · no free-form SQL box · write paths only when designed and reviewed · a user filter in app code is a convenience, not a security control.
- Warehouse runtime: owner's-rights stored-procedure restrictions apply (some `SHOW` / `DESCRIBE` / `LIST`, `ALTER USER`, some built-ins). Container runtime: they do not.
- Context functions need the global `READ SESSION` privilege on the owner role, and under owner's rights are unsuitable for per-user row access policies.

## Restricted caller's rights (per-user data)
Docs: `features/restricted-callers-rights` · `features/row-access`
- Container runtime, Streamlit ≥ 1.53.1.
```python
user_conn = st.connection("snowflake-callers-rights")   # queries run as the viewer
app_conn = st.connection("snowflake")                   # owner's rights; both usable in one app
```
- An admin with `MANAGE CALLER GRANTS` defines the caller grants (what the app may do on a viewer's behalf); the viewer's role must also hold those privileges.
- Runs with the viewer's default role. Token lives about 2 minutes — get the connection each run, never store it.
- Errors in local dev and on the warehouse runtime — give local dev a fallback to `st.connection("snowflake")`.
- Cache results per session only — the container cache is shared across viewers.
- Row access and masking policies then evaluate as the viewer. This is the control for per-user data.

## External access
Docs: `features/external-access`
```sql
CREATE NETWORK RULE my_db.my_schema.api_rule
  MODE = EGRESS TYPE = HOST_PORT VALUE_LIST = ('api.example.com');
CREATE SECRET my_db.my_schema.api_key
  TYPE = GENERIC_STRING SECRET_STRING = '<redacted>';   -- value entered at run time, never committed
CREATE EXTERNAL ACCESS INTEGRATION api_eai
  ALLOWED_NETWORK_RULES = (my_db.my_schema.api_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (my_db.my_schema.api_key)
  ENABLED = TRUE;
GRANT READ ON SECRET my_db.my_schema.api_key TO ROLE my_app_owner;
GRANT USAGE ON INTEGRATION api_eai TO ROLE my_app_owner;
ALTER STREAMLIT my_db.my_schema.my_app SET
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_eai, api_eai)
  SECRETS = ('api_key' = my_db.my_schema.api_key);
```
- No integration → no outbound network from Python at all (including PyPI installs on the container runtime).
- Allow-list exact hosts; one integration per purpose.
- `SET` replaces the whole list — include the integrations already attached.
- A secret cannot be attached without its integration.
- Requests made by the browser stay blocked by the content security policy regardless.

## Secrets
| Runtime | Read with |
|---|---|
| Container | `st.secrets["api_key"]`, or env var `api_key`. Basic auth: `st.secrets["name"]["username"]` / `["password"]`, env `NAME_USERNAME` / `NAME_PASSWORD`. Names are case-sensitive |
| Warehouse | `import _snowflake` → `_snowflake.get_generic_secret_string("api_key")`; alias must match the `SECRETS` clause |

- Container runtime: cloud-provider, symmetric-key, and OAuth secret types unsupported.
- `.streamlit/secrets.toml` shipped with the app is plain text in the staged files; it merges with managed secrets and wins on conflict; unsupported on the warehouse runtime. Non-sensitive settings only.
- Never print, log, or display a secret.
- Remove: `ALTER STREAMLIT … UNSET SECRETS` (and unset the integration); the secret objects stay.

## Not verified
- Privileges page lists secret `USAGE` as warehouse-runtime only, yet container apps attach `SECRETS` too. Grant `READ` on the secret to the owner role either way and confirm on the page.
- Caller's rights status: release note 2026-06-01 says GA; some pages still say Preview.
- Embedding (`features/embedding/snowflake-users`) and personalization (`app-development/personalization`) pages — read before using.
