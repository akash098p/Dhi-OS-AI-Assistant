"""LLM "big brain" for Dhi — Gemini primary, OpenRouter fallback.

When the regex intent engine (``modules/brain.py``) can't map a command to a
skill, this module gives Dhi real, free-form answers instead of dead search
links:

* **Primary** — Google Gemini (free key from https://aistudio.google.com/apikey)
* **Fallback** — OpenRouter's OpenAI-compatible chat API (any model)
* **Real-time grounding** — for time-sensitive questions, the top DuckDuckGo
  snippets (no key needed) are fetched and injected into the prompt, so answers
  reflect *current* information. Gemini's native Google Search tool is also
  attempted when the SDK supports it (best-effort; free tier may ignore it).

Keys are read from Streamlit secrets first, then environment variables:

    GEMINI_API_KEY     ... Google AI Studio key (primary provider)
    OPENROUTER_API_KEY ... OpenRouter key (fallback provider)
    GEMINI_MODEL       ... optional override, default ``gemini-2.5-flash``
    OPENROUTER_MODEL   ... optional override, default ``meta-llama/...:free``

Everything here is defensive: any failure returns ``None`` and callers simply
fall back to the old "here are search links" behaviour. Nothing raises.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import urllib.parse

HTTP_TIMEOUT = 12
SEARCH_TIMEOUT = 6
_DDG_SEARCH_URL = "https://html.duckduckgo.com/html/?q="
_DDG_LITE_URL = "https://lite.duckduckgo.com/lite/?q="
_BING_SEARCH_URL = "https://www.bing.com/search?q="
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# OpenRouter keeps retiring its popular ":free" slugs (e.g. llama-3.3-70b
# now returns 404 "unavailable for free"). These are verified-live free text
# models (probed 2026-09) that are tried in order before giving up.
_OPENROUTER_FREE_FALLBACKS = (
    "poolside/laguna-s-2.1:free",
    "dots-studio/dots-3-note-preview:free",
    "nex-agi/nex-n2.5-mini:free",
    "nvidia/nemotron-3.5-lightning:free",
)

# --------------------------------------------------------------------------- #
#  Keys & models
# --------------------------------------------------------------------------- #


def _secret(name: str) -> str:
    try:
        import streamlit as st  # local import: safe outside a Streamlit run
        return str(st.secrets.get(name, "") or "").strip()
    except Exception:
        return ""


def gemini_key() -> str:
    return (_secret("GEMINI_API_KEY")
            or os.environ.get("GEMINI_API_KEY", "").strip())


def openrouter_key() -> str:
    return (_secret("OPENROUTER_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY", "").strip())


def gemini_model() -> str:
    return (_secret("GEMINI_MODEL")
            or os.environ.get("GEMINI_MODEL", "").strip()
            or "gemini-2.5-flash")


def openrouter_model() -> str:
    return (_secret("OPENROUTER_MODEL")
            or os.environ.get("OPENROUTER_MODEL", "").strip()
            or _OPENROUTER_FREE_FALLBACKS[0])


def enabled() -> bool:
    """True when at least one LLM provider is configured."""
    return bool(gemini_key() or openrouter_key())


# --------------------------------------------------------------------------- #
#  Prompt building & real-time grounding
# --------------------------------------------------------------------------- #

_SYSTEM_PROMPT = (
    "You are Dhi, a premium voice-first AI assistant in a desktop app. "
    "Give complete, detailed and genuinely useful answers — never terse "
    "one-liners. Normally aim for a focused answer of about 4-8 sentences "
    "(a short paragraph that is comfortable to read aloud), using short "
    "bullet lists or numbered steps when they genuinely help. Include the "
    "key background and facts the user needs, and always finish with a "
    "one-line summary of your answer. "
    "Answer in the same language the user writes. "
    "If 'Recent web info' is included just above the user message, it contains "
    "live search snippets — use that information in your answer, mention one "
    "source in parentheses when you rely on it, and never claim you cannot "
    "access the web or lack real-time data, because those facts are provided "
    "just above. If you genuinely don't know, say so honestly instead of "
    "guessing. "
    "The current date is provided at the end of this instruction — treat it "
    "as 'today' and judge every date against it. For questions about "
    "upcoming, latest or current things, use ONLY events dated today or in "
    "the future, and never present past events as upcoming. If the snippets "
    "look older than today, say so, give the freshest confirmed information "
    "you have, and point the user to a live source for the very latest "
    "instead of inventing dates."
)


def _today_line() -> str:
    """'Today's date: …' line injected into every LLM system prompt."""
    return f"Today's date: {dt.datetime.now():%A, %d %B %Y}."


