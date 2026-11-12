---
name: darshan-singh-meel-streamlit-snowflake-react
description: Run React + TypeScript inside Streamlit in Snowflake (SiS), warehouse runtime first, container runtime where it differs, in two modes. Widget - a small two-way custom component (v1 declare_component from a one-file Vite build, components.html as one-way fallback, v2 on the container runtime). Prebuilt app - a whole React SPA with its Python API in the Streamlit process, its fetch('/api/...') calls batched through the component (size cap, retry, timeouts, read-only when hosted). Covers self-contained builds (no CDN), frame folder vs inlined strings, snowflake.yml artifacts, bundles without secrets, naming the runtime, theming, local dev vs deployed, tests (Vitest, AppTest, stdlib build and bundle checks), deploy, failures and fixes. Use when a SiS app needs a React widget, an existing React app must run in SiS, or one is blank, stale or unanswered there. Used alongside darshan-singh-meel-streamlit, -streamlit-snowflake, -frontend-react and -frontend. Not for React or Streamlit hosted outside Snowflake.
---

# React in Streamlit in Snowflake
Two modes, one job: React that builds, deploys and runs inside a SiS app. Alongside:

| Need | Skill |
|---|---|
| Streamlit app: layout, state, caching, AppTest, option ladder before a component | `darshan-singh-meel-streamlit` |
| SiS: runtimes, privileges, owner's rights, `snowflake.yml`, deploy, cost | `darshan-singh-meel-streamlit-snowflake` |
| React code: components, state, accessibility, Vitest; v2 package components | `darshan-singh-meel-frontend-react` (`streamlit-component.md`) |
| Look, layout, words | `darshan-singh-meel-frontend` |

Not for: React or Streamlit hosted outside Snowflake · SiS apps that native widgets, `st.html` or `components.html` alone cover.

## Mode
| | Widget | Prebuilt app |
|---|---|---|
| What | One control or view inside a Streamlit page | Whole React SPA that already has a Python API |
| Data | Args in, one value out | App's own `fetch("/api/…")`, answered in process |
| Build | One self-contained `index.html` (+ `widget.js` for v2) | App's normal Vite build, adapted by a bundle script |
| Template | `references/templates/app/` | `references/templates/spa/` |
| Read | `mount.md`, `build.md` | `spa.md`, `build.md` |
New app → Streamlit pages + widgets where needed. Prebuilt-app mode only to host an existing SPA with the same code.

## Refs (`references/<file>`; read only what the task needs)
| Topic | Ref |
|---|---|
| Widget: mount per runtime, data in/out, bridge messages, theme, height, v2 | `references/mount.md` |
| Prebuilt app: fetch bridge, batching, size cap, retry, timeouts, read-only hosting, bundle | `references/spa.md` |
| Builds: one file vs frame folder vs inlined strings, size, fonts, source hash | `references/build.md` |
| Layout, `snowflake.yml`, runtime naming, dependency files, local dev, deploy, smoke test, container | `references/deploy.md` |
| Vitest, AppTest with component faked, `check_dist.py`, `check_bundle.py`, gate | `references/testing.md` |
| Symptom → cause → fix | `references/failures.md` |
| What carries over from standalone React apps, what doesn't | `references/patterns.md` |
| Official pages used, what is not verified | `references/sources.md` |

## Defaults
- Warehouse runtime → components v1 (v2 not supported there). SiS docs name only `components.html` / `.iframe` as supported v1 APIs → `declare_component(path=…)` not verified there: smoke-test on the account first (`deploy.md`).
- Container runtime → components v2 (`st.components.v2.component`); v1 also works.
- Widget: `components.declare_component(name, path=component/dist)` (two-way) · fallback `components.html(page)` with args inlined (one-way, docs-confirmed) · `choice_v2` on container runtime.
- Prebuilt app: Streamlit shell + app's build in a v1 `frame/` (warehouse) or as inlined `js`/`css` strings (container); `fetch("/api/…")` → bridge → in-process API.
- Runtime always named: `runtime_name` / `RUNTIME_NAME` set, also for warehouse; omitted now = container runtime. `runtime_name` in `snowflake.yml` not a documented CLI field → confirm with `DESCRIBE STREAMLIT` after first deploy; SQL `CREATE STREAMLIT … RUNTIME_NAME` = documented fallback.
- Import the module: `import streamlit.components.v1 as components`; `st.components.v1.declare_component` called directly = deprecated.
- Templates first: copy + rename; no scaffold from a downloaded template.

