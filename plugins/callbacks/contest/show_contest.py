from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, enums

from database.mongodb import get_db
from plugins.others.contest import *
from bson import ObjectId

from plugins.commands.contest.contest import contest_command

@Client.on_callback_query(filters.regex(r"^show_contest_[a-f\d]{24}$"))
async def show_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    chat_id = call.message.chat.id
    username = call.from_user.username
    mid = call.message.id

    db = await get_db()
    contest = db.contest
    admins = db.admins

    contest_sel = await contest.find_one({'_id': contest_id})

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
Concurso de <strong>{contest_sel['title']}</strong>

<strong>Descripción</strong>:
{contest_sel['description']}
"""
    buttons = [
        [
            InlineKeyboardButton("✔️Suscribirse", callback_data=f"sub_contest_{contest_id}"),
            InlineKeyboardButton("❌Desuscribirse", callback_data=f"unsub_contest_{contest_id}"),
        ]
    ]
    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id in Admin:
        buttons.append([InlineKeyboardButton(f"🗑️Eliminar", callback_data=f"trash_contest_{contest_id}")])
    
    buttons.append([InlineKeyboardButton("🔙Atrás", callback_data=f"back_contests")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await app.edit_message_text(chat_id, mid, text=text, parse_mode=enums.ParseMode.HTML, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^sub_contest_[a-f\d]{24}$"))
async def sub_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    username = call.from_user.username
    mid = call.message.id

    db = await get_db()
    contest = db.contest

    found = None

    contest_sel = await contest.find_one({'_id': contest_id})

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
        await add_user(user_id, contest_id)

        if username is not None:
            name = f"@{username}"
        else:
            name = call.from_user.first_name

        buttons = [
            [
                InlineKeyboardButton("❌Desuscribirse", callback_data=f"unsub_contest_{contest_id}"),
            ]
        ]
         
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        match contest_sel['type']:
            case "text":
                text=f"""
<strong>Guía:</strong>

Para entregar tu obra debes enviarmela en formato escrito por mi chat y en privado (y no como una imagen). 

Tu obra debe contener más de <strong>{contest_sel['amount_text']} palabras</strong> y yo te preguntaré si es para el concurso, y para que concurso es en caso de estar participando en otros concursos.
"""
            case "photo":
                text=f"""
<strong>Guía:</strong>

Para entregar tu obra debes enviarmela como imagen(es), se agradece y valora mucho la calidad de la imagen. 

Puedes enviarme hasta un total de <strong>{contest_sel['amount_photo']} imagen(es)</strong> y yo te preguntaré si es para el concurso y para que concurso es, en caso de estar participando en otros concursos.
"""
            case "video":
                text=f"""
<strong>Guía:</strong>

Para entregar tu obra debes enviarmela como video(s), se agradece y valora mucho la calidad de la imagen. 

Puedes enviarme hasta un total de <strong>{contest_sel['amount_video']} video(s)</strong> y yo te preguntaré si es para el concurso y para que concurso es, en caso de estar participando en otros concursos.
"""
        
        await app.send_message(chat_id, text, enums.ParseMode.HTML)

        await app.edit_message_text(chat_id, mid, text=f'Bien acabo de registrarte en el concurso {name}.', reply_markup=markup)
        
        return


@Client.on_callback_query(filters.regex(r"^unsub_contest_[a-f\d]{24}$"))
async def unsub_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mid = call.message.id

    db = await get_db()
    contest = db.contest

    found = None

    contest_sel = await contest.find_one({'_id': contest_id})

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
        await app.answer_callback_query(call.id, "Oh! No estás registrado en el concurso", True)
        return
    
    await del_user(user_id, contest_id)
    await app.edit_message_text(chat_id, mid, text=f'Bien te has desuscrito del concurso.')
    return


@Client.on_callback_query(filters.regex(r"^back_contests"))
async def back_contests(app: Client, call: CallbackQuery):
    await contest_command(app, call.message, call.message.id)


#ADMINS -

@Client.on_callback_query(filters.regex(r"^trash_contest_[a-f\d]{24}$"))
async def sub_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    username = call.from_user.username
    mid = call.message.id
    
    db = await get_db()
    contest = db.contest
    admins = db.admins

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
    
    try:
        contest.delete_one({'_id': contest_id})
    except Exception as e:
        print("Ha ocurrido un error: " + str(e))
        return
    
    await app.edit_message_text(chat_id, mid, text=f'Concurso eliminado!')