from datetime import datetime, timedelta
from pyrogram import utils
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from database.mongodb import get_db
from plugins.commands.admin.mute import MuteUser

async def get_warnings(user_id):
    
    db = await get_db()
    users = db.users

    user = await users.find_one({"user_id": user_id})
    if user and "warnings" in user:
        return user["warnings"]
    else:
        return 0

async def add_warning(app, chat_id, user_id):
    
    db = await get_db()
    users = db.users

    user = await users.find_one({"user_id": user_id})
    if user:
        if "warnings" in user:
            warnings = user["warnings"] + 1
            if warnings >= 3:
                await MuteUser(app, chat_id, user_id)
                await users.update_one({"user_id": user_id}, {"$set": {"warnings": 2}})
                return "Usuario muteado por llegar al limite de advertencias."
            else:
                await users.update_one({"user_id": user_id}, {"$set": {"warnings": warnings}})
                return "Usuario advertido."
        else:
            await users.update_one({"user_id": user_id}, {"$set": {"warnings": 1}})
            return "Usuario advertido."
    else:
        await users.insert_one({"user_id": user_id, "warnings": 1})
        return "Usuario advertido."

async def remove_warning(user_id):
    
    db = await get_db()
    users = db.users

    user = await users.find_one({"user_id": user_id})
    if user and "warnings" in user:
        warnings = user["warnings"] - 1
        if warnings < 0:
            return "Este usuario no tiene advertencias."
        else:
            await users.update_one({"user_id": user_id}, {"$set": {"warnings": warnings}})
            return "1 Advertencia removida."
    else:
        return "Este usuario no tiene advertencias."
    
@Client.on_message(filters.command('aki_warn'))
async def warn_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje de un usuario.")
        return

    # ID del usuario a mutear
    user_warn_id = message.reply_to_message.from_user.id

    # Obtener la ID del chat
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return
    
    chat_member = await app.get_chat_member(chat_id, user_warn_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return
    
    Warn = await add_warning(app, chat_id, user_warn_id)
    await message.reply(Warn)