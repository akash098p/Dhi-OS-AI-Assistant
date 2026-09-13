"""Skill library for Dhi — weather, news, knowledge, math, utilities.

Every network skill degrades gracefully: helpers return ``(spoken, display)``
tuples and never raise. Pure-python helpers are unit-testable offline.
"""

from __future__ import annotations

import ast
import datetime as dt
import math
import operator
import random
import re
import urllib.parse
import xml.etree.ElementTree as ET

import pyjokes
import requests
import streamlit as st

HTTP_TIMEOUT = 8

# --------------------------------------------------------------------------- #
#  API keys & location
# --------------------------------------------------------------------------- #


def get_openweather_key() -> str:
    try:
        return st.secrets.get("OPENWEATHER_API_KEY", "") or ""
    except Exception:
        return ""


@st.cache_data(ttl=1800, show_spinner=False)
def detect_location() -> str | None:
    """Best-effort IP geolocation, e.g. ``"Mumbai, IN"``."""
    try:
        r = requests.get(
            "http://ip-api.com/json/?fields=status,city,country,countryCode",
            timeout=HTTP_TIMEOUT,
        )
        data = r.json()
        if data.get("status") == "success" and data.get("city"):
            return f"{data['city']}, {data.get('countryCode', '')}".strip(", ")
    except Exception:
        return None
    return None


