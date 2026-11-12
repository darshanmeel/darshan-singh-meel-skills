# Sources

Checked 2026-11. Statuses and supported versions change; recheck before relying on a limit.

| Fact | Page |
|---|---|
| Warehouse runtime: components v2 not supported; v1 `html` / `iframe` supported; container runtime supports v2 incl. package-based; no scripts from external domains | docs.snowflake.com/en/developer-guide/streamlit/limitations |
| CSP: external scripts, styles, iframes and `eval()` blocked; images, media, fonts from any HTTPS domain allowed | docs.snowflake.com/en/developer-guide/streamlit/limitations |
| 32 MB message limit on the warehouse runtime, not configurable; container 200 MB default | docs.snowflake.com/en/developer-guide/streamlit/limitations |
| Third-party components: their own licence, at the user's risk | docs.snowflake.com/en/developer-guide/streamlit/additional-features |
| Warehouse runtime: Streamlit 1.22+ limited selection, Snowflake Conda channel via `environment.yml`; container 1.50+ from PyPI | docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments |
| Warehouse runtime: main file at the source root | docs.snowflake.com/en/developer-guide/streamlit/app-development/file-organization |
| `declare_component(name, path=None, url=None)`; `url` takes precedence over `path` when both are given (the template passes one); calling `st.components.v1.declare_component` directly instead of importing its module is deprecated | docs.streamlit.io/develop/api-reference/custom-components/st.components.v1.declare_component |
| v1 frontend API: `setComponentValue`, `setFrameHeight`, `RENDER_EVENT`, theme needs `streamlit-component-lib` ≥ 1.2.0 | docs.streamlit.io/develop/concepts/custom-components/components-v1/intro |
| v2 theme variables (`--st-primary-color` …), injected into the component wrapper, also with `isolate_styles=True` | docs.streamlit.io/develop/concepts/custom-components/components-v2/theming |
| `st.html(body, *, width, unsafe_allow_javascript=False)`: not iframed, JavaScript off by default, DOMPurify | docs.streamlit.io/develop/api-reference/text/st.html |
| `RUNTIME_NAME` omitted → container runtime since behaviour change 2026_06 | docs.snowflake.com/en/release-notes/bcr-bundles/2026_06/bcr-2342 (as cited in `darshan-singh-meel-streamlit-snowflake`) |
| Build options (`base`, `outDir`, `assetsInlineLimit`, `cssCodeSplit`, `modulePreload`) and plugin hooks | vite.dev/config/build-options · vite.dev/guide/api-plugin |

## Not verified
- `declare_component(path=…)` on the warehouse runtime: the limitations page lists only `components.html` / `.iframe` as supported v1 APIs; a Snowflake release note is reported to allow custom components that make no external calls (release note not located). The smoke test in `deploy.md` settles it per account.
- Prebuilt-app mode end to end in Snowflake (packages such as FastAPI/httpx on the Snowflake channel, the CSP with an injected module script, speed of batched reruns): built and run with Streamlit locally only.
- The v2 inline-string rule (one line = file path, a newline = inline code): from working code, not from a docs page.
- PyPI installs on the container runtime through the shared artifact repository: from working deploy code; check the dependency-management page.
- Raw v1 message names and fields: taken from `streamlit-component-lib`'s source, not from a docs page.
- Artifact paths keeping their folder on the app stage: check the Files tab after the first deploy.
- Theme fields in the render message on the oldest warehouse-runtime Streamlit versions.
- Stage file-size limits for app files: not on the SiS pages.
- `runtime_name` and `compute_pool` as `snowflake.yml` fields: used here and in `darshan-singh-meel-streamlit-snowflake`, not found on the CLI project-definition page. If the CLI ignores them the app lands on the default runtime → `DESCRIBE STREAMLIT` after every first deploy (`post_deploy.sql`); fallback: SQL `CREATE STREAMLIT … RUNTIME_NAME = '…'` (documented).
- The default runtime: BCR-2342 (2026_06) says an omitted `RUNTIME_NAME` means the container runtime; the `CREATE STREAMLIT` reference page may still describe the warehouse runtime as the default. Naming it explicitly makes the difference irrelevant.
- `on_change=` on a v1 component instance (`component(..., on_change=cb)`): used by working code, not on the `declare_component` page. The smoke test (a click reaches Python) covers it.
- `ALTER STREAMLIT … SET ARTIFACT_REPOSITORIES = (snowflake.snowpark.pypi_shared_repository)` after a CLI deploy: from working `CREATE STREAMLIT` code; the `ALTER` form is not checked. `external_access_integrations` in `snowflake.yml` is the documented route.
- npm versions in `package.json` (React 19.3, Vite 8, TypeScript 7, Vitest 5): from `darshan-singh-meel-frontend-react`, not installed with this template; no lock file ships.
