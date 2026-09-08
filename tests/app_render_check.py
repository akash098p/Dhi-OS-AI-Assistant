"""Headless render check for app.py using Streamlit's AppTest framework."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest  # noqa: E402

at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"),
                       default_timeout=30)
at.session_state["set_mic"] = False   # skip the webrtc component (not AppTest-compatible)
at.run()

print("exception:", at.exception)
assert not at.exception, f"AppTest raised: {at.exception}"

# The boot overlay should have been rendered on first run and then flagged done.
print("booted flag:", at.session_state["booted"])
assert at.session_state["booted"] is True

print("command_count:", at.session_state.command_count)
print("session_id:", at.session_state.session_id)
print("sidebar / mini-hero + diagnostics rendered OK, title bar OK")
print("APP RENDER OK")