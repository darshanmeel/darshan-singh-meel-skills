---
name: darshan-singh-meel-streamlit
description: Build, run, test, and deploy open-source Streamlit apps on any host — app structure, multipage navigation, session state, caching, forms, fragments, data tables, charts, connections, secrets, login, AppTest tests, Docker and Community Cloud deploys, custom components. Use when writing, fixing, speeding up, testing, or deploying a Streamlit app or data app ("streamlit", "st.", "data app in Python"). For apps hosted in Snowflake also load darshan-singh-meel-streamlit-snowflake.
---

# Streamlit

App code is the same on every host; only deploy and runtime differ. Read only the reference files (`references/<file>`) the task needs.

| Task | File |
|---|---|
| Skeleton, file layout, multipage, session state, caching, forms, fragments | `app.md` |
| Layout, tables, editors, charts, theme, config | `ui.md` |
| Connections, secrets, login | `data-auth.md` |
| Tests with AppTest | `testing.md` |
| Run, Docker, Community Cloud, load balancers | `deploy.md` |
| Custom components, HTML embeds | `components.md` |

## Works with
| Need | Skill |
|---|---|
| Design: colour, type, layout, words, dashboards, quality floor | `darshan-singh-meel-frontend` (plan there, build here) |
| Code discipline, tests after changes | `darshan-singh-meel-code` |
| Hosted in Snowflake: runtimes, `CREATE STREAMLIT`, limits, privileges | `darshan-singh-meel-streamlit-snowflake` (adds to this skill) |
| Native widgets not enough → React component | `darshan-singh-meel-frontend-react`, wrapped per `components.md` |
| Exploring or checking data while developing | `darshan-singh-meel-notebook` (never ad-hoc queries from the app or shell) |
| SQL, warehouse, RBAC rules | `darshan-singh-meel-data-platform` |

## Versions
- Use the version the project pins (`requirements.txt`, `pyproject.toml`, lock file). Nothing pinned → latest stable, pinned exactly (`streamlit==1.67.0` at the time of writing; Python 3.11+).
- The host can cap the version (Snowflake warehouse runtime lags far behind). Check the host before using a new API.
- Unsure about an API, a parameter, or the version that added it → docs.streamlit.io only; name the page used.
- Never write deprecated calls: `use_container_width` → `width="stretch"`; `st.components.v1.html` / `.iframe` → `st.iframe` or `st.html`; `st.experimental_*` → the stable name.

## Rules
- **Built-ins first.** Native widgets, `st.dataframe`, built-in charts, `st.connection`, `st.login`. No extra package for one widget; no CSS hacks against Streamlit's DOM.
- **The script reruns top to bottom on every interaction.** Plain variables reset; keep state in `st.session_state`, change it in callbacks.
- **Cache every slow read.** `st.cache_data(ttl=…)` for data, `st.cache_resource` for clients and models. Always a `ttl` on data.
- **Push work to the engine.** Filter and aggregate in SQL; send the browser only what it shows.
- **Small app → one file.** Split into pages only when there are separate jobs. Shared logic in plain UI-free functions, testable without Streamlit.
- **Every data view has loading, empty, and error states** (`st.spinner`, `st.info`, `st.error` with the fix).
- **Keys on widgets** that tests, callbacks, or state refer to.

## Security and data
- No secrets in code or the repo. `st.secrets` or the host's secret store. `.streamlit/secrets.toml` is git-ignored and never opened by Claude: record that it exists; write `secrets.toml.example` with names and `<redacted>` values.
- SQL with bound parameters, never strings built from user input.
- Read-only database role for the app unless it must write; least privilege.
- Drop sensitive columns before `st.dataframe` — the viewer can reveal hidden columns. No PII in examples, tests, or screenshots; synthetic rows.
- Never pass untrusted HTML (user input, database text, LLM output) to `st.iframe`, or to `st.html` with JavaScript allowed.
- Pickle-backed features (`cache_data`, serializable session state) only with trusted data.

## Workflow
1. Design plan per `darshan-singh-meel-frontend` (existing theme → layout only).
2. Start from the skeleton in `app.md`: synthetic data first, real connection second.
3. Run `streamlit run app.py`. Fix every warning and deprecation notice in the terminal.
4. Test with AppTest (`testing.md`): one test that the app runs without exception, one per main interaction.
5. Deploy per `deploy.md`: pinned dependencies, secrets in the host's store, health check.
