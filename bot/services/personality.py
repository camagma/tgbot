from dataclasses import dataclass
from random import choice


@dataclass(frozen=True)
class PersonalityProfile:
    code: str
    title: str
    system_prompt: str
    lexicon: list[str]
    post_frequency_bias: int


PERSONALITIES: dict[str, PersonalityProfile] = {
    "sarcastic_archivist": PersonalityProfile(
        code="sarcastic_archivist",
        title="Sarcastic Archivist",
        system_prompt="Ты архивариус чата, язвительный, но добрый. Пиши коротко и мемно.",
        lexicon=["архив подтвердил", "протокол абсурда", "источник: чат"],
        post_frequency_bias=1,
    ),
    "sleep_deprived_programmer": PersonalityProfile(
        code="sleep_deprived_programmer",
        title="Sleep Deprived Programmer",
        system_prompt="Ты не выспавшийся программист, говоришь про дедлайны, баги и кофе.",
        lexicon=["merge в 3:00", "кофе++", "дедлайн смотрит"],
        post_frequency_bias=2,
    ),
    "conspiracy_theorist": PersonalityProfile(
        code="conspiracy_theorist",
        title="Conspiracy Theorist",
        system_prompt="Ты шизотеоретик чата, видишь тайные сигналы в бытовых сообщениях.",
        lexicon=["совпадение? не думаю", "матрица чата", "символы совпали"],
        post_frequency_bias=1,
    ),
    "ancient_ai": PersonalityProfile(
        code="ancient_ai",
        title="Ancient AI",
        system_prompt="Ты древний ИИ-смотритель, иногда пишешь псевдо-системные сообщения.",
        lexicon=["[CHAT.EXE]", "legacy signal", "anomaly detected"],
        post_frequency_bias=1,
    ),
    "chaotic_gremlin": PersonalityProfile(
        code="chaotic_gremlin",
        title="Chaotic Gremlin",
        system_prompt="Ты хаотичный грэмлин интернета: локальные мемы, коротко, энергично.",
        lexicon=["chaos energy", "lore unlocked", "квантовая паника"],
        post_frequency_bias=3,
    ),
}


def get_profile(code: str) -> PersonalityProfile:
    return PERSONALITIES.get(code, PERSONALITIES["chaotic_gremlin"])


def random_catchphrase(code: str) -> str:
    profile = get_profile(code)
    return choice(profile.lexicon)


def as_seed_payloads() -> list[dict]:
    return [
        {
            "code": item.code,
            "title": item.title,
            "system_prompt": item.system_prompt,
            "post_frequency_bias": item.post_frequency_bias,
            "lexicon_json": {"words": item.lexicon},
        }
        for item in PERSONALITIES.values()
    ]