# --------------------------------------------------------------------------- #
#  Weather
# --------------------------------------------------------------------------- #
_WIND_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _weather_icon(code: int) -> str:
    if 200 <= code < 300:
        return "⛈️"
    if 300 <= code < 400:
        return "🌦️"
    if 500 <= code < 600:
        return "🌧️"
    if 600 <= code < 700:
        return "❄️"
    if 700 <= code < 800:
        return "🌫️"
    if code == 800:
        return "☀️"
    if code == 801:
        return "🌤️"
    if code == 802:
        return "⛅"
    return "☁️"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(city: str, api_key: str) -> dict | None:
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"appid": api_key, "q": city, "units": "metric"},
            timeout=HTTP_TIMEOUT,
        )
        data = r.json()
        if data.get("cod") != 200:
            return {"error": data.get("message", "city not found")}
        main = data["main"]
        wind = data.get("wind", {})
        wx = data["weather"][0]
        return {
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", ""),
            "temp": round(main.get("temp", 0)),
            "feels": round(main.get("feels_like", 0)),
            "humidity": main.get("humidity", 0),
            "desc": (wx.get("description") or "").capitalize(),
            "icon": _weather_icon(wx.get("id", 800)),
            "wind": round(wind.get("speed", 0) * 3.6),
            "dir": _WIND_DIRS[int((wind.get("deg", 0) % 360) // 45)],
            "rain": 200 <= wx.get("id", 800) < 700,
        }
    except Exception:
        return None


def format_weather(city: str = "", default_city: str | None = None) -> tuple[str, str]:
    key = get_openweather_key()
    if not key:
        msg = "Add a free OpenWeatherMap key to `.streamlit/secrets.toml` as `OPENWEATHER_API_KEY`."
        return "I need an OpenWeatherMap API key for weather.", f"🔑 {msg}"

    target = (city or "").strip() or (default_city or "").strip() or detect_location() or "Kolkata"
    data = fetch_weather(target, key)
    if data is None:
        return ("Sorry, the weather service is not responding right now.",
                "🌩️ Weather service unavailable — try again in a moment.")
    if "error" in data:
        return (f"Sorry, I couldn't find the weather for {target}.",
                f"❌ Couldn't find weather for **{target.title()}** — _{data['error']}_")

    spoken = (f"It's {data['temp']} degrees in {data['city']} with {data['desc']}. "
              f"Feels like {data['feels']}. Humidity is {data['humidity']} percent.")
    if data["rain"]:
        spoken += " You might want an umbrella!"
    display = (
        f"{data['icon']} **{data['temp']}°C** in {data['city']}, {data['country']}  \n"
        f"_{data['desc']}_  \n\n"
        f"| Feels like | Humidity | Wind |\n|---|---|---|\n"
        f"| {data['feels']}°C | {data['humidity']}% | {data['wind']} km/h {data['dir']} |"
    )
    if data["rain"]:
        display = "☔ " + display
    return spoken, display


# --------------------------------------------------------------------------- #
#  News (Google News RSS — free, no API key)
# --------------------------------------------------------------------------- #


@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(topic: str | None = None, limit: int = 6) -> list[dict]:
    if topic:
        url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(topic)
               + "&hl=en-US&gl=US&ceid=US:EN")
    else:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:EN"
    try:
        r = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
        items: list[dict] = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            source = (item.findtext("source") or "Google News").strip()
            if title:
                items.append({"title": re.split(r"\s+-\s+", title, maxsplit=1)[0],
                              "link": link, "source": source})
            if len(items) >= limit:
                break
        return items
    except Exception:
        return []


def format_news(topic: str | None = None) -> tuple[str, str]:
    items = fetch_news(topic)
    label = topic or "Top stories"
    if not items:
        return ("Sorry, I couldn't fetch the news right now.",
                f"📡 Couldn't fetch **{label}** — try again in a moment.")
    lead = ". ".join(i["title"] for i in items) + "."
    spoken = f"Here are the top headlines{' about ' + topic if topic else ''}. {lead}"
    lines = "\n".join(f"- [{i['title']}]({i['link']}) — _{i['source']}_" for i in items)
    return spoken, f"📰 **{label}**\n\n{lines}"


# --------------------------------------------------------------------------- #
#  Knowledge (Wikipedia)
# --------------------------------------------------------------------------- #


def wiki_summary(query: str) -> tuple[str, str]:
    import wikipedia as wiki

    try:
        matches = wiki.search(query, results=1)
        if not matches:
            return (f"Sorry, I couldn't find anything about {query}.",
                    f"🔍 No Wikipedia results for **{query}**.")
        title = matches[0]
        summary = wiki.summary(title, sentences=4, auto_suggest=False)
        url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        # Speak the *whole* summary — Dhi reads back everything she shows.
        spoken = summary.rstrip(".") + "."
        display = f"📚 **{title}**\n\n{summary}\n\n[Read more on Wikipedia]({url})"
        return spoken, display
    except wiki.exceptions.DisambiguationError:
        return (f"There are multiple matches for {query}. Please be more specific.",
                f"⚠️ Multiple Wikipedia entries match **{query}** — be more specific.")
    except wiki.exceptions.PageError:
        return (f"Sorry, I could not find any information on {query}.",
                f"🔍 No Wikipedia page found for **{query}**.")
    except Exception:
        return ("Sorry, Wikipedia seems unreachable right now.",
                "📡 Wikipedia is unreachable right now.")


# --------------------------------------------------------------------------- #
#  Dictionary (dictionaryapi.dev — free, no key)
# --------------------------------------------------------------------------- #


@st.cache_data(ttl=86400, show_spinner=False)
def _define_primary(word: str) -> dict | None:
    """dictionaryapi.dev — rich definitions with phonetics & examples."""
    try:
        r = requests.get(
            "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(word),
            timeout=12,
        )
        if r.status_code != 200:
            return None
        entry = r.json()[0]
        for meaning in entry.get("meanings", []):
            defs = meaning.get("definitions", [])
            if defs:
                return {
                    "word": entry.get("word", word),
                    "phonetic": entry.get("phonetic", ""),
                    "pos": meaning.get("partOfSpeech", ""),
                    "definition": defs[0].get("definition", ""),
                    "example": defs[0].get("example", ""),
                }
    except Exception:
        return None
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def _define_fallback(word: str) -> dict | None:
    """Wiktionary REST API — resilient backup dictionary source."""
    try:
        r = requests.get(
            "https://en.wiktionary.org/api/rest_v1/page/definition/"
            + urllib.parse.quote(word),
            timeout=12,
            headers={"User-Agent": "Dhi/2.1"},
        )
        if r.status_code != 200:
            return None
        for entry in r.json().get("en", []):
            defs = entry.get("definitions", [])
            if not defs:
                continue
            import html
            import re as _re

            definition = _re.sub(r"<[^>]+>", "", defs[0].get("definition", "")).strip()
            if definition:
                example_list = defs[0].get("examples") or []
                example = ""
                if example_list:
                    example = _re.sub(r"<[^>]+>", "", example_list[0].get("example", ""))
                    example = html.unescape(example).strip()
                return {
                    "word": word,
                    "phonetic": "",
                    "pos": entry.get("partOfSpeech", ""),
                    "definition": html.unescape(definition),
                    "example": example,
                }
    except Exception:
        return None
    return None


def define_word(word: str) -> dict | None:
    return _define_primary(word) or _define_fallback(word)


def format_definition(word: str) -> tuple[str, str]:
    data = define_word(word.strip())
    if not data:
        return (f"Sorry, I couldn't find a definition for {word}.",
                f"📖 No definition found for **{word}**.")
    spoken = f"{data['word']}, {data['pos']}: {data['definition']}"
    if data["example"]:
        spoken += f" For example, {data['example']}"
    display = (f"📖 **{data['word']}** {data['phonetic']}  _({data['pos']})_\n\n"
               f"> {data['definition']}")
    if data["example"]:
        display += f"\n\n💬 _“{data['example']}”_"
    return spoken, display


# --------------------------------------------------------------------------- #
#  Fun: quotes, facts, jokes, coin, dice
# --------------------------------------------------------------------------- #
FALLBACK_QUOTES = [
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Programs must be written for people to read.", "Harold Abelson"),
    ("Any sufficiently advanced technology is indistinguishable from magic.", "Arthur C. Clarke"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
]

FUN_FACTS = [
    "Honey never spoils — 3,000-year-old honey found in Egyptian tombs is still edible.",
    "Octopuses have three hearts and blue blood.",
    "A day on Venus is longer than its year.",
    "Bananas are berries, but strawberries are not.",
    "There are more possible chess games than atoms in the observable universe.",
    "The Eiffel Tower grows about 15 centimetres taller in summer due to heat expansion.",
    "Wombat poop is cube-shaped.",
    "The first computer bug was an actual moth found inside a Harvard computer in 1947.",
    "Sharks existed before trees — by about 50 million years.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "A bolt of lightning is about five times hotter than the surface of the Sun.",
    "The word 'robot' comes from the Czech word 'robota', meaning forced labour.",
    "Antarctica is technically the world's largest desert.",
    "Cows have best friends and get stressed when separated from them.",
    "Sound travels about four times faster in water than in air.",
    "Nintendo was founded in 1889 — it originally made playing cards.",
]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_quote() -> tuple[str | None, str | None]:
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=HTTP_TIMEOUT)
        data = r.json()[0]
        return data.get("q"), data.get("a")
    except Exception:
        return None, None


def format_quote() -> tuple[str, str]:
    quote, author = fetch_quote()
    if not quote:
        quote, author = random.choice(FALLBACK_QUOTES)
    return (f"Here's a quote by {author}. {quote}",
            f"💬 _“{quote}”_\n\n**— {author}**")


def format_fact() -> tuple[str, str]:
    fact = random.choice(FUN_FACTS)
    return f"Here's a fun fact. {fact}", f"💡 {fact}"


def format_joke() -> tuple[str, str]:
    try:
        joke = pyjokes.get_joke()
    except Exception:
        joke = "Why do programmers prefer dark mode? Because light attracts bugs."
    return joke, f"😄 {joke}"


def format_coin() -> tuple[str, str]:
    result = random.choice(["Heads", "Tails"])
    return f"{result}!", f"🪙 **{result}!**"


def format_dice(sides: int = 6) -> tuple[str, str]:
    roll = random.randint(1, max(2, sides))
    return f"You rolled a {roll}.", f"🎲 You rolled **{roll}** (d{max(2, sides)})"


# --------------------------------------------------------------------------- #
#  Time / date
# --------------------------------------------------------------------------- #


def format_time() -> tuple[str, str]:
    now = dt.datetime.now()
    pretty = now.strftime("%I:%M %p").lstrip("0")
    return f"The current time is {pretty}.", f"🕒 It's **{pretty}**"


def format_date() -> tuple[str, str]:
    now = dt.datetime.now()
    pretty = now.strftime("%A, %B %d, %Y")
    return f"Today is {pretty}.", f"📅 Today is **{pretty}**"


def format_day() -> tuple[str, str]:
    day = dt.datetime.now().strftime("%A")
    return f"Today is {day}.", f"📆 Today is **{day}**"


def format_uptime(seconds: int) -> str:
    """Pretty-print an uptime duration, e.g. 3725 -> '1h 02m 05s'."""
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


# --------------------------------------------------------------------------- #
#  Links, sites & search
# --------------------------------------------------------------------------- #

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "maps": "https://maps.google.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "chatgpt": "https://chat.openai.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
}


