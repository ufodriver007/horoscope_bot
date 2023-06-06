from aiogram import Router
from aiogram.filters import Command
from aiogram.filters import Text
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import Chat
from services import posting
from filters.custom_filters import IsAdmin, IsCorrectTime, IsContact
from create_bot import bot, db
from keyboards import simple_row, admins_list_keyboard, channels_list_keyboard
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from services import scheduler
from states.config_menu_states import SetConfig
import asyncio
from external_services.bai_chat import get_regular_horoscope, get_joke_horoscope, get_love_horoscope
from aiogram.exceptions import TelegramBadRequest
from create_bot import config
# админские команды:
# /conf               настройки
# /cancel             отмена состояния диалога
# /post_rh            пост во все указанные каналы полного обычного гороскопа


# Инициализируем роутер
router: Router = Router()
router.message.filter(IsAdmin())


config_menu_items = ['Расписание парсеров',
                     'Расписание постинга',
                     'Запостить сейчас',
                     'Спарсить гороскопы сейчас',
                     'Изменить список каналов',
                     'Изменить список админов',
                     'Рассылка сообщения',
                     'Показать кол-во подписок',
                     '/cancel']
config_menu_horoscopes = ['Обычный гороскоп', 'Любовный гороскоп', 'Шуточный гороскоп', '/cancel']


# Пост всего обычного гороскопа /post_rh
@router.message(Command(commands='post_rh'))
async def post_regular_horoscope_command(message: Message):
    # получаем названия всех чатов из списка id-шников
    chats = await db.get_chats_id()
    chats_names = []
    for ch in chats:
        chat_info: Chat = await bot.get_chat(ch)
        chats_names.append(chat_info.title.title())

    await message.answer(text=f'Постим обычный гороскоп во все каналы с ботом...')
    await message.answer(text=f'Список каналов с ботом: {",".join(chats_names)}')
    await posting.post_full_regular_horoscope_in_all_chats()


# Меню конфигурации /conf
@router.message(Command(commands='conf'))
async def conf_command(message: Message, state: FSMContext):
    await message.answer(text='Что нужно поменять?', reply_markup=simple_row.make_simple_keyboard(config_menu_items).as_markup(resize_keyboard=True))
    await state.set_state(SetConfig.choosing_config_menu)


