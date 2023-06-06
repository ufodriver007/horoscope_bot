"""
Бот выдающий пользователям гороскопы.
Генерирует с помощью chatGPT гороскоп(один из трёх видов) для любого знака и выдаёт пользователям.
Имеется возможность платной подписки для составления ежедневного персонального гороскопа.
Есть административный интерфейс(по комманде /conf).Там можно:
   -Изменить еремя ежедневного расписания парсера любого из гороскопов
   -Изменить еремя ежедневного расписания автопостинга обычного гороскопа
   -Запостить гороскоп во все группы с ботом сейчас
   -Запустить все парсеры сейчас
   -Показать список групп в которых состоит бот и выйти из любой
   -Изменить список администраторов
   -Разослать сообщение всем пользователям, которые добавивили бота и активировали его.
   -Посмотреть количество активных премиум пользователей
"""
import asyncio
from aiogram import Bot
from create_bot import dp, bot, db
from aiogram.types import BotCommand
from handlers import user_handlers, admin_handlers, other_handlers, order_handlers, premium_user_handlers
from services import scheduler


async def main() -> None:

    async def set_main_menu(bot: Bot):
        """Создаем список с командами и их описанием для кнопки menu"""
        main_menu_commands = [
            BotCommand(command='/start',
                       description='Начальная команда'),
            BotCommand(command='/horoscope',
                       description='Получить гороскоп'),
            BotCommand(command='/horoscope_love',
                       description='Получить любовный гороскоп'),
            BotCommand(command='/horoscope_joke',
                       description='Получить шуточный гороскоп'),
            BotCommand(command='/personal_horoscope',
                       description='Персональный гороскоп'),
            BotCommand(command='/pay',
                       description='Подписка')]

        await bot.set_my_commands(main_menu_commands)

    async def on_startup():
        """автозагрузка"""
        await db.connect()  # записываем объект подключения в поле экземпляра класса db
        await set_main_menu(bot)
        asyncio.create_task(scheduler.scheduler())
        print('[INFO]Bot started')

    # Регистриуем роутеры в диспетчере
    dp.include_router(order_handlers.router)
    dp.include_router(premium_user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router_for_channels_transitions)
    dp.include_router(other_handlers.router_for_users_transitions)
    dp.startup.register(on_startup)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
