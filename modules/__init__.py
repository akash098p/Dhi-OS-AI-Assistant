"""Dhi — a premium, voice-first AI assistant (DHI OS).

Sub-modules
-----------
- speech        : text-to-speech engine, wake word ("Dhi") + audio utilities
- webrtc_audio  : microphone capture + speech-to-text pipeline
- skills        : the assistant's skill library (weather, news, math, ...)
- llm           : LLM big brain — Gemini primary, OpenRouter fallback, web-grounded
- brain         : natural-language intent engine routing to skills
- ui_styles     : DHI HUD theming, boot sequence and UI components
"""

__version__ = "3.0.0"
