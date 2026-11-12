"""Builds the folder Snowflake gets for a prebuilt React app: shell, bridge, API code, the app's build.

    python tools/sis/build_bundle.py --runtime warehouse|container --database DB --schema SCH --warehouse WH
        [--pool POOL] [--eai INTEGRATION | --pypi-repo] [--api api] [--web-dist web/dist]
        [--include config] [--data FILE] [--root .]

Writes build/sis/ (git-ignore it), rebuilt from scratch, with its own snowflake.yml and post_deploy.sql.
Deploy: cd build/sis && snow streamlit deploy --replace --prune, then run post_deploy.sql.
The app's own build (base "/") is reused as it is: no second Vite config.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_bundle import DATA, SECRET_DIRS, SECRETS  # noqa: E402  one list for building and checking

SKIP = shutil.ignore_patterns(*SECRETS, *SECRET_DIRS, *DATA, "__pycache__", "*.pyc", "node_modules", ".git")
STREAMLIT_CONFIG = '[client]\ntoolbarMode = "minimal"\n\n[browser]\ngatherUsageStats = false\n'
FRAME_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>app</title><link rel="stylesheet" href="assets/{css}"></head>
<body data-bundle="assets/{js}">
<div id="root">Loading…</div>
<details><summary>Browser checks</summary><pre id="bridge-checks">The bridge has not run.</pre></details>
<script src="bridge_core.js"></script>
<script src="bridge_frame.js"></script>
</body>
</html>
"""
YML = """definition_version: 2
entities:
  {app}:
    type: streamlit
    identifier:
      name: {app}
      database: {database}
      schema: {schema}
    query_warehouse: {warehouse}
    runtime_name: {runtime}
{extra}    main_file: streamlit_app.py
    artifacts:
{artifacts}
"""


def check_data(path):
    """Refuse test, demo or fake data, by content (a marker row the fixtures carry), never by file name."""
    raise SystemExit(f"check_data() is not filled in: write the content check for {path.name}, then rerun")


def one(folder, pattern):
    found = sorted(folder.glob(pattern))
    if len(found) != 1:
        raise SystemExit(f"want one {pattern} in {folder}, found {len(found)}: empty the build folder and rebuild")
    return found[0]


def build_frame(assets, frame):
    """v1 serves frame/ as files: index.html, the app's assets, the bridge scripts."""
    shutil.copytree(assets, frame / "assets", ignore=SKIP)
    css, js = one(assets, "index-*.css"), one(assets, "index-*.js")
    # The frame is served under the component's own path, so "/assets/..." would point at the wrong root.
    text = re.sub(r"url\(\s*(['\"]?)/assets/", r"url(\1", css.read_text(encoding="utf-8"))
    (frame / "assets" / css.name).write_text(text, encoding="utf-8")
    (frame / "index.html").write_text(FRAME_HTML.format(css=css.name, js=js.name), encoding="utf-8")
    for name in ("bridge_core.js", "bridge_frame.js"):
        shutil.copy2(HERE / name, frame / name)


def build(root, runtime, pool="<compute_pool>", api="api", web_dist="web/dist", include=(), data=(), eai=None,
          pypi_repo=False, database="<db>", schema="<schema>", warehouse="<app_wh>", app="spa_app"):
    out = root / "build" / "sis"
    if out.exists():
        shutil.rmtree(out)  # files from an older build or the other runtime must not ship
    out.mkdir(parents=True)
    for name in ("streamlit_app.py", "bridge_server.py"):
        shutil.copy2(HERE / name, out / name)
    shutil.copytree(root / api, out / Path(api).name, ignore=SKIP)
    # Config the API reads (thresholds, masking): what viewers can't change ships as files.
    for extra in ((root / "config",) if (root / "config").is_dir() else ()) + tuple(root / i for i in include):
        copy = shutil.copytree if extra.is_dir() else shutil.copy2
        copy(extra, out / extra.relative_to(root), **({"ignore": SKIP} if extra.is_dir() else {}))
    for f in map(Path, data):
        check_data(f)
        (out / "data").mkdir(exist_ok=True)
        shutil.copy2(f, out / "data" / f.name)
    (out / ".streamlit").mkdir()
    (out / ".streamlit" / "config.toml").write_text(STREAMLIT_CONFIG, encoding="utf-8")
    assets = root / web_dist / "assets"
    post = [f"-- Confirm the runtime the app got (read-only):\nDESCRIBE STREAMLIT {database}.{schema}.{app};"]
    if runtime == "warehouse":
        shutil.copy2(HERE / "environment.yml", out / "environment.yml")
        build_frame(assets, out / "frame")
        name, extra = "SYSTEM$WAREHOUSE_RUNTIME", ""
    else:
        shutil.copy2(HERE / "requirements.txt", out / "requirements.txt")
        one(assets, "index-*.js"), one(assets, "index-*.css")
        shutil.copytree(assets, out / "dist" / "assets", ignore=SKIP)
        for f in ("bridge_core.js", "bridge_container.js"):
            shutil.copy2(HERE / f, out / f)
        name, extra = "SYSTEM$ST_CONTAINER_RUNTIME_PY3_11", f"    compute_pool: {pool}\n"
        if eai:
            extra += f"    external_access_integrations:\n      - {eai}\n"
        if pypi_repo:
            post.insert(0, f"-- PyPI installs through the shared repository:\nALTER STREAMLIT {database}.{schema}.{app} "
                           "SET ARTIFACT_REPOSITORIES = (snowflake.snowpark.pypi_shared_repository);")
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in out.iterdir())
    # Named for both runtimes: leaving it out now means the container runtime.
    (out / "snowflake.yml").write_text(YML.format(
        app=app, database=database, schema=schema, warehouse=warehouse, runtime=name, extra=extra,
        artifacts="\n".join(f"      - {e}" for e in entries)), encoding="utf-8")
    # Not an artifact: the user runs it after the deploy.
    (out / "post_deploy.sql").write_text("\n\n".join(post) + "\n", encoding="utf-8")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runtime", choices=("warehouse", "container"), default="warehouse")
    for name, default in (("--database", "<db>"), ("--schema", "<schema>"), ("--warehouse", "<app_wh>"),
                          ("--pool", "<compute_pool>"), ("--app", "spa_app"), ("--api", "api"), ("--web-dist", "web/dist")):
        p.add_argument(name, default=default)
    p.add_argument("--eai", help="external access integration for PyPI (container runtime)")
    p.add_argument("--pypi-repo", action="store_true", help="write the ARTIFACT_REPOSITORIES step into post_deploy.sql")
    p.add_argument("--include", action="append", default=[], help="extra file or folder to ship (code, config; never data)")
    p.add_argument("--data", action="append", default=[], help="a data file to ship into data/, after check_data()")
    p.add_argument("--root", type=Path, default=HERE.parents[1], help="the repo root")
    a = p.parse_args()
    root = a.root.resolve()
    out = build(root, a.runtime, a.pool, a.api, a.web_dist, a.include, a.data, a.eai, a.pypi_repo,
                a.database, a.schema, a.warehouse, a.app)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) / 1048576
    print(f"{out.relative_to(root).as_posix()} ({size:.1f} MB); check: python tools/sis/check_bundle.py")


if __name__ == "__main__":
    main()
