"""Premium JARVIS-style UI layer for DHI OS — HUD theming, boot sequence, animations."""

from __future__ import annotations

import streamlit as st

# --------------------------------------------------------------------------- #
#  Theme CSS — "DHI OS · JARVIS Protocol" HUD
# --------------------------------------------------------------------------- #
_CSS1 = """
<style>
/* ============ fonts & base ============ */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Michroma&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, li, span {
    font-family: 'Outfit', 'Segoe UI', system-ui, sans-serif;
}
.stApp {
    background:
        radial-gradient(1200px 560px at 8% -12%, rgba(124, 92, 255, .20), transparent 62%),
        radial-gradient(1000px 520px at 104% 6%, rgba(0, 209, 255, .14), transparent 58%),
        radial-gradient(820px 600px at 50% 124%, rgba(255, 94, 177, .10), transparent 64%),
        repeating-linear-gradient(0deg, rgba(0, 209, 255, .028) 0 1px, transparent 1px 72px),
        repeating-linear-gradient(90deg, rgba(124, 92, 255, .028) 0 1px, transparent 1px 72px),
        #04060f;
    color: #e8ecf8;
}

/* faint CRT scanlines over everything (non-interactive) */
body::after {
    content: "";
    position: fixed; inset: 0; z-index: 2147483000;
    background: repeating-linear-gradient(0deg, rgba(255, 255, 255, .016) 0 1px, transparent 1px 3px);
    pointer-events: none;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
a { color: #8fd3ff; }
h1, h2, h3, h4 { font-weight: 700; letter-spacing: .3px; }
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
    background: linear-gradient(180deg, rgba(15, 20, 42, .97), rgba(6, 9, 22, .99));
    border-right: 1px solid rgba(0, 209, 255, .12);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* ============ glass chat ============ */
[data-testid="stChatMessage"] {
    background: linear-gradient(150deg, rgba(255, 255, 255, .065), rgba(255, 255, 255, .02));
    border: 1px solid rgba(255, 255, 255, .1);
    border-left: 3px solid rgba(0, 209, 255, .4);
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, .3);
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
</style>
"""
_CSS2 = """
<style>
/* ============ chat input ============ */
[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, .07) !important;
    border: 1px solid rgba(0, 209, 255, .28) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 22px rgba(0, 209, 255, .12);
}

/* ============ buttons — angular command launchers ============ */
.stButton > button, .stDownloadButton > button {
    border-radius: 8px;
    border: 1px solid rgba(0, 209, 255, .35);
    background: linear-gradient(135deg, rgba(124, 92, 255, .18), rgba(0, 209, 255, .12));
    color: #e8ecf8;
    font-weight: 600;
    font-size: .86rem;
    padding: 6px 14px;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%);
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, filter .16s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 209, 255, .9);
    box-shadow: 0 10px 26px rgba(0, 209, 255, .35), inset 0 0 18px rgba(124, 92, 255, .3);
    color: #fff;
    filter: brightness(1.08);
}

/* ============ hero / reactor core ============ */
.hero { text-align: center; padding: 8px 0 2px; }
.hero-badge {
    display: inline-block; font-size: .7rem; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; color: #8fd3ff;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid rgba(0, 209, 255, .5); border-radius: 4px;
    padding: 5px 14px; margin-bottom: 10px;
    background: rgba(0, 209, 255, .08);
    animation: floaty 4s ease-in-out infinite;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
}
.hero h1, .core-h {
    font-family: 'Michroma', 'Outfit', sans-serif;
    font-size: clamp(1.7rem, 4.6vw, 2.7rem); margin: 0 0 6px; font-weight: 600; letter-spacing: .5px;
}
.hero p { color: #a6b0cf; font-size: .98rem; margin: 0; }
.grad {
    background: linear-gradient(92deg, #9d7bff 0%, #00d1ff 55%, #ff5eb1 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
@keyframes floaty { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

/* ---- reactor core ------------------------------------------------------- */
.core-wrap { display: flex; flex-direction: column; align-items: center; margin-top: 10px; }
.core-frame { position: relative; width: 210px; height: 210px; }
.core-corner { position: absolute; width: 30px; height: 30px; border: 2px solid rgba(0, 209, 255, .6); opacity: .9; }
.core-corner.tl { top: 0; left: 0; border-right: none; border-bottom: none; }
.core-corner.tr { top: 0; right: 0; border-left: none; border-bottom: none; }
.core-corner.bl { bottom: 0; left: 0; border-right: none; border-top: none; }
.core-corner.br { bottom: 0; right: 0; border-left: none; border-top: none; }
.core-react { position: absolute; inset: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.core-ring { position: absolute; border-radius: 50%; border: 2px dashed rgba(0, 209, 255, .5); }
.core-ring.r1 { inset: 0; animation: spin 16s linear infinite; }
.core-ring.r2 { inset: 10px; border: 1.5px solid rgba(124, 92, 255, .6); animation: spin 11s linear infinite reverse; }
.core-ring.r3 { inset: 22px; border: 1px dashed rgba(255, 94, 177, .45); animation: spin 7s linear infinite; }
.core-inner {
    width: 118px; height: 118px; border-radius: 50%;
    background: radial-gradient(circle at 32% 28%, #cfe8ff, #7c5cff 55%, #1b1256);
    box-shadow: 0 0 44px rgba(0, 209, 255, .65), inset 0 0 24px rgba(255, 255, 255, .3);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    z-index: 3;
}
.core-name {
    font-family: 'Michroma', sans-serif; font-size: 1.9rem; color: #fff;
    letter-spacing: 2px; text-shadow: 0 0 14px rgba(0, 209, 255, .9); line-height: 1;
}
.core-sub { font-family: 'JetBrains Mono', monospace; font-size: .52rem; letter-spacing: 2.5px; color: rgba(255, 255, 255, .75); margin-top: 3px; }
.core-glow {
    position: absolute; inset: -8px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 209, 255, .28), transparent 70%);
    animation: breathe 3.2s ease-in-out infinite; z-index: 1;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes breathe { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.07); } }

/* ---- HUD readout --------------------------------------------------------- */
.core-hud {
    display: inline-grid; grid-template-columns: auto auto; gap: 4px 12px;
    font-family: 'JetBrains Mono', monospace; font-size: .72rem; margin-top: 12px;
    background: rgba(8, 12, 26, .55); border: 1px solid rgba(0, 209, 255, .22); border-radius: 8px;
    padding: 8px 14px; text-align: left;
}
.hud-line { color: #93a0c4; text-transform: uppercase; letter-spacing: .6px; }
.hud-val { color: #e8ecf8; }
.hud-val.ok { color: #3dffa7; }
.hud-val.warn { color: #ffc257; }
</style>
"""
_CSS3 = """
<style>
/* ============ sidebar mini-hero ============ */
.mini-hero {
    display: flex; align-items: center; gap: 10px; padding: 8px 10px;
    border: 1px solid rgba(0, 209, 255, .25); border-radius: 8px;
    background: rgba(8, 12, 26, .55); margin-bottom: 6px;
}
.mini-logo {
    font-family: 'Michroma', sans-serif; color: #00d1ff; font-size: 1.6rem;
    text-shadow: 0 0 10px rgba(0, 209, 255, .8); line-height: 1;
}
.mini-text { line-height: 1.3; }
.mini-name { font-family: 'JetBrains Mono', monospace; font-size: .8rem; color: #e8ecf8; letter-spacing: 1.2px; }
.mini-sub { font-size: .6rem; color: #8fd3ff; letter-spacing: 1.4px; }
.mini-who { font-size: .62rem; color: #7f8ab0; }

/* ============ listening orb (voice core) + equalizer ============ */
.orb-wrap { display: flex; flex-direction: column; align-items: center; padding: 6px 0 2px; }
.orb { position: relative; width: 108px; height: 108px; display: flex; align-items: center; justify-content: center; }
.orb-core {
    width: 84px; height: 84px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 32px;
    background: radial-gradient(circle at 32% 28%, #a585ff, #5b3df5 58%, #241a6e);
    box-shadow: 0 0 40px rgba(124, 92, 255, .55), inset 0 0 20px rgba(255, 255, 255, .24);
    z-index: 2; opacity: .85;
}
.orb-active .orb-core { opacity: 1; animation: breathe 1.4s ease-in-out infinite; }
.orb .ring { position: absolute; inset: 6px; border-radius: 50%; border: 2px solid rgba(0, 209, 255, .55); opacity: 0; }
.orb-active .ring { animation: ripple 1.7s ease-out infinite; }
.orb-active .ring.r2 { animation-delay: .57s; }
.orb-active .ring.r3 { animation-delay: 1.14s; }
@keyframes ripple { 0% { transform: scale(.85); opacity: .85; } 100% { transform: scale(2.05); opacity: 0; } }
.eq { display: flex; align-items: flex-end; gap: 3px; height: 22px; margin-top: 10px; }
.eq span { width: 5px; border-radius: 1px; background: linear-gradient(#00d1ff, #7c5cff); animation: eqbar 1.1s ease-in-out infinite; }
.eq span:nth-child(1) { animation-delay: 0s; }
.eq span:nth-child(2) { animation-delay: .14s; }
.eq span:nth-child(3) { animation-delay: .28s; }
.eq span:nth-child(4) { animation-delay: .42s; }
.eq span:nth-child(5) { animation-delay: .56s; }
@keyframes eqbar { 0%, 100% { height: 4px; } 50% { height: 20px; } }
.orb-label { margin-top: 8px; font-size: .88rem; color: #aab3d0; text-align: center; max-width: 460px; font-family: 'JetBrains Mono', monospace; }

/* ============ section titles (HUD slips) ============ */
.section-title {
    font-family: 'JetBrains Mono', monospace; font-size: .78rem;
    text-transform: uppercase; letter-spacing: 1.6px; color: #8fd3ff;
    padding: 7px 0 7px 12px; margin: 4px 0 2px;
    border-left: 3px solid rgba(0, 209, 255, .55);
    background: linear-gradient(90deg, rgba(0, 209, 255, .06), transparent);
}

/* ============ stats HUD ============ */
.stats-row { display: flex; gap: 8px; margin: 6px 0 2px; }
.stat {
    flex: 1; text-align: center; border-radius: 8px; padding: 9px 3px;
    background: rgba(255, 255, 255, .05); border: 1px solid rgba(0, 209, 255, .22);
    font-family: 'JetBrains Mono', monospace;
}
.stat-num { font-size: 1.15rem; font-weight: 700; color: #e8ecf8; }
.stat-lbl { font-size: .62rem; text-transform: uppercase; letter-spacing: .7px; color: #93a0c4; }

/* ============ core diagnostics panel ============ */
.diag-panel {
    font-family: 'JetBrains Mono', monospace; font-size: .7rem;
    background: rgba(8, 12, 26, .6); border: 1px solid rgba(124, 92, 255, .3);
    border-radius: 8px; padding: 9px 12px; margin: 4px 0;
}
.diag-title { color: #8fd3ff; letter-spacing: 1.4px; font-size: .66rem; text-transform: uppercase; margin-bottom: 6px; }
.diag-row { display: flex; justify-content: space-between; padding: 1px 0; }
.diag-row span { color: #7f8ab0; }
.diag-row b { color: #e8ecf8; }
.diag-row b.ok { color: #3dffa7; }
.diag-row b.warn { color: #ffc257; }
.diag-bar { height: 5px; margin: 8px 0 6px; background: rgba(255, 255, 255, .06); border: 1px solid rgba(0, 209, 255, .25); }
.diag-fill { height: 100%; width: 40%; background: linear-gradient(90deg, #7c5cff, #00d1ff); }
.diag-foot { color: #3dffa7; letter-spacing: .8px; font-size: .64rem; }
.diag-foot::before { content: "◆ "; }

/* ============ misc ============ */
.timer-chip, .note-chip {
    background: rgba(124, 92, 255, .12); border: 1px solid rgba(124, 92, 255, .35);
    border-radius: 8px; padding: 7px 12px; margin: 4px 0; font-size: .9rem;
}
.timer-chip {
    border-color: rgba(0, 209, 255, .4); background: rgba(0, 209, 255, .08);
    font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', monospace;
}
.cap-list .cap {
    font-size: .84rem; color: #c3cbe6; padding: 5px 10px; margin: 3px 0;
    background: rgba(255, 255, 255, .04); border-radius: 6px;
    border: 1px solid rgba(0, 209, 255, .14);
}
.empty-state { text-align: center; padding: 32px 10px; color: #9aa5c6; }
.empty-icon { font-size: 2.5rem; margin-bottom: 6px; }
.empty-tips { font-size: .88rem; color: #7f8ab0; margin-top: 12px; line-height: 1.9; font-family: 'JetBrains Mono', monospace; }
.footer { text-align: center; color: #6d7699; font-size: .78rem; padding: 20px 0 30px; }
[data-testid="stToast"] { backdrop-filter: blur(12px); }
</style>
"""
_CSS4 = """
<style>
/* ============ processing indicator ============ */
.proc-wrap { display: flex; align-items: center; gap: 10px; padding: 10px 6px; }
.proc-bars { display: flex; gap: 4px; }
.proc-bars span { width: 6px; height: 6px; border-radius: 50%; background: #00d1ff; animation: procbar .55s ease-in-out infinite; }
.proc-bars span:nth-child(2) { animation-delay: .11s; }
.proc-bars span:nth-child(3) { animation-delay: .22s; }
.proc-bars span:nth-child(4) { animation-delay: .33s; }
.proc-bars span:nth-child(5) { animation-delay: .44s; }
.proc-label { font-family: 'JetBrains Mono', monospace; font-size: .72rem; letter-spacing: 2px; color: #8fd3ff; text-transform: uppercase; }
@keyframes procbar { 0%, 100% { transform: scale(1); opacity: .55; } 50% { transform: scale(1.7); opacity: 1; } }

/* ============ boot sequence overlay ============ */
.boot-overlay {
    position: fixed; inset: 0; z-index: 100000;
    background:
        radial-gradient(900px 480px at 50% 28%, rgba(124, 92, 255, .16), transparent 62%),
        radial-gradient(700px 420px at 50% 78%, rgba(0, 209, 255, .10), transparent 60%),
        repeating-linear-gradient(0deg, rgba(0, 209, 255, .10) 0 1px, transparent 1px 54px),
        repeating-linear-gradient(90deg, rgba(124, 92, 255, .10) 0 1px, transparent 1px 54px),
        #04060f;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    animation: bootEnd 4.6s ease forwards;
}
@keyframes bootEnd {
    0% { opacity: 1; }
    78% { opacity: 1; }
    100% { opacity: 0; visibility: hidden; pointer-events: none; }
}
.boot-inner { display: flex; flex-direction: column; align-items: center; gap: 16px; max-width: 92vw; min-width: 300px; }
.boot-core {
    width: 108px; height: 108px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 34% 30%, #cfe8ff, #3a2aa8 60%, #140b3c);
    box-shadow: 0 0 46px rgba(0, 209, 255, .7), inset 0 0 22px rgba(255, 255, 255, .3);
    font-family: 'Michroma', sans-serif; color: #fff; font-size: 2.1rem;
    animation: breathe 1.1s ease-in-out infinite;
}
.boot-title { font-family: 'Michroma', sans-serif; font-size: 1.5rem; letter-spacing: 5px; color: #e8ecf8; }
.boot-ver { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: #3dffa7; }
.boot-sub { font-family: 'JetBrains Mono', monospace; font-size: .62rem; letter-spacing: 2.5px; color: #8fd3ff; text-transform: uppercase; }
.boot-lines { display: grid; grid-template-columns: auto; gap: 5px; text-align: left; font-family: 'JetBrains Mono', monospace; font-size: .74rem; color: #c3cbe6; }
.boot-line { opacity: 0; }
.boot-line span { color: #00d1ff; }
.boot-line b { color: #3dffa7; }
.boot-line:nth-child(1) { animation: bootLineIn .5s .1s ease forwards; }
.boot-line:nth-child(2) { animation: bootLineIn .5s .55s ease forwards; }
.boot-line:nth-child(3) { animation: bootLineIn .5s 1.0s ease forwards; }
.boot-line:nth-child(4) { animation: bootLineIn .5s 1.45s ease forwards; }
.boot-line:nth-child(5) { animation: bootLineIn .5s 1.9s ease forwards; }
.boot-line:nth-child(6) { animation: bootLineIn .5s 2.35s ease forwards; }
@keyframes bootLineIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.boot-progress { width: 340px; height: 6px; max-width: 86vw; background: rgba(255, 255, 255, .07); border: 1px solid rgba(0, 209, 255, .4); }
.boot-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #7c5cff, #00d1ff); box-shadow: 0 0 14px rgba(0, 209, 255, .7); animation: bootFill 3.9s linear forwards; }
@keyframes bootFill { from { width: 0%; } to { width: 100%; } }
.boot-pct { font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: 3px; color: #93a0c4; animation: bootPulse 1.6s ease-in-out infinite; }
@keyframes bootPulse { 0%, 100% { opacity: .45; } 50% { opacity: 1; } }
</style>
"""

