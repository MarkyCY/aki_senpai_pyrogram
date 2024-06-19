from pyrogram import utils
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

#from database.mongodb import get_db
from plugins.others.admin_func import get_until_date

import re

async def BanUser(app, chat_id, user_id, message=None, name=None, until_date=utils.zero_datetime()):
    # Banear al usuario
    try:
        if until_date == utils.zero_datetime():
            banned_till = "Indefinido"
        else:
            banned_till = until_date.strftime("%d/%m/%Y %I:%M %p")

        await app.ban_chat_member(chat_id, user_id, until_date=until_date)
    except Exception as e:
        print(e)
        return False
    
    if message:
        btns = [
            [
                InlineKeyboardButton(
                    "✅Desbanear", callback_data=f"unban_{user_id}"),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=btns)
        await message.reply(f"El usuario {name} ha sido baneado hasta: `{banned_till}`.", reply_markup=markup)
        return
    
    return True

async def UnbanUser(app, chat_id, user_id, name=None, message=None):
    # Desbanear al usuario
    try:
        await app.unban_chat_member(chat_id, user_id)
    except Exception as e:
        print(e)
        return False

    if message:
        await message.reply(f"El usuario {name} ha sido desbaneado.")
        return
    
    return True

@Client.on_message(filters.command('ban'))
async def ban_command(app: Client, message: Message):
    
    until_date = utils.zero_datetime()
    if message.command and len(message.command) > 1:
        elemento = message.command[1]
        
        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user_ban_id = get_user.user.id
            name = get_user.user.first_name
            if len(message.command) > 2:
                time = message.command[2]
                until_date = get_until_date(time)
            

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user_ban_id = get_user.user.id
                name = get_user.user.first_name
                if len(message.command) > 2:
                    time = message.command[2]
                    until_date = get_until_date(time)
    
    elif not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas mutear.")
        return
    
    else:
        user_ban_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name
        if message.command and len(message.command) > 1:
            time = message.command[1]
            until_date = get_until_date(time)

    # Obtener la ID del chat
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    chat_member = await app.get_chat_member(chat_id, user_ban_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return
    
    await BanUser(app, chat_id, user_ban_id, message=message, name=name, until_date=until_date)


@Client.on_message(filters.command('unban'))
async def unban_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if message.command and len(message.command) > 1:
        elemento = message.command[1]

        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user_unban_id = get_user.user.id
            name = get_user.user.first_name

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user_unban_id = get_user.user.id
                name = get_user.user.first_name
    
    elif not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas banear.")

        user_unban_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name
        return

    # Obtener la ID del chat
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    chat_member = await app.get_chat_member(chat_id, user_unban_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return

    await UnbanUser(app, chat_id, user_unban_id, name, message)