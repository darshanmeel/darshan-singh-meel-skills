# Testing with AppTest

Headless: runs the script and exposes its elements; no browser. Docs: docs.streamlit.io/develop/concepts/app-testing/get-started

## Example (for the skeleton in `app.md`)
```python
# tests/test_app.py
from streamlit.testing.v1 import AppTest


def run_app():
    return AppTest.from_file("../app.py", default_timeout=10).run()  # path relative to this file; 10 s covers cold imports


def test_runs_clean():
    at = run_app()
    assert not at.exception


def test_region_list():
    at = run_app()
    assert at.selectbox(key="region").options == ["All", "North", "South"]


def test_filter_by_region():
    at = run_app()
    at.selectbox(key="region").set_value("North").run()
    assert at.metric[0].value == "165.50"
    assert len(at.dataframe[0].value) == 2
```
Run from the project root: `pytest tests/test_app.py`.

## Rules
- `.run()` after creating the app and after every interaction; nothing updates without it.
- Find elements by key (`at.button(key="save")`); an index (`at.button[0]`) breaks when the layout changes. Containers: `at.sidebar`, `at.columns[0]`, `at.tabs[0]`.
- Interact: `.set_value()`, `.click()`, `.select()`, `.increment()`. Assert on `.value`, `at.session_state`, `at.exception`, `at.error`.
- Preset before the first run: `at.session_state["k"] = v`, `at.secrets["k"] = v`.
- A `.streamlit/` folder where pytest runs supplies `config.toml` and `secrets.toml` to the app → run from the project root with test-only secrets.
- No live database in tests: patch the load function (`unittest.mock.patch`) or point `st.connection("env:VAR")` at a local SQLite file with synthetic rows.
- Multipage: test each page file directly (`AppTest.from_file("../views/overview.py")`); preset the session state the entrypoint would have set.
- Default timeout is 3 s; cold imports (pandas) exceed it on the first test → always set `default_timeout`.
- Values may be cast (selectbox options come back as strings) and not every element or parameter is inspectable → assert on data and state, not styling.
- Logic in `core.py` gets plain pytest tests; AppTest covers wiring and interactions only.
- Layout and mobile width: run the app and look; AppTest can't see them.
