# Adds the skill-usage hook to ~/.claude/settings.json, keeping existing settings.
import json, os

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
entry = {"matcher": "Skill|Read",
         "hooks": [{"type": "command", "command": 'python3 "$HOME/.claude/hooks/log-skill.py"'}]}
post = settings.setdefault("hooks", {}).setdefault("PostToolUse", [])
if entry in post:
    print("already installed")
else:
    post.append(entry)
    json.dump(settings, open(path, "w"), indent=2)
    print("added skill-usage hook to", path)
