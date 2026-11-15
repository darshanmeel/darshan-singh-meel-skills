# Sources

Official pages behind the notation rules of this family. The base skill's `sources.md` covers Mermaid flowchart syntax, dbt and Airflow.

| Fact | Page |
|---|---|
| C4 notation: title with diagram type and scope, key / legend on every diagram, type of every element stated, short description per element, technology on every container and component, one-way lines with specific labels, technology on inter-container lines, no prescribed colours or shapes | https://c4model.com/diagrams/notation |
| System context: scope one software system; people and external systems as supporting elements; for technical and non-technical readers; recommended | https://c4model.com/diagrams/system-context |
| Container: scope one software system; containers = applications and data stores; for technical readers; recommended | https://c4model.com/diagrams/container |
| Component: scope one container; supporting containers, people and systems; for architects and developers; only when it adds value | https://c4model.com/diagrams/component |
| Deployment: one environment; deployment nodes nest; infrastructure nodes (DNS, load balancers, firewalls); container and software system instances | https://c4model.com/diagrams/deployment |
| Mermaid C4: `C4Context`, `C4Container`, `C4Component`, `C4Deployment`; `Person`, `System`, `Container(alias, label, techn, descr)`, `ContainerDb`, `ContainerQueue`, `Component`, `_Ext` variants; `Enterprise_Boundary`, `System_Boundary`, `Container_Boundary`; `Rel(from, to, label, techn)`; `title` line; Mermaid lays it out itself | https://mermaid.js.org/syntax/c4.html |
| Mermaid architecture diagrams (`architecture-beta`, groups with `in`, built-in icons cloud, database, disk, internet, server) are beta; this family uses flowcharts with nested subgraphs for the nested types instead | https://mermaid.js.org/syntax/architecture.html |
| Nested subgraphs in a Mermaid flowchart | https://mermaid.js.org/syntax/flowchart.html |

- Colours and shapes per kind are this family's own mapping; C4 leaves them free and asks for a key, which every diagram has.
- Network, trust-zone and layer conventions (public / private subnet, DMZ, restricted zone, strict / relaxed layering) are common practice with no single official notation page; the key of each diagram states what its frames and colours mean.
