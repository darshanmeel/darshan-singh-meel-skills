# LLM application types

Fields of `rag-pipeline`, `agent-loop`, `multi-agent` and `context-assembly`. Common fields (`id`, `type`, `title`, `key`, `notice`, `style`, `view`, `collapse`, `legend`, `max_w`) and node / edge fields are in the base `references/spec.md`.

## Node kinds (all AI types)
`data` · `step` · `model` · `agent` · `store` · `tool` · `guard` · `gate` · `human` · `client` · `gateway` · `router` · `cache` · `monitor` · `output` · `pass` · `fail`. Each type sets a default kind for its lists; set `kind` on a node to change it. dbt kind names are accepted too.

## `rag-pipeline`
| Field | Rule |
|---|---|
| `ingest` | ≥ 2 nodes in order (load, chunk, embed …), chained automatically; default kind `step` |
| `stores` | ≥ 1 node (vector index, keyword index, document store); default kind `store` |
| `query` | ≥ 2 nodes in order (question, embed, retrieve, rerank, generate, answer), chained |
| `edges` | at least one ingest step → each store and each store → one query step; labels such as `upsert`, `k-NN + keyword` |
| `ingest_label`, `query_label`, `store_label` | frame titles; defaults `Ingest (offline)`, `Query (per request)`, `Index` |
| `nodes` | extra boxes (an eval hook, a cache); switches to the layered layout |
| `layout` | `columns` (default: ingest, index, query side by side, the store level with the step that reads it) or `flow` |

- Mark model calls `kind: model` (embedders, rerankers, the generator): the reader sees every model in one colour.
- The same embedding model on both sides is the usual Notice; name it in both `sub` lines.

## `agent-loop`
| Field | Rule |
|---|---|
| `steps` | 2-4 loop steps in order (plan, act, observe); chained, last returns to first along the right side |
| `agent` | frame title: agent name and stop rule (`dispute-agent · repeats until done, max 8`) |
| `loop_label` | optional, appended to the frame title |
| `nodes` | everything around the loop; default kind `tool`; also `client`, `guard`, `store`, `human`, `output` |
| `edges` | links between steps and nodes; `kind: approval` for a human gate, `return` for results |
| `layout` | `loop` (default) or `flow` (layered) |

Placement in `loop`: the entry chain (client → input guard) runs down into the first step; memory stores sit under it; tools and humans right of the step that calls them, a chain continuing on its row; the exit path (output guard → reply) sits above, leaving the first step upwards. At least one `tool` and every node connected.

## `multi-agent`
| Field | Rule |
|---|---|
| `nodes` | ≥ 2 `kind: agent` (default); tools, stores, humans as needed; `operator` = role (`planner agent`) |
| `edges` | delegation, `kind: handoff` (thick), `return` (dashed), `approval` |
| `groups` | teams or parallel branches |

- Structure view (who may call whom): plain style.
- Run view (what happened last run): `style: "airflow"` and `state` per agent (`success`, `failed`, `up_for_retry`, `running`, `none` …); the legend shows the states used. A `human` node keeps its stick figure with the state colour; other kinds become task boxes, so put the role in `operator`.
- Supervisor patterns: one supervisor fanning out to a group of workers, results merging in one node.

## `context-assembly`
| Field | Rule |
|---|---|
| `limit` | context window in tokens (whole number) |
| `segments` | ≥ 2, top to bottom in prompt order: `id`, `label`, `tokens`, `kind`, optional `sub`, `source`, `via` (edge label), `tone` |
| `sources` | boxes left of the bar: `id`, `label`, `sub`, `kind` |
| `bar_h` | bar height for the full window in px (default 520) |

- Segment kinds: `system` · `tools` · `memory` · `retrieved` · `history` · `user` · `reserved` (dashed; the answer budget).
- Heights are proportional to tokens with a minimum that fits the text; the token count is printed in every segment, and the header gives total, limit and percentage. The unused rest is a dashed box.
- Segments over `limit` are an error: trim before drawing.
- Mermaid: a top-down flowchart with the segments in order inside a subgraph; proportions only in the SVG.
