# Connections, secrets, login

## Connections — `st.connection`
```python
conn = st.connection("db", type="sql")  # config: [connections.db] in secrets.toml
df = conn.query(
    "select region, sum(amount) as amount from orders where day >= :d group by region",
    params={"d": start},
    ttl=600,
)
```
- Built-in types: `sql` (SQLAlchemy 2; install `streamlit[sql]` + the database driver) and `snowflake`.
- Config under `[connections.<name>]` in `secrets.toml`; driver options under `create_engine_kwargs`. Keyword arguments in the call override secrets.
- `st.connection("env:VAR")` picks the section named by an environment variable → one code path for dev, test, and prod.
- The connection object and `conn.query` results are cached with no expiry. Always pass `ttl`; `conn.reset()` after an auth error.
- Bound parameters (`params=`) for every user-supplied value.
- Writes: `with conn.session as s: s.execute(...); s.commit()`. Destructive statements follow `darshan-singh-meel-data-platform` ("Destructive changes need a yes").
- No built-in type fits → create the client inside `@st.cache_resource`, query inside `@st.cache_data(ttl=…)`.
- Local SQLite does not persist on Community Cloud.
- Developing the SQL itself → notebook cells via `darshan-singh-meel-notebook`; move the finished query into the app.
- Docs: docs.streamlit.io/develop/concepts/connections/connecting-to-data

## Secrets
- Files, highest precedence first: `.streamlit/secrets.toml` next to the entrypoint → in the working directory → in the user's home `.streamlit/`. A higher file replaces whole top-level keys.
- Read: `st.secrets["key"]` or `st.secrets.section.key`. Root-level keys are also set as environment variables.
- Missing file → `FileNotFoundError`; missing key → `KeyError`. Restart the server after creating the file.
- `.streamlit/secrets.toml` in `.gitignore` from the first commit. Commit `secrets.toml.example`:
```toml
[connections.db]
url = "<redacted>"
```
- Deployed: the host's secret store (Community Cloud Secrets console, container secrets or a mounted file, a cloud secret manager) — never baked into an image.
- Docs: docs.streamlit.io/develop/concepts/connections/secrets-management

## Login — `st.login` (OIDC)
```python
if not st.user.is_logged_in:
    st.button("Log in", on_click=st.login)
    st.stop()
st.sidebar.button("Log out", on_click=st.logout)
```
- Install `streamlit[auth]`. OIDC providers only (no plain OAuth).
- `secrets.toml`: `[auth]` with `redirect_uri` (absolute, ends in `/oauth2callback`), `cookie_secret` (long, random), `client_id`, `client_secret`, `server_metadata_url`. Several providers → `[auth.<provider>]` (no underscores in the name) and `st.login("<provider>")`.
- `st.user` holds the ID-token claims. Authorise in code: check the email or group claim, then build the `st.navigation` page list from it.
- `st.logout` clears the app cookie only; the provider session stays. The cookie lasts 30 days.
- Set `redirect_uri` in the app and at the provider for every environment. Not supported in embedded apps.
- Host already authenticates (reverse proxy, platform SSO) → use that; no second login on top.
- Docs: docs.streamlit.io/develop/api-reference/user/st.login
