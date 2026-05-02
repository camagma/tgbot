import re

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
COMMAND_RE = re.compile(r"^/[a-zA-Z0-9_]+")

BAD_WORDS = {
    "дурак",
    "идиот",
}


def has_link(text: str) -> bool:
    return bool(URL_RE.search(text))


def is_command(text: str) -> bool:
    return bool(COMMAND_RE.match(text.strip()))


def has_bad_words(text: str) -> bool:
    lowered = text.lower()
    return any(bad in lowered for bad in BAD_WORDS)
