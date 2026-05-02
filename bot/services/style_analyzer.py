from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from bot.database.models import Message
from bot.utils.text_metrics import normalize_words


@dataclass
class StyleSnapshot:
    top_words: list[tuple[str, int]]
    top_phrases: list[tuple[str, int]]
    chaos_score: int
    mood: str


class StyleAnalyzer:
    def analyze(self, messages: list[Message]) -> StyleSnapshot:
        word_counter: Counter[str] = Counter()
        phrase_counter: Counter[str] = Counter()
        emoji_total = 0
        uppercase_total = 0

        for item in messages:
            words = normalize_words(item.text)
            word_counter.update(words)
            emoji_total += item.emoji_count
            uppercase_total += item.uppercase_count

            lowered = item.text.strip().lower()
            if len(lowered) > 6:
                phrase_counter[lowered] += 1

        total_messages = max(len(messages), 1)
        energy = int((emoji_total + uppercase_total) / total_messages)
        chaos_score = min(100, max(1, energy * 3))

        if chaos_score < 25:
            mood = "sleepy"
        elif chaos_score < 50:
            mood = "stable weirdness"
        elif chaos_score < 80:
            mood = "chaotic"
        else:
            mood = "quantum meltdown"

        return StyleSnapshot(
            top_words=word_counter.most_common(12),
            top_phrases=[item for item in phrase_counter.most_common(8) if item[1] > 1],
            chaos_score=chaos_score,
            mood=mood,
        )
