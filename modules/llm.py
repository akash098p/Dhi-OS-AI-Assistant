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

import os
import re
import urllib.parse

HTTP_TIMEOUT = 12
SEARCH_TIMEOUT = 6
_DDG_SEARCH_URL = "https://html.duckduckgo.com/html/?q="

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
            or "meta-llama/llama-3.3-70b-instruct:free")


def enabled() -> bool:
    """True when at least one LLM provider is configured."""
    return bool(gemini_key() or openrouter_key())


# --------------------------------------------------------------------------- #
#  Prompt building & real-time grounding
# --------------------------------------------------------------------------- #

_SYSTEM_PROMPT = (
    "You are Dhi, a premium voice-first AI assistant in a desktop app. "
    "Answer the user's question directly, clearly and concisely (normally "
    "1-4 sentences — the reply may be read aloud). Use plain text with only "
    "light markdown (bold, short bullet lists); avoid tables and long essays. "
    "Answer in the same language the user writes. "
    "If 'Recent web info' is included just above the user message, it contains "
    "live search snippets — use it for anything time-sensitive, mention one "
    "source in parentheses when you rely on it, and never claim you cannot "
    "know current facts when those snippets are present. If you genuinely "
    "don't know, say so honestly instead of guessing."
)

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


def web_search(query: str, limit: int = 3) -> str | None:
    """Fetch DuckDuckGo snippets (no API key) as grounding text for a prompt.

    Returns a compact block like ``"Recent web info (from web search):\\n• …"``
    or ``None`` on any failure — strictly best-effort.
    """
    try:
        import html as html_mod
        import requests

        url = _DDG_SEARCH_URL + urllib.parse.quote_plus(query)
        resp = requests.get(url, timeout=SEARCH_TIMEOUT,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        pattern = re.compile(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
            r'.*?class="result__snippet"[^>]*(?:class="[^"]*")?>*?(.*?)</a>',
            re.DOTALL,
        )
        found: list[str] = []
        for m in pattern.finditer(resp.text):
            title = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
            snippet = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()
            if title and snippet:
                found.append(f"• {title}: {snippet}")
            if len(found) >= limit:
                break
        if not found:
            return None
        return "Recent web info (from web search):\n" + "\n".join(found)
    except Exception:
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
                      "system_instruction": _SYSTEM_PROMPT}
            if use_tool:
                gsearch = getattr(types, "GoogleSearch", None)
                if gsearch is not None:
                    kwargs["tools"] = [types.Tool(google_search=gsearch())]
            resp = client.models.generate_content(
                model=gemini_model(),
                contents=contents,
                config=types.GenerateContentConfig(**kwargs),
            )
            text = (getattr(resp, "text", None)
                    or getattr(resp, "thought", None) or "").strip()
            if text:
                return text
        except Exception:
            continue
    return None


def _answer_openrouter(question: str, history, snippets) -> str | None:
    key = openrouter_key()
    if not key:
        return None
    try:
        import requests
    except Exception:
        return None

    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for role, text in _chat_rows(question, history, snippets):
        messages.append({"role": "user" if role == "user" else "assistant",
                         "content": text})

    payload = {
        "model": openrouter_model(),
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 700,
        "top_p": 0.9,
    }
    headers = {"Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=HTTP_TIMEOUT + 8,
        )
        if resp.status_code == 402:              # out of free credits/quota
            return None
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return (content or "").strip() or None
    except Exception:
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
    snippets = web_search(question) if search else None

    reply = _answer_gemini(question, history, snippets)
    if reply:
        return reply
    return _answer_openrouter(question, history, snippets)