# Appends one self-check entry per finished skill task to ~/.claude/skill-work/<skill>.jsonl.
# Write-only: a separate process reads these later to improve the skills.
import argparse, datetime, json, os, re, subprocess

SECRET = re.compile(r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*\S+|AKIA[0-9A-Z]{16}|dapi[0-9a-f]{32}|eyJ\w+\.\w+\.|[\w.+-]+@[\w-]+\.[\w.]+")

p = argparse.ArgumentParser()
p.add_argument("--skill", required=True)
p.add_argument("--task", required=True, help="one line: what was done")
p.add_argument("--confidence", required=True, choices=["high", "medium", "low"])
p.add_argument("--why", required=True, help="one line: reason for the confidence")
p.add_argument("--risk", required=True, help="the main risk that could undermine the work")
p.add_argument("--good", action="append", default=[], help="1-2 things that went well")
p.add_argument("--fixes", default="", help="earlier mistake this corrects, and the better way")
p.add_argument("--files", nargs="*", default=[], help="files touched, relative to the repo root")
a = p.parse_args()

text = " ".join([a.task, a.why, a.risk, a.fixes, *a.good, *a.files])
if SECRET.search(text):
    raise SystemExit("not logged: looks like a secret or e-mail; reword without it")
home = os.path.expanduser("~").replace("\\", "/")
clean = lambda s: s.replace("\\", "/").replace(home, "~")

cwd = os.getcwd()
try:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=cwd).stdout.strip()
except OSError:
    commit = ""
entry = {
    "time": f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
    "repo": os.path.basename(cwd.rstrip("/\\")),
    "commit": commit,
    "skill": a.skill,
    "task": clean(a.task),
    "confidence": a.confidence,
    "why": clean(a.why),
    "risk": clean(a.risk),
    "good": [clean(g) for g in a.good[:2]],
    "fixes": clean(a.fixes),
    "files": [clean(f) for f in a.files],
}
folder = os.path.expanduser("~/.claude/skill-work")
os.makedirs(folder, exist_ok=True)
with open(os.path.join(folder, re.sub(r"[^\w.-]", "_", a.skill) + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("logged", a.skill)
