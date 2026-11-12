# Patterns from standalone React apps

Data apps that serve a Vite build from their own FastAPI server, and also ship the same build into SiS as a prebuilt app (`spa.md`), solve some of the same problems. What carries over, and what doesn't.

## Carries over
- **Committed build + source hash test.** The build is committed so users and the deploy need no Node; a test recomputes the hash of the tracked source and fails on a stale build. Here: `vite.config.ts` + `check_dist.py`.
- **"Loads nothing from other sites" test.** Every `src`/`href` in the built page is local; no Google Fonts host in HTML or CSS. Here: stricter (everything inlined), same check.
- **Fonts as local files** (`@fontsource`, latin subset, licence files beside them) instead of a font CDN.
- **Honest states.** A view draws a chart only when the data says it ran with rows; otherwise it shows why: not assessed (and the reason), failed, empty for this window, or rows exist but filters exclude them. Never a 0 or an empty chart for "didn't run". For a widget: Python sends an `outcome` with the args; React renders the note, not the chart, for every outcome but rows; Vitest covers each outcome with `it.each`.
- **One state module.** Only one place reads and writes shared UI state, merging keys additively so two writers never clobber each other. For a widget: the wrapper owns the value; one `value` arg in, one value out.
- **No `window` globals** (`Object.assign(window, …)`, `window.__x`) in the source; a test greps for them. Same here: the widget talks only through the bridge.
- **Role → views mapping as a pure function** (role in, list of pages out) with unit tests. For SiS: Python decides what a viewer sees (owner's rights, the viewer's role); the widget only renders the args it gets. Never filter sensitive rows in React.
- **A gate script** (stdlib) that runs every check, reports each, and skips the web step with a note when Node is missing.
- **Vitest `pool: "threads"`** on Windows.

## Changes per mode
| Standalone pattern | Widget mode | Prebuilt-app mode |
|---|---|---|
| View state in `location.hash` (shareable links, `history.replaceState`) | The widget is an iframe; its hash never reaches the app URL → `st.query_params` in Python, passed in as args | Hash works inside the frame/component, but a copied link may not reopen the same view |
| Theme script in `index.html` before first paint, from `localStorage` / `prefers-color-scheme` | Theme comes from the render message | Move that code into the connector (`bridge_frame.js` / `bridge_container.js`) before the app starts: `index.html` is not the app's own there |
| `fetch("/api/…")` to the app's own server | No API: Python passes data as args | Kept: the bridge routes it to the API in process |
| Dev proxy to a local API server | `WIDGET_DEV_URL` + `npm run dev`; data from Python | Keep it for local dev; the bundle is built from the same build |
| Server swaps the brand into `index.html` at request time | Pass it as an arg | Pass it in the render args; the connector sets it before the app starts, like `APP_HOSTED` |
| `index.html` never cached, hashed bundles cached | One inlined file; Streamlit serves it | Frame folder (v1) or strings (v2) |
| `base: "/"` | `base: "./"` | Kept; the bundle script rewrites CSS `url(/assets/…)` for the frame |
