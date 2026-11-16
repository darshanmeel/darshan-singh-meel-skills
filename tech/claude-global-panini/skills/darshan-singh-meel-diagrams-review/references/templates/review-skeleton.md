# Diagrams review - <scope> - <YYYY-MM-DD HH:MM>

**Verdict:** <Ready | Ready after Must fixes | Not ready> - <one line why>

**Scope:** <pages, specs or folder reviewed> · Source: <repo code | document | layout and notation only> · Mermaid: <checked | HTML only>
**Script:** `review_diagrams.py` → <n> MUST, <m> SHOULD · <k> specs rebuilt, <j> LAYOUT lines · PNGs looked at: <count> light + <count> dark

## Must
1. **<what>** - `<spec or page>#<diagram id>` (<element>)
   - Why: <what the reader would wrongly believe, or what fails>
   - Fix: <exact spec change>

## Should
1. **<what>** - `<spec or page>#<diagram id>`
   - Why: …
   - Fix: …

## Other
- <what> · <why> · <fix>

## Re-derived from the source
| Diagram | Expected (from source) | Drawn | Match? |
|---|---|---|---|
| `<id>` | <boxes / edges with path:line> | <what the diagram shows> | Yes / No → Must 1 |

## Not checked
- <check that needs something unavailable> - <what the owner can confirm>

## Fixed (only after a fix request)
- Must 1 - <what changed> - rerun: <script output>
