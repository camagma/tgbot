from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import Settings
from bot.database.repositories import BotStateRepository, GeneratedRepository, MessageRepository
from bot.services.ai_generator import AIGenerator
from bot.services.markov_generator import MarkovGenerator
from bot.services.personality import get_profile


class GenerationService:
    def __init__(self, session_factory: async_sessionmaker, settings: Settings) -> None:
        self.session_factory = session_factory
        self.markov = MarkovGenerator()
        self.ai = AIGenerator(settings.openai_api_key, settings.openai_model)
        self.default_personality = settings.default_personality

    async def generate_npc_message(self, chat_id: int, mode: str = "markov", thread_id: int | None = None) -> str:
        async with self.session_factory() as session:
            msg_repo = MessageRepository(session)
            generated_repo = GeneratedRepository(session)
            state_repo = BotStateRepository(session)

            texts = await msg_repo.latest_texts(chat_id, limit=1000, thread_id=thread_id)
            state = await state_repo.get_or_create(chat_id, self.default_personality)
            profile = get_profile(state.personality_code)
            anti_repeat = await generated_repo.last_generated(chat_id, thread_id=thread_id)

            if mode == "ai":
                text = await self.ai.generate(profile, texts, anti_repeat=anti_repeat)
            else:
                self.markov.train(texts)
                text = self.markov.generate()

            if anti_repeat and text == anti_repeat:
                text += " (но это уже было в этой ветке реальности)"

            await generated_repo.add(
                chat_id,
                text=text,
                generation_mode=mode,
                personality_code=profile.code,
                thread_id=thread_id,
            )
            await session.commit()
            return text
