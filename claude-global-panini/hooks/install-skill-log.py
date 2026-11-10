# Adds the skill-usage hook to ~/.claude/settings.json, keeping existing settings.
# Matcher Skill|Read: Python starts after every Read; log-skill.py drops non-skill paths.
import json, os, sys

path = os.path.expanduser("~/.claude/settings.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
text = open(path, encoding="utf-8-sig").read() if os.path.exists(path) else ""
settings = json.loads(text) if text.strip() else {}
python = sys.executable.replace("\\", "/")
entry = {"matcher": "Skill|Read",
         "hooks": [{"type": "command", "command": f'"{python}" "$HOME/.claude/hooks/log-skill.py"'}]}
hooks = settings.get("hooks") or {}
settings["hooks"] = hooks
post = hooks.get("PostToolUse") or []
hooks["PostToolUse"] = post
if "log-skill.py" in json.dumps(post):
    print("already installed")
else:
    post.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    print("added skill-usage hook to", path)
