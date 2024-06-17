from datetime import datetime, timedelta
from pyrogram import utils
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from database.mongodb import get_db
from plugins.others.admin_func import isModerator

async def MuteUser(app, chat_id, user_id, message=None, name=None, until_date=utils.zero_datetime()):
    # Configurar los permisos de restricción (mutear al usuario)
    permissions = ChatPermissions(
        can_send_messages = False,
        can_send_audios = False,
        can_send_documents = False,
        can_send_photos = False,
        can_send_videos = False,
        can_send_video_notes = False,
        can_send_voice_notes = False,
        can_send_polls = False,
        can_send_other_messages = False,
        can_add_web_page_previews = False,
        can_change_info = False,
        can_invite_users = False,
        can_pin_messages = False,
        can_manage_topics = False,
        can_send_media_messages = False
        )

    # Mutear al usuario
    try:
        await app.restrict_chat_member(chat_id, user_id, permissions, until_date=until_date)
    except Exception as e:
        print(e)
        return False
    
    if message:
        await message.reply(f"El usuario {name} ha sido muteado por 24 horas.")

    return True

async def UnmuteUser(app, chat_id, user_id, name=None, message=None):
    # Configurar los permisos de restricción (desmutear al usuario)
    permissions = ChatPermissions(
        can_send_messages = True,
        can_send_audios = True,
        can_send_documents = True,
        can_send_photos = True,
        can_send_videos = True,
        can_send_video_notes = True,
        can_send_voice_notes = True,
        can_send_polls = True,
        can_send_other_messages = True,
        can_add_web_page_previews = True,
        can_change_info = True,
        can_invite_users = True,
        can_pin_messages = True,
        can_manage_topics = True,
        can_send_media_messages = True
        )

    # Desmutear al usuario
    try:
        await app.restrict_chat_member(chat_id, user_id, permissions)
    except Exception as e:
        print(e)
        return False

    if message:
        await message.reply(f"El usuario {name} ha sido desmuteado.")
        return
    
    return True

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
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return
    
    await MuteUser(app, chat_id, user_mute_id, message=message, name=name)



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
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return
    
    await UnmuteUser(app, chat_id, user_mute_id, name, message)