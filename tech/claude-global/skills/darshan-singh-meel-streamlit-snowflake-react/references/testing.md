# Tests

Docs: vitest.dev · testing-library.com · docs.streamlit.io/develop/concepts/app-testing

## Three layers
| Layer | Tool | What it proves | Template file |
|---|---|---|---|
| React | Vitest + Testing Library, jsdom | Renders each state from args; sends the right value once; read-only without a sender | `component/frontend/src/Widget.test.tsx` |
| Bridge | Vitest | The four v1 messages; ignores messages not from the host page | `component/frontend/src/bridge.test.ts` |
| Python | pytest + AppTest, component faked | The app passes the right args and uses the returned value; the static mount escapes args | `tests/test_widget.py` |
| Build | `tools/check_dist.py` (stdlib) | Built, from the committed source, self-contained, small, listed in `artifacts`, runtime named, no hard-coded dev URL; `dist-v2/widget.js` free of remote imports and `eval` | — |

## React
- Test the component with props, not through the bridge: `onPick` is a prop, `setValue` is wired in `main.tsx` only.
- Each state the widget can show: data, empty ("No options to show."), disabled. Add loading and error states when the args carry them.
- Assert on roles and accessible names (`getByRole("button", { name })`), `aria-pressed`, text; not on class names.
- `afterEach(cleanup)` when `globals` is off (template).
- Fixtures: synthetic values shaped like the real args; no real rows or names.

## Python
- AppTest does not render custom components → patch the module attribute the wrapper calls:
```python
with patch.object(widget, "_component", return_value="Weekly") as fake:
    at = AppTest.from_file(str(APP / "streamlit_app.py"), default_timeout=10).run()
assert fake.call_args.kwargs["options"] == [...]
```
- Patch `widget._component`, not `components.declare_component`: the declare runs at import, before the patch.
- One test per returned value that changes the page (None before the first click, a pick).
- `default_timeout=10`: cold imports exceed the 3 s default.
- The static-mount test needs the build → skipped with a reason when `component/dist/index.html` is missing.

## Build check
`python tools/check_dist.py [app folder]` → `dist OK` or one `ERROR` line per problem, exit 1:
- no build · no or stale source hash · `src`/`href` to anything but `data:`/`#` · CSS `url()`/`@import` to another site · `eval(` / `new Function(` · page over `MAX_BYTES` · build missing from `snowflake.yml` artifacts · frontend source in artifacts · no or unknown `runtime_name` · both builds shipped, or the wrong one for the runtime · globs (`component/**`, `**/*`) that ship the source · a `<…>` placeholder left in `snowflake.yml`, `environment.yml`, `requirements.txt`, `pyproject.toml` · a localhost URL anywhere in the root `.py` files · `dist-v2/widget.js` stale (its `/*! source-hash */` banner), remote, `eval`/`Function(`, or over the size budget.
- Hash skipped (note, not error) when git can't list the source (zip checkout, or source not yet added).

## Prebuilt app (SPA mode)
| Layer | Tool | What it proves |
|---|---|---|
| Server half | pytest on `bridge_server.py` (no Streamlit) | GET answered, headers dropped; writes → 409 unless allowed; exception → 500 with the type only; over the cap → rest retried; one too large → 413 |
| Bridge | Node or Vitest on `bridge_core.js` with a fake `send` | Only `/api/` intercepted; one batch of ≤ 8; stale `batch_id` ignored; responses resolve; `retry` re-sent; 204 has no body; timeout rejects |
| Bundle | `build_bundle.py` into a temp repo with planted secrets of every listed kind and data files → `check_bundle.py` | Secrets and data left out; config shipped; runtime named and known; placeholders filled; PyPI access on container; frame CSS and JS relative, refs exist; no CDN in JS or CSS; v2 one chunk, no import/export, under the cap; `--data` stops until `check_data()` exists |
| App | the app's own API tests and UI tests, unchanged | The same code runs locally and hosted |
| Hosted UI | a test that `HOSTED` hides each write action | Nothing writable is shown when hosted |
- The skill's `tests/run.py` runs all of these on the templates (Node part skipped when `node` is missing).
- Local end-to-end before the first deploy: `streamlit run build/sis/streamlit_app.py` from the bundle folder; the page must load its first screen through the bridge.

## Gate
One command before a change is done, every step reports, none stops the others:
```
python tools/check_dist.py && (cd component/frontend && npx tsc --noEmit && npx vitest run) ; pytest -q
```
- In a repo with a `tools/gate.py`, add the dist check and the web step there. Skip the web step (say "skip") when `npm` or `node_modules` is missing: the committed build plus `check_dist.py` still cover a Python-only checkout.
- CI: `npm ci` (lock file), then the gate, then the deploy.
- Not testable without an account: the CSP, the Snowsight frame, the runtime's Streamlit build → the smoke test in `deploy.md`.
