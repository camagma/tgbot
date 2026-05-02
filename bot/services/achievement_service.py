from dataclasses import dataclass

from sqlalchemy import Integer, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Achievement, Message, User, UserAchievement


@dataclass(frozen=True)
class AchievementDef:
    code: str
    title: str
    description: str
    rarity: str


ACHIEVEMENTS = [
    AchievementDef("night_owl", "Night Owl", "Пишет, когда город спит.", "rare"),
    AchievementDef("caps_wizard", "Caps Wizard", "Владеет CAPS энергией.", "epic"),
    AchievementDef("lore_keeper", "Lore Keeper", "Оставил много цитируемых следов.", "legendary"),
]


class AchievementService:
    async def seed(self, session: AsyncSession) -> None:
        for item in ACHIEVEMENTS:
            exists = await session.scalar(select(Achievement).where(Achievement.code == item.code))
            if exists:
                continue
            session.add(
                Achievement(
                    code=item.code,
                    title=item.title,
                    description=item.description,
                    rarity=item.rarity,
                )
            )

    async def evaluate_user(self, session: AsyncSession, user: User) -> list[str]:
        unlocked: list[str] = []

        night_msgs = await session.scalar(
            select(func.count(Message.id)).where(
                and_(
                    Message.user_id == user.id,
                    cast(func.strftime("%H", Message.sent_at), Integer) <= 5,
                )
            )
        )
        if (night_msgs or 0) >= 30:
            added = await self._award(session, user.id, "night_owl")
            if added:
                unlocked.append("Night Owl")

        if user.total_messages >= 150:
            added = await self._award(session, user.id, "lore_keeper")
            if added:
                unlocked.append("Lore Keeper")
        return unlocked

    async def _award(self, session: AsyncSession, user_id: int, code: str) -> bool:
        exists = await session.scalar(
            select(UserAchievement).where(UserAchievement.user_id == user_id, UserAchievement.achievement_code == code)
        )
        if exists:
            return False
        session.add(UserAchievement(user_id=user_id, achievement_code=code))
        return True
