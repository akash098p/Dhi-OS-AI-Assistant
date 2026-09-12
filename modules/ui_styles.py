"""Premium HUD UI layer for DHI OS — dual-theme luxe gradients, layout & components."""

from __future__ import annotations

import datetime as dt

import streamlit as st


_CSS_BASE = """
<style>
/* ============ fonts & base ============ */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Michroma&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, li, span {
    font-family: 'Outfit', 'Segoe UI', system-ui, sans-serif;
}
body { background: transparent; }

/* === restrained command-deck backdrop ==================================== */
.stApp {
    background: var(--dhi-app-bg);
    color: var(--dhi-tx);
}
body::before {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        linear-gradient(90deg, transparent 0 49.9%, rgba(255,255,255,.018) 50%, transparent 50.1%),
        linear-gradient(0deg, transparent 0 49.9%, rgba(255,255,255,.014) 50%, transparent 50.1%),
        radial-gradient(900px 520px at 78% -8%, var(--dhi-aurora2), transparent 72%),
        radial-gradient(760px 440px at 18% 108%, var(--dhi-aurora1), transparent 72%);
    background-size: 96px 96px, 96px 96px, auto, auto;
    opacity: .72;
}
body::after {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    border: 1px solid rgba(255,255,255,.035);
}
@keyframes dhiMsgIn { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
@keyframes dhiBreathe { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.25); opacity: .75; } }
@keyframes dhiShine { from { background-position: 0% 0; } to { background-position: 200% 0; } }

/* ============ header & sidebar controls ====================================
   FIX: never hide <header> itself — the sidebar reopen control lives there.
   Only the hamburger menu (#MainMenu) and footer are removed.               */
#MainMenu, footer { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; border: none !important; }
/* Sidebar collapse / reopen button — always visible, clearly styled */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    color: var(--dhi-tx-dim) !important;
    background: var(--dhi-panel) !important;
    border: 1px solid var(--dhi-panel-bd) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    cursor: pointer !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    color: var(--dhi-tx) !important;
    background: var(--dhi-glass) !important;
    border-color: var(--dhi-accent2) !important;
}

a { color: var(--dhi-link); }
h1, h2, h3, h4 { font-weight: 700; letter-spacing: .3px; color: var(--dhi-tx); }
hr { border-color: var(--dhi-glass-bd); }
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: var(--dhi-code-bg) !important;
    border: 1px solid var(--dhi-panel-bd);
    border-radius: 10px;
    color: var(--dhi-tx);
}

/* ============ scrollbar ============ */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--dhi-scroll); border-radius: 99px; }

/* ============ sidebar ============ */
section[data-testid="stSidebar"] {
    background: var(--dhi-sidebar);
    border-right: 1px solid var(--dhi-sidebar-bd);
}
section[data-testid="stSidebar"] * { color: var(--dhi-tx); }
section[data-testid="stSidebar"] .block-container { padding: 1.35rem 1.1rem 2rem; }
[data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 1500px;
    padding: 1rem 3.25rem 4rem;
}
[data-testid="stVerticalBlock"] { position: relative; z-index: 1; }

/* ============ glass chat ============ */
[data-testid="stChatMessage"] {
    background: var(--dhi-assist-bg);
    border: 1px solid var(--dhi-assist-bd);
    border-left: 3px solid var(--dhi-accent2);
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 14px 34px var(--dhi-shadow);
    backdrop-filter: blur(18px);
    margin: 8px 0;
    animation: dhiMsgIn .32s ease-out;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--dhi-user-bubble);
    border: 1px solid var(--dhi-glass-bd);
    border-left: 3px solid var(--dhi-accent);
    color: var(--dhi-user-tx);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    font-size: .98rem;
    line-height: 1.55;
}
[data-testid="stChatMessage"] table { border-collapse: collapse; width: 100%; font-size: .92rem; }
[data-testid="stChatMessage"] th, [data-testid="stChatMessage"] td {
    border: 1px solid var(--dhi-glass-bd) !important;
    padding: 6px 10px !important;
    background: var(--dhi-glass) !important;
}
[data-testid="stChatMessage"] blockquote {
    border-left: 3px solid var(--dhi-accent);
    padding: 4px 12px;
    color: var(--dhi-tx-dim);
    background: var(--dhi-glass);
    border-radius: 0 10px 10px 0;
}

/* ============ chat input ============ */
[data-testid="stChatInput"] > div {
    background: var(--dhi-input-bg) !important;
    border: 1px solid var(--dhi-input-bd) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(18px);
    box-shadow: 0 14px 36px var(--dhi-shadow);
}
[data-testid="stChatInput"] textarea { color: var(--dhi-tx) !important; }
[data-testid="stChatInput"] button { color: var(--dhi-tx) !important; }

/* ============ buttons — quiet, tactile controls =========================== */
.stButton > button, .stDownloadButton > button {
    min-height: 42px;
    border-radius: 9px;
    border: 1px solid var(--dhi-glass-bd);
    background: linear-gradient(180deg, var(--dhi-button-top), var(--dhi-button-bottom));
    color: var(--dhi-tx);
    font-weight: 600;
    font-size: .84rem;
    padding: 8px 14px;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, background .16s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    border-color: var(--dhi-accent2);
    box-shadow: 0 10px 26px var(--dhi-shadow);
    background: linear-gradient(135deg, var(--dhi-button-hover), var(--dhi-glass));
    color: var(--dhi-tx);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--dhi-accent), var(--dhi-accent2));
    border-color: transparent;
    color: #06101a;
}
.stButton > button[kind="primary"]:hover { color: #06101a; }
@media (max-width: 900px) {
    [data-testid="stAppViewContainer"] > .main .block-container { padding: .75rem 1rem 3rem; }
    .cmdbar { padding: 14px; gap: 8px; }
    .cmdbar-chip:nth-of-type(n+4) { display: none; }
}
</style>
"""

