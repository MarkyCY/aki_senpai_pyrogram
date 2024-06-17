from pyrogram import Client
from pyrogram.types import Message, ReplyParameters, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from database.mongodb import get_db


@Client.on_message(filters.command('info'))
async def info_command(app: Client, message: Message, user_data=None):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users


    # Obtener el elemento del comando
    if message.command and len(message.command) > 1:
        elemento = message.command[1]

        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user = get_user.user

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user = get_user.user
    
    elif user_data is None:
        user = message.reply_to_message.from_user
        if message.reply_to_message is None:
            await message.reply_text('Por favor, responde a un mensaje')
            return

    else:
        user = user_data
    
    user_action_id = user.id
    
    btns = [
        [
            InlineKeyboardButton("⚠️Advertencias", callback_data=f"warn_{user_action_id}"),
            InlineKeyboardButton("🪪Roles", callback_data=f"show_roles_{user_action_id}"),
        ],
        [
            InlineKeyboardButton("🔇Silenciar", callback_data=f"mute_{user_action_id}"),
            InlineKeyboardButton("⛔️Banear", callback_data=f"ban_{user_action_id}")
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    
    # Obtengo el rol del usuario en el chat
    chat_member = await app.get_chat_member(message.chat.id, user.id)
    role_name = str(chat_member.status).split('.')[1]
    role = role_name.capitalize()

    if role_name == "administrator":
        markup = None
    
    user_db = await users.find_one({"user_id": user.id})
    
    if user_db is None:
        await users.insert_one({
            "user_id": user.id
        })
        user_db = await users.find_one({"user_id": user.id})
    
    description = user_db.get('description', '-')

    msg=f"""🆔ID: {user.id}
👱Nombre: {user.first_name}
👤Nombre de usuario: @{user.username}
🪪Rol: {role}
⚠️Advertencias: {user_db.get('warnings', 0)}/3
ℹ️Descripción: {description}
"""
    
    if user_data is None:
        await app.send_message(message.chat.id, text=msg, reply_parameters=ReplyParameters(message_id=message.reply_to_message_id), reply_markup=markup)
    else:
        await app.edit_message_text(message.chat.id, message.id, text=msg, reply_markup=markup)