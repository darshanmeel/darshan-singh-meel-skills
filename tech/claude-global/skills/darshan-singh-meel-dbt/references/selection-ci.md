# Selection, state, slim CI, defer, clone, retry

## Graph operators
| Syntax | Selects |
|---|---|
| `m` | the model |
| `+m` / `m+` | all parents / all children |
| `2+m` / `m+1` | parents up to 2 levels / children 1 level |
| `@m` | m, its children, and all parents of those children (needed to build children) |
| `a b` | union |
| `a,b` | intersection (`tag:nightly,path:models/marts`) |
| `--exclude x` | removes x |
| `selector:name` | a YAML selector from `selectors.yml`, combinable with other methods (1.12+; older: `--selector name`) |

## Methods (docs: node-selection/methods)
`tag:` · `path:` · `file:` · `fqn:` · `package:` (`package:this`) · `config:materialized:incremental` · `resource_type:` · `source:` · `exposure:` · `metric:` · `semantic_model:` · `saved_query:` · `group:` · `access:public` · `version:latest|old|prerelease|none` · `test_type:unit|data|generic|singular` · `test_name:` · `unit_test:` · `result:error|fail|warn` (with `--state`) · `source_status:fresher` · `state:`.

## State
- `state:new` · `state:modified` (new + changed) · `state:old` · `state:unmodified`.
- Sub-selectors: `.body` (SQL / seed values) · `.configs` (not database/schema/alias/tags/meta) · `.relation` (database/schema/alias) · `.persisted_descriptions` · `.macros` (upstream macro changed) · `.contract`.
- `tags` and `meta` changes never mark a node modified.
- Env-aware configs (`target.name` in Jinja, env vars in `schema`) make every node look modified when the state manifest was built on another target: compare against a manifest built with the same target logic, or use `state:modified.body`.
- `--state` path or env var `DBT_ENGINE_STATE` (v1.11+; older `DBT_STATE`, check: docs.getdbt.com/reference/node-selection/defer).

## Slim CI
```bash
# user runs; prod manifest downloaded to prod-artifacts/
dbt build --select "state:modified+" --defer --state prod-artifacts --target ci
```
- CI builds into a CI schema (per-PR target). No prod manifest yet → `dbt build --select <changed_model>+`. Prod runs from the orchestrator or the dbt platform, never from laptops.
- `--defer`: unselected refs resolve to the state manifest's relations when the node is not selected and does not exist in the target (or `--favor-state`). Ephemeral models are never deferred.
- `--defer-state` defers to another environment than the one compared against.
- `dbt clone --select state:modified+ --state prod-artifacts` creates zero-copy clones (Snowflake, Databricks shallow/deep per adapter) of prod relations into CI so incremental models are tested on real history (check: docs.getdbt.com/reference/commands/clone).
- `dbt retry` reruns from the point of failure using the last `run_results.json`.
- `--empty` builds with zero-row sources/refs: schema check without cost (unit-test parents).
- CI on a dbt platform job uses the deferral environment automatically (check: docs.getdbt.com/docs/deploy/continuous-integration).

## Question catalogue
| Question | Command (offline, Claude may run with a yes) | Read it | Pitfall |
|---|---|---|---|
| What would `state:modified+` build? | `dbt ls --select state:modified+ --state prod-artifacts --resource-type model` | One line per node | Needs a prod manifest from the same dbt version range |
| Why is every model "modified"? | `dbt ls --select state:modified.configs --state …` vs `.body` | Configs only = env-aware config | Fix the config, or select `.body` |
| What does this selector really pick? | `dbt ls --select <expr> --output json --output-keys "unique_id resource_type"` | Full list | `,` is AND, space is OR |
| Which nodes fail if I change macro X? | `dbt ls --select state:modified.macros+ --state …` after the change | Children of nodes using it | Indirect calls through packages count |
| What children does m have (impact)? | `dbt ls --select m+` or `dbt_inventory.py impact m` | Downstream nodes and exposures | `ls` lists tests too: filter `--resource-type` |
| What do the last run's failures depend on? | `dbt ls --select result:error+ --state target` (user's last run artifacts) | Failed nodes and children | `run_results.json` holds only the last invocation |
| Which models are built nightly vs hourly? | `dbt ls --select tag:nightly` / selectors.yml | — | Untagged models are built by neither |
