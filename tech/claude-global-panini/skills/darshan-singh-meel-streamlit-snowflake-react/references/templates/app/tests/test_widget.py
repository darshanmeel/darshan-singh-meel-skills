"""Python side. AppTest does not render custom components, so the component call is faked."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
import widget  # noqa: E402


def test_app_passes_the_options_and_shows_the_pick():
    with patch.object(widget, "USE_V2", False), patch.object(widget, "_component", return_value="Weekly") as fake:
        at = AppTest.from_file(str(APP / "streamlit_app.py"), default_timeout=10).run()
    assert not at.exception
    assert fake.call_args.kwargs["options"] == ["Daily", "Weekly", "Monthly"]
    assert at.markdown[0].value == "Picked: Weekly"


def test_app_before_the_first_click():
    with patch.object(widget, "USE_V2", False), patch.object(widget, "_component", return_value=None):
        at = AppTest.from_file(str(APP / "streamlit_app.py"), default_timeout=10).run()
    assert at.markdown[0].value == "Picked: nothing yet"


@pytest.mark.skipif(not (widget.DIST / "index.html").exists(), reason="no build: cd component/frontend && npm run build")
def test_static_mount_puts_escaped_args_in_the_page():
    with patch.object(widget.components, "html") as html:
        widget.choice_static(["</script>"], label="Grain")
    page = html.call_args.args[0]
    assert widget.EMPTY_ARGS not in page
    assert '"options": ["\\u003c/script>"]' in page
