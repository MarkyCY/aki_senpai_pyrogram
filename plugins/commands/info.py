from pyrogram import Client
from pyrogram.types import Message, ReplyParameters
from pyrogram import filters

from database.mongodb import get_db

# Conectar a la base de datos
db = get_db()
users = db.users


@Client.on_message(filters.command('info'))
async def info_command(app: Client, message: Message):
    #Verificar si el mensaje es una respuesta a otro mensaje
    if message.reply_to_message is not None:
        #Si el mensaje es un reply a otro mensaje, obtengo los datos del usuario al que se le hizo reply
        user = message.reply_to_message.from_user
        #Obtengo el rol del usuario en el chat
        try:
            chat_member = await app.get_chat_member(message.chat.id, user.id)
            role_name = str(chat_member.status).split('.')[1]
            role = role_name.capitalize()
            user_db = users.find_one({"user_id": user.id})
            description = user_db.get('description', '-')
            #Envio la información del usuario y su rol en un mensaje de reply al mensaje original
            await app.send_message(message.chat.id, text=f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role}\nDescripción: {description}", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))
        except Exception as e:
            print(e)
            chat_member = await app.get_users(user.id)
            #Envio la información del usuario y su rol en un mensaje de reply al mensaje original
            await app.send_message(message.chat.id, text=f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))
        
    else:
        #Si el mensaje no es una respuesta a otro mensaje, obtener los datos del usuario que envió el comando
        user = message.from_user
        #Obtengo el rol del usuario en el chat
        try:
            chat_member = await app.get_chat_member(message.chat.id, user.id)
            role_name = str(chat_member.status).split('.')[1]
            role = role_name.capitalize()
            user_db = users.find_one({"user_id": user.id})
            description = user_db.get('description', '-')
            await app.send_message(message.chat.id, text=f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role}\nDescripción: {description}", reply_parameters=ReplyParameters(message_id=message.id))
        except Exception as e:
            print(e)
            chat_member = await app.get_users(user.id)
            await app.send_message(message.chat.id, text=f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}", reply_parameters=ReplyParameters(message_id=message.id))