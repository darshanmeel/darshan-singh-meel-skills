# Diagrams review - generated-docs/orders-pipeline.html - 2026-11-16 10:40

**Verdict:** Ready after Must fixes - both diagrams share one id, and the run diagram shows the wrong operator for the alert task.

**Scope:** `generated-docs/orders-pipeline.html`, specs in `generated-docs/diagrams/` · Source: repo code (`models/`, `dags/orders_nightly.py`) · Mermaid: HTML only
**Script:** `review_diagrams.py` → 4 MUST, 1 SHOULD (the 4 `duplicate id` lines and the `id reused` line are one defect → Must 1; Must 2 and both Shoulds come from the source and the PNGs) · 2 specs rebuilt, 0 LAYOUT lines · PNGs looked at: 2 light + 2 dark

## Must
1. **Two diagrams share the id `shop-lineage`** - `generated-docs/diagrams/orders-nightly.json#shop-lineage`
   - Why: the page has `dg-shop-lineage`, `fig-shop-lineage` and the title and desc ids twice; the second figure's CSS scope and arrow markers resolve to the first, and `#fig-shop-lineage` links to the wrong figure.
   - Fix: `"id": "orders-nightly-run"` in `orders-nightly.json`; rebuild the page.
2. **`notify_on_call` drawn as `EmptyOperator`** - `orders-nightly.json#shop-lineage` (node `notify`)
   - Why: `dags/orders_nightly.py:48` defines it as `SlackWebhookOperator`; an EmptyOperator sends nothing, so the picture says the on-call alert is a no-op.
   - Fix: `"operator": "SlackWebhookOperator"` on node `notify`.

## Should
1. **Sources of `dim_customers` cannot be read** - `shop-lineage.json#shop-lineage` (PNG: shop-lineage.shop-lineage.png, x ≈ 635)
   - Why: the arrows from `stg_orders`, `stg_payments` and `fx_rates` join one vertical trunk before splitting to `dim_customers` and `fct_orders`, so the picture suggests `stg_payments` feeds `dim_customers`; `models/marts/dim_customers.sql:3` reads only `stg_orders`.
   - Fix: `"own_port": true` on edge `stg_orders -> dim_customers`, or `route(..., spread=True)` through `"spread": true` in the spec.
2. **Notice says "skipped", the boxes say "upstream failed"** - `orders-nightly.json#shop-lineage`
   - Why: `skipped` is its own Airflow state (lilac); a reader looking for lilac boxes finds none. "Both marts" also reads as two mart tasks; the DAG has one, `dbt_marts`.
   - Fix: `"notice": "load_payments failed, so dbt_staging and dbt_marts ended upstream_failed; only the alert ran."`

## Other
- Edge label `one_failed` on `load_payments -> notify` · the Airflow look writes a trigger rule in the task box · move it to node `notify` as `sub: "rule one_failed"`.

## Re-derived from the source
| Diagram | Expected (from source) | Drawn | Match? |
|---|---|---|---|
| `shop-lineage` | 2 sources, 1 seed, `stg_orders`, `stg_payments` (`models/staging/`), `fct_orders` ← both staging + `fx_rates`, `dim_customers` ← `stg_orders` (`models/marts/*.sql`), exposure `revenue_dashboard` ← both marts (`models/exposures.yml:4`) | same 8 nodes, 8 edges | Yes (edges right, trunk misleads → Should 1) |
| `orders-nightly` | `wait_for_export >> [load_orders, load_payments] >> dbt_staging >> dbt_marts`; `notify_on_call` `SlackWebhookOperator`, `trigger_rule="one_failed"` (`dags/orders_nightly.py:12-52`) | same tasks and edges; `notify` as `EmptyOperator` | No → Must 2 |

## Not checked
- The cause "expired API token" in the Notice comes from the run log of that night, not from the repo - the DAG owner can confirm it from the task log of `load_payments`.
