from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.emodji import emodji


signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']

# инициализируем билдер
jh_kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

# создаём список с кнопками
buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=emodji[i]+i, callback_data=i+'_j') for i in signs]

# добавляем в билдер кнопки
jh_kb_builder.row(*buttons, width=4)  # width - желаемое кол-во кнопок в ряду(другие переносятся на след.)
