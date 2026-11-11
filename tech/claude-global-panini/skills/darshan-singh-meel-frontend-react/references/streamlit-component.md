# React component inside a Streamlit app

App-side rules (layout, state, caching, running in Snowflake): `darshan-singh-meel-streamlit`. This file covers only the React package.

## First: do you need one?
Usually not. Go through the option ladder in `darshan-singh-meel-streamlit` → `references/components.md` first; build a React package only at its last step (stateful or reused widget).
- Never render untrusted HTML (user input, database values, LLM output) in an iframe or with JavaScript enabled.

Docs: docs.streamlit.io/develop/concepts/custom-components (`/components-v2/…`, `/components-v1/…`, `/publish`)

## v2 package-based (React + TypeScript)
- **Scaffold:** `uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2` → choose React + TypeScript. Needs Python 3.11+, Node 24 LTS, uv.
- **Layout:**
```
pyproject.toml
my_component/
  pyproject.toml     [[tool.streamlit.component.components]] name, asset_dir = "frontend/build"
  __init__.py        registers and wraps the component
  frontend/          Vite library build → frontend/build/index-[hash].js
```
- Vite `outDir` must equal `asset_dir`.
- **Register (Python):** `st.components.v2.component("pkg.name", js="index-*.js", html=" ")`. The glob must match exactly one file: empty the build folder before each build.
- **Mount (Python):** call the returned object with `key`, `data`, `default`, `on_<name>_change`, `width`, `height`. The result exposes each state and trigger as an attribute (also under `st.session_state[key]`).
- **Entry (JS):** `export default function (component) { const { data, parentElement, setStateValue, setTriggerValue } = component; … }` — create a React root in `parentElement` and render; the template wires this up.

### Data contract
| Direction | How | Notes |
|---|---|---|
| Python → React | `data=` | JSON, DataFrame (Arrow, dtypes kept), or bytes. One-way |
| React → Python, lasting value | `setStateValue(key, value)` | Persists across reruns; callback fires on change. Each key in `default` needs an `on_<key>_change` (`lambda: None` is fine) |
| React → Python, event | `setTriggerValue(key, value)` | Lives for one rerun, then `None`; fires every time; ignored inside `st.form` |

- **Every setter call reruns the Python script.** Send on commit (blur, Enter, click, drag end), debounce continuous input; never send on every keystroke or mouse move.
- Python is the source of truth: React renders from `data`, keeps only transient UI state locally, and must survive being re-rendered with new `data`.
- To set the value from Python: write `st.session_state[key]`, rerun, and pass it back in `data`.
- Wrap the mount in one typed Python function (`def my_widget(rows, *, key=None) -> …`) so apps never touch the raw API.
- Keep `data` small: aggregate in Python; no full table for a widget that shows fifty rows. No PII unless the widget's job needs it.

### Styling
- Default `isolate_styles=True` puts the component in a shadow root: style isolation, not a security boundary.
- Follow the app theme through Streamlit's CSS variables (`/components-v2/theming`); no hard-coded colors, so light and dark both work.
- Size: `width: 100%; height: 100%` on the root; `ResizeObserver` only when exact pixels are needed.
- A full Tailwind + shadcn setup is usually too heavy here. Prefer plain CSS or CSS modules and a few Radix primitives; check that portals (dialogs, popovers) render inside the shadow root.

### Dev, test, release
- Dev: `uv pip install -e .` · `npm run dev` in `frontend/` · `streamlit run example.py` in a second terminal; refresh after changes.
- Test the React part like any component (`quality.md`); test the Python wrapper with a small example app.
- Release: `npm run build` → `uv build` → install the wheel or push to the internal package index. Public index only when asked; tokens come from the secret store, never the repo.
- Bundle everything: no CDN scripts, fonts, or styles loaded at runtime.

## v1 (`declare_component`): legacy only
- Dev: `declare_component("name", url="http://localhost:3001")`; release: `declare_component("name", path=<build dir>)`.
- React → Python: `Streamlit.setComponentValue(x)` (one value; wrap several in an object; each call reruns). Height: `Streamlit.setFrameHeight()`.
- Runs in an iframe: can't change app CSS, can't talk to other components, no built-in debouncing.
- Template: `streamlit/component-template`, folder `template/`. The docs disagree on the build script name (`npm run build` vs `npm run export`): read the template's `package.json`.

## Streamlit in Snowflake
Docs: docs.snowflake.com/en/developer-guide/streamlit/limitations
| Runtime | Components v2 | Components v1 |
|---|---|---|
| Container | Supported, including package-based | Supported |
| Warehouse | **Not supported** | `html` / `iframe` supported; packaged v1 components not confirmed, test first |

- Need a React component → use the container runtime.
- The content security policy blocks external scripts, styles, external-domain iframes, and `eval()` in both runtimes: the bundle must be fully self-contained. Images and fonts over HTTPS are allowed.
- The component gets data only through `data`; it never calls Snowflake or holds credentials.
