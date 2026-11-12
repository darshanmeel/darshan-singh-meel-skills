# Deploy, local dev, container runtime

General SiS deploy (CLI version, connections, SQL route, Git, CI): `darshan-singh-meel-streamlit-snowflake` → `deploy.md`. This file covers only the widget.

Docs: docs.snowflake.com/en/developer-guide/snowflake-cli/streamlit-apps/manage-apps/deploy-app · docs.snowflake.com/en/developer-guide/streamlit/app-development/file-organization

## snowflake.yml (warehouse runtime)
```yaml
definition_version: 2
entities:
  widget_app:
    type: streamlit
    identifier: { name: widget_app, database: <db>, schema: <schema> }
    query_warehouse: <app_wh>
    runtime_name: SYSTEM$WAREHOUSE_RUNTIME
    main_file: streamlit_app.py
    artifacts:
      - streamlit_app.py
      - widget.py
      - environment.yml
      - component/dist/index.html
```
- **Name the runtime, always:** `runtime_name: SYSTEM$WAREHOUSE_RUNTIME` (or `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` + `compute_pool`). Left out, `CREATE STREAMLIT` now picks the container runtime (behaviour change 2026_06), and a v1-only widget meets a different runtime than it was tested on. Both check scripts fail without it, or on an unknown name.
- **`runtime_name` and `compute_pool` are not on the CLI's documented `snowflake.yml` field list** (not verified). If the CLI ignores them, the app silently gets the default runtime → after the first deploy run `DESCRIBE STREAMLIT <db>.<schema>.<app>` (read-only; in a notebook cell) and check the runtime. Wrong runtime → the documented route: SQL `CREATE STREAMLIT … RUNTIME_NAME = 'SYSTEM$WAREHOUSE_RUNTIME'` (below).
- Grants in the project file: a `grants:` block (privilege + role, e.g. `USAGE` to the viewer role) re-applies them on every deploy, so `--replace` never leaves viewers locked out.
- Placeholders (`<db>`, `<x.y.z>`, …) must all be filled: both check scripts fail on any left.
- Container runtime: artifact `component/dist-v2/widget.js` instead, plus `requirements.txt` or `pyproject.toml`.
- List the build file, not `component/` or `.`: those upload the frontend source and `node_modules` (thousands of files, slow, and nothing Python needs). `check_dist.py` fails on both.
- Main file at the source root (warehouse runtime requirement); `widget.py` beside it, so `from widget import choice` works.
- Artifacts keep their relative path on the app's stage → `component/dist/index.html` lands where `widget.DIST` looks. After the first deploy, confirm in Snowsight (app → Files) that the path is the same.
- `environment.yml`: channel `snowflake` only, `streamlit=<x.y.z>` set to a version the Snowsight package picker offers. No npm or Node in the app: the build is already done.

## npm
- The template ships `package.json` without a lock file and its versions are not installed with it (not verified): first time, `npm install` in `component/frontend`, check that `npm run build` and `npm test` pass, and commit `package-lock.json`. From then on `npm ci`.

## Local dev
| Mode | Commands | Use for |
|---|---|---|
| Hot reload | `npm run dev` in `component/frontend` · `WIDGET_DEV_URL=http://localhost:5173 streamlit run streamlit_app.py` | Writing the widget |
| Built | `npm run build` · `streamlit run streamlit_app.py` (no env var) | What Snowflake will run |
| Widget alone | `npm test`; `npm run dev` and open the page (static data via the `args` script tag) | Layout and states without Python |

- Same Streamlit version locally as in `environment.yml` (conda env from it, channel `https://repo.anaconda.com/pkgs/snowflake`).
- Local runs cannot show the SiS content security policy, the Snowsight frame or the runtime's Streamlit build → the smoke test on a dev deploy is required.

## Deploy steps (the user runs them)
1. `python tools/check_dist.py` → `dist OK`; `npm test`; `pytest`.
2. Commit source and build together.
3. `snow streamlit deploy --replace --connection <dev>` from the folder with `snowflake.yml`.
4. Smoke test (below) on dev.
5. Same command with the prod connection.

