# Common failures

| Symptom | Cause | Fix |
|---|---|---|
| Blank widget, 404 for `/assets/index-….js` in the console | `base: "/"` (Vite default) | `base: "./"`; better, the inline build (one file, no asset requests) |
| Blank widget, CSP violation in the console | A CDN script, style or font URL; `eval()` / `new Function()` in a library | Bundle it; replace the library; `check_dist.py` names the line type |
| Blank widget, no console error | `componentReady` never sent, or the render handler throws on missing args | Send `componentReady` once at load; default every arg (`a.options ?? []`) |
| Widget works locally, blank in Snowflake | `component/dist/index.html` not in `artifacts`, or deployed under another path | Add the exact path; check the app's Files tab; `check_dist.py` |
| Works locally only with `npm run dev` running | `url=` left in `declare_component` | `url` only from `WIDGET_DEV_URL`; unset it and test the built mode |
| Deploy slow, thousands of files uploaded | `component/` or `.` in `artifacts` → `node_modules` uploaded | List `component/dist/index.html` only |
| Old UI after a deploy | Build not rerun after a source change, or the build not committed | Rebuild, commit both; the stale-hash error catches it |
| `check_dist.py`: stale, but nothing changed | A new file not `git add`ed before the build, or a line-ending-only change in an untracked file | `git add component/frontend`, rebuild |
| Build throws "git tracks no files here" | Source never added to git | `git add component/frontend`, then build |
| Value never reaches Python | Static mount (`components.html`) used; or v1 `path=` not served on this account | Use `choice()`; if the smoke test fails, native widget + `choice_static`, or container runtime + v2 |
| `st.components.v2` error on the warehouse runtime | v2 unsupported there | v1 (this template) or the container runtime |
| Script reruns on every keystroke or mouse move | `setValue` in `onChange` / `onMouseMove` | Send on commit; debounce |
| Value resets or jumps back | React keeps its own state and ignores new args, or Python never stores the value | Python stores it (`st.session_state`) and passes `value`; React syncs local state from props |
| Two widgets share one value | Same `key`, or no `key` with identical args | A distinct `key` per instance |
| Widget cut off or with an inner scrollbar | No `setFrameHeight` | `ResizeObserver` → `setHeight(scrollHeight)`; static mount: larger `height=` |
| Dropdown or tooltip clipped | It can't leave the iframe | Open inline, or grow the frame while open |
| Colours wrong in dark mode | Hard-coded colours; theme not applied | CSS variables from the render message's `theme` |
| `MessageSizeError` | Args or the static page over 32 MB (warehouse) | Aggregate in Python, paginate, pass fewer columns |
| `DeprecationWarning` on `declare_component` | Called as `st.components.v1.declare_component` | `import streamlit.components.v1 as components`; `components.declare_component(…)` |
| `TypeError: unsupported operand type(s) for \|` at import | `str \| None` on Python < 3.10 | Pin `python=3.11.*` or add `from __future__ import annotations` |
| Streamlit version unavailable at deploy | `environment.yml` pins a version the warehouse runtime does not offer | Pick one from the Snowsight package picker |
| AppTest: `UnknownElement`, value always None | AppTest does not render components | Patch `widget._component` (`testing.md`) |
| Vitest hangs starting workers on Windows | Forks pool | `test: { pool: "threads" }` |
| `npm ci` fails: no lock file | The template ships none | `npm install` once, commit `package-lock.json` |
| v2 widget unstyled or wrong colours | Variables declared on `:root`, which a shadow root lacks | Declare them on the widget element as `var(--st-…, fallback)` (template `widget.css`) |
| Build stops: "second JS chunk" / "want one JS file" | A dynamic `import()` in the widget | Import statically |
| Text from data renders as HTML | `dangerouslySetInnerHTML` | Render as React text; never inject table values or LLM output as HTML |

## Prebuilt app (SPA mode)
| Symptom | Cause | Fix |
|---|---|---|
| Stuck on "Loading…", "Browser checks" says the bridge has not run | Bridge script blocked or failed to load | Read the CSP lines under Browser checks; frame mode: `frame/index.html` names files that are not there → `check_bundle.py` |
| Frame loads, fonts or images missing | CSS still says `url(/assets/…)` | Rewrite to relative in the build script (`build_bundle.py` does) |
| Every request "did not answer" after 300 s | `on_batch` not wired (`on_change` v1 / `on_batch_change` v2), or the batch handler raised | Wire the callback; read the app's error under the page; one failing request must return 500, not raise |
| Same screen loads forever after one request | Answers sent without `batch_id`, or the page ignores them as stale | Echo the batch id; one batch in flight |
| Whole page reruns and flickers on each request | Mount not inside `st.fragment` | Wrap the mount in a fragment |
| `HTTP 413` under Browser checks | One response over 24 MB | Page or aggregate in the API; never raise the cap above the 32 MB message limit |
| Settings or refresh "do nothing" | Write blocked (409) when hosted | Expected; hide the control with `HOSTED`; ship the setting as config |
| v2: `SyntaxError: import/export` | Bundle wrapped in `startApp()` has module-level imports | One chunk, no dynamic `import()`; `check_bundle.py` flags it |
| v2: the app finds no `#root` | `isolate_styles=True` put it in a shadow root | `isolate_styles=False` for a whole app |
| v2: JS string treated as a file name | One-line string | Wrap with newlines (the template does) |
| `FileNotFoundError` for the bundle | More than one or no `index-*.js` | Empty the build folder before building; one entry chunk |
| A key or `.env` on the stage | Folder copied without an ignore list | Rebuild with `build_bundle.py`; `check_bundle.py` fails on secret-looking names; rotate the key |
| Old files or the other runtime's files still deployed | Bundle reused or deploy without `--prune` | Rebuild from scratch; `--prune`, or REMOVE then PUT |
| App created on the wrong runtime | `RUNTIME_NAME` left out, or the CLI ignored `runtime_name` in `snowflake.yml` | `DESCRIBE STREAMLIT` after deploy; recreate with SQL `CREATE STREAMLIT … RUNTIME_NAME = '…'` |
| Container app: `ModuleNotFoundError: fastapi` | No PyPI access | `--eai <integration>` or `--pypi-repo` + `post_deploy.sql` |
| `build_bundle.py` stops: "check_data() is not filled in" | `--data` used before the content check exists | Write the check that refuses test/demo data, then rerun |
