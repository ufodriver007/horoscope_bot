from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram import F
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.types import Message
from keyboards import horoscope_keyboard, love_horoscope_keyboard, joke_horoscope_keyboard
from lexicon.emodji import emodji
from create_bot import db
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

# пользовательские команды:
# /horoscope
# /horoscope_love
# /horoscope_joke
# /cancel
# /pay

# Инициализируем роутер
router: Router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())  # теперь декорируем через объект router, а не dp как раньше
async def process_start_command(message: Message):
    await message.answer(text='Этот бот может выдавать гороскопы.\n'
                              'Обычный гороскоп /horoscope \n'
                              'Любовный гороскоп /horoscope_love \n'
                              'Шуточный гороскоп /horoscope_joke')
    telegram_id = str(message.from_user.id)
    first_name = str(message.from_user.first_name)
    last_name = str(message.from_user.last_name)
    await db.add_new_user(telegram_id, first_name, last_name)


# Этот хэндлер срабатывает на команду /horoscope_joke
@router.message(Command(commands='horoscope_joke'))
async def get_horoscope_command(message: Message):
    await message.answer(text='Для какого знака Вам нужен гороскоп?', reply_markup=joke_horoscope_keyboard.jh_kb_builder.as_markup())


# Этот хэндлер срабатывает на команду /horoscope_love
@router.message(Command(commands='horoscope_love'))
async def get_horoscope_command(message: Message):
    await message.answer(text='Для какого знака Вам нужен гороскоп?', reply_markup=love_horoscope_keyboard.lh_kb_builder.as_markup())


# Этот хэндлер срабатывает на команду /horoscope
@router.message(Command(commands='horoscope'))
async def get_horoscope_command(message: Message):
    await message.answer(text='Для какого знака Вам нужен гороскоп?', reply_markup=horoscope_keyboard.h_kb_builder.as_markup())


# Этот хэндлер отдаёт любовный гороскоп
@router.callback_query(Text(text=['Овен_l', 'Телец_l', 'Близнецы_l', 'Рак_l', 'Лев_l', 'Дева_l', 'Весы_l', 'Скорпион_l', 'Стрелец_l', 'Козерог_l', 'Водолей_l', 'Рыбы_l']))
async def process_buttons_press(callback: CallbackQuery):
    await callback.answer()                                 # убирает часики.
    horoscope = await db.read_horoscope('love')
    await callback.message.answer(text=emodji[callback.data[:-2]] + horoscope[callback.data[:-2]])
    await callback.message.delete()                         # Удаляем сообщение, в котором была нажата кнопка


# Этот хэндлер отдаёт шуточный гороскоп
@router.callback_query(Text(text=['Овен_j', 'Телец_j', 'Близнецы_j', 'Рак_j', 'Лев_j', 'Дева_j', 'Весы_j', 'Скорпион_j', 'Стрелец_j', 'Козерог_j', 'Водолей_j', 'Рыбы_j']))
async def process_buttons_press(callback: CallbackQuery):
    await callback.answer()                                 # убирает часики.
    horoscope = await db.read_horoscope('joke')
    await callback.message.answer(text=emodji[callback.data[:-2]] + horoscope[callback.data[:-2]])
    await callback.message.delete()                         # Удаляем сообщение, в котором была нажата кнопка


# Этот хэндлер отдаёт обычный гороскоп
@router.callback_query(Text(text=['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']))
async def process_buttons_press(callback: CallbackQuery):
    await callback.answer()                                 # убирает часики.
    horoscope = await db.read_horoscope('regular')
    await callback.message.answer(text=emodji[callback.data] + horoscope[callback.data])
    await callback.message.delete()                         # Удаляем сообщение, в котором была нажата кнопка


@router.message(Command(commands='personal_horoscope'))
async def post_regular_horoscope_command(message: Message):
    await message.answer(text=f'Только для премиум пользователей. Вы также можете оформить подписку /pay .Всего 149руб в мес.')


# Отмена /cancel
@router.message(Command(commands='cancel'))
async def cancel_state_command(message: Message, state: FSMContext):
    await message.answer('Отменено', reply_markup=ReplyKeyboardRemove())
    await message.delete(reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Все остальные запросы
@router.message(F.text)
async def other_commands(message: Message):
    await message.answer(text='...')
