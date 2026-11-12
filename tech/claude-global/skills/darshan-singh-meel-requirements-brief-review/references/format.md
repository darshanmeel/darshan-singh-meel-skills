# Review file format

File: `reviews/requirements-brief-<YYYY-MM-DD-HHMM>.md`. Paths relative to the project root. Omit empty sections except "Traceability", "Numbers" and "Claims".

```markdown
# Review: <brief title>
Date: <YYYY-MM-DD HH:MM> · Skill: darshan-singh-meel-requirements-brief-review · File: generated-docs/requirements-brief-<slug>.html
Inputs re-read: <n files> (<names>) · Data profiled again: <yes: n files | none supplied>
Stack given: <techs from the spec's stack and the inputs> · Skills named: <skills the spec lists, or none>
Verdict: <Ready | Ready after Must fixes | Rework>
Counts: Must <n> · Should <n> · Other <n> · Build: <n> ERROR, <n> WARN

## Must
- **[<area>] section <n> / "<subsection>"** - what: <one line, quoted words or ids> · why: <one line> · fix: <the corrected row, value or sentence>

## Should
- ...

## Other
- ...

## Traceability
| # | Input item (file, line or id) | Kind | In the brief | Holds |
|---|---|---|---|---|
| 1 | FLT-3 (fleet-requirements.md) | requirement | 3 Requirements, FLT-3 gap; 7 needs; W1 | yes |
| 2 | engine_hours (source B) | data point | 4 Sources, B | yes |
| 3 | "retention 24 months" (source B note) | constraint | 3 FLT-7 conflict | yes |
| 4 | ... | consumer | missing | no → Must 1 |

## Numbers
| Number in the brief (section) | Fresh profile | Result |
|---|---|---|
| vin overlap 17 of 20 (8) | 17 of 20 | confirmed |
| card_no empty 25% (8) | 25% | confirmed |

## Claims
| # | Claim (section, row) | Source read | Result |
|---|---|---|---|
| 1 | "Snowpipe loads on file arrival" (9, SFTP CSV) | docs.snowflake.com: Snowpipe | confirmed |
| 2 | "Fivetran has a connector for this FMS" (9, REST API) | fivetran.com/docs connectors | not supported by the page |

## Checked without findings
<areas that passed, one line>

## Not checked
<what could not be verified and why: page unreachable, data file not available, tool not installed>
```

## Rules for the tables
- **Traceability:** one row per item found in the inputs by the reviewer (requirements, sources, data points, consumers, constraints, named platforms), never copied from the spec. Kinds: requirement · source · data point · consumer · constraint · platform. "Holds" = the brief's wording and status match the input; `no` links the finding.
- **Numbers:** every number in Data findings and every derived number elsewhere ("3 of 20 VINs", "25%"). Results: `confirmed` · `differs` (→ Must, with both values) · `no profile` (→ Must when data files exist).
- **Claims:** one row per product fact in Technology options and Context. Results: `confirmed` · `wrong` (→ Must, what the page says) · `not supported by the page` (→ Must) · `against the skill's rule` (→ Must, name the skill and quote the rule) · `unsourced` (→ Should; Must for a limit or a price) · `not checked` (reason under "Not checked").
- Name the page by site and title; URLs only for official sites.
- Area tags: Traceability, Status, Numbers, Claims, Given, Diagrams, Fit, Clarity, Voice, Words, Dependencies, Privacy, Layout, Build.

## After fixes (only when the user asked for them)
Append:
```markdown
## Fixed <YYYY-MM-DD HH:MM>
- Must 1 - <what changed> · rebuilt: 0 ERROR, <n> WARN
- Should 2 - not changed: <reason>
Verdict after fixes: <...>
```