# --------------------------------------------------------------------------- #
#  Theme tokens — "Dark Aurora" & "Light Pearl"
#  Values are substituted into _CSS_THEME via ##KEY## placeholders.
# --------------------------------------------------------------------------- #
_THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "APP_BG": "linear-gradient(180deg,#080d14 0%,#0a1119 54%,#071018 100%)",
        "AURORA1": "rgba(0,209,255,.11)", "AURORA2": "rgba(52,211,153,.10)",
        "AURORA3": "rgba(255,183,77,.06)", "SCAN": "transparent",
        "TX": "#e8f0f5", "TX_DIM": "#91a6b3", "TX_FAINT": "#607783",
        "ACCENT": "#56e0c0", "ACCENT2": "#67c8ff", "ACCENT3": "#ffb45c",
        "GOLD": "#ffc978", "GLASS": "rgba(225,242,247,.055)",
        "GLASS_BD": "rgba(177,224,234,.15)", "PANEL": "rgba(10,22,29,.78)",
        "PANEL_BD": "rgba(103,200,255,.20)", "INPUT_BG": "rgba(225,242,247,.075)",
        "INPUT_BD": "rgba(103,200,255,.34)",
        "USER_BUBBLE": "linear-gradient(135deg, rgba(86,224,192,.18), rgba(103,200,255,.12))",
        "USER_TX": "#effffc", "ASSIST_BG": "rgba(225,242,247,.045)",
        "ASSIST_BD": "rgba(177,224,234,.13)", "LINK": "#8bd8ff",
        "CODE_BG": "rgba(5,14,20,.90)",
        "SIDEBAR": "linear-gradient(180deg, rgba(8,17,24,.98), rgba(6,13,19,.99))",
        "SIDEBAR_BD": "rgba(103,200,255,.16)", "SCROLL": "linear-gradient(#56e0c0,#67c8ff)",
        "SUCCESS": "#56e0c0", "WARN": "#ffc978", "SHADOW": "rgba(0,0,0,.42)",
        "TOPBAR": "linear-gradient(105deg, rgba(20,53,62,.90), rgba(12,35,45,.88) 56%, rgba(20,46,52,.90))",
        "SHINE": "linear-gradient(90deg, transparent, #56e0c0, #67c8ff, transparent)",
        "BADGE_BG": "rgba(86,224,192,.08)", "BUTTON_TOP": "rgba(225,242,247,.10)",
        "BUTTON_BOTTOM": "rgba(225,242,247,.035)", "BUTTON_HOVER": "rgba(86,224,192,.18)",
    },
    "light": {
        "APP_BG": "linear-gradient(180deg,#f4f8f7 0%,#edf3f3 52%,#e8f0f2 100%)",
        "AURORA1": "rgba(57,174,157,.08)", "AURORA2": "rgba(64,143,190,.09)",
        "AURORA3": "rgba(225,161,78,.05)", "SCAN": "transparent",
        "TX": "#1a2931", "TX_DIM": "#506673", "TX_FAINT": "#71848e",
        "ACCENT": "#087f73", "ACCENT2": "#167cad", "ACCENT3": "#b66b16",
        "GOLD": "#a96012", "GLASS": "rgba(255,255,255,.58)",
        "GLASS_BD": "rgba(37,83,96,.16)", "PANEL": "rgba(255,255,255,.76)",
        "PANEL_BD": "rgba(22,124,173,.20)", "INPUT_BG": "rgba(255,255,255,.88)",
        "INPUT_BD": "rgba(22,124,173,.38)",
        "USER_BUBBLE": "linear-gradient(135deg, rgba(8,127,115,.13), rgba(22,124,173,.10))",
        "USER_TX": "#17262e", "ASSIST_BG": "rgba(255,255,255,.72)",
        "ASSIST_BD": "rgba(37,83,96,.16)", "LINK": "#075e91",
        "CODE_BG": "rgba(232,240,242,.94)",
        "SIDEBAR": "linear-gradient(180deg, rgba(250,252,251,.98), rgba(235,243,244,.99))",
        "SIDEBAR_BD": "rgba(22,124,173,.22)", "SCROLL": "linear-gradient(#087f73,#167cad)",
        "SUCCESS": "#087f73", "WARN": "#a96012", "SHADOW": "rgba(35,68,78,.16)",
        "TOPBAR": "linear-gradient(105deg, rgba(255,255,255,.88), rgba(224,241,242,.90) 56%, rgba(244,239,225,.88))",
        "SHINE": "linear-gradient(90deg, transparent, #087f73, #167cad, transparent)",
        "BADGE_BG": "rgba(22,124,173,.08)",
        "BUTTON_TOP": "rgba(255,255,255,.92)",
        "BUTTON_BOTTOM": "rgba(225,235,237,.78)",
        "BUTTON_HOVER": "rgba(8,127,115,.12)",
    },
}

