"""Inventory of the knowledge graph: what the docs must cover, and the fixed doc skeleton (plan) derived from it.

Usage: python <skill>/references/templates/inventory.py [--out DIR]   (run from the repo root)
       python <skill>/references/templates/inventory.py --check-facts [--out DIR]   (reruns every facts.json `how`)
Finds the graph like build.py (.knowledge-graph pointer file, else <repo>-knowledge-graph/; none -> a plan from a
stdlib file scan: entry points by convention, config, CI and test files, no flows) and writes
DIR/inventory.json and DIR/facts.json (DIR default generated-docs/_spec). Same graph and repo -> byte-identical files;
facts the writer added to facts.json are kept.
"""
import ast
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HOW = "python <skill>/references/templates/inventory.py"
HERE = Path(__file__).resolve().parent
TEST = re.compile(r"(^|/)(tests?|__tests__|fixtures?|spec)/|(^|/)(test_[^/]*|[^/]*_test\.\w+|[^/]*\.(test|spec)\.\w+|conftest\.py)$")
CI = re.compile(r"(^|/)(\.github/|\.gitlab-ci|azure-pipelines|Jenkinsfile|\.circleci/|bitbucket-pipelines|docker-compose)")
DOCCFG = re.compile(r"\.(md|rst|txt|ya?ml|json|toml|ini|cfg|conf|html?)$", re.I)
DATA = re.compile(r"\.(csv|tsv|json|jsonl|ini|txt|parquet|avro|xml|xlsx?)$", re.I)  # fixtures: test data, not tests
CODE = re.compile(r"\.(py|ts|tsx|js|jsx|mjs|go|rs|java|kt|scala|rb|cs|php)$")
BROKER = re.compile(r"kafka|redpanda|kinesis|pub/?sub|event ?hubs?|rabbitmq|nats|faust|pulsar", re.I)
ML = re.compile(r"onnx|mlflow|sklearn|scikit|xgboost|lightgbm|torch|tensorflow|keras|feast|inference|\btrain|predict|drift", re.I)
SECRET = re.compile(r"\.env.*|.*\.(pem|key|p12|pfx|jks|keystore|tfvars)|.*\.tfstate.*|id_.*|credentials.*|secrets?.*|"
                    r"\.npmrc|\.pypirc|\.netrc|\.git-credentials|profiles\.ya?ml|kubeconfig|.*service[-_]?account.*\.json", re.I)  # never read
HEX = re.compile(r"[0-9a-f]{7,40}")
SKIP_ITEMS = {"repo", "folder", "file", "column", "test_case", "dbt_test", "example_data"}
TEST_TYPES = ("test_case", "test_file", "file", "function", "module", "class")  # tests come only from these node types
# step order from the edges between a flow's steps: FORWARD = `from` runs first, BACK = `to` runs first
FORWARD = {"calls", "triggers", "schedules", "writes", "deploys", "produces", "publishes", "feeds", "exposes", "starts"}
BACK = {"depends_on", "reads", "ref", "derived_from", "imports", "consumes", "needs"}
RANK = {"endpoint": 0, "job": 1, "dag": 1, "cli_command": 2, "ui_screen": 3}  # Main flows order: entry group, then path
RUNNABLE = {"pipeline", "dbt", "web_api", "streaming"}  # services and pipelines: the only repos with an Operations section
OUTPUT = ("table", "view", "dbt_model", "storage_location", "external_system", "ui_screen")  # step types an h3 may end on
RUN_TESTS = "Run the tests"  # the one Operations how-to for every test-tagged process node
ENTRY_H3 = {"job": "Scheduled run → written data", "endpoint": "HTTP request → response", "cli_command": "Command line → output",
            "ui_screen": "User action → screen", "terraform_root": "Terraform root → cloud resources",
            "public_module": "Function call → return value"}
MAX_ER = 9
BRANCH_TYPES = {"decision", "branch", "condition"}  # a step of this type is a branch: its Main flows h3 gets a flow diagram


def version():
    """Templates version: hash of the shipped scripts and style. build.py and inventory.py print it; a spec folder
    whose inventory.json has another version was planned by another copy of the skill."""
    h = hashlib.sha256()
    for f in ("build.py", "check.py", "inventory.py", "style.css"):
        p = HERE / f
        h.update(p.read_bytes().replace(b"\r\n", b"\n") if p.is_file() else b"")
    return h.hexdigest()[:10]


def secret(rel_path):
    """A secret file is never read: by any part of its path (secrets/x.txt) or a known secret file."""
    parts = Path(rel_path).parts
    return any(SECRET.fullmatch(p) for p in parts) or tuple(parts[-2:]) == (".docker", "config.json")


def git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


CI_DIRS = {".github", ".gitlab", ".circleci", ".azure-pipelines"}  # hidden folders a scan still reads
SCAN_SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "dist", "build",
             "reviews", "analysis", "generated-docs", ".terraform"}
CONFIG = re.compile(r"(^|/)(pyproject\.toml|setup\.cfg|setup\.py|package\.json|tsconfig\.json|Dockerfile[^/]*|docker-compose[^/]*"
                    r"|Makefile|[^/]+\.(toml|ya?ml|ini|cfg|conf|properties))$")
BY_CONVENTION = [  # (node type, path pattern): entry points when there is no graph
    ("dag", re.compile(r"(^|/)dags/(?!__init__)[^/]+\.py$")),
    ("endpoint", re.compile(r"(^|/)(routes?|routers?|endpoints|controllers|views)/(?!__init__)[^/]+\.(py|ts|js)$"
                            r"|(^|/)(app|server|api|wsgi|asgi)\.(py|ts|js)$")),
    ("cli_command", re.compile(r"(^|/)(cli|__main__|manage|main)\.py$|(^|/)bin/[^/.]+$")),
    ("ui_screen", re.compile(r"(^|/)(pages|screens|views)/[^/]+\.(tsx|jsx|vue|svelte)$|(^|/)App\.(tsx|jsx|vue|svelte)$")),
]


