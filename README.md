# speech2text

Local, zero-cost, system-wide speech-to-text for Windows.
Hold a hotkey → speak → cleaned text is pasted at the cursor.

## Stack
- **faster-whisper** — local STT (Whisper base model, CPU/int8)
- **pynput** — global hotkey (Ctrl+Win) + Ctrl+V paste simulation
- **pystray** — system tray icon (green=idle, red=recording, yellow=processing)

## Usage
```
python main.py
```
| Action | Result |
|---|---|
| Hold Ctrl+Win | Start recording (tray → red) |
| Release either key | Stop + process (tray → yellow) |
| Done | Text pasted at cursor; also in clipboard as fallback |
| Tray → Quit | Exit |

## Setup
```
pip install -r requirements.txt
```
Requires Python 3.10+.

## How it works
1. Hold Ctrl+Win — recording starts, tray turns red, beep sounds
2. Speak
3. Release either key — recording stops, tray turns yellow
4. Whisper transcribes the audio locally on CPU
5. Regex cleaner removes filler words and stutters
6. Text is copied to clipboard and pasted at the cursor via Ctrl+V

## Regex cleaning
Runs automatically after every transcription. Removes:
- **Filler words**: um, uh, ah, er, hmm, mhm, huh, you know, i mean, so, basically, literally, right, okay, ok, actually, honestly, obviously, clearly, anyway
- **Stutters**: immediate word repetition ("the the cat" → "the cat")

## Key files
| File | Role |
|---|---|
| `config.py` | All settings — model size, language, beep tones |
| `main.py` | App entry point; wires all components together |
| `state.py` | Thread-safe state machine: IDLE → RECORDING → PROCESSING → IDLE |
| `transcriber.py` | faster-whisper wrapper |
| `regex_cleaner.py` | Filler word and stutter removal |
| `output_handler.py` | Clipboard write + Ctrl+V paste simulation |
| `tray_icon.py` | System tray icon with colour-coded status |
| `hotkey_listener.py` | Push-to-talk: Ctrl+Win hold/release detection |

## Architecture note
`pystray` owns the main thread (Windows requirement). Whisper transcription runs on a daemon worker thread spawned per recording. The hotkey listener runs on its own daemon thread.

## Changing the model
Edit `config.py`:
- `WHISPER_MODEL_SIZE` — `tiny` / `base` / `small` / `medium` / `large-v3`
- `WHISPER_LANGUAGE` — set to `None` for auto-detect (slower)
