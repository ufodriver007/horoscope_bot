from asyncpg import Connection
import asyncpg
from config_data.config import Config, load_config


class Db:
    conn: Connection = None                         # объект соединения с БД
    __instance = None                               # единственный экземпляр

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance                       # если создан, то возвращ. ссылку из переменной класса

    def __del__(self):
        Db.__instance = None

    async def connect(self):
        try:
            # Получаем данные из переменных окружения
            config: Config = load_config('.env')
            self.conn = await asyncpg.connect(user=config.db.db_user, password=config.db.db_password,
                                              database=config.db.database, host=config.db.db_host)
        except Exception as e:
            print(e)
            print('[INFO]Невозможно соединиться с БД')

    async def select_by_field(self, table: str, field: str):
        values = list(await self.conn.fetch(
            f'SELECT {field} FROM {table}'
        ))
        return [tuple(x)[0] for x in values]

    # async def select_all(self, table: str):
    #     values = await self.conn.fetch(
    #         f'SELECT * FROM {table}'
    #     )
    #     return values

    async def get_chats_id(self):
        values = await self.conn.fetch(
            'SELECT telegram_id FROM channels'
        )
        return [tuple(x)[0] for x in values]

    async def write_horoscope(self, horoscope_dict: dict, name: str):
        table = f'horoscope_{name}'
        conn = self.conn
        for k, v in horoscope_dict.items():
            await conn.execute(f"INSERT INTO {table} (sign, text) VALUES('{k}', '{v}')")

    async def read_horoscope(self, name: str) -> dict:
        table = f'horoscope_{name}'
        values = await self.conn.fetch(
            f'SELECT DISTINCT * FROM {table} ORDER BY date'
        )
        return {tuple(i)[1]: tuple(i)[2] for i in values}
        # res = {}
        # for i in values:
        #     res[tuple(i)[1]] = tuple(i)[2]
        # return res

    async def get_all_channels(self) -> list:
        values = await self.conn.fetch(
            f"SELECT * FROM channels"
        )
        return [(tuple(i)[1], tuple(i)[2]) for i in values]
        # res = []
        # for i in values:
        #     res.append((tuple(i)[1], tuple(i)[2]))
        # return res

    async def add_new_channel(self, t_id: str, name: str):
        await self.conn.execute(
            f"INSERT INTO channels (telegram_id, name) VALUES('{t_id}', '{name}')")

    async def add_new_user(self, t_id: str, f_name: str, l_name: str):
        values = await self.conn.fetchrow(
            f"SELECT * FROM users WHERE telegram_id = '{t_id}'"
        )
        # Если такого пользователя ещё нет в БД, добавляем
        if not values:
            await self.conn.execute(f"INSERT INTO users (telegram_id, first_name, last_name, is_premium)) VALUES('{t_id}', '{f_name}', '{l_name}', 'no')")

    async def add_new_premium_user(self, t_id: str, f_name: str, l_name: str):
        # удаляем старую запись
        await self.delete_user(t_id)
        # добавляем новую запись
        await self.conn.execute(f"INSERT INTO users (telegram_id, first_name, last_name, is_premium) VALUES('{t_id}', '{f_name}', '{l_name}', 'yes')")

    async def check_premium_period(self):
        # находим все записи старше 30 дней с премиумом
        values = await self.conn.fetch(  # is_premium = 'yes'
            f"SELECT * FROM users WHERE date < current_date - interval '30 days' AND is_premium='yes'"
        )
        # и если они есть, то ставим им is_premium='no'
        if values:
            for user_id in [tuple(i)[1] for i in values]:
                await self.conn.execute(
                    f"UPDATE users SET is_premium='no' WHERE telegram_id='{user_id}'")

    async def delete_user(self, t_id: str):
        await self.conn.execute(f"DELETE FROM users WHERE telegram_id = '{t_id}'")

    async def delete_channel(self, t_id: str):
        await self.conn.execute(f"DELETE FROM channels WHERE telegram_id = '{t_id}'")

    async def users_quantity(self) -> int:
        values = await self.conn.fetch(
            f"SELECT * FROM users"
        )
        return len(values)

    async def premium_users_quantity(self) -> int:
        values = await self.conn.fetch(
            f"SELECT * FROM users WHERE is_premium='yes'"
        )
        return len(values)

    async def get_premium_users(self) -> list:
        values = await self.conn.fetch(
            f"SELECT * FROM users WHERE is_premium='yes'"
        )
        return [tuple(x)[1] for x in values] if values else []

    async def get_users_chats(self) -> list[str]:
        values = await self.conn.fetch(
            f"SELECT telegram_id FROM users"
        )
        return [tuple(i)[0] for i in values]
        # res = []
        # for i in values:
        #     res.append(tuple(i)[0])
        # return res

    async def get_admins(self) -> list:
        values = await self.conn.fetch(
            f"SELECT * FROM admins"
        )
        return [(tuple(i)[1], tuple(i)[2], tuple(i)[3]) for i in values]
        # res = []
        # for i in values:
        #     res.append((tuple(i)[1], tuple(i)[2], tuple(i)[3]))
        # return res

    async def delete_admin(self, t_id):
        await self.conn.execute(f"DELETE FROM admins WHERE telegram_id = '{t_id}'")

    async def add_new_admin(self, t_id: str, f_name: str, l_name: str):
        values = await self.conn.fetchrow(
            f"SELECT * FROM admins WHERE telegram_id = '{t_id}'"
        )
        # Если такого пользователя ещё нет в БД, добавляем
        if not values:
            await self.conn.execute(f"INSERT INTO admins (telegram_id, first_name, last_name) VALUES('{t_id}', '{f_name}', '{l_name}')")
