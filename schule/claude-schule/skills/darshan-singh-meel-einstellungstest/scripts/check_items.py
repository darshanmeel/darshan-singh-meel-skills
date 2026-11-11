"""Check Einstellungstest question and chapter JSON, their English sidecars and the printed sheets.

Usage: python check_items.py <file-or-folder> [more files or folders]
- Questions (list of items with "options"): schema, 4 distinct options, answer 0-3 (-1 only for modules without a key),
  ids unique across all files, one id prefix per file, topic = a chapter topic (when chapters are scanned),
  no duplicate question in a folder, answer-index balance.
- Every JSON (except profil.json "sources") and sheet: no e-mail, link or machine path.
- "check" field: a Python expression that computes the result; exactly the option at "answer" must equal it.
- Chapters (list of items with "concept"): keys, 4-6 tips, 2-4 traps.
- English sidecar en/<same name>.json: every id, every text field, same list lengths.
- Sheets (*.html in a given folder): data-frage ids exist, options A-D print exactly the JSON options in JSON order,
  key files carry the right data-loesung letter, task files carry none.
Errors fail the run (exit code 1). Lines with "?" are warnings.
"""
import ast
import html
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

Q_KEYS = ("id", "module", "topic", "difficulty", "question", "options", "answer", "explanation", "time_seconds")
C_KEYS = ("id", "module", "topic", "title", "concept", "example", "example_explained", "tips", "traps", "practice_topics")
Q_EN = ("question", "options", "explanation")
C_EN = ("title", "concept", "example", "example_explained", "tips", "traps")
NO_KEY = {"persoenlichkeit", "sjt"}  # no right or wrong: answer -1, the explanation carries the content
LINK = re.compile(r"[\w.+-]+@[\w-]+\.\w+|https?://|www\.\w|[A-Za-z]:\\\\?(?:Users|home)\b|/(?:Users|home)/\w")
NUM = re.compile(r"-?\d+(?:\.\d{3})*(?:,\d+)?(?:/\d+)?")
NODES = (ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop, ast.Call, ast.Name, ast.Load,
         ast.Store, ast.List, ast.Tuple, ast.Subscript, ast.Slice, ast.ListComp, ast.GeneratorExp, ast.comprehension,
         ast.Compare, ast.cmpop, ast.BoolOp, ast.boolop, ast.IfExp)


def nach(printed, rule):
    """Next term of a series: the printed terms must be the start of the series built from the rule."""
    rule = list(rule)
    if rule[:len(printed)] != list(printed):
        raise ValueError(f"printed terms {list(printed)} do not follow the rule {rule[:len(printed)]}")
    return rule[len(printed)]


ALLOWED = {"F": Fraction, "nach": nach, "round": round, "abs": abs, "min": min, "max": max, "sum": sum, "len": len,
           "range": range, "sorted": sorted, "int": int, "str": str, "chr": chr, "ord": ord}


def compute(expr):
    tree = ast.parse(expr, mode="eval")
    bound = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    for n in ast.walk(tree):
        if not isinstance(n, NODES):
            raise ValueError(f"{type(n).__name__} is not allowed in a check")
        if isinstance(n, ast.Name) and n.id not in ALLOWED and n.id not in bound:
            raise ValueError(f"name '{n.id}' is not allowed in a check")
    return eval(compile(tree, "check", "eval"), {"__builtins__": {}, **ALLOWED})


def number(text):
    """First number of an option in German notation: 1.250,5 -> 1250.5, 3/4 -> 3/4."""
    m = NUM.search(text.replace("−", "-").replace(" ", " "))
    if not m:
        return None
    top, _, bottom = m[0].replace(".", "").replace(",", ".").partition("/")
    return Fraction(top) / int(bottom) if bottom and int(bottom) else Fraction(top)


def same(value, option):
    if isinstance(value, str):
        return value.strip() == option.strip()
    n = number(option)
    return n is not None and abs(Fraction(value) - n) < Fraction(1, 10**9)


def norm(text):
    return " ".join(str(text).split())  # case kept: capitalisation items differ only in case


def links(text, err):
    if m := LINK.search(text):
        err(f"e-mail, link or machine path: \"{m[0][:30]}\"")


def sidecar(path):
    p = path.parent / "en" / path.name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def check_en(items, en, fields, err):
    if en is None:
        return err("no English sidecar en/<same name>.json")
    for it in items:
        e = en.get(it.get("id"))
        if not isinstance(e, dict):
            err(f"{it.get('id')}: missing in the English sidecar")
            continue
        for k in fields + (("material",) if "material" in it else ()):
            if not e.get(k) or type(e[k]) is not type(it.get(k)):
                err(f"{it['id']}: English '{k}' missing or of another type")
            elif isinstance(e[k], list) and (len(e[k]) != len(it[k]) or not all(isinstance(s, str) and s.strip() for s in e[k])):
                err(f"{it['id']}: English '{k}' needs {len(it[k])} non-empty entries")
    for extra in sorted(set(en) - {it.get("id") for it in items}):
        err(f"{extra}: in the English sidecar only")


