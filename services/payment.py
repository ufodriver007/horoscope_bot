from aiogram import types
from config_data.config import Config, load_config


# Получаем данные из переменных окружения
config: Config = load_config('.env')
PAYMENT_TOKEN = config.payment.payment_token

PRICE = types.LabeledPrice(label="Подписка личный гороскоп на 1 месяц", amount=149*100)  # в копейках

