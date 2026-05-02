from random import randint

from bot.database.models import User


class EconomyService:
    def reward_message(self, user: User) -> int:
        coins = randint(1, 3)
        xp = randint(2, 6)
        user.coins += coins
        user.xp += xp
        return coins

    def level_for_xp(self, xp: int) -> int:
        return max(1, int((xp / 60) ** 0.5) + 1)
