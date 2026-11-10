# Layout, data display, charts, theme

What goes where, colours, words: `darshan-singh-meel-frontend`. This file is how to build it.

## Layout
| Need | Use |
|---|---|
| Side by side | `st.columns` |
| Group, border, fixed height | `st.container` |
| Alternative views | `st.tabs` |
| Optional detail | `st.expander`, `st.popover` |
| Global filters, navigation | `st.sidebar` |
| Modal | `@st.dialog` |
| Placeholder to fill or replace | `st.empty` |
| Pinned to the bottom (chat input) | `st.bottom` |
| Vertical gap | `st.space` |

- Filters for the whole page → sidebar; filters for one chart → next to it.
- KPI row: `st.columns` + `st.metric`, units and time range in the label.
- Columns stack on narrow screens; keep to 4 or fewer and check mobile width.
- Docs: docs.streamlit.io/develop/api-reference/layout

## Tables — `st.dataframe`
- Sizing: `width="stretch" | "content" | int`, `height="auto" | "content" | "stretch" | int`. `use_container_width` is deprecated.
- `column_config`: label, format, and type per column (`st.column_config.NumberColumn`, `LinkColumn`, `ProgressColumn`, `DateColumn`, …). `None` hides a column; `"_index"` targets the index.
- Row, column, or cell selection: `on_select="rerun"` + `selection_mode`; the call returns the selection.
- Above 150,000 rows it loads lazily; search, CSV download, `on_select`, and Styler stop working there.
- Hidden columns are not a security control. `client.disableDataExport=true` turns off download and copy.
- Docs: docs.streamlit.io/develop/api-reference/data/st.dataframe

## Editing — `st.data_editor`
- `num_rows`: `"fixed"` (default), `"dynamic"`, `"add"`, `"delete"`. `disabled=True` or a column list locks cells.
- Returns the edited data. With `key`, `st.session_state[key]` holds `edited_rows`, `added_rows`, `deleted_rows` (read-only) → write back only the changes.
- Edits reset when the input's columns, dtypes, row count, or index change → keep the input stable (cache it).
- No lazy loading; mixed-type columns can't be edited.
- Docs: docs.streamlit.io/develop/api-reference/data/st.data_editor

## Charts
| Need | Use |
|---|---|
| Line, bar, area, scatter | `st.line_chart`, `st.bar_chart`, `st.area_chart`, `st.scatter_chart` |
| More control, layered, faceted | `st.altair_chart` |
| 3D, scientific (violin, ternary), an existing Plotly figure | `st.plotly_chart` |

- Built-ins and Altair are the default: they follow the app theme and need no extra package.
- Selections: `on_select="rerun"` with a `key`.
- Chart colours from the theme, not hard-coded per chart.
- Docs: docs.streamlit.io/develop/api-reference/charts

## Theme and config
- `.streamlit/config.toml`, committed. `[theme]` plus `[theme.light]`, `[theme.dark]`, and their `.sidebar` tables: fonts, text and background colours, primary colour, borders, radius, chart colours.
- Map the frontend plan's tokens (ground, surface, ink, accent) to theme keys. Check the exact key names on the config reference page before writing them.
- Theme edits apply live on save; `[server]` options need a restart.
- `client.toolbarMode = "viewer"` (or `"minimal"`) for deployed apps.
- No CSS injected through `st.markdown(unsafe_allow_html=True)` to restyle widgets — it breaks on upgrades. Theme first; what the theme can't do stays default.
- Docs: docs.streamlit.io/develop/concepts/configuration/theming · docs.streamlit.io/develop/api-reference/configuration/config.toml
