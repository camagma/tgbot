from random import randint


class EventReactor:
    KEYWORD_REACTIONS = {
        "спать": '[CHAT.EXE]\nanomaly detected: "пойду спать"\ncredibility: 2%',
        "дедлайн": "Дедлайн почуял страх и стал ближе на 12%.",
        "кофе": "Кофейный ритуал принят. Производительность симулируется.",
        "теория": "Совпадение? Индекс шизотеории = 94/100.",
    }

    def react(self, text: str) -> str | None:
        lowered = text.lower()
        for key, value in self.KEYWORD_REACTIONS.items():
            if key in lowered and randint(1, 100) > 72:
                return value
        return None
