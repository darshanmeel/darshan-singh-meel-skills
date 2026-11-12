"""Tests for this skill: the templates hold the rules, and check_dist.py / check_bundle.py catch each failure.
Usage: python tests/run.py (stdlib; git for the source-hash cases, node for the bridge case)"""
import importlib.util
import json
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ in the templates folder
SKILL = Path(__file__).resolve().parents[1]
APP = SKILL / "references" / "templates" / "app"
FRONT = APP / "component" / "frontend"
SPA = SKILL / "references" / "templates" / "spa"
spec = importlib.util.spec_from_file_location("check_dist", APP / "tools" / "check_dist.py")
check_dist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_dist)
sys.path.insert(0, str(SPA))
import bridge_server  # noqa: E402
import build_bundle  # noqa: E402
import check_bundle  # noqa: E402

GIT = shutil.which("git") is not None
TMP = Path(tempfile.mkdtemp())
fails = []


def ok(cond, name, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond or not detail else f" -> {detail}"))
    if not cond:
        fails.append(name)


def text(p):
    return p.read_text(encoding="utf-8")


def tmpdir():
    return Path(tempfile.mkdtemp(dir=TMP))


def fill(p):
    """Placeholders filled the way a real project would."""
    p.write_text(re.sub(r"<x\.y\.z>", "1.0.0", re.sub(r"<(\w+)>", r"my_\1", text(p))), encoding="utf-8")


def make_app(git=True, page=None, yml=None, v2=None):
    """A copy of the template app with a synthetic one-file build stamped with the source hash."""
    d = tmpdir()
    shutil.copytree(APP, d, dirs_exist_ok=True)
    for name in ("snowflake.yml", "environment.yml"):
        fill(d / name)
    if git:
        for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "t"]):
            subprocess.run(["git", "-c", "core.autocrlf=false", *cmd], cwd=d, check=True, capture_output=True)
    h = check_dist.source_hash(d / "component" / "frontend") or "0" * 16
    body = page or '<script type="module">console.log(1)</script><style>a{color:red}</style>'
    (d / "component" / "dist").mkdir(parents=True, exist_ok=True)
    (d / "component" / "dist" / "index.html").write_text(
        f'<!doctype html><html><head><meta name="source-hash" content="{h}">{body}</head><body></body></html>', encoding="utf-8")
    if v2 is not None:
        (d / "component" / "dist-v2").mkdir(parents=True, exist_ok=True)
        (d / "component" / "dist-v2" / "widget.js").write_text(v2.replace("HASH", h), encoding="utf-8")
    if yml is not None:
        (d / "snowflake.yml").write_text(yml, encoding="utf-8")
    return d


def errors_of(d):
    return " | ".join(check_dist.check(d)[0])


# Templates hold the rules.
vite = text(FRONT / "vite.config.ts")
ok('base: "./"' in vite, "vite: relative base")
ok('outDir: "../dist"' in vite and "emptyOutDir: true" in vite, "vite: builds into component/dist, emptied first")
ok("inlineAll()" in vite and "source-hash" in vite, "vite: inlines the bundle and stamps the source hash")
ok("!file.isEntry" in vite and "throw new Error" in vite, "vite: a second chunk stops the build")
ok("assetsInlineLimit" in vite and "cssCodeSplit: false" in vite, "vite: fonts/images and CSS inlined")
v2cfg = text(FRONT / "vite.v2.config.ts")
ok('"process.env.NODE_ENV"' in v2cfg and 'formats: ["es"]' in v2cfg, "vite.v2: defines NODE_ENV, one ES module")
ok("source-hash:" in v2cfg and "sourceHash()" in v2cfg, "vite.v2: stamps the source hash as a banner")
pkg = json.loads(text(FRONT / "package.json"))
ok({"build", "build:v2", "test", "dev"} <= set(pkg["scripts"]), "package.json: dev, build, build:v2, test scripts")
ok(not re.search(r"https?://", text(FRONT / "index.html")), "index.html: no external URL")
ok('<script id="args" type="application/json">{}</script>' in text(FRONT / "index.html"), "index.html: args placeholder")
css = text(FRONT / "src" / "widget.css")
ok(".widget,\n.note {" in css and "var(--st-primary-color," in css and ":root {" not in css, "widget.css: theme vars on the widget, not :root")
ok("--st-primary-color" in text(FRONT / "src" / "main.tsx"), "main.tsx: v1 theme written as the v2 variable names")
widget = text(APP / "widget.py")
ok("EMPTY_ARGS = '<script id=\"args\" type=\"application/json\">{}</script>'" in widget, "widget.py: placeholder matches index.html")
ok('declare_component("choice", path=' in widget and "import streamlit.components.v1 as components" in widget,
   "widget.py: declares through the imported module, from the build path")
