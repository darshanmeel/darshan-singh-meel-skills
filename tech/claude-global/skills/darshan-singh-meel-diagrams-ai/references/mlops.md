# ML platform types

Fields of `ml-lifecycle`, `feature-store`, `eval-pipeline` and `model-serving`. Node kinds: `references/llm.md`. Common fields: base `references/spec.md`.

## `ml-lifecycle`
| Field | Rule |
|---|---|
| `stages` | ≥ 3 nodes in order (build training set, train, evaluate, register, deploy, monitor), chained; default kind `step` |
| `loops` | ≥ 1 `{from, to, label}` back edge, drawn as `feedback` (dashed blue) |
| `groups` | e.g. experimentation vs production; `group` on each stage |
| `nodes`, `edges` | extra boxes (feature store, registry) and links; default kind `store` |
| `layout` | `ring` (default for ≥ 4 stages) or `flow` (layered, left to right) |

- `ring`: first half of the stages left to right on top, second half right to left below; a loop from the last stage back to the first runs round the outside on the left. Groups map naturally to the two rows.
- Name the trigger on every loop (`drift alert`, `AUC below 0.80`) and the gate metric in the evaluate stage.
- A training pipeline run with task states is `boxes` (or `ml-lifecycle` with `layout: "flow"`) in airflow style.

## `feature-store`
| Field | Rule |
|---|---|
| `sources` | raw inputs; default kind `data` |
| `pipelines` | feature views / transformations, the one shared definition; default kind `step` |
| `offline`, `training` | offline store(s) and training path (point-in-time join, training job) |
| `online`, `serving` | online store(s) and serving path (inference service) |
| `edges` | all links; must contain offline → a training node and online → a serving node |
| `labels` | frame titles `{pipelines, training, serving}` |
| `layout` | `split` (default: top-down, training frame left, serving frame right) or `flow` |

- The Notice says where skew can or cannot enter (same definitions, same keys, point-in-time).
- `style: "dbt"` reads as feature lineage (filled pills by kind).

## `eval-pipeline`
| Field | Rule |
|---|---|
| `datasets` | eval sets with size in `sub`; default kind `data` |
| `run` | system under test, chained (candidate version, prompt, retriever) |
| `graders` | `grader`: `code`, `model` (LLM judge) or `human`; `metrics`: ids it scores |
| `metrics` | `value`, `threshold`, `higher_is_better` (default true) → green "meets gate" / red "misses gate", sub `0.91 (gate >= 0.95)` |
| `gate` | one decision node `{id, label}` |
| `outcomes` | ≥ 2 nodes; `when` labels the gate exit, `fail: true` draws it red |
| `labels` | frame titles `{datasets, run, graders, metrics, gate}` |

- Every metric needs a grader; every grader's metrics must exist.
- `style: "airflow"` shows an eval run: metrics become success / failed states.

## `model-serving`
| Field | Rule |
|---|---|
| `nodes` | at least one `model` and one `gateway` or `router`; `client`, `cache`, `guard`, `monitor` as needed |
| `edges` | request path; `kind: fallback` (dashed amber), `telemetry` (dotted) |
| `groups` | providers or clusters holding the model endpoints |
| `layout` | `fan` (default: request path down the left, grouped endpoints right of their caller) or `flow` |

- Ungrouped nodes form the request path; grouped nodes fan out. Put every endpoint in a group.
- Name the routing rule on each exit (`reasoning`, `short tasks`, `timeout`); a router is a decision and needs ≥ 2 exits.
