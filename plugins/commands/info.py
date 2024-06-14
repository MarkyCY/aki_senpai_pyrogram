from pyrogram import Client
from pyrogram.types import Message, ReplyParameters, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from database.mongodb import get_db


@Client.on_message(filters.command('info'))
async def info_command(app: Client, message: Message):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    btns = [
        [
            InlineKeyboardButton("⚠️Advertencias", callback_data=f"warn_{message.from_user.id}"),
            InlineKeyboardButton("🪪Roles", callback_data=f"show_roles"),
        ],
        [
            InlineKeyboardButton("🤫Silenciar", callback_data=f"mute_{message.from_user.id}"),
            InlineKeyboardButton("⛔️Banear", callback_data=f"ban_{message.from_user.id}")
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    
    # Verificar si el mensaje es una respuesta a otro mensaje
    if message.reply_to_message is not None:
        message.reply_text('Por favor, responde a un mensaje')
        return
    
    # Si el mensaje es un reply a otro mensaje, obtengo los datos del usuario al que se le hizo reply
    user = message.reply_to_message.from_user
    # Obtengo el rol del usuario en el chat
    try:
        chat_member = await app.get_chat_member(message.chat.id, user.id)
        role_name = str(chat_member.status).split('.')[1]
        role = role_name.capitalize()
     
        user_db = await users.find_one({"user_id": user.id})
     
        if user_db is None:
            await users.insert_one({
                "user_id": user.id
            })
            user_db = await users.find_one({"user_id": user.id})
     
        description = user_db.get('description', '-')
        # Envio la información del usuario y su rol en un mensaje de reply al mensaje original
        await app.send_message(message.chat.id, text=f"""🆔ID: {user.id}
👱Nombre: {user.first_name}
👤Nombre de usuario: @{user.username}
🪪Rol: {role}
⚠️Advertencias: {user_db.get('warnings', 0)}/3
ℹ️Descripción: {description}
""", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id), reply_markup=markup)
    except Exception as e:
        print(e)
        chat_member = await app.get_users(user.id)
        # Envio la información del usuario y su rol en un mensaje de reply al mensaje original
        await app.send_message(message.chat.id, text=f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))