# Cost

Docs: docs.snowflake.com/en/developer-guide/streamlit/object-management/billing. Warehouse sizing and resource monitors: `darshan-singh-meel-data-platform` → `snowflake.md`.

## What is billed
| | Warehouse runtime | Container runtime |
|---|---|---|
| App code | The warehouse, while any viewer session is alive | The compute pool node, continuously while the app is up |
| When it stops | Session ends ~15 min after last activity (mouse movement counts); then normal warehouse auto-suspend | App process ends after 3 days with no viewers; pool then suspends per its own auto-suspend |
| Scales with | Concurrent viewers (one process each) | Node size × node count, not viewers |
| Queries | Query warehouse | Query warehouse |

- System compute pool: idle nodes are not billed; an app running on them is.
- Workspaces dev apps: compute released after 3 hours idle.

## Choosing by cost
- Few viewers, occasional use → warehouse runtime can be cheaper (nothing runs between visits).
- Many viewers or always-on → container runtime (one shared instance).
- Say this trade-off when recommending a runtime; functional needs (`runtimes.md`) decide first.

## Keep it low
- **Query warehouse:** dedicated, XS, `AUTO_SUSPEND = 60`, `AUTO_RESUME = TRUE` — isolates and exposes the app's cost. Warehouse runtime: never below 30 s (package cache clears on suspend).
- **Compute pool:** smallest instance family · `MIN_NODES = 1` · `MAX_NODES` = apps needed at once · `AUTO_RESUME = TRUE` · short auto-suspend · a budget on the pool. Small apps share one pool.
- **Queries:** cache with a `ttl` · aggregate in SQL · read pre-built tables · no query on every widget change (forms, fragments — see `darshan-singh-meel-streamlit`).
- **Warehouse runtime:** set a sleep timer under `[snowflake.sleep]` in `.streamlit/config.toml`; an open browser tab keeps the session and its warehouse alive.
- Suspend or drop apps nobody uses.
- Flag any change that raises cost: bigger node, more nodes, longer suspend, larger warehouse.

## Not verified
- The key name and allowed range under `[snowflake.sleep]` — take it from the billing page.
- Workspaces admin controls and cost monitoring (`streamlit-in-workspaces/streamlit-in-workspaces-admin`).
