from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from database.mongodb import get_db
from plugins.others.contest import *

from plugins.commands.contest.contest import contest_command

@Client.on_callback_query(filters.regex(r"^show_contest_\d+$"))
async def show_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_num = int(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    username = call.from_user.username
    mid = call.message.id

    db = await get_db()
    contest = db.contest

    contest_sel = await contest.find_one({'contest_num': contest_num})

    if username is None:
        await app.answer_callback_query(call.id, "Deber tener un nombre de usuario para participar en el concurso... Si tienes dudas pregunta en el grupo.", True)
        return
    
    if contest_sel is None:
        await app.answer_callback_query(call.id, "No existe el concurso...", True)
        return
    
    if contest_sel["status"] != "active":
        await app.answer_callback_query(call.id, "El concurso está cerrado...", True)
        return
    
    text = f"""
Acciones para el concurso de {contest_sel['title']}:
"""
    buttons = [
        [
            InlineKeyboardButton("✔️Suscribirse", callback_data=f"sub_contest_{int(contest_num)}"),
            InlineKeyboardButton("❌Desuscribirse", callback_data=f"unsub_contest_{int(contest_num)}"),
        ],
        [
            InlineKeyboardButton("🔙Atrás", callback_data=f"back_contests")
        ]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await app.edit_message_text(chat_id, mid, text=text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^sub_contest_\d+$"))
async def sub_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_num = int(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    username = call.from_user.username
    mid = call.message.id

    db = await get_db()
    contest = db.contest

    found = None

    contest_sel = await contest.find_one({'contest_num': contest_num})

    if contest_sel is None:
        await app.answer_callback_query(call.id, "No existe el concurso...", True)
        return
    
    if contest_sel["status"] != "active":
        await app.answer_callback_query(call.id, "El concurso está cerrado...", True)
        return

    for sub in contest_sel['subscription']:
        if sub['user'] == user_id:
            found = True
            break
                
    if found is True:
        await app.answer_callback_query(call.id, "Oh! Ya estabas registrado en el concurso...", True)
        return
    
    if not found:
        await add_user(user_id)
        await app.edit_message_text(chat_id, mid, text=f'Bien acabo de registrarte en el concurso @{username}.')
        return


@Client.on_callback_query(filters.regex(r"^unsub_contest_\d+$"))
async def unsub_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_num = int(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mid = call.message.id

    db = await get_db()
    contest = db.contest

    found = None

    contest_sel = await contest.find_one({'contest_num': contest_num})

    if contest_sel is None:
        await app.answer_callback_query(call.id, "No existe el concurso...", True)
        return
    
    if contest_sel["status"] != "active":
        await app.answer_callback_query(call.id, "El concurso está cerrado...", True)
        return

    for sub in contest_sel['subscription']:
        if sub['user'] == user_id:
            found = True
            break
                
    if not found:
        await app.send_message(chat_id, text=f'No estás registrado en el concurso')
        await app.answer_callback_query(call.id, "Oh! No estás registrado en el concurso", True)
        return
    
    await del_user(user_id)
    await app.edit_message_text(chat_id, mid, text=f'Bien te has desuscrito del concurso.')
    return


@Client.on_callback_query(filters.regex(r"^back_contests"))
async def back_contests(app: Client, call: CallbackQuery):
    await contest_command(app, call.message, call.message.id)