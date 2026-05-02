from __future__ import annotations

from openai import AsyncOpenAI

from bot.services.personality import PersonalityProfile


class AIGenerator:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.model = model

    async def generate(
        self,
        personality: PersonalityProfile,
        messages: list[str],
        anti_repeat: str | None = None,
        temperature: float = 1.0,
        memory_size: int = 25,
        max_output_tokens: int = 90,
    ) -> str:
        if not self.client:
            return "AI-модуль не активирован. Переключаюсь в режим гаражного Markov."

        context = "\n".join(messages[:memory_size])
        anti_repeat_text = anti_repeat or "(none)"

        prompt = (
            "Сгенерируй одну короткую абсурдно-смешную фразу в стиле локального чата друзей.\n"
            "Требования: 1 предложение, максимум 140 символов, без оскорблений, без токсичности.\n"
            f"Не повторяй дословно: {anti_repeat_text}\n"
            "Контекст:\n"
            f"{context}"
        )

        result = await self.client.responses.create(
            model=self.model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            input=[
                {"role": "system", "content": personality.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return (result.output_text or "").strip() or "Сигнал AI потерян, но chaos сохраняется."
