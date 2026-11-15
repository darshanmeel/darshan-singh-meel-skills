# Tables: `er` and `star-schema`

Both draw entity tables: a header (name, optional `sub`) and one row per column (key, name, type). Mermaid form: `erDiagram`.

## Entity (both types)
| Field | Rule |
|---|---|
| `id` | table name; also the Mermaid entity name |
| `label` | optional display name (default `id`) |
| `sub` | one short line under the name: grain, SCD type, owner |
| `columns` | list of `"name type KEY"` strings (`"order_id bigint PK,FK"`) or `{name, type, key}`; key `PK`, `FK`, `UK` or a comma list |
| `more` | number of columns left out; drawn as "+ n more columns" |
| `tone` | header colour: `plain` (grey), `blue`, `teal`, `amber`, `lav`, `green`, `red` |
| `dim`, `tip`, `free` | faded / hover text / no unconnected warning |

- List key columns and the few that explain the relation; the rest goes in `more`.
- A long column name wraps after `_`; a long type moves under the name. The box never grows past `max_w` (spec, default 260 for `er`, 240 for `star-schema`).
- No columns → a header-only box (conceptual model).

## `er`
```json
{"id": "shop-er", "type": "er", "title": "...", "key": "...", "notice": "...",
 "areas": [{"id": "sales", "label": "sales"}],
 "entities": [{"id": "orders", "area": "sales", "columns": ["order_id bigint PK", "customer_id bigint FK"]}],
 "relations": [{"from": "customers", "to": "orders", "card": "1:0..N", "label": "places", "identifying": false}]}
```
- `card` = `<from>:<to>`, each `1`, `0..1`, `0..N`, `1..N`. Draw `from` = the parent (the one side) so the layout flows parent → child.
- `identifying: false` → dashed line (Mermaid `..`); default solid (`--`).
- `label` = verb phrase, ≤ 36 characters; leave it out when the FK name says it.
- `areas` = subject areas drawn as frames; Mermaid lists them as comments.
- `from_side` / `to_side` (`left right top bottom`) on a relation: use when two relations reach one table from the same side and read as one line (e.g. a table in another area below → `to_side: "bottom"`).
- `direction` LR (default) or TB; `rank` on an entity fixes its column; `area_layout` `auto` | `bands` | `columns`.
- Too wide: split by area, cut columns with `more`, or `direction: "TB"`.

## `star-schema`
```json
{"id": "sales-star", "type": "star-schema", "title": "...", "key": "...", "notice": "...",
 "fact": {"id": "fct_sales", "sub": "1 row per order line", "columns": ["customer_key int FK", "net_amount decimal"]},
 "dimensions": [{"id": "dim_customer", "side": "left", "via": "customer_key", "columns": ["customer_key int PK"]},
                {"id": "dim_category", "parent": "dim_product"}]}
```
- Fact in the middle (blue header); dimensions alternate left and right unless `side` is set (teal header).
- `parent` makes a snowflaked outrigger (grey header) stacked under its parent dimension.
- `via` = label on the relation (join key or role, e.g. "order / ship date" for a role-playing date).
- `card` default `1:0..N` (one dimension row, many fact rows); `identifying` as in `er`.
- Several facts sharing dimensions (bus matrix) → `er` with areas, or a base `grid` for the matrix.
