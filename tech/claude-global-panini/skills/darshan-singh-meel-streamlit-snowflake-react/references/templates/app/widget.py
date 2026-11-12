"""The React widget as typed functions, so pages never touch the component API."""
import json
import os
from pathlib import Path

import streamlit as st
# Import the module: calling st.components.v1.declare_component directly is deprecated.
import streamlit.components.v1 as components

DIST = Path(__file__).parent / "component" / "dist"
DIST_V2 = Path(__file__).parent / "component" / "dist-v2"
# The deploy ships one build per runtime (snowflake.yml artifacts), so the file present picks the mount.
USE_V2 = (DIST_V2 / "widget.js").is_file() and not (DIST / "index.html").is_file()
EMPTY_ARGS = '<script id="args" type="application/json">{}</script>'
# Local hot reload only (npm run dev). Never set in Snowflake, so the committed build is used there.
DEV_URL = os.environ.get("WIDGET_DEV_URL")
_component = (
    components.declare_component("choice", url=DEV_URL)
    if DEV_URL
    else components.declare_component("choice", path=str(DIST))
)


def choice(options: list[str], *, label: str, value: str | None = None, key: str = "choice") -> str | None:
    """One button per option; returns the option clicked last, or None before the first click."""
    if USE_V2:
        return choice_v2(options, label=label, value=value, key=key)
    return _component(options=options, label=label, value=value, key=key, default=None)


def choice_static(options: list[str], *, label: str, value: str | None = None, height: int = 120) -> None:
    """One-way fallback from the same build: the args go into the page, nothing comes back to Python."""
    # "<" escaped so a value can never close the script tag.
    args = json.dumps({"options": options, "label": label, "value": value}).replace("<", "\\u003c")
    page = (DIST / "index.html").read_text(encoding="utf-8")
    components.html(page.replace(EMPTY_ARGS, f'<script id="args" type="application/json">{args}</script>', 1), height=height)


@st.cache_resource
def _v2():
    # A one-line string is read as a file path; the trailing newline marks it as inline code.
    js = (DIST_V2 / "widget.js").read_text(encoding="utf-8") + "\n"
    return st.components.v2.component("choice_v2", html="<div></div>", js=js)


def choice_v2(options: list[str], *, label: str, value: str | None = None, key: str = "choice") -> str | None:
    """Container runtime (v2). Same widget and return value as choice()."""
    result = _v2()(key=key, data={"options": options, "label": label, "value": value},
                   default={"value": value}, on_value_change=lambda: None)
    return result.value
