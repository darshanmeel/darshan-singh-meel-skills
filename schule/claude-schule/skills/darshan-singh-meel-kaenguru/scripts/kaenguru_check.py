"""Check Kaenguru-style multiple-choice material, or score an answer string.

Usage:
  python kaenguru_check.py <folder>                      check test.html + erwartungshorizont.html or arbeitsblatt.html + loesung.html,
                                                         data-stufe and footer of every .html, then run <folder>/pruefung.py
                                                         and compare its problem numbers and letters with the key file
  python kaenguru_check.py score <key file> <answers>    answers: one sign per task, A-E, "-" = no answer, F = several marks
                                                         (points come from the key file, else from the task file next to it)
Run check_material.py of darshan-singh-meel-schule as well: it checks HTML, DE/EN pairs and point sums.
Errors fail the run (exit code 1); warnings are listed.
"""
import math
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

LETTERS = "ABCDE"
AFB = {3: "I", 4: "II", 5: "III"}
FULL = {"jg03-04": 24, "jg05-06": 24, "jg07-08": 30, "jg09-10": 30, "jg11-13": 30}
VOID = {"br", "img", "input", "meta", "hr", "col", "wbr"}
PAIRS = (("test.html", "erwartungshorizont.html"), ("arbeitsblatt.html", "loesung.html"))
FOOTER = "keine Wettbewerbsaufgaben"


