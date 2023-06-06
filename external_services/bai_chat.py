"""Подключение к bai-chat(китайская обёртка для API chatGPT)"""
import asyncio
from create_bot import db
from baichat_py import BAIChat


signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
horoscope = dict.fromkeys(signs)


async def ask_horoscope_baichat(req: str, pos: int):
    chat = BAIChat()
    r = await chat.async_ask(req)
    horoscope[signs[pos]] = r.text


async def ask_baichat(request: str) -> str:
    chat = BAIChat()
    response = chat.sync_ask(request).text
    return response


async def get_regular_horoscope():
    print('[INFO]Запрос на обычный гороскоп...')
    tasks = []
    try:
        for i in range(12):
            request = f'Представь, что ты астролог. Случайно сгенерируй гороскоп на сегодняшний день для знака {signs[i]}. Сразу пиши текст гороскопа, без предисловий'
            task = asyncio.create_task(ask_horoscope_baichat(request, i))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await db.write_horoscope(horoscope, 'regular')
        print('[INFO]Обычный гороскоп получен')
    except Exception as e:
        print('[INFO]Ошибка получения гороскопа')
        print('[INFO]Попробуем позже...')
        await asyncio.sleep(120)
        await get_regular_horoscope()


async def get_love_horoscope():
    print('[INFO]Запрос на любовный гороскоп...')
    tasks = []
    try:
        for i in range(12):
            request = f'Представь, что ты астролог. Случайно сгенерируй любовный гороскоп на сегодняшний день для знака {signs[i]}. Сразу пиши текст гороскопа, без предисловий'
            task = asyncio.create_task(ask_horoscope_baichat(request, i))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await db.write_horoscope(horoscope, 'love')
        print('[INFO]Любовный гороскоп получен')
    except Exception:
        print('[INFO]Ошибка получения любовного гороскопа')
        print('[INFO]Попробуем позже...')
        await asyncio.sleep(120)
        await get_love_horoscope()


async def get_joke_horoscope():
    print('[INFO]Запрос на шуточный гороскоп...')
    tasks = []
    try:
        for i in range(12):
            request = f'Представь, что ты стендапер. Случайно сгенерируй шуточный гороскоп на сегодняшний день для знака {signs[i]}. Сразу пиши текст гороскопа, без предисловий'
            task = asyncio.create_task(ask_horoscope_baichat(request, i))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await db.write_horoscope(horoscope, 'joke')
        print('[INFO]Шуточный гороскоп получен')
    except Exception:
        print('[INFO]Ошибка получения шуточного гороскопа')
        print('[INFO]Попробуем позже...')
        await asyncio.sleep(120)
        await get_joke_horoscope()


async def get_personal_horoscope(date: str, place: str, time: str):
    print('[INFO]Запрос на персональный гороскоп...')
    try:
        request = f'Представь, что ты астролог. Сгенерируй персональный гороскоп на сегодня используя эти данные: ' \
                  f'дата рождения {date}, место рождения {place}, время рождения: {time} .' \
                  f'Сразу пиши текст гороскопа, без предисловий'
        response = await ask_baichat(request)
        return response
    except Exception:
        print('[INFO]Ошибка получения персонального гороскопа')
        print('[INFO]Попробуем позже...')
        return ''
