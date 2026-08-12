"""
Fast, zero-latency filler-word and repetition remover.
Runs after Whisper, optionally before the LLM pass.
"""
import re

# Common spoken fillers — whole-word match only
_FILLERS = re.compile(
    r'\b(um+|uh+|ah+|er+|hmm+|mhm+|huh'
    r'|i mean|basically|ok'
    r'|anyway)\b,?\s*',
    re.IGNORECASE,
)

# "right" as a filler only at the start of a sentence (e.g. "Right, so..." or "Right.")
# Mid-sentence "right" is kept ("right button", "turn right")
_RIGHT_FILLER = re.compile(r'(?:^|(?<=[.!?])\s+)right\b,?\s*', re.IGNORECASE)

# Immediate word stutters: "I I want" → "I want", "the the cat" → "the cat"
_STUTTER = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)

# Collapse leftover double spaces
_SPACES = re.compile(r'\s{2,}')


def clean(text: str) -> str:
    text = _FILLERS.sub(' ', text)
    text = _RIGHT_FILLER.sub('', text)
    text = _STUTTER.sub(r'\1', text)
    text = _SPACES.sub(' ', text)
    return text.strip()
