from __future__ import annotations

from collections import defaultdict
from random import choice


class MarkovGenerator:
    def __init__(self) -> None:
        self.chain: dict[str, list[str]] = defaultdict(list)
        self.words: list[str] = []

    def train(self, texts: list[str]) -> None:
        self.chain.clear()
        self.words.clear()
        for text in texts:
            words = text.split()
            self.words.extend(words)
            if len(words) < 2:
                continue
            for i in range(len(words) - 1):
                key = words[i].lower()
                self.chain[key].append(words[i + 1])

    def generate(self, min_words: int = 3, max_words: int = 15) -> str:
        if not self.chain or not self.words:
            return "Система генерации еще не накопила достаточно lore."

        start = choice(self.words)
        output = [start.capitalize()]

        target_length = max(min_words, min(max_words, choice(range(min_words, max_words + 1))))
        while len(output) < target_length:
            key = output[-1].lower()
            next_options = self.chain.get(key)
            if not next_options:
                output.append(choice(self.words))
            else:
                output.append(choice(next_options))

        phrase = " ".join(output).strip()
        
        return phrase
