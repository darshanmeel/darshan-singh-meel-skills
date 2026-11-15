# Sources

Official pages behind the notation in this family. The base skill's `references/sources.md` covers Mermaid flowcharts, Airflow task states, the Airflow Graph view and dbt resource types.

| Fact | Page |
|---|---|
| Mermaid `erDiagram`: cardinality markers `\|o` `\|\|` `}o` `}\|` (right side `o\|` `\|\|` `o{` `\|{`), `--` identifying vs `..` non-identifying, attributes `type name PK, FK "comment"`, type starts with a letter and allows digits, `-`, `_`, `()`, `[]`, `direction` | https://mermaid.js.org/syntax/entityRelationshipDiagram.html |
| Crow's foot reading (zero or one, exactly one, zero or more, one or more) as used by Mermaid ER | https://mermaid.js.org/syntax/entityRelationshipDiagram.html |
| dbt graph operators `+x`, `x+`, `n+x+m`, `@x` | https://docs.getdbt.com/reference/node-selection/graph-operators |
| dbt resource types (models, seeds, snapshots, sources, exposures, metrics, semantic models, saved queries, analyses, tests, functions) | https://docs.getdbt.com/docs/build/projects |
| Airflow task instance states | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html |
| Airflow TaskGroups organise tasks in Graph view; trigger rules (`all_success` default, `one_failed`, `all_done`, `none_failed`, ...) | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html |
| Asset scheduling: `schedule=[Asset(...)]` waits for all listed assets; `&` / `\|` expressions; producer tasks declare `outlets` | https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html |
| DAG run end states `success`, `failed` | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html |

## Not from an official page (marked check)
- dbt `manifest.json` fields read by `scripts/dbt_manifest.py` (`nodes`, `sources`, `exposures`, `resource_type`, `fqn`, `config.materialized`, `depends_on.nodes`, `attached_node`) - check: https://docs.getdbt.com/reference/artifacts/manifest-json
- DAG run states `queued` and `running` - check: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html
- ADF dependency conditions (Succeeded, Failed, Skipped, Completed), activity run statuses and container activities (ForEach, If Condition, Until, Switch) - check: https://learn.microsoft.com/azure/data-factory/concepts-pipelines-activities
- DFD symbols (Yourdon/DeMarco circles vs Gane-Sarson rounded boxes; this skill uses rounded processes and two-line stores) - no official standard page.
- Medallion layer names (bronze, silver, gold) - check: https://docs.databricks.com/aws/en/lakehouse/medallion
- Data mesh product types (source-aligned, aggregate, consumer-aligned) - no official standard page.
- Colours for every kind, role and state are this family's mapping onto the base palette; none of the pages above define colours.