ok("USE_V2 =" in widget and "if USE_V2:" in widget, "widget.py: picks v1 or v2 by the build present")
ok('+ "\\n"' in widget and "on_value_change" in widget, "widget.py: v2 js passed inline, state callback set")
yml = text(APP / "snowflake.yml")
ok("runtime_name: SYSTEM$WAREHOUSE_RUNTIME" in yml, "snowflake.yml: warehouse runtime set explicitly")
ok(check_dist.artifacts(APP / "snowflake.yml") == ["streamlit_app.py", "widget.py", "environment.yml", "component/dist/index.html"],
   "snowflake.yml: artifacts parsed")
ok("channels:\n  - snowflake" in text(APP / "environment.yml"), "environment.yml: snowflake channel only")
for py in [APP / "widget.py", APP / "streamlit_app.py", APP / "tools" / "check_dist.py", APP / "tests" / "test_widget.py",
           SPA / "streamlit_app.py", SPA / "build_bundle.py", SPA / "check_bundle.py", SPA / "bridge_server.py"]:
    try:
        py_compile.compile(str(py), cfile=str(TMP / "x.pyc"), doraise=True)
        ok(True, f"compiles: {py.parent.name}/{py.name}")
    except py_compile.PyCompileError as e:
        ok(False, f"compiles: {py.name}", str(e))

