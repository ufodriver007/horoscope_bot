from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram import Router, F, Bot
from create_bot import db

# Инициализируем роутер
router_for_channels_transitions: Router = Router()
router_for_channels_transitions.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))


@router_for_channels_transitions.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added_as_admin(event: ChatMemberUpdated, bot: Bot):
    print(f'[INFO]Добавлен в группу {event.chat.title}. Её ID {event.chat.id}')
    telegram_id = str(event.chat.id)
    name = event.chat.title
    # добавляем в БД
    await db.add_new_channel(telegram_id, name)


@router_for_channels_transitions.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_added_as_admin(event: ChatMemberUpdated, bot: Bot):
    telegram_id = str(event.chat.id)
    # удаляем из БД
    await db.delete_channel(telegram_id)


router_for_users_transitions: Router = Router()


# если пользователь заблокировал бота
@router_for_users_transitions.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    # удаляем из БД
    await db.delete_user(str(event.from_user.id))


# если пользователь разблокировал бота
@router_for_users_transitions.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    # добавляем в БД
    telegram_id = str(event.from_user.id)
    first_name = str(event.from_user.first_name)
    last_name = str(event.from_user.last_name)
    await db.add_new_user(telegram_id, first_name, last_name)
