# Azure Data Factory (and Synapse pipelines)

- Pipelines, datasets, linked services, and triggers as code: Git integration + ARM/Bicep or Terraform deployment through CI — never edited only in the portal for test/prod.
- **Parameterise** pipelines and datasets (environment, paths, dates) instead of copying them per table or environment; global parameters per environment.
- **Credentials:** linked services use managed identity or Key Vault references — never stored secrets or keys in JSON.
- **Idempotent runs:** each run processes one window (`@trigger().outputs.windowStartTime` / tumbling window) and overwrites or merges that window — never blind appends.
- Copy activity: explicit schema mapping, fault tolerance chosen on purpose (skip vs fail), staging for large loads; choose the right integration runtime (Azure vs self-hosted for on-prem).
- Prefer pushing transformations to the engine (Databricks, Snowflake, SQL) over complex Data Flows or many small activities.
- Retries and timeouts on every activity; failure paths (On failure) that alert — no silent success.
- Avoid deep ForEach nesting and huge activity counts; keep a pipeline to one clear job.
- Monitoring: alerts on failed runs; docs state pipeline names, triggers, schedules, and how to rerun a window.
