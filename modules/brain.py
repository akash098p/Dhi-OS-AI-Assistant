"""Intent engine ('brain') for Dhi.

Pure functions: ``respond(command, ctx) -> Reply``. Session effects (notes,
name memory, timers) are expressed through ``ctx`` mutations and ``action``
fields so the UI layer stays in control of state.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from . import llm, skills, speech


@dataclass
class Reply:
    """A structured assistant reply."""

    spoken: str                 # text for TTS
    display: str                # markdown for the chat bubble
    icon: str = "✨"
    action: str | None = None   # "set_name" | "set_timer" | ...
    data: dict = field(default_factory=dict)


_GREETING_RE = re.compile(
    r"^(?:hi+|hello+|hey|yo|hiya|namaste|greetings|good\s*(?:morning|afternoon|evening|day)"
    r"|नमस्ते|नमस्कार|हेलो|हैलो|सुप्रभात)(?=\W|$)"
    r"(?:[\s,!.]*(?:there|echo|alexa|dhi|assistant|team|everyone|friend|धी|डी))*[\s,!.]*$",
    re.IGNORECASE,
)
# Called by name only: "Dhi!" / "ok Dhi" / "धी" -> she answers "Yes? I'm listening."
_ATTENTION_RE = re.compile(
    r"^(?:(?:ok|okay|hey|hi|hello|ओ|अरे|हे|हेय)\s+)?"
    r"(?:dhi|dhee|dee|धी|धि|डी|डि|ढी|दी)[\s!.,?]*$",
    re.IGNORECASE,
)
# Dhi protocol: "good morning", "good evening sir", "good night" ...
_PROTOCOL_GREETING_RE = re.compile(
    r"^(?:good\s+)?(?:morning|afternoon|evening|day|night)"
    r"(?:\s*(?:sir|ma'?am|madam|boss|captain|commander|agent|maestro))?$",
    re.IGNORECASE,
)


def _greeting(ctx: dict) -> Reply:
    hour = dt.datetime.now().hour
    part = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"
    name = ctx.get("user_name")
    who = f", {name}" if name else ""
    return Reply(
        f"Good {part}{who}! Dhi here — how can I help you?",
        f"👋 Good **{part}**{who}! I'm **Dhi** — tap the mic or type below.",
        icon="👋",
    )


def _protocol_greeting(ctx: dict) -> Reply:
    """Dhi protocol greeting: 'good morning sir' -> systems operational."""
    hour = dt.datetime.now().hour
    period = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"
    who = ctx.get("user_name") or "sir"
    return Reply(
        f"Good {period}, {who}. All systems are operational, and I'm at your service.",
        f"🟢 **Good {period}, {who}.** All systems are operational, and I'm at your service.",
        icon="🟢",
    )


def _status_reply(ctx: dict) -> Reply:
    """Dhi system status report powered by live session stats."""
    s = ctx.get("stats") or {}
    commands = int(s.get("commands", 0))
    notes = int(s.get("notes", 0))
    timers = int(s.get("timers", 0))
    uptime = int(s.get("uptime", 0))
    mic = s.get("mic", "STANDBY")
    lang = (s.get("lang") or "English (US)").split("(")[0].strip()
    up_str = skills.format_uptime(uptime)
    level = min(100, 30 + commands * 3 + (0 if mic == "STANDBY" else 9))
    spoken = (f"All systems nominal. Uptime {up_str}. "
              f"{commands} commands executed, {notes} notes stored, {timers} timers active. "
              f"Microphone on {mic}, voice language {lang}.")
    display = (
        "🛰️ **DHI OS · System status**\n\n"
        f"| Metric | Value |\n|---|---|\n"
        f"| ⏱ Uptime | {up_str} |\n"
        f"| ⌨ Commands | {commands} |\n"
        f"| 📝 Notes | {notes} |\n"
        f"| ⏲ Timers | {timers} |\n"
        f"| 🎙 Mic | {mic} |\n"
        f"| 🗣 Voice | {lang} |\n"
        f"| 🧠 Core load | {level}% |\n\n"
        "> ◆ _All systems are nominal._"
    )
    return Reply(spoken, display, icon="🛰️")


def _identity_reply(ctx: dict) -> Reply:
    name = ctx.get("user_name")
    who = f", {name}" if name else ""
    spoken = ("I'm Dhi, your premium voice-first assistant. I listen, think and "
              "respond with more than twenty skills, and I get a little better "
              "every time you talk to me.")
    display = (
        f"🌸 **I'm Dhi{who}** — your premium voice-first assistant.\n\n"
        "I listen, think and speak back — powered by an intent engine with **25+ skills**, "
        "real-time APIs and a premium interface.\n\n"
        "_Say_ **“what can you do”** _for the full tour — or just call my name anytime._"
    )
    return Reply(spoken, display, icon="🤖")


def capabilities_reply() -> Reply:
    spoken = ("I'm Dhi. I can tell time and date, check weather and news, answer questions "
              "with Wikipedia, do math, currency and unit conversions, define words, take "
              "notes, run timers, play music, open websites, search the web, and crack jokes.")
    display = (
        "### 🧰 Everything I can do\n\n"
        "| Skill | Try saying |\n|---|---|\n"
        "| 🕒 Time & date | “what time is it” · “what's the date today” |\n"
        "| 🌦️ Weather | “weather in Tokyo” · “temperature in Paris” |\n"
        "| 📰 News | “show me the news” · “news about cricket” |\n"
        "| 📚 Knowledge | “who is Ada Lovelace” · “tell me about black holes” |\n"
        "| 🧮 Math | “calculate 25 times 8” · “what is 15% of 2400” |\n"
        "| 💱 Currency | “convert 100 usd to inr” |\n"
        "| 📐 Units | “convert 10 km to miles” · “convert 100 f to c” |\n"
        "| 📖 Dictionary | “define serendipity” |\n"
        "| 📝 Notes | “take a note that buy milk” · “show my notes” |\n"
        "| ⏲️ Timers | “set a timer for 5 minutes” |\n"
        "| 🎵 Music | “play Bohemian Rhapsody” |\n"
        "| 🔗 Websites | “open youtube” · “open github” |\n"
        "| 🔍 Search | “search quantum computing” |\n"
        "| 😄 Fun | “tell me a joke” · “flip a coin” · “roll a dice” |\n"
        "| 👤 Personal | “my name is Alex” · “how are you” |"
    )
    return Reply(spoken, display, icon="🧰")


def _timer_reply(lowered: str) -> Reply:
    duration = skills.parse_duration(lowered)
    if duration and duration >= 5:
        label_m = re.search(r"timer\s+(?:for\s+)?(?:named\s+|called\s+)?([a-z0-9 ]+)$", lowered)
        label = label_m.group(1).strip() if label_m else ""
        label = re.sub(r"\bfor\b", " ", label)
        label = re.sub(r"\d+(\.\d+)?\s*(hours?|hrs?|h\b|minutes?|mins?|m\b|seconds?|secs?|s\b)",
                       " ", label).strip()
        label = label.title() if label else "Timer"
        pretty = skills.pretty_duration(duration)
        return Reply(
            f"Timer set for {pretty}.",
            f"⏲️ **Timer set:** {pretty} — _{label}_",
            icon="⏲️",
            action="set_timer",
            data={"seconds": duration, "label": label},
        )
    return Reply(
        "Tell me a duration, like “set a timer for 5 minutes”.",
        "⏲️ Say e.g. **“set a timer for 5 minutes”** or **“timer 90 seconds”**.",
        icon="⏲️",
    )


def _extract_city(lowered: str) -> str:
    m = re.search(
        r"\b(?:weather|temperature|forecast)\s*(?:like|outside)?\s*(?:in|at|for|of)\s+([a-z\s.'-]+)$",
        lowered,
    )
    if m:
        return m.group(1).strip(" ?!.,")
    m = re.search(r"\b(?:in|at|for)\s+([a-z\s.'-]+)$", lowered)
    if m:
        return m.group(1).strip(" ?!.,")
    return ""


def respond(command: str, ctx: dict) -> Reply:
    """Map a user command to a skill. ``ctx``: user_name, notes, default_city."""
    text = speech.strip_wake_word((command or "").strip())
    lowered = text.lower().strip().rstrip("?!. ")

    if not text:
        return Reply("I didn't catch that. Try again?",
                     "🤔 I didn't catch that — say it again, or type below.", icon="👂")

    # -- small talk & meta ---------------------------------------------------
    if _PROTOCOL_GREETING_RE.match(lowered):        # "good morning sir" etc.
        return _protocol_greeting(ctx)
    if _GREETING_RE.match(lowered):
        return _greeting(ctx)
    if _ATTENTION_RE.match(lowered):          # called by name: "Dhi!"
        return Reply(
            "Yes? I'm listening — what would you like?",
            "🌸 **Yes?** I'm listening — what would you like?",
            icon="👂",
        )
    if re.search(r"\bwho (?:are|made|created|built) you\b|\bwho (?:is|'?s) dhi\b|\byour name\b"
                 r"|\bintroduce yourself\b|\btell me about (?:yourself|dhi)\b", lowered):
        if re.search(r"\bwho (?:made|created|built) you\b", lowered):
            return Reply("I was crafted with Python, Streamlit and a lot of coffee.",
                         "☕ I was crafted with **Python, Streamlit** and a *lot* of coffee.",
                         icon="☕")
        return _identity_reply(ctx)
    if re.search(r"\bwhat can you do\b|^help\b|\bhelp me\b|\byour (?:features|commands|skills|capabilities)\b",
                 lowered):
        return capabilities_reply()
    if re.search(r"\bhow are you\b|\bhow'?s it going\b|\bwhat'?s up\b", lowered):
        return Reply("Running at full capacity. All systems green, power reserves optimal.",
                     "⚡ **All systems green.** Core stable, response matrix optimized — ready for your command.",
                     icon="⚡")
    if re.search(r"\b(?:system status|status report|system check|run\s+(?:a\s+)?diagnostic|diagnostics?|all systems)\b",
                 lowered):
        return _status_reply(ctx)
    if re.search(r"\bthanks?\b|\bthank you\b|\bappreciate\b", lowered):
        return Reply("You're welcome!", "💙 You're very welcome!", icon="💙")
    # -- standby protocol -------------------------------------------------------
    if re.search(r"\b(?:shut\s*down|power\s*(?:down|off)|go\s+to\s+sleep|sleep\s+mode|stand\s*by|deactivate|deep\s+sleep)\b",
                 lowered):
        return Reply("Powering down. I'll remain on standby if you need me.",
                     "🔻 **Powering down** — standing by on low power. Say **“wake up”** to bring me back online.",
                     icon="🔻", action="goodbye")
    if re.search(r"\b(?:wake\s*up|start\s*up|power\s*on|power\s*up|boot\s*(?:up)?|initiate|come\s+back\s+online|revive)\b",
                 lowered):
        return Reply("All systems online. Dhi OS reporting for duty.",
                     "🟢 **All systems online** — Dhi OS reporting for duty. What's our next move?",
                     icon="🟢")

    if re.search(r"\b(?:bye|goodbye|see you|good night)\b|\bexit\b|\bshut down\b"
                 r"|\b(?:stop|end) (?:listening|the app)\b", lowered):
        return Reply("Goodbye! Talk to you soon.",
                     "👋 **Goodbye!** Click **Start** whenever you need me again.",
                     icon="👋", action="goodbye")

    # -- timers (before "time") ----------------------------------------------
    if re.search(r"\btimer\b|\bremind me in\b|\balarm in\b", lowered):
        return _timer_reply(lowered)

    # -- time / date / day ----------------------------------------------------
    if re.search(r"\btime\b", lowered) and not re.search(r"\btimer\b", lowered):
        spoken, display = skills.format_time()
        return Reply(spoken, display, icon="🕒")
    if re.search(r"\bdate\b", lowered):
        spoken, display = skills.format_date()
        return Reply(spoken, display, icon="📅")
    if re.search(r"\b(?:what|which)\s+day\b|\bday is it\b|\btoday'?s day\b", lowered):
        spoken, display = skills.format_day()
        return Reply(spoken, display, icon="📆")

    # -- notes ----------------------------------------------------------------
    m = re.match(r"^(?:take|make|add|save|write)\s+(?:a\s+|down\s+)?note(?:\s+(?:that|to|saying|:))?\s*(.+)$",
                 lowered)
    if m and m.group(1).strip():
        note = m.group(1).strip()
        ctx.setdefault("notes", []).append(note)
        return Reply(f"Note saved: {note}.", f"📝 **Note saved**\n\n> {note}",
                     icon="📝", action="add_note")
    if re.search(r"\b(?:show|read|list|see|what are)\b.*\bnotes?\b", lowered):
        notes = ctx.get("notes") or []
        if not notes:
            return Reply("You have no notes yet.",
                         "📝 **Your notes**\n\n_Nothing yet — say “take a note that …” to save one._",
                         icon="📝")
        body = "\n".join(f"{i}. {n}" for i, n in enumerate(notes, 1))
        return Reply(f"You have {len(notes)} notes.", f"📝 **Your notes**\n\n{body}", icon="📝")
    if re.search(r"\b(?:clear|delete|erase|remove|wipe)\b.*\bnotes?\b", lowered):
        count = len(ctx.get("notes") or [])
        if count:
            ctx["notes"] = []
            return Reply(f"Cleared {count} notes.", f"🗑️ Cleared **{count}** note(s).",
                         icon="🗑️", action="clear_notes")
        return Reply("No notes to clear.", "📝 You have no notes to clear.", icon="📝")

    # -- weather --------------------------------------------------------------
    if re.search(r"\bweather\b|\btemperature\b|\bforecast\b|\brain(?:ing)?\b.*\b(?:today|now|outside)\b"
                 r"|\bhow (?:hot|cold)\b", lowered):
        spoken, display = skills.format_weather(_extract_city(lowered), ctx.get("default_city"))
        return Reply(spoken, display, icon="🌦️")

    # -- news -----------------------------------------------------------------
    m = re.search(r"\b(?:news|headlines)\b(?:\s+(?:about|on|for|regarding)\s+(.+))?", lowered)
    if m:
        topic = (m.group(1) or "").strip() or None
        spoken, display = skills.format_news(topic)
        return Reply(spoken, display, icon="📰")

    # -- play music -----------------------------------------------------------
    m = re.match(r"^(?:play|put on|listen to)\s+(.+)$", lowered)
    if m:
        what = m.group(1)
        sp = re.search(r"\bon\s+spotify\s*$", what)
        if sp:
            q = what[:sp.start()].strip() or "music"
            spoken = f"Here's {q} on Spotify."
            display = f"🎧 [{q.title()} on Spotify]({skills.spotify_url(q)})"
        else:
            q = re.sub(r"\s+on\s+youtube\s*$", "", what).strip() or what
            spoken = f"Playing {q}. Here's a YouTube search — pick your track."
            display = f"🎵 **{q.title()}** — [▶️ Open on YouTube]({skills.youtube_url(q)})"
        return Reply(spoken, display, icon="🎵")

    # -- open websites --------------------------------------------------------
    m = re.match(r"^(?:open|launch|go to|visit)\s+(.+)$", lowered)
    if m:
        site = m.group(1).strip().rstrip(".!").removeprefix("the ").strip()
        hit = skills.format_open_site(site)
        if hit:
            return Reply(hit[0], hit[1], icon="🔗")
        return Reply(f"I don't know {site} yet — searching instead.",
                     f"❓ No shortcut for **{site}** — [search Google]({skills.google_url(site)}).",
                     icon="🔗")

    # -- web search -------------------------------------------------------------
    m = re.match(r"^(?:search(?:\s+for)?|google|look\s*up|find)\s+(.+)$", lowered)
    if m:
        spoken, display = skills.format_search(m.group(1))
        return Reply(spoken, display, icon="🔍")

    # -- math -------------------------------------------------------------------
    calc = skills.try_calculate(lowered)
    if calc:
        return Reply(calc[0], calc[1], icon="🧮")

    # -- currency & units ---------------------------------------------------------
    cur = skills.try_currency(lowered)
    if cur:
        return Reply(cur[0], cur[1], icon="💱")
    units = skills.try_units(lowered)
    if units:
        return Reply(units[0], units[1], icon="📐")

    # -- dictionary ----------------------------------------------------------------
    m = re.match(r"^(?:define|definition of|meaning of)\s+(.+)$", lowered)
    if not m:
        m = re.match(r"^what\s+does\s+(.+?)\s+mean$", lowered)
    if m:
        spoken, display = skills.format_definition(m.group(1).strip())
        return Reply(spoken, display, icon="📖")

    # -- fun ------------------------------------------------------------------------
    if re.search(r"\bjoke\b|\bmake me laugh\b|\bsomething funny\b", lowered):
        spoken, display = skills.format_joke()
        return Reply(spoken, display, icon="😄")
    if re.search(r"\bquote\b|\binspire\b|\bmotivat\w+\b", lowered):
        spoken, display = skills.format_quote()
        return Reply(spoken, display, icon="💬")
    if re.search(r"\bfun fact\b|\bfacts?\b|\bsomething (?:interesting|cool)\b|\btell me something\b",
                 lowered):
        spoken, display = skills.format_fact()
        return Reply(spoken, display, icon="💡")
    if re.search(r"\bflip\b.*\bcoin\b|\bcoin\b.*\bflip\b|\bheads or tails\b|\btoss a coin\b", lowered):
        spoken, display = skills.format_coin()
        return Reply(spoken, display, icon="🪙")
    if re.search(r"\broll\b.*\b(?:dice|die)\b|\b(?:dice|die) roll\b", lowered):
        spoken, display = skills.format_dice()
        return Reply(spoken, display, icon="🎲")

    # -- Hindi quick intents (हिंदी) ---------------------------------------------
    if re.search(r"\b(?:समय|टाइम|टाइम क्या|कितने बज)\w*", lowered):
        spoken, display = skills.format_time()
        return Reply(spoken, display, icon="🕒")
    if re.search(r"\b(?:तारीख|तारीख़|आज कौन स|आज की)\w*", lowered):
        spoken, display = skills.format_date()
        return Reply(spoken, display, icon="📅")
    if re.search(r"\b(?:मौसम)\w*", lowered):
        spoken, display = skills.format_weather("", (ctx.get("default_city") or None))
        return Reply(spoken, display, icon="🌦️")
    if re.search(r"\b(?:चुटकुला|मज़ाक|मजाक|जोक)\w*", lowered):
        spoken, display = skills.format_joke()
        return Reply(spoken, display, icon="😄")

    # -- remember name ------------------------------------------------------------
    m = re.match(r"^(?:my name is|call me|i go by)\s+([a-z][a-z' -]{1,30})$", lowered)
    if m:
        name = m.group(1).strip().title()
        return Reply(f"Nice to meet you, {name}!",
                     f"🤝 Nice to meet you, **{name}**! I'll remember that.",
                     icon="🤝", action="set_name", data={"name": name})

    # -- knowledge (Wikipedia) --------------------------------------------------------
    m = re.search(r"\b(?:who\s+(?:is|was|are)|what\s+(?:is|are|was)|tell\s+me\s+about"
                  r"|search\s+wikipedia\s+for)\s+(.+)$", lowered)
    if m:
        spoken, display = skills.wiki_summary(m.group(1).strip())
        return Reply(spoken, display, icon="📚")

    # -- graceful fallback: real answers via the LLM (Gemini → OpenRouter) -------------
    # No regex skill matched — ask the big brain. Recent chat history is passed
    # for follow-ups; ``llm.answer`` returns None when no API key is configured
    # or every provider fails, keeping the old search-link fallback.
    history = list(ctx.get("history") or [])
    if history and history[-1].get("role") == "user":
        history = history[:-1]        # current question is appended by llm.answer
    llm_reply = llm.answer(text, history or None)
    if llm_reply:
        return Reply(llm_reply, f"🌐 {llm_reply}", icon="🌐")

    spoken = f"I'm not sure about that. Here's a web search for {text}."
    display = (f"🤔 I couldn't map **“{text}”** to a skill yet — try one of these:\n\n"
               f"- [🔍 Google]({skills.google_url(text)})\n"
               f"- [🦆 DuckDuckGo]({skills.duck_url(text)})\n\n"
               f"_Say_ **“what can you do”** _to see everything I master._")
    return Reply(spoken, display, icon="🌐")


