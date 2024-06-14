from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from database.mongodb import get_db
from plugins.others.admin_func import isModerator

async def MuteUser(app, message, chat_id, user_id, name, until_date):
    # Configurar los permisos de restricción (mutear al usuario)
    permissions = ChatPermissions(can_send_messages=False)

    # Calcular la fecha hasta la cual el usuario estará muteado (24 horas desde ahora)
    until_date = datetime.now() + timedelta(days=1)

    # Mutear al usuario
    await app.restrict_chat_member(chat_id, user_id, permissions, until_date=until_date)
    
    await message.reply(f"El usuario {name} ha sido muteado por 24 horas.")

async def UnmuteUser(app, message, chat_id, user_id, name):
    # Configurar los permisos de restricción (desmutear al usuario)
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True)

    # Desmutear al usuario
    await app.restrict_chat_member(chat_id, user_id, permissions)

    await message.reply(f"El usuario {name} ha sido desmuteado.")

@Client.on_message(filters.command('aki_mute'))
async def mute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas mutear.")
        return

    # ID del usuario a mutear
    user_mute_id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.first_name

    # Obtener la ID del chat
    chat_id = message.chat.id

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if not await isModerator(message.from_user.id) or role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return
    
    await MuteUser(app, message, chat_id, user_mute_id, name, until_date=None)



@Client.on_message(filters.command('aki_unmute'))
async def unmute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas desmutear.")
        return

     # ID del usuario a mutear
    user_mute_id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.first_name

    # Obtener la ID del chat
    chat_id = message.chat.id

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if not await isModerator(message.from_user.id) or role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return
    
    await UnmuteUser(app, message, chat_id, user_mute_id, name)