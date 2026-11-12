"""A prebuilt React app inside Streamlit in Snowflake. The page's fetch("/api/...") calls come here
through a component and the app's own API answers them in this process: no port, no network.
frame/ present (warehouse runtime) -> v1 component; absent (container runtime) -> v2 component."""
import base64
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from bridge_server import answer, pack

HERE = Path(__file__).resolve().parent
FRAME = HERE / "frame"
ASSETS = HERE / "dist" / "assets"
WORKERS = 4  # about what a browser sends a local server at once
# Writes that are safe for every viewer, e.g. {("POST", "/api/search")}; everything else non-GET -> 409.
ALLOWED_WRITES = frozenset()
PAGE_CSS = """
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: none !important; }
[data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
"""
PAGE_HTML = '<div id="root">Loading…</div><details><summary>Browser checks</summary><pre id="bridge-checks">The bridge has not run.</pre></details>'


@st.cache_resource
def client():
    """The app's ASGI API, called in-process (FastAPI's TestClient needs httpx)."""
    from fastapi.testclient import TestClient

    from api.main import app  # the app's own API module: the folder build_bundle.py --api copied
    return TestClient(app, raise_server_exceptions=False)


# Not ASGI (Flask, plain functions)? Replace this with a dispatcher that returns (status, text, headers).
def call(method, path, body, headers):
    res = client().request(method, path, content=body, headers=headers)
    return res.status_code, res.text, dict(res.headers)


def on_batch():
    """Runs before the fragment reruns: answer the batch, keep the answer for the next render."""
    value = st.session_state["bridge"]
    batch = value if FRAME.exists() else value.batch
    if not batch:
        return
    with ThreadPoolExecutor(WORKERS) as pool:
        responses = list(pool.map(lambda r: answer(r, call, ALLOWED_WRITES), batch["requests"]))
    kept, retry = pack(responses)
    st.session_state["bridge_out"] = {"batch_id": batch["id"], "responses": kept, "retry": retry}


def inline_fonts(css):
    """v2 has no file serving: font files travel inside the stylesheet."""
    def to_data(m):
        data = base64.b64encode((ASSETS / m[1]).read_bytes()).decode("ascii")
        return f"url(data:font/{m[2]};base64,{data})"
    return re.sub(r"url\(\s*['\"]?(?:\.?/)?(?:assets/)?([\w.-]+\.(woff2|woff|ttf))['\"]?\s*\)", to_data, css)


@st.cache_resource
def v2_parts():
    bundle = next(ASSETS.glob("index-*.js")).read_text(encoding="utf-8")
    bridge = "\n".join((HERE / f).read_text(encoding="utf-8") for f in ("bridge_core.js", "bridge_container.js"))
    css = inline_fonts(next(ASSETS.glob("index-*.css")).read_text(encoding="utf-8"))
    # The build runs only when the bridge calls startApp(); newlines mark the strings as inline code.
    return f"function startApp() {{\n{bundle}\n}}\n{bridge}\n", f"{PAGE_CSS}\n{css}\n"


@st.fragment
def view(component):
    # A fragment: answering a batch reruns this, not the whole page.
    out = st.session_state.get("bridge_out")
    if FRAME.exists():
        component(out=out, key="bridge", default=None, on_change=on_batch)
    else:
        component(key="bridge", data={"out": out}, on_batch_change=on_batch)


st.set_page_config(layout="wide")
st.markdown(f"<style>{PAGE_CSS}</style>", unsafe_allow_html=True)
if FRAME.exists():
    view(components.declare_component("spa", path=str(FRAME)))
else:
    js, css = v2_parts()
    # Not isolated: the build looks up #root in the document, as on its own page.
    view(st.components.v2.component("spa", html=PAGE_HTML, css=css, js=js, isolate_styles=False))
