---
name: darshan-singh-meel-diagrams-ai
description: AI and ML diagram family for darshan-singh-meel-diagrams - nine types as static inline SVG plus Mermaid, layout-checked - RAG pipeline (ingest, chunk, embed, index; query, retrieve, rerank, generate), LLM agent loop (plan, act, observe with tools, memory, guardrails, human approval), multi-agent orchestration, ML lifecycle / MLOps with feedback loops, feature store training vs serving split, eval pipeline (datasets, graders, metrics vs thresholds, release gate), model serving topology (gateway, router, cache, fallback), prompt / context assembly against a token budget, neural network / transformer block. Node-edge types take the base graph styles - airflow for agent and pipeline runs with state, dbt for feature and data lineage. Load with darshan-singh-meel-diagrams. Triggers - "RAG diagram", "agent loop diagram", "multi-agent diagram", "MLOps diagram", "feature store diagram", "eval pipeline", "LLM gateway diagram", "context window diagram", "transformer diagram".
---

# Diagrams: AI and ML

Family skill. Load `darshan-singh-meel-diagrams` alongside: spec basics, build, checks, embedding and the palette live there and are not repeated here.

## When to use
Pick the type by the question the reader has. One question per diagram.

| Type | Answers | Not for (use instead) |
|---|---|---|
| `rag-pipeline` | How do documents become answers? Where does retrieval quality come from? | Agent tool calls (`agent-loop`); plain ETL (`boxes`, data family) |
| `agent-loop` | What does one agent do per step, which tools can it touch, where do guardrails and humans sit? | Several agents (`multi-agent`); a fixed workflow without a loop (flow family) |
| `multi-agent` | Who delegates to whom, what runs in parallel, where are handoffs; with `airflow` style: what happened in this run? | One agent (`agent-loop`); message order over time (interaction family, sequence) |
| `ml-lifecycle` | How does a model go from data to production and back (retraining loops, gates)? | One training job's steps (`boxes`, airflow style) |
| `feature-store` | Do training and serving compute features the same way? Where can skew enter? | Generic lineage (data family, dbt style) |
| `eval-pipeline` | What blocks a release: which dataset, grader, metric and threshold? | Model monitoring in production (`ml-lifecycle`) |
| `model-serving` | How does a request reach a model: gateway, cache, routing, fallback? | Cloud network detail (architecture family) |
| `context-assembly` | What fills the context window, in which order, and how close is it to the limit? | Where the content comes from upstream (`rag-pipeline`) |
| `nn-block` | What are the layers of a model or block, with shapes and residuals? | Training infrastructure (`ml-lifecycle`) |

## High level first, then detail
- Overview first: `ml-lifecycle` or `model-serving` with ≤ 9 boxes, or any node-edge type with `view: "overview"` (one box per group).
- Then one detail diagram per area: the RAG query band, one agent's loop, one eval gate, one block of the network.
- Link them: the overview's Notice names the detail diagrams.

## Graph styles (any node-edge type here)
The author picks; nothing forces a style.
- **airflow** - executable runs with state: `multi-agent` runs, `eval-pipeline` runs (metrics map to success / failed), training pipelines in `ml-lifecycle`. Set `state` (and `operator` as the role) per node; family kinds give way to state colours, except `human`, which keeps its stick figure.
- **dbt** - lineage: `feature-store` (sources to feature views to stores to models), the RAG ingest side, model dependency maps. Kinds become filled pills.
- **plain** (default) - loops, topologies and stacks: `agent-loop`, `model-serving`, `nn-block`.
- `context-assembly` draws its own bar and takes no style.

## Process
1. Pick the type above; read its fields in the reference: `references/llm.md` (rag-pipeline, agent-loop, multi-agent, context-assembly), `references/mlops.md` (ml-lifecycle, feature-store, eval-pipeline, model-serving), `references/nn.md` (nn-block).
2. Write the spec from the real system: model names, index names, thresholds, token budgets from code or config. Synthetic values only in examples.
3. Build with the base CLI: `python <skills>/darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png`. Every `LAYOUT` line or `ERROR` is a defect; the message names the fix.
4. Look at the PNG, light and `--dark`; read every label.
5. Embed as the base `references/embedding.md` says.

## Notation (this family's own conventions)
No standard body defines AI diagrams; these rules keep ours consistent. Shapes and colours come from `kind`, are listed in the legend and named in the key.
- `data` document shape, green · `model` lav (LLM, embedder, reranker, judge) · `store` / `cache` cylinder · `tool` teal · `guard` hexagon, amber (guardrail) · `gate` diamond, amber (release / promotion gate) · `human` stick figure · `router` diamond · `gateway` dark box · `monitor` dashed.
- Edge kinds: `feedback` dashed blue (retraining loop) · `fallback` dashed amber · `approval` dashed amber (waits for a human) · `return` dashed grey · `handoff` thick · `telemetry` dotted · `residual` grey (skip connection).
- Red only for failure or a missed gate; green only for success or a met gate.
- Offline and online paths always in separate frames (`rag-pipeline`, `feature-store`): the split is the point.
- Model and index names are real (`text-embed-v3`, `kb_chunks`), never "LLM" alone when the name is known; numbers carry units (tokens, ms, dims).

## Sizing limits
- ≤ 9 boxes per diagram; agent loops 2-4 steps; ≤ 6 tools on one agent (group the rest).
- Edge labels ≤ 36 characters; long labels widen column gaps, so short ones (`miss`, `upsert`) keep the canvas under 1000px.
- Fixed layouts (agent, ring, fan, split, columns, nn stack) wrap box text narrower before giving up; then the error says what to cut.

## Common mistakes
- One picture for ingest, query, agent and eval: split into four.
- A RAG index with no ingest edge or no query edge: the build rejects it.
- A lifecycle with no loop back: that is a pipeline; use `boxes` with airflow style.
- Context segments that add up past `limit`: the build rejects it; trim the segment the Notice is about.
- Metrics without thresholds: they cannot be coloured; add `value` and `threshold`.
- Colour without a legend word: kinds and states always print their label.

## Rules
- Never edit `darshan-singh-meel-diagrams` or other family skills; this skill only adds `scripts/types_ai.py`.
- Output stays local; no artifacts or hosted pages. No secrets, keys, endpoints with credentials or personal data in labels.
- Examples: `references/examples/` - one spec and rendered SVG per type; `python tests/run.py` rebuilds and checks them (`--write` refreshes the SVGs).
