from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import enums

from database.mongodb import get_db
from plugins.others.admin_func import isCollaborator

import asyncio

@Client.on_message(filters.command('add_anime'))
async def add_anime_command(app: Client, message: Message):
    # Conectar a la base de datos
    db = await get_db()
    animes = db.animes

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque no se ha proporcionado un título.")
        return

    if not message.reply_to_message:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque no se ha respondido a ningún mensaje.")
        return

    if message.reply_to_message.forum_topic_created is not None:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque el mensaje es un tema del foro.")
        return

    chat_username = message.chat.username
    if chat_username is None:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque el chat no tiene un nombre de usuario.")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner'] and await isCollaborator(user_id) is False:
        await message.reply_text(text="Solo los administradores o colaboradores pueden usar este comando.")
        return

    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return

    message_id = message.reply_to_message_id
    topic_id = message.message_thread_id if message.is_topic_message else None
    if not topic_id or topic_id != 251973:
        await message.reply_text(text="Este comando solo puede ser usado en el tópico de <a href='https://t.me/OtakuSenpai2020/251973'>Anime</a>", parse_mode=enums.ParseMode.HTML)
        return

    text = f"Título: {args[1]} \nEnlace: https://t.me/{chat_username}/{topic_id}/{message_id}"
    print(text)
    link = f"https://t.me/{chat_username}/{topic_id}/{message_id}"
    
    is_anime = await animes.find_one({"link": link})
    if is_anime is not None:
        await message.reply_text(text="Este link ya fue registrado")
        return

    try:
        await animes.insert_one({"title": args[1], "link": link})
    except Exception as e:
        await message.reply_text(text=f"Error al registrar anime en la base de datos: {e}")
        return

    msg = await message.reply_text(text=text)
    await asyncio.sleep(5)
    await app.delete_messages(msg.chat.id, [msg.id])

@Client.on_message(filters.command('del_anime'))
async def del_anime_command(app: Client, message: Message):
    # Conectar a la base de datos
    db = await get_db()
    animes = db.animes

    if not message.reply_to_message:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque no se ha respondido a ningún mensaje.")
        return

    if message.reply_to_message.forum_topic_created is not None:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque el mensaje es un tema del foro.")
        return

    chat_username = message.chat.username
    if chat_username is None:
        await message.reply_text(text="No se puede obtener el enlace del mensaje porque el chat no tiene un nombre de usuario.")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner'] and await isCollaborator(user_id) is False:
        await message.reply_text(text="Solo los administradores o colaboradores pueden usar este comando.")
        return

    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return

    message_id = message.reply_to_message_id
    topic_id = message.message_thread_id if message.is_topic_message else None
    if not topic_id or topic_id != 251973:
        await message.reply_text(text="Este comando solo puede ser usado en el tópico de <a href='https://t.me/OtakuSenpai2020/251973'>Anime</a>", parse_mode=enums.ParseMode.HTML)
        return

    link = f"https://t.me/{chat_username}/{topic_id}/{message_id}"
    is_anime = await animes.find_one({"link": link})
    if is_anime is None:
        await message.reply_text(text="Este anime no existe en la base de datos.")
        return

    try:
        await animes.delete_one({"link": link})
    except Exception as e:
        await message.reply_text(text=f"Error al eliminar anime en la base de datos: {e}")
        return

    msg = await message.reply_text(text="Anime eliminado correctamente.")
    await asyncio.sleep(5)
    await app.delete_messages(msg.chat.id, [msg.id])
