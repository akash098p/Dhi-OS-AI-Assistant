"""Dhi — a premium, voice-first AI assistant.

Run with:
    streamlit run app.py
or simply double-click ``Dhi.bat`` on Windows.
"""

from __future__ import annotations

import datetime as dt
import time
import uuid

import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from modules import brain, skills, speech, ui_styles
from modules.webrtc_audio import AudioProcessor

# --------------------------------------------------------------------------- #
#  Page setup & session state
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="DHI OS v3.0",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="expanded",
)
ui_styles.inject_css()


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("messages", [])            # chat history
    ss.setdefault("notes", [])               # voice notes
    ss.setdefault("timers", [])              # [{"label", "end", "duration"}]
    ss.setdefault("command_count", 0)
    ss.setdefault("session_started", dt.datetime.now())
    ss.setdefault("user_name", None)
    ss.setdefault("default_city", None)
    ss.setdefault("autoplay_html", "")       # TTS to play on this render
    ss.setdefault("pending_voice", [])       # voice transcripts awaiting processing
    # Dhi core state
    ss.setdefault("booted", False)           # boot sequence shown once per session
    ss.setdefault("session_id", uuid.uuid4().hex[:6].upper())
    ss.setdefault("last_cmd", None)          # last command executed
    ss.setdefault("last_latency", None)      # last brain.respond latency (ms)
    ss.setdefault("mic_state", "STANDBY")    # STANDBY / CAPTURING / HANDS-FREE
    # settings (widget-backed)
    ss.setdefault("set_voice", True)          # speak replies aloud
    ss.setdefault("set_audio_player", False)  # show replay player in bubbles
    ss.setdefault("set_handsfree", True)      # auto-send utterances after a pause
    ss.setdefault("set_mic", True)            # render the microphone component
    ss.setdefault("set_wake", True)           # strip leading wake word ("alexa")
    ss.setdefault("set_rec_lang", "English (US)")
    ss.setdefault("set_tts_lang", "English (US)")


_init_state()

if not st.session_state.booted:
    ui_styles.render_boot_overlay()
    st.session_state.booted = True


# --------------------------------------------------------------------------- #
#  Command handling
# --------------------------------------------------------------------------- #
MAX_MESSAGES = 80


def _say(spoken: str, display: str, icon: str = "✨") -> None:
    """Append an assistant message (with TTS attached when voice is on).

    Both the spoken reply and the chat-bubble text are translated into the
    selected voice language, so quick-action buttons (time, jokes, weather,
    ...) as well as voice commands come back in that language. Markdown links
    (e.g. weather/news results) are left untouched to keep them intact.
    """
    tts_lang = st.session_state.set_tts_lang
    audio = None
    if st.session_state.set_voice and spoken:
        spoken_tts = speech.translate_text(spoken, tts_lang)
        audio = speech.tts_bytes(spoken_tts, tts_lang)
        if audio:
            st.session_state.autoplay_html = speech.autoplay_html(audio)
    if display and "](" not in display:
        display = speech.translate_text(display, tts_lang)
    st.session_state.messages.append({
        "role": "assistant",
        "content": display,
        "icon": icon,
        "audio": audio,
        "ts": dt.datetime.now().strftime("%H:%M"),
    })
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]


def handle_command(text: str, source: str = "text") -> None:
    """Process one user command end-to-end and refresh the UI."""
    text = (text or "").strip()
    if not text:
        return
    st.session_state.command_count += 1
    st.session_state.messages.append({
        "role": "user",
        "content": text,
        "source": source,
        "ts": dt.datetime.now().strftime("%H:%M"),
    })

    uptime = int((dt.datetime.now() - st.session_state.session_started).total_seconds())
    ctx = {
        "user_name": st.session_state.user_name,
        "notes": st.session_state.notes,
        "default_city": st.session_state.default_city,
        "stats": {
            "uptime": uptime,
            "commands": st.session_state.command_count,
            "notes": len(st.session_state.notes),
            "timers": len(st.session_state.timers),
            "mic": st.session_state.mic_state,
            "lang": st.session_state.set_rec_lang,
            "session_id": st.session_state.session_id,
        },
    }
    t0 = time.perf_counter()
    reply = brain.respond(text, ctx)
    st.session_state.last_latency = round((time.perf_counter() - t0) * 1000)
    st.session_state.last_cmd = text[:40]

    if reply.action == "set_name":
        st.session_state.user_name = reply.data.get("name")
    elif reply.action == "set_timer":
        st.session_state.timers.append({
            "label": reply.data.get("label", "Timer"),
            "end": time.time() + int(reply.data.get("seconds", 0)),
            "duration": int(reply.data.get("seconds", 0)),
        })

    st.session_state.notes = ctx.get("notes", st.session_state.notes)
    _say(reply.spoken, reply.display, reply.icon)
    st.rerun()


