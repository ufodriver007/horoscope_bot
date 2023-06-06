from lexicon.emodji import emodji
from create_bot import dp, bot, config, db
from models.db import Db


async def post_full_regular_horoscope_in_all_chats():
    chats = await Db.get_chats_id(db)
    horoscope = await db.read_horoscope('regular')
    for chat in chats:
        for sign, description in horoscope.items():
            await bot.send_message(chat, f'{emodji[sign]} {description}')


async def post_full_joke_horoscope_in_all_chats():
    chats = await Db.get_chats_id(db)
    horoscope = await db.read_horoscope('joke')
    for chat in chats:
        for sign, description in horoscope.items():
            await bot.send_message(chat, f'{emodji[sign]} {description}')


async def post_full_love_horoscope_in_all_chats():
    chats = await Db.get_chats_id(db)
    horoscope = await db.read_horoscope('love')
    for chat in chats:
        for sign, description in horoscope.items():
            await bot.send_message(chat, f'{emodji[sign]} {description}')


async def post_full_horoscope(horo_type='regular'):
    chats = await Db.get_chats_id(db)
    horoscope = await db.read_horoscope(horo_type)
    for sign, description in horoscope.items():
        await bot.send_message(chats[0], f'{emodji[sign]} {description}')