def repo_paths():
    """Repo files from the cwd: git tracked + untracked (not ignored), else a walk; tool folders, graph folders and secret
    files left out (never read)."""
    got = git("-c", "core.quotepath=off", "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    if not got:
        for d, dirs, fs in os.walk("."):
            dirs[:] = sorted(x for x in dirs if x not in SCAN_SKIP and (not x.startswith(".") or x in CI_DIRS))
            got += [Path(os.path.relpath(Path(d) / f)).as_posix() for f in sorted(fs)]
    skip = lambda p: any(x in SCAN_SKIP or x.endswith("-knowledge-graph") for x in Path(p).parts[:-1]) or secret(p)
    return sorted(p.replace("\\", "/") for p in got if not skip(p) and Path(p).is_file())


def scan_nodes():
    """No graph: graph-shaped nodes from a file scan (stdlib only). Entry points by convention (dags/, routes, cli.py,
    __main__.py, pages/, pyproject [project.scripts], dbt_project.yml + models/*.sql, Terraform roots), config files,
    CI files, test files, code modules and their top-level public functions and classes (Python, by ast). No flows,
    no tables, no edges."""
    paths, nodes = repo_paths(), []
    add = lambda t, name, path, line=None, **k: nodes.append({"id": f"{t}:{path}:{name}", "type": t, "name": name, "path": path,
                                                              "line_start": line, **k})
    for p in paths:
        test, ci = bool(TEST.search(p)), bool(CI.search(p))
        if ci:
            add("job", p, p)
        elif test:
            add("file", p, p) if CODE.search(p) and not DATA.search(p) else None
        elif CONFIG.search(p):
            add("config", p, p)
        for t, rx in BY_CONVENTION if not (test or ci) else []:
            if rx.search(p):
                add(t, Path(p).stem if t in ("dag", "ui_screen") else p, p)
                break
        if CODE.search(p) and not test and not ci:
            add("module", p, p)
        if p.endswith(".py") and not test and not ci:
            try:
                tree = ast.parse(Path(p).read_text(encoding="utf-8", errors="ignore"))
            except (SyntaxError, ValueError):
                continue
            for x in tree.body:
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not x.name.startswith("_"):
                    add("class" if isinstance(x, ast.ClassDef) else "function", x.name, p, x.lineno)
    if "dbt_project.yml" in {Path(p).name for p in paths}:
        nodes += [{"id": f"dbt_model:{p}", "type": "dbt_model", "name": Path(p).stem, "path": p}
                  for p in paths if re.search(r"(^|/)models/.+\.sql$", p)]
    tf = sorted({str(Path(p).parent.as_posix()) for p in paths if p.endswith(".tf") and "modules/" not in f"{p}"})
    nodes += [{"id": f"tf:{d}", "type": "module", "name": d, "path": d, "tags": ["terraform"]} for d in tf]
    nodes += [{"id": f"script:{s}", "type": "cli_command", "name": s, "path": "pyproject.toml"} for s in sorted(scripts())]
    return nodes


def scripts():
    """pyproject [project.scripts]: {command: "package.module:function"}."""
    try:
        import tomllib
        return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8")).get("project", {}).get("scripts", {})
    except (ImportError, ValueError, OSError):
        return {}


def unit(path):
    """The program or app a file belongs to: its top package (src/ and lib/ skipped), or the file's own name at the top
    or in bin/."""
    parts = Path(path).parts
    parts = parts[1:] if parts[:1] in (("src",), ("lib",)) else parts
    return parts[0] if len(parts) > 1 and parts[0] != "bin" else Path(path).stem


def scan_plan(inv):
    """A file-scan plan: one Main flows h3 per entry point: a CLI program (its script, cli.py and __main__.py), an app
    (its routes or screens), a job, a Terraform root, a package's public API (only modules with a public function or
    class; its CLI files left out). Deploy units = the CI files; no section ruled out (the scan cannot tell a missing
    data model from an unscanned one)."""
    p, sc = inv["plan"], scripts()
    callable_ = {x["path"] for t in ("function", "class") for x in inv["items"].get(t, [])}
    cli = {e["path"] for e in inv["entry_points"] if e["group"] == "cli_command"}
    groups = {}  # (group, unit) -> (name, files)
    for e in inv["entry_points"]:
        g, path = e["group"], e["path"]
        stem = Path(path).stem
        if g == "public_module" and (path in cli or path not in callable_ or stem.startswith("_") and stem != "__init__"):
            continue
        script = g == "cli_command" and e["name"] in sc  # a pyproject script: the package of its target module
        key = e["name"] if g in ("job", "terraform_root") else re.split(r"[.:]", sc[e["name"]])[0] if script else unit(path)
        name, files = groups.get((g, key), (None, []))
        if not name or script:  # a program is named by its script
            name = e["name"] if script or g in ("job", "terraform_root") else key
        groups[(g, key)] = (name, files + [path])
    p["main_flows"] = [{"h3": f"{name}: {ENTRY_H3[g]}", "flow": None, "steps": 0, "ordered": False, "diagram": False, "entry": None,
                        "boxes": [], "files": sorted(set(files))} for (g, _), (name, files) in groups.items()] or p["main_flows"]
    p["deploy"]["units"] = [x["name"] for x in inv["items"].get("job", []) if x.get("ci")]
    for d in p["sections"].values():
        d["not_applicable"] = {}
    p["coverage"] = [t for t in p["coverage"] if t not in ("flow", "business_rule", "process", "table", "view", "storage_location")]


def find_graph():
    """(graph folder or None, why). Pointer file first, then <repo>-knowledge-graph/ in the repo root."""
    link = Path(".knowledge-graph")
    if link.is_file():
        p = Path(link.read_text(encoding="utf-8").strip())
        return (p, "") if (p / "graph").is_dir() else (None, f".knowledge-graph points to {p.name}, which has no graph/ folder")
    name = Path(git("rev-parse", "--show-toplevel") or Path.cwd()).name
    p = Path(f"{name}-knowledge-graph")
    if (p / "graph").is_dir():
        return p, ""
    return None, f"no .knowledge-graph pointer and no {p}/graph/ folder"


def rel(p):
    """Path from the cwd; a path outside it (other drive, ../, absolute pointer) as its folder name only."""
    try:
        r = Path(os.path.relpath(p)).as_posix()
    except ValueError:
        return Path(p).name
    return Path(p).resolve().name if r == ".." or r.startswith("../") else r


def graph_meta(graph):
    try:
        m = json.loads((Path(graph) / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return m if isinstance(m, dict) else {}


def meta_commit(meta):
    """Graph commit from meta.json, only if it is a commit id ("not a git repo" is not one)."""
    v = next((meta[k] for k in ("commit", "repo_commit", "git_commit", "head", "sha") if isinstance(meta.get(k), str)), "")
    v = v.strip().lower()
    return v[:12] if HEX.fullmatch(v) else ""


def meta_date(meta):
    return next((str(meta[k])[:10] for k in ("built_at", "built", "generated_at", "date") if meta.get(k)), "")


def stale(meta):
    """Repo files (from the cwd) whose content no longer matches meta.json's file hashes (sha256, sha1, git blob or md5,
    full or as a prefix; LF and CRLF both tried), plus hashed files that are gone. Secret files are never read."""
    hashes = next((meta[k] for k in ("file_hashes", "files", "hashes") if isinstance(meta.get(k), dict)), {})
    out = []
    for f, want in sorted(hashes.items()):
        p, want = Path(f), str(want).lower()
        if secret(f) or not want:
            continue
        if not p.is_file():
            out.append(f"{f} (deleted)")
            continue
        data, got = p.read_bytes(), []
        for b in {data, data.replace(b"\r\n", b"\n")}:
            got += [hashlib.sha256(b).hexdigest(), hashlib.sha1(b).hexdigest(), hashlib.md5(b).hexdigest(),
                    hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()]
        if not any(g.startswith(want) for g in got):
            out.append(f)
    return out


def jsonl(p):
    if not p.is_file():
        return None
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def item(n):
    line = n.get("line_start", n.get("line"))
    return {"name": str(n.get("name") or n.get("id")), "path": str(n.get("path") or "").replace("\\", "/"),
            "line": line if isinstance(line, int) else None}


def order(x):
    return (x["path"], x["line"] or 0, x["name"])


def is_test(n):
    """A test node, left out of items and entry points. Never a process, flow or document: a test process is a how-to."""
    if n.get("type") in ("process", "flow", "document"):
        return False
    return tagged_test(n) or n.get("type") in ("test_case", "dbt_test") or str(n.get("name", "")).startswith("test_")


def tagged_test(n):
    return bool(TEST.search(str(n.get("path") or "").replace("\\", "/"))) or "test" in (n.get("tags") or [])


def is_test_file(n):
    """A test file: a test_case, file, function, module or class node on a test path (never a process, flow or doc)."""
    return n.get("type") in TEST_TYPES and bool(TEST.search(str(n.get("path") or "").replace("\\", "/")))


def is_ci(n):
    return bool(CI.search(str(n.get("path") or ""))) or bool({"ci", "docker-compose"} & set(n.get("tags") or []))


def public_module(n):
    tags, last = set(n.get("tags") or []), str(n.get("name", "")).split(".")[-1]
    return (n.get("type") == "module" and "external" not in tags and "terraform" not in tags and n.get("path")
            and not last.startswith("_") and bool(CODE.search(str(n["path"]))))


def profile(nodes, edges):
    """Repo kinds from node types, each with the counts that decided it. pipeline needs a real scheduler: a dag, a job
    with tasks, or a schedules edge into a job, dag or task (an in-process timer is not one: it goes to Events)."""
    c = Counter(n.get("type") for n in nodes)
    byid = {n["id"]: n for n in nodes}
    typ = lambda i: byid.get(i, {}).get("type")
    run = {i for i, n in byid.items() if n["type"] in ("job", "dag") and not is_ci(n)}
    linked = {e.get(a) for e in edges if e.get("type") in ("contains", "part_of") for a, b in (("from", "to"), ("to", "from"))
              if e.get(a) in run and typ(e.get(b)) == "task"}
    sched = sum(1 for e in edges if e.get("type") == "schedules" and typ(e.get("to")) in ("job", "dag", "task")
                and not is_ci(byid.get(e.get("to"), {})))
    paths = {str(n["path"]) for n in nodes if n.get("path")}
    ev = {
        "pipeline": {k: v for k, v in (("dag", sum(typ(i) == "dag" for i in run)), ("job with tasks", len(linked)),
                                       ("schedules edges", sched)) if v},
        "dbt": {t: c[t] for t in ("dbt_model", "dbt_source", "dbt_macro") if c[t]},
        "web_api": {"endpoint": c["endpoint"]} if c["endpoint"] else {},
        "ui": {"ui_screen": c["ui_screen"]} if c["ui_screen"] else {},
        "cli": {"cli_command": c["cli_command"]} if c["cli_command"] else {},
        "infra": {k: v for k, v in (("terraform_resource", c["terraform_resource"]),
                                     ("terraform module", sum("terraform" in (n.get("tags") or []) for n in nodes if n.get("type") == "module"))) if v},
        "streaming": {k: v for k, v in (("topic", sum("topic" in (n.get("tags") or []) for n in nodes if n.get("type") == "storage_location")),
                                         ("broker client", sum(bool(BROKER.search(str(n.get("name")))) for n in nodes if n.get("type") == "external_system"))) if v},
        "ml": {"ml names": sum(bool(ML.search(" ".join([str(n.get("name"))] + [str(t) for t in n.get("tags") or []]))) for n in nodes
                               if n.get("type") not in ("business_rule", "document", "column"))},
        "library": {"public module": sum(bool(public_module(n)) and not is_test(n) for n in nodes)},
        "docs_config": {"doc/config paths": sum(bool(DOCCFG.search(p)) for p in paths), "all paths": len(paths)},
    }
    keep = {
        "pipeline": bool(ev["pipeline"]), "dbt": bool(ev["dbt"].get("dbt_model")), "web_api": bool(c["endpoint"]),
        "ui": bool(c["ui_screen"]), "cli": bool(c["cli_command"]), "infra": bool(ev["infra"]),
        "streaming": ev["streaming"].get("topic", 0) >= 1 or ev["streaming"].get("broker client", 0) >= 2,
        "ml": ev["ml"]["ml names"] >= 3,
        "docs_config": bool(paths) and 2 * ev["docs_config"]["doc/config paths"] >= len(paths),
    }
    keep["library"] = ev["library"]["public module"] > 0 and not any(keep[k] for k in ("pipeline", "dbt", "web_api", "ui", "infra"))
    return [{"kind": k, "evidence": ev[k]} for k in ev if keep[k]]


def topo(ids, edges):
    """The one order of the step nodes `ids` that the edges between them allow (FORWARD/BACK types), or None when the
    edges leave more than one order (or none: a cycle)."""
    pos, after = set(ids), {i: set() for i in ids}
    for e in edges:
        a, b, t = e.get("from"), e.get("to"), e.get("type")
        if a in pos and b in pos and a != b and (t in FORWARD or t in BACK):
            first, then = (a, b) if t in FORWARD else (b, a)
            after[first].add(then)
    need = {i: sum(i in v for v in after.values()) for i in ids}
    out, ready = [], [i for i in ids if not need[i]]
    while ready:
        if len(ready) > 1:
            return None
        i = ready.pop()
        out.append(i)
        for j in after[i]:
            need[j] -= 1
            if not need[j]:
                ready.append(j)
    return out if len(out) == len(ids) else None


def branches(steps, edges):
    """The flow branches: a step is a decision (BRANCH_TYPES), or leads to 2+ other steps of the flow."""
    ids = {s["id"] for s in steps}
    nxt = {}
    for e in edges:
        a, b, t = e.get("from"), e.get("to"), e.get("type")
        if a in ids and b in ids and a != b and (t in FORWARD or t in BACK):
            nxt.setdefault(a if t in FORWARD else b, set()).add(b if t in FORWARD else a)
    return any(s["type"] in BRANCH_TYPES for s in steps) or any(len(v) > 1 for v in nxt.values())


def flows(nodes, edges, byid):
    """Graph flow and process nodes with their steps, and whether that order is reliable (`ordered`): the node's own
    numbered steps list, part_of edges that all carry a step number, or the one order the edges between the steps
    allow. Otherwise the steps keep file order and ordered is false. Sorted by entry group (endpoint, job, cli,
    ui, other: the type of the first step), then path."""
    out = []
    for n in nodes:
        if n.get("type") not in ("flow", "process"):
            continue
        steps, ordered = [], False
        if isinstance(n.get("steps"), list) and n["steps"] and all(isinstance(s, dict) for s in n["steps"]):
            ordered = True  # an explicit list is an order
            for k, s in sorted(enumerate(n["steps"]), key=lambda x: (x[1].get("n") if isinstance(x[1].get("n"), int) else x[0], x[0])):
                m = byid.get(s.get("node"), {})
                steps.append({"name": str(m.get("name") or s.get("node") or s.get("text") or ""), "type": m.get("type"),
                              "text": s.get("text"), "evidence": s.get("evidence"), "id": s.get("node")})
        else:
            po = [(e.get("step") if isinstance(e.get("step"), int) else 10**6, k, e) for k, e in enumerate(edges)
                  if e.get("type") == "part_of" and e.get("to") == n["id"]]
            po.sort(key=lambda x: x[:2])
            ordered = bool(po) and all(x[0] < 10**6 for x in po)
            if po and not ordered:
                ids = list(dict.fromkeys(e.get("from") for _, _, e in po))
                got = topo(ids, edges)
                if got:
                    po.sort(key=lambda x: got.index(x[2].get("from")))
                    ordered = True
            for _, _, e in po:
                m = byid.get(e.get("from"), {})
                steps.append({"name": str(m.get("name") or e.get("from")), "type": m.get("type"), "text": None,
                              "evidence": e.get("evidence"), "id": e.get("from")})
        types = [s["type"] for s in steps[:1]] if ordered else [s["type"] for s in steps]
        rank = min([RANK.get(t, 4) for t in types] or [4])
        out.append({**item(n), "id": n["id"], "type": n["type"], "ordered": ordered, "branches": branches(steps, edges),
                    "steps": steps, "_rank": rank})
    out.sort(key=lambda f: (f["_rank"],) + order(f))
    for f in out:
        del f["_rank"]
        for s in f["steps"]:
            s.pop("id")
    return out


def h3(f, byid):
    """Main flows h3: the flow name if it has "→"; else "<name>: a → z" from its summary chain; else, when the steps are
    ordered and the last one is an output (table, store, external system, screen), "<name> → <last>"; else the flow
    name alone. Never a step function name, never a made-up order."""
    name = re.sub(r"\s*(->|→)\s*", " → ", f["name"]).strip()
    if "→" in name:
        return name
    chain = re.split(r"\s*(?:->|→)\s*", str(byid[f["id"]].get("summary") or "").split(";")[0])
    a, z = chain[0].split(":")[-1].strip(" ."), chain[-1].split(",")[0].strip(" .")
    if len(chain) > 1 and a and z and len(a) <= 40 and len(z) <= 40:
        return f"{name}: {a} → {z}"
    last = f["steps"][-1] if f["ordered"] and len(f["steps"]) > 1 else {}
    if last.get("type") in OUTPUT and len(last["name"]) <= 40:
        return f"{name} → {last['name']}"
    return name


def entries(main, flows_):
    """Main flows diagram entry (title "<entry>, N steps"): the first step; when it is longer than 40 chars or not unique
    among the diagrams, the flow name up to its first ":" or "→"; still not unique, the h3."""
    byid = {f["id"]: f for f in flows_}
    pick = [(byid[m["flow"]]["steps"][0]["name"] if m["diagram"] else None) for m in main]
    dup = [x is not None and (len(x) > 40 or pick.count(x) > 1) for x in pick]
    pick = [re.split(r"\s*(?:->|→|:)\s*", byid[m["flow"]]["name"])[0] if d else x for x, d, m in zip(pick, dup, main)]
    return [m["h3"] if x is not None and pick.count(x) > 1 else x for x, m in zip(pick, main)]


def diagram_titles(kinds, sched=False):
    """Title form of each top-level diagram outside technical Main flows (a sub-flow: "inside <box>"): "steps" =
    numbered arrows, "<entry>, N steps"; "area" = a map without numbers, "<area> area". The technical Overview of a
    scheduled repo is one run (steps); of any other repo a map."""
    run = "steps" if sched or set(kinds) & {"pipeline", "dbt"} else "area"
    return {"technical": {"Overview": run, "Architecture": "area", "Job DAG and schedule": "steps", "Screens and navigation": "area",
                          "Endpoints": "area", "Commands": "area", "Events and messages": "area", "Deploy and environments": "steps"},
            "overview": {"How it works": "steps"},
            "user-guide": {"How it reaches you": "steps", "Screens": "area", "What answers what": "area", "When data is fresh": "steps"}}


def public_api(nodes):
    """Library public API: functions and classes in a public module, no name part starting with "_"; a dotted name only
    as Class.method (inner functions are not API). Test nodes left out."""
    path = lambda n: str(n.get("path") or "").replace("\\", "/")
    mods = {path(n) for n in nodes if public_module(n) and not is_test(n)}
    classes = {(path(n), n.get("name")) for n in nodes if n.get("type") == "class"}
    out = []
    for n in nodes:
        parts = str(n.get("name", "")).split(".")
        if (n.get("type") in ("function", "class") and path(n) in mods and not is_test(n) and not any(q.startswith("_") for q in parts)
                and (len(parts) == 1 or len(parts) == 2 and (path(n), parts[0]) in classes)):
            out.append({"type": n["type"], **item(n)})
    return sorted(out, key=order)


def er_areas(tables, fks):
    """Area = one root table (no fk parent) plus all its descendants, in inventory order; neighbouring areas merge
    while the total stays <= 9 tables; a bigger area is cut into parts of 9."""
    names = [t["id"] for t in tables]
    kids = {i: [] for i in names}
    parent = {i: False for i in names}
    for a, b in fks:  # a (child) -> b (parent)
        kids[b].append(a)
        parent[a] = True
    seen, areas = set(), []
    for root in [i for i in names if not parent[i]] + names:  # roots first; leftovers (cycles) after
        if root in seen:
            continue
        got, todo = [], [root]
        while todo:
            i = todo.pop(0)
            if i in seen:
                continue
            seen.add(i)
            got.append(i)
            todo += sorted(kids[i], key=names.index)
        for k in range(0, len(got), MAX_ER):
            areas.append([got[k:k + MAX_ER], 1 + k // MAX_ER, len(got) > MAX_ER, root])
    label = {t["id"]: t["name"] for t in tables}
    merged = []
    for ids, part, cut, root in areas:
        if merged and not cut and not merged[-1]["cut"] and len(merged[-1]["ids"]) + len(ids) <= MAX_ER:
            merged[-1]["ids"] += ids
            merged[-1]["roots"] += 1
        else:
            merged.append({"ids": list(ids), "roots": 1, "cut": cut, "part": part, "root": root})
    out = []
    for a in merged:
        root = label[a["root"]]
        name = ("all tables" if len(merged) == 1 and a["roots"] > 1 else f"{root} (part {a['part']})" if a["cut"]
                else f"{root} + {a['roots'] - 1} more" if a["roots"] > 1 else root)
        out.append({"name": name, "title": f"ER: {name}", "tables": [label[i] for i in a["ids"]]})
    return out


def plan(kinds, inv, nodes, edges):
    k = set(kinds)
    data = any(d["type"] in ("table", "view", "dbt_model") for d in inv["data_objects"])
    model = sum(d["type"] in ("table", "view", "dbt_model") for d in inv["data_objects"]) >= 2 or bool(inv["fks"])
    byid = inv["_byid"]
    tf_sched = any(e.get("type") == "schedules" and byid.get(e.get("from"), {}).get("type") == "terraform_resource" for e in edges)
    sched = bool(k & {"pipeline", "dbt"}) or tf_sched  # a Terraform-defined scheduler is a schedule too
    rules = bool(inv["items"].get("business_rule")) and "docs_config" not in k
    runs = bool(k & RUNNABLE)
    apply = {  # section -> (applies, reason when it does not)
        "technical": {"Job DAG and schedule": (sched, "no dag, job with tasks, scheduled job outside CI, Terraform scheduler or dbt models in the graph"),
                      "Screens and navigation": ("ui" in k, "no ui_screen nodes in the graph"),
                      "Endpoints": ("web_api" in k, "no endpoint nodes in the graph"),
                      "Commands": ("cli" in k, "no cli_command nodes in the graph"),
                      "Events and messages": ("streaming" in k, "no topics or message-broker clients in the graph"),
                      "Data model": (model, "one table and no fk edges in the graph: name it in Architecture components" if data
                                     else "no table, view or dbt_model nodes in the graph"),
                      "Operations": (runs, "not a service or pipeline (no pipeline, dbt, web_api or streaming profile): "
                                           "name each process in the Deploy or Tests steps")},
        "overview": {"Schedule": (sched, "nothing scheduled in the graph")},
        "user-guide": {"Screens": ("ui" in k, "no ui_screen nodes in the graph"),
                       "What answers what": (data or "web_api" in k, "no data objects or endpoints in the graph"),
                       "When data is fresh": (sched, "nothing scheduled in the graph"),
                       "History and deletions": (data, "no data objects in the graph")},
    }
    always = {"technical": ["Overview", "Architecture", "Main flows", "Deploy and environments"],
              "overview": ["What it is and why", "How it works", "Example"],
              "user-guide": ["How it reaches you", "How to *", "Problems and fixes", "Who to contact"]}
    always["technical"] += ["Business rules"] if rules else []
    need = {"technical": ["Job DAG and schedule", "Data model", "Screens and navigation", "Endpoints", "Commands", "Events and messages",
                          "Operations"],
            "overview": [], "user-guide": ["What answers what", "When data is fresh", "Screens"]}
    sections = {d: {"required": always[d] + [s for s in need[d] if apply[d][s][0]],
                    "not_applicable": {s: why for s, (ok, why) in apply[d].items() if not ok}} for d in always}
    main, fl = [], [f for f in inv["flows"] if f["type"] == "flow"]
    for f in fl:
        main.append({"h3": h3(f, byid), "flow": f["id"], "steps": len(f["steps"]), "ordered": f["ordered"],
                     "diagram": f["branches"], "entry": None, "boxes": [s["name"] for s in f["steps"]]})
    for m, e in zip(main, entries(main, fl)):
        m["entry"] = e
    if not main:  # no flow nodes: one h3 per entry-point group
        main = [{"h3": ENTRY_H3[g], "flow": None, "steps": 0, "ordered": False, "diagram": False, "entry": None, "boxes": []}
                for g in dict.fromkeys(e["group"] for e in inv["entry_points"])]
    if not main:
        main = [{"h3": "Input → output", "flow": None, "steps": 0, "ordered": False, "diagram": False, "entry": None, "boxes": []}]
    cover = ["flow"]
    cover += ["job", "dag", "task"] if "pipeline" in k else []
    cover += ["dbt_model"] if "dbt" in k else []
    cover += ["table", "view"] if data else []
    cover += ["storage_location"] if inv["items"].get("storage_location") else []
    cover += ["endpoint"] if "web_api" in k else []
    cover += ["ui_screen"] if "ui" in k else []
    cover += ["cli_command"] if "cli" in k else []
    cover += ["terraform_resource"] if "infra" in k else []
    api = public_api(nodes) if "library" in k else []
    cover += (["module"] + (["api"] if api else [])) if "library" in k else []
    cover += ["business_rule"] if rules else []
    cover += ["process"] if inv["items"].get("process") else []
    cover += ["config"] + (["test_file"] if inv["tests"] else [])
    app = [a for a, ks in (("pipeline", {"pipeline", "dbt"}), ("ui", {"ui"}), ("api", {"web_api"}), ("cli", {"cli"}), ("events", {"streaming"})) if k & ks]
    procs = sorted((n for n in nodes if n.get("type") == "process"), key=lambda n: order(item(n)))
    hows = [n["name"] for n in procs if not tagged_test(n)] + ([RUN_TESTS] if any(tagged_test(n) for n in procs) else [])
    # Deploy names what the graph deploys and how: CI and compose jobs and tasks, and deploys edges (not those of
    # Terraform resources: Architecture covers them)
    units = [x["name"] for t in ("job", "dag", "task") for x in inv["items"].get(t, []) if x.get("ci")
             and not re.fullmatch(r"[\w.-]+/[\w./-]+@\S+", x["name"])]  # a CI action reference (owner/action@v4) deploys nothing
    deps = sorted({f"{byid[e['from']]['name']} → {byid[e['to']]['name']}" for e in edges if e.get("type") == "deploys"
                   and e.get("from") in byid and e.get("to") in byid and byid[e["from"]]["type"] != "terraform_resource"})
    return {"app_types": app, "main_flows": main, "how_tos": list(dict.fromkeys(hows)) if runs else [],
            "er_areas": er_areas(inv["_tables"], inv["_fks"]) if model else [], "sections": sections, "coverage": cover,
            "diagram_titles": diagram_titles(kinds, sched), "api": api,
            "deploy": {"units": list(dict.fromkeys(units)), "deploys": deps}, "rerun_and_backfill": bool(k & {"pipeline", "dbt"})}


def facts_for(out, inv):
    """The plan counts, each with a `how` that reruns from the repo root (one POSIX shell line)."""
    p = rel(out / "inventory.json")
    q = lambda expr: f"python -c \"import json; d = json.load(open('{p}', encoding='utf-8')); print({expr})\""
    return [{"fact": "main flows (h3)", "value": len(inv["plan"]["main_flows"]), "how": q("len(d['plan']['main_flows'])")},
            {"fact": "ER areas", "value": len(inv["plan"]["er_areas"]), "how": q("len(d['plan']['er_areas'])")},
            {"fact": "test files", "value": len(inv["tests"]), "how": q("len(d['tests'])")}]


def keep_facts(path, mine):
    """Writer facts already in facts.json: every fact the inventory does not write (old inventory facts dropped)."""
    try:
        old = json.loads(path.read_text(encoding="utf-8")).get("facts", [])
    except (OSError, ValueError, AttributeError):
        return []
    ours = {f["fact"] for f in mine}
    return [f for f in old if isinstance(f, dict) and f.get("fact") not in ours and f.get("how") != HOW
            and not re.fullmatch(r"graph \S+ nodes", str(f.get("fact")))]


def posix_sh():
    """A POSIX sh for the `how` lines: on Windows Git for Windows' own (a `bash` on PATH there may be WSL's), else sh."""
    if os.name != "nt":
        return shutil.which("sh")
    git_exe = shutil.which("git")
    root = Path(git_exe).resolve().parent.parent if git_exe else None  # <Git>/cmd/git.exe or <Git>/mingw64/bin/git.exe
    for c in [root / x for x in ("bin/sh.exe", "usr/bin/sh.exe", "../bin/sh.exe", "../usr/bin/sh.exe")] if root else []:
        if c.is_file():
            return str(c.resolve())
    return None


def check_facts(out):
    """Rerun every facts.json `how` from the repo root and compare its last output line with `value` (a number: the
    line's first number, `200_000` = 200000, so `retries: 10` or `19 passed in 0.1s` match). A how without
    shell syntax runs directly (`python` = this Python); one with pipes, globs or redirects runs in a POSIX sh."""
    try:
        facts = json.loads((out / "facts.json").read_text(encoding="utf-8")).get("facts", [])
    except (OSError, ValueError, AttributeError):
        sys.exit(f"ERROR no readable {rel(out / 'facts.json')}: run {HOW} first")
    sh, bad = posix_sh(), 0
    env = dict(os.environ, PATH=os.pathsep.join([str(Path(sh).parent)] * bool(sh) + [os.environ.get("PATH", "")]))
    for f in [f for f in facts if isinstance(f, dict)]:
        how, want = str(f.get("how", "")), str(f.get("value", "")).strip()
        if re.search(r"[|<>;&$`*?]", how):
            if not sh:
                bad += 1
                print(f"NOT RUN {f.get('fact')}: needs a POSIX sh (Git for Windows): {how}")
                continue
            cmd = [sh, "-c", how]
        else:
            cmd = shlex.split(how)
            cmd[:1] = [sys.executable] if cmd[:1] == ["python"] else cmd[:1]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
            got = (r.stdout.strip().splitlines() or [""])[-1].strip()
        except (OSError, ValueError) as e:
            got, r = f"({e})", None
        num = re.search(r"-?\d[\d_,]*(?:\.\d+)?", got)
        if got == want or (re.fullmatch(r"-?\d+(\.\d+)?", want) and num and re.sub("[_,]", "", num.group()) == want):
            print(f"ok {f.get('fact')} = {got}")
        else:
            bad += 1
            print(f"MISMATCH {f.get('fact')}: facts.json says {want}, how printed {got!r}"
                  + (f" (exit {r.returncode}: {r.stderr.strip()[:120]})" if r and r.returncode else ""))
    print(f"facts: {len(facts)} rerun, {bad} mismatched or not run")
    sys.exit(1 if bad else 0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("generated-docs/_spec")
    if "--check-facts" in sys.argv:
        return check_facts(out)
    ver = version()
    graph, why = find_graph()
    if not graph and Path(".knowledge-graph").is_file():  # a pointer means a graph was meant: never plan around it
        sys.exit(f"ERROR no knowledge graph: {why}. Fix the pointer or build the graph (darshan-singh-meel-knowledge-graph skill), then rerun: {HOW}")
    if graph:
        nodes, edges = jsonl(graph / "graph" / "nodes.jsonl"), jsonl(graph / "graph" / "edges.jsonl")
        if nodes is None:
            sys.exit(f"ERROR {rel(graph)}/graph/nodes.jsonl is missing: rebuild the graph (darshan-singh-meel-knowledge-graph skill)")
        not_checked = [] if edges is not None else ["graph/edges.jsonl missing: no flow steps from part_of edges, no fk edges"]
    else:  # no graph ({why}): a minimal plan from the files
        nodes, edges, not_checked = scan_nodes(), [], ["no knowledge graph: plan from a file scan; build the graph for flows and coverage"]
    edges = [e for e in edges or [] if isinstance(e, dict)]
    nodes = [n for n in nodes if isinstance(n, dict) and n.get("id") and n.get("type")]
    byid = {n["id"]: n for n in nodes}
    meta = graph_meta(graph) if graph else {}
    if graph and not meta:
        not_checked.append("meta.json missing or unreadable: graph commit and file hashes unknown")
    items = {}
    for n in nodes:
        if n["type"] not in SKIP_ITEMS and not is_test(n) and (n["type"] != "module" or public_module(n) or "terraform" in (n.get("tags") or [])):
            items.setdefault(n["type"], []).append({**item(n), **({"ci": True} if n["type"] in ("job", "dag", "task") and is_ci(n) else {})})
    items = {t: sorted({json.dumps(x, sort_keys=True): x for x in v}.values(), key=order) for t, v in sorted(items.items())}
    entry = [{"group": "job", **item(n)} for n in nodes if n["type"] in ("dag", "job") and not is_ci(n) and not is_test(n)]
    entry += [{"group": n["type"], **item(n)} for n in nodes if n["type"] in ("endpoint", "cli_command", "ui_screen") and not is_test(n)]
    entry += [{"group": "terraform_root", **item(n)} for n in nodes if n["type"] == "module" and "terraform" in (n.get("tags") or [])
              and "module_call" not in (n.get("tags") or []) and "modules/" not in f"{n.get('path')}/" and not is_test(n)]
    kinds = profile(nodes, edges)
    if "library" in [k["kind"] for k in kinds]:
        entry += [{"group": "public_module", **item(n)} for n in nodes if public_module(n) and not is_test(n)]
    groups = list(ENTRY_H3)
    entry.sort(key=lambda e: (groups.index(e["group"]),) + order(e))
    dtypes = ("table", "view", "dbt_model", "storage_location")
    data = sorted(({"type": n["type"], **item(n), "id": n["id"]} for n in nodes if n["type"] in dtypes and not is_test(n)), key=order)
    erk = "table" if any(d["type"] == "table" for d in data) else "dbt_model"
    tables = [d for d in data if d["type"] == erk]
    tid = {d["id"] for d in tables}
    owner = {}  # column -> table, from part_of / contains edges or the column id "column:<table>.<col>"
    for e in edges:
        if e.get("type") == "part_of" and byid.get(e.get("from"), {}).get("type") == "column" and e.get("to") in tid:
            owner.setdefault(e["from"], e["to"])
        if e.get("type") == "contains" and e.get("from") in tid and byid.get(e.get("to"), {}).get("type") == "column":
            owner.setdefault(e["to"], e["from"])
    lift = lambda i: i if i in tid else owner.get(i)
    fks = sorted({(lift(e["from"]), lift(e["to"])) for e in edges if e.get("type") == "fk"
                  and lift(e.get("from")) and lift(e.get("to")) and lift(e["from"]) != lift(e["to"])})
    cols = {}
    for c, t in sorted(owner.items()):
        cols.setdefault(t, []).append(str(byid[c].get("name") or c).split(".")[-1])
    for d in data:
        own = byid[d["id"]].get("columns")
        d["columns"] = cols.get(d["id"]) or [str(x.get("name")) for x in own if isinstance(x, dict)] if isinstance(own, list) else cols.get(d["id"], [])
    tests = sorted({str(n.get("path")).replace("\\", "/") for n in nodes if n.get("path") and is_test_file(n)
                    and not DATA.search(str(n["path"]))})
    inv = {"how": HOW, "templates": ver, "graph": rel(graph) if graph else "", **({} if graph else {"scan": True}),
           "graph_commit": meta_commit(meta), "graph_built": meta_date(meta), "stale_files": stale(meta),
           "counts": {"nodes": len(nodes), "edges": len(edges), "by_type": dict(sorted(Counter(n["type"] for n in nodes).items()))},
           "profile": kinds, "items": items, "flows": flows(nodes, edges, byid), "entry_points": entry,
           "data_objects": [{k: v for k, v in d.items() if k != "id"} for d in data],
           "fks": [{"from": byid[a]["name"], "to": byid[b]["name"]} for a, b in fks], "tests": tests}
    inv["_byid"], inv["_tables"], inv["_fks"] = byid, tables, fks
    if not inv["flows"] and graph:
        not_checked.append("no flow or process nodes: Main flows planned from entry points")
    if not nodes:
        not_checked.append("graph has no nodes: empty inventory" if graph else "file scan found no files")
    unordered = [f["name"] for f in inv["flows"] if f["type"] == "flow" and f["steps"] and not f["ordered"]]
    if unordered:
        not_checked.append(f"steps of {len(unordered)} flows have no order in the graph (no step numbers, edges allow several): "
                           f"{', '.join(unordered)}: h3 is the flow name")
    inv["plan"] = plan([k["kind"] for k in kinds], inv, nodes, edges)
    if not graph:
        scan_plan(inv)
    inv["not_checked"] = not_checked
    for k in ("_byid", "_tables", "_fks"):
        del inv[k]
    out.mkdir(parents=True, exist_ok=True)
    mine = facts_for(out, inv)
    facts = {"how": HOW, "facts": mine + keep_facts(out / "facts.json", mine)}
    for name, data_ in (("inventory.json", inv), ("facts.json", facts)):
        (out / name).write_text(json.dumps(data_, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"inventory (templates {ver}): {len(nodes)} nodes, profile {[k['kind'] for k in kinds] or 'none'}, "
          f"{len(inv['plan']['main_flows'])} main flows, {len(inv['plan']['er_areas'])} ER areas -> {rel(out / 'inventory.json')}")
    if inv["stale_files"]:
        print(f"WARN graph is stale: {len(inv['stale_files'])} files changed since it was built "
              f"({', '.join(inv['stale_files'][:5])}{', ...' if len(inv['stale_files']) > 5 else ''}): update the graph, then rerun {HOW}")
    for x in not_checked:
        print("note:", x)


if __name__ == "__main__":
    main()
