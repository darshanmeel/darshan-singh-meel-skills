# Engine contract

The public API of `scripts/diagram.py` for family type modules and for other skills' builders. Names here are stable; anything starting with `_` is private.

## Calling it from another skill
```python
import sys; sys.path.insert(0, "<skills>/darshan-singh-meel-diagrams/scripts")
import diagram
r = diagram.build(spec)            # never raises on a bad spec
r["svg"]       # standalone <svg> with title, key and Notice drawn in
r["html"]      # <figure> fragment: title, scrolling frame with the svg, key and Notice as HTML
r["geometry"]  # layout record (below), None when the build failed
r["mermaid"]   # Mermaid text, or None when the type has no Mermaid form
r["errors"]    # [str]: spec errors, "layout: …", "LAYOUT <id> | <problem> | <text>"; empty = shippable
r["warnings"]  # [str]: "WARN <id> | unconnected node | …", "registry: …"
diagram.page([r1, r2], title)      # standalone HTML page holding several figures
diagram.png(r["svg"], "x.png", dark=False)   # error text or None (needs Playwright)
diagram.registry()                 # {type: {"svg", "mermaid", "validate", "family", "doc"}}
```
`build(spec, chrome=False)` leaves title, key and Notice out of `svg` (the `html` fragment always has them as text).

