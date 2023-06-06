from aiogram.filters.state import State, StatesGroup


class SetConfig(StatesGroup):
    choosing_config_menu = State()

    choosing_parser_schedule = State()
    update_parser_schedule = State()

    update_posting_schedule = State()

    spam_message = State()

    admins_choosing = State()
    admin_adding = State()

    channels_choosing = State()

    ph_entering_date = State()
    ph_entering_place = State()
    ph_entering_time = State()
    ph_result = State()
