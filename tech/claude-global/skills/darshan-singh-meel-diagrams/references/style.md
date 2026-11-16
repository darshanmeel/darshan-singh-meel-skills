# Visual style

Same palette and fonts as the docs pages (`darshan-singh-meel-docs-v2/references/templates/style.css`), so a diagram sits on any page without restyling.

## Palette (CSS variables, scoped to each svg as `--dg-*`)
| Token | Light | Dark | Used for |
|---|---|---|---|
| ground | #F6F6F3 | #141619 | page behind the PNG |
| card | #FFFFFF | #1C1F24 | diagram background, box fill, text on solid fills |
| line | #D9DBDF | #3A3F47 | axes, grid lines |
| ink | #17191D | #E8EAED | box border, labels |
| muted | #5B6068 | #A4AAB3 | sub lines, tags, key, legend |
| soft | #EEEFEC | #272B32 | `soft` tone, lanes, headers |
| teal / teal-ink | #DDF0EE / #1C5C57 | #173A37 / #83D3C9 | `teal` tone |
| amber / amber-ink | #FCEBC8 / #8A5A00 | #3B2E12 / #EEC065 | `amber` tone, notes |
| lav / lav-ink | #E7E2F5 / #6B4FA8 | #2B2540 / #BCA9F0 | `lav` tone, group frames |
| green / green-bg | #1E6B43 / #E2F1E8 | #6CCB95 / #16301F | `green` tone |
| blue / blue-bg | #1F5FA8 / #E2ECF8 | #86B2EE / #172A42 | `blue` tone |
| red / red-bg | #A12D2D / #F8E3E3 | #F09090 / #3A1C1C | `red` tone, failure paths |
| edge | #40454D | #B7BCC4 | arrows |

- Tone = light fill + strong border. `solid` = strong fill + card-coloured text (dbt style).
- `dim` = outline and fill at 40 % opacity, text in `muted` at 80 % (≥ 3:1 in both modes; the review checks it); a dim `solid` pill becomes an outline pill.
- Dark mode: `prefers-color-scheme: dark` unless the page sets `data-theme="light"`; `data-theme="dark"` forces it.
- No colours outside this table, no gradients, shadows, icons, logos or decoration.

## Fonts
- IBM Plex Sans (fallback Segoe UI, Arial): labels 13px semibold, sub 12px.
- IBM Plex Mono (fallback Consolas): tags 10.5px, edge labels and group labels 11px, key 11.5px, identifiers (`mono: true`, dbt and airflow styles) 12.5px.
- Title 15px semibold; Notice 12.5px.

## Meaning, not decoration
- One colour = one meaning, named in the key or legend; the text says it too (state word, kind tag), so the picture works in greyscale.
- Red only for failure, risk or "breaks"; green for success or healthy; amber for warnings, manual steps, notes.
- Dashed line = asynchronous, optional or triggered later; dotted = weak or inferred; thick = main path.
- Group frames are lav dashed; boundaries (trust, network) are grey dashed.

## Size and density
- ≤ 7 ± 2 boxes per level; more → overview plus detail diagrams.
- Canvas ≤ 1000px wide. Boxes wrap at 200px (`max_w`), never cut a word; identifiers break after `/ . _ - :`.
- Edge labels ≤ 36 chars; longer text belongs in a box `sub`.
