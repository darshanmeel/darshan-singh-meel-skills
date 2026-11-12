# Prebuilt React app in Streamlit (SPA mode)

A whole single-page app, already built by Vite for its own server, runs inside SiS. Streamlit is only the shell; the app's own Python API answers in the Streamlit process. Templates: `templates/spa/`.

## When
- A React app with a Python API exists (FastAPI or another ASGI app) and must also run inside Snowflake, with the same code.
- Not for a new app: build it in Streamlit, with a widget only where needed (widget mode).
- Not when the API needs a login, a local file the viewer chooses, or writes shared state: the hosted copy is read-only.

## How it works
```
browser: React build ── fetch("/api/x") ──▶ bridge_core.js (patched fetch, queue)
          ▲                                        │ batch ≤ 8 requests, 15 ms after the first
          │ new Response(body)                     ▼ setComponentValue (v1) / setTriggerValue (v2)
          │                              streamlit_app.py on_batch → fragment rerun
          │                                        │ thread pool (4) → bridge_server.answer()
          └── render args.out ◀── pack() ≤ 24 MB ◀── TestClient(app): in-process, no port
```
- The browser can't reach a port on Snowflake's side, and the CSP blocks other origins: the only channel is the component's value (page → Python) and its render args (Python → page).
- One batch in flight. Python answers it, stores `{batch_id, responses, retry}` in session state, the fragment rerenders the component with it, the bridge resolves each `fetch` promise with a real `Response`.
- `st.fragment` around the mount: a batch reruns the fragment, not the page.
- v1 and v2 differ only in the connector file: `bridge_frame.js` (postMessage, `args.out`) or `bridge_container.js` (default export, `setTriggerValue("batch", …)`, `data.out`).

## Bridge rules (templates follow them)
| Rule | Value | Why |
|---|---|---|
| Intercept only | string URLs starting `/api/` | Everything else (data: URIs, the bundle) uses the real `fetch` |
| Batch | max 8, sent 15 ms after the first request | One rerun per page load burst, not one per request |
| Timeout | 300 s per batch → every request in it rejects "The app did not answer. Reload the page." | A lost rerun never hangs the page silently |
| Stale answers | ignored unless `batch_id` = the one in flight | Every rerun re-sends the last args |
| Size cap | 24 MB per answer message | Warehouse runtime caps a message at 32 MB, fixed |
| Over the cap | first responses kept; the rest returned as `retry` ids and re-sent next batch; one response over 24 MB alone → 413 | The page shows "too large", never a broken frame |
| No-body statuses | 101, 204, 205, 304 → `new Response(null, …)` | `Response` throws on a body there |
| Dropped headers | `content-length`, `content-encoding`, `transfer-encoding` | The client already decoded the body |
| Request shape | method, path, string body, plain-object headers | It travels as JSON; `FormData`, `Blob`, `Headers` objects don't |
| Errors | 500 with the exception type only | No message text, no data, no stack in the page |
| Start order | the app bundle starts after the first render | `fetch` is patched and a sender exists before the app's first request |
| Diagnostics | CSP violations and script errors listed in a "Browser checks" `<pre>` | A blocked script fails silently otherwise |

## Read-only when hosted
- Every viewer shares one copy of the app's data and runs under the owner role. A write (settings, refresh, upload) would reach everyone or needs a login the hosted app doesn't have.
- Server: any method other than GET/HEAD → 409 "Read-only in the hosted app.", unless listed in `ALLOWED_WRITES` (e.g. a search sent as POST). Enforced in Python, not only hidden.
- Page: the bridge sets `window.APP_HOSTED = true` before the app starts. The app reads it in one place (`export const HOSTED = !!window.APP_HOSTED`) and hides write actions (refresh, settings, upload).
- What the viewer can't change (masking, thresholds) is set before the deploy and shipped as config.

