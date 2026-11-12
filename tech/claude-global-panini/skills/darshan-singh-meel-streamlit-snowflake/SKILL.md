---
name: darshan-singh-meel-streamlit-snowflake
description: Streamlit in Snowflake (SiS) only — setup, privileges, creating apps (Snowsight, SQL CREATE STREAMLIT, snow CLI), snowflake.yml and snow streamlit deploy, warehouse vs container runtime, packages, session and st.connection, owner's vs caller's rights, external access integrations, secrets, sharing, limits and unsupported features, cost, Git integration, local dev then deploy. Use when building, deploying, migrating, sharing, securing, or debugging a Streamlit app hosted in Snowflake. Not for Streamlit hosted elsewhere (use darshan-singh-meel-streamlit).
---

# Streamlit in Snowflake
Only what differs when Snowflake hosts the app. Alongside:

| Need | Skill |
|---|---|
| General Streamlit: layout, caching, state, forms, components | `darshan-singh-meel-streamlit` |
| RBAC, warehouses, SQL, cost | `darshan-singh-meel-data-platform` (`snowflake.md`, `rbac.md`) |
| UI design | `darshan-singh-meel-frontend` |
| Any query against data or metadata | `darshan-singh-meel-notebook` |

Not for React in a SiS app (custom widget · whole prebuilt React app + its API: build, mount, fetch bridge, deploy, tests) → `darshan-singh-meel-streamlit-snowflake-react`.

## Refs (`references/<file>`; read only what the task needs)
| Topic | Ref |
|---|---|
| Create (Snowsight · SQL · CLI), `snowflake.yml`, dependency files, deploy, local dev, Git, CI | `deploy.md` |
| Warehouse vs container runtime, packages, limits, unsupported features, `config.toml` | `runtimes.md` |
| Privileges, session, owner's vs caller's rights, external access, secrets, sharing | `access.md` |
| What is billed, how to keep it low | `cost.md` |

Official docs: docs.snowflake.com/en/developer-guide/streamlit/ — unsure → check; name the page used. Facts checked 2026-11; statuses (Preview/GA) change.

## Defaults
- Runtime: container — Python 3.11 · Streamlit ≥ 1.50 · `pyproject.toml` pinned with `==`. Since behaviour change 2026_06 also what `CREATE STREAMLIT` picks when `RUNTIME_NAME` is omitted.
- Warehouse runtime only when: container unavailable (government/China regions, most Native Apps) · no compute pool · asked.
- `RUNTIME_NAME` always explicit; never rely on the default.
- Session: `st.connection("snowflake")` — local + deployed, both runtimes. No `get_active_session()` in new apps (fails on container runtime).
- Deploy: project folder with `snowflake.yml` (v2) + `snow streamlit deploy --replace`. Snowsight editor → throwaway prototypes only.
- Source in Git; the Streamlit object = deploy target, never source of truth.

## Flow
1. Ask (one prompt, skip what is known): runtime · who views it and what they may see · external network calls needed?
2. Build + run locally (`streamlit run`), same code as deployed.
3. Setup SQL (roles, grants, pool, integrations, secrets) in a script → user runs it.
4. Give the deploy command → user runs it (creates or replaces an object).
5. Share: grant `USAGE` on the app to a viewer role.

## Rules
- Claude never executes DDL/DCL · `PUT` · `snow streamlit deploy|share`; writes the files and commands. Read-only checks (`SHOW STREAMLITS`, `DESC STREAMLIT`) → notebook cell.
- Owner's rights by default: every viewer sees what the owner role sees → owner role dedicated, least-privilege, read-only on exactly what the app shows. Per-user data → restricted caller's rights (`access.md`).
- Secrets: Snowflake `SECRET` + external access integration, read via `st.secrets`. Never in code · `snowflake.yml` · titles/comments · `.streamlit/secrets.toml` (stored as plain text with the app).
- Project folder = app files only (the CLI may upload what is in it): no `.env`, keys, data extracts.
- No PII or data in app title, comment, object names.
- No external scripts, styles, iframes (blocked by the content security policy) → bundle JS/CSS locally.
- Push work to SQL; cache query results with a `ttl`. Container runtime shares the cache across viewers → never cache per-user data there without session scope.
- Dedicated small query warehouse, short auto-suspend; small compute pool, auto-suspend (`cost.md`).
- Pin every package; version change → redeploy.
- Ref marks "not verified" → say so, or check the docs first; never state as fact · in files: fact about the app ("Not yet tested on the container runtime"), not a note to the reader.
