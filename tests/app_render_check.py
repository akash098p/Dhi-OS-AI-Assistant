"""Headless render + interaction checks for app.py using Streamlit's AppTest."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app.py")

at = AppTest.from_file(APP, default_timeout=30)
at.session_state["set_mic"] = False    # skip the webrtc component (not AppTest-compatible)
at.session_state["set_voice"] = False  # skip network TTS in tests
at.run()

print("exception:", at.exception)
assert not at.exception, f"AppTest raised: {at.exception}"

# The boot overlay should have been rendered on first run and then flagged done.
print("booted flag:", at.session_state["booted"])
assert at.session_state["booted"] is True

print("command_count:", at.session_state.command_count)
print("session_id:", at.session_state.session_id)

# ---- typed command reaches the conversation --------------------------------
n0 = len(at.session_state["messages"])
at.chat_input[0].set_value("what time is it").run()
assert not at.exception, f"chat run raised: {at.exception}"
msgs = at.session_state["messages"]
assert len(msgs) >= n0 + 2, "expected user + assistant messages after typed command"
assert msgs[-1]["role"] == "assistant"
print("typed command OK ->", len(msgs), "messages")

# ---- queued voice transcript is drained into the conversation ---------------
at2 = AppTest.from_file(APP, default_timeout=30)
at2.session_state["set_mic"] = False
at2.session_state["set_voice"] = False
at2.session_state["pending_voice"] = ["dhi"]
at2.run()
assert not at2.exception, f"voice-drain run raised: {at2.exception}"
vmsgs = at2.session_state["messages"]
assert at2.session_state["pending_voice"] == [], "pending_voice not drained"
assert any("listening" in m["content"].lower() for m in vmsgs), \
    "expected the attention reply for the 'dhi' call"
assert at2.session_state["last_heard"] == "dhi"
print("voice drain OK ->", len(vmsgs), "messages, last_heard:",
      at2.session_state["last_heard"])

print("APP RENDER + INTERACTION OK")