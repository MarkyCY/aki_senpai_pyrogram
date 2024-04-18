from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import enums

from database.mongodb import get_db
from plugins.others.contest import *

import os

@Client.on_message(filters.command('sub'))
async def sub_command(app: Client, message: Message):
    
    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'private'):
        await message.reply_text(text="Este comando solo puede ser usado en privado.")
        return

    # Conectar a la base de datos
    db = await get_db()
    users = db.users
    contest = db.contest

    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    found = False

    chat_member = await app.get_chat_member(-1001485529816, user_id)

    if chat_member is None:
        await message.reply_text(text=f"Solo los participantes de <a href='https://t.me/OtakuSenpai2020'>Otaku Senpai</a> pueden participar en el concurso.", parse_mode=enums.ParseMode.HTML)
        return

    if username is None:
        await message.reply_text(text=f"Lo siento, no te puedes subscribir al concurso sin un nombre de usuario")
        return
    
    user = users.find_one({'user_id': user_id})
    if user:
        pass
    else:
        await reg_user(user_id, username)

    contest_list = contest.find({'contest_num': 2})

    async for user in contest_list:
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break
                
            if found:
                await app.send_message(chat_id, text=f"Oh! Ya estabas registrado en el concurso.")
                break
            
            if not found:
                await add_user(user_id)
                await app.send_message(chat_id, text=f'Bien acabo de registrarte en el concurso @{username}. Para desuscribirte en cualquier momento usa el comando /unsub')

@Client.on_message(filters.command('unsub'))
async def unsub_command(app: Client, message: Message):
    
    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'private'):
        await message.reply_text(text="Este comando solo puede ser usado en privado.")
        return

    # Conectar a la base de datos
    db = await get_db()
    users = db.users
    contest = db.contest
    Contest_Data = db.contest_data

    chat_id = message.chat.id
    user_id = message.from_user.id
    found = False
    
    user = await users.find_one({'user_id': user_id})
    content_photo = await Contest_Data.find_one({'u_id': user_id, 'type': 'photo'})
    content_text = await Contest_Data.find_one({'u_id': user_id, 'type': 'text'})

    contest_list = contest.find({'contest_num': 2})

    async for user in contest_list:
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break

            if not found:
                await app.send_message(chat_id, text=f'No estás registrado en el concurso')
                return
            
            await del_user(user_id)
            await app.send_message(chat_id, text=f"Bien te has desuscrito del concurso.")

            if content_photo:
                await Contest_Data.delete_one({'u_id': user_id, 'type': 'photo'})
                os.remove(f"./downloads/{user_id}.jpg")

            if content_text:
                await Contest_Data.delete_one({'u_id': user_id, 'type': 'text'})
            
            await app.send_message(chat_id, text=f"Se han eliminado tus datos de concurso.")
            break