# check_dist catches each failure.
W = "entities:\n  a:\n    runtime_name: SYSTEM$WAREHOUSE_RUNTIME\n    artifacts:\n      - component/dist/index.html\n"
C = "entities:\n  a:\n    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11\n    artifacts:\n      - component/dist-v2/widget.js\n"
CASES = [  # (name, app kwargs, text expected in the errors; "" = no error)
    ("good build", {}, ""),
    ("good build, both runtimes built, container deploy", {"v2": "/*! source-hash: HASH */\nexport{a as default};", "yml": C}, ""),
    ("external script", {"page": '<script src="https://cdn.example.com/x.js"></script>'}, "loads from another site"),
    ("separate bundle file", {"page": '<script type="module" src="./assets/index-a1.js"></script>'}, "the build must inline everything"),
    ("CDN font in CSS", {"page": "<style>@font-face{src:url(https://fonts.example.com/f.woff2)}</style>"}, "loads from another site"),
    ("@import font CSS", {"page": '<style>@import "https://fonts.example.com/css";</style>'}, "loads from another site"),
    ("script created at runtime with a CDN src", {"page": '<script type="module">s.src="https://cdn.example.com/x.js"</script>'}, "loads from another site"),
    ("eval", {"page": '<script type="module">eval("1")</script>'}, "eval()"),
    ("plain Function(", {"page": "<script type=\"module\">Function('return this')()</script>"}, "Function()"),
    ("too big", {"page": "<style>" + "a" * (check_dist.MAX_BYTES + 1) + "</style>"}, "bytes >"),
    ("stale v2 build", {"v2": "/*! source-hash: 0000000000000000 */\nexport{a as default};"}, "dist-v2/widget.js is stale" if GIT else ""),
    ("v2 build without a stamp", {"v2": "export default function(){}"}, "dist-v2/widget.js has no source-hash"),
    ("font url() in widget.js", {"v2": '/*! source-hash: HASH */\nconst f="@font-face{src:url(https://fonts.example.com/x.woff2)}";'}, "widget.js loads from another site"),
    ("oversized widget.js", {"v2": "/*! source-hash: HASH */\n/*" + "a" * (check_dist.MAX_BYTES + 1) + "*/"}, "widget.js is"),
    ("dist not deployed", {"yml": "entities:\n  a:\n    runtime_name: SYSTEM$WAREHOUSE_RUNTIME\n    artifacts:\n      - streamlit_app.py\n"}, "artifacts miss"),
    ("frontend deployed", {"yml": W + "      - component/\n"}, "uploads the frontend source"),
    ("'component/**' glob", {"yml": W.replace("component/dist/index.html", "component/**")}, "uploads the frontend source"),
    ("'**/*' glob", {"yml": W + "      - '**/*'\n"}, "uploads the frontend source"),
    ("src: frontend/src + dest", {"yml": W + "      - src: component/frontend/src\n        dest: src\n"}, "uploads the frontend source"),
    ("src/dest form of the build", {"yml": W.replace("- component/dist/index.html", "- src: component/dist/index.html\n        dest: component/dist/index.html")}, ""),
    ("both builds shipped", {"yml": W + "      - component/dist-v2/widget.js\n"}, "also ships component/dist-v2/widget.js"),
    ("container without the v2 build", {"yml": C.replace("dist-v2/widget.js", "dist/index.html")}, "miss component/dist-v2/widget.js"),
    ("runtime not named", {"yml": W.replace("    runtime_name: SYSTEM$WAREHOUSE_RUNTIME\n", "")}, "no runtime_name"),
    ("runtime name misspelt", {"yml": W.replace("SYSTEM$WAREHOUSE_RUNTIME", "SYSTEM$WAREHOUSE")}, "not a known runtime name"),
    ("placeholder left", {"yml": W.replace("entities:", "entities:\n  b:\n    query_warehouse: <app_wh>")}, "placeholder <app_wh>"),
]
for name, kw, want in CASES:
    errs = errors_of(make_app(git=GIT, **kw))
    ok((want in errs) if want else errs == "", f"check_dist: {name}", errs)

d = make_app(git=GIT)
shutil.rmtree(d / "component" / "dist")
ok("no build" in errors_of(d), "check_dist: missing build")
for name, src in (("hard-coded url=", 'c.declare_component("x", url="http://localhost:5173")'),
                  ("dev url as env default", 'U = os.environ.get("WIDGET_DEV_URL", "http://localhost:5173")'),
                  ("dev url via constant", 'DEV_URL = "http://127.0.0.1:5173"')):
    d = make_app(git=GIT)
    (d / "widget.py").write_text(src + "\n", encoding="utf-8")
    ok("localhost dev URL" in errors_of(d), f"check_dist: {name}")
d = make_app(git=GIT)
shutil.copy2(APP / "environment.yml", d / "environment.yml")
ok("placeholder <x.y.z>" in errors_of(d), "check_dist: unpinned environment.yml")

if GIT:
    d = make_app()
    (d / "component" / "frontend" / "src" / "Widget.tsx").write_text("// changed\n", encoding="utf-8")
    ok("stale" in errors_of(d), "check_dist: source changed without a rebuild")
    d = make_app()
    p = d / "component" / "frontend" / "src" / "Widget.tsx"
    p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    ok(errors_of(d) == "", "check_dist: CRLF checkout hashes the same")
else:
    print("SKIP source-hash cases: git not on PATH")
errs, notes = check_dist.check(make_app(git=False))
ok(errs == [] and any("skip source-hash" in n for n in notes), "check_dist: no git -> hash check skipped, not failed", errs)

