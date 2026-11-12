# Brief spec — input to build.py
`<skill>` = this skill's folder. Run from the project root:
`python <skill>/references/templates/build.py generated-docs/_spec/requirements-brief-<slug>.json generated-docs/requirements-brief-<slug>.html`
- Prints WARN lines, a summary line (requirements by status, use cases without a source, decisions open, sources, options, work items), then `built <out>: 12 sections, N WARN`. ERROR lines stop the build.
- Rescans `inputs_dir` (default `generated-docs/_spec/inputs`) for requirement ids with `inputs.py`: every id found there must be a requirements row. Folder missing → `note:` and the spec's `inputs[].ids` alone are checked.
- Start from `examples/requirements-brief-example.json`; nothing of the example survives into a real brief. Builder tests: `python <skill>/tests/run.py`.
- Helpers next to it: `inputs.py` (inventory, ids, plain text, .gitignore entries), `profile.py` (structure-only data profile → `profile.json`), `skills.py` (installed skills that cover the confirmed stack).

## Fixed sections, free content
The top level is the same in every brief: 12 sections, these names, this order. The build refuses a missing or extra one.
Inside a section the content is chosen from the input: blocks sit directly in the section; a subsection is a named group with its own
heading, named from the input (a source, a conflict, a flow), never a wrapper title that fits any brief (the build warns on
"Overview", "Per need", "Linking rules", "What the sample shows", the section's name, a block type, …). One exception: in section 11 the
groups "Gaps", "Assumptions", "Risks" and "Open points" are the content and are allowed as titles. A section with nothing to say is one `line`.

| # | Section | Holds | Typical blocks |
|---|---|---|---|
| 1 | At a glance | goal, outcome, scope in/out, MVP vs later, source count, refresh, given stack; the build appends the Status row (counts from the rows, also when the section is one line) | `facts` |
| 2 | Context | sources → ingestion → platform → consumers; how the given stack fits | `flow`, `bullets` |
| 3 | Requirements | every requirement with the input's own id and a status; conflicts and how we resolve them | `requirements`, `bullets` |
| 4 | Sources and data | per source: system, connector, key, cadence, data points; sources not yet defined as `planned` | `sources` (one subsection per source, or one block for all) |
| 5 | Identity and linking | entities, identifiers, what joins what; linking rules | `links`, `bullets` |
| 6 | Flows | a timeline or flow only where it explains (batch window, hand-offs); else one line | `timeline`, `flow` |
| 7 | Use cases and data needs | consumer or tactic → data needed → sources; rows with no source are flagged, partly covered rows say what is `missing` | `needs` |
| 8 | Data findings | profile of supplied data (structure only), what it shows, requirement vs data; no data → one line | `profile`, `bullets`, `table` |
| 9 | Technology options | per need: the confirmed stack as given, else one pick + 2–3 alternatives with a trade-off, source page | `options` |
| 10 | What needs to be done | work items: build / configure / decide / clarify, owner role, dependency, reference ids | `work` |
| 11 | Gaps, assumptions and risks | facts in author voice ("Owner to decide: …"); mitigation per risk | `bullets`, `table` |
| 12 | Glossary | domain and product terms used in the brief | `terms` |

A one-line section is allowed everywhere; in 1, 3, 9 and 10 it is a WARN (those carry the brief).

## Fields
```json
{"title": "<use case>", "date": "YYYY-MM-DD", "subtitle": "<reader-facing one line: what, sources, cadence, given stack>",
 "stack": ["Snowflake", "Airflow"],
 "inputs_dir?": "generated-docs/_spec/inputs",
 "inputs": [{"name": "<file or paste>", "kind": "text|tickets|docx|pdf|data|dictionary", "ids": ["FLT-1"]}],
 "sections": {"<fixed name>": {"line": "…"} | {"lead?": "…", "blocks?": [ … ], "subsections?": [{"title": "…", "blocks": [ … ]}]}}}
```
- `stack` = the techs the user confirmed in Step 0; each must appear as a whole word in the `rec` of a `given` options row (ERROR otherwise), and a given row naming none of them is a WARN. Not rendered as a list: it shows through the given chips.
- `inputs[].ids` = the requirement ids `inputs.py` found; every one must be a `requirements` row (ERROR). Inputs with no ids (data files, notes) list `[]`. Requirements without ids in the input get ours: `R1…`, said in the row's `source`.
- A section renders `lead`, then its own `blocks`, then the `subsections` in order.

## Blocks
| Type | Fields | Rendered as |
|---|---|---|
| `text` | `text` | paragraph |
| `bullets` | `items` | list; one fact per item |
| `table` | `head`, `rows` (same length), `title?` | table |
| `facts` | `rows` [[label, value]] (no "Status" row: the build adds it) | label/value grid |
| `flow` | `title`, `nodes` [{id, label, sub?, kind: source·step·store·consumer, col, row, tag?}], `edges` [{from, to, label?, dashed?}], `lanes?` (one per row), `key` | SVG: boxes on a grid; arrows right within a row, down between rows (around any box in between), dashed up; `tag` printed top-right (GIVEN, LATER, MANUAL, NEW) |
| `links` | `title`, `entities` [{id, label, ids: [identifiers]}], `joins` [{a, b, on}], `key` | SVG: entity boxes with their identifiers, join lines "on <key>" |
| `timeline` | `title`, `steps` [{at, do, out?}] (≤ 7), `key` | SVG strip: time above, step, output below |
| `requirements` | `rows` [{id, text, status: clear·gap·conflict, source?, note?}] | table with status chips |
| `sources` | `rows` [{id, system, connector, key, cadence, volume?, note?, points: [[name, description, note?]], planned?: true}] | per source: heading, meta line, data points table; `planned` needs id and system only and shows a PLANNED chip |
| `needs` | `rows` [{use, data, sources: [source ids], missing?, note?}] | table; empty `sources` → "no source" chip; `missing` → "partial" chip + what the listed sources lack |
| `profile` | `from`: path of `profile.py` output (relative to the project root; the file names inside are relative too, or the build fails) | per file: rows, columns table (type, non-null, null %, distinct, min/max or "values withheld"); key overlap table |
| `options` | `rows` [{need, rec, why, given?: true, alternatives: [{name, tradeoff}] (2–3 unless given; none when given), source?}] | table; given rows show a GIVEN chip and no alternatives |
| `work` | `rows` [{id, what, kind: build·configure·decide·clarify, owner, depends?: [work ids], ref: [requirement ids, source ids or option needs]}] | table |
| `terms` | `rows` [[term, meaning]] | two-column glossary |

Text in any field: `code` and **bold** are rendered; ≤ 40 words per string.

## Checks
**ERROR** (no output): a fixed section missing or an unknown one · a section with neither `line` nor blocks/subsections, or `line` with either · a subsection without title or blocks · unknown block type · a typed "Status" facts row · requirement without id/text/status, status not clear·gap·conflict, id twice · source without id/system/connector/key/cadence (id/system when `planned`), id twice, data point not [name, description(, note)] · option without need/rec/why, not 2–3 alternatives with name + tradeoff (unless `given`), given with alternatives, pick listed as an alternative · a `stack` tech with no given row · work item without id/what/kind/owner/ref, kind unknown, `depends` not a work id · links join not between listed entities or without `on` · needs row without use/data, naming a source with no sources row, or `missing` with no sources · flow or links or timeline without title · flow box without id/label/col/row, unknown kind, id twice, fewer than 3 boxes, edge to an unknown box, lanes fewer than rows · a `source` box whose id has no sources row · timeline step without at/do · table head and rows of different lengths · facts or terms row not 2 cells · `profile.from` missing or not JSON · an input id (spec list or rescan of `inputs_dir`) with no requirements row · Requirements without a requirements block · `TODO` · absolute or machine path · a literal secret value · an e-mail address or phone number in any text (international with 7+ digits, local with 9+ digits; time ranges, row counts and IBAN groups are not phones) · a machine path inside `profile.json` · missing output folder.
**WARN**: a one-line section among 1, 3, 9, 10 · a subsection title that fits any brief · an id found in `inputs_dir` but not in the spec's inputs list · a given row not in `stack` · "N requirements" in a text with N ≠ the rows · diagram without `key` · edge or join label over 12 characters · box text cut (shorten `label`/`sub`) · timeline over 7 steps · a sources row that is no `source` box in a flow · work `ref` naming nothing known · option without `source` · Data findings with content but no profile block · chat voice (`you`, `your`, `the user`, `Claude`, `the requester`, `asked us`, `as discussed`, `as requested`, `confirm with`, `we could not check`, `was skipped`, `not provided by`) · filler (robust, seamless, leverage, very, simply, comprehensive, …) · a string over 40 words · the same sentence (≥ 6 words) twice.

**Added by the build:** `<meta name="generator" content="darshan-singh-meel-requirements-brief <version>">`, numbered sections and a table of contents, the date and input names under the title, the Status row in At a glance.
