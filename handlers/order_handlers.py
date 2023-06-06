from aiogram import F
from aiogram import Router, Bot
from aiogram.filters import Command
from filters.custom_filters import IsPremiumUser
from aiogram.types import Message, PreCheckoutQuery, ContentType
from services.payment import PAYMENT_TOKEN, PRICE
from create_bot import db


router: Router = Router()


# Этот хэндлер срабатывает на команду /pay для премиум пользователей
@router.message(Command(commands='pay'), IsPremiumUser())
async def process_paid_command(message: Message, bot: Bot):
    await message.answer(text='Вы УЖЕ являетесь премиум пользователем. Спасибо за поддержку!')


# Этот хэндлер срабатывает на команду /pay для обычных пользователей
@router.message(Command(commands='pay'))
async def process_pay_command(message: Message, bot: Bot):
    await message.answer(text='Оплата месячной подписки. 149р.')
    if PAYMENT_TOKEN.split(':')[1] == 'TEST':
        await message.answer(text='Тестовый платёж!')

    # инвойс
    await bot.send_invoice(chat_id=message.chat.id,
                           title="Подписка на бота",
                           description="Оплата месячной подписки.",
                           provider_token=PAYMENT_TOKEN,
                           currency="rub",
                           photo_url="https://aliceskill.ru/media/data/fa/35/fa359b8c-8672-4675-8c82-0dd12298bbaf/goroskop-naden..256x256_q85_background-%23ffffff.jpg",
                           photo_width=256,
                           photo_height=256,
                           photo_size=100,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload",
                           request_timeout=15)


# pre checkout (must be answered in 10 seconds). Здесь можно отклонить платёж
@router.pre_checkout_query(F.invoice_payload.startswith("test"))
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True, error_message='[INFO]Произошла ошибка оплаты. Попробуйте позднее.')


# successful payment
@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT, F.successful_payment.invoice_payload.startswith('test'))
async def successful_payment(message: Message):
    await message.answer(text=f'Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошёл успешно.')

    # записываем в БД как премиум пользователя
    await db.add_new_premium_user(message.chat.id, message.chat.first_name, message.chat.last_name)
