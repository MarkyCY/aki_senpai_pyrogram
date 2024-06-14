from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, enums

from database.mongodb import get_db

from plugins.commands.admin.ban import BanUser, UnbanUser
from plugins.commands.admin.mute import MuteUser, UnmuteUser
from plugins.commands.info import info_command


@Client.on_callback_query(filters.regex(r"^info_\d{8,11}$"))
async def info_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    user_data = await app.get_chat_member(chat_id, user_mute_id)

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    await info_command(app, call.message, user_data.user)
    return


@Client.on_callback_query(filters.regex(r"^ban_\d{8,11}$"))
async def ban_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")
    
    btns = [
        [
            InlineKeyboardButton("✅Desbanear", callback_data=f"unban_{user_mute_id}"),
            InlineKeyboardButton("🔙Atrás", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    
    ban = await BanUser(app, chat_id, user_mute_id)
    if ban is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido baneado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido banear al usuario.")


@Client.on_callback_query(filters.regex(r"^mute_\d{8,11}$"))
async def mute_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton("🔊Desilenciar", callback_data=f"unmute_{user_mute_id}"),
            InlineKeyboardButton("🔙Atrás", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    mute = await MuteUser(app, chat_id, user_mute_id)
    if mute is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido muteado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido mutear al usuario.")


@Client.on_callback_query(filters.regex(r"^unban_\d{8,11}$"))
async def unban_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")
    
    btns = [
        [
            InlineKeyboardButton("🔙Atrás", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    unban = await UnbanUser(app, chat_id, user_mute_id)
    if unban is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido desbaneado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido desbanear al usuario.")

@Client.on_callback_query(filters.regex(r"^unmute_\d{8,11}$"))
async def unmute_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton("🔙Atrás", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    
    unmute = await UnmuteUser(app, chat_id, user_mute_id)
    if unmute is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido desmuteado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido desmutear al usuario.")
