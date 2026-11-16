# Sources

Official pages behind the notation facts of this family. Engine, palette and graph-style facts are in the base skill's `sources.md`.

| Fact | Page |
|---|---|
| Mermaid sequence syntax: `participant` / `actor`, `as` alias, `->>` `-->>` `-)` `--)` arrows, `+` / `-` activation, `Note right of / left of / over`, `alt` / `else`, `opt`, `loop`, `par` / `and`, `critical` / `option`, `break`, `autonumber`, `#59;` for a semicolon, "end" breaks parsing | https://mermaid.js.org/syntax/sequenceDiagram.html |
| Mermaid gantt syntax: `dateFormat`, `axisFormat`, `section`, task line `title :tags, id, start, length`, tags `done` `active` `crit` `milestone`, `after a b`, `s` durations, `vert` markers on dates and times (`vert, v1, 17:30, 2m`), own today marker | https://mermaid.js.org/syntax/gantt.html |
| Mermaid timeline syntax: `timeline`, `section`, `period : event : event`, `:` separates fields | https://mermaid.js.org/syntax/timeline.html |
| Mermaid user journey syntax: `journey`, `section`, `Task: score: actors`, score 1-5 | https://mermaid.js.org/syntax/userJourney.html |
| UML 2.5.1 is the current UML version (Dec 2017) | https://www.omg.org/spec/UML/ |
| dbt Model timing: Gantt-style timeline of the resources in a run, grouped by thread, longest model, estimated critical path | https://docs.getdbt.com/docs/deploy/run-visibility |
| Airflow Dag Run view: task instances with a Gantt-style timeline of each task's duration; Dag Run details show "Queued At" | https://airflow.apache.org/docs/apache-airflow/stable/ui.html |
| Airflow task-instance states (used by the airflow style) | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html |

## Not verified on an official page
- UML sequence notation (filled head = synchronous, open head = asynchronous, dashed = reply, execution specification bar, combined-fragment tab and operators) follows UML 2.5.1 chapter 17 "Interactions". check: https://www.omg.org/spec/UML/2.5.1/PDF
- Escaping `:` in Mermaid gantt / timeline / journey text: the pages document no escape, so the builder writes a ratio sign (U+2236) instead. check: https://mermaid.js.org/syntax/timeline.html
- RACI (one Accountable per task) and the service blueprint lanes and lines are practice conventions without an official standard page; the rules in `SKILL.md` are this skill's.
- Drawing queued time before the run bar is this skill's choice; the Airflow UI page names "Queued At" but does not describe it on the timeline.
