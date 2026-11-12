"""Find installed skills that cover a confirmed tech stack, by their SKILL.md frontmatter (name and description only).

Usage: python skills.py <tech>...            e.g. python skills.py Snowflake Airflow dbt Streamlit
  scans ~/.claude/skills and ./.claude/skills; prints one line per matching skill, best first (name · matched techs · where),
  then `offer:` the top 3 to put in the question, and the techs no skill covers (official docs for those).
  Process skills (review, docs, graph, prototype, architecture, ask-me, notebook, requirements-brief, tech-blog) are left out:
  they do not carry tech rules. Nothing is loaded or executed.
"""
import re
import sys
from pathlib import Path

ROOTS = [Path.home() / ".claude" / "skills", Path(".claude") / "skills"]
ALIAS = {"adf": "azure data factory", "aws s3": "s3", "azure blob": "azure", "gcs": "google cloud storage", "pyspark": "spark",
         "azure data factory": "adf", "spark": "pyspark"}
PROCESS = re.compile(r"(^|-)(review|docs|knowledge-graph|graph|prototype|architecture|ask-me|notebook|requirements-brief|tech-blog)(-|$)")
OFFER = 3  # AskUserQuestion shows up to 4 options: the top 3 plus Other


def frontmatter(p):
    """(name, description) from the frontmatter only; a folded `description: >` block is joined."""
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None, ""
    head = text.split("\n---", 1)[0]
    name = re.search(r"^name:\s*(\S+)", head, re.M)
    desc = re.search(r"^description:[ \t]*(.*)((?:\n[ \t]+.*)*)", head, re.M)
    body = (desc[1] + " " + desc[2]).strip() if desc else ""
    return (name[1] if name else p.parent.name), re.sub(r"^[>|][-+]?\s*", "", re.sub(r"\s+", " ", body))


def matches(techs):
    out, seen = [], set()
    for root in ROOTS:
        for p in sorted(root.glob("*/SKILL.md")) if root.is_dir() else []:
            name, desc = frontmatter(p)
            if not name or name in seen or PROCESS.search(name):
                continue
            seen.add(name)
            hay = f"{name} {desc}".lower()
            word = lambda t: re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", hay)
            hit = [t for t in techs if word(t.lower()) or (t.lower() in ALIAS and word(ALIAS[t.lower()]))]
            if hit:
                out.append((name, hit, root.as_posix().replace(Path.home().as_posix(), "~")))
    return sorted(out, key=lambda x: (-len(x[1]), x[0]))


def main(techs):
    sys.stdout.reconfigure(encoding="utf-8")
    if not techs:
        sys.exit(__doc__)
    found = matches(techs)
    for name, hit, where in found:
        print(f"{name} · {', '.join(hit)} · {where}")
    print("offer: " + (", ".join(n for n, _, _ in found[:OFFER]) if found else "none"))
    covered = {t for _, hit, _ in found for t in hit}
    rest = [t for t in techs if t not in covered]
    print("no skill: " + (", ".join(rest) if rest else "none") + " → official docs")


if __name__ == "__main__":
    main(sys.argv[1:])
