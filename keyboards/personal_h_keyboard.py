from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup)


# Создаем объекты кнопок
cancel: KeyboardButton = KeyboardButton(text='/cancel')

# Создаем объект клавиатуры, добавляя в него кнопки
p_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[cancel]],
    resize_keyboard=True,  # кнопки меньше обычного
    one_time_keyboard=True)
