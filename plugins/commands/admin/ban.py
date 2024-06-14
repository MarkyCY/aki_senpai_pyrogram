from datetime import datetime, timedelta
from pyrogram import utils
from pyrogram import Client, filters
from pyrogram.types import Message

#from database.mongodb import get_db

async def BanUser(app, chat_id, user_id, message=None, name=None, until_date=utils.zero_datetime()):
    # Banear al usuario
    try:
        await app.ban_chat_member(chat_id, user_id, until_date=until_date)
    except Exception as e:
        print(e)
        return False
    
    if message:
        await message.reply(f"El usuario {name} ha sido baneado.")
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

@Client.on_message(filters.command('aki_ban'))
async def ban_command(app: Client, message: Message):
     # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas banear.")
        return

    # ID del usuario a mutear
    user_mute_id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.first_name

    # Obtener la ID del chat
    chat_id = message.chat.id

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return
    
    await BanUser(app, chat_id, user_mute_id, message=message, name=name)


@Client.on_message(filters.command('aki_unban'))
async def unban_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas desbanear.")
        return

    # ID del usuario a mutear
    user_mute_id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.first_name

    # Obtener la ID del chat
    chat_id = message.chat.id

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    await UnbanUser(app, chat_id, user_mute_id, name, message)