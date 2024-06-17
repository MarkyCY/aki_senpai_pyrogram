from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters
from pyrogram import enums

from database.mongodb import get_db
from plugins.others.contest import *

import os

@Client.on_message(filters.command(['concursos', 'sub']))
async def contest_command(app: Client, message: Message, call_msg_id=None, user_id=None):
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🏆 Ver Concursos",
                    url="https://t.me/Akira_Senpai_bot?start=contests"
                )
            ],
        ]
    )
    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'private'):
        await message.reply_text(text="Este comando solo puede ser usado en privado. Presiona el botón.", reply_markup=reply_markup)
        return

    # Conectar a la base de datos
    db = await get_db()
    users = db.users
    contest = db.contest
    admins = db.admins

    chat_id = message.chat.id
    if user_id is None:
        user_id = message.from_user.id
    username = message.from_user.username

    chat_member = await app.get_chat_member(-1001485529816, user_id)

    if chat_member is None:
        await message.reply_text(text=f"Solo los integrantes de <a href='https://t.me/OtakuSenpai2020'>Otaku Senpai</a> pueden participar en el concurso.", parse_mode=enums.ParseMode.HTML)
        return

    if username is None:
        await message.reply_text(text=f"Lo siento, no te puedes subscribir al concurso sin un nombre de usuario. Para crearte un nombre de usuario:\nVe a `Ajustes > Nombre de usuario` y escribe uno que sea único.")
        return
    
    user = users.find_one({'user_id': user_id})
    if user:
        pass
    else:
        await reg_user(user_id, username)

    contest_list = contest.find({'status': 'active'})

    Admin = [doc['user_id'] async for doc in admins.find()]
    if user_id in Admin:
        contest_list = contest.find()
    count = await contest_list.to_list(length=None)

    if contest_list is None or len(count) == 0:
        await app.send_message(chat_id, text=f"Lo siento, no hay ningún concurso abierto en este momento.")
        return
    
    btns = []

    if user_id not in Admin:
        list = [doc async for doc in contest.find({'status': 'active'})]
        for contest in list:
            title = contest['title']
            btn = [InlineKeyboardButton(str(title), callback_data=f"show_contest_{contest['_id']}")]
            btns.append(btn)
    else:
        list = [doc async for doc in contest.find()]
        for contest in list:
            title = contest['title']
            if contest['status'] == 'active':
                title = f"{title} | 🔵"
            elif contest['status'] == 'inactive':
                title = f"{title} | ⚪"
            elif contest['status'] == 'closed':
                title = f"{title} | 🔴"
            btn = [InlineKeyboardButton(str(title), callback_data=f"show_contest_{contest['_id']}")]
            btns.append(btn)

    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    if call_msg_id is not None:
        await app.edit_message_text(chat_id, call_msg_id, text=f"Concursos Disponibles:", reply_markup=markup)
        return
    
    await message.reply_text(text=f"Concursos Disponibles:", reply_markup=markup)