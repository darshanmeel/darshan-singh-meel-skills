# Technology options by need

Fills the Technology options section. One row per need the requirements raise; needs the input does not raise → left out.

## Rules
- Given stays given: platform the requirements name (warehouse, scheduler, BI tool, CRM) → `given: true`, no alternatives, `why` = how it carries the need. Never re-litigate; real misfit → section 11 risk.
- Pick for this brief, not in general: `why` names the requirement fact that decides it (cadence · volume · connector available · team skill · platform present). Simplest tool meeting the need on the given platform wins; new platform needs a reason the given one cannot meet.
- 2–3 alternatives, one trade-off each: the condition under which it becomes the pick ("if the provider can publish events"), not a feature list.
- Product facts from official docs only (connector names · features · limits · pricing model). Unsure → `check: <official page>` inside trade-off or why; reply lists it. Nothing from memory about limits or prices.
- `source`: official page the row rests on, as site + page title (`docs.snowflake.com: Snowpipe`). URLs only to official sites.
- Network: official docs sites only (list in `darshan-singh-meel-data-platform`); never send requirements, data, company names in a search.

## Catalogue
Candidates per need + official docs home. Pick from here first; unlisted tool fine when its official docs confirm the fit.

| Need | Candidates (official docs) | Usual pick on a given platform |
|---|---|---|
| Orchestration | Apache Airflow (airflow.apache.org/docs) · Dagster (docs.dagster.io) · Prefect (docs.prefect.io) · Azure Data Factory (learn.microsoft.com/azure/data-factory) · Databricks Jobs (docs.databricks.com) · Snowflake Tasks (docs.snowflake.com) | scheduler already in place; none → Airflow |
| Ingestion: SaaS and databases | Fivetran (fivetran.com/docs) · Airbyte (docs.airbyte.com) · Azure Data Factory copy activity · AWS Glue (docs.aws.amazon.com/glue) · Debezium CDC (debezium.io/documentation) | managed connector when one exists for the source; else a scheduler task |
| Ingestion: files (SFTP, drops) | Snowflake stages + COPY INTO / Snowpipe (docs.snowflake.com) · Databricks Auto Loader (docs.databricks.com) · BigQuery load jobs (cloud.google.com/bigquery/docs) · S3 / Azure Blob + event trigger (docs.aws.amazon.com/s3, learn.microsoft.com/azure/storage) | platform's file load on a stage |
| Ingestion: APIs | scheduler task in Python (requests) → stage · Airbyte connector builder · Fivetran (if a connector exists) | scheduler task for small daily payloads |
| Streaming / events | Apache Kafka (kafka.apache.org/documentation) · Amazon Kinesis (docs.aws.amazon.com/kinesis) · Azure Event Hubs (learn.microsoft.com/azure/event-hubs) · Google Pub/Sub (cloud.google.com/pubsub/docs) · Snowpipe Streaming, Snowflake Streams and Tasks (docs.snowflake.com) · Spark Structured Streaming (spark.apache.org/docs) | only when a requirement states a latency batch cannot meet |
| Storage and modelling | Snowflake (docs.snowflake.com) · Databricks with Delta Lake (docs.databricks.com) · BigQuery (cloud.google.com/bigquery/docs) · Amazon Redshift (docs.aws.amazon.com/redshift) · Apache Iceberg tables (iceberg.apache.org/docs) · PostgreSQL (postgresql.org/docs) | given warehouse; raw → core → marts |
| Transformation | dbt Core / dbt Cloud (docs.getdbt.com) · SQLMesh (sqlmesh.readthedocs.io) · Snowflake Dynamic Tables (docs.snowflake.com) · Databricks Lakeflow Declarative Pipelines (docs.databricks.com) · Dataform on BigQuery (cloud.google.com/dataform/docs) · Spark SQL (spark.apache.org/docs) | dbt on the given warehouse |
| Identity resolution / matching | deterministic mapping tables in SQL or dbt (exact keys, validity dates) · Splink (moj-analytical-services.github.io/splink) · Zingg (check: docs.zingg.ai) · AWS Entity Resolution (docs.aws.amazon.com/entityresolution) · Databricks or Snowflake native partner apps (check: platform's marketplace page) | deterministic when keys exact; probabilistic only for dirty names and addresses |
| Segmentation / scoring | SQL marts in dbt · Snowflake Snowpark ML (docs.snowflake.com) · Databricks ML and MLflow (docs.databricks.com, mlflow.org/docs) · Amazon SageMaker (docs.aws.amazon.com/sagemaker) · Azure Machine Learning (learn.microsoft.com/azure/machine-learning) | rules in SQL first; ML once history exists |
| Activation / reverse ETL | Hightouch (hightouch.com/docs) · Census (docs.getcensus.com) · Segment (segment.com/docs) · destination's own import API | reverse ETL from warehouse when several destinations need the same segments |
| Dashboards / consumption | Power BI (learn.microsoft.com/power-bi) · Tableau (help.tableau.com) · Looker (cloud.google.com/looker/docs) · Streamlit in Snowflake (docs.snowflake.com) · Databricks AI/BI dashboards (docs.databricks.com) · Metabase (metabase.com/docs) | BI tool already licensed; none named → owner to decide, platform-native option for the MVP |
| Data quality | dbt tests (docs.getdbt.com) · Great Expectations (docs.greatexpectations.io) · Soda (docs.soda.io) · Snowflake Data Metric Functions (docs.snowflake.com) · Databricks Lakeflow expectations (docs.databricks.com) | tests in the transformation tool; a DQ table for the report |
| Governance / catalogue / lineage | Unity Catalog (docs.databricks.com) · Snowflake Horizon features: tags, masking, row access policies (docs.snowflake.com) · Microsoft Purview (learn.microsoft.com/purview) · DataHub (datahubproject.io/docs) · OpenMetadata (docs.open-metadata.org) · Collibra (check: productresources.collibra.com) · Atlan (check: docs.atlan.com) | platform's own policies first; a catalogue when more than one platform or team must find data |
| Consent / data protection | masking and row access policies of the platform · consent fields modelled in core (purpose, timestamp, source) · OneTrust (check: my.onetrust.com documentation) · Didomi (check: developers.didomi.io) | platform policies; a consent platform only when requirements name one |
| Secrets, access | platform roles + cloud secret store: AWS Secrets Manager (docs.aws.amazon.com/secretsmanager), Azure Key Vault (learn.microsoft.com/azure/key-vault), Google Secret Manager (cloud.google.com/secret-manager/docs) | cloud already in use |

`check:` = docs home not verified at catalogue writing; confirm the page before citing.
