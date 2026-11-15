# Groups, access, versions, docs, exposures, semantic layer

## Groups and access
```yaml
groups:
  - name: finance
    owner: {name: Finance data team, email: finance-data@example.com}
models:
  - name: fct_revenue
    config: {group: finance, access: public}
```
- `access`: `private` (only same group can ref) · `protected` (default; same project) · `public` (other projects can ref).
- A `ref` that breaks access fails at parse: `Node … attempted to reference node …, which is not allowed`.
- Public models: contract enforced, versions when breaking, description with grain and owner.

## Versions
```yaml
models:
  - name: dim_customer
    latest_version: 2
    versions:
      - v: 2
      - v: 1
        deprecation_date: 2026-06-30
        columns: [{include: all, exclude: [segment_v2]}]
```
- `ref('dim_customer')` → latest; `ref('dim_customer', v=1)` pins. Files `dim_customer_v1.sql`, `dim_customer_v2.sql` (or `defined_in`).
- Relation names get `_v<n>` unless an alias is set; a view `dim_customer` pointing to latest is a common post-hook pattern (check: docs.getdbt.com/docs/mesh/govern/model-versions).

## Cross-project refs (mesh)
- `dependencies.yml` lists upstream projects; `ref('other_project', 'model')` to public models only. Needs the dbt platform metadata for resolution in Core-free setups (check: docs.getdbt.com/docs/mesh/govern/project-dependencies).

## Docs
- `description:` on every mart model and column used by consumers; `{% docs name %}` blocks for shared text; `persist_docs: {relation: true, columns: true}` writes comments to the warehouse.
- `dbt docs generate` connects (catalog query); `dbt parse` gives a manifest without column types.

## Exposures
```yaml
exposures:
  - name: revenue_dashboard
    type: dashboard
    maturity: high
    owner: {name: BI team, email: bi@example.com}
    depends_on: [ref('fct_revenue'), ref('dim_customer')]
```
- Exposures make impact visible (`dbt ls --select +exposure:revenue_dashboard`) and stop "orphan" false positives.

## Semantic layer (MetricFlow)
- `semantic_models` (entities, dimensions, measures on a model) → `metrics` (simple, ratio, derived, cumulative, conversion) → `saved_queries`.
- Query: dbt platform (`dbt sl query`, APIs) or local `mf query` with Core (check: docs.getdbt.com/docs/build/metricflow-commands). Both run SQL on the warehouse → the user runs them.
- Fusion requires the latest Semantic Layer YAML spec (docs: fusion supported-features).
- One entity per grain; the primary entity of the semantic model must match the model's grain, else joins fan out.

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| Which public models have no contract? | `dbt_inventory.py health` → `public_no_contract` | One row per model | Breaking changes reach other projects silently |
| Which models have no owner / group? | `health` → `no_group` | — | Only matters for marts |
| Which models have no description? | `health` → `no_description` | — | Staging descriptions can be one line |
| Which exposures depend on model m? | `dbt_inventory.py impact m` | `exposures:` line | Undeclared dashboards are invisible: check warehouse access (performance-cost.md S6 / D6) |
| Which old versions are still referenced? | `dbt ls --select version:old` + `dbt_inventory.py impact dim_customer.v1` | Children of the old version | Other projects' refs are not in this manifest |
| Why does a metric double count? | Check the semantic model's entity keys vs model grain | Entity not unique = fan-out | Measures on a fact joined to a non-unique dim |
