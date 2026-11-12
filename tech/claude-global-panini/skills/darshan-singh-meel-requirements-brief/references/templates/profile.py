"""Structure-only profile of data files: columns, inferred types, non-null counts, null %, distinct counts, min/max for
numeric and date columns that do not look sensitive, and key overlap between files. Never prints or writes a value.

Usage: python profile.py <file>... --out <profile.json> [--key <column> ...]
  csv/tsv with the standard library; xlsx (every sheet) when openpyxl is installed. Secret-looking files are skipped.
  Keys for the overlap table: --key columns, else columns present in 2+ files that end in id, key, no, number or code,
  or are unique in one of the files.
"""
import csv
import json
import re
import sys
from itertools import combinations
from pathlib import Path

SENSITIVE = {"name", "first", "last", "surname", "email", "mail", "phone", "mobile", "tel", "telephone", "address", "street", "city", "zip", "postal",
             "postcode", "plate", "registration", "licence", "license", "iban", "bic", "account", "card", "ssn", "tax", "salary", "income", "wage",
             "birth", "birthday", "dob", "age", "gender", "sex", "health", "diagnosis", "medical", "passport", "national", "token", "password",
             "secret", "ip", "user", "customer", "driver", "patient", "employee", "person", "contact", "lat", "lon", "latitude", "longitude"}
SENSITIVE_RX = re.compile(r"^(first|last|sur|full|user|nick|display|middle)?name$|^e?mail$|^(tele|mobile|cell|home|work)?phone$|^(zip|postal)code$|"
                          r"^(birth|licen[cs]e|diagnos)\w*$")
KEY_TOKENS = {"id", "key", "no", "number", "uuid", "guid", "nr"}  # as the last token of a column name: an identifier, values withheld
KEYISH = re.compile(r"(^|_)id$|key$|no$|number$|code$", re.I)
DMY = re.compile(r"^(\d{2})[./](\d{2})[./](\d{4})$")
SECRET = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.(pem|key|p12|pfx|jks|keystore|tfvars)|[^/]*\.tfstate[^/]*|id_(rsa|dsa|ecdsa|ed25519)[^/]*|"
                    r"credentials[^/]*|secrets?[^/]*|\.npmrc|\.pypirc|\.netrc|\.git-credentials|kubeconfig[^/]*|profiles\.yml)$|(^|/)[^/]*secret[^/]*/", re.I)
INT, FLOAT = re.compile(r"^[+-]?\d+$"), re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$|^\d{2}[./]\d{2}[./]\d{4}$")
BOOL = {"true", "false", "yes", "no", "0", "1", "y", "n"}
NULL = {"", "null", "none", "nan", "n/a", "na", "-"}


def tables(path):
    """(name, header, rows) per table in the file: one for csv/tsv, one per sheet for xlsx."""
    if path.suffix.lower() in (".csv", ".tsv", ".txt"):
        with path.open(encoding="utf-8-sig", newline="") as f:
            sample = f.read(20000)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            except csv.Error:
                dialect = csv.excel
            rows = list(csv.reader(f, dialect))
        if rows:
            yield path.as_posix(), [str(c).strip() for c in rows[0]], rows[1:]
    elif path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            print(f"skip {path.as_posix()}: openpyxl not installed (pip install openpyxl, or export the sheet as CSV)")
            return
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            rows = [["" if v is None else str(v) for v in r] for r in ws.iter_rows(values_only=True)]
            if rows:
                yield f"{path.as_posix()}#{ws.title}", [c.strip() for c in rows[0]], rows[1:]
    else:
        print(f"skip {path.as_posix()}: not a csv, tsv or xlsx file")


def kind(vals):
    if all(INT.match(v) for v in vals):
        return "int"
    if all(FLOAT.match(v) for v in vals):
        return "float"
    if all(DATE.match(v) for v in vals):
        return "date"
    if all(v.lower() in BOOL for v in vals):
        return "bool"
    return "text"


def tokens(name):
    """Words of a column name: snake_case, kebab-case, spaces and camelCase split; 'capacity' is not 'city'."""
    return [t for t in re.split(r"[^a-z0-9]+", re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()) if t]


