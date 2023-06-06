from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


values = ['Удалить']

# инициализируем билдер
channels_kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

# создаём список с кнопками
buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=value, callback_data=f'{value}') for value in values]

# добавляем в билдер кнопки
channels_kb_builder.row(*buttons)
