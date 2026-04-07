import requests

import config

_SYSTEM_PROMPT = (
    "You are a transcription editor. The user will give you raw speech-to-text output. "
    "Your job: remove filler words (um, uh, ah, er, like, you know, so), "
    "remove false starts and word repetitions, and fix obvious transcription errors. "
    "Preserve all meaning and content. "
    "Return ONLY the cleaned text — no explanation, no quotation marks, nothing else."
)


class LLMCleaner:
    def __init__(self) -> None:
        self._generate_url = f"{config.OLLAMA_BASE_URL}/api/generate"
        self._tags_url = f"{config.OLLAMA_BASE_URL}/api/tags"

    def is_available(self) -> bool:
        """Returns True if Ollama is running and reachable."""
        try:
            r = requests.get(self._tags_url, timeout=3)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def clean(self, raw_text: str) -> str:
        """Clean up transcription via Ollama. Falls back to raw_text on any error."""
        if not raw_text.strip():
            return raw_text

        payload = {
            "model":   config.OLLAMA_MODEL,
            "system":  _SYSTEM_PROMPT,
            "prompt":  raw_text,
            "stream":  False,
            "options": {"temperature": 0.1},
        }

        try:
            r = requests.post(self._generate_url, json=payload, timeout=config.OLLAMA_TIMEOUT_SECONDS)
            r.raise_for_status()
            cleaned = r.json().get("response", "").strip()
            return cleaned if cleaned else raw_text
        except requests.RequestException as exc:
            print(f"[LLM] Ollama error ({exc}). Using raw transcript.")
            return raw_text