# SPA mode: server half.
req = lambda i, m="GET", p="/api/x": {"id": i, "method": m, "path": p}
api = lambda status, body: (lambda *a: (status, body, {"content-type": "application/json", "content-length": "9"}))
r = bridge_server.answer(req(1), api(200, '{"a":1}'))
ok(r["status"] == 200 and "content-length" not in r["headers"], "server: answers GET, drops length headers")
ok(bridge_server.answer(req(2, "PUT", "/api/settings?x=1"), api(200, ""))["status"] == 409, "server: write -> 409 when hosted")
ok(bridge_server.answer(req(3, "POST", "/api/search"), api(200, "[]"), {("POST", "/api/search")})["status"] == 200,
   "server: allowed write passes")


def boom(*a):
    raise ValueError("secret detail")


r = bridge_server.answer(req(4), boom)
ok(r["status"] == 500 and "secret detail" not in r["body"], "server: error -> 500 with the type only")
big = lambda i, n: {"id": i, "path": "/api/x", "status": 200, "headers": {}, "body": "x" * n}
kept, retry = bridge_server.pack([big(1, 10), big(2, 10), big(3, 10)], max_bytes=160)
ok([k["id"] for k in kept] == [1, 2] and retry == [3], "server: over the cap -> rest retried next batch")
kept, retry = bridge_server.pack([big(1, 500)], max_bytes=250)
ok(kept[0]["status"] == 413 and retry == [], "server: one response too large alone -> 413")

# SPA mode: bundle builder and check.
PLANTED = [".env", "deploy_key.p8", "secrets.toml", ".npmrc", ".pypirc", ".netrc", ".git-credentials", "id_ecdsa",
           "kubeconfig", "gcp-service-account.json", "app-credentials.json", "terraform.tfstate", "prod.tfvars",
           "store.jks", "app.keystore", "profiles.yml", "credentials.ini", "data.duckdb", "rows.csv"]


def make_repo():
    root = tmpdir()
    (root / "api" / "sub").mkdir(parents=True)
    (root / "api" / "main.py").write_text("app = None\n", encoding="utf-8")
    for planted in PLANTED:
        (root / "api" / "sub" / planted).write_text("<redacted>\n", encoding="utf-8")
    (root / "api" / ".snowflake").mkdir()
    (root / "api" / ".snowflake" / "connections.toml").write_text("<redacted>\n", encoding="utf-8")
    (root / "config").mkdir()
    (root / "config" / "settings.yml").write_text("mask: true\n", encoding="utf-8")
    a = root / "web" / "dist" / "assets"
    a.mkdir(parents=True)
    (a / "index-a1.js").write_text('const x=1;fetch("/api/x");', encoding="utf-8")
    (a / "index-a1.css").write_text("@font-face{src:url(/assets/f-b2.woff2)}", encoding="utf-8")
    (a / "f-b2.woff2").write_bytes(b"\x00font")
    return root


NAMES = dict(database="my_db", schema="my_schema", warehouse="my_wh")


def bundle(runtime, plant=None, **kw):
    root = make_repo()
    if plant:
        plant(root)
    out = build_bundle.build(root, runtime, "my_pool", **{**NAMES, **kw})
    for name in ("environment.yml", "requirements.txt"):
        if (out / name).is_file():
            fill(out / name)
    return out


