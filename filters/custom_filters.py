from aiogram.filters import BaseFilter
from aiogram.types import Message
from models.db import Db
from create_bot import config
import re


class IsAdmin(BaseFilter):
    """Является ли пишущий администратором"""
    async def __call__(self, message: Message) -> bool:
        db = Db()
        admins = await db.select_by_field('admins', 'telegram_id')
        return message.from_user.id in map(int, admins) or message.from_user.id == int(config.admin.telegram_id)


class IsCorrectTime(BaseFilter):
    """Фильтр строки. Проверяет подходит ли строка под формат ЧЧ:ММ"""
    key = 'time_format'

    def __init__(self, time_format: str) -> None:
        self.time_format = time_format

    async def __call__(self, message: Message) -> bool:
        return bool(re.match(r'^(0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', message.text))


class IsContact(BaseFilter):
    """Является ли сообщение контактом"""
    async def __call__(self, message: Message) -> bool:
        return bool(message.contact)


class IsPremiumUser(BaseFilter):
    """Является ли пишущий премиум пользователем"""
    async def __call__(self, message: Message) -> bool:
        db = Db()
        premium_users_list = await db.get_premium_users()
        return message.from_user.id in map(int, premium_users_list)