def check_question(q, err, warn):
    qid = q.get("id", "?")
    missing = [k for k in Q_KEYS if k not in q]
    if missing:
        return err(f"{qid}: missing {', '.join(missing)}")
    opts, ans = q["options"], q["answer"]
    if not (isinstance(opts, list) and len(opts) == 4 and all(isinstance(o, str) and o.strip() for o in opts)):
        return err(f"{qid}: needs exactly 4 non-empty options")
    if len({norm(o) for o in opts}) < 4:
        err(f"{qid}: two options are the same")
    if q["difficulty"] not in (1, 2, 3):
        err(f"{qid}: difficulty must be 1, 2 or 3")
    if not isinstance(q["time_seconds"], int) or not 5 <= q["time_seconds"] <= 600:
        err(f"{qid}: time_seconds must be a whole number from 5 to 600")
    for k in ("module", "topic", "question", "explanation"):
        if not isinstance(q[k], str) or not q[k].strip():
            err(f"{qid}: '{k}' is empty")
    no_key = q["module"] in NO_KEY
    if ans not in ((-1,) if no_key else (0, 1, 2, 3)) or isinstance(ans, bool):
        return err(f"{qid}: answer must be {'-1 (module without a key)' if no_key else '0, 1, 2 or 3'}")
    if no_key:
        if "check" in q:
            err(f"{qid}: a question without a key cannot carry a check")
        return
    if "check" not in q:
        if q["module"] == "mathe" or "reihen" in q["topic"]:
            warn(f"{qid}: no 'check' field - result not recomputed")
        return
    try:
        value = compute(q["check"])
        hits = [i for i, o in enumerate(opts) if same(value, o)]
    except Exception as e:  # any failure of the expression is a finding, not a crash
        return err(f"{qid}: check '{q['check']}' failed: {e}")
    shown = value if isinstance(value, str) else float(value)
    if hits != [ans]:
        err(f"{qid}: check gives {shown}; matching options {['ABCD'[i] for i in hits] or 'none'}, key {'ABCD'[ans]}")
    return True


def check_chapter(c, err, warn):
    cid = c.get("id", "?")
    missing = [k for k in C_KEYS if k not in c]
    if missing:
        return err(f"{cid}: missing {', '.join(missing)}")
    for k, lo, hi in (("tips", 4, 6), ("traps", 2, 4), ("practice_topics", 1, 99)):
        if not isinstance(c[k], list) or not lo <= len(c[k]) <= hi or not all(isinstance(s, str) and s.strip() for s in c[k]):
            err(f"{cid}: '{k}' needs {lo}-{hi} non-empty entries" if hi < 99 else f"{cid}: '{k}' is empty")
    for k in C_KEYS[:7]:
        if not isinstance(c[k], str) or not c[k].strip():
            err(f"{cid}: '{k}' is empty")
    if isinstance(c["traps"], list) and not any(re.search(r"\bist\b.*\bnicht\b", str(t)) for t in c["traps"]):
        warn(f"{cid}: no trap in the form 'X ist Y, nicht Z.'")