def sensitive(name):
    tk = tokens(name)
    return any(t in SENSITIVE or SENSITIVE_RX.match(t) for t in tk) or (bool(tk) and tk[-1] in KEY_TOKENS)


def iso(vals):
    """Dotted or slashed dates as yyyy-mm-dd so they compare as dates: dd.mm by default, mm/dd when a 'month' over 12
    says so; both orders impossible → None (the column gets no min/max)."""
    parts = [DMY.match(v) for v in vals]
    first, second = (max(int(m[1]) for m in parts if m), max(int(m[2]) for m in parts if m)) if any(parts) else (0, 0)
    if first > 12 and second > 12:
        return None
    out = []
    for v, m in zip(vals, parts):
        if not m:
            out.append(v)
        elif second > 12:  # the second part is the day: month/day/year
            out.append(f"{m[3]}-{m[1]}-{m[2]}")
        else:
            out.append(f"{m[3]}-{m[2]}-{m[1]}")
    return out


def column(name, vals, n):
    present = [v.strip() for v in vals if v is not None and v.strip().lower() not in NULL]
    t = kind(present) if present else "empty"
    c = {"name": name, "type": t, "count": len(present), "null_pct": 100.0 * (n - len(present)) / n if n else 0.0,
         "distinct": len(set(present)), "sensitive": sensitive(name)}
    if present and t in ("int", "float", "date") and not c["sensitive"]:
        num = [float(v) for v in present] if t in ("int", "float") else iso(present)
        if num is not None:
            lo, hi = min(num), max(num)
            c["min"], c["max"] = (int(lo), int(hi)) if t == "int" else (lo, hi)
    return c


def relative(p):
    """The path as written when relative, else relative to the current folder, else the file name: no machine paths in the profile."""
    if not p.is_absolute():
        return p
    try:
        return p.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return Path(p.name)


def profile(paths, keys):
    files, cols = [], {}
    for p in paths:
        if SECRET.search(p.as_posix()):
            print(f"skip {p.as_posix()}: secret file (name)")
            continue
        for name, header, rows in tables(p):
            name = name.replace(p.as_posix(), relative(p).as_posix(), 1)
            n = len(rows)
            by = {h: [r[i] if i < len(r) else "" for r in rows] for i, h in enumerate(header) if h}
            files.append({"file": name, "rows": n, "columns": [column(h, v, n) for h, v in by.items()]})
            for h, v in by.items():
                cols.setdefault(h.lower(), []).append((name, {x.strip().lower() for x in v if x.strip().lower() not in NULL}))
    # overlap keys: --key, else a column in 2+ files that looks like a key by name or is unique in one of them
    unique = {c["name"].lower() for f in files for c in f["columns"] if c["count"] and c["distinct"] == c["count"]}
    wanted = {k.lower() for k in keys} or {k for k, v in cols.items() if len(v) > 1 and (KEYISH.search(k) or k in unique)}
    overlaps = []
    for k in sorted(wanted):
        for (fa, a), (fb, b) in combinations(cols.get(k, []), 2):
            both = len(a & b)
            overlaps.append({"key": k, "a": fa, "b": fb, "a_distinct": len(a), "b_distinct": len(b), "both": both,
                             "pct_a_in_b": 100.0 * both / len(a) if a else 0.0})
    return {"files": files, "overlaps": overlaps}


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    out, keys, paths = None, [], []
    it = iter(argv)
    for a in it:
        if a == "--out":
            out = next(it, None)
        elif a == "--key":
            keys.append(next(it, ""))
        else:
            paths.append(Path(a))
    if not out or not paths:
        sys.exit(__doc__)
    p = profile(paths, keys)
    Path(out).write_text(json.dumps(p, indent=1), encoding="utf-8")
    for f in p["files"]:
        sens = sum(c["sensitive"] for c in f["columns"])
        print(f"{f['file']}: {f['rows']} rows, {len(f['columns'])} columns ({sens} sensitive-looking, values withheld)")
    for o in p["overlaps"]:
        print(f"overlap {o['key']}: {o['both']} of {o['a_distinct']} in {o['a']} also in {o['b']} ({o['pct_a_in_b']:.0f}%)")
    print(f"wrote {Path(out).as_posix()}")


if __name__ == "__main__":
    main(sys.argv[1:])
