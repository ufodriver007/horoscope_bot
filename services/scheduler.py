import asyncio
import aioschedule
from external_services.bai_chat import get_regular_horoscope, get_joke_horoscope, get_love_horoscope
from services import posting
from create_bot import db


# TODO: сделать автоматическую подгрузку из БД
GET_REGULAR_HOROSCOPE_TIME = "06:00"
GET_LOVE_HOROSCOPE_TIME = "06:10"
GET_JOKE_HOROSCOPE_TIME = "06:20"
POST_FULL_REGULAR_HOROSCOPE_TIME = "08:30"
CHECK_PREMIUM_PERIOD = "07:00"

kill_shed = False


async def scheduler():
    global kill_shed
    kill_shed = False
    """менеджер выполнения по расписанию"""
    aioschedule.every().day.at(CHECK_PREMIUM_PERIOD).do(db.check_premium_period)
    aioschedule.every().day.at(GET_REGULAR_HOROSCOPE_TIME).do(get_regular_horoscope)
    aioschedule.every().day.at(GET_LOVE_HOROSCOPE_TIME).do(get_love_horoscope)
    aioschedule.every().day.at(GET_JOKE_HOROSCOPE_TIME).do(get_joke_horoscope)
    aioschedule.every().day.at(POST_FULL_REGULAR_HOROSCOPE_TIME).do(posting.post_full_regular_horoscope_in_all_chats)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
        if kill_shed:
            asyncio.current_task().cancel()


async def new_parser_schedule(parser: str, ptime: str):
    """Запись нового расписания"""
    global GET_JOKE_HOROSCOPE_TIME, GET_LOVE_HOROSCOPE_TIME, GET_REGULAR_HOROSCOPE_TIME
    config_menu_horoscopes = ['Обычный гороскоп', 'Любовный гороскоп', 'Шуточный гороскоп']

    if parser == config_menu_horoscopes[0]:
        GET_REGULAR_HOROSCOPE_TIME = ptime
    elif parser == config_menu_horoscopes[1]:
        GET_LOVE_HOROSCOPE_TIME = ptime
    elif parser == config_menu_horoscopes[2]:
        GET_JOKE_HOROSCOPE_TIME = ptime

    await restart_scheduler()


async def new_posting_schedule(ptime: str):
    global POST_FULL_REGULAR_HOROSCOPE_TIME
    POST_FULL_REGULAR_HOROSCOPE_TIME = ptime

    await restart_scheduler()


async def restart_scheduler():
    """Перезапуск шедулера"""
    global kill_shed
    aioschedule.clear()
    kill_shed = True
    await asyncio.sleep(2)
    asyncio.create_task(scheduler())