_CSS = _CSS1 + _CSS2 + _CSS3 + _CSS4


def inject_css() -> None:
    """Apply the DHI OS HUD theme (call once at app start)."""
    st.markdown(_CSS, unsafe_allow_html=True)


def _fmt_hhmmss(seconds: int) -> str:
    """Format seconds as HUD-style 00:00:00."""
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
# --------------------------------------------------------------------------- #
#  Reusable HTML components
# --------------------------------------------------------------------------- #


def render_boot_overlay() -> None:
    """Full-screen JARVIS boot sequence (CSS auto-fades after ~4.5 s)."""
    st.markdown(
        """
        <div class="boot-overlay">
          <div class="boot-inner">
            <div class="boot-core">DHI</div>
            <div class="boot-title">DHI&nbsp;OS <span class="boot-ver">v3.0</span></div>
            <div class="boot-sub">JARVIS Protocol · Premium Edition</div>
            <div class="boot-lines">
              <div class="boot-line"><span>&gt;</span> Neural core ........... <b>ONLINE</b></div>
              <div class="boot-line"><span>&gt;</span> Audio subsystem ....... <b>CALIBRATED</b></div>
              <div class="boot-line"><span>&gt;</span> Intent matrix ......... <b>LOADED</b></div>
              <div class="boot-line"><span>&gt;</span> Skill modules ......... <b>25+ READY</b></div>
              <div class="boot-line"><span>&gt;</span> Security handshake .... <b>VERIFIED</b></div>
              <div class="boot-line"><span>&gt;</span> All systems ........... <b>NOMINAL</b></div>
            </div>
            <div class="boot-progress"><div class="boot-fill"></div></div>
            <div class="boot-pct">INITIALIZING…</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(user_name: str | None = None, uptime: int = 0,
                commands: int = 0) -> None:
    """Main hero — arc-reactor core with live HUD readouts."""
    who = f", {user_name}" if user_name else ""
    up = _fmt_hhmmss(uptime)
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-badge">✦ DHI OS v3.0 · JARVIS PROTOCOL</div>
          <div class="core-wrap">
            <div class="core-frame">
              <div class="core-corner tl"></div><div class="core-corner tr"></div>
              <div class="core-corner bl"></div><div class="core-corner br"></div>
              <div class="core-react">
                <div class="core-glow"></div>
                <div class="core-ring r1"></div><div class="core-ring r2"></div><div class="core-ring r3"></div>
                <div class="core-inner"><div class="core-name">DHI</div><div class="core-sub">AI CORE</div></div>
              </div>
            </div>
            <div class="core-hud">
              <div class="hud-line">Status</div><div class="hud-val ok">● NOMINAL</div>
              <div class="hud-line">Uptime</div><div class="hud-val">{up}</div>
              <div class="hud-line">Cmds</div><div class="hud-val">{commands}</div>
            </div>
          </div>
          <h1 class="core-h">Welcome{who} — <span class="grad">Dhi</span> is online</h1>
          <p>Speak or type: weather, news, math, music, knowledge, timers &amp; more — JARVIS-class response time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mini_hero(user_name: str | None = None) -> None:
    """Compact HUD identity block for the sidebar."""
    who = user_name or "Operator"
    st.markdown(
        f"""
        <div class="mini-hero">
          <div class="mini-logo">◈</div>
          <div class="mini-text">
            <div class="mini-name">DHI OS</div>
            <div class="mini-sub">v3.0 · JARVIS PROTOCOL</div>
            <div class="mini-who">Hello, {who}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_listening_orb(active: bool, label: str | None = None) -> None:
    """Voice core orb with animated equalizer while listening."""
    state = "orb-active" if active else ""
    eq = ('<div class="eq"><span></span><span></span><span></span>'
          '<span></span><span></span></div>') if active else ""
    text = label or ("Listening — speak freely" if active else "Tap Start and speak")
    st.markdown(
        f"""
        <div class="orb-wrap">
          <div class="orb {state}">
            <div class="orb-core"><span>🎙️</span></div>
            <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
          </div>
          {eq}
          <div class="orb-label">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def render_processing(label: str = "PROCESSING") -> str:
    """JARVIS-style 'processing' chip (bouncing bars + label)."""
    bars = "".join("<span></span>" for _ in range(5))
    return (f'<div class="proc-wrap"><div class="proc-bars">{bars}</div>'
            f'<div class="proc-label">{label}</div></div>')


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


def render_diagnostics(session: str, uptime_sec: int, commands: int, mic: str,
                       lang: str, voice: bool, last: str | None = None) -> None:
    """Sidebar 'Core Diagnostics' HUD panel."""
    up = _fmt_hhmmss(uptime_sec)
    mic_cls = "ok" if mic not in ("STANDBY", "OFF") else "warn"
    level = min(100, 28 + int(commands) * 3 + (0 if mic == "STANDBY" else 9))
    last_row = (f"<div class='diag-row'><span>Last cmd</span>"
                f"<b>{last[:18]}</b></div>" if last else "")
    lang_short = lang.split("(")[0].strip()
    st.markdown(
        f"""
        <div class="diag-panel">
          <div class="diag-title">◢ CORE DIAGNOSTICS</div>
          <div class="diag-row"><span>Session</span><b>#{session}</b></div>
          <div class="diag-row"><span>Uptime</span><b>{up}</b></div>
          <div class="diag-row"><span>Commands</span><b>{commands}</b></div>
          <div class="diag-row"><span>Mic</span><b class="{mic_cls}">{mic}</b></div>
          <div class="diag-row"><span>Voice</span><b>{"ON" if voice else "MUTE"}</b></div>
          <div class="diag-row"><span>Lang</span><b>{lang_short}</b></div>
          {last_row}
          <div class="diag-bar"><div class="diag-fill" style="width:{level}%"></div></div>
          <div class="diag-foot">All systems nominal</div>
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
          <div class="empty-icon">◈</div>
          <h3>Say “Dhi” to wake the core</h3>
          <p>Tap <b>Start</b> on the voice console and just talk — call <b>“Dhi”</b> anytime,
          or type below. Hands-free mode sends your speech automatically when you pause.</p>
          <div class="empty-tips">
            “Dhi, what's the weather in Tokyo?” · “system status”<br>
            “calculate 18% of 2450” · “set a timer for 2 minutes” · “good morning, sir”
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<div class="footer">DHI OS v3.0 · JARVIS Protocol · Python + Streamlit · '
        'Crafted with 💜 and a lot of ☕</div>',
        unsafe_allow_html=True,
    )