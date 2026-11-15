# dbt review — <scope> — <YYYY-MM-DD HH:MM>

**Verdict:** <Ready | Ready after Must fixes | Not ready> — <one line why>

**Scope:** <files / folder / answer reviewed> · Platform: <Snowflake | Databricks> · dbt <version from requirements>
**Scripts:** `dbt_inventory.py health` → <key counts> · `check_queries.py analysis/<topic>` → <N ERROR>

## Must
1. **<what>** — `<path>:<line>`
   - Why: <the wrong number, row loss, missing view, write, secret>
   - Fix: <exact change>

## Should
1. **<what>** — `<path>:<line>`
   - Why: …
   - Fix: …

## Other
- <what> · <why> · <fix>

## Re-derived answers
| Question | Reviewed answer | Re-derived | Match? |
|---|---|---|---|
| <question> | <their result or claim> | <own result from references / docs> | Yes / No → Must 1 |

## Not checked
- <check that needs data or a connection> — read-only query for the owner to run: `<file or block>`

## Fixed (only after a fix request)
- Must 1 — <what changed> — rerun: <script output>
