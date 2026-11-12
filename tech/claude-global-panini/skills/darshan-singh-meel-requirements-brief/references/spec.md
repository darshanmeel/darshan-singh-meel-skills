# Brief spec — input to build.py
`<skill>` = this skill's folder. Run from project root:
`python <skill>/references/templates/build.py generated-docs/_spec/requirements-brief-<slug>.json generated-docs/requirements-brief-<slug>.html`
- Prints WARN lines, a summary line (requirements by status, use cases without a source, decisions open, sources, options, work items), then `built <out>: 12 sections, N WARN`. ERROR stops the build.
- Rescans `inputs_dir` (default `generated-docs/_spec/inputs`) for requirement ids with `inputs.py`: every id found must be a requirements row. Folder missing → `note:`, only spec's `inputs[].ids` checked.
- Start from `examples/requirements-brief-example.json`; nothing of example survives into a real brief. Builder tests: `python <skill>/tests/run.py`.
- Helpers beside it: `inputs.py` (inventory · ids · plain text · .gitignore entries) · `profile.py` (structure-only data profile → `profile.json`) · `skills.py` (installed skills covering the confirmed stack).

## Fixed sections, free content
Top level same in every brief: 12 sections, these names, this order. Build refuses a missing/extra one.
Inside: content chosen from input. Blocks sit directly in section; subsection = named group with own heading, named from input (a source · a conflict · a flow), never a wrapper fitting any brief (WARN on "Overview", "Per need", "Linking rules", "What the sample shows", the section's name, a block type, …). Exception: in section 11 the groups "Gaps", "Assumptions", "Risks", "Open points" are the content, allowed as titles. Section with nothing to say = one `line`.

| # | Section | Holds | Typical blocks |
|---|---|---|---|
| 1 | At a glance | goal · outcome · scope in/out · MVP vs later · source count · refresh · given stack; build appends Status row (counts from rows, also when section is one line) | `facts` |
| 2 | Context | sources → ingestion → platform → consumers; how given stack fits | `flow`, `bullets` |
| 3 | Requirements | every requirement, input's own id + status; conflicts + how we resolve | `requirements`, `bullets` |
| 4 | Sources and data | per source: system · connector · key · cadence · data points; undefined sources `planned` | `sources` (one subsection per source, or one block) |
| 5 | Identity and linking | entities · identifiers · what joins what; linking rules | `links`, `bullets` |
| 6 | Flows | timeline/flow only where it explains (batch window, hand-offs); else one line | `timeline`, `flow` |
| 7 | Use cases and data needs | consumer/tactic → data needed → sources; no-source rows flagged, partly covered rows say what is `missing` | `needs` |
| 8 | Data findings | profile of supplied data (structure only) · what it shows · requirement vs data; no data → one line | `profile`, `bullets`, `table` |
| 9 | Technology options | per need: confirmed stack as given, else one pick + 2–3 alternatives with trade-off, source page | `options` |
| 10 | What needs to be done | work items: build/configure/decide/clarify · owner role · dependency · reference ids | `work` |
| 11 | Gaps, assumptions and risks | facts in author voice ("Owner to decide: …"); mitigation per risk | `bullets`, `table` |
| 12 | Glossary | domain + product terms used | `terms` |

One-line section allowed everywhere; in 1, 3, 9, 10 → WARN (they carry the brief).

## Fields
```json
{"title": "<use case>", "date": "YYYY-MM-DD", "subtitle": "<reader-facing one line: what, sources, cadence, given stack>",
 "stack": ["Snowflake", "Airflow"],
 "inputs_dir?": "generated-docs/_spec/inputs",
 "inputs": [{"name": "<file or paste>", "kind": "text|tickets|docx|pdf|data|dictionary", "ids": ["FLT-1"]}],
 "sections": {"<fixed name>": {"line": "…"} | {"lead?": "…", "blocks?": [ … ], "subsections?": [{"title": "…", "blocks": [ … ]}]}}}
```
- `stack` = techs confirmed in Step 0; each must appear as whole word in `rec` of a `given` options row (ERROR otherwise); a given row naming none of them → WARN. Not rendered as a list: shows through given chips.
- `inputs[].ids` = requirement ids `inputs.py` found; each must be a `requirements` row (ERROR). Inputs without ids (data files, notes) → `[]`. Requirements without ids in input get ours `R1…`, said in row's `source`.
- Section renders `lead`, then own `blocks`, then `subsections` in order.

## Blocks
| Type | Fields | Rendered as |
|---|---|---|
| `text` | `text` | paragraph |
| `bullets` | `items` | list; one fact per item |
| `table` | `head`, `rows` (same length), `title?` | table |
| `facts` | `rows` [[label, value]] (no "Status" row: build adds it) | label/value grid |
| `flow` | `title`, `nodes` [{id, label, sub?, kind: source·step·store·consumer, col, row, tag?}], `edges` [{from, to, label?, dashed?}], `lanes?` (one per row), `key` | SVG boxes on a grid; arrows right within a row, down between rows (around any box between), dashed up; `tag` top-right (GIVEN, LATER, MANUAL, NEW) |
| `links` | `title`, `entities` [{id, label, ids: [identifiers]}], `joins` [{a, b, on}], `key` | SVG entity boxes with identifiers, join lines "on <key>" |
| `timeline` | `title`, `steps` [{at, do, out?}] (≤ 7), `key` | SVG strip: time above, step, output below |
| `requirements` | `rows` [{id, text, status: clear·gap·conflict, source?, note?}] | table with status chips |
| `sources` | `rows` [{id, system, connector, key, cadence, volume?, note?, points: [[name, description, note?]], planned?: true}] | per source: heading · meta line · data points table; `planned` needs id + system only, PLANNED chip |
| `needs` | `rows` [{use, data, sources: [source ids], missing?, note?}] | table; empty `sources` → "no source" chip; `missing` → "partial" chip + what listed sources lack |
| `profile` | `from`: path of `profile.py` output (relative to project root; file names inside relative too, or build fails) | per file: rows · columns table (type, non-null, null %, distinct, min/max or "values withheld"); key overlap table |
| `options` | `rows` [{need, rec, why, given?: true, alternatives: [{name, tradeoff}] (2–3 unless given; none when given), source?}] | table; given rows GIVEN chip, no alternatives |
| `work` | `rows` [{id, what, kind: build·configure·decide·clarify, owner, depends?: [work ids], ref: [requirement ids, source ids or option needs]}] | table |
| `terms` | `rows` [[term, meaning]] | two-column glossary |

Text in any field: `code` + **bold** rendered; ≤ 40 words per string.

## Checks
**ERROR** (no output):
- Structure: fixed section missing or unknown · section with neither `line` nor blocks/subsections, or `line` with either · subsection without title/blocks · unknown block type · typed "Status" facts row · `TODO` · missing output folder.
- Requirements: row without id/text/status · status not clear·gap·conflict · id twice · input id (spec list or `inputs_dir` rescan) with no requirements row · Requirements without a requirements block.
- Sources: row without id/system/connector/key/cadence (id/system when `planned`) · id twice · data point not [name, description(, note)] · `source` box whose id has no sources row.
- Options: row without need/rec/why · not 2–3 alternatives with name + tradeoff (unless `given`) · given with alternatives · pick listed as alternative · `stack` tech with no given row.
- Work: item without id/what/kind/owner/ref · unknown kind · `depends` not a work id.
- Needs: row without use/data · naming a source with no sources row · `missing` with no sources.
- Diagrams: flow/links/timeline without title · flow box without id/label/col/row · unknown kind · id twice · fewer than 3 boxes · edge to unknown box · lanes fewer than rows · links join not between listed entities or without `on` · timeline step without at/do.
- Tables: table head + rows of different lengths · facts/terms row not 2 cells · `profile.from` missing or not JSON.
- Privacy: absolute or machine path · literal secret value · e-mail address or phone number in any text (international 7+ digits, local 9+ digits; time ranges, row counts, IBAN groups are not phones) · machine path inside `profile.json`.

**WARN**:
- Shape: one-line section among 1, 3, 9, 10 · subsection title fitting any brief · string over 40 words · same sentence (≥ 6 words) twice · "N requirements" in text with N ≠ rows.
- Consistency: id found in `inputs_dir` but not in spec's inputs list · given row not in `stack` · sources row that is no `source` box in a flow · work `ref` naming nothing known · option without `source` · Data findings with content but no profile block.
- Diagrams: no `key` · edge/join label over 12 characters · box text cut (shorten `label`/`sub`) · timeline over 7 steps.
- Voice: chat voice (`you`, `your`, `the user`, `Claude`, `the requester`, `asked us`, `as discussed`, `as requested`, `confirm with`, `we could not check`, `was skipped`, `not provided by`) · filler (robust, seamless, leverage, very, simply, comprehensive, …).

**Added by build:** `<meta name="generator" content="darshan-singh-meel-requirements-brief <version>">` · numbered sections + table of contents · date + input names under title · Status row in At a glance.
