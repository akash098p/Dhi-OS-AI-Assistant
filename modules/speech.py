"""Text-to-speech engine, wake-word handling and audio utilities for Dhi."""

from __future__ import annotations

import base64
import functools
import io
import re
import wave

import numpy as np
from gtts import gTTS

# --------------------------------------------------------------------------- #
#  Wake word — "Dhi" (she also answers to her old codename "Alexa")
# --------------------------------------------------------------------------- #
# Short names get mis-heard by STT engines, so common variants are accepted:
# "dhi", "dhee", "dee", "de", "the", "d".
_WAKE_WORD_RE = re.compile(
    r"^(?:hey\s+|hi\s+|ok\s+|okay\s+|hello\s+|हे\s+|हेय\s+|अरे\s+|ओ\s+)?"
    r"(?:dhi|dhee|dhe|dee|de|the|d|alexa|echostream|echo\s*stream|धी|धि|डी|डि|ढी)"
    r"(?=\W|$)[\s,!.?::-]*",
    re.IGNORECASE,
)


def strip_wake_word(text: str) -> str:
    """Remove leading wake words ("dhi", "hey dhi", "ok dhi", "alexa", ...).

    If the utterance is *only* a wake word it is returned unchanged, so the
    brain can respond to the call itself ("Dhi!" -> "Yes? I'm listening.").
    """
    cleaned = text.strip()
    for _ in range(3):
        stripped = _WAKE_WORD_RE.sub("", cleaned, count=1).strip()
        if not stripped or stripped == cleaned:
            break
        cleaned = stripped
    return cleaned or text.strip()


# Display label -> (gTTS language code, Google TTS "tld" for accents)
TTS_LANGUAGES: dict[str, tuple[str, str]] = {
    "English (US)": ("en", "com"),
    "English (UK)": ("en", "co.uk"),
    "English (India)": ("en", "co.in"),
    "English (Australia)": ("en", "com.au"),
    "Hindi": ("hi", "com"),
    "Spanish": ("es", "com"),
    "French": ("fr", "com"),
    "German": ("de", "com"),
    "Italian": ("it", "com"),
    "Portuguese (Brazil)": ("pt", "com"),
    "Japanese": ("ja", "com"),
    "Korean": ("ko", "com"),
    "Russian": ("ru", "com"),
    "Arabic": ("ar", "com"),
    "Chinese (Mandarin)": ("zh-CN", "com"),
}

# Display label -> Google speech-recognition locale
RECOGNITION_LANGUAGES: dict[str, str] = {
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "English (India)": "en-IN",
    "English (Australia)": "en-AU",
    "Hindi": "hi-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese (Brazil)": "pt-BR",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Russian": "ru-RU",
    "Arabic": "ar-SA",
    "Chinese (Mandarin)": "zh-CN",
}


def _tts_lang_code(language_label: str = "English (US)") -> str:
    """gTTS language code for a display label, e.g. 'Hindi' -> 'hi'."""
    return TTS_LANGUAGES.get(language_label, ("en", "com"))[0]


# Emoji & symbol ranges that make no sense to a speech synthesizer.
_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF"         # emoticons, pictographs, symbols
    "\u2300-\u23FF"                  # misc technical (⏰ clocks, ⚙)
    "\u2600-\u27BF"                  # misc symbols + dingbats (☀ ⭐ ✈)
    "\u2B00-\u2BFF"                  # arrows / symbols (⬆ ★)
    "\u2190-\u21FF"                  # arrows
    "\uFE0F\u200D\u20E3]"            # variation selectors, ZWJ, keycaps
)


