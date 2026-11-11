"""Pre-commit checks for this repo. Usage: python tools/check_repo.py
Fails (exit 1) on: absolute/machine paths or private names in tracked text, a full/panini twin that differs
in a script, template, example or test (.md text may differ), a skill without frontmatter name/description, __pycache__ left behind.
Warns on: description > 1024 chars (Agent Skills API limit; Claude Code shows up to 1536).
Private names: one per line in .private-names (git-ignored, never committed)."""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TWINS = [("tech/claude-global", "tech/claude-global-panini"), ("schule/claude-schule", "schule/claude-schule-panini")]
ABS = re.compile(r"(?<![\w\\])[A-Za-z]:[\\/](?:Users|home)|(?<![\w.~])/Users/[a-z]|/home/[a-z]")
# files that hold path-detecting regexes or deliberate test fixtures
ABS_OK = re.compile(r"(build|check_material|blog_post|check_repo)\.py$|tests/run\.py$")


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    return [ROOT / p for p in out.splitlines()]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    err, warn = [], []
    names_file = ROOT / ".private-names"
    names = [n.strip() for n in names_file.read_text(encoding="utf-8").splitlines() if n.strip()] if names_file.is_file() else []
    if not names:
        warn.append("no .private-names file: private-name scan skipped (add one name per line)")
    priv = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b", re.I) if names else None
    for f in tracked():
        if not f.is_file() or f.suffix in (".png", ".jpg", ".zip", ".pdf"):
            continue
        rel = f.relative_to(ROOT).as_posix()
        text = f.read_text(encoding="utf-8", errors="ignore")
        if not ABS_OK.search(rel) and (m := ABS.search(text)):
            err.append(f"{rel}: machine path '{m[0]}'")
        if priv and (m := priv.search(text)):
            err.append(f"{rel}: private name '{m[0]}'")
    for full, pan in TWINS:
        a, b = ROOT / full / "skills", ROOT / pan / "skills"
        sa = {p.name for p in a.iterdir() if p.is_dir()}
        sb = {p.name for p in b.iterdir() if p.is_dir()}
        for s in sorted(sa ^ sb):
            err.append(f"{full} vs {pan}: skill {s} only in one version")
        for s in sorted(sa & sb):
            fa = {p.relative_to(a / s).as_posix() for p in (a / s).rglob("*") if p.is_file()}
            fb = {p.relative_to(b / s).as_posix() for p in (b / s).rglob("*") if p.is_file()}
            for p in sorted(fa ^ fb):
                err.append(f"{s}: {p} only in one version")
            for p in sorted(fa & fb):
                if not p.endswith(".md") and (a / s / p).read_bytes().replace(b"\r\n", b"\n") != (b / s / p).read_bytes().replace(b"\r\n", b"\n"):
                    err.append(f"{s}: {p} differs between versions (only .md text may)")
    for skill in ROOT.glob("*/*/skills/*/SKILL.md"):
        t = skill.read_text(encoding="utf-8")
        name = re.search(r"^name:\s*(\S+)", t, re.M)
        desc = re.search(r"^description:\s*(.+)$", t, re.M)
        where = skill.relative_to(ROOT).as_posix()
        if not t.startswith("---") or not name or not desc:
            err.append(f"{where}: frontmatter needs name and description")
        elif name[1] != skill.parent.name:
            err.append(f"{where}: name '{name[1]}' is not the folder name")
        elif len(desc[1]) > 1536:
            err.append(f"{where}: description {len(desc[1])} chars > 1536 (Claude Code cuts it)")
        elif len(desc[1]) > 1024:
            warn.append(f"{where}: description {len(desc[1])} chars > 1024 (API limit)")
    for p in ROOT.rglob("__pycache__"):
        err.append(f"{p.relative_to(ROOT).as_posix()}: remove __pycache__")
    for w in warn:
        print("WARN", w)
    for e in err:
        print("ERROR", e)
    print(f"{len(err)} ERROR, {len(warn)} WARN")
    sys.exit(1 if err else 0)


main()
