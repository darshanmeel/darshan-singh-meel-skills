# Stacks: what the target technology can and cannot render

The design is HTML on the canvas; the implementation is React or Streamlit. Design within what the stack can build, and say in `spec.md` where the HTML and the stack differ.

## Plain HTML / CSS (small tools, the canvas itself)
- Everything in the directions is buildable as is. Deliver `final/index.html` + `tokens.css`; the implementer copies the structure, not the file.

## React (Vite or Next.js, shadcn/ui or the project's library)
- Anything on the canvas is buildable. Map each component in `spec.md` → Components to an existing component (read the project's `src/components`, `package.json` for the library) or mark it new.
- Tokens → the project's CSS variables or Tailwind theme. With Tailwind, `tokens.css` stays the source and `tailwind.config` reads `var(--…)`; do not duplicate values. shadcn/ui expects its own variable names (`--background`, `--foreground`, `--primary`…): add a bridge block that maps them to the tokens - check: ui.shadcn.com/docs/theming.
- Dark mode: the project's mechanism (`class="dark"` or `data-theme`) sets `color-scheme`; `light-dark()` tokens then follow. If the project lacks `color-scheme` handling, say so in the spec.
- Charts: the design's bars and sparklines become the project's chart library; keep the data labels and colours as specified.
- Build skill: `darshan-singh-meel-frontend-react`.

## Streamlit (open source and in Snowflake)
Streamlit renders its own components; CSS hacks against its DOM are not allowed by `darshan-singh-meel-streamlit`. Design to what the API offers:

| Design element | Streamlit | Note |
|---|---|---|
| Page structure | `st.set_page_config(layout="wide")`, `st.sidebar`, `st.columns`, `st.container(border=True)`, `st.tabs`, `st.expander` | no CSS grid; column widths are ratios; no sticky elements |
| Navigation | `st.navigation` + `st.Page` (multipage), sidebar | top bar nav is not native |
| KPI | `st.metric(label, value, delta)` in columns | delta colour is fixed (green up / red down, `delta_color="inverse"` to flip) |
| Status badge | `st.badge`, `:green[...]` Markdown colours, `st.status` | limited palette names |
| Table | `st.dataframe` with `column_config` (progress, bar, link, date columns), `st.data_editor` | row click selection via `on_select`; no custom cell HTML |
| Cards | `st.container(border=True)` | one border style; no accent edge |
| Buttons | `st.button(type="primary"|"secondary"|"tertiary")`, `st.link_button`, `st.download_button` | one primary colour |
| Forms | `st.form`, inputs, validation by your code after submit | no inline-on-blur validation |
| Charts | `st.bar_chart`, `st.line_chart`, `st.altair_chart`, `st.plotly_chart` | colours via the chart library |
| Empty / error | `st.info`, `st.warning`, `st.error`, `st.empty()` | fixed shapes and icons |
| Detail panel | `st.dialog` (modal), second column, expander | no side drawer |
| Loading | `st.spinner`, `st.skeleton` (newer versions), fragments for partial refresh | - |

- **Theme tokens** → `.streamlit/config.toml` `[theme]`: `primaryColor` = `--accent`, `backgroundColor` = `--bg`, `secondaryBackgroundColor` = `--surface-2`, `textColor` = `--ink`, `font` = family name; newer versions add `base`, `baseRadius`, `borderColor`, `linkColor`, `codeFont`, `headingFont`, `baseFontSize`, `[theme.sidebar]` and `[[theme.fontFaces]]` for a font file - check: docs.streamlit.io, "Theming" and `config.toml` reference, for the version the project pins. Colours must be hex or named in `config.toml`: convert the OKLCH tokens (`check_design.py` prints no hex; use a one-line Python conversion with its `srgb()` function).
- **Light and dark**: two theme configs are possible in recent versions (`[theme]` + `[theme.dark]` or a base switch) - check: the same page; otherwise the app follows the user's system theme with one palette.
- **Directions for Streamlit** differ in page structure and widget choice (sidebar filters vs. inline chips, metrics row vs. exceptions list, dataframe vs. cards), not in custom styling. Draw them on the canvas as HTML that uses only shapes Streamlit has (one border style, one primary colour, stacked blocks), and write the widget per element in `spec.md`.
- Streamlit in Snowflake lags behind open-source Streamlit: check the supported version before using `st.badge`, `st.dialog`, `column_config` options or theme keys (`darshan-singh-meel-streamlit-snowflake`).
- Build skill: `darshan-singh-meel-streamlit` (+ `-snowflake`). A React component inside Streamlit is the last resort and needs its own justification in the spec.

## What the design never does
- Edit application code, config, theme files or dependencies. The output is `designs/<name>/`; the implementing agent changes the project.
- Promise an interaction the stack cannot build (hover-only information in Streamlit, sticky columns, custom cell rendering) without naming the fallback in the spec.