def _drain_voice() -> None:
    """Process any transcripts captured by the microphone."""
    for text in st.session_state.pending_voice:
        if text.startswith("[speech service error"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "📡 I couldn't reach the speech service — check your connection.",
                "icon": "📡", "audio": None,
                "ts": dt.datetime.now().strftime("%H:%M"),
            })
            continue
        if not text.strip():
            # STT returned speech but no words — surface feedback so Dhi
            # doesn't look "broken" when she silently hears nothing.
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🤔 I didn't catch that — check your mic/internet or try speaking a bit louder.",
                "icon": "🤔", "audio": None,
                "ts": dt.datetime.now().strftime("%H:%M"),
            })
            continue
        handle_command(text, source="voice")   # reruns internally
    st.session_state.pending_voice = []


def _transcript_markdown() -> str:
    lines = [f"# DHI OS · chat export — {dt.datetime.now():%Y-%m-%d %H:%M}", ""]
    for m in st.session_state.messages:
        who = "🧑 You" if m["role"] == "user" else "🌸 Dhi"
        lines.append(f"**{who}** _({m.get('ts', '')})_:  ")
        lines.append(m["content"].replace("\n", "  \n"))
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Live fragments: voice console & timers
# --------------------------------------------------------------------------- #
RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}


@st.fragment(run_every=0.5)
def voice_panel() -> None:
    """Microphone console — polling fragment so utterances surface hands-free."""
    if not st.session_state.set_mic:
        st.info("🎙️ Microphone is disabled — enable it in the sidebar to talk to me.")
        return

    webrtc_ctx = webrtc_streamer(
        key="dhi-mic",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={
            "video": False,
            "audio": {"echoCancellation": True, "noiseSuppression": True,
                      "autoGainControl": True},
        },
        rtc_configuration=RTC_CONFIG,
        async_processing=True,
    )
    proc = webrtc_ctx.audio_processor
    playing = bool(webrtc_ctx.state.playing)

    if playing and proc:
        rec_lang = speech.RECOGNITION_LANGUAGES.get(st.session_state.set_rec_lang, "en-US")
        proc.configure(rec_lang, st.session_state.set_wake)
        proc.ensure_recording()

        if st.session_state.set_handsfree:
            st.session_state.mic_state = "HANDS-FREE"
            ui_styles.render_listening_orb(
                True, "🎧 Hands-free — call “Dhi” and speak; I send when you pause")
            results = proc.pop_results()
            if results:
                st.session_state.pending_voice = results
                st.rerun(scope="app")
        else:
            st.session_state.mic_state = "CAPTURING"
            ui_styles.render_listening_orb(True, "🎙️ Recording — press **Stop** to send")
    else:
        st.session_state.mic_state = "STANDBY"
        if proc is not None:
            leftover = proc.finalize_now()   # flush push-to-talk / interrupted speech
            if leftover:
                st.session_state.pending_voice = [leftover]
                st.rerun(scope="app")
        hint = ("👋 Tap **Start** and just talk — say **“Dhi”** to get her attention"
                if st.session_state.set_handsfree
                else "👋 Tap **Start**, speak, then tap **Stop**")
        ui_styles.render_listening_orb(False, hint)


