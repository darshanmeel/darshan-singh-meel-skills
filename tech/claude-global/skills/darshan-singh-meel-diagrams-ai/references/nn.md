# Neural network blocks

`nn-block`: a model or one block of it as a top-down layer stack. Common fields: base `references/spec.md`.

| Field | Rule |
|---|---|
| `layers` | ≥ 2 in forward order: `id`, `label`, `kind`, optional `sub` (heads, sizes, activation), `out` (tensor shape after this layer, drawn on the arrow), `group` |
| `blocks` | repeated blocks `{id, label, repeat}` → frame titled `Decoder block × 12`; layers join with `group` |
| `residuals` | `{from, to}` skip connections, drawn grey down the right side inside the frame |
| `edges` | anything else (cross-attention from an encoder) |

- Kinds: `input`, `output` (pill) · `embed` green · `attention` lav · `ffn` teal · `norm` (add, layer norm) · `linear` blue (projections, heads) · `activation` amber · `conv` · `pool`.
- Draw one block in detail and give the repeat count; never draw twelve copies.
- Shapes as `[B, T, d]` with real sizes; put the shape on the arrow where it changes.
- Name the variant in the label (`Causal self-attention`, `Pre-norm`): the order of norm and add differs between architectures, so draw what the code does.
- Mermaid: a top-down flowchart with the block as a subgraph.
