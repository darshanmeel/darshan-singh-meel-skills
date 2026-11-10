# Cloud storage: AWS S3, Azure Blob / ADLS Gen2

## Both
- Private by default; encryption at rest on; TLS only.
- Access by role/identity, not keys: IAM roles (AWS), managed identities (Azure). Short-lived credentials only.
- Separate buckets/containers (or accounts) per environment.
- Layout: `<zone>/<source>/<table>/dt=YYYY-MM-DD/` (zones e.g. `raw`, `curated`).
- Columnar formats (Parquet/Delta) over CSV/JSON for analytics; avoid many tiny files.
- Lifecycle rules to move or expire old data; versioning or soft delete on important data.
- Warehouses read via integrations, not keys: Snowflake storage integration + external stage; Databricks storage credential + external location.

## AWS S3
- Block Public Access on (account and bucket).
- Default encryption SSE-S3 or SSE-KMS (KMS when key control/audit is required).
- Bucket policies scoped to specific roles and prefixes; deny non-TLS (`aws:SecureTransport`).
- Versioning on for raw/critical buckets; lifecycle to cheaper tiers / expiry.

## Azure Blob / ADLS Gen2
- Hierarchical namespace on for data lake use (ADLS Gen2).
- Access via Azure RBAC data roles (`Storage Blob Data Reader` / `Contributor`) to groups or managed identities.
- Shared keys disabled where possible; SAS tokens only short-lived and scoped.
- Private endpoints / firewall rules for production accounts.
- Soft delete and versioning on; lifecycle management for tiering.
