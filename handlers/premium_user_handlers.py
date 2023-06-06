import asyncio
from aiogram import Router
from filters.custom_filters import IsPremiumUser
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from external_services.bai_chat import get_personal_horoscope
from states.config_menu_states import SetConfig
from keyboards.personal_h_keyboard import p_keyboard
# команды для премиум пользователей:
# /personal_horoscope

# Инициализируем роутер
router: Router = Router()
router.message.filter(IsPremiumUser())


# Отмена /cancel
@router.message(Command(commands='cancel'))
async def cancel_state_command(message: Message, state: FSMContext):
    await message.answer('Отменено', reply_markup=ReplyKeyboardRemove())
    await message.delete(reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(Command(commands='personal_horoscope'))
async def post_regular_horoscope_command(message: Message, state: FSMContext):
    await message.answer(text=f'Для составления персонального гороскопа нужны будет получить некоторые данные. '
                              f'Для начала укажите точную дату рождения.', reply_markup=p_keyboard)

    await state.set_state(SetConfig.ph_entering_date)


@router.message(SetConfig.ph_entering_date)
async def change_channels_process_command(message: Message, state: FSMContext):
    await state.update_data(date_of_birth=message.text)
    await message.answer(text=f'Отлично. Теперь укажите место рождения.', reply_markup=p_keyboard)
    await state.set_state(SetConfig.ph_entering_time)


@router.message(SetConfig.ph_entering_time)
async def change_channels_process_command(message: Message, state: FSMContext):
    await state.update_data(place_of_birth=message.text)
    await message.answer(text=f'И последнее. Как можно точнее укажите время в которое Вы родились.', reply_markup=p_keyboard)
    await state.set_state(SetConfig.ph_result)


@router.message(SetConfig.ph_result)
async def change_channels_process_command(message: Message, state: FSMContext):
    await state.update_data(time_of_birth=message.text)
    await message.answer(text=f'Замечательно. Сейчас рассчитаем гороскоп для Вас на сегодня. Это может занять немного времени...',
                         reply_markup=ReplyKeyboardRemove())
    user_data = await state.get_data()
    for _ in range(5):
        horoscope = await get_personal_horoscope(user_data['date_of_birth'], user_data['place_of_birth'], user_data['time_of_birth'])
        if horoscope:
            await message.answer(text=horoscope)
            break
        else:
            await message.answer(text=f'[INFO]Произошла ошибка при составлении гороскопа. Пробуем ещё раз...')
            await asyncio.sleep(10)

    await state.clear()