def _system_prompt() -> str:
    """System prompt with the current date appended (freshness anchor)."""
    return f"{_SYSTEM_PROMPT}\n{_today_line()}"

_TIME_WORDS = (
    "today", "tonight", "yesterday", "tomorrow", "latest", "recent", "now",
    "current", "live", "breaking", "news", "score", "match", "result",
    "winner", "price", "stock", "share", "market", "election", "update",
    "schedule", "forecast", "weather", "president", "pm", "minister",
    "ceo", "release", "version",
)


def should_search(question: str) -> bool:
    """Heuristic: does this question need *current* web information?"""
    q = (question or "").lower()
    if re.search(r"\b(?:19|20)\d{2}\b", q):       # any year → time-sensitive
        return True
    return any(word in q for word in _TIME_WORDS)


def _search_query(question: str) -> str:
    """Bias time-sensitive searches toward the current year.

    'upcoming matches' alone returns stale schedule pages from months ago;
    appending today's year pulls freshest-first results. Questions that
    already contain a year are left untouched.
    """
    if re.search(r"\b20\d{2}\b", question):
        return question
    return f"{question} {dt.datetime.now().year}"


_DDG_RE = re.compile(
    r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
    r'.{0,400}?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
    re.DOTALL,
)
_DDG_LITE_RE = re.compile(
    r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
    r'.{0,400}?<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
    re.DOTALL,
)
_BING_RE = re.compile(
    r'<li[^>]*class="b_algo"[^>]*>.{0,300}?<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
    r'.{0,600}?<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>(.*?)</p>',
    re.DOTALL,
)


def _snips(html_text: str, patterns, limit: int) -> list[str]:
    """Extract (title, snippet) pairs from a search-results page."""
    import html as html_mod

    found: list[str] = []
    for pat in patterns:
        for m in pat.finditer(html_text):
            title = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
            snippet = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()
            if title and snippet and not re.search(r"\bAd\b", title + " " + snippet):
                found.append("\u2022 " + title + ": " + snippet)
            if len(found) >= limit:
                return found
        if found:
            return found
    return found


def web_search(query: str, limit: int = 3) -> str | None:
    """Fetch web snippets (Bing -> DuckDuckGo, no API key) as grounding.

    Returns a compact block like "Recent web info (from web search):"
    plus one bullet line per result, or ``None`` on any failure. Bing is
    tried first because DuckDuckGo often rate-limits server IPs (HTTP 202
    anomaly pages).
    """
    try:
        import requests
    except Exception:
        return None

    q = urllib.parse.quote_plus(query)
    for name, url, pats in (
        ("bing", _BING_SEARCH_URL, (_BING_RE,)),
        ("ddg", _DDG_SEARCH_URL, (_DDG_RE,)),
        ("ddg-lite", _DDG_LITE_URL, (_DDG_LITE_RE,)),
    ):
        try:
            resp = requests.get(url + q, timeout=SEARCH_TIMEOUT,
                                headers={"User-Agent": _UA})
            if resp.status_code != 200 or not resp.text:
                continue
            found = _snips(resp.text, pats, limit)
            if found:
                return (f"Recent web info (fetched {dt.datetime.now():%d %b %Y}, "
                        f"from web search):\n" + "\n".join(found))
        except Exception:
            continue
    return None


def _crop(text: str, n: int = 400) -> str:
    text = (text or "").replace("\n", " ").strip()
    return text[:n] + ("…" if len(text) > n else "")


def _chat_rows(question: str, history, snippets):
    """Rebuild recent chat as [(role, text), ...] + grounded current question."""
    rows: list[tuple[str, str]] = []
    for msg in (history or [])[-8:]:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        rows.append(("model" if role == "assistant" else "user", _crop(content)))
    if snippets:
        rows.append(("user", f"{snippets}\n\n(Q) {question}"))
    else:
        rows.append(("user", question))
    return rows
# --------------------------------------------------------------------------- #
#  Providers — Gemini, then OpenRouter
# --------------------------------------------------------------------------- #


