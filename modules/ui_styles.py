"""Premium UI layer for Dhi — theming, animations, custom components."""

import streamlit as st

_CSS_PART1 = """
<style>
/* ============ fonts & base ============ */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, li, span {
    font-family: 'Outfit', 'Segoe UI', system-ui, sans-serif;
}
.stApp {
    background:
        radial-gradient(1100px 520px at 10% -10%, rgba(124, 92, 255, .22), transparent 60%),
        radial-gradient(900px 480px at 108% 8%, rgba(0, 209, 255, .15), transparent 55%),
        radial-gradient(760px 520px at 50% 118%, rgba(255, 94, 177, .12), transparent 62%),
        #070a16;
    color: #e8ecf8;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
a { color: #8fd3ff; }
h1, h2, h3, h4 { font-weight: 700; letter-spacing: .2px; }
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(13, 18, 38, .9) !important;
    border: 1px solid rgba(124, 92, 255, .25);
    border-radius: 10px;
}

/* ============ scrollbar ============ */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: linear-gradient(#7c5cff, #00d1ff); border-radius: 99px; }

/* ============ sidebar ============ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(17, 22, 44, .96), rgba(8, 11, 24, .98));
    border-right: 1px solid rgba(255, 255, 255, .07);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }

/* ============ glass chat ============ */
[data-testid="stChatMessage"] {
    background: linear-gradient(150deg, rgba(255, 255, 255, .065), rgba(255, 255, 255, .02));
    border: 1px solid rgba(255, 255, 255, .09);
    border-radius: 18px;
    padding: 12px 16px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, .28);
    backdrop-filter: blur(12px);
    margin-bottom: 6px;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    font-size: .98rem;
    line-height: 1.55;
}
[data-testid="stChatMessage"] table { border-collapse: collapse; width: 100%; font-size: .92rem; }
[data-testid="stChatMessage"] th, [data-testid="stChatMessage"] td {
    border: 1px solid rgba(255, 255, 255, .12) !important;
    padding: 6px 10px !important;
    background: rgba(255, 255, 255, .03) !important;
}
[data-testid="stChatMessage"] blockquote {
    border-left: 3px solid #7c5cff;
    padding: 4px 12px;
    color: #cfd6ee;
    background: rgba(124, 92, 255, .08);
    border-radius: 0 10px 10px 0;
}
[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, .07) !important;
    border: 1px solid rgba(255, 255, 255, .14) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
}

/* ============ buttons ============ */
.stButton > button, .stDownloadButton > button {
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, .14);
    background: linear-gradient(135deg, rgba(124, 92, 255, .16), rgba(0, 209, 255, .12));
    color: #e8ecf8;
    font-weight: 600;
    font-size: .88rem;
    padding: 6px 14px;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(124, 92, 255, .7);
    box-shadow: 0 10px 26px rgba(124, 92, 255, .35);
    color: #fff;
}

/* ============ hero ============ */
.hero { text-align: center; padding: 10px 0 2px; }
.hero-badge {
    display: inline-block; font-size: .74rem; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; color: #b9a8ff;
    border: 1px solid rgba(124, 92, 255, .45); border-radius: 999px;
    padding: 5px 14px; margin-bottom: 12px;
    background: rgba(124, 92, 255, .12);
    animation: floaty 4s ease-in-out infinite;
}
.hero h1 { font-size: clamp(2rem, 5vw, 3.1rem); margin: 0 0 6px; font-weight: 800; }
.hero p { color: #a6b0cf; font-size: 1.02rem; margin: 0; }
.grad {
    background: linear-gradient(92deg, #9d7bff 0%, #00d1ff 55%, #ff5eb1 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
@keyframes floaty { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

/* ============ listening orb ============ */
.orb-wrap { display: flex; flex-direction: column; align-items: center; padding: 6px 0 2px; }
.orb { position: relative; width: 96px; height: 96px; display: flex; align-items: center; justify-content: center; }
.orb-core {
    width: 76px; height: 76px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 30px;
    background: radial-gradient(circle at 32% 28%, #a585ff, #5b3df5 58%, #241a6e);
    box-shadow: 0 0 36px rgba(124, 92, 255, .5), inset 0 0 18px rgba(255, 255, 255, .22);
    z-index: 2; opacity: .85;
}
.orb-active .orb-core { opacity: 1; animation: breathe 1.5s ease-in-out infinite; }
.orb .ring { position: absolute; inset: 6px; border-radius: 50%; border: 2px solid rgba(124, 92, 255, .5); opacity: 0; }
.orb-active .ring { animation: ripple 1.8s ease-out infinite; }
.orb-active .ring.r2 { animation-delay: .6s; }
.orb-active .ring.r3 { animation-delay: 1.2s; }
@keyframes ripple { 0% { transform: scale(.85); opacity: .8; } 100% { transform: scale(2.05); opacity: 0; } }
@keyframes breathe { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }
.orb-label { margin-top: 10px; font-size: .9rem; color: #aab3d0; text-align: center; max-width: 440px; }

/* ============ misc components ============ */
.timer-chip, .note-chip {
    background: rgba(124, 92, 255, .12); border: 1px solid rgba(124, 92, 255, .35);
    border-radius: 12px; padding: 7px 12px; margin: 4px 0; font-size: .92rem;
}
.timer-chip {
    border-color: rgba(0, 209, 255, .4); background: rgba(0, 209, 255, .08);
    font-variant-numeric: tabular-nums;
}
.stats-row { display: flex; gap: 10px; margin: 6px 0 2px; }
.stat {
    flex: 1; text-align: center; border-radius: 14px; padding: 10px 4px;
    background: rgba(255, 255, 255, .05); border: 1px solid rgba(255, 255, 255, .09);
}
.stat-num { font-size: 1.25rem; font-weight: 800; }
.stat-lbl { font-size: .68rem; text-transform: uppercase; letter-spacing: .8px; color: #93a0c4; }
.cap-list .cap {
    font-size: .85rem; color: #c3cbe6; padding: 5px 10px; margin: 3px 0;
    background: rgba(255, 255, 255, .04); border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, .06);
}
.empty-state { text-align: center; padding: 34px 10px; color: #9aa5c6; }
.empty-icon { font-size: 2.6rem; margin-bottom: 6px; }
.empty-tips { font-size: .88rem; color: #7f8ab0; margin-top: 12px; line-height: 1.9; }
.footer { text-align: center; color: #6d7699; font-size: .8rem; padding: 22px 0 30px; }
[data-testid="stToast"] { backdrop-filter: blur(12px); }
</style>
"""

