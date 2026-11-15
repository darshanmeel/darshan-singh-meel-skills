---
name: darshan-singh-meel-diagrams-architecture
description: Architecture diagram family for the darshan-singh-meel-diagrams engine - C4 system context, container and component (native Mermaid C4), deployment per environment, cloud or network topology (nested frames - VPC or VNet, subnets, gateways, firewalls, private endpoints; generic shapes, no logos), integration map, event-driven pub-sub with DLQ, microservices dependency map (health, impact view), layered architecture with rule breaks in red, request path through tiers, and trust boundaries with numbered crossings. JSON spec in, static SVG (light and dark) plus Mermaid out, checked for overlaps; integration, event and service maps also take the dbt graph style. Use for architecture pictures in docs v1 and v3, tech summaries, reviews and briefs; load darshan-singh-meel-diagrams alongside. Triggers - "C4 diagram", "system context", "container diagram", "deployment diagram", "network diagram", "integration map", "pub-sub", "service dependency map", "layered architecture", "request path", "trust boundaries".
---

# Diagrams - architecture family

Types for "what is the system made of, where does it run, what talks to what". The engine, common spec fields, style, checks and embedding live in `darshan-singh-meel-diagrams` (load it too); this skill adds types only.

## Pick the type
| Type | Question it answers | Not when | Instead |
|---|---|---|---|
| `c4-context` | Who uses the system, which external systems does it talk to? | Inside the system | `c4-container` |
| `c4-container` | Which apps and data stores make up one system, on what technology? | Where they run | `deployment` |
| `c4-component` | Which parts make up one container? Only when it adds value. | Code-level detail | a class or module list in text |
| `deployment` | Which instance runs where in one environment (cluster, namespace, node, managed service)? | Address ranges and routes matter | `network-topology` |
| `network-topology` | Which subnet holds what, how traffic enters, what has no route out? | Who may talk to whom and under which control | `trust-boundaries` |
| `integration-map` | Which systems exchange data, by API, event, file, batch or shared DB? | One system's insides | `c4-container` |
| `event-driven` | Who publishes which topic, who subscribes, where do failures land? | Direct calls | `service-map` |
| `service-map` | Which service calls which, what does an outage or change touch? | Order of calls in one request | `request-path` or a sequence (interaction family) |
| `layered-architecture` | What are the layers, what may call what, where is the rule broken? | Runtime pieces and protocols | `c4-container` |
| `request-path` | Which tiers does one request cross, in what order, where does time go? | Many requests or branching | `service-map`, flowchart (flow family) |
| `trust-boundaries` | Which flows cross a trust zone, under which control? | Network addressing | `network-topology` |

- Spec fields per type: `references/c4.md` (C4 levels), `references/infrastructure.md` (deployment, network, trust), `references/connections.md` (integration, events, services, request path), `references/layered.md`.
- `python ../darshan-singh-meel-diagrams/scripts/diagram.py --list` shows them with the base types.

## High level first, then detail
- Start with `c4-context` (≤ 7 boxes), then `c4-container`; add `c4-component` only for a container the reader must change.
- Many services → `service-map` with `view: "overview"` (one pill per tier or domain), then one detail per group.
- Infrastructure → one `deployment` per environment; `network-topology` for production only unless environments differ in shape.
- Two questions → two diagrams: "what runs where" and "what may talk across which border" are `deployment` and `trust-boundaries`, not one picture.

## Graph style
| Type | Styles | Why |
|---|---|---|
| `integration-map`, `event-driven`, `service-map` | `plain`, `dbt` | dependency graphs: dbt look gives layer columns, solid pills by kind, overview and `dim` impact views |
| `c4-*` | `plain` | C4 has its own notation |
| `request-path` | `plain` | one numbered route, not a dependency graph |
| `deployment`, `network-topology`, `trust-boundaries`, `layered-architecture` | own layout | nested frames or bands; the graph styles need flat columns |
- `airflow` fits none of these: nothing here has a task run state. Service health uses `state: healthy | degraded | down`. CI/CD or deploy pipelines are flow or data family diagrams in airflow style.
- Example in dbt style: `references/examples/booking-services.json` (impact view) and `booking-integrations.json`.

## Process
1. Pick the type above; read its reference file.
2. Write the spec with real names, technology and ports from the code or infra files (Terraform, Helm, compose, config); never invent a component.
3. Build: `python ../darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png` (or `build(spec)`); fix every error and `LAYOUT` line.
4. Look at the PNG, light and `--dark`; read every label; check the picture answers the title.
5. Embed as the base `references/embedding.md` says (inline SVG in HTML, Mermaid in Markdown).

## Notation rules
- C4: every element has a type tag, a one-line description, and technology for containers and components; every line is one direction with a specific label ("Charges card [REST]", never "Uses"); the key says what colours and shapes mean.
- Boxes say their kind in text (tag), so the picture works in greyscale; the product goes in `sub`, never a logo.
- Frames: grey dashed = boundary (account, region, environment, third party); tinted = network, subnet, cluster or trust zone, named in the legend.
- Red only for failure, risk or a broken rule (DLQ, `down`, untrusted zone, layer-rule break).
- Ports and protocols on arrows, ≤ 36 characters; address ranges in frame labels.

## Sizing limits
- ≤ 9 boxes per diagram, ≤ 6 frames, nesting ≤ 4 deep; over that → split per zone, tier or environment.
- Canvas ≤ 1000px: the engine tries LR, then TB; it errors with the fix when both are too wide.
- A group that reads better as a line: `layout: "row"` (side by side) or `"column"` (stacked).
- Crowded ports in TB (two labelled arrows leaving one box downwards): send one out sideways with `from_side`.

## Common mistakes
- Mixing C4 levels (components of two containers, or containers on a context diagram).
- One diagram for deployment, network and trust at once; three readers, three diagrams.
- Every box on a service map: show the tier or domain overview, then the slice that matters, with the rest `dim`.
- Event arrows between services without the topic: the topic is the contract and belongs in the picture.
- Labels that repeat the key ("publish" on every arrow); label only what the key cannot say.
- Vendor icons or brand colours; use the kinds and say the product in `sub`.

## Rules
- Inherits every rule of `darshan-singh-meel-diagrams`: local files only, no artifacts; paths relative to the repo root; no secrets, hostnames of real customers, connection strings or personal data in labels.
- Never edits the base skill or another family; a missing engine feature is a local helper here, raised with the base owner.
- Tests: `python tests/run.py` builds every example and runs the base `check.py` (0 LAYOUT lines).
