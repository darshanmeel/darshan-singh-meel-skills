# Mount: how Python shows the widget

Docs: docs.snowflake.com/en/developer-guide/streamlit/limitations · docs.streamlit.io/develop/api-reference/custom-components

## Which mount where
| Mount | Warehouse runtime | Container runtime | Values back to Python |
|---|---|---|---|
| `components.declare_component(name, path=dist)` (v1) | Not listed in the SiS docs; **smoke-test first** (`deploy.md`) | Works | Yes, one JSON value per widget |
| `components.html(page, height=…)` with the args inlined (v1) | Supported (docs) | Supported | No |
| `st.components.v2.component(…)` | **Not supported** | Supported, incl. package-based | Yes, named states and triggers |
| `st.html(…, unsafe_allow_javascript=True)` | Depends on the offered Streamlit version | Works | No; not iframed, runs in the app page → never with untrusted input |

- Template builds once and serves both v1 mounts: `widget.choice()` (two-way) and `widget.choice_static()` (one-way); `npm run build:v2` adds `widget.choice_v2()` for the container runtime.
- Smoke test fails on the account → keep the React part, switch pages to `choice_static`, and collect the value with a native widget next to it (`st.segmented_control`, `st.selectbox`), or move the app to the container runtime and v2.
- `components.html` / `.iframe` are deprecated since Streamlit 1.56 in favour of `st.iframe` / `st.html`; the warehouse runtime offers a limited set of versions → use what the pinned version has. check: docs.streamlit.io release notes before upgrading.
- One wrapper for both runtimes: `widget.py` sets `USE_V2` when only `component/dist-v2/widget.js` was deployed (the container `snowflake.yml` ships only that file), so `choice()` picks v2 there and v1 everywhere else, locally included. Never call v2 on the warehouse runtime.

## declare_component rules
- `import streamlit.components.v1 as components` and call `components.declare_component`: calling `st.components.v1.declare_component` directly is deprecated. Declaring it in a wrapper module (`widget.py`) keeps pages clean; that part is style, not a rule.
- `path` = absolute path of the build folder: `Path(__file__).parent / "component" / "dist"`. Never a relative string; the working directory differs between local and deployed.
- `url=` only for local hot reload, from an env var that is unset in Snowflake (`WIDGET_DEV_URL`). A hard-coded `url="http://localhost…"` fails `check_dist.py`.
- Name: short, unique in the app. Two widgets of the same kind on a page → different `key`s.
- Call signature: keyword args become the render `args`; `key`, `default` are reserved. `default` is returned until the widget sends its first value.

## Data contract
| Direction | How | Notes |
|---|---|---|
| Python → React | keyword args to the wrapper | JSON only (`str`, numbers, `bool`, `None`, lists, dicts). Aggregate in Python; no full tables |
| React → Python | `setValue(x)` in `bridge.ts` | One JSON value; several fields → one object. Every call reruns the script |
| Python → React (static mount) | JSON in `<script id="args" type="application/json">` | `<` escaped as `<`, so a value can never close the tag |

- Returned value stays until the widget sends another one. To reset from Python, change the `key` (new instance) or pass the wanted `value` in the args and let React show it.
- Python owns the state: keep the pick in `st.session_state`, pass it back as `value`; React keeps only a local copy for the moment between click and rerun.
- DataFrames: convert to records in Python (`df.to_dict("records")`) after aggregating. Arrow transfer (`dfs`) needs `streamlit-component-lib`.

## Bridge messages (components v1)
All `window.parent.postMessage({isStreamlitMessage: true, type, …}, "*")`:
| Message | Sent by | Fields |
|---|---|---|
| `streamlit:componentReady` | widget, once on load | `apiVersion: 1` |
| `streamlit:render` | Streamlit, on every rerun | `args`, `disabled`, `theme` (`dfs` when Arrow is used) |
| `streamlit:setComponentValue` | widget | `value`, `dataType: "json"` |
| `streamlit:setFrameHeight` | widget | `height` (px) |

- Template's `bridge.ts` implements exactly these, and ignores messages whose `source` is not `window.parent`.
- These are the messages `streamlit-component-lib` sends (its `streamlit.ts`); the Streamlit docs document the lib's API, not the raw messages. A Streamlit upgrade that breaks the widget → compare with the lib first.

## Theme
- Render message carries `theme`: `base` (`light` / `dark`), `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `font`. Theme in the message needs a Streamlit version whose component API sends it (lib ≥ 1.2.0 era); older → fallbacks.
- `main.tsx` writes them to CSS variables (`--primary`, `--bg`, `--bg2`, `--text`, `--font`) on every render; CSS uses only the variables. Fallback values in `:root` = Streamlit's light defaults.
- `body { background: transparent }` so the iframe blends into the app.
- Static mount gets no theme → pass `theme` in the args if it matters, from the app's `.streamlit/config.toml` values.
- Fonts: the theme's `font` names a family the iframe does not have loaded → keep a system fallback in the stack; bundle a font file only if the design needs it (`build.md`).

## Components v2 (container runtime)
Docs: docs.streamlit.io/develop/concepts/custom-components/components-v2
- Build: `vite.v2.config.ts`, library mode → one ES module `component/dist-v2/widget.js` whose default export receives `{ data, parentElement, setStateValue, setTriggerValue }`. CSS imported with `?inline` and appended to `parentElement`.
- `define: { "process.env.NODE_ENV": '"production"' }`: library mode leaves `process.env` in React's code and the browser has no `process`.
- Python: `st.components.v2.component(name, html="<div></div>", js=code + "\n")`, cached with `st.cache_resource`. A one-line string is read as a file path; the newline marks inline code. A package with `asset_dir` (frontend-react skill) is the alternative for a reused widget.
- Mount: `result = comp(key=…, data={…}, default={"value": v}, on_value_change=lambda: None)` → `result.value`. Every key in `default` needs its `on_<key>_change`.
- Render, don't remount: the default export runs on every rerun with the same `parentElement`; keep the React root in a `WeakMap` keyed by it (template).
- `isolate_styles=True` (default) puts it in a shadow root: style isolation, not security. `False` only when the code looks things up in `document` (prebuilt-app mode).
- State that lasts → `setStateValue`; one-off events → `setTriggerValue` (prebuilt-app batches use a trigger).
- Theme: v2 provides `--st-primary-color`, `--st-background-color`, `--st-secondary-background-color`, `--st-text-color`, `--st-font` (and more), also inside the shadow root. A shadow root has no `:root`, so `widget.css` declares its variables on `.widget, .note` as `var(--st-…, fallback)`; under v1, `main.tsx` writes the same `--st-*` names from the render message.

## Height
- v1 iframes don't grow by themselves: send `setFrameHeight(document.documentElement.scrollHeight)` from a `ResizeObserver` on `body` (template does).
- Static mount: fixed `height=` in Python; pick the tallest state (empty, loaded, error) or allow `scrolling=True`.
- Popover, menu or tooltip can't leave the iframe → open inline, or grow the frame while it is open.