def google_url(q: str) -> str:
    return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)


def duck_url(q: str) -> str:
    return "https://duckduckgo.com/?q=" + urllib.parse.quote_plus(q)


def youtube_url(q: str) -> str:
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)


def spotify_url(q: str) -> str:
    return "https://open.spotify.com/search/" + urllib.parse.quote_plus(q)


def format_search(query: str) -> tuple[str, str]:
    spoken = f"Here's what I found on the web for {query}."
    display = (f"🔍 Search results for **{query}**\n\n"
               f"- [Google]({google_url(query)})\n"
               f"- [DuckDuckGo]({duck_url(query)})\n"
               f"- [YouTube]({youtube_url(query)})")
    return spoken, display


def format_open_site(site: str) -> tuple[str, str] | None:
    url = SITES.get(site)
    if not url:
        return None
    return f"Opening {site}.", f"🔗 [{site.title()}]({url})"


# --------------------------------------------------------------------------- #
#  Calculator — word math + safe AST evaluation (no eval() of arbitrary code)
# --------------------------------------------------------------------------- #
_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000,
}
_ALT = "|".join(_NUMBER_WORDS)
_NUMBER_SEQ_RE = re.compile(
    rf"\b(?:{_ALT})(?:(?:\s+and\s+|\s+|-)(?:{_ALT}))*\b", re.IGNORECASE
)
_PERCENT_RE = re.compile(r"([\d.]+)\s*(?:%|percent)\s*of\s+([\d.]+)", re.IGNORECASE)
_SQRT_RE = re.compile(r"\b(?:square\s*root\s*(?:of)?|root\s+of)\s*([\d.]+)", re.IGNORECASE)
_MATH_SUBS = [
    (re.compile(r"\bplus\b|\badded\s+to\b", re.IGNORECASE), "+"),
    (re.compile(r"\bminus\b|\bsubtracted\s+from\b|\bless\b", re.IGNORECASE), "-"),
    (re.compile(r"\btimes\b|\bmultiplied\s+by\b|\binto\b|\bx\b", re.IGNORECASE), "*"),
    (re.compile(r"\bdivided\s+by\b|\bdivided\b|\bover\b", re.IGNORECASE), "/"),
    (re.compile(r"\bmod(?:ulo)?\b", re.IGNORECASE), "%"),
    (re.compile(r"\bto\s+the\s+power\s+(?:of\s+)?|\braised\s+to\s+(?:the\s+)?(?:power\s+of\s+)?",
                re.IGNORECASE), "**"),
    (re.compile(r"\bsquared\b", re.IGNORECASE), "**2"),
    (re.compile(r"\bcubed\b", re.IGNORECASE), "**3"),
]
_BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod, ast.Pow: operator.pow}
_UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"sqrt": math.sqrt, "log": math.log10, "ln": math.log, "abs": abs,
          "round": round, "sin": math.sin, "cos": math.cos, "tan": math.tan}
