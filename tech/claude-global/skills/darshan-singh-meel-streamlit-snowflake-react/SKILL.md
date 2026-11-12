---
name: darshan-singh-meel-streamlit-snowflake-react
description: Run React + TypeScript inside Streamlit in Snowflake (SiS), warehouse runtime first, container runtime where it differs, in two modes. Widget - a small two-way custom component (v1 declare_component from a one-file Vite build, components.html as one-way fallback, v2 on the container runtime). Prebuilt app - a whole React SPA with its Python API in the Streamlit process, its fetch('/api/...') calls batched through the component (size cap, retry, timeouts, read-only when hosted). Covers self-contained builds (no CDN), frame folder vs inlined strings, snowflake.yml artifacts, bundles without secrets, naming the runtime, theming, local dev vs deployed, tests (Vitest, AppTest, stdlib build and bundle checks), deploy, failures and fixes. Use when a SiS app needs a React widget, an existing React app must run in SiS, or one is blank, stale or unanswered there. Used alongside darshan-singh-meel-streamlit, -streamlit-snowflake, -frontend-react and -frontend. Not for React or Streamlit hosted outside Snowflake.
---

# React in Streamlit in Snowflake

Two modes, one job: React code that builds, deploys and runs inside a SiS app. Use alongside:

| Need | Skill |
|---|---|
| Streamlit app: layout, state, caching, AppTest, the option ladder before a component | `darshan-singh-meel-streamlit` |
| SiS: runtimes, privileges, owner's rights, `snowflake.yml`, deploy, cost | `darshan-singh-meel-streamlit-snowflake` |
| React code: components, state, accessibility, Vitest; v2 package components | `darshan-singh-meel-frontend-react` (`streamlit-component.md`) |
| Look, layout, words | `darshan-singh-meel-frontend` |

Not for: React or Streamlit hosted outside Snowflake · SiS apps that native widgets, `st.html` or `components.html` alone already cover.

## Pick the mode
| | Widget | Prebuilt app |
|---|---|---|
| What | One control or view inside a Streamlit page | A whole React SPA that already has a Python API |
| Data | Args in, one value out | The app's own `fetch("/api/…")`, answered in process |
| Build | One self-contained `index.html` (+ `widget.js` for v2) | The app's normal Vite build, adapted by a bundle script |
| Template | `references/templates/app/` | `references/templates/spa/` |
| Read | `mount.md`, `build.md` | `spa.md`, `build.md` |
New app → Streamlit pages with widgets where needed. Prebuilt-app mode only to host an existing SPA with the same code.

## References (read only what the task needs)
| Topic | File |
|---|---|
| Widget: which mount on which runtime, data in/out, bridge messages, theme, height, v2 | `references/mount.md` |
| Prebuilt app: fetch bridge, batching, size cap, retry, timeouts, read-only hosting, bundle | `references/spa.md` |
| Builds: one file vs frame folder vs inlined strings, size, fonts, source hash | `references/build.md` |
| Layout, `snowflake.yml`, runtime naming, dependency files, local dev, deploy, smoke test, container | `references/deploy.md` |
| Vitest, AppTest with the component faked, `check_dist.py`, `check_bundle.py`, the gate | `references/testing.md` |
| Symptom → cause → fix | `references/failures.md` |
| What carries over from standalone React apps, and what doesn't | `references/patterns.md` |
| Official pages used, what is not verified | `references/sources.md` |

## Defaults
- **Warehouse runtime: components v1** (v2 is not supported there). The SiS docs name only `components.html` / `.iframe` as supported v1 APIs → `declare_component(path=…)` is not verified there: smoke-test on the account first (`deploy.md`).
- **Container runtime: components v2** (`st.components.v2.component`); v1 also works.
- **Widget:** `components.declare_component(name, path=component/dist)` (two-way); fallback `components.html(page)` with args inlined (one-way, docs-confirmed); `choice_v2` on the container runtime.
- **Prebuilt app:** Streamlit shell + the app's build in a v1 `frame/` (warehouse) or as inlined `js`/`css` strings (container); `fetch("/api/…")` → bridge → in-process API.
- **Always name the runtime:** `runtime_name` / `RUNTIME_NAME` set, also for the warehouse runtime; leaving it out now means the container runtime. `runtime_name` in `snowflake.yml` is not a documented CLI field → confirm with `DESCRIBE STREAMLIT` after the first deploy; SQL `CREATE STREAMLIT … RUNTIME_NAME` is the documented fallback.
- **Import the module:** `import streamlit.components.v1 as components`; calling `st.components.v1.declare_component` directly is deprecated.
- **Templates first:** copy and rename; don't scaffold from a downloaded template.