# Отмена /cancel
@router.message(Command(commands='cancel'))
async def cancel_state_command(message: Message, state: FSMContext):
    await message.answer('Отменено', reply_markup=ReplyKeyboardRemove())
    await message.delete(reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Пункт меню /conf -> Показать кол-во активных подписок
@router.message(SetConfig.choosing_config_menu, Text('Показать кол-во подписок'))
async def show_subscribers_command(message: Message, state: FSMContext):
    subscribers_quantity = await db.premium_users_quantity()
    await message.answer(text=f'Сейчас активных подписчиков: {subscribers_quantity}', reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Пункт меню /conf -> Изменить список каналов
@router.message(SetConfig.choosing_config_menu, Text('Изменить список каналов'))
async def change_channels_start_command(message: Message, state: FSMContext):
    channels = await db.get_all_channels()
    await message.answer(text=f'Сейчас список каналов:', reply_markup=ReplyKeyboardRemove())
    for channel in channels:
        await message.answer(text=f'{channel[1]} ID: {channel[0]}', reply_markup=channels_list_keyboard.channels_kb_builder.as_markup())

    await state.set_state(SetConfig.channels_choosing)


# Удаление бота из определённого канала
@router.callback_query(SetConfig.channels_choosing)
async def change_channels_process_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()                                 # убирает часики.
    await db.delete_channel(callback.message.text.split()[-1])
    await bot.leave_chat(chat_id=callback.message.text.split()[-1])
    await state.clear()


# Пункт меню /conf -> Изменить список админов
@router.message(SetConfig.choosing_config_menu, Text('Изменить список админов'))
async def change_admins_start_command(message: Message, state: FSMContext):
    admins = await db.get_admins()
    await message.answer(text=f'Сейчас администраторы бота:', reply_markup=ReplyKeyboardRemove())
    await message.answer(text=f'superuser: {config.admin.telegram_id}', reply_markup=admins_list_keyboard.admins_kb_builder.as_markup())
    for admin in admins:
        await message.answer(text=f'{admin[1]} {admin[2]} ({admin[0]})', reply_markup=admins_list_keyboard.admins_kb_builder.as_markup())

    await state.set_state(SetConfig.admins_choosing)


# Удаление или добавление администратора
@router.callback_query(SetConfig.admins_choosing)
async def change_admins_process_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()                                 # убирает часики.
    if callback.data == 'Удалить':
        if callback.message.text.startswith('superuser'):
            await callback.message.answer(text='Суперпользователя нельзя удалить!')
        else:
            await db.delete_admin(callback.message.text.split()[-1][1:-1])
            await callback.message.answer(text='Администратор удалён')

        await state.clear()
    elif callback.data == 'Добавить':
        await callback.message.answer(text='Пришлите контакт нового администратора')
        await state.set_state(SetConfig.admin_adding)


# Добавление нового админа
@router.message(SetConfig.admin_adding, IsContact())
async def add_new_admin_command(message: Message, state: FSMContext):
    await message.answer(text=f'Новый администратор {message.contact.user_id} {message.contact.first_name} {message.contact.last_name}')
    await db.add_new_admin(str(message.contact.user_id), message.contact.first_name, message.contact.last_name)
    await state.clear()


# Пункт меню /conf -> Рассылка сообщения(начало)
@router.message(SetConfig.choosing_config_menu, Text('Рассылка сообщения'))
async def write_spam_command(message: Message, state: FSMContext):
    users_quantity = await db.users_quantity()
    await message.answer(text=f'Рассылаем сообщение всем пользователям, добавившим бота. Общее количество: {users_quantity}. Напишите пост. Или введите /cancel', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetConfig.spam_message)


# Рассылка сообщения
@router.message(SetConfig.spam_message)
async def spam_command(message: Message, state: FSMContext):
    await message.answer(text='Рассылка началась. Это может занять какое-то время...')
    await state.update_data(spam_message=message.text)
    user_data = await state.get_data()
    chats = await db.get_users_chats()
    try:
        for ch in chats:
            await bot.send_message(chat_id=ch, text=user_data['spam_message'])
    except TelegramBadRequest:
        await message.answer(text='[INFO]Один из чатов не был найден.')
    await message.answer(text='Рассылка завершена.')
    await state.clear()


# Пункт меню /conf -> Спарсить гороскопы сейчас
@router.message(SetConfig.choosing_config_menu, Text('Спарсить гороскопы сейчас'))
async def parser_schedule_command(message: Message, state: FSMContext):
    await message.answer(text='Процесс парсинга запущен, потребуется некоторое время...', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await get_regular_horoscope()
    await asyncio.sleep(60)
    await get_love_horoscope()
    await asyncio.sleep(60)
    await get_joke_horoscope()
    await message.answer(text='Парсинг всех гороскопов завершён.')


# Пункт меню /conf -> Изменение расписания постинга
@router.message(SetConfig.update_posting_schedule, IsCorrectTime('time_format'))
async def change_posting_schedule_command(message: Message, state: FSMContext):
    await state.update_data(new_posting_time=message.text.lower())
    user_data = await state.get_data()
    await message.answer(
        text=f"Новое расписание для постинга {user_data['new_posting_time']}",
        reply_markup=ReplyKeyboardRemove()
    )

    await scheduler.new_posting_schedule(user_data['new_posting_time'])
    await message.answer(text='Расписание обновлено.')
    await state.clear()


# Пункт меню /conf -> Выбор парсера для изменения расписания
@router.message(SetConfig.choosing_config_menu, Text('Расписание парсеров'))
async def parser_schedule_command(message: Message, state: FSMContext):
    await message.answer(text='Выберите парсер', reply_markup=simple_row.make_simple_keyboard(config_menu_horoscopes).as_markup(resize_keyboard=True))
    await state.set_state(SetConfig.choosing_parser_schedule)


# Новое расписание для парсера
@router.message(SetConfig.choosing_parser_schedule, F.text.in_(config_menu_horoscopes))
async def new_parser_schedule_command(message: Message, state: FSMContext):
    await state.update_data(chosen_parser=message.text)
    p = None
    if message.text == config_menu_horoscopes[0]:
        p = scheduler.GET_REGULAR_HOROSCOPE_TIME
    elif message.text == config_menu_horoscopes[1]:
        p = scheduler.GET_LOVE_HOROSCOPE_TIME
    elif message.text == config_menu_horoscopes[2]:
        p = scheduler.GET_JOKE_HOROSCOPE_TIME
    await message.answer(text=f'Расписание для текущего парсера: {p}', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Введите время в формате ЧЧ:ММ')
    await state.set_state(SetConfig.update_parser_schedule)


# Изменение расписание парсера
@router.message(SetConfig.update_parser_schedule, IsCorrectTime('time_format'))
async def change_parser_schedule_command(message: Message, state: FSMContext):
    await state.update_data(new_time=message.text.lower())
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали парсер {user_data['chosen_parser']}. Новое расписание {user_data['new_time']}",
        reply_markup=ReplyKeyboardRemove()
    )

    await scheduler.new_parser_schedule(user_data['chosen_parser'], user_data['new_time'])
    await message.answer(text='Расписание обновлено.')
    await state.clear()


# Неверно задано время расписания для парсера
@router.message(SetConfig.update_parser_schedule)
async def wrong_time_command(message: Message):
    await message.answer(text='Время ДОЛЖНО БЫТЬ в 24-часовом формате ЧЧ:ММ. Введите время ещё раз')


# Пункт меню /conf -> Запостить сейчас(из меню настроек)
@router.message(SetConfig.choosing_config_menu, Text('Запостить сейчас'))
async def post_now_command(message: Message):
    await post_regular_horoscope_command(message)


# Пункт меню /conf -> Новое расписание для постинга
@router.message(SetConfig.choosing_config_menu, Text('Расписание постинга'))
async def posting_schedule_command(message: Message, state: FSMContext):
    await message.answer(text=f'Текущее расписание постинга: {scheduler.POST_FULL_REGULAR_HOROSCOPE_TIME}', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Введите время в формате ЧЧ:ММ')
    await state.set_state(SetConfig.update_posting_schedule)


# Неверные данные для добавления администратора
@router.message(SetConfig.admin_adding)
async def wrong_new_admin_command(message: Message):
    await message.answer(text=f'Пришлите именно контакт пользователя. Или введите /cancel')
