# Embedding diagrams

## HTML pages (docs v1 and v3, tech summaries, reviews, review v2, architecture reviews, briefs, blog posts)
- Paste `r["html"]` (or `--fragment x.html`): a `<figure>` with the title, the SVG in a frame that scrolls sideways on phones (`overflow-x:auto`), then the key and the Notice as HTML text (searchable, readable by screen readers).
- The SVG carries its own `<style>` scoped to `#dg-<id>`; it reads the page's theme (`data-theme` on `:root`, else `prefers-color-scheme`). No page CSS is needed; the docs `style.css` variables match.
- Ids: every diagram on one page needs a different `id`; it prefixes the svg id (`dg-<id>`), the CSS scope and the arrow-marker ids, so two diagrams never share a marker.
- Link to a diagram with `#fig-<id>`.
- Several diagrams in one builder: call `build` per spec, check `errors` is empty for each, join the `html` fragments.
- Static only: no script, no external fonts or images, nothing fetched at view time.

## Markdown and Confluence
- Mermaid types: paste `r["mermaid"]` in a ```` ```mermaid ```` block. It starts with the frontmatter title, then `%% Key` and `%% Notice` comments; write the key and Notice as normal text under the block too.
- No Mermaid form (`NOTE <id> | no Mermaid form`): save the standalone SVG (`-o diagrams/<id>.svg`, title, key and Notice drawn in) next to the document and embed it as an image.
- The Mermaid text keeps groups, labels and colours (classDef); layout and the legend are Mermaid's own, so the SVG is the reference picture.

## Reviews
- One diagram per finding at most, only where it explains the issue (impact path, call chain, before/after).
- Impact views: dbt style with the affected path in full colour and the rest `dim: true`; Notice names what breaks.
- Before/after: two specs with the same ids for unchanged nodes and the same direction, so they compare side by side.

## Knowledge-graph answers
- Answers in the terminal: give the Mermaid text, or write the SVG to the graph folder and name its path relative to the repo root.

## Rules
- Paths in pages and reports are relative to the repo root.
- Never publish diagrams as artifacts or hosted pages; outputs are local files.
