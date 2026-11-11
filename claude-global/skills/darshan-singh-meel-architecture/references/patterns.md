# Re-architecture moves — catalogue
A move is per component: **signal in the graph or code → move → fits · not · impact · pick + alternatives**.
- **No signal, no move.** Each move cites its signal (`signal: [path:line]`); a tool swap without one is not proposed.
- **Current stack first:** a feature of the pinned versions (incremental, liquid clustering, Dynamic Tables, auto-suspend, retries) beats a new tool. Unsure of a version, name or feature → its official docs (the section's **Docs** line, or the data-platform skill list); name the page in `source`.
- **Hybrid is normal:** the target keeps what works. Every component gets one row in `proposal.moves`: `keep` (why it stays) · `move` (to what, which change) · `later` (what must be true first). Full redesign only when signals cover most components.
- **Pick + alternatives on every row:** a `move` names one pick that fits this repo; every row (`keep` and `later` too) lists 2–3 current alternatives with one trade-off each, so the user can say "use <alternative> instead". The lists below are starting points; check what is current. A tool the user names that is not listed: check its fit in its docs, add it (replacing the weakest), then `--use`.
- **Fits / Not** guard every move: a signal alone is not enough; a component matching **Not** stays (`keep`, say why).
- **Free in target:** per fix proposed on the current engine, note whether the target tool provides it built in (`free_in`: null-safe merge, latest-per-key, run order, lineage, tests, retries). ≥ 3 free fixes are a signal for the move: never rebuild by hand what the target gives.
- **Size both options:** a script counts the lines, tasks and tests the move replaces; estimate the target (SQL models ~20–40 lines each plus shared macros). A rewrite is never listed with costs only.
- **Current stack vs catalogue pick:** both fit → pick the one that keeps tests, lineage and reviewable code; the other goes in alternatives, and an option smaller than the pick gets `why_not` with its docs page.
- **`later` needs a shown blocker** (a cited line, a docs page, a missing feature). An assumed org constraint ("until a template exists") → `move` now and list the constraint as a question.
- Spec: `changes[].pattern` = the id after `###` (build WARNs on an unknown id).
- Impact words: **cost** (compute, licences, people) · **perf** (run time, latency, memory) · **maint** (edits per change, on-call, upgrades) · **debt** (copies, drift, hand-rolled framework).

## Pipeline — Spark / Python batch
**Docs:** docs.getdbt.com · sqlmesh.readthedocs.io · spark.apache.org/docs · docs.databricks.com · duckdb.org/docs · docs.pola.rs · pandas.pydata.org/docs

### `spark-sql-models`
- **Signal:** PySpark DataFrame code doing select/join/filter/groupBy/window only; many near-copy jobs; hand-written merge, dedup or upsert; no lineage; custom run order.
- **Move:** declarative SQL models with incremental/merge materialisation, tests and lineage (dbt on the same engine).
- **Fits:** transforms are SQL-expressible; analysts read SQL; ≥ 5 similar jobs. **Not:** UDF-heavy, ML features, row-by-row API calls, complex state machines.
- **Not a blocker until checked:** dynamic schemas and nested flattening. Check the adapter first (catalog-driven column macros, merge with schema evolution, `on_schema_change`, adapter macro overrides) and name the doc page.
- **Comes free:** null-safe merge keys, latest-per-key dedup, run order from `ref()`, tests and lineage: fixes for these on the old engine count toward the move.
- **Impact:** debt − (copies become one macro or model) · maint − (one edit per rule, tests per model) · perf ≈ or + (incremental) · cost ≈ to − (same compute, fewer full rebuilds).
- **Pick / alternatives:** dbt (dbt-databricks / dbt-spark) · SQLMesh (virtual environments, column lineage) · Spark SQL files run by the platform's jobs · Lakeflow / Spark Declarative Pipelines (managed, platform lock-in).

### `pyspark-to-spark-sql`
- **Signal:** one or a few PySpark jobs whose logic is plain SQL, no shared macros needed.
- **Move:** the same job as Spark SQL (a `.sql` file or `spark.sql`), kept in the current scheduler.
- **Fits:** small repo, no appetite for a new tool. **Not:** many models with shared logic (→ `spark-sql-models`).
- **Impact:** maint − (readable by SQL users) · debt − · cost ≈ · perf ≈.
- **Pick / alternatives:** Spark SQL files · dbt (when it grows) · SQL notebooks in the platform's jobs.

### `pandas-to-duckdb`
- **Signal:** pandas joins/groupbys on files that fit one machine; `read_csv`/`read_parquet` → transform → write; memory errors or chunk loops; SQL-shaped logic in Python.
- **Move:** DuckDB SQL over the files (Parquet/CSV in place); dbt-duckdb when there are several models.
- **Fits:** single-node data (up to ~100s of GB), batch. **Not:** data already in a warehouse (→ `pandas-to-warehouse`), heavy per-row Python, multi-writer OLTP.
- **Impact:** perf + (columnar, out-of-core; measure one run before and after) · cost − (no cluster) · maint − (SQL, fewer lines) · debt −.
- **Pick / alternatives:** DuckDB · Polars (lazy DataFrames, stays in Python) · dbt-duckdb (models, tests, lineage) · warehouse SQL.

### `pandas-to-warehouse`
- **Signal:** Python pulls warehouse tables into pandas, transforms, writes back.
- **Move:** push the transform into warehouse SQL (a view, a dbt model, a Dynamic Table).
- **Fits:** data is already there; volume grows. **Not:** logic needs Python libraries (→ Snowpark / PySpark UDF, still in-engine).
- **Impact:** perf + (no round trip) · cost − (egress, VM) · maint − · debt −.
- **Pick / alternatives:** dbt model · warehouse-native (Snowflake Dynamic Tables, Databricks materialised views) · Snowpark / PySpark in-engine.

### `notebooks-to-jobs`
- **Signal:** notebooks as pipeline code: `%run` chains, widgets as parameters, jobs that run notebooks in order, no unit tests.
- **Move:** the logic as a package (wheel) or SQL models run as job tasks; notebooks only for exploration.
- **Fits:** notebooks scheduled in prod. **Not:** one-off analysis or reports read as notebooks.
- **Impact:** maint − (diffs, tests, imports) · debt − · risk − (no hidden state between cells) · cost ≈.
- **Pick / alternatives:** Python wheel task in the platform's jobs · dbt models (SQL-shaped logic) · Lakeflow Declarative Pipelines (managed, platform lock-in).

### `tables-to-open-format`
- **Signal:** plain Parquet or Hive tables rewritten by overwrite; manual partition repair (`MSCK REPAIR`); no MERGE; readers see half-written data.
- **Move:** a table format with ACID MERGE, schema evolution and time travel.
- **Fits:** a lake with updates, deletes or concurrent writers. **Not:** write-once archives read by one engine.
- **Impact:** risk − (atomic writes) · perf + (data skipping, compaction) · maint − (no partition repair) · cost ≈.
- **Pick / alternatives:** Delta Lake (Databricks-native, CDF) · Apache Iceberg (multi-engine: Spark, Snowflake, Athena, Trino) · Apache Hudi (record-level upserts).

### `full-to-incremental`
- **Signal:** full reload or `overwrite` each run while only recent rows change; run time grows with history.
- **Move:** incremental load by watermark or CDF/CDC with merge on a key and a lookback window.
- **Fits:** append-mostly data with a reliable change column. **Not:** small tables (< minutes to rebuild), no change column and no CDC.
- **Impact:** cost − (scan days not years) · perf + · risk + (late data: lookback, full-refresh path).
- **Pick / alternatives:** the current tool's incremental mode (dbt incremental, Delta MERGE, Snowflake streams) · CDC ingestion (Debezium, Lakeflow Connect, Fivetran) · Dynamic Tables.
- **Per model:** watermark on a change column (default) or CDF/CDC with the cursor kept in the target (e.g. a table property); say which and why.

## dbt / SQL warehouse
**Docs:** docs.getdbt.com · docs.snowflake.com · docs.databricks.com · cube.dev/docs

### `dbt-shared-logic`
- **Signal:** the same CASE/join/filter in ≥ 2 models; magic numbers in SQL.
- **Move:** one intermediate model, macro or seed; models `ref()` it.
- **Fits:** ≥ 2 models repeat the rule. **Not:** rules that differ on purpose per model (name the difference).
- **Impact:** debt − · maint − (one edit) · risk − (no drift).
- **Pick / alternatives:** intermediate model · macro · seed/lookup table · semantic layer metric (dbt Semantic Layer, Cube).

### `dbt-materialisation`
- **Signal:** `table` on large, append-mostly models; views stacked deep and slow; full refresh in prod schedule.
- **Move:** incremental (`merge`, `microbatch`, `insert_overwrite`) or clustering on the read key.
- **Fits:** models over ~1 M rows or minutes to build. **Not:** small models (a `table` rebuild is cheaper than merge logic).
- **Impact:** cost − · perf + · risk + (late rows, schema change: `on_schema_change`).
- **Pick / alternatives:** dbt incremental (microbatch for time series) · Dynamic Tables / materialised views · clustering or partition pruning only.

### `procs-to-models`
- **Signal:** stored procedures or Task/job chains doing INSERT/MERGE in sequence; SQL built in strings; order kept by hand.
- **Move:** SQL models with `ref()` order, incremental materialisation and tests.
- **Fits:** set-based SQL. **Not:** admin procedures (grants, maintenance) or loops calling external APIs.
- **Impact:** maint − (one file per table, lineage) · debt − · risk − (tests) · cost ≈.
- **Pick / alternatives:** dbt · SQLMesh · Snowflake Dynamic Tables / Databricks materialised views (no scheduler, fewer tests).

### `dbt-ci`
- **Signal:** deploys from laptops, no CI, no slim CI, tests only in prod.
- **Move:** CI builds changed models and children (`state:modified+`, deferral) on pull request; deploy on merge.
- **Fits:** ≥ 2 people change models, or prod breaks after merges. **Not:** a single maintainer with a scheduled prod job and a test run (say so).
- **Impact:** risk − · maint − · cost + (small CI compute).
- **Pick / alternatives:** the repo's CI (GitHub Actions, Azure Pipelines) with dbt Core · dbt platform jobs · Databricks Asset Bundles / platform CI.

## Orchestration
**Docs:** airflow.apache.org/docs · docs.aws.amazon.com/mwaa · cloud.google.com/composer/docs · astronomer.io/docs · docs.dagster.io · docs.prefect.io · learn.microsoft.com/azure/data-factory · docs.databricks.com (Lakeflow Jobs) · docs.snowflake.com (Tasks)

### `adf-to-code`
- **Signal:** ADF pipelines with code-like logic: nested If/ForEach/Switch, long dynamic expressions, copy-paste pipelines per source, logic hidden in JSON, no unit tests.
- **Move:** orchestration as code; ADF kept only for what it does well (copy activities, self-hosted IR) or retired.
- **Fits:** engineers own it; logic changes often. **Not:** a few linear copy pipelines run by non-coders (keep ADF; use parameters and templates).
- **Impact:** maint − (diffable, testable, one template per pattern) · debt − · cost ≈ (scheduler fee vs ADF activity runs) · risk + (new platform to run).
- **Pick / alternatives:** Airflow (Astronomer, MWAA or self-run on AKS; DAGs and tasks as Python) · Dagster (assets, lineage) · Prefect (light, Python-first) · platform jobs (Databricks Lakeflow Jobs, Fabric Data Factory pipelines) when everything already runs there.

### `cron-to-orchestrator`
- **Signal:** cron chains, `sleep` between jobs, shell scripts calling scripts, hand-written retry or dependency code, a status table polled by jobs.
- **Move:** an orchestrator with dependencies, retries, alerts and backfill.
- **Fits:** ≥ 3 dependent jobs or any backfill need. **Not:** one independent job (keep cron + an alert).
- **Impact:** risk − (retries, alerts) · maint − (no home-made framework) · debt − · cost + (scheduler).
- **Pick / alternatives:** the platform's native jobs if all tasks run there (Databricks Lakeflow Jobs, Snowflake Tasks) · Airflow, self-run or managed (MWAA, Cloud Composer, Astronomer) · Dagster · Prefect.

### `task-per-model-orchestration`
- **Signal:** a platform job with one task per table or entity, plus a dispatcher that maps a parameter to a job class.
- **Move:** one build task that runs the tool's own dependency graph with threads (`dbt build --threads N`); `max_concurrent_runs: 1` when tasks merge into shared tables.
- **Fits:** ≥ 5 tasks that only run models. **Not:** tasks with their own schedules, owners or compute.
- **Keep:** platform retries plus the tool's rerun-from-failure command (`dbt retry`); a rebuild drops these easily.
- **Impact:** maint − (no dispatcher, no edges by hand) · debt − · perf ≈ to + (threads) · risk ≈ (one task fails as a unit: rerun from failure).
- **Pick / alternatives:** one dbt build task in the platform job · Lakeflow Declarative Pipelines (managed graph) · Airflow / Dagster with per-model tasks (Cosmos, dagster-dbt) when models need their own schedules.

### `orchestrator-native`
- **Signal:** a self-hosted scheduler VM (single point of failure), all tasks on one platform, Airflow used only to call that platform.
- **Move:** managed scheduler, or the platform's native jobs.
- **Fits:** every task runs on one platform or managed service. **Not:** tasks across several clouds or on-prem agents (keep an orchestrator).
- **Impact:** risk − · maint − (no patching) · cost ± (fee vs VM).
- **Pick / alternatives:** managed Airflow (MWAA, Cloud Composer, Astronomer) · platform jobs (Lakeflow Jobs, Snowflake Tasks) · Dagster+ / Prefect Cloud.

### Target checklist for any incremental pipeline (in `technical`, or a question)
- **Merge:** dedup within the batch on the unique key before MERGE; an explicit tie-breaker (timestamp → offset or sequence → hash); say what a re-read of the same event does.
- **Cursor:** never "max of a row column" (stalls on empty batches); a watermark with lookback, or a CDF version stored as table metadata, chosen per model.
- **Rows gone from the source** (removed children, deleted keys): give hard delete and soft delete + audit log as two options, tied to a consumer question.
- **Data quality sink:** duplicates and explode row-loss checks logged to a side table (`dq-side-table`), warning tests for drift.
- **Packaging:** version upper bounds (e.g. `dbt-core<2`), offline wheels where the runtime has no package index, a sandbox mode for restricted workspaces.

## Compute
**Docs:** docs.databricks.com · docs.snowflake.com · the cloud's pricing pages

### `serverless-compute`
- **Signal:** fixed-size job clusters for SQL-shaped transforms; start-up time per task; no autoscaling or auto-stop.
- **Move:** serverless SQL warehouse or serverless jobs, measured first: run time and cost of one week before and after.
- **Fits:** transforms move to SQL; runs are short or spiky. **Not:** long steady jobs where reserved compute is cheaper.
- **Not a reason to keep:** "no run history in the repo". Make it a `later` with a measure-first step.
- **Impact:** perf + (no cluster start) · maint − (no node sizing) · cost ± (per-second billing vs a higher unit price).
- **Pick / alternatives:** serverless SQL warehouse (dbt) · serverless jobs compute · job clusters with autoscaling and spot.

## Migration and data quality
**Docs:** docs.getdbt.com · hub.getdbt.com (audit_helper) · docs.greatexpectations.io · docs.soda.io · docs.databricks.com (expectations)

### `parallel-run-cutover`
- **Signal:** any rewrite of a pipeline whose outputs have consumers.
- **Move:** build into a separate schema next to the old pipeline; compare row counts and keys per table; cut over by one committed config value; roll back by switching it back.
- **Fits:** outputs have consumers that cannot pause. **Not:** an internal table nobody reads yet (cut over directly).
- **Impact:** risk − (no big bang) · cost + (double compute during the parallel run).
- **Pick / alternatives:** separate target schema + a compare script or tests · dbt `audit_helper` / data-diff tools · shadow tables in the same schema.

### `soft-delete-flag`
- **Signal:** rows removed at the source stay in the target, and the consumer contract for deletes is unknown.
- **Move:** an `is_deleted` flag set after the merge, views filter it, each flagged row logged; hard delete only when the contract asks.
- **Fits:** deletes at the source must disappear downstream and the contract is unclear. **Not:** append-only facts (no deletes to carry).
- **Impact:** risk − (reversible; no delete rows for downstream CDF readers) · cost ≈ (one UPDATE with EXISTS per child table).
- **Pick / alternatives:** flag + view filter · hard delete in the MERGE (`WHEN NOT MATCHED BY SOURCE`) · a deletion date column the consumer reads.

### `dq-side-table`
- **Signal:** dedup or filters drop rows silently; known defects kept for parity.
- **Move:** log dropped duplicates, null keys and removed rows to a partitioned issues table, reported after each run. A rewrite that keeps a known defect for parity logs it and lists it as an open question.
- **Fits:** rows are dropped or changed by rules. **Not:** a pipeline that never filters (tests are enough).
- **Impact:** risk − (loss is visible) · maint − (cause found from the table) · cost ≈.
- **Pick / alternatives:** an issues table written by pre/post-hooks · dbt tests with `store_failures` · the platform's expectations (Lakeflow expectations, Great Expectations, Soda).

## Web API / backend
**Docs:** fastapi.tiangolo.com · docs.pydantic.dev · docs.sqlalchemy.org · alembic.sqlalchemy.org · docs.celeryq.dev · docs.docker.com · kubernetes.io/docs · opentelemetry.io/docs

### `api-config-secrets`
- **Signal:** secrets or keys in compose files, settings, or code; one config for all environments.
- **Move:** settings from environment or a secret store; **rotate** every value already committed (moving it is not enough); stateful stores need their own change step (e.g. `ALTER ROLE … PASSWORD` for a database volume already initialised).
- **Fits:** any secret in the repo or a shared default. **Not:** values that are public by design (say which).
- **Impact:** risk − · maint ≈.
- **Pick / alternatives:** env + the platform's secret store (Key Vault, Secrets Manager, Docker/K8s secrets) · Pydantic Settings / framework settings · SOPS-encrypted files.

### `api-layering`
- **Signal:** SQL or business rules inside route handlers; the same query in several handlers; handlers > 100 lines.
- **Move:** handler → service → repository; one place per rule.
- **Fits:** ≥ 2 handlers share a query or rule. **Not:** a few thin CRUD handlers (layers add files, no saving).
- **Impact:** debt − · maint − (unit tests without HTTP) · perf ≈.
- **Pick / alternatives:** plain service modules · the framework's DI (FastAPI `Depends`, Spring) · a query layer (SQLAlchemy 2.x, Prisma).

### `api-schema-migrations`
- **Signal:** `create_all`, manual DDL, schema drift between environments.
- **Move:** versioned migrations run once per deploy, before the app starts (separate job, not in the app command).
- **Fits:** a database the app owns. **Not:** a schema owned by another team (read-only models).
- **Impact:** risk − · maint −.
- **Pick / alternatives:** Alembic · Flyway / Liquibase · the framework's migrations (Django, Prisma).

### `api-async-work`
- **Signal:** long work inside a request (emails, reports, file processing); timeouts; retries by the client.
- **Move:** a queue and a worker; the request returns a job id.
- **Fits:** requests over ~5 s or that time out. **Not:** short work that can be lost (framework background task).
- **Impact:** perf + (latency) · risk − · cost + (worker).
- **Pick / alternatives:** the cloud queue + worker (SQS, Service Bus) · Celery / RQ / Dramatiq · framework background tasks (only for short, losable work).

### `api-health-ops`
- **Signal:** no restart policy, no health probe, no structured logs, single instance.
- **Move:** health and readiness probes, restart policy, structured logs, ≥ 2 replicas behind the load balancer when state allows.
- **Fits:** a service with users. **Not:** a local tool or one-off job.
- **Impact:** risk − · maint −.
- **Pick / alternatives:** compose/K8s probes + restart · the platform's app service health checks · OpenTelemetry for traces and logs.

## UI / frontend
**Docs:** react.dev · vite.dev · nextjs.org/docs · reactrouter.com · tanstack.com/query · swr.vercel.app · openapi-ts.dev · orval.dev

### `ui-build-serve`
- **Signal:** dev server in production, no build step, CRA or other unmaintained tooling.
- **Move:** a production build served as static files (with SPA fallback to `index.html` for client routes; API origin and CORS updated together).
- **Fits:** the UI is served to users. **Not:** a local dev-only tool.
- **Impact:** perf + (bundle, caching) · risk − · maint − (maintained tooling).
- **Pick / alternatives:** Vite build + static server or CDN · Next.js / Remix when SSR is needed · the platform's static hosting (Static Web Apps, S3 + CloudFront).

### `ui-server-state`
- **Signal:** fetch in many components, hand-written caches, loading flags copied, stale data bugs.
- **Move:** one server-state library; components read hooks.
- **Fits:** ≥ 3 components fetch the same data. **Not:** one or two pages with simple fetches.
- **Impact:** debt − · maint − · perf + (dedup, cache).
- **Pick / alternatives:** TanStack Query · SWR · framework loaders (React Router, Next.js).

### `ui-typed-api`
- **Signal:** API types written by hand in the UI; contract drift bugs.
- **Move:** types generated from the API schema (OpenAPI) in CI.
- **Fits:** the API publishes an OpenAPI schema. **Not:** a third-party API without one (hand types plus a contract test).
- **Impact:** risk − · debt −.
- **Pick / alternatives:** openapi-typescript · orval · tRPC / GraphQL codegen (when both sides are TypeScript).

## CLI / library
**Docs:** docs.python.org · typer.tiangolo.com · click.palletsprojects.com · docs.astral.sh/uv · python-poetry.org/docs · hatch.pypa.io · packaging.python.org

### `cli-framework`
- **Signal:** hand-parsed `sys.argv`, copy-paste subcommands, no `--help`.
- **Move:** a CLI framework; one function per command.
- **Fits:** ≥ 3 subcommands or options. **Not:** one command with one argument (argparse or nothing).
- **Impact:** maint − · debt −.
- **Pick / alternatives:** argparse (stdlib, no dependency) · Typer · Click.

### `lib-packaging`
- **Signal:** `setup.py` with logic, unpinned dependencies, no lock file, manual release.
- **Move:** `pyproject.toml`, a lock file, release from CI on a tag.
- **Fits:** the code is installed or released. **Not:** a script folder nobody installs.
- **Impact:** risk − · maint −.
- **Pick / alternatives:** uv · Poetry · Hatch / PDM.

### `lib-public-api`
- **Signal:** callers import private modules; breaking changes without a version bump.
- **Move:** one public module (`__all__`), semantic versions, deprecation warnings before removal.
- **Fits:** other repos import it. **Not:** an internal package with one caller.
- **Impact:** risk − · debt −.
- **Pick / alternatives:** explicit `__all__` + changelog · API docs generated from docstrings · type stubs and a type check in CI.

## Infra / Terraform
**Docs:** developer.hashicorp.com/terraform · opentofu.org/docs · terragrunt.gruntwork.io/docs · runatlantis.io/docs · docs.databricks.com/dev-tools/bundles

### `tf-modules`
- **Signal:** per-environment folders with near-copy `.tf` files; drift between dev/test/prod; long copy diffs.
- **Move:** one module per pattern, one small root per environment passing variables.
- **Fits:** ≥ 2 environments with the same shape. **Not:** environments that differ on purpose (keep separate, document why).
- **Impact:** debt − · maint − (one edit) · risk − (no drift).
- **Pick / alternatives:** Terraform modules + per-env `tfvars` (never committed with secrets) · Terragrunt (DRY roots and backends) · workspaces (only for identical environments) · OpenTofu (same language, open licence).

### `tf-ci`
- **Signal:** `apply` from laptops, local state, no plan review.
- **Move:** remote state with locking; plan on pull request, apply on merge with a deploy identity.
- **Fits:** ≥ 2 people apply, or prod infra. **Not:** a personal sandbox.
- **Impact:** risk − · maint −.
- **Pick / alternatives:** the repo's CI + remote backend (S3 + lock, Azure Storage, GCS) · HCP Terraform / Spacelift / env0 · Atlantis.

### `deploy-bundles`
- **Signal:** job JSON or templates per environment; deploys by hand (`databricks jobs create/reset`, CLI scripts, README steps); pins edited per run.
- **Move:** jobs, pipelines and their config as one bundle with a target per environment, deployed from CI on merge.
- **Fits:** Databricks jobs or pipelines. **Not:** other platforms (→ `tf-ci` or the platform's own IaC).
- **Impact:** risk − (same code in every environment) · maint − (one file, `bundle validate`) · debt −.
- **Pick / alternatives:** Databricks Asset Bundles · Terraform Databricks provider (infra and jobs in one state) · CI calling the Jobs API (no new tool, more script).

### `tf-clickops`
- **Signal:** resources referenced but not defined in code; README steps "create in the portal".
- **Move:** import them into code (`import` blocks), then manage there.
- **Fits:** resources this team owns. **Not:** shared resources another team manages (data sources).
- **Impact:** risk − · maint −.
- **Pick / alternatives:** `import` blocks · the provider's export tools (aztfexport) · leave as data sources when another team owns them.

## ML / streaming
**Docs:** mlflow.org/docs · docs.databricks.com · feast.dev · spark.apache.org/docs · nightlies.apache.org/flink · the cloud's ML and stream docs

### `ml-tracking`
- **Signal:** models saved to folders by hand, metrics in notebooks, no record of which data trained what.
- **Move:** experiment tracking and a model registry; training as a scheduled job.
- **Fits:** models retrained or compared. **Not:** one model trained once.
- **Impact:** risk − · maint −.
- **Pick / alternatives:** MLflow (managed on Databricks) · the cloud's ML platform (SageMaker, Azure ML, Vertex) · Weights & Biases.

### `ml-features-sql`
- **Signal:** feature code in pandas duplicated between training and serving.
- **Move:** features as SQL models or a feature store, one definition for both.
- **Fits:** the same features in training and serving. **Not:** features only used offline once.
- **Impact:** debt − · risk − (training/serving skew).
- **Pick / alternatives:** dbt models as feature tables · the platform's feature store (Databricks, SageMaker, Feast) · DuckDB SQL for single-node.

### `stream-to-batch`
- **Signal:** a streaming job whose consumers read hourly or daily; always-on cluster at low load.
- **Move:** scheduled micro-batch (trigger once / available now) or incremental batch.
- **Fits:** consumers read hourly or slower. **Not:** alerts or SLAs in minutes.
- **Impact:** cost − (no always-on compute) · perf − (latency rises to the schedule) · maint −.
- **Pick / alternatives:** Structured Streaming `availableNow` · incremental batch (dbt, Delta CDF) · Dynamic Tables with a target lag.

### `batch-to-stream`
- **Signal:** batch polling with short intervals; consumers need minutes, not hours.
- **Move:** event stream with exactly-once sinks.
- **Fits:** a consumer needs minutes and says so. **Not:** "faster would be nice" (cost rises for no user).
- **Impact:** perf + (latency) · cost + · maint +.
- **Pick / alternatives:** Spark Structured Streaming · Flink · the cloud's managed stream (Kinesis, Event Hubs) + Snowpipe Streaming / Lakeflow.

## Monorepo
**Docs:** docs.astral.sh/uv · pnpm.io · nx.dev · turbo.build · pantsbuild.org

### `mono-ci-paths`
- **Signal:** every change runs every pipeline; long CI; unrelated deploys.
- **Move:** CI per package with path filters; build only what changed and what depends on it.
- **Fits:** ≥ 3 packages and CI over ~10 min. **Not:** a small repo where everything builds in minutes.
- **Impact:** cost − (CI minutes) · perf + (feedback) · risk ≈.
- **Pick / alternatives:** CI path filters · uv / pnpm workspaces · Nx / Turborepo / Pants (dependency graph, caching).

### `mono-shared-code`
- **Signal:** the same helper copied into several packages; version drift between copies.
- **Move:** one shared internal package; others depend on it.
- **Fits:** ≥ 2 copies that drift. **Not:** packages that must ship and version alone (keep copies, say why).
- **Impact:** debt − · maint −.
- **Pick / alternatives:** workspace package · published internal package · keep copies when packages must ship alone (say why).