_CONSTS = {"pi": math.pi, "e": math.e}


def _seq_value(seq: str) -> int:
    """'one hundred twenty' -> 120, 'two thousand five hundred' -> 2500."""
    total, current = 0, 0
    for token in re.split(r"(?:\s+and\s+|\s+|-)", seq.strip().lower()):
        value = _NUMBER_WORDS.get(token)
        if value is None:
            continue
        if value == 100:
            current = max(current, 1) * 100
        elif value >= 1000:
            total += max(current, 1) * value
            current = 0
        else:
            current += value
    return total + current


def words_to_numbers(text: str) -> str:
    return _NUMBER_SEQ_RE.sub(lambda m: str(_seq_value(m.group(0))), text)


def safe_eval(expression: str) -> float:
    """Evaluate arithmetic safely via the AST — no arbitrary code execution."""
    node = ast.parse(expression.strip(), mode="eval").body
    return _eval_node(node)


def _eval_node(node):
    if (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Name) and node.id.lower() in _CONSTS:
        return _CONSTS[node.id.lower()]
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id.lower() in _FUNCS and not node.keywords):
        return _FUNCS[node.func.id.lower()](*[_eval_node(a) for a in node.args])
    raise ValueError("unsupported expression")


def fmt_number(value) -> str:
    """Human-friendly number formatting."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, int):
        return f"{value:,}" if abs(value) >= 10_000 else str(value)
    return f"{value:,.6g}"


def try_calculate(command: str) -> tuple[str, str] | None:
    """Return (spoken, display) if the command is arithmetic, else None."""
    text = command.strip().rstrip("?!. ")
    lowered = text.lower()

    triggered = re.match(r"^(?:calculate|compute|solve|eval(?:uate)?)\s+(.+)$", lowered)
    casual = re.match(r"^(?:what(?:'?s| is)|how much is)\s+(.+)$", lowered)
    if triggered:
        source = triggered.group(1)
    elif casual:
        source = casual.group(1)
    elif re.search(r"[\d)]\s*[+\-*/^%]\s*[\d(]", text):
        source = lowered
    else:
        return None

    expr = words_to_numbers(source)
    expr = re.sub(r"\b(?:the|a|an|please)\b", " ", expr)   # filler words
    expr = _PERCENT_RE.sub(r"((\1)/100)*\2", expr)
    expr = _SQRT_RE.sub(r"sqrt(\1)", expr)
    for pattern, replacement in _MATH_SUBS:
        expr = pattern.sub(replacement, expr)
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    expr = re.sub(r"[=]", " ", expr)
    expr = re.sub(r"\s+", " ", expr).strip()

    if not expr or not re.search(r"\d", expr):
        return None
    try:
        result = safe_eval(expr)
    except Exception:
        return None

    result_fmt = fmt_number(result)
    spoken = f"The answer is {result_fmt}."
    display = f"🧮 `{source.strip()}` = **{result_fmt}**"
    return spoken, display


# --------------------------------------------------------------------------- #
#  Currency conversion (open.er-api.com — free, no key)
# --------------------------------------------------------------------------- #
_CURRENCY_NAMES = {
    "dollar": "USD", "dollars": "USD", "usd": "USD", "us dollar": "USD",
    "euro": "EUR", "euros": "EUR", "eur": "EUR",
    "pound": "GBP", "pounds": "GBP", "gbp": "GBP", "quid": "GBP",
    "rupee": "INR", "rupees": "INR", "inr": "INR",
    "yen": "JPY", "jpy": "JPY",
    "yuan": "CNY", "cny": "CNY", "renminbi": "CNY",
    "dirham": "AED", "dirhams": "AED", "aed": "AED",
    "riyal": "SAR", "riyals": "SAR",
    "australian dollar": "AUD", "canadian dollar": "CAD", "cad": "CAD",
    "swiss franc": "CHF", "chf": "CHF", "franc": "CHF",
    "bitcoin": "BTC", "btc": "BTC", "ethereum": "ETH", "eth": "ETH",
    "won": "KRW", "ruble": "RUB", "rub": "RUB", "real": "BRL", "reais": "BRL",
    "lira": "TRY", "zloty": "PLN", "baht": "THB", "ringgit": "MYR",
    "peso": "MXN", "pesos": "MXN",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rates(base: str) -> dict | None:
    try:
        r = requests.get(f"https://open.er-api.com/v6/latest/{base.upper()}",
                         timeout=HTTP_TIMEOUT)
        data = r.json()
        if data.get("result") == "success":
            return data.get("rates", {})
    except Exception:
        pass
    return None


def _currency_code(raw: str) -> str | None:
    raw = raw.strip()
    return _CURRENCY_NAMES.get(raw) or (raw.upper() if re.fullmatch(r"[a-z]{3}", raw) else None)


def try_currency(command: str) -> tuple[str, str] | None:
    text = command.lower().strip().rstrip("?!. ")
    if not re.search(r"\b(convert|exchange|currency)\b", text):
        return None
    cleaned = re.sub(r"\b(?:convert|exchange|currency|rate|rates|from)\b", " ", text)
    m = re.match(r"\s*([\d,.]+)?\s*([a-z][a-z ]*?)\s*(?:to|into|in)\s+([a-z][a-z ]*?)\s*$",
                 cleaned)
    if not m:
        return None
    amount_str, src_raw, dst_raw = m.group(1), m.group(2), m.group(3)
    amount = float(amount_str.replace(",", "")) if amount_str else 1.0
    src, dst = _currency_code(src_raw), _currency_code(dst_raw)
    if not src or not dst:
        return None
    rates = fetch_rates(src)
    if not rates or dst not in rates:
        return ("Sorry, I couldn't fetch exchange rates right now.",
                "💱 Couldn't fetch exchange rates — try again shortly.")
    converted = amount * rates[dst]
    spoken = (f"{fmt_number(amount)} {src} equals "
              f"{fmt_number(round(converted, 2))} {dst}.")
    display = (f"💱 **{fmt_number(amount)} {src}** = "
               f"**{fmt_number(round(converted, 2))} {dst}**\n\n"
               f"_1 {src} = {round(rates[dst], 4)} {dst}_")
    return spoken, display


# --------------------------------------------------------------------------- #
#  Unit conversion (length / mass / volume / temperature)
# --------------------------------------------------------------------------- #
_LENGTH = {
    "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0, "kms": 1000.0,
    "m": 1.0, "meter": 1.0, "meters": 1.0,
    "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
    "mm": 0.001, "mile": 1609.344, "miles": 1609.344,
    "yard": 0.9144, "yards": 0.9144, "feet": 0.3048, "foot": 0.3048, "ft": 0.3048,
    "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
    "nautical mile": 1852.0, "nautical miles": 1852.0,
}
_MASS = {
    "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0, "kilo": 1.0, "kilos": 1.0,
    "g": 0.001, "gram": 0.001, "grams": 0.001, "mg": 1e-6,
    "pound": 0.45359237, "pounds": 0.45359237, "lb": 0.45359237, "lbs": 0.45359237,
    "ounce": 0.028349523125, "ounces": 0.028349523125, "oz": 0.028349523125,
    "ton": 1000.0, "tonne": 1000.0, "tons": 1000.0,
}
_VOLUME = {
    "liter": 1.0, "liters": 1.0, "litre": 1.0, "litres": 1.0, "l": 1.0,
    "ml": 0.001, "gallon": 3.785411784, "gallons": 3.785411784, "gal": 3.785411784,
}
_TEMP = {"celsius": "C", "centigrade": "C", "°c": "C", "c": "C",
         "fahrenheit": "F", "°f": "F", "f": "F", "kelvin": "K", "k": "K"}


def _convert_temp(v: float, src: str, dst: str) -> float:
    if src == dst:
        return v
    c = v if src == "C" else (v - 32) * 5 / 9 if src == "F" else v - 273.15
    if dst == "C":
        return c
    if dst == "F":
        return c * 9 / 5 + 32
    return c + 273.15


def try_units(command: str) -> tuple[str, str] | None:
    text = command.lower().strip().rstrip("?!. ")
    if not re.search(r"\bconvert\b", text):
        return None
    cleaned = re.sub(r"\bconvert\b", " ", text)
    m = re.match(r"\s*([\d,.]+)\s*([a-z °]+?)\s*(?:to|into|in)\s+([a-z °]+?)\s*$", cleaned)
    if not m:
        return None
    amount = float(m.group(1).replace(",", ""))
    src_raw, dst_raw = m.group(2).strip(), m.group(3).strip()

    s_t, d_t = _TEMP.get(src_raw), _TEMP.get(dst_raw)
    if s_t and d_t:
        result = round(_convert_temp(amount, s_t, d_t), 2)
        spoken = f"{fmt_number(amount)} degrees {src_raw} is {fmt_number(result)} degrees {dst_raw}."
        display = f"📐 **{amount:g}°{s_t}** = **{result:g}°{d_t}**"
        return spoken, display

    for table in (_LENGTH, _MASS, _VOLUME):
        if src_raw in table and dst_raw in table:
            result = round(amount * table[src_raw] / table[dst_raw], 4)
            spoken = f"{fmt_number(amount)} {src_raw} equals {fmt_number(result)} {dst_raw}."
            display = (f"📐 **{fmt_number(amount)} {src_raw}** = "
                       f"**{fmt_number(result)} {dst_raw}**")
            return spoken, display
    return None


# --------------------------------------------------------------------------- #
#  Timer parsing
# --------------------------------------------------------------------------- #


def parse_duration(text: str) -> int | None:
    """'5 minutes and 30 seconds' -> 330 (seconds); None if no duration found."""
    total = 0.0
    found = False
    for m in re.finditer(
        r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h\b|minutes?|mins?|m\b|seconds?|secs?|s\b)",
        text, re.IGNORECASE,
    ):
        value = float(m.group(1))
        unit = m.group(2).lower()
        found = True
        if unit.startswith("h"):
            total += value * 3600
        elif unit.startswith("m"):
            total += value * 60
        else:
            total += value
    return int(total) if found and total >= 1 else None


def pretty_duration(seconds: int) -> str:
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours and minutes:
        return f"{hours} hr {minutes} min {sec} sec"
    if hours:
        return f"{hours} hr {sec} sec" if sec else f"{hours} hr"
    if minutes and sec:
        return f"{minutes} min {sec} sec"
    if minutes:
        return f"{minutes} minute" + ("s" if minutes != 1 else "")
    return f"{sec} second" + ("s" if sec != 1 else "")






