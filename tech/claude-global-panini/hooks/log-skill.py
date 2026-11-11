# Claude Code hook: logs each skill used and each skill reference file read.
import datetime, json, os, sys

d = json.loads(sys.stdin.buffer.read().decode("utf-8"))
inp = d.get("tool_input") or {}
if d.get("tool_name") == "Skill":
    item = inp.get("skill", "?")
else:  # Read: only files inside a .claude/skills folder
    path = inp.get("file_path", "").replace("\\", "/")
    if "/.claude/skills/" not in path:
        sys.exit(0)
    item = "  read " + path.split("/.claude/skills/", 1)[1]
repo = os.path.basename((d.get("cwd") or "").rstrip("/\\")) or "?"
with open(os.path.expanduser("~/.claude/skill-usage.log"), "a", encoding="utf-8") as f:
    f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M}  {repo}  {item}\n")
