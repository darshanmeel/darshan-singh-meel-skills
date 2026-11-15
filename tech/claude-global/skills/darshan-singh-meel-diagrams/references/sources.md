# Sources

Official pages the base skill relies on. Family skills keep their own `sources.md` for their notations (UML on omg.org, C4 on c4model.com, BPMN on omg.org).

| Fact | Page |
|---|---|
| Mermaid flowchart syntax: node shapes, `-->` `-.->` `==>` `---` `~~~`, link text, `subgraph id [title]`, `classDef` / `class`, entity codes (`#quot;`, `#35;`), lowercase `end` breaks a flowchart, frontmatter `title` | https://mermaid.js.org/syntax/flowchart.html |
| Airflow task instance states: none, scheduled, queued, running, success, restarting, failed, skipped, upstream_failed, up_for_retry, up_for_reschedule, deferred, awaiting_input, removed | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html |
| Airflow Graph view: node = task, edges = dependencies, run-specific states overlaid, asset overlays and DAG-to-DAG asset dependencies | https://airflow.apache.org/docs/apache-airflow/stable/ui.html |
| dbt lineage graph: DAG of the project's resources, filterable with `--select` / `--exclude` | https://docs.getdbt.com/docs/build/view-documentation |
| dbt resource types: models, snapshots, seeds, data tests, sources, exposures, metrics, groups, analysis, semantic models, saved queries, user-defined functions | https://docs.getdbt.com/docs/build/projects |

- Colours for dbt kinds and Airflow states are this skill's own palette mapping; neither page defines colours. Task-group collapse in the Graph view: check: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html (TaskGroups).
- Palette and fonts: `darshan-singh-meel-docs-v2/references/templates/style.css` in this repo.