class Page(HTMLParser):
    """Collects tasks (data-aufgabe + data-punkte or data-loesung), their options, body attributes, answer-sheet cells,
    data-max and data-gesamt values, and the page text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.body, self.tasks, self.cells = 0, {}, [], []
        self.maxes, self.sums, self.text = [], [], ""
        self.task = self.opt = self.max = None  # open task / option / data-max element, each with the depth it was opened at

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.body = a
        if "data-antwort" in a:
            self.cells.append(a["data-antwort"])
        if "data-max" in a:
            self.max = [a["data-max"], "", self.depth]
            self.maxes.append(self.max)
        if "data-gesamt" in a:
            self.sums.append(a["data-gesamt"])
        if "data-aufgabe" in a and ("data-punkte" in a or "data-loesung" in a):
            self.task = {"id": a["data-aufgabe"], "punkte": a.get("data-punkte"), "afb": a.get("data-afb"),
                         "loesung": a.get("data-loesung"), "options": [], "depth": self.depth}
            self.tasks.append(self.task)
        if self.task and "data-option" in a:
            self.opt = [a["data-option"], "", self.depth]
            self.task["options"].append(self.opt)
        if tag not in VOID:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        self.depth -= 1
        if self.max and self.depth == self.max[2]:
            self.max = None
        if self.opt and self.depth == self.opt[2]:
            self.opt = None
        if self.task and self.depth == self.task["depth"]:
            self.task = None

    def handle_data(self, data):
        self.text += data
        if self.max:
            self.max[1] += data
        if self.opt:
            self.opt[1] += data


def read(path):
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def points_of(tasks):
    return [int(t["punkte"]) if (t["punkte"] or "").isdigit() else 0 for t in tasks]


def check_totals(page, tasks, name):
    """Mock test: every data-gesamt = sum of problem points; every data-max = start points + that sum = the number printed in it."""
    total = sum(points_of(tasks))
    top = len(tasks) + total
    err = [f'{name}: data-gesamt="{v}" but the problems sum to {total}' for v in page.sums if v != str(total)]
    for v, text, _ in page.maxes:
        if v != str(top) or text.split()[:1] != [v]:
            err.append(f'{name}: data-max="{v}" with text "{" ".join(text.split())}", but start {len(tasks)} + points {total} = {top}')
    if not page.maxes:
        err.append(f'{name}: no data-max (every stated maximum score carries data-max="{top}")')
    return err


def check_tasks(page, mock):
    """Task file (test.html or arbeitsblatt.html): options, points, thirds, start points, time, maximum."""
    err, warn, tasks = [], [], page.tasks
    points = points_of(tasks)
    for t, pt in zip(tasks, points):
        letters = "".join(o[0] for o in t["options"])
        texts = [re.sub(r"\(?[A-E]\)", "", " ".join(o[1].split()), count=1).strip() for o in t["options"]]
        if letters != LETTERS:
            err.append(f"task {t['id']}: options must be A B C D E in this order, found '{letters}'")
        if any(not x for x in texts):
            err.append(f"task {t['id']}: empty option")
        if len(set(texts)) != len(texts):
            err.append(f"task {t['id']}: two options are identical")
        if pt not in AFB:
            err.append(f"task {t['id']}: data-punkte must be 3, 4 or 5")
        elif t["afb"] != AFB[pt]:
            err.append(f"task {t['id']}: {pt} points need data-afb=\"{AFB[pt]}\" (3 = I, 4 = II, 5 = III)")
    if points != sorted(points):
        err.append("tasks must run from 3-point to 5-point problems")
    if mock:
        n, stufe = len(tasks), page.body.get("data-stufe")
        if n % 3 or any(points.count(p) != n // 3 for p in AFB):
            err.append(f"mock test: {n} tasks must split into three equal thirds of 3, 4 and 5 points")
        if page.body.get("data-start") != str(n):
            err.append(f"mock test: body data-start must be {n} (start points = number of tasks)")
        if stufe in FULL:
            real = n * 75 / FULL[stufe]
            zeit = float(page.body.get("data-zeit") or 0)
            if n > FULL[stufe]:
                err.append(f"mock test: {n} tasks, the competition has {FULL[stufe]} at this level")
            if not real <= zeit <= 5 * math.ceil(real / 5):
                warn.append(f"mock test: data-zeit {zeit:g} min, competition pace gives {real:g} (round up to the next 5 at most)")
        if page.cells != [t["id"] for t in tasks]:
            err.append("mock test: answer sheet needs one data-antwort cell per task, same ids, same order")
        err += check_totals(page, tasks, "test.html")
    return err, warn


def check_key(page, tasks, mock):
    """Key file (erwartungshorizont.html or loesung.html) against the task file."""
    err, warn = [], []
    key = [t["loesung"] or "" for t in page.tasks]
    if [t["id"] for t in page.tasks] != [t["id"] for t in tasks]:
        err.append("key and task file list different tasks")
    for t, k in zip(page.tasks, key):
        if len(k) != 1 or k not in LETTERS:
            err.append(f"task {t['id']}: data-loesung must be one letter A-E")
    for t, k in zip(tasks, page.tasks):
        if k["punkte"] not in (None, t["punkte"]):
            err.append(f"task {t['id']}: data-punkte differs between task file and key file")
    if mock:
        err += check_totals(page, tasks, "erwartungshorizont.html")
    n = len(key)
    count = {c: key.count(c) for c in LETTERS}
    limit = max(2, 2 * n // 5)  # at most 40 %
    if n >= 10 and min(count.values()) == 0:
        warn.append(f"key balance: a letter is never correct {count}")
    if max(count.values(), default=0) > limit:
        warn.append(f"key balance: one letter is correct more than {limit} times {count}")
    if re.search(r"(.)\1\1", "".join(key)):
        warn.append(f"key balance: the same letter three times in a row ({''.join(key)})")
    return err, warn, "".join(key)


def check_files(root):
    """Every .html of the folder: one valid data-stufe on <body>, footer sentence present."""
    err, stufen = [], set()
    for f in sorted(root.glob("*.html")):
        page = read(f)
        stufen.add(str(page.body.get("data-stufe")))
        if page.body.get("data-stufe") not in FULL:
            err.append(f"{f.name}: body data-stufe must be one of {', '.join(FULL)}")
        if FOOTER not in " ".join(page.text.split()):
            err.append(f'{f.name}: footer sentence "... {FOOTER}" is missing')
    if len(stufen) > 1:
        err.append(f"files carry different data-stufe values: {sorted(stufen)}")
    return err


def check_proof(lines, keys):
    """Output of pruefung.py against the key file: same problem numbers, same letters."""
    proven = {m[1]: m[2] for m in (re.match(r"OK\s+Aufgabe\s+(\w+):.*=\s*\(([A-E])\)\s*$", x) for x in lines) if m}
    hand = sorted(m[1] for m in (re.match(r"HAND\s+Aufgabe\s+(\w+)", x) for x in lines) if m)
    err = [f"task {nr}: not covered by pruefung.py" for nr in keys if nr not in proven and nr not in hand]
    err += [f"task {nr}: in pruefung.py but not in the key file" for nr in list(proven) + hand if nr not in keys]
    err += [f"task {nr}: key file says ({keys[nr]}), pruefung.py proves ({x})" for nr, x in proven.items()
            if nr in keys and keys[nr] != x]
    return err, [f"task {nr}: HAND line, key ({keys.get(nr, '?')}) is not recomputed" for nr in hand]


def score(keyfile, answers):
    keyfile = Path(keyfile)
    tasks = read(keyfile).tasks
    if any(t["punkte"] is None for t in tasks):  # loesung.html carries no points: take them from the task file
        other = {k: t for t, k in PAIRS}.get(keyfile.name)
        if not other or not (keyfile.parent / other).exists():
            sys.exit(f"{keyfile.name} has no data-punkte and no task file next to it")
        punkte = {t["id"]: t["punkte"] for t in read(keyfile.parent / other).tasks}
        for t in tasks:
            t["punkte"] = punkte.get(t["id"])
    answers = answers.upper().replace(" ", "-")
    if len(answers) != len(tasks) or re.search(r"[^A-F-]", answers):
        sys.exit(f"need {len(tasks)} signs from A-E, F (several marks) or - (no answer)")
    start = len(tasks)  # holds when the thirds are equal: all answers wrong then gives exactly 0
    total, right, wrong, jump, best = float(start), 0, 0, 0, 0
    for t, a in zip(tasks, answers):
        pt = int(t["punkte"])
        if a == t["loesung"]:
            total, right, jump = total + pt, right + 1, jump + 1
            best = max(best, jump)
        else:
            jump = 0
            if a != "-":  # F (several marks) is scored as wrong here; not confirmed by the organiser's pages
                total, wrong = total - pt / 4, wrong + 1
    top = start + sum(int(t["punkte"]) for t in tasks)
    print(f"right {right}, wrong {wrong}, empty {len(tasks) - right - wrong}, "
          f"points {total:g} of {top} (start {start}), longest jump {best}")


def report(head, err, warn=()):
    print(f"{'FAIL' if err else 'OK  '} {head}")
    for line in err:
        print(f"     - {line}")
    for line in warn:
        print(f"     ? {line}")
    return len(err)


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "score":
        return score(args[1], args[2])
    if len(args) != 1:
        sys.exit(__doc__)
    root, bad, keys = Path(args[0]), 0, None
    for taskfile, keyfile in PAIRS:
        if not (root / taskfile).exists():
            continue
        page = read(root / taskfile)
        err, warn = check_tasks(page, taskfile == "test.html")
        note = f"{len(page.tasks)} tasks"
        if keys is not None:
            err.append("two problem sets in one folder: pruefung.py proves one set; use one folder per set")
        keys = {}
        if (root / keyfile).exists():
            keypage = read(root / keyfile)
            e, w, key = check_key(keypage, page.tasks, taskfile == "test.html")
            err, warn, note = err + e, warn + w, f"{note}, key {key}"
            keys = {t["id"]: t["loesung"] for t in keypage.tasks}
        else:
            err.append(f"{keyfile} is missing")
        bad += report(f"{taskfile} + {keyfile}  {note}", err, warn)
    if keys is None:
        sys.exit(f"no test.html or arbeitsblatt.html in {root}")
    bad += report(f"data-stufe and footer in {len(list(root.glob('*.html')))} .html files", check_files(root))
    if (root / "pruefung.py").exists():
        run = subprocess.run([sys.executable, "pruefung.py"], cwd=root, capture_output=True, text=True)
        lines = (run.stdout + run.stderr).splitlines()
        err, warn = check_proof(lines, keys)
        if run.returncode:
            err = [x for x in lines if not x.startswith("OK")] + err or ["pruefung.py exit code 1"]
        bad += report(f"pruefung.py  {sum(x.startswith('OK') for x in lines)} keys recomputed, "
                      f"compared with {len(keys)} letters of the key file", err, warn)
    else:
        print("FAIL pruefung.py is missing: no key is proven")
        bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