_CSS = _CSS_PART1


def inject_css() -> None:
    """Apply the premium theme (call once at app start)."""
    st.markdown(_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Reusable HTML components
# --------------------------------------------------------------------------- #


def render_hero(user_name: str | None = None) -> None:
    who = f", {user_name}" if user_name else ""
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-badge">✦ Dhi v2.1 — Premium Edition</div>
          <h1>Meet <span class="grad">Dhi</span> — Your Voice-First Assistant{who}</h1>
          <p>Call her by name or type anything — weather, news, math, music, knowledge, timers, notes &amp; more.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_listening_orb(active: bool, label: str | None = None) -> None:
    state = "orb-active" if active else ""
    text = label or ("Listening — speak freely" if active else "Tap Start and speak")
    st.markdown(
        f"""
        <div class="orb-wrap">
          <div class="orb {state}">
            <div class="orb-core"><span>🎙️</span></div>
            <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
          </div>
          <div class="orb-label">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def render_stats(commands: int, notes: int, timers: int, minutes: int) -> None:
    st.markdown(
        f"""
        <div class="stats-row">
          <div class="stat"><div class="stat-num">{commands}</div><div class="stat-lbl">commands</div></div>
          <div class="stat"><div class="stat-num">{notes}</div><div class="stat-lbl">notes</div></div>
          <div class="stat"><div class="stat-num">{timers}</div><div class="stat-lbl">timers</div></div>
          <div class="stat"><div class="stat-num">{minutes}</div><div class="stat-lbl">min active</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_capability_list() -> None:
    caps = [
        "🌦️ Live weather & forecasts", "📰 World news headlines",
        "📚 Wikipedia knowledge", "🧮 Smart calculator & word-math",
        "💱 Currency conversion", "📐 Unit & temperature conversion",
        "📖 Dictionary definitions", "📝 Voice notes",
        "⏲️ Timers with alerts", "🎵 Music & website shortcuts",
        "😄 Jokes, quotes & facts", "🗣️ Multi-language voice",
    ]
    rows = "".join(f'<div class="cap">{c}</div>' for c in caps)
    st.markdown(f'<div class="cap-list">{rows}</div>', unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
          <div class="empty-icon">🌸</div>
          <h3>Say “Dhi” to wake her</h3>
          <p>Tap <b>Start</b> on the mic above and just talk — call <b>“Dhi”</b> anytime,
          or type below. Hands-free mode sends your speech automatically when you pause.</p>
          <div class="empty-tips">
            “Dhi, what's the weather in Tokyo?” · “hey Dhi”<br>
            “calculate 18% of 2450” · “set a timer for 2 minutes”
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<div class="footer">Dhi v2.1 · Python + Streamlit · '
        'Crafted with 💜 and a lot of ☕</div>',
        unsafe_allow_html=True,
    )