def clean_for_tts(text: str) -> str:
    """Strip markdown/emoji/URLs so the synthesizer reads *all* the real text.

    The chat bubbles are markdown (bold, links, tables, emojis). Left as-is,
    Google TTS either mumbles the formatting characters or silently drops
    chunks of the reply, so Dhi wouldn't read back everything she wrote. This
    converts a bubble into clean, speakable prose.
    """
    if not text:
        return ""
    t = text
    t = re.sub(r"```.*?```", " ", t, flags=re.DOTALL)          # code blocks
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)             # [label](url) -> label
    t = re.sub(r"https?://\S+|www\.\S+", " ", t)               # bare URLs
    t = re.sub(r"(?m)^\s*#{1,6}\s*", "", t)                    # # headings
    t = re.sub(r"(?m)^\s*>\s?", "", t)                         # blockquotes
    t = re.sub(r"(?m)^\s*\|[\s:|\-]+\|\s*$", "", t)            # table separator rows
    t = re.sub(r"\s*\|\s*", ", ", t)                           # table pipes -> commas
    t = re.sub(r"(?m)^\s*[-*+]\s+", "", t)                     # '  - bullet' -> text
    t = re.sub(r"\*\*([^*]+?)\*\*", r"\1", t)                  # **bold**
    t = re.sub(r"\*([^*]+?)\*", r"\1", t)                      # *italic*
    t = re.sub(r"(?<![A-Za-z0-9_])_([^_]{1,60})_(?![A-Za-z0-9_])", r"\1", t)  # _italics_
    t = re.sub(r"[`_*]", " ", t)                               # stray markers
    t = _EMOJI_RE.sub(" ", t)                                  # emojis
    t = re.sub(r"\s+", " ", t).strip(" ,;:")                   # normalise spaces
    return t.strip()


_TRANSLATOR: object = None


def _translator():
    """One shared translatepy Translator (lazy; False if unavailable)."""
    global _TRANSLATOR
    if _TRANSLATOR is None:
        try:
            from translatepy import Translator
            _TRANSLATOR = Translator()
        except Exception:
            _TRANSLATOR = False
    return _TRANSLATOR


@functools.lru_cache(maxsize=512)
def translate_text(text: str, language_label: str = "English (US)") -> str:
    """Best-effort translation of ``text`` into the selected voice language.

    Returns the original text when the target is English or when translation is
    unavailable, so Dhi always degrades gracefully to English replies instead
    of breaking. Results are cached per (text, language) to avoid re-calling
    the network on every message.
    """
    if not text:
        return text
    lang = _tts_lang_code(language_label)
    if lang == "en":
        return text
    t = _translator()
    if not t:
        return text
    try:
        result = t.translate(text, lang)
        # translatepy 2.x exposes the translation on `.result` (older builds used
        # `.text`) — check both so we never silently fall back to the original.
        translated = getattr(result, "result", None) or getattr(result, "text", None)
        return translated or text
    except Exception:
        return text


def tts_bytes(text: str, language_label: str = "English (US)", slow: bool = False) -> bytes | None:
    """Synthesize ``text`` and return MP3 bytes (``None`` on failure).

    The text is cleaned first (``clean_for_tts``) so every word Dhi wrote in
    the bubble is actually spoken — markdown symbols, emojis and URLs are
    stripped instead of being read aloud or silently dropping speech.
    """
    lang, tld = TTS_LANGUAGES.get(language_label, ("en", "com"))
    cleaned = clean_for_tts(text)
    if not cleaned:
        return None
    try:
        fp = io.BytesIO()
        gTTS(text=cleaned, lang=lang, tld=tld, slow=slow).write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception:
        return None


def autoplay_html(mp3_bytes: bytes | None) -> str:
    """Return an invisible auto-playing <audio> element for instant voice replies."""
    if not mp3_bytes:
        return ""
    b64 = base64.b64encode(mp3_bytes).decode()
    return (
        '<audio autoplay="true">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        "</audio>"
    )


def alert_beep(times: int = 3, freq: float = 880.0, seconds: float = 0.35,
               rate: int = 44100) -> bytes:
    """Generate a short WAV alert tone (used for finished timers)."""
    t = np.linspace(0.0, seconds, int(rate * seconds), endpoint=False)
    env = np.ones_like(t)
    attack = max(int(rate * 0.02), 1)
    release = max(int(rate * 0.08), 1)
    env[:attack] = np.linspace(0.0, 1.0, attack)
    env[-release:] = np.linspace(1.0, 0.0, release)
    tone = (np.sin(2 * np.pi * freq * t) * env * 0.45 * 32767).astype(np.int16)
    gap = np.zeros(int(rate * 0.18), dtype=np.int16)
    data = np.concatenate([tone, gap] * max(1, times))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(data.tobytes())
    buf.seek(0)
    return buf.getvalue()
