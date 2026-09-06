"""Offline smoke tests for Dhi's brain, skills and audio pipeline.

Run:  python tests/smoke_test.py
(Network-backed skills are exercised defensively — they assert only what is
guaranteed without internet access.)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from modules import brain, skills, speech  # noqa: E402
from modules.webrtc_audio import AudioProcessor, strip_wake_word  # noqa: E402

PASS, FAIL = 0, []


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS
    if condition:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL.append(name)
        print(f"  XX  {name} {detail}")


print("- speech utilities -")
beep = speech.alert_beep()
check("alert_beep returns WAV bytes", isinstance(beep, bytes) and beep[:4] == b"RIFF")
check("autoplay_html empty-safe", speech.autoplay_html(None) == "")

print("- calculator -")
r = skills.try_calculate("what is 25 times 4")
check("word math (25 times 4 = 100)", r is not None and "100" in r[1], str(r))
r = skills.try_calculate("calculate 15 percent of 2400")
check("percent (15% of 2400 = 360)", r is not None and "360" in r[1], str(r))
r = skills.try_calculate("what is the square root of 144")
check("sqrt (144 -> 12)", r is not None and "12" in r[1], str(r))
r = skills.try_calculate("calculate 2 plus 2")
check("plus (2+2=4)", r is not None and "4" in r[1], str(r))
r = skills.try_calculate("what is (12 + 8) * 3")
check("raw expression ((12+8)*3=60)", r is not None and "60" in r[1], str(r))
check("non-math rejected", skills.try_calculate("what is python") is None)
check("safe_eval power", skills.safe_eval("2**10") == 1024)
check("safe_eval sqrt", skills.safe_eval("sqrt(144)") == 12)
try:
    skills.safe_eval("__import__('os').system('echo hacked')")
    check("safe_eval blocks code injection", False)
except Exception:
    check("safe_eval blocks code injection", True)
check("words_to_numbers", skills.words_to_numbers("twenty one thousand five hundred") == "21500")

print("- durations & units -")
check("parse_duration 5 min", skills.parse_duration("set a timer for 5 minutes") == 300)
check("parse_duration 90 sec", skills.parse_duration("timer 90 seconds") == 90)
check("parse_duration combo", skills.parse_duration("1 hour and 30 minutes") == 5400)
r = skills.try_units("convert 10 km to miles")
check("units km->miles", r is not None and "6.2137" in r[1], str(r))
r = skills.try_units("convert 100 f to c")
check("units f->c", r is not None and "37.78" in r[1], str(r))
check("units rejects non-convert", skills.try_units("10 km to miles") is None)

print("- wake word -")
check("strip 'hey alexa'", strip_wake_word("hey alexa what time is it") == "what time is it")
check("strip 'echo stream'", strip_wake_word("echo stream, play music") == "play music")
check("keeps plain text", strip_wake_word("play echo chamber song") == "play echo chamber song")
check("strip 'dhi' wake", strip_wake_word("dhi what time is it") == "what time is it")
check("strip 'hey dhi'", strip_wake_word("hey dhi, weather in paris") == "weather in paris")
check("bare 'dhi' kept", strip_wake_word("dhi") == "dhi")
check("strip double 'dhi'", strip_wake_word("dhi dhi open youtube") == "open youtube")

print("- brain intents (offline) -")
r = brain.respond("hello", {})
check("greeting", r.icon == "👋")
r = brain.respond("what time is it", {})
check("time", r.icon == "🕒" and "time" in r.spoken.lower())
r = brain.respond("what's the date today", {})
check("date", r.icon == "📅")
r = brain.respond("what can you do", {})
check("capabilities", "Everything I can do" in r.display)

ctx = {"notes": [], "user_name": None, "default_city": None}
r = brain.respond("take a note that buy milk", ctx)
check("note saved", r.action == "add_note" and ctx["notes"] == ["buy milk"])
r = brain.respond("show my notes", ctx)
check("notes listed", "buy milk" in r.display)
r = brain.respond("clear my notes", ctx)
check("notes cleared", r.action == "clear_notes" and ctx["notes"] == [])

r = brain.respond("my name is alex", ctx)
check("name memory", r.action == "set_name" and r.data["name"] == "Alex")
ctx["user_name"] = "Alex"
r = brain.respond("hello", ctx)
check("personalised greeting", "Alex" in r.spoken)

r = brain.respond("dhi", ctx)
check("answers when called ('dhi')", r.icon == "👂" and "listening" in r.display.lower())
r = brain.respond("hey dhi", ctx)
check("'hey dhi' greets", r.icon == "👋")
r = brain.respond("ok dhi", ctx)
check("'ok dhi' attention", r.icon == "👂")
r = brain.respond("who is dhi", ctx)
check("knows herself", "Dhi" in r.display and r.icon == "🤖")
r = brain.respond("dhi, tell me a joke", ctx)
check("'dhi,' prefix stripped", r.icon == "😄")

r = brain.respond("set a timer for 5 minutes", ctx)
check("timer intent", r.action == "set_timer" and r.data["seconds"] == 300)
r = brain.respond("goodbye", ctx)
check("bye", r.action == "goodbye")
r = brain.respond("weather in london", ctx)
check("weather path responds", isinstance(r.display, str) and len(r.display) > 5)
r = brain.respond("open youtube", ctx)
check("open site", "youtube.com" in r.display)
r = brain.respond("search quantum computing", ctx)
check("web search", "google.com/search" in r.display)
r = brain.respond("play bohemian rhapsody", ctx)
check("play music", "youtube.com" in r.display)
r = brain.respond("xyzzy plugh", ctx)
check("fallback gives search links", "google.com/search" in r.display)

print("- audio processor (synthetic frames) -")


class FakeFrame:
    """Mimics av.AudioFrame for recv()."""

    def __init__(self, samples: np.ndarray, rate: int = 48000):
        self._data = samples
        self.sample_rate = rate
        self.samples = samples.size

    def to_ndarray(self, format: str = "s16"):  # noqa: A002
        return self._data.reshape(1, -1)


proc = AudioProcessor()
proc.ensure_recording()
sr_rate = 48000
t = np.linspace(0, 0.1, sr_rate // 10, endpoint=False)
loud = (np.sin(2 * np.pi * 440 * t) * 12000).astype(np.int16).reshape(1, -1)
for _ in range(15):                       # 1.5 s of loud tone
    proc.recv(FakeFrame(loud, sr_rate))
data = proc._take_audio()
check("captures audio while recording", data is not None and len(data) > 10000)
check("buffer drained after take", proc._take_audio() is None)
check("pop_results empty initially", proc.pop_results() == [])
proc.finalize_now()
check("finalize_now stops recording", proc._recording is False)
proc.ensure_recording()
check("restart recording works", proc._recording is True)

print("- format helpers -")
check("format_time tuple", all(isinstance(x, str) for x in skills.format_time()))
check("format_date tuple", all(isinstance(x, str) for x in skills.format_date()))
check("format_day tuple", all(isinstance(x, str) for x in skills.format_day()))
c0 = skills.format_coin()[0]
check("coin", "Heads" in c0 or "Tails" in c0)
d = skills.format_dice()[0]
check("dice in 1..6", any(str(n) in d for n in range(1, 7)))
check("fact non-empty", len(skills.format_fact()[0]) > 20)

print(f"\nResult: {PASS} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)

