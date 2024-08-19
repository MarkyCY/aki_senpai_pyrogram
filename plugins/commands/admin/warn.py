from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

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
    
@Client.on_message(filters.command('warn'))
async def warn_command(app: Client, message: Message):

    if not message.reply_to_message and message.command and len(message.command) > 1:
        elemento = message.command[1]
        
        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user_warn_id = get_user.user.id
            name = get_user.user.first_name
            

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user_warn_id = get_user.user.id
                name = get_user.user.first_name
    
    elif not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas advertir.")
        return
    
    else:
        user_warn_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name

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
    btns = [
        [
            InlineKeyboardButton(
                "-1 Warn", callback_data=f"remove_warn_{user_warn_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    await message.reply(Warn, reply_markup=markup)