def check_sheet(path, questions, err):
    text = path.read_text(encoding="utf-8")
    links(html.unescape(re.sub(r"<[^>]+>", " ", text)), err)
    tags = list(re.finditer(r'<[^>]*\bdata-frage="([^"]+)"[^>]*>', text))
    is_key = path.name.startswith(("loesung", "erwartungshorizont"))
    for i, m in enumerate(tags):
        q = questions.get(m[1])
        if not q:
            err(f"data-frage=\"{m[1]}\": no such question id")
            continue
        want = "ABCD"[q["answer"]] if q["answer"] in (0, 1, 2, 3) else "-"
        key = re.search(r'data-loesung="([^"]*)"', m[0])
        if is_key and (not key or key[1] != want):
            err(f"{m[1]}: data-loesung is {key[1] if key else 'missing'}, the JSON key is {want}")
        if not is_key and key:
            err(f"{m[1]}: a task file must not carry data-loesung")
        chunk = text[m.end():tags[i + 1].start() if i + 1 < len(tags) else len(text)]
        opts = re.findall(r'<li[^>]*data-option="([^"]+)"[^>]*>(.*?)</li>', chunk, re.S)
        if not opts:
            continue
        if [letter for letter, _ in opts] != list("ABCD"):
            err(f"{m[1]}: options must be A, B, C, D in this order")
            continue
        for (letter, body), option in zip(opts, q["options"]):
            body = re.sub(r'<(\w+)[^>]*\bclass="en"[^>]*>.*?</\1>', " ", body, flags=re.S)  # English line of a pair
            if norm(html.unescape(re.sub(r"<[^>]+>", " ", body))).removeprefix(f"({letter})").strip() != norm(option):
                err(f"{m[1]}: option ({letter}) does not print the JSON option \"{option}\"")
    return len(tags)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    roots = [Path(a) for a in sys.argv[1:]]
    if not roots:
        sys.exit(__doc__)
    files = [f for r in roots for f in (sorted(p for p in r.rglob("*.json") if "en" not in p.relative_to(r).parts[:-1])
                                        if r.is_dir() else [r])]
    if not files:
        sys.exit("no .json files given")
    loaded, report = [], {}
    for f in files:
        report[f] = ([], [], [])  # errors, warnings, notes
        try:
            loaded.append((f, json.loads(f.read_text(encoding="utf-8"))))
        except (ValueError, UnicodeDecodeError) as e:
            report[f][0].append(f"not valid UTF-8 JSON: {e}")
    kind = {f: "questions" if isinstance(d, list) and d and isinstance(d[0], dict) and "options" in d[0]
            else "chapters" if isinstance(d, list) and d and isinstance(d[0], dict) and "concept" in d[0] else "other"
            for f, d in loaded}
    topics = {}  # chapter topics per folder: a mock-test folder without chapters is not checked against others
    for f, d in loaded:
        if kind[f] == "chapters":
            topics.setdefault(f.parent, set()).update(c.get("topic") for c in d)
    ids, prefixes, stems, questions = {}, {}, {}, {}
    for f, data in loaded:
        errors, warnings, notes = report[f]
        err, warn = errors.append, warnings.append
        scan = {k: v for k, v in data.items() if k != "sources"} if isinstance(data, dict) else data  # profile names its pages
        links(json.dumps(scan, ensure_ascii=False), err)
        if kind[f] == "other":
            notes.append("no questions or chapters (scanned for links only)")
            continue
        items = [it for it in data if isinstance(it, dict)]
        for it in items:
            iid = str(it.get("id", ""))
            if iid in ids:
                err(f"{iid}: id also in {ids[iid].name}")
            ids[iid] = f
        own = {iid.rpartition("-")[0] for iid in (str(it.get("id", "")) for it in items)}
        if len(own) != 1 or "" in own:
            err(f"ids need one prefix per file, like 'ma-pro-001'; found {sorted(own)}")
        for p in own:
            if prefixes.setdefault(p, f) != f:
                err(f"id prefix '{p}' is also used in {prefixes[p].name}")
        if kind[f] == "chapters":
            for c in items:
                check_chapter(c, err, warn)
            check_en(items, sidecar(f), C_EN, err)
            notes.append(f"{len(items)} chapter(s)")
            continue
        recomputed, keys = 0, []
        for q in items:
            recomputed += check_question(q, err, warn) is True
            questions[q.get("id")] = q
            if f.parent in topics and q.get("topic") not in topics[f.parent]:
                err(f"{q.get('id')}: topic \"{q.get('topic')}\" is not a chapter topic")
            stem = (f.parent, norm(q.get("material", "")), norm(q.get("question", "")), tuple(sorted(map(norm, q.get("options") or []))))
            if stem in stems:
                err(f"{q.get('id')}: same question and options as {stems[stem]}")
            stems[stem] = q.get("id")
            if q.get("answer") in (0, 1, 2, 3):
                keys.append(q["answer"])
        check_en(items, sidecar(f), Q_EN, err)
        count = [keys.count(i) for i in range(4)]
        if len(keys) >= 8 and max(count) - min(count) > max(2, len(keys) // 8):
            err(f"answer index unbalanced: A/B/C/D = {'/'.join(map(str, count))}")
        if len(items) >= 6 and len({q.get("difficulty") for q in items}) == 1:
            warn("only one difficulty in the file")
        notes.append(f"{len(items)} question(s), key A/B/C/D = {'/'.join(map(str, count))}, {recomputed} recomputed")
    sheets = [s for r in roots if r.is_dir() for s in sorted(r.glob("*.html"))]
    for s in sheets:
        report[s] = ([], [], [])
        report[s][2].append(f"{check_sheet(s, questions, report[s][0].append)} question(s) on the sheet")
    bad = warned = 0
    for f, (errors, warnings, notes) in report.items():
        print(f"{'FAIL' if errors else 'OK  '} {f.as_posix()}  {'; '.join(notes)}")
        for e in errors:
            print(f"     - {e}")
        for w in warnings:
            print(f"     ? {w}")
        bad += len(errors)
        warned += len(warnings)
    print(f"{len(report)} file(s), {bad} error(s), {warned} warning(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
