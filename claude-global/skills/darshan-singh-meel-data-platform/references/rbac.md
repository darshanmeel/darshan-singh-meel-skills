# Access model (RBAC) across platforms

```
people → groups (identity provider) → functional roles → access roles → objects
pipelines → service identity (one per pipeline) → functional role → access roles
```

- Separate read, write, and admin; default to read-only.
- One service identity per pipeline/app, scoped to exactly what it touches.
- Environment isolation: dev roles can't write prod; prod write only for pipeline identities.
- Sensitive data: masking / row filters at the platform level, not in each query.
- No shared passwords; no long-lived keys; rotate what can't be avoided.
- Docs state for each environment: roles, what they can do, who gets them, how to request.

| Platform | Group/role mechanism | Service identity |
|---|---|---|
| Snowflake | Access roles → functional roles; SCIM-synced groups | `TYPE=SERVICE` user, key-pair |
| Databricks | Unity Catalog grants to account groups | Service principal |
| AWS | IAM roles + policies; SSO permission sets | IAM role (assumed) |
| Azure | Entra ID groups + Azure RBAC roles | Managed identity / service principal |
| Airflow | RBAC roles (Viewer, User, Op, Admin) | Connections per target system |
