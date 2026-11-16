# Review report opening

The verdict and the deciding finding move to the first line; the introduction and repeated summary go.

## Before
```markdown
# Code review

## Introduction
In this report we review the changes made to the order loading pipeline. It is important to note that the
review covered all files in the diff. We looked at correctness, security, performance and design. Overall
the code is in reasonable shape, but there are some issues. The most serious one is that the incremental
filter in models/orders.sql compares against the wrong column, which means late-arriving rows are dropped.
There are also a few naming issues.

## Summary
Some issues were found, the most serious being the incremental filter.
```

## After
```markdown
# Review: order pipeline - do not merge yet

**Late-arriving orders are silently dropped**: the incremental filter in `models/orders.sql:14` compares
`created_at` instead of `updated_at`.

Any order changed after its first load never reaches the mart, so revenue reports undercount refunds.

## Must
- `models/orders.sql:14` - filter on `updated_at`; add a test with a row updated after load.

## Should
- `models/stg_orders.sql:3` - rename `dt` to `order_date`; three models guess its meaning.
```

## What changed
- Title states the verdict; the lede states the deciding finding with `path:line`.
- Why it matters names the business effect in one line.
- "Introduction", "It is important to note" and the repeated summary are gone; no fact was lost.
