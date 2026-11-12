"""Checks the folder build_bundle.py wrote before a deploy: no secrets or stray data, runtime named, PyPI
reachable, files complete, one chunk, no CDN. build_bundle.py imports SECRETS and DATA from here.

    python tools/sis/check_bundle.py [bundle folder]     (default: build/sis under the repo root)

Exit 1 on any ERROR. Stdlib only. Secret-looking files are reported by name and never read.
"""
import fnmatch
import re
import sys
from pathlib import Path

SECRETS = (".env*", "*.pem", "*.key", "*.p8", "*.p12", "*.pfx", "*.jks", "*.keystore", "id_rsa*", "id_dsa*",
           "id_ecdsa*", "id_ed25519*", "credentials*", "*credentials*.json", "*service*account*.json", "secrets*",
           "*.tfvars", "*.tfvars.json", "*.tfstate*", ".npmrc", ".pypirc", ".netrc", ".git-credentials",
           "kubeconfig*", "connections.toml", "profiles.yml")
SECRET_DIRS = (".snowflake", ".ssh", ".aws", ".kube", ".docker", ".gnupg")
# Data travels only through build_bundle.py --data, into data/: every viewer of the app sees all of it.
DATA = ("*.duckdb*", "*.db", "*.sqlite*", "*.parquet", "*.csv")
# Container runtime: the code travels in a message (200 MB default cap there); this keeps start-up fast.
MAX_V2_BYTES = 24 * 1024 * 1024
RUNTIMES = re.compile(r"SYSTEM\$WAREHOUSE_RUNTIME|SYSTEM\$ST_CONTAINER_RUNTIME_PY3_\d+")
CSP = re.compile(r"\beval\s*\(|\bFunction\s*\(")
REMOTE_JS = re.compile(r"""\.?\bsrc\s*=\s*["'](?:https?:)?//|\b(?:import|from)\s*\(?\s*["'](?:https?:)?//""")
REMOTE_CSS = re.compile(r"""url\(\s*["']?(?:https?:)?//|@import""")
PLACEHOLDER = re.compile(r"<[^<>\s][^<>\n]*>")


def is_secret(rel):
    return any(fnmatch.fnmatch(rel.name, p) for p in SECRETS) or any(part in SECRET_DIRS for part in rel.parts)


def check(out):
    errors = []
    files = [p for p in out.rglob("*") if p.is_file()]
    for p in files:
        rel = p.relative_to(out)
        if is_secret(rel):
            errors.append(f"{rel.as_posix()}: secret-looking file in the bundle (not read): remove it")
        elif any(fnmatch.fnmatch(rel.name, p) for p in DATA) and rel.parts[0] != "data":
            errors.append(f"{rel.as_posix()}: data file outside data/: ship data only with --data")
    yml = out / "snowflake.yml"
    text = yml.read_text(encoding="utf-8") if yml.is_file() else ""
    for name in ("snowflake.yml", "environment.yml", "requirements.txt", "pyproject.toml"):
        p = out / name
        if p.is_file() and (m := PLACEHOLDER.search(p.read_text(encoding="utf-8"))):
            errors.append(f"{name} still has the placeholder {m[0]}: fill it in")
    m = re.search(r"^\s*runtime_name:\s*(\S+)", text, re.M)
    if not m:
        return errors + ["snowflake.yml has no runtime_name: leaving it out now means the container runtime"]
    if not RUNTIMES.fullmatch(m[1].strip("'\"")):
        errors.append(f"snowflake.yml runtime_name '{m[1]}' is not a known runtime name")
    if not (out / "streamlit_app.py").is_file():
        errors.append("no streamlit_app.py at the bundle root")
    for p in files:
        rel = p.relative_to(out).as_posix()
        if p.suffix in (".js", ".mjs"):
            code = p.read_text(encoding="utf-8", errors="ignore")
            if CSP.search(code):
                errors.append(f"{rel}: eval() or Function(): the content security policy blocks it")
            if REMOTE_JS.search(code):
                errors.append(f"{rel}: loads a script from another site: bundle it")
        elif p.suffix == ".css" and REMOTE_CSS.search(p.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"{rel}: CSS loads from another site (url() or @import): bundle it")

    if "WAREHOUSE" in m[1]:
        frame = out / "frame"
        if not (out / "environment.yml").is_file():
            errors.append("warehouse runtime needs environment.yml")
        if not (frame / "index.html").is_file():
            return errors + ["warehouse runtime needs frame/index.html (build_bundle.py --runtime warehouse)"]
        html = (frame / "index.html").read_text(encoding="utf-8")
        for ref in re.findall(r'\b(?:src|href|data-bundle)\s*=\s*["\']([^"\']+)', html):
            if re.match(r"(?:https?:)?//", ref):
                errors.append(f"frame/index.html loads '{ref}' from another site: bundle it")
            elif not (frame / ref).is_file():
                errors.append(f"frame/index.html names '{ref}', which is not in frame/")
        for p in frame.rglob("*"):
            rel = p.relative_to(out).as_posix()
            if p.suffix == ".css" and re.search(r"url\(\s*['\"]?/(?!/)", p.read_text(encoding="utf-8")):
                errors.append(f"{rel}: url(/...) is root-relative: the frame has no /assets")
            if p.suffix == ".js" and re.search(r"[\"'`]/assets/", p.read_text(encoding="utf-8", errors="ignore")):
                errors.append(f"{rel}: '/assets/...' is root-relative (a lazy chunk or preload): build one chunk")
    else:
        assets = out / "dist" / "assets"
        js = sorted(assets.glob("*.js"))
        if len(js) != 1 or not js[0].name.startswith("index-") or len(list(assets.glob("index-*.css"))) != 1:
            return errors + ["container runtime needs exactly one JS file (index-*.js) and one index-*.css in dist/assets: no code splitting"]
        code = js[0].read_text(encoding="utf-8")
        # The bundle is wrapped in a function, so module-level import/export would not parse.
        if re.match(r"\s*import\s*[\w{*\"']", code) or re.search(r"\bexport\s*(?:\{|default\b)", code):
            errors.append("dist bundle has import/export at module level: build one chunk with no exports")
        if re.search(r"\bimport\s*\(", code):
            errors.append("dist bundle has a dynamic import(): v2 serves no chunk files")
        for f in ("bridge_core.js", "bridge_container.js"):
            if not (out / f).is_file():
                errors.append(f"container runtime needs {f}")
        if not ((out / "requirements.txt").is_file() or (out / "pyproject.toml").is_file()):
            errors.append("container runtime needs requirements.txt or pyproject.toml")
        if "compute_pool:" not in text:
            errors.append("snowflake.yml has no compute_pool")
        post = out / "post_deploy.sql"
        if "external_access_integrations:" not in text and not (post.is_file() and "ARTIFACT_REPOSITORIES" in post.read_text(encoding="utf-8")):
            errors.append("no PyPI access: add --eai <integration> or the ARTIFACT_REPOSITORIES step (build_bundle.py --pypi-repo)")
        size = sum(f.stat().st_size for f in assets.iterdir())
        if size > MAX_V2_BYTES:
            errors.append(f"dist/assets is {size:,} bytes > {MAX_V2_BYTES:,}: the v2 code travels in one message")
    return errors


def main():
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "build" / "sis"
    errors = check(out)
    for e in errors:
        print("ERROR", e)
    print("bundle OK" if not errors else f"{len(errors)} ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
