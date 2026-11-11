# Custom components and embeds

Stop at the first that works:
1. Native widgets, `column_config`, built-in charts.
2. Static HTML → `st.html` (sanitised; JavaScript ignored unless explicitly allowed).
3. External page, or self-contained HTML with scripts → `st.iframe`.
4. Small interactive widget → inline component v2 (HTML/CSS/JS strings).
5. Stateful, reusable UI → packaged component v2 in React + TypeScript, built per `darshan-singh-meel-frontend-react`.

- `st.components.v1.html` and `.iframe` are deprecated (since 1.56) → `st.iframe` / `st.html`.
- v1 `declare_component`: only for a legacy component or a host without v2 (Snowflake warehouse runtime — see `darshan-singh-meel-streamlit-snowflake`).
- Third-party component packages: maintained ones only, pinned; each is code running in the user's browser.
- Docs: docs.streamlit.io/develop/concepts/custom-components

## Inline component v2
```python
import streamlit as st

counter = st.components.v2.component(
    "counter",
    html="<button id='add'>Add one</button>",
    js="""
    export default function (component) {
        const { parentElement, data, setStateValue } = component;
        parentElement.querySelector("#add").onclick = () =>
            setStateValue("count", data.count + 1);
    }
    """,
)

if "count" not in st.session_state:
    st.session_state.count = 0


def on_count():
    st.session_state.count = st.session_state.counter.count


counter(
    key="counter",
    data={"count": st.session_state.count},
    default={"count": 0},
    on_count_change=on_count,
)
st.write("Count:", st.session_state.count)
```
- Register once per app (`name` unique). Mount with keyword arguments: `key`, `data`, `default`, `on_<name>_change`, `width`, `height`.
- `data` is one-way, Python → JS (JSON, DataFrames as Arrow, bytes). JS → Python only through the setters; each call reruns the script → debounce noisy events in JS.
- **State** (`setStateValue`): persists across reruns; the callback fires on change. Every key in `default` needs an `on_<key>_change` (`lambda: None` is enough).
- **Trigger** (`setTriggerValue`): lasts one rerun, then `None`; for events (click, submit). Ignored inside `st.form`.
- Result: attributes on the returned object and, with `key`, in `st.session_state[key]`.
- `isolate_styles=True` (default) puts the component in a shadow root: style isolation, not a security boundary.
- Bundle all JS; no CDN scripts (blocked on hosts with a strict CSP).
- Docs: docs.streamlit.io/develop/concepts/custom-components/components-v2

## Packaged React component (v2)
- Scaffold from the official template, React + TypeScript option: `uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2`. Needs Node LTS and uv. It downloads from GitHub → ask first.
- Layout: the package's `pyproject.toml` has `[[tool.streamlit.component.components]]` (`name`, `asset_dir = "frontend/build"`); `frontend/` is built by Vite as an ES module with a hashed file name, `outDir` = `asset_dir`.
- Python side: `st.components.v2.component("<package>.<name>", js="index-*.js", html=" ")` — the glob must match exactly one file.
- React side: the default export receives the same `component` object; render into `parentElement`, read `data`, report through the setters. Component design, state, accessibility: `darshan-singh-meel-frontend-react`.
- Keep the contract small: props in through `data`, a few named states and triggers out. No app logic in the component.
- Follow the app theme (see the components v2 theming page) instead of hard-coded colours.
- Dev: `uv pip install -e .`, then `npm run dev` in `frontend/` and `streamlit run example.py` side by side. Release: `npm run build`, `uv build`. Pin Node and npm dependencies with the lock file.
- Test: component logic with the frontend's test runner; the Python wiring by running the example app.
- Docs: docs.streamlit.io/develop/concepts/custom-components/components-v2/package-based
