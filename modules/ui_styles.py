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
@keyframes dhiOrbit { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes dhiOrbitReverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
@keyframes dhiStarDrift { from { transform: translate3d(0, 0, 0); } to { transform: translate3d(-28px, 18px, 0); } }
@keyframes dhiPulseLine { 0%, 100% { opacity: .35; transform: scaleX(.72); } 50% { opacity: 1; transform: scaleX(1); } }
@keyframes dhiParticleFloat { 0%, 100% { transform: translate3d(0, 8px, 0) scale(.7); opacity: .15; } 50% { transform: translate3d(12px, -18px, 0) scale(1.25); opacity: .95; } }
@keyframes dhiScan { 0% { transform: translateY(-130%); opacity: 0; } 18%, 70% { opacity: .8; } 100% { transform: translateY(330%); opacity: 0; } }
@keyframes dhiEnergy { 0%, 100% { transform: scale(.84); opacity: .25; } 50% { transform: scale(1.22); opacity: .78; } }
@keyframes dhiSatellite { from { transform: rotate(0deg) translateX(75px) rotate(0deg); } to { transform: rotate(360deg) translateX(75px) rotate(-360deg); } }

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
    width: 300px !important;
    min-width: 300px !important;
    max-width: 300px !important;
}
section[data-testid="stSidebar"] > div:first-child { width: 300px !important; }
section[data-testid="stSidebar"] * { color: var(--dhi-tx); box-sizing: border-box; }
section[data-testid="stSidebar"] .block-container { width: 100%; padding: .85rem 1rem 1.25rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .35rem; }
[data-testid="stSidebar"] .stToggle { margin: 0 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: .72rem !important; white-space: normal; }
[data-testid="stSidebar"] [data-testid="stSelectbox"],
[data-testid="stSidebar"] [data-testid="stTextInput"],
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] .stDownloadButton { width: 100%; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { min-height: 40px; }
[data-testid="stSidebar"] [data-testid="stToggle"] label { min-height: 30px; }
.side-control-label { color: var(--dhi-accent); font: .57rem 'JetBrains Mono', monospace; letter-spacing: 2px; margin: 13px 8px 2px; text-transform: uppercase; }
[data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 1500px;
    padding: 1rem 3.25rem 4rem;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
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
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer {
    background: color-mix(in srgb, var(--dhi-app-bg) 88%, transparent) !important;
    border-top: 1px solid var(--dhi-glass-bd) !important;
    box-shadow: 0 -12px 28px var(--dhi-shadow) !important;
    backdrop-filter: blur(18px);
}
[data-testid="stChatInput"] textarea {
    color: var(--dhi-tx) !important;
    -webkit-text-fill-color: var(--dhi-tx) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--dhi-tx-dim) !important;
    -webkit-text-fill-color: var(--dhi-tx-dim) !important;
    opacity: 1 !important;
}
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
    section[data-testid="stSidebar"] { width: 280px !important; min-width: 280px !important; max-width: 280px !important; }
    section[data-testid="stSidebar"] > div:first-child { width: 280px !important; }
    [data-testid="stAppViewContainer"] > .main .block-container { padding: .75rem 1rem 3rem; }
    [data-testid="stMainBlockContainer"] { padding-top: .75rem !important; }
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
.cmdbar-logo { white-space: nowrap; }
.cmdbar-hello { display: grid; gap: 2px; min-width: 120px; }
.cmdbar-hello b { color: var(--dhi-tx); font-size: .76rem; font-weight: 500; }
.cmdbar-hello small { color: var(--dhi-tx-dim); font-size: .59rem; }
.cmdbar-metrics { display: flex; align-items: stretch; gap: 0; margin-left: auto; }
.cmdbar-metric { min-width: 72px; padding: 0 12px; border-left: 1px solid var(--dhi-glass-bd); text-align: center; }
.cmdbar-metric span { display: block; color: var(--dhi-tx-dim); font: .55rem 'JetBrains Mono', monospace; letter-spacing: 1px; text-transform: uppercase; }
.cmdbar-metric b { color: var(--dhi-tx); font: 600 .67rem 'JetBrains Mono', monospace; }
.cmdbar-date { color: var(--dhi-tx-dim); font: .58rem 'JetBrains Mono', monospace; text-align: right; }

/* ============ reference-style core workspace ============================== */
.core-hero {
    min-height: 275px;
    margin: 8px 0 10px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(71, 191, 237, .22);
    border-radius: 18px;
    background:
        radial-gradient(circle at 50% 48%, rgba(0, 207, 255, .16), transparent 21%),
        radial-gradient(ellipse at 50% 115%, rgba(0, 152, 220, .34), transparent 49%),
        radial-gradient(circle at 18% 28%, rgba(0, 196, 255, .10) 0 1px, transparent 2px),
        radial-gradient(circle at 82% 26%, rgba(0, 196, 255, .14) 0 1px, transparent 2px),
        linear-gradient(180deg, rgba(1, 16, 30, .93), rgba(2, 14, 25, .98));
    box-shadow: inset 0 0 70px rgba(0, 162, 222, .12), 0 18px 50px rgba(0, 0, 0, .25);
}
.core-hero::before {
    content: "";
    position: absolute;
    inset: -30% -8% 8%;
    background-image: radial-gradient(rgba(119, 224, 255, .72) 0 1px, transparent 1.5px);
    background-size: 92px 76px;
    opacity: .25;
    animation: dhiStarDrift 22s linear infinite alternate;
}
.core-hero::after {
    content: "";
    position: absolute;
    width: 72%;
    height: 31%;
    bottom: -14%;
    border-radius: 50% 50% 0 0;
    background: radial-gradient(ellipse at 50% 0%, #1f9ed2 0 1%, #073c67 8%, #031522 45%, #020910 72%);
    box-shadow: 0 -12px 36px rgba(0, 194, 255, .22);
    transform: perspective(180px) rotateX(12deg);
}
.core-scan {
    position: absolute; inset: 0; z-index: 1; pointer-events: none; overflow: hidden;
}
.core-scan::before {
    content: ""; position: absolute; left: 8%; right: 8%; top: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(95, 226, 255, .8), transparent);
    box-shadow: 0 0 18px rgba(0, 205, 255, .8); animation: dhiScan 5.5s ease-in-out infinite;
}
.hero-particle { position: absolute; z-index: 1; width: 4px; height: 4px; border-radius: 50%; background: #8aefff; box-shadow: 0 0 12px #00cfff; animation: dhiParticleFloat 3.8s ease-in-out infinite; }
.hero-particle.p1 { left: 24%; top: 25%; animation-delay: -.8s; }
.hero-particle.p2 { left: 31%; top: 70%; animation-delay: -2.4s; transform: scale(.7); }
.hero-particle.p3 { right: 27%; top: 28%; animation-delay: -1.6s; }
.hero-particle.p4 { right: 20%; top: 64%; animation-delay: -3s; transform: scale(.65); }
.hero-particle.p5 { left: 14%; top: 48%; animation-delay: -2s; transform: scale(.6); }
.hero-copy, .core-orbit { position: relative; z-index: 1; }
.hero-copy { text-align: center; margin-top: 4px; }
.hero-kicker { color: var(--dhi-accent2); font: 600 .65rem 'JetBrains Mono', monospace; letter-spacing: 3px; text-transform: uppercase; }
.hero-copy h1 { margin: 8px 0 4px; font-size: 1.6rem; letter-spacing: .4px; }
.hero-copy p { margin: 0; color: var(--dhi-tx-dim); font-size: .85rem; }
.core-orbit { width: 170px; height: 170px; display: grid; place-items: center; }
.core-orbit::before, .core-orbit::after {
    content: ""; position: absolute; border: 1px solid rgba(45, 205, 255, .72); border-radius: 50%;
}
.core-orbit::before { inset: 11px; box-shadow: 0 0 20px rgba(0, 210, 255, .38), inset 0 0 16px rgba(0, 210, 255, .25); }
.core-orbit::after { inset: -2px 27px; transform: rotate(55deg); border-color: rgba(103, 224, 255, .42); animation: dhiOrbit 12s linear infinite; }
.core-orbit::marker { content: ""; }
.orbit-ring { position: absolute; inset: 21px; border: 1px dashed rgba(110, 221, 255, .55); border-radius: 50%; animation: dhiOrbitReverse 18s linear infinite; }
.orbit-ring::before, .orbit-ring::after { content: ""; position: absolute; width: 5px; height: 5px; background: var(--dhi-accent2); border-radius: 50%; box-shadow: 0 0 12px var(--dhi-accent2); }
.orbit-ring::before { top: 18px; left: 24px; }
.orbit-ring::after { right: 16px; bottom: 24px; }
.core-emblem {
    width: 78px; height: 78px; display: grid; place-items: center; border-radius: 50%;
    color: #eaffff; font: 700 1.45rem 'Michroma', sans-serif; letter-spacing: 5px;
    background: radial-gradient(circle at 32% 26%, #b8f8ff, #087fc1 34%, #031e3e 73%);
    border: 2px solid rgba(151, 242, 255, .82);
    box-shadow: 0 0 25px #00bfff, 0 0 75px rgba(0, 176, 255, .42), inset 0 0 22px rgba(209, 255, 255, .42);
    animation: dhiBreathe 3s ease-in-out infinite;
}
.core-emblem::before, .core-emblem::after { content: ""; position: absolute; border-radius: 50%; pointer-events: none; }
.core-emblem::before { inset: -13px; border: 1px solid rgba(0, 220, 255, .25); animation: dhiEnergy 2.6s ease-in-out infinite; }
.core-emblem::after { inset: -25px; border: 1px solid rgba(0, 220, 255, .12); animation: dhiEnergy 2.6s .8s ease-in-out infinite; }
.orbit-satellite { position: absolute; width: 7px; height: 7px; border-radius: 50%; background: #d5ffff; box-shadow: 0 0 14px #00d9ff; animation: dhiSatellite 6s linear infinite; }
.orbit-satellite.s2 { animation-duration: 9s; animation-delay: -3s; }
.core-status {
    position: absolute;
    top: calc(50% + 61px);
    left: 50%;
    transform: translateX(-50%);
    width: max-content;
    margin: 0;
    color: var(--dhi-accent);
    font: 600 .65rem 'JetBrains Mono', monospace;
    letter-spacing: 3px;
}
.hero-side-note { position: absolute; top: 45%; width: 120px; color: var(--dhi-tx-dim); font: .61rem/1.7 'JetBrains Mono', monospace; letter-spacing: 1.5px; text-transform: uppercase; }
.hero-side-note::after { content: ""; display: block; width: 28px; height: 2px; margin-top: 8px; background: var(--dhi-accent); animation: dhiPulseLine 2.4s ease-in-out infinite; }
.hero-side-note.left { left: 8%; }
.hero-side-note.right { right: 8%; }
.quick-launch { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin: 10px 0 18px; }
.quick-launch .stButton > button { min-height: 46px; border-color: rgba(31, 183, 233, .34); background: rgba(3, 27, 45, .72); }
.workspace-rail { display: grid; gap: 12px; align-content: start; }
.rail-card { padding: 15px; border: 1px solid rgba(50, 184, 230, .28); border-radius: 12px; background: rgba(3, 25, 40, .78); box-shadow: inset 0 0 24px rgba(0, 180, 255, .05); }
.rail-label { color: var(--dhi-accent2); font: .62rem 'JetBrains Mono', monospace; letter-spacing: 2px; text-transform: uppercase; }
.rail-value { color: var(--dhi-tx); font-size: 1.45rem; font-weight: 700; margin-top: 8px; }
.rail-muted { color: var(--dhi-tx-dim); font-size: .75rem; line-height: 1.45; }
.rail-status { display: flex; justify-content: space-between; padding: 7px 0; color: var(--dhi-tx-dim); font-size: .75rem; border-bottom: 1px solid rgba(126, 208, 238, .10); }
.rail-status b { color: var(--dhi-accent); font-family: 'JetBrains Mono', monospace; font-size: .65rem; }
.side-nav { display: grid; gap: 3px; margin: 14px 0 12px; }
.side-nav-group { color: var(--dhi-accent); font: .57rem 'JetBrains Mono', monospace; letter-spacing: 2px; margin: 10px 8px 5px; text-transform: uppercase; }
.side-nav-item { display: flex; align-items: center; gap: 9px; padding: 8px 9px; border-radius: 7px; color: var(--dhi-tx-dim) !important; font-size: .73rem; }
.side-nav-item.active { color: var(--dhi-tx) !important; background: linear-gradient(90deg, rgba(0, 190, 255, .22), rgba(0, 190, 255, .04)); border-left: 2px solid var(--dhi-accent2); }
.side-nav-item span { width: 15px; text-align: center; color: var(--dhi-accent2) !important; }
.side-nav-rule { height: 1px; margin: 9px 8px; background: var(--dhi-glass-bd); }
.side-session { border: 1px solid var(--dhi-panel-bd); border-radius: 9px; padding: 9px; margin-top: 10px; font: .62rem 'JetBrains Mono', monospace; }
.side-session-row { display: flex; justify-content: space-between; padding: 3px 0; color: var(--dhi-tx-dim); }
.side-session-row b { color: var(--dhi-tx); }

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
.empty-state { text-align: center; padding: 10px 10px 12px; color: var(--dhi-tx-dim); }
.empty-icon { font-size: 1.8rem; margin-bottom: 2px; }
.empty-state h3 { color: var(--dhi-tx); }
.empty-state p { margin: 4px 0; font-size: .78rem; }
.empty-tips { font-size: .72rem; color: var(--dhi-tx-faint); margin-top: 5px; line-height: 1.45; font-family: 'JetBrains Mono', monospace; }
.footer { text-align: center; color: var(--dhi-tx-faint); font-size: .78rem; padding: 20px 0 30px; }
[data-testid="stToast"] { backdrop-filter: blur(12px); }

/* ==== core ignition sequence ============================================== */
.boot-overlay {
    position: fixed; inset: 0; z-index: 2147483647 !important;
    background:
        radial-gradient(circle at 50% 42%, rgba(0, 208, 255, .20), transparent 18%),
        radial-gradient(ellipse at 50% 100%, rgba(0, 133, 196, .18), transparent 52%),
        linear-gradient(180deg, #02070d, #030d17 60%, #02060b);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    animation: dhiBootEnd 3.8s cubic-bezier(.76, 0, .24, 1) forwards;
}
@keyframes dhiBootEnd {
    0% { opacity: 1; }
    72% { opacity: 1; }
    100% { opacity: 0; visibility: hidden; pointer-events: none; }
}
.boot-inner { display: flex; flex-direction: column; align-items: center; gap: 13px; max-width: 92vw; min-width: 300px; }
.boot-orbit { width: 164px; height: 164px; position: relative; display: grid; place-items: center; animation: dhiBootRise .9s ease-out both; }
.boot-orbit::before, .boot-orbit::after { content: ""; position: absolute; border-radius: 50%; border: 1px solid rgba(0, 216, 255, .55); }
.boot-orbit::before { inset: 7px; box-shadow: 0 0 32px rgba(0, 201, 255, .40), inset 0 0 22px rgba(0, 201, 255, .26); }
.boot-orbit::after { inset: -8px 26px; border-style: dashed; animation: dhiOrbit 7s linear infinite; }
.boot-orbit-ring { position: absolute; inset: 20px; border: 1px dashed rgba(127, 236, 255, .66); border-radius: 50%; animation: dhiOrbitReverse 10s linear infinite; }
.boot-orbit-ring::before, .boot-orbit-ring::after { content: ""; position: absolute; width: 5px; height: 5px; border-radius: 50%; background: #74edff; box-shadow: 0 0 12px #00cfff; }
.boot-orbit-ring::before { top: 12px; left: 20px; }
.boot-orbit-ring::after { right: 12px; bottom: 20px; }
.boot-core {
    width: 76px; height: 76px; border-radius: 50%; position: relative; z-index: 1;
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 34% 28%, #d8ffff, #087fc1 38%, #031e3e 76%);
    box-shadow: 0 0 24px #00cfff, 0 0 58px rgba(0, 180, 255, .48), inset 0 0 18px rgba(255, 255, 255, .34);
    font-family: 'Michroma', sans-serif; color: #fff; font-size: 1.25rem; letter-spacing: 3px;
    animation: dhiBootCore 1.7s ease-in-out infinite;
}
@keyframes dhiBootCore { 0%, 100% { transform: scale(.96); } 50% { transform: scale(1.08); } }
@keyframes dhiBootRise { from { opacity: 0; transform: translateY(18px) scale(.84); } to { opacity: 1; transform: none; } }
.boot-title { font-family: 'Michroma', sans-serif; font-size: 1.3rem; letter-spacing: 5px; color: #e8fbff; animation: dhiBootText .7s .25s ease both; }
.boot-ver { font-family: 'JetBrains Mono', monospace; font-size: .65rem; color: #56e0c0; }
.boot-sub { font-family: 'JetBrains Mono', monospace; font-size: .58rem; letter-spacing: 3px; color: #74dfff; text-transform: uppercase; animation: dhiBootText .7s .45s ease both; }
.boot-lines { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: .61rem; color: #8aaeba; }
.boot-line { opacity: 0; animation: dhiBootLine .45s ease forwards; }
.boot-line span { color: #67dfff; }.boot-line b { color: #56e0c0; }
.boot-line:nth-child(1) { animation-delay: .7s; }.boot-line:nth-child(2) { animation-delay: .95s; }.boot-line:nth-child(3) { animation-delay: 1.2s; }
@keyframes dhiBootText { from { opacity: 0; letter-spacing: 11px; } to { opacity: 1; letter-spacing: 5px; } }
@keyframes dhiBootLine { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: none; } }
.boot-wave { width: 280px; height: 22px; max-width: 82vw; background: repeating-linear-gradient(90deg, transparent 0 5px, rgba(0, 208, 255, .52) 6px 7px, transparent 8px 12px); mask-image: linear-gradient(90deg, transparent, #000 18%, #000 82%, transparent); animation: dhiWave 1.1s ease-in-out infinite alternate; }
@keyframes dhiWave { from { transform: scaleY(.35); opacity: .45; } to { transform: scaleY(1); opacity: 1; } }
.boot-progress { width: 280px; height: 3px; max-width: 82vw; background: rgba(255, 255, 255, .08); }
.boot-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #56e0c0, #67c8ff); box-shadow: 0 0 14px rgba(0, 209, 255, .7); animation: dhiBootFill 3.1s linear forwards; }
@keyframes dhiBootFill { from { width: 0%; } to { width: 100%; } }
.boot-pct { font-family: 'JetBrains Mono', monospace; font-size: .58rem; letter-spacing: 3px; color: #7593a0; animation: dhiBootPulse 1.4s ease-in-out infinite; }
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
                        <div class="boot-orbit">
                            <div class="boot-orbit-ring"></div>
                            <div class="boot-core">DHI</div>
                        </div>
            <div class="boot-title">DHI&nbsp;OS <span class="boot-ver">v3.0</span></div>
                        <div class="boot-sub">Neural interface · initializing</div>
            <div class="boot-lines">
                            <div class="boot-line"><span>CORE</span> <b>ONLINE</b></div>
                            <div class="boot-line"><span>VOICE</span> <b>READY</b></div>
                            <div class="boot-line"><span>MEMORY</span> <b>SYNCED</b></div>
            </div>
                        <div class="boot-wave"></div>
                        <div class="boot-progress"><div class="boot-fill"></div></div>
                        <div class="boot-pct">ESTABLISHING PRESENCE</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(uptime_sec: int = 0, session: str = "------",
                  user_name: str | None = None, mic_state: str = "STANDBY",
                  commands: int = 0) -> None:
    """Reference-style telemetry header with only essential status."""
    now = dt.datetime.now().strftime("%H:%M:%S")
    who = user_name or "Operator"
    st.markdown(
        f"""
        <div class="cmdbar">
          <div class="cmdbar-logo">◈ DHI<span class="cmdbar-ver">&nbsp;OS v3.0</span></div>
          <span class="cmdbar-dot"></span>
                    <span class="cmdbar-chip">ONLINE</span>
                    <div class="cmdbar-hello"><b>Hello, {who}</b><small>Always here for you</small></div>
                    <div class="cmdbar-metrics">
                        <div class="cmdbar-metric"><span>Mic</span><b>{mic_state.title()}</b></div>
                        <div class="cmdbar-metric"><span>Lang</span><b>English</b></div>
                        <div class="cmdbar-metric"><span>Commands</span><b>{commands}</b></div>
                        <div class="cmdbar-metric"><span>Uptime</span><b>{_fmt_hhmmss(uptime_sec)}</b></div>
                        <div class="cmdbar-metric"><span>Session</span><b>#{session}</b></div>
                    </div>
                    <div class="cmdbar-date"><strong class="cmdbar-time">{now}</strong><br>Thu, 11 Sep 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_core_hero(mic_state: str = "STANDBY") -> None:
        """Render the cinematic DHI core hero from the reference layout."""
        status = "LISTENING..." if mic_state != "STANDBY" else "READY TO HELP"
        st.markdown(
                f"""
                <section class="core-hero">
                    <div class="core-scan"></div>
                    <span class="hero-particle p1"></span><span class="hero-particle p2"></span>
                    <span class="hero-particle p3"></span><span class="hero-particle p4"></span>
                    <span class="hero-particle p5"></span>
                    <div class="hero-side-note left">THINK<br>UNDERSTAND<br>PLAN<br>EXECUTE<br>FOR YOU</div>
                    <div class="hero-side-note right">A SMARTER<br>DAY BEGINS<br>WITH A<br>SIMPLE HELLO</div>
                    <div class="core-orbit">
                        <div class="orbit-ring"></div>
                        <div class="orbit-satellite"></div><div class="orbit-satellite s2"></div>
                        <div class="core-emblem">DHI</div>
                        <div class="core-status">{status}</div>
                    </div>
                    <div class="hero-copy">
                        <div class="hero-kicker">DHI OS · INTELLIGENCE CORE</div>
                        <h1>How can I help you today?</h1>
                        <p>Talk to me, type a command, or use quick actions below.</p>
                    </div>
                </section>
                """,
                unsafe_allow_html=True,
        )


def render_workspace_rail(uptime_sec: int, commands: int, session: str,
                                                    city: str, mic_state: str) -> None:
        """Render compact ambient context cards beside the conversation."""
        st.markdown(
                f"""
                <aside class="workspace-rail">
                    <div class="rail-card">
                        <div class="rail-label">❝ DAILY SIGNAL</div>
                        <div class="rail-muted" style="margin-top:10px">A small step with Dhi today can make a big difference tomorrow.</div>
                        <div class="rail-label" style="margin-top:12px">— DHI</div>
                    </div>
                    <div class="rail-card">
                        <div class="rail-label">SYSTEM STATUS</div>
                        <div class="rail-status"><span>Core</span><b>ONLINE</b></div>
                        <div class="rail-status"><span>Voice</span><b>{mic_state}</b></div>
                        <div class="rail-status"><span>Commands</span><b>{commands}</b></div>
                        <div class="rail-status"><span>Uptime</span><b>{_fmt_hhmmss(uptime_sec)}</b></div>
                        <div class="rail-status"><span>Session</span><b>#{session}</b></div>
                    </div>
                </aside>
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


def render_sidebar_nav() -> None:
        """Render the minimal navigation rail shown in the reference product UI."""
        st.markdown(
                """
                <nav class="side-nav">
                    <div class="side-nav-group">◉ System</div>
                    <div class="side-nav-item active"><span>⌂</span>Core</div>
                    <div class="side-nav-item"><span>☷</span>Conversation</div>
                    <div class="side-nav-item"><span>▦</span>Memory</div>
                    <div class="side-nav-item"><span>⚒</span>Tools</div>
                    <div class="side-nav-item"><span>♩</span>Voice</div>
                    <div class="side-nav-item"><span>⚙</span>System</div>
                    <div class="side-nav-rule"></div>
                    <div class="side-nav-group">Control</div>
                    <div class="side-nav-item"><span>◉</span>Appearance</div>
                    <div class="side-nav-item"><span>◎</span>Language</div>
                    <div class="side-nav-item"><span>♩</span>Microphone</div>
                    <div class="side-nav-item"><span>⚙</span>Behaviour</div>
                </nav>
                """,
                unsafe_allow_html=True,
        )


def render_sidebar_session(session: str, commands: int, notes: int,
                                                     timers: int, uptime_sec: int) -> None:
        st.markdown(
                f"""
                <div class="side-session">
                    <div class="side-nav-group" style="margin:0 0 5px">Session</div>
                    <div class="side-session-row"><span>Commands</span><b>{commands}</b></div>
                    <div class="side-session-row"><span>Notes</span><b>{notes}</b></div>
                    <div class="side-session-row"><span>Timers</span><b>{timers}</b></div>
                    <div class="side-session-row"><span>Uptime</span><b>{_fmt_hhmmss(uptime_sec)}</b></div>
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


