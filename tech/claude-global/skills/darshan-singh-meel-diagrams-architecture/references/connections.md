# Connection types: `integration-map`, `event-driven`, `service-map`, `request-path`

Flat node-edge graphs on the base layered layout. Every arrow gets its own port on box shapes, so labelled arrows never share a line. Groups, `rank`, `dim`, `direction`, `max_w`, `kinds` / `edge_kinds` overrides and `legend` work as in the base (`darshan-singh-meel-diagrams/references/spec.md`).

## `integration-map` - which systems exchange data, and how
```json
{"type": "integration-map", "style": "dbt",
 "groups": [{"id": "in", "label": "sources"}, {"id": "core", "label": "booking platform"}, {"id": "out", "label": "consumers"}],
 "nodes": [{"id": "api", "label": "booking-api", "kind": "system", "group": "core"}],
 "edges": [{"from": "api", "to": "fin", "label": "SFTP 02:00", "via": "file"}]}
```
- Node `kind`: `system` (ours), `external`, `hub` (ESB, iPaaS, event bus), `store`, `file` (file drop).
- Edge `via`: `api` (solid) · `event` (dashed lav) · `file` (dotted amber) · `batch` (dashed blue) · `db` (thick: shared database). Label = protocol and frequency.
- Styles: `plain` or `dbt` (columns = sources → us → consumers, solid pills). Not `airflow`: nothing here has a run state.

## `event-driven` - who publishes, who subscribes
- Node `kind`: `producer`, `topic` (topic or queue), `consumer`, `dlq`, `store`, `external`. At least one `topic`.
- Every edge touches a topic or DLQ: into a topic = publish (solid), out of a topic = subscribe (dashed). A direct call is a `service-map` arrow.
- An arrow into a `dlq` is a failure path (red). Put the retry rule in the DLQ `sub` ("after 5 retries").
- Columns are automatic when producers and consumers have no group and all topics share at most one group (the broker): producers | broker | consumers; a DLQ sits after the consumers.
- Name topics as in the broker (`booking.confirmed`); the label on an arrow is only for a filter or key ("key = booking_id").
- Styles: `plain` or `dbt`.

## `service-map` - which service depends on which, what an outage or change touches
- Node `kind`: `gateway` (gateway / BFF), `service`, `worker`, `datastore`, `cache`, `queue`, `external`.
- Edge `call`: `sync` (solid) or `async` (dashed).
- Node `state`: `healthy` (green), `degraded` (amber), `down` (red); the word is added to the sub line. For an incident view.
- Impact view: `style: "dbt"`, groups as tiers, the affected path in full colour, everything else `dim: true`; the Notice names what breaks.
- Overview: `view: "overview"` collapses each group to one pill with counts (dbt style); then one detail diagram per tier or domain.
- Styles: `plain` or `dbt`. Not `airflow`: services are not task runs; use `state` instead.

## `request-path` - one request through the tiers, in order
- Groups = tiers in request order (client, edge, application, data); layout `columns` by default.
- Node `kind`: `client`, `edge`, `app`, `cache`, `store`, `external`; `p95` adds "p95 …" to the sub line.
- Edges in spec order are the hops, numbered 1, 2, … (`numbered: false` turns it off); `ms` appends the time budget ("3 HTTP 20 ms"); `async: true` draws a side call dashed. Number + label + budget ≤ 36 characters.
- One request per diagram. The response path is implied; draw it only when it differs (a second diagram or a sequence diagram in the interaction family).
- Style: `plain` only.

## Mermaid
All four give a Mermaid flowchart (groups as subgraphs, tones as classDef, dashed and thick links). Layout and legend are Mermaid's own; the SVG is the reference.
