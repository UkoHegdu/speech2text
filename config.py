# Audio capture
SAMPLE_RATE: int = 16000
CHANNELS: int = 1
DTYPE: str = "float32"
MIN_RECORDING_SECONDS: float = 0.3   # Ignore recordings shorter than this

# Whisper (local transcription)
WHISPER_MODEL_SIZE: str = "small"    # tiny | base | small | medium | large-v3
WHISPER_DEVICE: str = "cpu"          # cpu | cuda
WHISPER_COMPUTE_TYPE: str = "int8"   # int8 is fastest on CPU
WHISPER_LANGUAGE: str = "en"         # Set to None for auto-detect (slower)
WHISPER_VAD_FILTER: bool = False     # Skip silent sections (requires silero-vad download)
# Biases Whisper toward clean output; reduce fillers at the source before any post-processing
WHISPER_INITIAL_PROMPT: str = "Concise, grammatically correct speech without filler words:"

# Regex cleaner — always runs after Whisper, before LLM (or instead of it)
REGEX_CLEAN_ENABLED: bool = True

# Ollama (local LLM cleanup) — optional second pass
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "phi3:mini"      # Any installed Ollama model works
OLLAMA_TIMEOUT_SECONDS: int = 30
LLM_ENABLED: bool = False            # Enable once Ollama is set up

# Window tracker — per-editor vocabulary (see window_tracker.py)
CLAUDE_PROCESS_NAME: str = "claude.exe"   # Claude Desktop foreground process
CLAUDE_VOCAB_PROJECT: str = "claude"      # ~/.speech2text/vocab/claude.txt

# Beep feedback (Windows winsound — frequency Hz, duration ms)
BEEP_START      = (880,  150)   # High — recording started
BEEP_STOP       = (660,  150)   # Mid  — recording stopped
BEEP_DONE       = (1047, 200)   # High — text pasted
BEEP_ERROR      = (300,  400)   # Low  — something went wrong