def _answer_gemini(question: str, history, snippets) -> str | None:
    key = gemini_key()
    if not key:
        return None
    try:
        from google import genai
        from google.genai import types
    except Exception:
        return None

    try:
        client = genai.Client(api_key=key)
    except Exception:
        return None

    contents = [{"role": role, "parts": [text]}
                for role, text in _chat_rows(question, history, snippets)]
    # Pass 1: with Google Search grounding (real-time) when the SDK supports
    # it; pass 2: plain call. Any error on a pass just tries the next one.
    for use_tool in (True, False):
        try:
            kwargs = {"temperature": 0.4,
                      "system_instruction": _system_prompt(),
                      "max_output_tokens": 900}
            if use_tool:
                gsearch = getattr(types, "GoogleSearch", None)
                if gsearch is not None:
                    kwargs["tools"] = [types.Tool(google_search=gsearch())]
            try:
                config = types.GenerateContentConfig(**kwargs)
            except Exception:          # older SDK without max_output_tokens
                kwargs.pop("max_output_tokens", None)
                config = types.GenerateContentConfig(**kwargs)
            resp = client.models.generate_content(
                model=gemini_model(),
                contents=contents,
                config=config,
            )
            text = (getattr(resp, "text", None)
                    or getattr(resp, "thought", None) or "").strip()
            if text:
                return text
        except Exception:
            continue
    return None


def _extract_or_content(message: dict) -> str:
    """Pull the final answer text from an OpenRouter message.

    Some free models return ``content`` as ``None`` with the text in ``parts``,
    or as a list of content blocks — handle both shapes.
    """
    content = message.get("content")
    if isinstance(content, str):
        return content
    blocks = []
    for source in (content if isinstance(content, list) else [],
                   message.get("parts")):
        if isinstance(source, list):
            for p in source:
                blocks.append(str(p.get("text", "")) if isinstance(p, dict) else str(p))
    return "".join(blocks)


def _answer_openrouter(question: str, history, snippets) -> str | None:
    key = openrouter_key()
    if not key:
        return None
    try:
        import requests
    except Exception:
        return None

    messages: list[dict] = [{"role": "system", "content": _system_prompt()}]
    for role, text in _chat_rows(question, history, snippets):
        messages.append({"role": "user" if role == "user" else "assistant",
                         "content": text})

    # Try the configured model first, then verified live free fallbacks.
    models: list[str] = []
    for m in (openrouter_model(), *_OPENROUTER_FREE_FALLBACKS):
        if m and m not in models:
            models.append(m)

    base = {"messages": messages, "temperature": 0.4,
            "max_tokens": 900, "top_p": 0.9}
    headers = {"Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    for model in models[:4]:
        try:
            payload = dict(base, model=model)
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=payload, timeout=25,
            )
            if resp.status_code in (402, 408, 429) or resp.status_code >= 500:
                continue                      # quota / rate limit / provider error
            resp.raise_for_status()
            content = _extract_or_content(
                resp.json().get("choices", [{}])[0].get("message", {}))
            if content and content.strip():
                return content.strip()
        except Exception:
            continue                          # model unavailable → try next
    return None


# --------------------------------------------------------------------------- #
#  Public entry point
# --------------------------------------------------------------------------- #


def answer(question: str, history: list[dict] | None = None,
           *, search: bool | None = None) -> str | None:
    """Free-form answer via Gemini, falling back to OpenRouter.

    - ``question``: the user's text (wake word already stripped).
    - ``history``: recent chat as ``[{"role", "content"}, ...]`` (the current
      question should **not** be the last entry — it is appended here).
    - ``search``: ``None`` auto-detects time-sensitive questions and adds live
      web snippets as grounding; pass ``False``/``True`` to force it.

    Returns a plain-text answer, or ``None`` when no provider could answer
    (callers keep their previous behaviour).
    """
    question = (question or "").strip()
    if not question or not enabled():
        return None
    if search is None:
        search = should_search(question)
    # Year-bias the search so 'upcoming/latest' questions fetch fresh pages
    # instead of stale schedule pages from months ago.
    snippets = web_search(_search_query(question), limit=4) if search else None

    reply = _answer_gemini(question, history, snippets)
    if reply:
        return reply
    return _answer_openrouter(question, history, snippets)