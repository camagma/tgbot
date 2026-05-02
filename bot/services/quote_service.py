from random import random

from bot.database.models import Message


class QuoteService:
    def rarity_for(self, message: Message) -> str:
        length = message.message_length
        roll = random()
        if length > 140 and roll > 0.8:
            return "legendary"
        if length > 90 and roll > 0.5:
            return "epic"
        if roll > 0.25:
            return "rare"
        return "common"
