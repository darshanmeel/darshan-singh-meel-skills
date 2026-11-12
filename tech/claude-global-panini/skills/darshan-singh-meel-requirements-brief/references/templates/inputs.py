"""Inventory the requirement inputs: kind, size, requirement ids (EPIC-12, US-3, REQ-007 ...), and plain text to read.
Never opens secret-looking files; data files (csv, xlsx, JSON or YAML arrays of records) give their structure only, never rows.

Usage: python inputs.py <file|folder>... [--text <out dir>]
  prints one line per file and, last, a JSON `inputs` list to paste into the spec (name, kind, ids).
  --text writes <out dir>/<relative path>.txt with the plain text of .md/.txt/.docx/.pdf (pypdf if installed), small
  config-like JSON/YAML, and Jira-style CSV exports (key, summary, description, issue type, epic or parent per row: never
  assignee, reporter or other people columns); other csv/xlsx and record-shaped JSON/YAML: columns or keys only.
  <out dir> is skipped when it lies inside a scanned folder, so reruns do not re-read their own extracts.
  Ids: EPIC 12, EPIC_12 and EPIC-12 are one id (EPIC-12); standards, codecs, quarters and the like (ISO-8601, UTF-8,
  SHA-256, Q1-2025, COVID-19, S3-1, GDPR-17) are not ids.
  <out dir> and an existing `inputs/` sibling, when under the current folder, are added to .gitignore: raw requirements stay out of git.
"""
import csv
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ID = re.compile(r"\b(?:[A-Z][A-Z0-9]{1,9}-\d{1,6}|(?:EPIC|US|REQ|BR|FR|NFR|STORY)[ _]?\d{1,6})\b")
NOT_ID = re.compile(r"^(ISO|IEC|IEEE|DIN|EN|RFC|UTF|SHA|MD|CRC|AES|RSA|TLS|SSL|HTTPS?|PCI|HL|SOC|CVE|GPT|MP|MPEG|IPV|OAUTH|UTC|GMT|CET|"
                    r"Q|FY|CW|KW|COVID|SARS|S3|EC2|PI|GDPR|DSGVO|CCPA|HIPAA|SOX|BASEL)-?\d", re.I)
SECRET = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.(pem|key|p12|pfx|jks|keystore|tfvars)|[^/]*\.tfstate[^/]*|id_(rsa|dsa|ecdsa|ed25519)[^/]*|"
                    r"credentials[^/]*|secrets?[^/]*|\.npmrc|\.pypirc|\.netrc|\.git-credentials|kubeconfig[^/]*|profiles\.yml)$|(^|/)[^/]*secret[^/]*/", re.I)
TEXT = {".md", ".txt", ".rst"}
STRUCTURED = {".json", ".yaml", ".yml"}
RECORDS = 5  # a JSON/YAML list with more records than this is data: keys only
JIRA_KEY = re.compile(r"^(issue ?key|key)$", re.I)
JIRA = re.compile(r"^(issue ?key|key|summary|description|issue ?type|epic.*|parent.*)$", re.I)  # the only Jira columns kept
YAML_KEY = re.compile(r"^\s*-?\s*([\w.-]+)\s*:", re.M)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
GITIGNORE = "# requirements-brief: raw inputs and text extracts (confidential)"


def ids_in(text):
    return {re.sub(r"[ _]", "-", i) for i in ID.findall(text) if not NOT_ID.match(i)}


def id_key(x):
    return re.sub(r"\d+", "", x), int(re.search(r"\d+", x)[0])


def docx_text(p):
    with zipfile.ZipFile(p) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
    paras = ["".join(t.text or "" for t in para.iter(f"{W}t")) for para in root.iter(f"{W}p")]
    return "\n".join(x for x in paras if x.strip())


def pdf_text(p):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)


def csv_text(p):
    """Jira-style export (a key column plus summary or description) → one block per row with the kept columns only;
    any other csv → the header."""
    with p.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return "data", ""
    head = [h.strip() for h in rows[0]]
    if any(JIRA_KEY.match(h) for h in head) and any(re.match(r"^(summary|description)$", h, re.I) for h in head):
        keep = [i for i, h in enumerate(head) if JIRA.match(h)]
        blocks = ["\n".join(f"{head[i]}: {r[i]}" for i in keep if i < len(r) and r[i].strip()) for r in rows[1:]]
        return "tickets", "\n\n".join(blocks)
    return "data", "columns: " + ", ".join(head)