## Flow
1. Ask (one prompt, skip what is known): mode · runtime (warehouse, container, both) · what goes in and what must come back · does the app write anything?
2. Widget: check the ladder in `darshan-singh-meel-streamlit` → `components.md`; a native widget or `st.html` wins → say so and stop.
3. Copy the template; rename to the job: component names (`choice`, `choice_v2`, `spa`), wrapper functions, `Widget` and its props, session-state keys, the `snowflake.yml` entity (`widget_app`, `spa_app`), the npm package name. First time: `npm install`, commit `package-lock.json`.
4. Widget: React part + Vitest → typed Python wrapper + AppTest with `_component` faked.
   Prebuilt app: wire `api.main:app`, list `ALLOWED_WRITES`, set `HOSTED` in the app, hide write actions.
5. Build: widget → `git add` source, `npm run build` (and `build:v2`), commit source and build together. Prebuilt app → the app's normal build, then `build_bundle.py --runtime … --database … --schema … --warehouse …` (container: `--pool`, `--eai` or `--pypi-repo`).
6. Check: `check_dist.py` or `check_bundle.py`, `npm test`, `pytest`. All green before a deploy.
7. Give the deploy command and `post_deploy.sql`; **the user runs them**. Then the smoke test in `deploy.md` (runtime confirmed, a value reaches Python).

## Rules
- **Claude never runs** `snow streamlit deploy`, `PUT`, `REMOVE`, DDL or DCL. It writes the files and the commands.
- **No network at runtime:** no CDN script, style, font, iframe or third-party call. The CSP blocks external scripts, styles, iframes and `eval()` in both runtimes, and a blocked script fails silently. Fonts and images over HTTPS are allowed; bundle them anyway.
- **React never calls Snowflake** and holds no credentials. Python queries under the owner role and sends only what is shown.
- **Message size:** warehouse runtime caps a message at 32 MB, fixed. Widget page ≤ 2 MB; prebuilt-app answers packed ≤ 24 MB, the rest retried, one too large → 413.
- **Every value sent back reruns the script:** widget → send on commit, debounce; prebuilt app → batch (max 8, 15 ms) inside an `st.fragment`, 300 s timeout per batch.
- **Read-only when hosted:** non-GET requests → 409 unless allow-listed; the page hides write actions behind one `HOSTED` flag. Settings viewers must not change ship as config.
- **Bundle without secrets:** the deploy folder is rebuilt from scratch with an ignore list (`.env*`, keys, `credentials*`, `secrets*`, `connections.toml`, `.snowflake/`, `profiles.yml`); the check fails on any left (name only, never read).
- **Stale files never ship:** rebuild the deploy folder, deploy with `--prune` (or REMOVE then PUT).
- **Shipped data:** only via `--data`, after a `check_data()` that refuses test/demo data by content; anyone granted the app sees all of it → mask before the deploy.
- **Container PyPI:** an external access integration or the PyPI artifact repository, or nothing installs.
- **Python owns the state;** React renders from args. One typed wrapper per widget.
- **Theme from Streamlit** → CSS variables; no hard-coded colours beyond fallbacks.
- **Untrusted text** renders as React text, never `dangerouslySetInnerHTML`; errors reach the page as the exception type only.
- **Pin:** Streamlit in `environment.yml` to a version the warehouse runtime offers; npm with the lock file.
- Facts marked "not verified" → say so, or check the docs first; never state them as fact.

## Before finishing
- The checks of step 6 pass; say which ran.
- After the user's deploy: the smoke test passed, or the failure is in `failures.md` with its fix.
- Name any version or API taken from memory rather than checked.