_THEME_LABELS = {"dark": "🌙 Dark aurora", "light": "☀️ Light pearl"}


def theme_names() -> list[str]:
    """Available theme keys, in display order."""
    return ["dark", "light"]


def theme_label(key: str) -> str:
    """Pretty label for a theme key."""
    return _THEME_LABELS.get(key, key)


def _theme_css(name: str) -> str:
    """Build the theme <style> block by substituting ##TOKEN## placeholders."""
    css = _CSS_THEME
    for key, val in _THEMES[name].items():
        css = css.replace(f"##{key}##", val)
    return f"<style>\n{css}\n</style>"
_CSS_THEME = """
/* ============ DHI OS theme tokens (##THEME##) ============ */
:root {
    --dhi-app-bg: ##APP_BG##;
    --dhi-aurora1: ##AURORA1##;
    --dhi-aurora2: ##AURORA2##;
    --dhi-aurora3: ##AURORA3##;
    --dhi-scan: ##SCAN##;
    --dhi-tx: ##TX##;
    --dhi-tx-dim: ##TX_DIM##;
    --dhi-tx-faint: ##TX_FAINT##;
    --dhi-accent: ##ACCENT##;
    --dhi-accent2: ##ACCENT2##;
    --dhi-accent3: ##ACCENT3##;
    --dhi-gold: ##GOLD##;
    --dhi-glass: ##GLASS##;
    --dhi-glass-bd: ##GLASS_BD##;
    --dhi-panel: ##PANEL##;
    --dhi-panel-bd: ##PANEL_BD##;
    --dhi-input-bg: ##INPUT_BG##;
    --dhi-input-bd: ##INPUT_BD##;
    --dhi-user-bubble: ##USER_BUBBLE##;
    --dhi-user-tx: ##USER_TX##;
    --dhi-assist-bg: ##ASSIST_BG##;
    --dhi-assist-bd: ##ASSIST_BD##;
    --dhi-link: ##LINK##;
    --dhi-code-bg: ##CODE_BG##;
    --dhi-sidebar: ##SIDEBAR##;
    --dhi-sidebar-bd: ##SIDEBAR_BD##;
    --dhi-scroll: ##SCROLL##;
    --dhi-success: ##SUCCESS##;
    --dhi-warn: ##WARN##;
    --dhi-shadow: ##SHADOW##;
    --dhi-topbar: ##TOPBAR##;
    --dhi-shine: ##SHINE##;
    --dhi-badge-bg: ##BADGE_BG##;
    --dhi-button-top: ##BUTTON_TOP##;
    --dhi-button-bottom: ##BUTTON_BOTTOM##;
    --dhi-button-hover: ##BUTTON_HOVER##;
}

/* ============ form widgets ============ */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background: var(--dhi-input-bg) !important;
    border-color: var(--dhi-input-bd) !important;
    border-radius: 10px !important;
    color: var(--dhi-tx) !important;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: var(--dhi-input-bg) !important;
    color: var(--dhi-tx) !important;
    border-color: var(--dhi-input-bd) !important;
    border-radius: 10px !important;
}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label,
[data-testid="stToggle"] label, [data-testid="stWidgetLabel"] p {
    color: var(--dhi-tx) !important;
}
[data-baseweb="radio"] [aria-checked] {
    background: var(--dhi-input-bg) !important;
    border-color: var(--dhi-input-bd) !important;
}
[data-baseweb="tag"], [data-baseweb="popover"] {
    background: var(--dhi-panel) !important;
    border-color: var(--dhi-panel-bd) !important;
    color: var(--dhi-tx) !important;
}

/* ============ top command bar ============ */
.cmdbar {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    padding: 12px 18px; border-radius: 16px;
    background: var(--dhi-topbar);
    border: 1px solid var(--dhi-glass-bd);
    box-shadow: 0 10px 30px var(--dhi-shadow), inset 0 1px 0 rgba(255, 255, 255, .08);
    backdrop-filter: blur(14px);
    position: relative; overflow: hidden;
}
.cmdbar::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px;
    background: var(--dhi-shine); background-size: 200% 100%;
    animation: dhiShine 6s linear infinite; opacity: .85;
}
.cmdbar-logo {
    font-family: 'Michroma', sans-serif; font-size: 1.12rem; letter-spacing: 3px;
    color: var(--dhi-tx); text-shadow: 0 0 16px var(--dhi-accent2); line-height: 1;
}
.cmdbar-ver {
    font-family: 'JetBrains Mono', monospace; font-size: .6rem;
    color: var(--dhi-accent2); letter-spacing: 2px;
}
.cmdbar-chip {
    font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: 1.4px;
    text-transform: uppercase; color: var(--dhi-tx-dim);
    padding: 4px 10px; border: 1px solid var(--dhi-glass-bd);
    border-radius: 999px; background: var(--dhi-glass);
}
.cmdbar-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--dhi-success); box-shadow: 0 0 10px var(--dhi-success);
    animation: dhiBreathe 2s ease-in-out infinite;
}
.cmdbar-spacer { flex: 1; }
.cmdbar-time {
    font-family: 'JetBrains Mono', monospace; font-size: .92rem; font-weight: 700;
    color: var(--dhi-gold); letter-spacing: 2px; text-shadow: 0 0 12px var(--dhi-gold);
}

/* ============ sidebar identity ============ */
.mini-hero {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    border: 1px solid var(--dhi-panel-bd); border-radius: 12px;
    background: var(--dhi-panel); margin-bottom: 6px;
}
.mini-logo {
    font-family: 'Michroma', sans-serif; color: var(--dhi-accent2);
    font-size: 1.6rem; text-shadow: 0 0 12px var(--dhi-accent2); line-height: 1;
}
.mini-text { line-height: 1.35; }
.mini-name {
    font-family: 'JetBrains Mono', monospace; font-size: .82rem;
    color: var(--dhi-tx); letter-spacing: 1.4px;
}
.mini-sub { font-size: .6rem; color: var(--dhi-accent2); letter-spacing: 1.6px; }
.mini-who { font-size: .64rem; color: var(--dhi-tx-dim); }

/* ============ HUD section slips ============ */
.section-title {
    font-family: 'JetBrains Mono', monospace; font-size: .76rem;
    text-transform: uppercase; letter-spacing: 1.8px; color: var(--dhi-accent2);
    padding: 7px 0 7px 12px; margin: 6px 0 2px;
    border-left: 3px solid var(--dhi-accent2);
    background: linear-gradient(90deg, var(--dhi-badge-bg), transparent);
    border-radius: 0 8px 8px 0;
}

/* ============ voice orb (listening core) + equalizer ============ */
.orb-wrap { display: flex; flex-direction: column; align-items: center; padding: 8px 0 2px; }
.orb { position: relative; width: 108px; height: 108px; display: flex; align-items: center; justify-content: center; }
.orb-core {
    width: 84px; height: 84px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 32px;
    background: radial-gradient(circle at 32% 28%, #a585ff, #5b3df5 58%, #241a6e);
    box-shadow: 0 0 40px var(--dhi-accent), inset 0 0 20px rgba(255, 255, 255, .24);
    z-index: 2; opacity: .88;
}
.orb-active .orb-core { opacity: 1; animation: dhiBreathe 1.4s ease-in-out infinite; }
.orb .ring { position: absolute; inset: 6px; border-radius: 50%; border: 2px solid var(--dhi-accent2); opacity: 0; }
.orb-active .ring { animation: dhiRipple 1.7s ease-out infinite; }
.orb-active .ring.r2 { animation-delay: .57s; }
.orb-active .ring.r3 { animation-delay: 1.14s; }
@keyframes dhiRipple { 0% { transform: scale(.85); opacity: .85; } 100% { transform: scale(2.05); opacity: 0; } }
.eq { display: flex; align-items: flex-end; gap: 3px; height: 22px; margin-top: 10px; }
.eq span { width: 5px; border-radius: 1px; background: linear-gradient(var(--dhi-accent2), var(--dhi-accent)); animation: dhiEq 1.1s ease-in-out infinite; }
.eq span:nth-child(1) { animation-delay: 0s; }
.eq span:nth-child(2) { animation-delay: .14s; }
.eq span:nth-child(3) { animation-delay: .28s; }
.eq span:nth-child(4) { animation-delay: .42s; }
.eq span:nth-child(5) { animation-delay: .56s; }
@keyframes dhiEq { 0%, 100% { height: 4px; } 50% { height: 20px; } }
.orb-label {
    margin-top: 8px; font-size: .88rem; color: var(--dhi-tx-dim);
    text-align: center; max-width: 460px; font-family: 'JetBrains Mono', monospace;
}

/* ============ processing indicator ============ */
.proc-wrap { display: flex; align-items: center; gap: 10px; padding: 10px 6px; }
.proc-bars { display: flex; gap: 4px; }
.proc-bars span { width: 6px; height: 6px; border-radius: 50%; background: var(--dhi-accent2); animation: dhiProc .55s ease-in-out infinite; }
.proc-bars span:nth-child(2) { animation-delay: .11s; }
.proc-bars span:nth-child(3) { animation-delay: .22s; }
.proc-bars span:nth-child(4) { animation-delay: .33s; }
.proc-bars span:nth-child(5) { animation-delay: .44s; }
.proc-label {
    font-family: 'JetBrains Mono', monospace; font-size: .72rem;
    letter-spacing: 2px; color: var(--dhi-accent2); text-transform: uppercase;
}
@keyframes dhiProc { 0%, 100% { transform: scale(1); opacity: .55; } 50% { transform: scale(1.7); opacity: 1; } }

/* ============ stats HUD ============ */
.stats-row { display: flex; gap: 8px; margin: 6px 0 2px; }
.stat {
    flex: 1; text-align: center; border-radius: 10px; padding: 9px 3px;
    background: var(--dhi-panel); border: 1px solid var(--dhi-panel-bd);
    font-family: 'JetBrains Mono', monospace;
}
.stat-num { font-size: 1.15rem; font-weight: 700; color: var(--dhi-tx); }
.stat-lbl { font-size: .6rem; text-transform: uppercase; letter-spacing: .8px; color: var(--dhi-tx-dim); }

/* ============ core diagnostics panel ============ */
.diag-panel {
    font-family: 'JetBrains Mono', monospace; font-size: .7rem;
    background: var(--dhi-panel); border: 1px solid var(--dhi-panel-bd);
    border-radius: 12px; padding: 10px 12px; margin: 4px 0;
}
.diag-title { color: var(--dhi-accent2); letter-spacing: 1.6px; font-size: .66rem; text-transform: uppercase; margin-bottom: 6px; }
.diag-row { display: flex; justify-content: space-between; padding: 1px 0; }
.diag-row span { color: var(--dhi-tx-dim); }
.diag-row b { color: var(--dhi-tx); }
.diag-row b.ok { color: var(--dhi-success); }
.diag-row b.warn { color: var(--dhi-warn); }
.diag-bar { height: 5px; margin: 8px 0 6px; background: var(--dhi-glass); border: 1px solid var(--dhi-panel-bd); }
.diag-fill { height: 100%; width: 40%; background: linear-gradient(90deg, var(--dhi-accent), var(--dhi-accent2)); }
.diag-foot { color: var(--dhi-success); letter-spacing: .9px; font-size: .64rem; }
.diag-foot::before { content: "◆ "; }

/* ============ chips, capabilities, empty state, footer ============ */
.timer-chip, .note-chip {
    background: var(--dhi-glass); border: 1px solid var(--dhi-panel-bd);
    border-radius: 10px; padding: 7px 12px; margin: 4px 0; font-size: .9rem;
    color: var(--dhi-tx);
}
.timer-chip {
    border-color: var(--dhi-input-bd);
    font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', monospace;
}
.cap-list .cap {
    font-size: .84rem; color: var(--dhi-tx); padding: 5px 10px; margin: 3px 0;
    background: var(--dhi-glass); border-radius: 8px;
    border: 1px solid var(--dhi-glass-bd);
}
.empty-state { text-align: center; padding: 34px 10px; color: var(--dhi-tx-dim); }
.empty-icon { font-size: 2.5rem; margin-bottom: 6px; }
.empty-state h3 { color: var(--dhi-tx); }
.empty-tips { font-size: .88rem; color: var(--dhi-tx-faint); margin-top: 12px; line-height: 1.9; font-family: 'JetBrains Mono', monospace; }
.footer { text-align: center; color: var(--dhi-tx-faint); font-size: .78rem; padding: 20px 0 30px; }
[data-testid="stToast"] { backdrop-filter: blur(12px); }

/* ==== boot sequence (cinematic dark — independent of theme) ==== */
.boot-overlay {
    position: fixed; inset: 0; z-index: 2147482000;
    background:
        radial-gradient(900px 480px at 50% 28%, rgba(124, 92, 255, .16), transparent 62%),
        radial-gradient(700px 420px at 50% 78%, rgba(0, 209, 255, .10), transparent 60%),
        repeating-linear-gradient(0deg, rgba(0, 209, 255, .10) 0 1px, transparent 1px 54px),
        repeating-linear-gradient(90deg, rgba(124, 92, 255, .10) 0 1px, transparent 1px 54px),
        #04060f;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    animation: dhiBootEnd 4.6s ease forwards;
}
@keyframes dhiBootEnd {
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
    animation: dhiBootCore 1.1s ease-in-out infinite;
}
@keyframes dhiBootCore { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.boot-title { font-family: 'Michroma', sans-serif; font-size: 1.5rem; letter-spacing: 5px; color: #e8ecf8; }
.boot-ver { font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: #3dffa7; }
.boot-sub { font-family: 'JetBrains Mono', monospace; font-size: .62rem; letter-spacing: 2.5px; color: #8fd3ff; text-transform: uppercase; }
.boot-lines { display: grid; grid-template-columns: auto; gap: 5px; text-align: left; font-family: 'JetBrains Mono', monospace; font-size: .74rem; color: #c3cbe6; }
.boot-line { opacity: 0; }
.boot-line span { color: #00d1ff; }
.boot-line b { color: #3dffa7; }
.boot-line:nth-child(1) { animation: dhiBootLine .5s .1s ease forwards; }
.boot-line:nth-child(2) { animation: dhiBootLine .5s .55s ease forwards; }
.boot-line:nth-child(3) { animation: dhiBootLine .5s 1.0s ease forwards; }
.boot-line:nth-child(4) { animation: dhiBootLine .5s 1.45s ease forwards; }
.boot-line:nth-child(5) { animation: dhiBootLine .5s 1.9s ease forwards; }
.boot-line:nth-child(6) { animation: dhiBootLine .5s 2.35s ease forwards; }
@keyframes dhiBootLine { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.boot-progress { width: 340px; height: 6px; max-width: 86vw; background: rgba(255, 255, 255, .07); border: 1px solid rgba(0, 209, 255, .4); }
.boot-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #7c5cff, #00d1ff); box-shadow: 0 0 14px rgba(0, 209, 255, .7); animation: dhiBootFill 3.9s linear forwards; }
@keyframes dhiBootFill { from { width: 0%; } to { width: 100%; } }
.boot-pct { font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: 3px; color: #93a0c4; animation: dhiBootPulse 1.6s ease-in-out infinite; }
@keyframes dhiBootPulse { 0%, 100% { opacity: .45; } 50% { opacity: 1; } }
"""

