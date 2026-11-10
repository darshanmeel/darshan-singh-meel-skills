# Create, deploy, local dev, Git

Docs (under docs.snowflake.com/en/): `developer-guide/streamlit/app-development/creating-your-app` · `sql-reference/sql/create-streamlit` · `developer-guide/snowflake-cli/streamlit-apps/manage-apps/deploy-app`

## Three ways to create
| Way | Use for | Notes |
|---|---|---|
| **Snowflake CLI** (`snow` ≥ 3.14.0) | Default: repeatable, in Git, CI-ready | `snowflake.yml` + `snow streamlit deploy` |
| **SQL** `CREATE STREAMLIT … FROM` | Migration scripts, Git repository objects | Files must already be on an internal stage or in a Git repository object |
| **Snowsight** (Projects » Streamlit, or Workspaces) | Prototypes, quick edits | Side-by-side editor and preview; move to Git before it matters |

## Project layout (container runtime)
```
my_app/
  snowflake.yml
  pyproject.toml           # or requirements.txt — exactly one
  streamlit_app.py
  pages/
  .streamlit/config.toml   # theme only; no secrets
```
Optional scaffold: `snow init my_app --template example_streamlit -D query_warehouse=<wh> -D stage=<stage>` — gives a warehouse-runtime layout (`environment.yml`); adjust for container.

## snowflake.yml (container runtime)
```yaml
definition_version: 2
entities:
  my_app:
    type: streamlit
    identifier:
      name: my_app
      database: my_db
      schema: my_schema
    title: My app
    query_warehouse: my_app_wh
    compute_pool: my_app_pool
    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11
    external_access_integrations:
      - pypi_eai            # needed to install from PyPI
    main_file: streamlit_app.py
    pages_dir: pages
    artifacts:
      - streamlit_app.py
      - pyproject.toml
      - pages/
      - .streamlit/config.toml
```
- One Streamlit entity per file. Required: `query_warehouse`, `artifacts`.
- Optional: `comment`, `tags`, `secrets`, `grants` (privilege + role), `stage`, `imports` (warehouse runtime only).
- Dev and prod → same file, different CLI connection or `--database` / `--schema` / `--role` on the command. No templating system.

## Dependency file
**Container runtime — `pyproject.toml`** (recommended):
```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.11,<3.12"
dependencies = [
    "streamlit[snowflake]==<x.y.z>",   # latest stable the container runtime supports
    "pandas==<x.y.z>",
]
```
Or `requirements.txt` (wins over `pyproject.toml` in the same folder):
```
streamlit[snowflake]==<x.y.z>
pandas==<x.y.z>
```
- Replace `<x.y.z>` with exact versions checked on the docs or PyPI before pinning. Streamlit ≥ 1.50 required; ≥ 1.53.1 for caller's rights.
- `streamlit[snowflake]` brings Snowpark. Commit `uv.lock` when using `pyproject.toml`.

**Warehouse runtime — `environment.yml`** (add it to `artifacts`; remove `compute_pool`; `runtime_name: SYSTEM$WAREHOUSE_RUNTIME`):
```yaml
name: app_environment
channels:
  - snowflake          # the only allowed channel; no pip section
dependencies:
  - python=3.11.*
  - streamlit=1.50.0   # must be a version Snowflake offers — see the Snowsight package picker
  - pandas=2.*
```

## Deploy
```bash
snow streamlit deploy --replace --connection <name>   # --open launches it, --prune deletes files removed locally
snow streamlit get-url my_app --connection <name>
```
- Run from the folder holding `snowflake.yml`.
- Files go to the app's own stage — no named stage needed. Never `--legacy` (`ROOT_LOCATION`) for new apps.
- CLI connection uses key-pair or SSO, configured outside the project. No passwords in files.
- Other commands: `list`, `describe`, `share`. The CLI cannot rename — `ALTER STREAMLIT … RENAME TO`.

## SQL route
```sql
-- upload first: PUT file://streamlit_app.py @my_db.my_schema.my_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT my_db.my_schema.my_app
  FROM '@my_db.my_schema.my_stage/my_app'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = my_app_wh
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = my_app_pool
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_eai);
ALTER STREAMLIT my_db.my_schema.my_app ADD LIVE VERSION FROM LAST;
```
- `FROM` is copied **once** at creation. Later stage changes do not update the app.
- `ADD LIVE VERSION FROM LAST` is required before `USAGE`-only viewers can open the app (opening it once in Snowsight as the owner also works).
- `CREATE OR REPLACE` drops grants on the app — re-grant after, or change with `ALTER`.
- Other clauses: `TITLE`, `COMMENT`, `SECRETS`, `IMPORTS` (warehouse only). `IMPORTS` or `EXECUTE AS` fail on the container runtime.
- Change later: `ALTER STREAMLIT … SET QUERY_WAREHOUSE | COMPUTE_POOL | MAIN_FILE | EXTERNAL_ACCESS_INTEGRATIONS | SECRETS`.
- Cloning a schema or database does **not** clone Streamlit objects — deploy into the clone.
- Internal stages only; external stages unsupported.

## Local dev, then deploy
1. Same pinned versions locally: `uv sync` (container) or a conda env from `environment.yml` with channel `https://repo.anaconda.com/pkgs/snowflake` + `nodefaults` (warehouse).
2. `streamlit run streamlit_app.py`. `st.connection("snowflake")` reads the local connection config — keep it outside the project, or in a git-ignored `.streamlit/secrets.toml` that is not in `artifacts`.
3. Local role = a dev role on a dev database, with the same read grants the owner role will have.
4. Cannot be tested locally: caller's rights connection (errors), Snowflake-managed secrets, the content security policy, runtime limits. Test these on a dev deploy.
5. Deploy to dev → check → same command with the prod connection.

## Git integration
Docs: `developer-guide/streamlit/features/git-integration`
- **Preferred:** normal Git repo + CLI deploy from CI. Works with both runtimes.
- **Snowflake-native** — needs a Git repository object (API integration) in the account:
  - SQL: `CREATE STREAMLIT … FROM '@my_db.my_schema.my_repo/branches/main/my_app'`.
  - Snowsight: Projects » Streamlit » "Create from repository". Database and schema cannot change afterwards.
  - Connect an existing app: `OWNERSHIP` or `READ` on the repository + `USAGE` on its schema.
  - Push: `OWNERSHIP` or `WRITE` on the repository + a personal access token (stored by Snowflake). Pull from the Files tab.
- Not available for legacy `ROOT_LOCATION` apps.
- Workspaces: private dev app, then an explicit deploy to targets defined in `snowflake.yml`; Git-backed workspaces supported. Docs: `developer-guide/streamlit/streamlit-in-workspaces/streamlit-in-workspaces-overview`.

## CI
- On merge to the main branch: install a pinned CLI, run `snow streamlit deploy --replace`.
- Auth: service user (`TYPE = SERVICE`, key-pair) holding only the app owner role; key in the CI secret store. The docs example uses a password secret — prefer key-pair.

## Not verified
- A `snow streamlit init` command — docs use `snow init … --template example_streamlit`.
- Exact Streamlit versions offered on the warehouse runtime — read the list in Snowsight.
- Which runtimes Snowsight Git integration supports; its Preview/GA status.
