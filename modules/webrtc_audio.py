"""WebRTC microphone capture + speech-to-text pipeline for Dhi.

This fixes the original app's biggest architectural bug: the audio buffer,
lock and recognizer were module-level globals shared across *every* browser
session. Everything here is instance-scoped and thread-safe.

Two interaction modes:
- Push-to-talk : press Start, speak, press Stop -> utterance transcribed.
- Hands-free   : a lightweight voice-activity detector finalizes each
  utterance automatically after a short pause (no clicking needed).

Say "Dhi" (or "hey Dhi", "ok Dhi") to get her attention.
"""

from __future__ import annotations

import io
import threading
import time

import av
import numpy as np
import speech_recognition as sr
from streamlit_webrtc import AudioProcessorBase

from .speech import strip_wake_word  # noqa: F401  (wake word + re-exported)

SPEECH_RMS_THRESHOLD = 400.0   # raw RMS above this counts as speech (lower => catches quieter voices)
SILENCE_TO_FINALIZE = 1.0      # seconds of quiet after speech -> finalize utterance sooner
MIN_UTTERANCE_SECONDS = 0.6    # ignore blips / button noise
MAX_RECORD_SECONDS = 75.0      # safety cap for a single utterance


class AudioProcessor(AudioProcessorBase):
    """Per-session mic capture with voice-activity based utterance detection."""

    def __init__(self, language: str = "en-US", strip_wake: bool = True) -> None:
        self._lock = threading.Lock()
        self._recognition_lock = threading.Lock()
        self._recognizer = sr.Recognizer()

        self._buffer = io.BytesIO()
        self._samples = 0
        self._sample_rate = 48000
        self._recording = False

        self._speech_detected = False
        self._last_sound_at: float | None = None

        self._results: list[str] = []   # finalized transcripts (hands-free mode)
        self._language = language
        self._strip_wake = strip_wake

    # ------------------------------------------------------------------ config
    def configure(self, language: str, strip_wake: bool) -> None:
        self._language = language
        self._strip_wake = strip_wake

    # --------------------------------------------------------------- lifecycle
    def ensure_recording(self) -> None:
        """Start capturing audio (idempotent)."""
        with self._lock:
            if self._recording:
                return
            self._recording = True
            self._reset_buffer_locked()

    def _reset_buffer_locked(self) -> None:
        self._buffer.seek(0)
        self._buffer.truncate(0)
        self._samples = 0
        self._speech_detected = False
        self._last_sound_at = None

    # ------------------------------------------------------------- WebRTC hook
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        """Called on the media thread for every incoming audio frame."""
        if not self._recording:
            return frame

        try:
            flat = frame.to_ndarray(format="s16").reshape(-1).astype(np.float32)
        except Exception:
            return frame

        rate = int(getattr(frame, "sample_rate", 48000) or 48000)
        frame_samples = max(getattr(frame, "samples", len(flat)), 1)
        channels = max(1, len(flat) // frame_samples)
        if channels > 1:  # down-mix stereo/interleaved to mono
            flat = flat.reshape(-1, channels).mean(axis=1)
        pcm = flat.astype(np.int16)

        rms = float(np.sqrt(np.mean(pcm.astype(np.float32) ** 2))) if pcm.size else 0.0
        now = time.monotonic()

        with self._lock:
            self._sample_rate = rate
            self._buffer.write(pcm.tobytes())
            self._samples += len(pcm)
            if rms > SPEECH_RMS_THRESHOLD:
                self._speech_detected = True
                self._last_sound_at = now
            seconds = self._samples / max(rate, 1)
            should_finalize = (
                self._speech_detected
                and self._last_sound_at is not None
                and (now - self._last_sound_at) >= SILENCE_TO_FINALIZE
                and seconds >= MIN_UTTERANCE_SECONDS
            ) or seconds >= MAX_RECORD_SECONDS

        if should_finalize:
            self._finalize_async()
        return frame

    # -------------------------------------------------------------- transcribe
    def _take_audio(self) -> bytes | None:
        """Atomically drain the buffer; returns None if too short to matter."""
        with self._lock:
            self._buffer.seek(0)
            data = self._buffer.read()
            seconds = self._samples / max(self._sample_rate, 1)
            self._reset_buffer_locked()
        return data if seconds >= MIN_UTTERANCE_SECONDS else None

    def _recognize(self, pcm_bytes: bytes) -> str:
        audio = sr.AudioData(pcm_bytes, self._sample_rate, 2)
        try:
            with self._recognition_lock:
                text = self._recognizer.recognize_google(audio, language=self._language)
            text = text.strip()
            if self._strip_wake:
                text = strip_wake_word(text)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            return f"[speech service error: {exc}]"

    def _finalize_async(self) -> None:
        """Hand the finished utterance to a background recognition thread."""
        pcm = self._take_audio()
        if pcm:
            threading.Thread(target=self._worker, args=(pcm,), daemon=True).start()

    def _worker(self, pcm: bytes) -> None:
        text = self._recognize(pcm)
        if text:
            with self._lock:
                self._results.append(text)
        else:
            # Recognition failed (noise / unclear speech) — surface feedback
            # instead of silently dropping the utterance, so the user knows
            # the mic heard *something* but couldn't decode it.
            with self._lock:
                self._results.append("[inaudible]")

    # ------------------------------------------------------------------ public
    def pop_results(self) -> list[str]:
        """Drain finalized transcripts (hands-free mode)."""
        with self._lock:
            out, self._results = self._results, []
        return out

    def finalize_now(self) -> str:
        """Push-to-talk: stop capture and synchronously transcribe the buffer."""
        with self._lock:
            self._recording = False
        pcm = self._take_audio()
        if not pcm:
            return ""
        return self._recognize(pcm)

