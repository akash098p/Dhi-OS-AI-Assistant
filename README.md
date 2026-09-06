# 🎙️ EchoStream · **Dhi** — A Premium Voice-First AI Assistant

> **v2.1 · Premium Edition** — meet **Dhi**: call her by name and she answers.
> Speak or type anything — weather, news, knowledge, math, music, timers, notes,
> conversions and much more — wrapped in a glassmorphic, animated interface.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49%2B-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What's new in v2.0

| Area | Before | Now |
|---|---|---|
| **Architecture** | One 213-line script | Modular package (`brain`, `skills`, `speech`, `webrtc_audio`, `ui_styles`) |
| **Input** | Voice only, press Start **and** Stop | Voice **hands-free** (auto-send on pause) + push-to-talk + **text chat** |
| **Intents** | 5 rigid `elif` checks | **25+ intents** with regex NLU, priority ordering & graceful fallback |
| **Skills** | Time, joke, weather, wiki, play | + Calculator, news, dictionary, currency, units, notes, timers, quotes, facts, coin, dice, search, site shortcuts, name memory, small talk |
| **Audio pipeline** | Global buffer shared across all sessions (bug) | Per-session, thread-safe capture with **voice-activity detection** |
| **Voice** | English only | **15 languages** for speech + recognition, replay player |
| **UI** | Default Streamlit | Premium dark glassmorphism, animated listening orb, chat bubbles, quick actions, stats, transcript export |

---

## 🧠 Feature tour

### Voice
- 🌸 **Her name is Dhi** — say **“Dhi”**, **“hey Dhi”** or **“ok Dhi”** and she answers
  *“Yes? I'm listening.”* 
- 🪄 **Hands-free mode** — a lightweight VAD detects when you stop speaking and
  sends the utterance automatically. No clicking.
- 🎙️ **Push-to-talk** — classic Start → speak → Stop flow.
- 🧹 **Wake-word stripping** — “Dhi, what time is it” just works.
- 🗣️ **15 languages** — English variants, Hindi, Spanish, French, German, Japanese, and more.
- 🔁 Optional replay player inside every reply bubble.

### Brain (25+ intents)
| Skill | Try saying |
|---|---|
| 🕒 Time & date | "what time is it" · "what's the date today" |
| 🌦️ Weather | "weather in Tokyo" · "how hot is it in Dubai" (auto IP-detect if no city) |
| 📰 News | "show me the news" · "news about cricket" |
| 📚 Knowledge | "who is Ada Lovelace" · "tell me about black holes" |
| 🧮 Math | "calculate 25 times 8" · "what is 15% of 2400" · "square root of 144" |
| 💱 Currency | "convert 100 usd to inr" (live rates) |
| 📐 Units | "convert 10 km to miles" · "convert 100 f to c" |
| 📖 Dictionary | "define serendipity" (dual API with automatic failover) |
| 📝 Notes | "take a note that buy milk" · "show my notes" · "clear my notes" |
| ⏲️ Timers | "set a timer for 5 minutes" → live countdown chip + beep + spoken alert |
| 🎵 Music | "play Bohemian Rhapsody" · "play lo-fi beats on spotify" |
| 🔗 Websites | "open youtube" · "open github" (19 shortcuts) |
| 🔍 Search | "search quantum computing" → Google / DuckDuckGo / YouTube links |
| 😄 Fun | "tell me a joke" · "flip a coin" · "roll a dice" · "give me a quote" · "tell me a fun fact" |
| 👤 Personal | "my name is Alex" → remembered & used in greetings |
| 🌸 Call her | "Dhi" · "hey Dhi" · "who is Dhi" → she answers & introduces herself |
| 🤖 Small talk | "hello" · "how are you" · "who are you" · "what can you do" · "thanks" · "bye" |

Unrecognized input never dead-ends: it returns handy web-search links.

---

### Interface
- Animated gradient background + glass cards + custom fonts (Outfit / JetBrains Mono)
- Pulsing **listening orb** that reacts to mic state
- Chat-style conversation with timestamps, quick-action chips, session stats
- One-click **chat export** (Markdown) and **clear chat**

---

## 🚀 Quick start

