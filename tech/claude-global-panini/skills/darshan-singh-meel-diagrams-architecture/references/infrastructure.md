# Nested-frame types: `deployment`, `network-topology`, `trust-boundaries`

Where things run and what may talk across which border. Frames nest (`parent`); boxes sit in the innermost frame.

## Spec (same shape for all three)
```json
{"id": "booking-network", "type": "network-topology", "title": "…", "key": "…", "notice": "…",
 "direction": "LR",
 "groups": [{"id": "vpc", "label": "vpc-booking · 10.20.0.0/16", "kind": "network"},
            {"id": "app", "label": "app · 10.20.1.0/24", "kind": "subnet_private", "parent": "vpc", "layout": "row"}],
 "nodes": [{"id": "api", "label": "booking-api", "sub": "ECS tasks", "kind": "container", "group": "app"}],
 "edges": [{"from": "api", "to": "pe", "label": "5432"}]}
```

| Field | Rule |
|---|---|
| group `parent` | id of the enclosing frame; no loops; every frame holds at least one box somewhere inside |
| group `kind` | frame look (below); `frame: "group" \| "boundary"` and `tone` override it |
| group `layout` | `flow` (default: children in columns by arrow order), `row` (side by side), `column` (one under another) |
| group `label` | put the address range or size in it: "app · 10.20.1.0/24", "node pool general · 3 VMs" |
| node `kind` | box look (below); the kind's name is drawn as the tag unless `tag` is set |
| node | `label`, `sub`, `tag`, `shape`, `tone`, `dim`, `href`, `tip`, `group`, `max_w` as in the base |
| edge | base fields: `label` (port, protocol), `style`, `tone`, `kind`, `from_side`, `to_side` |
| `direction` | `LR` or `TB`; unset: LR, then TB when LR is over 1000px |

- Style: `plain` only, and no `view` / `collapse`: frames nest, while the dbt and airflow looks need flat layer columns. Too big → split per zone or environment.

## `deployment` and `network-topology`
- Frame kinds: `environment`, `cloud`, `region`, `zone`, `onprem` (grey dashed boundary) · `network` (VPC / VNet, blue) · `subnet_public` (amber) · `subnet_private` (teal) · `cluster`, `namespace` (lav) · `node` (node pool, VM, managed-service group; soft).
- Box kinds: `user`, `internet` (cloud shape), `dns`, `cdn`, `gateway` (hexagon: internet, NAT, VPN, API gateway), `firewall` (firewall / WAF), `lb`, `endpoint` (private endpoint), `compute`, `container`, `function`, `database`, `storage`, `queue`, `secret`, `server` (on-premises), `external`.
- Generic labelled shapes only; no vendor icons or logos. The product name goes in `sub` ("ECS tasks", "PostgreSQL 16, HA").
- `deployment` answers "which instance runs on which node in this environment" (C4: deployment nodes nest; infrastructure nodes such as DNS, load balancers and firewalls sit beside the container instances). One environment per diagram.
- `network-topology` answers "which subnet holds what, which path enters from the internet, what has no route out".

## `trust-boundaries`
- Frame kinds: `untrusted` (red) · `dmz` (amber) · `internal` (blue) · `restricted` (green: cardholder, health or personal data) · `third_party` (grey dashed).
- Box kinds: `actor`, `process`, `store`, `external`, `control` (hexagon: WAF, gateway, vault).
- Every arrow whose ends sit in different frames is numbered T1, T2, … in spec order and drawn thick; put the control in its label ("T2 mTLS"). Label ≤ 33 characters, the number takes the rest. `number_crossings: false` turns numbering off.
- List the crossings with their control, owner and threat in a table under the diagram; the picture shows where they are.

## Layout notes
- Inside a frame, children follow the arrows: sources first, then what they call. `row` / `column` fix a frame that reads better as a line (two subnets side by side, two replicas).
- A long chain (internet → WAF → LB → app → endpoint → DB) goes TB; a short one with wide frames goes LR.
- Arrows cross frame borders freely; keep the frame count per diagram ≤ 6 so the borders stay readable.