## API in process
- `fastapi.testclient.TestClient(app, raise_server_exceptions=False)`, created once with `st.cache_resource`. Needs `httpx` in the environment.
- Not ASGI (Flask, plain functions)? Replace `call()` in `streamlit_app.py` with a dispatcher returning `(status, text, headers)`; `bridge_server.py` stays as it is.
- The import in `client()` names the API folder `--api` copied (default `api.main:app`).
- The API must not start background threads, schedulers or a server on import; anything that needs a login or the network → off when hosted.
- Shared resources (one DB connection, caches) as the local server would set them; `st.cache_resource` is per server process.
- Data the app reads ships with it (a DuckDB or SQLite file) or comes from Snowflake through the session. Shipped data:
  - data files (`*.duckdb*`, `*.db`, `*.sqlite*`, `*.parquet`, `*.csv`) are never copied with the code; ship one with `--data FILE` into `data/`. `check_bundle.py` fails on a data file anywhere else;
  - `--data` calls `check_data(path)` first, which stops the build until it is filled in: refuse test, demo or fake data by content (a marker row the fixtures carry), not by file name;
  - every viewer granted the app sees all of it, whatever their own role → mask at export time, not in the UI.

## Build: reuse the app's own build
- The app keeps its normal Vite build (`base: "/"`, hashed `assets/index-*.js` and `.css`, fonts as files). No second Vite config; `build_bundle.py` adapts it.
- **Warehouse (v1):** `frame/` = `index.html` written by the build script + the app's `assets/` + the bridge scripts.
  - CSS `url(/assets/…)` → `url(…)`: the frame is served under the component's path, so root-relative URLs point at nothing.
  - `<body data-bundle="assets/index-*.js">`; `bridge_frame.js` injects that module after the first render.
- **Container (v2):** no file serving. Python reads the build and passes strings:
  - `js` = `function startApp() {\n<bundle>\n}\n` + `bridge_core.js` + `bridge_container.js`. The bundle must be one chunk with no module-level `import`/`export` (`check_bundle.py`).
  - `css` = the app CSS with font `url()`s replaced by `data:font/woff2;base64,…`.
  - `html` = the root element plus the checks `<pre>`; `isolate_styles=False`, because the app finds `#root` in the document.
  - A one-line string is read as a file path; the newlines in the wrapped code mark it as inline.
- Exactly one `index-*.js` and one `index-*.css`: empty the build folder before each build (`emptyOutDir`).
- No code splitting: container → one JS file and no `import(` (`check_bundle.py`); frame → no `"/assets/…"` in JS (a lazy chunk or preload with base `/` points at nothing). Vite: no dynamic `import()` in the app, or `build.rollupOptions.output.inlineDynamicImports` (check the option name for the pinned Vite).

## Bundle folder (what Snowflake gets)
- `build_bundle.py` writes `build/sis/` (git-ignored) fresh each time: shell, `bridge_server.py`, the API package (`--api`, default `api`), `config/` if present, anything in `--include`, `frame/` or `dist/assets` (from `--web-dist`, default `web/dist`) + bridge, `.streamlit/config.toml` (`toolbarMode = "minimal"`), `environment.yml` or `requirements.txt`, its own `snowflake.yml` (names from `--database`, `--schema`, `--warehouse`, `--app`), and `post_deploy.sql` (not an artifact).
- One secret list, `SECRETS` + `SECRET_DIRS` in `check_bundle.py`, imported by `build_bundle.py`: `.env*`, `*.pem`, `*.key`, `*.p8`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `id_rsa*`/`id_dsa*`/`id_ecdsa*`/`id_ed25519*`, `credentials*`, `*credentials*.json`, `*service*account*.json`, `secrets*`, `*.tfvars`, `*.tfstate*`, `.npmrc`, `.pypirc`, `.netrc`, `.git-credentials`, `kubeconfig*`, `connections.toml`, `profiles.yml`, and folders `.snowflake`, `.ssh`, `.aws`, `.kube`, `.docker`, `.gnupg`. The build skips them; the check fails on any left (name only, never read).
- Deleted and rebuilt each time, and deployed with `--prune` (or REMOVE then PUT on the SQL route): files from an older build or the other runtime never ship.

## Limits that stay
- Every batch is a Streamlit rerun: slower than a local server; many small requests on one screen → fewer, larger API calls.
- Links: on the warehouse runtime the app is in a frame, so its URL hash never reaches the browser bar; a "copy link" copies the frame's URL.
- Cost: the warehouse stays on while a tab is open (activity keeps it awake); set a sleep timer. Container: the compute pool bills while the app's node runs.
- Untested on the account until the smoke test passes (`deploy.md`).
