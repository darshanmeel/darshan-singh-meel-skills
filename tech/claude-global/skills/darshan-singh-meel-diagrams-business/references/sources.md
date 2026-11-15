# Sources

Notation facts this family relies on. Base sources (Mermaid flowchart, dbt, Airflow) are in `darshan-singh-meel-diagrams/references/sources.md`.

| Fact | Page |
|---|---|
| Mermaid quadrantChart: `x-axis <left> --> <right>`, `y-axis <bottom> --> <top>`, `quadrant-1` top right, `quadrant-2` top left, `quadrant-3` bottom left, `quadrant-4` bottom right, points `Name: [x, y]` with x and y from 0 to 1 | https://mermaid.js.org/syntax/quadrantChart.html |
| Mermaid mindmap: `mindmap` keyword, hierarchy by indentation, `root((text))` circle shape, markdown strings ``id["`text`"]`` | https://mermaid.js.org/syntax/mindmap.html |
| Mermaid Ishikawa: `ishikawa-beta`, first line = problem, causes and sub-causes by indentation, Mermaid 11.12.3 or later | https://mermaid.js.org/syntax/ishikawa.html |
| Mermaid has no funnel, SWOT, SIPOC, value chain, business model canvas or decision-matrix diagram (diagram syntax list) | https://mermaid.js.org/intro/ |

Conventions without an official standards page; the layouts follow the common form and are marked for checking:
- Team Topologies team types (stream-aligned, platform, enabling, complicated-subsystem) and interaction modes (collaboration, X-as-a-Service, facilitating): check: https://teamtopologies.com/key-concepts
- Business model canvas, nine building blocks and their order: check: https://www.strategyzer.com/library/the-business-model-canvas
- Value chain (support over primary activities, margin): Porter, Competitive Advantage (1985); check: https://www.isc.hbs.edu/strategy/business-strategy/Pages/the-value-chain.aspx
- Value stream ladder (process time, wait time, % complete and accurate, flow efficiency): check: https://www.lean.org/lexicon-terms/value-stream-mapping/
- Fishbone / Ishikawa cause-and-effect and SIPOC: check: https://asq.org/quality-resources/fishbone and https://asq.org/quality-resources/sipoc
- Power / interest grid quadrant names (Manage closely, Keep satisfied, Keep informed, Monitor): Mendelow's matrix, common project-management usage; check: https://www.pmi.org/learning/library
- Colours are this skill's mapping onto the docs palette; none of these sources defines colours.