def structured_text(p):
    """JSON or YAML: a list of records (or a dict holding one) is data → its keys only; anything else is read as text."""
    raw = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix.lower() == ".json":
        try:
            doc = json.loads(raw)
        except ValueError:
            return "text", raw
        lists = [doc] if isinstance(doc, list) else [v for v in doc.values() if isinstance(v, list)] if isinstance(doc, dict) else []
        for lst in lists:
            if len(lst) > RECORDS and all(isinstance(x, dict) for x in lst):
                keys = sorted({k for x in lst for k in x})
                return "data", f"records: {len(lst)}\nkeys: " + ", ".join(keys)
        return "text", raw
    items = raw.count("\n- ")
    if items > RECORDS:
        return "data", f"records: about {items}\nkeys: " + ", ".join(sorted(set(YAML_KEY.findall(raw))))
    return "text", raw


def xlsx_header(p):
    try:
        import openpyxl
    except ImportError:
        return "sheets not read (openpyxl not installed): export as CSV"
    wb = openpyxl.load_workbook(p, read_only=True)
    out = []
    for ws in wb.worksheets:
        first = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
        out.append(f"{ws.title}: columns: " + ", ".join("" if c is None else str(c) for c in first))
    return "\n".join(out)


def one(p):
    """(kind, text or None, note) for one file."""
    s = p.suffix.lower()
    if SECRET.search(p.as_posix()):
        return "secret", None, "secret file: not opened"
    if s in TEXT:
        return "text", p.read_text(encoding="utf-8", errors="replace"), ""
    if s in STRUCTURED:
        kind, t = structured_text(p)
        return kind, t, "" if kind == "text" else "data file: structure only"
    if s == ".docx":
        return "docx", docx_text(p), ""
    if s == ".pdf":
        t = pdf_text(p)
        return "pdf", t, "" if t is not None else "pypdf not installed: export the PDF as text"
    if s in (".csv", ".tsv"):
        kind, t = csv_text(p)
        return kind, t, "" if kind == "tickets" else "data file: header only"
    if s in (".xlsx", ".xlsm"):
        return "data", xlsx_header(p), "data file: header only"
    return "other", None, "not read"


def gitignore(folders):
    """Add the raw-input folders (relative, under the current folder) to .gitignore here, created if missing."""
    gi = Path(".gitignore")
    lines = gi.read_text(encoding="utf-8").splitlines() if gi.is_file() else []
    add = [f"/{f}/" for f in folders if f"/{f}/" not in lines and f"{f}/" not in lines]
    if add:
        gi.write_text("\n".join(lines + [GITIGNORE] + add) + "\n", encoding="utf-8")
        print(f"added to .gitignore: {', '.join(add)}")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    out_dir, paths = None, []
    it = iter(argv)
    for a in it:
        if a == "--text":
            out_dir = Path(next(it, "generated-docs/_spec/text"))
        else:
            paths.append(Path(a))
    if not paths:
        sys.exit(__doc__)
    skip = out_dir.resolve() if out_dir else None
    files, used = [], set()  # (file, name): relative to the scanned folder; a name already taken gets the folder in front
    for p in paths:
        found = [(x, x.relative_to(p).as_posix()) for x in sorted(p.rglob("*")) if x.is_file() and not (skip and skip in x.resolve().parents)] if p.is_dir() else [(p, p.name)]
        for x, rel in found:
            rel = rel if rel not in used else f"{p.name}/{rel}"
            used.add(rel)
            files.append((x, rel))
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        under = lambda f: not f.is_absolute() and ".." not in f.parts
        sib = out_dir.parent / "inputs"
        gitignore([f.as_posix() for f in (out_dir, sib) if under(f) and (f is out_dir or f.is_dir())])
    inputs = []
    for p, rel in files:
        kind, text, note = one(p)
        ids = sorted(ids_in(text or ""), key=id_key)
        print(f"{p.as_posix()} · {kind} · {p.stat().st_size} bytes · ids: {len(ids)}" + (f" · {note}" if note else ""))
        if out_dir and text:
            (out_dir / (rel.replace("/", "__") + ".txt")).write_text(text, encoding="utf-8")
        inputs.append({"name": rel, "kind": kind, "ids": ids})
    print(json.dumps({"inputs": inputs}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