```bash
# 1. Clone & enter
git clone https://github.com/akash098p/Dhi-AI-assistant.git
cd Dhi-AI-assistant

# 2. Create a virtual environment (Python 3.10+)
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your (free) OpenWeatherMap key
copy .streamlit\secrets.example.toml .streamlit\secrets.toml
#    → edit secrets.toml and paste your key from https://openweathermap.org/api

# 5. Run
streamlit run app.py
```

**⚡ Instant launch (Windows):** after setup, just **double-click `Dhi.bat`** —
it starts the server and opens your browser automatically.

Open the browser, click **Start** on the mic (allow permission) and just talk —
or type in the chat box.

> ⚠️ Microphone access requires **localhost or HTTPS** (browser policy).

---

## 🗂️ Project structure

```
EchoStream/
├── Dhi.bat                    # ⚡ double-click launcher (Windows)
├── app.py                     # UI layer: hero, sidebar, fragments, chat
├── modules/
│   ├── brain.py               # Intent engine: command → Reply (25+ intents)
│   ├── skills.py              # Skill library: weather, news, math, currency…
│   ├── speech.py              # TTS engine, wake word "Dhi", alert beeps
│   ├── webrtc_audio.py        # Thread-safe mic capture + VAD + STT
│   └── ui_styles.py           # Premium CSS + reusable HTML components
├── tests/
│   └── smoke_test.py          # 56 offline tests for brain/skills/audio
├── .streamlit/
│   ├── config.toml            # Premium dark theme
│   ├── secrets.toml           # Your API keys (never commit!)
│   └── secrets.example.toml   # Template
└── requirements.txt
```

### How it works

```
 Browser mic ──WebRTC──▶ AudioProcessor (per-session, thread-safe)
                            │  RMS voice-activity detection
                            ├─ hands-free: silence 1.6 s → finalize utterance
                            └─ push-to-talk: Stop → finalize
                            ▼
                    SpeechRecognition (Google STT, 15 locales)
                            ▼
                    brain.respond(command, ctx)  ──regex NLU──▶ 25+ intents
                            ▼
                    skills.<handler>()  →  Reply{spoken, display, action}
                            ▼
              Chat bubble (markdown) + gTTS voice reply + side-effects
              (timers, notes, name memory) + autoplay audio
```

---

## 🔑 API keys

| Service | Used for | Required? |
|---|---|---|
| [OpenWeatherMap](https://openweathermap.org/api) | Weather skill | Recommended (free) |
| Google News RSS | News skill | No key needed |
| dictionaryapi.dev + Wiktionary | Dictionary | No key needed |
| open.er-api.com | Currency | No key needed |
| ZenQuotes | Quotes | No key needed |
| Google Speech / Translate TTS | STT & voice replies | No key needed |

Put keys in `.streamlit/secrets.toml` (see `secrets.example.toml`). The file is
git-ignored — never commit real keys.

---

## 🧪 Tests

```bash
python tests/smoke_test.py
```

56 assertions cover the wake word ("Dhi" & variants), the calculator (incl.
safe-eval code-injection blocking), durations, unit conversion, all offline
brain intents (incl. answering when called), and the audio processor
(synthetic WebRTC frames).

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Fatal error in launcher: Unable to create process…` | The venv was moved/copied and its `.exe` launchers hold stale paths. **`Dhi.bat` handles this automatically** (it runs `python -m streamlit` instead). Manual fix: `venv\Scripts\python.exe -m pip install --force-reinstall --no-deps streamlit`, or delete `venv\` and re-run `pip install -r requirements.txt` |
| Mic doesn't start | Use localhost or HTTPS; check browser camera/mic permission |
| "Could not understand audio" | Speak louder/closer; VAD threshold lives in `modules/webrtc_audio.py` (`SPEECH_RMS_THRESHOLD`) |
| Weather says key missing | Add `OPENWEATHER_API_KEY` to `.streamlit/secrets.toml` |
| Audio doesn't autoplay | Browsers block autoplay until first interaction — click anywhere once |
| Speech service error | Google STT needs internet; check connectivity |

---

## 📜 License

MIT — free to use, learn from and build upon.