# --------------------------------------------------------------------------- #
#  Engine
# --------------------------------------------------------------------------- #


def inject_css(theme: str = "dark") -> None:
    """Apply the DHI OS HUD theme (call once at app start, after state init)."""
    if theme not in _THEMES:
        theme = "dark"
    st.markdown(_CSS_BASE, unsafe_allow_html=True)
    st.markdown(_theme_css(theme), unsafe_allow_html=True)


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
    """Full-screen DHI boot sequence (CSS auto-fades after ~4.6 s)."""
    st.markdown(
        """
        <div class="boot-overlay">
          <div class="boot-inner">
            <div class="boot-core">DHI</div>
            <div class="boot-title">DHI&nbsp;OS <span class="boot-ver">v3.0</span></div>
            <div class="boot-sub">Premium Edition</div>
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


def render_topbar(uptime_sec: int = 0, session: str = "------",
                  user_name: str | None = None, mic_state: str = "STANDBY",
                  commands: int = 0) -> None:
    """Glass command bar — identity, live status chips and clock."""
    now = dt.datetime.now().strftime("%H:%M:%S")
    who = user_name or "Operator"
    st.markdown(
        f"""
        <div class="cmdbar">
          <div class="cmdbar-logo">◈ DHI<span class="cmdbar-ver">&nbsp;OS v3.0</span></div>
          <span class="cmdbar-dot"></span>
          <span class="cmdbar-chip">online</span>
          <span class="cmdbar-chip">hello, {who}</span>
          <span class="cmdbar-chip">mic · {mic_state}</span>
          <span class="cmdbar-chip">{commands} cmds</span>
          <span class="cmdbar-chip">up {_fmt_hhmmss(uptime_sec)}</span>
          <span class="cmdbar-spacer"></span>
          <span class="cmdbar-chip">session #{session}</span>
          <span class="cmdbar-time">{now}</span>
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
            <div class="mini-sub">v3.0 · PREMIUM EDITION</div>
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
    """DHI 'processing' chip (bouncing bars + label)."""
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
        '<div class="footer">DHI OS v3.0 · Premium Edition · Python + Streamlit · '
        'Crafted with 💜 and a lot of ☕</div>',
        unsafe_allow_html=True,
    )