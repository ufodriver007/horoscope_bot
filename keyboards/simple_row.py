from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_simple_keyboard(items: list[str]) -> ReplyKeyboardBuilder:
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=item) for item in items]
    kb_builder.row(*buttons, width=2)
    return kb_builder
