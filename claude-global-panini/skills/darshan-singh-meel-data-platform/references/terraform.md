# Terraform

## Structure
- Separate state per environment (separate directories or backends); don't rely on one state for dev and prod.
- Remote state with locking (S3 backend with locking, or `azurerm` backend). Never commit `.tfstate`.
- Pin Terraform and provider versions (`required_version`, `required_providers`); commit `.terraform.lock.hcl`.
- Modules only when reused 2+ times or clearly bounded; no wrapper modules around a single resource.
- `for_each` over `count` for collections whose order may change.
- Variables with types and only the defaults that are truly safe; no unused variables or outputs.

## Safety
- `terraform plan` reviewed in the PR before every `apply`; apply from CI, not laptops, for shared envs.
- `lifecycle { prevent_destroy = true }` on stateful resources (databases, buckets, storage accounts, Snowflake databases).
- Read the plan for `-/+` (replace) and `destroy` — flag them explicitly.
- Bring existing resources in with `import`, don't recreate. Fix drift in code, never in the console.
- No secrets in `.tf`/`.tfvars` committed; read from the secrets manager or CI variables; mark outputs `sensitive`. Never open `*.tfvars`: a committed one is flagged by path (`git ls-files`).

## Data platform specifics
- Manage Snowflake roles, grants, warehouses, databases, and Databricks workspaces, catalogs, grants, cluster policies as code.
- Storage: encryption, public-access block, versioning, lifecycle rules set in code (see `cloud-storage.md`).

## Checks
- `terraform fmt -check`, `terraform validate`, and the project's linter (e.g. `tflint`) in CI.
