from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from database.mongodb import get_db
from plugins.others.admin_func import isModerator

@Client.on_message(filters.command('aki_mute'))
async def mute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas mutear.")
        return

    # ID del usuario a mutear
    user_mute = message.reply_to_message.from_user.id

    # Obtener la ID del chat
    chat_id = message.chat.id

    # Verifica si el que ejecuta el comando es un moderador
    if not await isModerator(message.from_user.id):
        await message.reply("No tienes permisos para usar este comando.")
        return

    # Configurar los permisos de restricción (mutear al usuario)
    permissions = ChatPermissions(can_send_messages=False)

    # Calcular la fecha hasta la cual el usuario estará muteado (24 horas desde ahora)
    until_date = datetime.now() + timedelta(days=1)

    # Mutear al usuario
    await app.restrict_chat_member(chat_id, user_mute, permissions, until_date=until_date)

    # Confirmar la acción en el chat
    await message.reply(f"El usuario {user_mute} ha sido muteado por 24 horas.")


@Client.on_message(filters.command('aki_unmute'))
async def unmute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas desmutear.")
        return

    # ID del usuario a desmutear
    user_unmute = message.reply_to_message.from_user.id

    # Obtener la ID del chat
    chat_id = message.chat.id

    # Verifica si el que ejecuta el comando es un moderador
    if not await isModerator(message.from_user.id):
        await message.reply("No tienes permisos para usar este comando.")
        return

    # Configurar los permisos de restricción (desmutear al usuario)
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True)

    # Desmutear al usuario
    await app.restrict_chat_member(chat_id, user_unmute, permissions)

    # Confirmar la acción en el chat
    await message.reply(f"El usuario {user_unmute} ha sido desmuteado.")


@Client.on_message(filters.command('aki_delete'))
async def delete_message_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje que deseas eliminar.")
        return

    # Obtener el ID del mensaje a eliminar
    message_id_to_delete = message.reply_to_message.id

    # Obtener la ID del chat
    chat_id = message.chat.id

    # Verifica si el que ejecuta el comando es un moderador
    if not await isModerator(message.from_user.id):
        await message.reply("No tienes permisos para usar este comando.")
        return

    # Eliminar el mensaje
    await app.delete_messages(chat_id, message_id_to_delete)

    # Confirmar la acción en el chat
    await message.reply("El mensaje ha sido eliminado.")