## Family module
- File: `darshan-singh-meel-diagrams-<family>/scripts/types_<family>.py`, next to this skill's folder. The registry finds it in the repo and in `~/.claude/skills` (glob `../../darshan-singh-meel-diagrams-*/scripts/types_*.py` from `diagram.py`). Extra files or folders for tests: `DIAGRAM_TYPES` (os.pathsep list).
- It defines `TYPES` and nothing else runs at import. `import diagram as core` at the top gives the already-loaded engine (its folder is on `sys.path`); never load a second copy by file path.
```python
import diagram as core

def svg(spec, core):        # the engine is passed in as well
    ...                     # return core.finish(c) -> (svg_body, geometry), or (body, geometry, [css])
def mermaid(spec): ...      # -> str or None ("no Mermaid form")
def validate(spec): ...     # -> [str] errors; [] = ok

TYPES = {"c4-context": {"svg": svg, "mermaid": mermaid, "validate": validate,
                        "doc": "one line for --list"}}
```
- Type names are global: prefix nothing, but never reuse a name another family or the base owns (`boxes`, `layers`, `grid`); a clash is skipped and reported in `registry: …` warnings. A module that fails to import is reported, the others still load.
- Errors: raise `core.LayoutError("what is wrong: the fix")` when a spec cannot be laid out; `build` turns it into `layout: …`. Any other exception becomes `layout crashed: …` - a bug in the module.
- Common fields (`id`, `type`, `title`, `key`, `notice`) are validated by `build`; `validate` covers only the type's own fields.
- Extra CSS: `core.add_css(c, "#S .x{fill:var(--dg-red-bg)}")` (`#S` = this diagram's scope) or return it as the third tuple item. Use the `--dg-*` variables only (`references/style.md`).

## Node-edge types: reuse `graph`
Most types are nodes and arrows with a family meaning. Map the spec onto generic nodes and let the base lay out, route, style and check:
```python
def svg(spec, core):
    nodes = [{"id": t["id"], "label": t["name"], "tag": "container", "sub": t["tech"], "kind": t["kind"],
              "group": t.get("boundary")} for t in spec["items"]]
    return core.graph(spec, nodes, spec["links"], spec.get("boundaries"), kinds=MY_KINDS)
def mermaid(spec):           # module-level `core` from `import diagram as core`
    return core.mermaid_graph(spec, nodes, edges, groups, kinds=MY_KINDS)  # same mapping as svg
```
- `graph(spec, nodes=None, edges=None, groups=None, kinds=None, states=None, direction=None, max_w=None, spread=False, gap=None)` → `(body, geometry)`; `None` = take `spec["nodes"]` etc. Applies `spec["style"]`, `view`, `collapse`, `group_layout`, legend.
  - `spread=True`: one port per arrow, no shared trunks - for types whose arrows all carry labels (integration maps, DFD flows, service calls).
  - `gap`: main-axis gap between layers for the first layout; the automatic top-down retry uses the default.
- `style_graph(spec, nodes, edges, groups, kinds, states)` → `{"nodes", "edges", "groups", "legend", "group_layout", "direction"}` when a type draws itself but wants the style mapping.
- `mermaid_graph(...)` same arguments → Mermaid flowchart with the same collapse and colours.
- `kinds` / `states`: `{name: tone}` or `{name: {"tone", "label", "shape", "solid", "dashed"}}`. The spec's own `kinds` / `states` override them. Built-in maps: `DBT_KINDS`, `AIRFLOW_STATES`, `EDGE_KINDS`.
- `check_graph(spec, nodes_key="nodes", edges_key="edges")` and `check_style(spec)` → `[str]` for `validate`.

## Drawing primitives (own layouts)
| Function | Does |
|---|---|
| `canvas(spec)` → `c` | empty drawing with its geometry record |
| `size(n, max_w=200, min_w=96)` → `(w, h)` | outer size of a node dict with its text wrapped inside |
| `node(c, n, x, y, w, h, clear=None)` | draws node `n`: `id, label, sub, tag, shape, tone, solid, dashed, strong, dim, mono, align ("left"), tip, href, cls, decision, free`; `clear` = how far arrows stay away (default `CLEAR` 10; e.g. 4 for dense Gantt rows) |
| `obstacle(c, x, y, w, h, margin=None)` | keeps routed arrows `margin` (default `CLEAR`) away from a rectangle that is not a node: a label column, a note, an outside label |
| `container(c, id, label, x, y, w, h, members=(), kind="group", tone=None, header_w=0, label_w=None)` | `kind`: `group` (dashed frame, label wrapped to `label_w` or `w`), `boundary` (grey dashed), `lane` / `band` (soft stripe, label in a left header of `header_w`) |
| `route(c, edges, direction="LR", spread=None)` | orthogonal routing around every drawn node; edges `from, to, label, style, head, tail, tone, kind, dim, from_side, to_side, own_port`. Arrows that all leave or all reach one side share a port (trunk); `spread=True` gives every arrow its own port, `own_port: true` on an edge splits that side only. Ports spread on box, rounded, note, cylinder, document, pill and hexagon (on the outline). Channels on a frame border are avoided, near one cost a little |
| `arrow(c, pts, e)` | an edge along fixed points (sequence messages, timelines); label placed in `finish` |
| `text(c, x, y, s, cls, anchor, size, mono, bold, check=True)` | free one-line text, registered for overlap checks |
| `line(c, pts, cls)` / `rect(c, x, y, w, h, cls, rx)` | free axes, lifelines, bars (not checked) |
| `legend(c, entries)` | queue legend swatches drawn under the diagram |
| `add(c, svg, z)` / `add_css(c, rules)` | raw SVG at layer z (0 frames, 1 edges, 2 nodes, 3 labels) / scoped CSS |
| `finish(c, w=None, h=None)` → `(body, geometry)` | places edge labels, draws the legend, sizes the canvas |
| `wrap(s, width, size, mono, bold)` / `text_width(...)` | word wrap that never cuts a word; width estimate |

Layouts return rectangles `(x, y, w, h)`; draw with `node` / `container`, then `route`:
`layout_layered(items, edges, direction, groups, gap, cross_gap, group_layout)` (returns `label_w` for `container` in TB) · `ranks(ids, edges, fixed, lower, pull)` · `layout_grid(sizes, cols, gap, start, uniform)` · `layout_lanes(lanes, items, edges, header_w, gap, row_gap)` · `layout_tree(items, direction, gap, start)` · `layout_radial(center, items, gap, child_gap)` · `layout_matrix(row_heads, col_heads, cell_w, cell_h, head_w, head_h, start, gap)` · `time_axis(start, end, x0, x1)` → `(to_x, ticks)`.
Mermaid helpers: `mermaid_head(spec, kind)`, `mermaid_flowchart(spec, nodes, edges, direction, groups)`, `mm_text(s)`, `mm_id(s)`.
Constants: `MAX_W` 1000, `MARGIN`, `SHAPES`, `TONES`, `HEADS`, `STYLES`, `EDGE_TONES`, `GRAPH_STYLES`, `LIGHT`, `DARK`.

## Geometry record (what `check.py` reads)
```
{"id", "type", "width", "height", "connected": bool,           # connected false: no unconnected-node warning
 "nodes": [{"id", "x", "y", "w", "h", "shape", "text", "decision", "free",
            "inner": [x, y, w, h], "lines": [{"text", "x", "y", "w", "h"}]}],
 "containers": [{"id", "x", "y", "w", "h", "kind", "text", "members": [ids], "header_w"}],
 "edges": [{"from", "to", "points": [[x, y], ...], "label": index into labels or None}],
 "labels": [{"text", "x", "y", "w", "h", "edge": index or None, "kind": "edge|container|text|legend"}]}
```
`node`, `container`, `text`, `arrow`, `route`, `legend` fill it; a type that draws raw SVG with `add` must register what it wants checked itself.

## Checks (`check.py`, run by every build)
canvas over 1000px · outside canvas · boxes overlap · member outside its group · box inside or across a foreign group · groups overlap · arrow through a box (also its own) · two unrelated arrows on one line · label on a box, on a foreign line, on another label, across a group border · text overflows its box · decision with fewer than 2 exits · warning: unconnected node.
