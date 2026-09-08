# ◈ DHI OS — A Premium Voice-First AI Assistant

> **v3.0 · Premium Edition** — meet **Dhi**: call her by name and she answers.
> Speak or type anything — weather, news, knowledge, math, music, timers, notes,
> conversions and much more — wrapped in a premium HUD with an animated
> boot sequence, arc-reactor core and live system diagnostics.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49%2B-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What's new in v3.0 (DHI OS)

| Area | Before | Now |
|---|---|---|
| **Boot** | Static hero screen | Full-screen **DHI OS boot sequence** — reactor core, staggered system checks (`neural core online → all systems nominal`) and animated progress bar, then auto-fade |
| **Identity** | Simple greeting | **Dhi persona** — "Good morning, sir. All systems operational", "Powering down… standing by", "Wake up" to revive |
| **Diagnostics** | Basic stats row | Live **Core Diagnostics HUD** — session id, uptime, command count, mic state, voice language, core-load bar, last command |
| **Input feel** | Instant replies | **ANALYZING → PROCESSING → COMPUTING → EXECUTING** animation before typed replies |
| **Voice console** | Static orb | Arc-reactor orb with **animated equalizer** while listening |
| **Typography** | Single font | **Michroma** (HUD) + **JetBrains Mono** (readouts) + Outfit (body) |
| **Commands** | 25 intents | + **system status** report, protocol greetings, power down / wake up (`🛰️ Status` quick action) |

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

### Dhi protocol
- 🛰️ **System status** — “system status” · “run diagnostics” → live report of
  uptime, commands, notes, timers, mic state, voice language and core load.
- 🟢 **Protocol greetings** — “good morning sir” · “good evening” → *“All systems
  are operational, and I'm at your service.”*
- 🔻 **Power down / revive** — “power down” · “go to sleep” → *standing by on low
  power*; “wake up” → *all systems online*.
- 🖥️ **Boot sequence** — every session opens with an animated DHI core boot,
  then melts away into the workspace.

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
- **DHI OS boot sequence** — premium animated core splash on every session, auto-fades
- Animated gradient background + subtle CRT scanlines + custom fonts (Michroma / Outfit / JetBrains Mono)
- **Arc-reactor hero** with rotating rings, HUD readouts and angular command buttons
- Sidebar **Core Diagnostics** console — session id, uptime, commands, mic, voice language, core-load bar
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
DHI-OS/
├── Dhi.bat                    # ⚡ double-click launcher (Windows)
├── app.py                     # UI layer: hero, sidebar, fragments, chat
├── modules/
│   ├── brain.py               # Intent engine: command → Reply (25+ intents)
│   ├── skills.py              # Skill library: weather, news, math, currency…
│   ├── speech.py              # TTS engine, wake word "Dhi", alert beeps
│   ├── webrtc_audio.py        # Thread-safe mic capture + VAD + STT
│   └── ui_styles.py           # DHI HUD theme, boot sequence, components
├── tests/
│   └── smoke_test.py          # 67 offline tests for brain/skills/audio/protocol
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

67 assertions cover the wake word ("Dhi" & variants), the calculator (incl.
safe-eval code-injection blocking), durations, unit conversion, all offline
brain intents (incl. answering when called), the Dhi protocol (status report,
protocol greetings, power down / wake up), multi-language translation wiring,
and the audio processor
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

