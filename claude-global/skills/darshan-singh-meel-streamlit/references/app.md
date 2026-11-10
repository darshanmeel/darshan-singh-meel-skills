# App structure and execution

## Skeleton (one file, runs as is)
```python
# app.py
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Orders", layout="wide")


@st.cache_data(ttl=600)
def load_orders() -> pd.DataFrame:
    # Synthetic rows. Real data: st.connection("db").query(sql, ttl=600)
    return pd.DataFrame(
        {"region": ["North", "South", "North"], "amount": [120.0, 80.0, 45.5]}
    )


st.title("Orders")
df = load_orders()

region = st.selectbox("Region", ["All", *sorted(df["region"].unique())], key="region")
if region != "All":
    df = df[df["region"] == region]

st.metric("Total amount", f"{df['amount'].sum():,.2f}")
if df.empty:
    st.info("No orders for this region.")
else:
    st.dataframe(df, hide_index=True)
```
Test for it: `testing.md`.

## Files
```
app.py                  entrypoint (router + frame when multipage)
views/                  one file per page (multipage only)
core.py                 data and logic functions; no st.* calls except cache decorators
tests/test_app.py
.streamlit/config.toml  theme, server options (committed)
.streamlit/secrets.toml git-ignored
requirements.txt        pinned
```

## Multipage — `st.Page` + `st.navigation` (preferred)
```python
# app.py
import streamlit as st

st.set_page_config(page_title="Orders", layout="wide")
pages = {
    "Main": [st.Page("views/overview.py", title="Overview", icon=":material/home:", default=True)],
    "Admin": [st.Page("views/settings.py", title="Settings", icon=":material/settings:")],
}
st.navigation(pages).run()
```
- Call `st.navigation` once, in the entrypoint, and `.run()` the result. Anything else in the entrypoint shows on every page.
- `st.Page` source: file path, function, or URL. `visibility="hidden"` keeps a page reachable by URL, `st.page_link`, `st.switch_page`.
- `st.navigation(position=…)`: sidebar, top, or hidden. Build the page list per user for role-based access — a page not in the list gives "Page not found".
- `st.set_page_config` in the entrypoint; a page may override it.
- New apps: no `pages/` auto-discovery folder (name the folder `views/` so it is not picked up).
- Docs: docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation

## Execution model
- Any widget interaction reruns the whole script. Each browser tab is its own session.
- `st.session_state` survives reruns, fragment reruns, and page switches. It is per tab and lost on reload or tab close.
- Init: `if "k" not in st.session_state: st.session_state.k = …` (reading an unset key raises).
- A widget with `key=` mirrors its value into session state.
- Callbacks (`on_change`, `on_click`, with `args` / `kwargs`) run before the rerun → the place to update state.
- Can't be set through session state: buttons, `form_submit_button`, file and media inputs, `st.data_editor`, chart selections.
- Docs: docs.streamlit.io/develop/concepts/architecture/session-state

## Caching
| | `st.cache_data` | `st.cache_resource` |
|---|---|---|
| For | DataFrames, query results, API responses | connections, clients, models |
| Returns | a copy per call (safe to mutate) | the one shared object (must be thread-safe; a mutation hits all users) |
| Needs | picklable values | — |

- Both: `ttl` (seconds or `timedelta`), `max_entries`, `show_spinner`, `hash_funcs`, `scope="session"` for per-user caches.
- `max_size="500MB"` on `cache_data` only; `server.maxCacheDataSize` caps globally.
- Arguments form the cache key. Prefix an unhashable argument with `_` to skip it (`_conn`).
- Per-user data (row-level security, user-specific results) → put the user in the arguments or use `scope="session"`; otherwise one user's result is served to everyone.
- `st.*` calls inside a cached function are replayed on a hit — keep cached functions UI-free.
- Never a cache decorator and `st.fragment` on the same function.
- Docs: docs.streamlit.io/develop/concepts/architecture/caching

## Forms — batch inputs into one rerun
```python
with st.form("filters"):
    start = st.date_input("From", key="start")
    if st.form_submit_button("Apply filters"):
        ...
```
- Needs `st.form_submit_button`. No `st.button`, `st.download_button`, or nested form inside.
- Only the submit button takes a callback; in it, read values from `st.session_state` by key, not through `args`.
- Unsubmitted edits are dropped when a widget outside the form reruns the script.
- Docs: docs.streamlit.io/develop/concepts/architecture/forms

## Fragments — rerun one part only
```python
@st.fragment(run_every="10s")
def live_status():
    st.metric("Queue", get_queue_depth())
```
- Widgets inside rerun only that function. `run_every` = timer refresh.
- Return values are ignored on fragment reruns; pass results out through session state.
- Writing to an outside container or the sidebar: do it on every full run too, or reserve the spot with `st.empty()`.
- Full rerun from inside: `st.rerun()`.
- Docs: docs.streamlit.io/develop/concepts/architecture/fragments

## Performance
- Slow page → in this order: cache the read, filter in SQL, fragment the busy part, put the inputs in a form.
- Large tables: rely on `st.dataframe` lazy loading (starts above 150,000 rows); never `st.data_editor` on large frames.
- Limits come from `server.maxMessageSize`, server memory, and the browser — aggregate before sending.