for runtime, kw in (("warehouse", {}), ("container", {"eai": "pypi_eai"}), ("container", {"pypi_repo": True})):
    out = bundle(runtime, **kw)
    errs = check_bundle.check(out)
    ok(errs == [], f"bundle {runtime} {kw}: builds clean", errs)
    shipped = {p.name for p in out.rglob("*")}
    ok(not shipped & {*PLANTED, "connections.toml"}, f"bundle {runtime}: no planted secret or data file shipped", shipped & {*PLANTED, "connections.toml"})
    ok((out / "config" / "settings.yml").is_file() and (out / ".streamlit" / "config.toml").is_file(), f"bundle {runtime}: config and .streamlit shipped")
    yml_text = text(out / "snowflake.yml")
    ok(("SYSTEM$WAREHOUSE_RUNTIME" if runtime == "warehouse" else "compute_pool: my_pool") in yml_text,
       f"bundle {runtime}: runtime named in snowflake.yml")
    ok("post_deploy.sql" not in yml_text and "DESCRIBE STREAMLIT my_db.my_schema.spa_app" in text(out / "post_deploy.sql"),
       f"bundle {runtime}: post_deploy.sql confirms the runtime, not deployed")

out = bundle("warehouse")
ok("url(f-b2.woff2)" in text(out / "frame" / "assets" / "index-a1.css"), "bundle warehouse: CSS url rewritten relative")
ok('data-bundle="assets/index-a1.js"' in text(out / "frame" / "index.html"), "bundle warehouse: frame names the bundle")
(out / "frame" / "assets" / "index-a1.css").write_text("a{background:url(/assets/x.png)}", encoding="utf-8")
(out / "frame" / "index.html").write_text(text(out / "frame" / "index.html").replace("bridge_core.js", "https://cdn.example.com/x.js"), encoding="utf-8")
(out / "api" / "id_ed25519").write_text("<redacted>\n", encoding="utf-8")
(out / "api" / "dump.parquet").write_text("x", encoding="utf-8")
(out / "frame" / "assets" / "index-a1.js").write_text('import("/assets/Chart-a1.js")', encoding="utf-8")
errs = " | ".join(check_bundle.check(out))
for want in ("url(/...) is root-relative", "another site", "secret-looking", "data file outside data/", "'/assets/...' is root-relative"):
    ok(want in errs, f"check_bundle warehouse: planted '{want}' caught", errs)

PLANTS = [  # (name, runtime, plant on the bundle, expected error)
    ("module-level export", "container", lambda o: (o / "dist/assets/index-a1.js").write_text("export default 1;"), "import/export at module level"),
    ("dynamic import()", "container", lambda o: (o / "dist/assets/index-a1.js").write_text('import("./c.js")'), "dynamic import()"),
    ("second chunk file", "container", lambda o: (o / "dist/assets/Chart-a1.js").write_text("1"), "exactly one JS file"),
    ("external CSS on container", "container", lambda o: (o / "dist/assets/index-a1.css").write_text("@import url(https://x.example.com/a.css);"), "CSS loads from another site"),
    ("CDN src in JS", "container", lambda o: (o / "dist/assets/index-a1.js").write_text('s.src="https://cdn.example.com/x.js"'), "loads a script from another site"),
    ("eval", "container", lambda o: (o / "dist/assets/index-a1.js").write_text('eval("1")'), "eval()"),
    ("no compute_pool", "container", lambda o: (o / "snowflake.yml").write_text(text(o / "snowflake.yml").replace("    compute_pool: my_pool\n", "")), "no compute_pool"),
    ("unpinned requirements", "container", lambda o: shutil.copy2(SPA / "requirements.txt", o / "requirements.txt"), "placeholder <x.y.z>"),
    ("runtime misspelt", "warehouse", lambda o: (o / "snowflake.yml").write_text(text(o / "snowflake.yml").replace("SYSTEM$WAREHOUSE_RUNTIME", "SYSTEM$WAREHOUSE")), "not a known runtime name"),
    ("runtime not named", "warehouse", lambda o: (o / "snowflake.yml").write_text("entities: {}\n"), "no runtime_name"),
    ("frame names a missing bundle", "warehouse", lambda o: (o / "frame/assets/index-a1.js").unlink(), "which is not in frame/"),
]
for name, runtime, plant, want in PLANTS:
    out = bundle(runtime, eai="pypi_eai")
    plant(out)
    errs = " | ".join(check_bundle.check(out))
    ok(want in errs, f"check_bundle {runtime}: {name}", errs)
