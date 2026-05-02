import re

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)


def emoji_count(text: str) -> int:
    return len(EMOJI_RE.findall(text))


def uppercase_count(text: str) -> int:
    return sum(1 for ch in text if ch.isalpha() and ch.isupper())


def normalize_words(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
    return [part for part in cleaned.split() if len(part) > 2]
