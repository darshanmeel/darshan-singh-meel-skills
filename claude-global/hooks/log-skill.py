# Claude Code hook: logs each skill used and each skill reference file read.
import datetime, json, os, sys

d = json.load(sys.stdin)
inp = d.get("tool_input") or {}
if d.get("tool_name") == "Skill":
    item = inp.get("skill", "?")
else:  # Read: only files inside a skills folder
    path = inp.get("file_path", "")
    if "/skills/" not in path.replace("\\", "/"):
        sys.exit(0)
    item = "  read " + path.replace("\\", "/").split("/skills/", 1)[1]
repo = os.path.basename(d.get("cwd") or "") or "?"
with open(os.path.expanduser("~/.claude/skill-usage.log"), "a") as f:
    f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M}  {repo}  {item}\n")