## Flow
1. Ask (one prompt, skip what is known): mode · runtime (warehouse, container, both) · what goes in, what must come back · does the app write anything?
2. Widget: ladder in `darshan-singh-meel-streamlit` → `components.md`; native widget or `st.html` wins → say so, stop.
3. Copy template; rename to the job: component names (`choice`, `choice_v2`, `spa`) · wrapper functions · `Widget` + props · session-state keys · `snowflake.yml` entity (`widget_app`, `spa_app`) · npm package name. First time: `npm install`, commit `package-lock.json`.
4. Widget: React part + Vitest → typed Python wrapper + AppTest with `_component` faked.
   Prebuilt app: wire `api.main:app` · list `ALLOWED_WRITES` · set `HOSTED` in the app · hide write actions.
5. Build: widget → `git add` source, `npm run build` (+ `build:v2`), commit source + build together. Prebuilt app → app's normal build, then `build_bundle.py --runtime … --database … --schema … --warehouse …` (container: `--pool`, `--eai` or `--pypi-repo`).
6. Check: `check_dist.py` or `check_bundle.py` · `npm test` · `pytest`. All green before a deploy.
7. Give deploy command + `post_deploy.sql` → user runs them. Then smoke test in `deploy.md` (runtime confirmed, a value reaches Python).

## Rules
- Claude never runs `snow streamlit deploy` · `PUT` · `REMOVE` · DDL · DCL; writes the files and commands.
- No network at runtime: no CDN script, style, font, iframe, third-party call. CSP blocks external scripts, styles, iframes, `eval()` in both runtimes; a blocked script fails silently. Fonts + images over HTTPS allowed; bundle them anyway.
- React never calls Snowflake, holds no credentials. Python queries under the owner role, sends only what is shown.
- Message size: warehouse runtime caps a message at 32 MB, fixed. Widget page ≤ 2 MB; prebuilt-app answers packed ≤ 24 MB, rest retried, one too large → 413.
- Every value sent back reruns the script: widget → send on commit, debounce · prebuilt app → batch (max 8, 15 ms) inside an `st.fragment`, 300 s timeout per batch.
- Read-only when hosted: non-GET → 409 unless allow-listed; page hides write actions behind one `HOSTED` flag. Settings viewers must not change → ship as config.
- Bundle without secrets: deploy folder rebuilt from scratch with an ignore list (`.env*`, keys, `credentials*`, `secrets*`, `connections.toml`, `.snowflake/`, `profiles.yml`); check fails on any left (name only, never read).
- Stale files never ship: rebuild deploy folder, deploy with `--prune` (or REMOVE then PUT).
- Shipped data: only via `--data`, after a `check_data()` that refuses test/demo data by content; anyone granted the app sees all of it → mask before deploy.
- Container PyPI: external access integration or PyPI artifact repository, else nothing installs.
- Python owns the state; React renders from args. One typed wrapper per widget.
- Theme from Streamlit → CSS variables; no hard-coded colours beyond fallbacks.
- Untrusted text → React text, never `dangerouslySetInnerHTML`; errors reach the page as the exception type only.
- Pin: Streamlit in `environment.yml` to a version the warehouse runtime offers; npm with the lock file.
- Ref marks "not verified" → say so, or check the docs first; never state as fact.

## Before finishing
- Checks of step 6 pass; say which ran.
- After the user's deploy: smoke test passed, or failure in `failures.md` with its fix.
- Name any version or API taken from memory, not checked.