@st.fragment(run_every=2)
def timers_fragment() -> None:
    """Live countdown chips + alerts when timers finish."""
    now = time.time()
    active = [t for t in st.session_state.timers if t["end"] > now]
    finished = [t for t in st.session_state.timers if t["end"] <= now]

    if finished:
        st.session_state.timers = active
        for t in finished:
            st.toast(f"⏰ {t['label']} finished!", icon="⏰")
            st.audio(speech.alert_beep(), format="audio/wav")
            label = t["label"] if t["label"] != "Timer" else "your"
            spoken_label = f"your {t['label']}" if t["label"] != "Timer" else "your"
            _say(f"Time's up! {spoken_label} timer has finished.",
                 f"⏰ **Time's up!** The **{label}** timer has finished.", icon="⏰")
        st.rerun(scope="app")
    elif active:
        for t in sorted(active, key=lambda x: x["end"]):
            remaining = max(0, int(t["end"] - now))
            mm, sec = divmod(remaining, 60)
            hh, mm = divmod(mm, 60)
            st.markdown(
                f"<div class='timer-chip'>⏲️ <b>{t['label']}</b> — "
                f"{hh:02d}:{mm:02d}:{sec:02d} remaining</div>",
                unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------- #
#  Sidebar — settings, notes, stats, export
# --------------------------------------------------------------------------- #
with st.sidebar:
    ui_styles.render_mini_hero(st.session_state.user_name)

    ui_styles.render_section("🛰️ Core diagnostics")
    uptime_sec = int((dt.datetime.now() - st.session_state.session_started).total_seconds())
    ui_styles.render_diagnostics(
        session=st.session_state.session_id,
        uptime_sec=uptime_sec,
        commands=st.session_state.command_count,
        mic=st.session_state.mic_state,
        lang=st.session_state.set_rec_lang,
        voice=st.session_state.set_voice,
        last=st.session_state.last_cmd,
    )

    ui_styles.render_section("⚙️ Settings")
    st.toggle("🔊 Speak replies aloud", key="set_voice")
    st.toggle("🎧 Show replay player in bubbles", key="set_audio_player")
    st.toggle("🪄 Hands-free mic (auto-send on pause)", key="set_handsfree",
              help="Finalizes each spoken sentence automatically — no clicking needed.")
    st.toggle("🎙️ Microphone enabled", key="set_mic")
    st.toggle("🧹 Strip wake word (“Dhi”)", key="set_wake",
              help="Also strips “hey dhi”, “ok dhi” — and her old codename “alexa”.")
    st.selectbox("🧠 Understand language", list(speech.RECOGNITION_LANGUAGES),
                 key="set_rec_lang")
    st.selectbox("🗣️ Voice language", list(speech.TTS_LANGUAGES), key="set_tts_lang")

    city_in = st.text_input(
        "🌐 Default weather city",
        value=st.session_state.default_city or "",
        placeholder="Auto-detect (via IP)",
    )
    if city_in.strip():
        st.session_state.default_city = city_in.strip()

    ui_styles.render_section("📝 Quick notes")
    notes = st.session_state.notes
    if notes:
        st.caption(f"{len(notes)} saved — say “show my notes” anytime")
        for note in notes[-5:]:
            st.markdown(f"<div class='note-chip'>📝 {note}</div>", unsafe_allow_html=True)
    else:
        st.caption("Say “take a note that buy milk” to save one.")

    ui_styles.render_section("📊 This session")
    uptime = int((dt.datetime.now() - st.session_state.session_started).total_seconds() // 60)
    ui_styles.render_stats(
        st.session_state.command_count, len(st.session_state.notes),
        len(st.session_state.timers), uptime,
    )

    ui_styles.render_section("✨ What I can do")
    ui_styles.render_capability_list()

    st.markdown("")
    col_a, col_b = st.columns(2)
    if col_a.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.autoplay_html = ""
        st.rerun()
    if st.session_state.messages:
        col_b.download_button(
            "📥 Export chat", data=_transcript_markdown(),
            file_name=f"dhi_chat_{dt.datetime.now():%Y%m%d_%H%M}.md",
            mime="text/markdown", use_container_width=True,
        )

# --------------------------------------------------------------------------- #
#  Main layout
# --------------------------------------------------------------------------- #
ui_styles.render_hero(
    st.session_state.user_name,
    uptime=int((dt.datetime.now() - st.session_state.session_started).total_seconds()),
    commands=st.session_state.command_count,
)

# ---- quick actions -----------------------------------------------------------
ui_styles.render_section("⚡ Quick actions")
QUICK_ACTIONS = [
    ("🕒 Time", "what time is it"),
    ("📅 Date", "what's the date today"),
    ("🌦️ Weather", "weather in London"),
    ("📰 News", "show me the news"),
    ("🧮 Math", "calculate 15 percent of 2400"),
    ("🛰️ Status", "system status"),
    ("😄 Joke", "tell me a joke"),
    ("💡 Fact", "tell me a fun fact"),
    ("💬 Quote", "give me an inspiring quote"),
    ("🪙 Coin", "flip a coin"),
    ("🎲 Dice", "roll a dice"),
    ("❓ Help", "what can you do"),
]
for row_start in range(0, len(QUICK_ACTIONS), 6):
    cols = st.columns(6)
    for col, (label, cmd) in zip(cols, QUICK_ACTIONS[row_start:row_start + 6]):
        if col.button(label, key=f"qa_{label}", use_container_width=True):
            handle_command(cmd, source="quick")

# ---- voice console -----------------------------------------------------------
ui_styles.render_section("🎙️ Voice console")
voice_panel()
if st.session_state.timers:
    timers_fragment()

# ---- chat --------------------------------------------------------------------
ui_styles.render_section("💬 Conversation")
_drain_voice()

if not st.session_state.messages:
    ui_styles.render_empty_state()

for msg in st.session_state.messages:
    avatar = "🧑‍🚀" if msg["role"] == "user" else "🌸"
    with st.chat_message(msg["role"], avatar=avatar):
        if (msg["role"] == "assistant" and msg.get("audio")
                and st.session_state.set_audio_player):
            st.audio(msg["audio"], format="audio/mp3")
        st.markdown(msg["content"])
        ts = msg.get("ts", "")
        st.caption(f"❮ DHI · CORE ❯ {ts}" if msg["role"] == "assistant" else ts)

prompt = st.chat_input(
    "Send a command — “system status”, “weather in Tokyo”, “play some music”…"
)
if prompt:
    now_str = dt.datetime.now().strftime("%H:%M")
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)
        st.caption(now_str)
    ph = st.empty()
    for label in ("ANALYZING", "PROCESSING", "COMPUTING", "EXECUTING"):
        ph.markdown(ui_styles.render_processing(label), unsafe_allow_html=True)
        time.sleep(0.25)
    ph.empty()
    handle_command(prompt, source="text")

# ---- voice replies (auto-play once) -------------------------------------------
if st.session_state.autoplay_html:
    components.html(st.session_state.autoplay_html, height=0)
    st.session_state.autoplay_html = ""

ui_styles.render_footer()



