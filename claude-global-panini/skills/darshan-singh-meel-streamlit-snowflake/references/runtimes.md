# Runtimes, packages, limits

Docs (under docs.snowflake.com/en/developer-guide/streamlit/): `app-development/runtime-environments` · `app-development/dependency-management` · `limitations`

## Warehouse vs container
| | Warehouse runtime | Container runtime (default) |
|---|---|---|
| `RUNTIME_NAME` | `SYSTEM$WAREHOUSE_RUNTIME` | `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` |
| Instance | On demand, one per viewer | Long-running, one shared by all viewers |
| App code runs on | Warehouse | Compute pool node |
| Queries run on | Query warehouse | Query warehouse |
| Python | 3.9 – 3.11 | 3.11 only |
| Streamlit | 1.22+, limited selection | 1.50+, any version |
| Packages | Snowflake Anaconda channel, `environment.yml` | PyPI or another index, `pyproject.toml` / `requirements.txt` |
| Pin syntax | `=`, `*` wildcards | `==`, `<`, `<=`, `>=`, `>` |
| `st.cache_*` | Per session | Shared across sessions |
| Runs as | Owner's-rights stored procedure (its restrictions apply) | Not a stored procedure |
| Caller's rights | No | Yes (Streamlit ≥ 1.53.1) |
| Components v2, static file serving | No | Yes |
| Message / upload size | 32 MB / 200 MB, fixed | 200 MB / 200 MB default, configurable, capped by memory |
| Secrets | `_snowflake.get_generic_secret_string` | `st.secrets`, env vars |

- **Default:** since behaviour change 2026_06, `CREATE STREAMLIT` without `RUNTIME_NAME` → container. Existing apps, Native Apps, and government/China regions unaffected. No account-wide opt-out documented — set `RUNTIME_NAME` per statement. Docs: `release-notes/bcr-bundles/2026_06/bcr-2342`.
- Container runtime: few government regions, not FedRAMP-authorized; subject to the container-services maintenance window.
- Native Apps: warehouse runtime by default; container runtime in Preview (2026-09).
- 32 MB exceeded on the warehouse runtime → `MessageSizeError`: send less data (aggregate, paginate) before changing runtime.

## Migrating warehouse → container
Docs: `migrations-and-upgrades/runtime-migration`
| From | To |
|---|---|
| `environment.yml` | `pyproject.toml` (conda names → PyPI names, e.g. `opencv` → `opencv-python`) |
| `get_active_session()` | `st.connection("snowflake").session()` |
| `_snowflake.get_generic_secret_string("x")` | `st.secrets["x"]` |
| `IMPORTS` | Files in the project, or packages |
| Per-session cache assumptions | Review every `st.cache_*` for per-user data |

## Compute pool (container)
- Owner role needs `USAGE`; pool needs `AUTO_RESUME = TRUE`.
- No pool given → account parameter `DEFAULT_STREAMLIT_COMPUTE_POOL`.
- `SYSTEM_COMPUTE_POOL_CPU`: 3 apps per node. Other pools: 1 app per node → `MIN_NODES` ≈ apps that must be up at once.
- Smallest instance family that fits; heavy computation belongs in SQL, not on the node.

## Packages
**Container**
- Lookup walks from the entrypoint folder up to the source root; first file found wins; `requirements.txt` beats `pyproject.toml` in the same folder. Keep exactly one.
- `pyproject.toml` recommended: sets `requires-python`, produces `uv.lock`, and is required for non-PyPI indexes (`[[tool.uv.index]]`).
- PyPI needs an external access integration attached to the app:
```sql
CREATE EXTERNAL ACCESS INTEGRATION pypi_eai
  ALLOWED_NETWORK_RULES = (snowflake.external_access.pypi_rule) ENABLED = TRUE;
GRANT USAGE ON INTEGRATION pypi_eai TO ROLE my_app_owner;
```
- Private index: scoped read-only token, never committed.
- An attached artifact repository replaces the uv environment — integrations then do not apply to installs; attaching or removing one restarts the app.
- Non-Python system libraries: only what is pre-installed.

**Warehouse**
- `environment.yml` at the source root; channel `snowflake` only; no `pip:` section.
- Package cache clears when the warehouse suspends — auto-suspend ≥ 30 s.
- Package missing from the channel → move to the container runtime; do not vendor it.

## Unsupported — all runtimes
- `st.set_page_config`: `page_title`, `page_icon`, `menu_items`.
- Content security policy: no external scripts or styles, no iframes of external sites, no `eval()`. Images, media, and fonts over HTTPS are fine. A blocked script fails silently — no Python error.
- Custom components that load scripts from a CDN — bundle everything.
- External stages; `.so` files.
- Mapbox/Carto maps: warehouse runtime needs the External Offerings Terms accepted; container runtime does not.

## config.toml sections
| Section | Warehouse | Container |
|---|---|---|
| `[theme]`, `[theme.sidebar]` | Yes | Yes |
| `[runner]` | No | Yes |
| `[global]`, `[client]` | No | Limited |
| `[snowflake.sleep]` | Yes | No |
| `[logger]`, `[server]`, `[browser]` | No | No |

## Components
- v1 (`st.components.v1.html` / `.iframe`): both runtimes; deprecated in Streamlit 1.56 for `st.iframe` / `st.html`.
- v2 (`st.components.v2`): container runtime only, including package-based components.

## Not verified
- `[server]` is listed as unsupported, yet `server.maxMessageSize` / `server.maxUploadSize` are described as configurable on the container runtime — check the limitations page first.
- Third-party pip-installed v1 components on the warehouse runtime.
- An explicit "GA" label for the container runtime (implied by the 2026_06 default).
