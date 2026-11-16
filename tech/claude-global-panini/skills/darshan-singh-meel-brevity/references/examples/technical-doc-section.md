# Technical doc section

The mechanism moves to the first line and the numbers into a table; every value stays.

## Before
```markdown
## Retry handling

This section describes how retries work in the ingestion service. Historically the service had no retries,
and failures were handled manually by the on-call engineer, which was time-consuming. In order to improve
this, a retry mechanism was introduced. Basically, when a call to the vendor API fails with a 429 or a 5xx
status, the client waits and tries again. The wait doubles each time, starting at two seconds, and there
are at most five attempts. After the last attempt the message is moved to the dead-letter queue, where it
stays for fourteen days. A 4xx other than 429 is not retried because it will not succeed on retry.
```

## After
```markdown
## Retry handling

**Rate limits and server errors retry with backoff; everything else fails fast to the dead-letter queue.**

| Response | Action |
|---|---|
| 429, 5xx | retry, wait 2 s and double each time, at most 5 attempts |
| other 4xx | no retry - the request itself is wrong |
| still failing after the last attempt | move to the dead-letter queue (kept 14 days) |

- Code: `ingest/client.py:41` (`send_with_retry`).
- Replay from the dead-letter queue: runbook `generated-docs/runbook-ingest.md`, section "Replay".
```

## What changed
- The lede gives the mechanism in one sentence; the history paragraph is cut (no reader needs it to operate the service).
- Every number stays - brevity never removes Technical-doc depth; the table shows it faster than prose.
- "This section describes", "In order to", "Basically" are gone.