## Prebuilt app: deploy the bundle folder
1. The app's normal build (`npm run build` in its web folder).
2. `python tools/sis/build_bundle.py --runtime warehouse --database <db> --schema <schema> --warehouse <wh>` (container: `--runtime container --pool <pool> --eai <pypi_integration>` or `--pypi-repo`) → `build/sis/` with its own `snowflake.yml` and `post_deploy.sql`, rebuilt from scratch. Layout options: `--api`, `--web-dist`, `--include`, `--data` (`spa.md`).
3. `python tools/sis/check_bundle.py` → `bundle OK`.
4. `cd build/sis && snow streamlit deploy --replace --prune --connection <dev>`: `--prune` deletes stage files the new bundle no longer has.
5. Run `build/sis/post_deploy.sql`: the artifact-repository step when `--pypi-repo` was used, and `DESCRIBE STREAMLIT` to confirm the runtime. It is not an artifact.
- **SQL route** (no CLI): `REMOVE @<stage>/<app_folder>/` first, then `PUT 'file://…' @<stage>/<app_folder>/<sub> AUTO_COMPRESS=FALSE OVERWRITE=TRUE` per folder, then `CREATE OR REPLACE STREAMLIT … FROM @<stage>/<app_folder> MAIN_FILE = 'streamlit_app.py' QUERY_WAREHOUSE = … RUNTIME_NAME = '…'` and `ALTER STREAMLIT … ADD LIVE VERSION FROM LAST`.
  - A `PUT` glob skips dotfiles (`.streamlit/`) and can't match folders → one PUT per file in folders with subfolders or dotfiles.
  - The local path is a quoted glob with no documented escape → refuse to run from a path containing `'`, `[` or `]` (before the REMOVE empties the stage).
  - `CREATE OR REPLACE` drops grants → re-grant `USAGE` after each deploy.
- Container runtime installs from PyPI, or nothing installs (FastAPI, httpx): `external_access_integrations` in `snowflake.yml` (`--eai`, documented field), or the shared PyPI artifact repository (`--pypi-repo` → `ALTER STREAMLIT … SET ARTIFACT_REPOSITORIES = (snowflake.snowpark.pypi_shared_repository)` in `post_deploy.sql`, with database role `SNOWFLAKE.PYPI_REPOSITORY_USER`; the ALTER form is not verified). `check_bundle.py` fails when neither is set.
- Viewers on a restricted network need `*.snowflake.app`, `*.snowflake.com` (container: also `*.snowflakecomputing.app`) and WebSockets allowed; a blocked frame looks like a blank widget. check: the SiS network page.

## Smoke test (first deploy on an account, and after any Streamlit version change)
- Widget visible, not blank; height fits its content.
- `DESCRIBE STREAMLIT` shows the runtime the files were built for.
- Click → the Python text under it shows the value (two-way works) → `declare_component(path=…)` and the instance `on_change=` callback work on this account and runtime.
- Theme follows the app; switch Snowsight to dark if the app allows it.
- Browser console (or the app's "Browser checks"): no CSP violation, no 404.
- Prebuilt app: the first screen loads its data; a write action is hidden, and if called answers 409; a large export shows "too large", not a hang.
- Blank or no value back → `failures.md`; if v1 `path=` is not served there, switch to `choice_static` + a native widget, or to the container runtime.

## Container runtime differences
| | Warehouse | Container |
|---|---|---|
| Component API | v1 only | v2 preferred (package with `asset_dir`); v1 works |
| Dependency file | `environment.yml` (Snowflake channel) | `pyproject.toml` or `requirements.txt` (PyPI via an external access integration) |
| Packaged widget | Files in the app folder (this template) | A wheel with the built assets, installed from the index, or the same app-folder layout |
| Message size | 32 MB fixed | 200 MB default, configurable |
| Main file | Source root | Anywhere in the source folder |
| Cache | Per session | Shared across viewers: never cache per-user args there |
- Compute pool: the app's node keeps running until about three days of viewer inactivity, and only then does the pool's auto-suspend apply → suspend the pool when done, or use a shared pool. check: SiS container-runtime cost page.
- Moving a v1 widget to v2: `setValue` → `setStateValue` / `setTriggerValue`, render args → `data`, the bridge goes away, the default export receives `parentElement`. Build: `npm run build:v2` (`vite.v2.config.ts`, `src/v2.tsx`) → `component/dist-v2/widget.js`; mount with `widget.choice_v2` (`mount.md`).