out = bundle("container")
ok("no PyPI access" in " | ".join(check_bundle.check(out)), "check_bundle container: no EAI and no artifact repository")
out = build_bundle.build(make_repo(), "warehouse")
ok("placeholder <" in " | ".join(check_bundle.check(out)), "check_bundle: template default names left as placeholders")
try:
    bundle("warehouse", data=[str(make_repo() / "api" / "sub" / "data.duckdb")])
    ok(False, "build_bundle: --data stops until check_data() is filled in")
except SystemExit as e:
    ok("check_data() is not filled in" in str(e), "build_bundle: --data stops until check_data() is filled in")
try:
    bundle("container", plant=lambda r: (r / "web/dist/assets/index-b2.js").write_text("1"))
    ok(False, "build_bundle: two entry bundles stop the build")
except SystemExit:
    ok(True, "build_bundle: two entry bundles stop the build")

NODE_TEST = r"""
const fs = require("fs");
const sent = [];
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, addEventListener: () => {} };
window.addEventListener = () => {};
window.fetch = async () => "real";
eval(fs.readFileSync(process.argv[2], "utf8") + ";globalThis.makeBridge = makeBridge;");
const b = makeBridge();
b.send = (name, v) => sent.push(v);
(async () => {
  const p1 = fetch("/api/a"), p2 = fetch("/api/b", { method: "post" });
  const other = await fetch("https://example.com/x");
  await new Promise((r) => setTimeout(r, 40));
  if (other !== "real" || sent.length !== 1 || sent[0].requests.length !== 2 || sent[0].requests[1].method !== "POST") throw "batch";
  b.receive({ batch_id: 99, responses: [], retry: [] });
  b.receive({ batch_id: sent[0].id, responses: [{ id: 1, path: "/api/a", status: 200, headers: {}, body: "{\"ok\":1}" }], retry: [2] });
  if ((await (await p1).json()).ok !== 1) throw "resolve";
  await new Promise((r) => setTimeout(r, 40));
  if (sent.length !== 2 || sent[1].requests.length !== 1 || sent[1].requests[0].id !== 2) throw "retry";
  b.receive({ batch_id: sent[1].id, responses: [{ id: 2, path: "/api/b", status: 204, headers: {}, body: "" }], retry: [] });
  if ((await p2).status !== 204) throw "no body";
  console.log("ok");
  process.exit(0);
})().catch((e) => { console.log("fail " + e); process.exit(1); });
"""
if shutil.which("node"):
    js = TMP / "t.cjs"
    js.write_text(NODE_TEST, encoding="utf-8")
    r = subprocess.run(["node", str(js), str(SPA / "bridge_core.js")], capture_output=True, text=True, timeout=60)
    ok(r.stdout.strip() == "ok", "bridge_core.js: batches, ignores stale answers, resolves, retries, empty body", r.stdout + r.stderr)
else:
    print("SKIP bridge_core.js: node not on PATH")

# SKILL.md form.
skill = text(SKILL / "SKILL.md")
desc = re.search(r"^description:\s*(.+)$", skill, re.M)[1]
ok(len(desc) <= 1024, f"description {len(desc)} chars <= 1024")
ok(": " not in desc and not desc.startswith(("'", '"', "[", "{")), "description is a plain YAML scalar (no ': ')")
body = skill.split("---", 2)[2]
ok(len(body.strip().splitlines()) <= 120, f"body {len(body.strip().splitlines())} lines <= 120")
for ref in sorted(set(re.findall(r"`references/([\w./-]+)`", skill))):
    ok((SKILL / "references" / ref).exists(), f"SKILL.md names an existing file: references/{ref}")

shutil.rmtree(TMP, ignore_errors=True)
print(f"{len(fails)} failed" if fails else "all passed")
sys.exit(1 if fails else 0)
