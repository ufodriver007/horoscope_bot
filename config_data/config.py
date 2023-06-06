from dataclasses import dataclass
from environs import Env


@dataclass
class Admin:
    telegram_id: str            # Токен для доступа к телеграм-боту


@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту


@dataclass
class Payment:
    payment_token: str    # Токен платёжного шлюза


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    payment: Payment
    admin: Admin


def load_config(path: str | None) -> Config:
    """Читаем переменные окружения ,записываем данные в экземпляр класса Config и возвращаем его"""
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('TOKEN')),
                  db=DatabaseConfig(database=env('DATABASE'),
                                    db_host=env('DB_HOST'),
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD')),
                  payment=Payment(payment_token=env('PAYMENT_TOKEN')),
                  admin=Admin(telegram_id=env('ADMIN')))
