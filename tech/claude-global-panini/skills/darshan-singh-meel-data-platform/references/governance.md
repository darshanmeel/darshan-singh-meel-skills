# Data governance

- **Ownership:** every dataset/model/table has an owning team and a contact, recorded in metadata (dbt `meta`, catalog tags).
- **Classification:** tag columns as public / internal / confidential / PII; masking or row filters follow the tag, not individual queries.
- **Access:** `rbac.md`; review grants periodically.
- **Lineage:** keep source → mart lineage visible (dbt docs, catalog lineage, or the knowledge graph).
- **Quality:** tests per `testing.md`; failures alert the owner.
- **Retention & deletion:** retention per dataset class; lifecycle rules in storage; documented delete process for personal data.
- **Audit:** access and change history available (warehouse query/access history, cloud audit logs).
- **Environments:** prod data copied to lower environments only masked or sampled.
