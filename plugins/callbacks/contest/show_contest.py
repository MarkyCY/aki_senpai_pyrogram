from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji
from pyrogram import filters, enums

from database.mongodb import get_db
from plugins.others.contest import *
from bson import ObjectId

from plugins.commands.contest.contest import contest_command
from datetime import datetime

conversations_contest = {}
infos_contest = {}

def timestamp_to_str(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%d/%m/%Y %I:%M %p")

def string_a_timestamp(fecha_string):
    formato = "%d/%m/%Y %H:%M"
    try:
        fecha_objeto = datetime.strptime(fecha_string, formato)
        timestamp = int(fecha_objeto.timestamp())
        return timestamp
    except ValueError:
        return False

def conv_filter(conversation_level):
    def func(_, __, message):
        return conversations_contest.get(message.from_user.id) == conversation_level

    return filters.create(func, "ConversationFilter")

@Client.on_callback_query(filters.regex(r"^show_contest_[a-f\d]{24}$"))
async def show_contest(app: Client, call: CallbackQuery, re_open=None):

    try:
        conversations_contest.pop(call.from_user.id)
        infos_contest.pop(call.from_user.id)
    except KeyError:
        pass

    if re_open:
        contest_id = re_open
    else:
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
    
    Admin = [doc['user_id'] async for doc in admins.find()]
    #if call.from_user.id not in Admin:
    if contest_sel["status"] != "active" and call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "El concurso está cerrado...", True)
        return
    
    text = f"""
Concurso de <strong>{contest_sel['title']}</strong>

<strong>Descripción</strong>:
{contest_sel['description']}
<strong>Fecha de cierre</strong>: {timestamp_to_str(contest_sel['end_date'])}
"""
    buttons = [
        [
            InlineKeyboardButton("✔️Suscribirse", callback_data=f"sub_contest_{contest_id}"),
            InlineKeyboardButton("❌Desuscribirse", callback_data=f"unsub_contest_{contest_id}"),
        ]
    ]
    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id in Admin:
        match contest_sel['status']:
            case "active":
                buttons.append([InlineKeyboardButton(f"🔒Cerrar", callback_data=f"close_contest_{contest_id}"), InlineKeyboardButton(f"📝Editar", callback_data=f"edit_contest_{contest_id}")])
            case "closed" | "inactive":
                buttons.append([InlineKeyboardButton("🔓Abrir", f"open_contest_{contest_id}"), InlineKeyboardButton(f"📝Editar", callback_data=f"edit_contest_{contest_id}")])
        
        buttons.append([InlineKeyboardButton("👥Ver suscriptores", callback_data=f"subscribers_contest_{contest_id}")])
                

    buttons.append([InlineKeyboardButton("🔙Atrás", callback_data=f"back_contests")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        await app.edit_message_text(chat_id, mid, text=text, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
    except:    
        await app.edit_inline_reply_markup(inline_message_id=str(mid), reply_markup=markup)


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
    Disq = None

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
    if 'disqualified' in contest_sel:
        for disq in contest_sel['disqualified']:
            if disq['user'] == user_id:
                Disq = True
                break
    
    if Disq is True:
        await app.answer_callback_query(call.id, "Lo siento pero estás descalificado para este concurso...", True)
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

        try:
            await app.edit_message_text(chat_id, mid, text=f'Bien acabo de registrarte en el concurso {name}.', reply_markup=markup)
        except Exception as e:
            print(e)

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
    await contest_command(app, call.message, call.message.id, call.from_user.id)


#region ADMINS

@Client.on_callback_query(filters.regex(r"^close_contest_[a-f\d]{24}$"))
async def close_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    
    db = await get_db()
    contest = db.contest
    admins = db.admins

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
    
    try:
        contest.update_one({'_id': contest_id}, {'$set': {'status': 'closed'}})
    except Exception as e:
        print("Ha ocurrido un error: " + str(e))
        return
    
    await show_contest(app, call, contest_id)
    await app.answer_callback_query(call.id, "Concurso cerrado!")

@Client.on_callback_query(filters.regex(r"^open_contest_[a-f\d]{24}$"))
async def open_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    
    db = await get_db()
    contest = db.contest
    admins = db.admins

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
    
    try:
        contest.update_one({'_id': contest_id}, {'$set': {'status': 'active'}})
    except Exception as e:
        print("Ha ocurrido un error: " + str(e))
        return
    
    await show_contest(app, call, contest_id)
    await app.answer_callback_query(call.id, "Concurso abierto!")

#Ver Suscriptores
@Client.on_callback_query(filters.regex(r"^subscribers_contest_[a-f\d]{24}$"))
async def subscribers_contest(app: Client, call: CallbackQuery):
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])

    db = await get_db()
    contest = db.contest
    admins = db.admins

    contest_sel = await contest.find_one({'_id': contest_id})

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
    
    subs = []
    if contest_sel['subscription'] == []:
        return await app.answer_callback_query(call.id, "No hay suscriptores..")
    else:
        text = f"Estos son los suscriptores del concurso {contest_sel['title']}:\n\n"
        for sub in contest_sel['subscription']:
            subs.append(sub['user'])
    try:
        users = await app.get_users(subs)
    except Exception as e:
        print("Ha ocurrido un error: " + str(e))

    text = text + "\n".join([f"{i}. <a href='tg://user?id={user.id}'>{user.first_name}</a>" for i, user in enumerate(users, start=1)])
    return await app.send_message(call.message.chat.id, text, parse_mode=enums.ParseMode.HTML)


#region Edit Contest
@Client.on_callback_query(filters.regex(r"^edit_contest_[a-f\d]{24}$"))
async def edit_contest(app: Client, call: CallbackQuery, edit_id=None, message_id=None):
    if edit_id:
        contest_id = edit_id
        chat_id = call.chat.id
    else:
        parts = call.data.split('_')
        contest_id = ObjectId(parts[2])
        message_id = call.message.id
        chat_id = call.message.chat.id

    db = await get_db()
    contest = db.contest
    admins = db.admins

    contest_sel = await contest.find_one({'_id': contest_id})

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
        
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📝 Título", f"edit_contest_0_{contest_id}"),
                InlineKeyboardButton("💬 Descripción", f"edit_contest_1_{contest_id}"),
            ],
            [
                InlineKeyboardButton("📆 Fecha de Inicio", f"edit_contest_2_{contest_id}"),
                InlineKeyboardButton("🕰️ Fecha de Cierre", f"edit_contest_3_{contest_id}"),
            ],
            [
                InlineKeyboardButton("🔙Atrás", f"show_contest_{contest_id}"),
            ],
        ]
    )


    text = f"""
Edición del conruso <strong>{contest_sel['title']}:</strong>

<strong>Descripción</strong>:
{contest_sel['description']}

<strong>Fecha de inicio</strong>: {timestamp_to_str(contest_sel['start_date'])}
<strong>Fecha de cierre</strong>: {timestamp_to_str(contest_sel['end_date'])}
"""

    await app.edit_message_text(chat_id, message_id, text=text, reply_markup=reply_markup)


#Leyenda: 0 - Titulo, 1 - Descripcion, 2 - Fecha de inicio, 3 - Fecha de cierre
@Client.on_callback_query(filters.regex(r"^edit_contest_(\d+)_[a-f\d]{24}$"))
async def edit_title(app: Client, call: CallbackQuery):
    # Add your logic here for editing the title
    parts = call.data.split('_')
    type = int(parts[2])
    contest_id = ObjectId(parts[3])

    chat_id = call.message.chat.id

    db = await get_db()
    admins = db.admins

    Admin = [doc['user_id'] async for doc in admins.find()]
    if call.from_user.id not in Admin:
        await app.answer_callback_query(call.id, "No eres administrador...")
        return
    
    match type:
        case 0:
            await app.send_message(chat_id, f"Escribe el nuevo titulo del concurso:")
        case 1:
            await app.send_message(chat_id, f"Escribe la nueva descripción del concurso:")
        case 2:
            await app.send_message(chat_id, f"Escribe la nueva fecha de inicio del concurso:\n\nFormato:\n25/07/2024 15:30\nDD/MM/AAAA HH:MM")
        case 3:
            await app.send_message(chat_id, f"Escribe la nueva fecha de cierre del concurso:\n\nFormato:\n25/07/2024 15:30\nDD/MM/AAAA HH:MM")
        case _:
            await app.answer_callback_query(call.id, "Opcion invalida...")
            return

    conversations_contest.update({call.from_user.id: "edit_contest"})
    infos_contest.update({call.from_user.id: {"edit": type, "contest_id": contest_id, "message_id": call.message.id}})



@Client.on_message(conv_filter("edit_contest") & filters.private)
async def edit_contest_step(app: Client, message: Message):
    db = await get_db()
    contest = db.contest
    admins = db.admins

    Admin = [doc['user_id'] async for doc in admins.find()]
    if message.from_user.id not in Admin:
        await app.answer_callback_query(message.id, "No eres administrador...")
        return

    chat_id = message.chat.id
    text = message.text

    edit = infos_contest[message.from_user.id]["edit"]
    contest_id = infos_contest[message.from_user.id]["contest_id"]
    message_id = infos_contest[message.from_user.id]["message_id"]

    contest_sel = await contest.find_one({'_id': contest_id})

    match edit:
        case 0:
            try:
                contest.update_one({'_id': contest_id}, {'$set': {'title': text}})
            except Exception as e:
                print("Ha ocurrido un error: " + str(e))
                return
            
            await edit_contest(app, message, contest_id, message_id)
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👍")])

        case 1:
            try:
                contest.update_one({'_id': contest_id}, {'$set': {'description': text}})
            except Exception as e:
                print("Ha ocurrido un error: " + str(e))
                return
            
            await edit_contest(app, message, contest_id, message_id)
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👍")])

        case 2:

            date = string_a_timestamp(text)

            if date is False:
                await message.reply_text('Formato incorrecto\n\nFormato:\n25/07/2024 15:30\nDD/MM/AAAA HH:MM')
                return
            
            if date > contest_sel['end_date']:
                await message.reply_text('La fecha de inicio debe ser anterior a la de finalización')
                return
            print(date)
            try:
                contest.update_one({'_id': contest_id}, {'$set': {'start_date': date}})
            except Exception as e:
                print("Ha ocurrido un error: " + str(e))
                return
            
            await edit_contest(app, message, contest_id, message_id)
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👍")])

        case 3:
            date = string_a_timestamp(message.text)
    
            if date is False:
                await message.reply_text('Formato incorrecto\n\nFormato:\n25/07/2024 15:30\nDD/MM/AAAA HH:MM')
                return

            if date < contest_sel['start_date']:
                await message.reply_text('La fecha de finalización debe ser posterior a la de inicio')
                return
            print(date)
            try:
                contest.update_one({'_id': contest_id}, {'$set': {'end_date': date}})
            except Exception as e:
                print("Ha ocurrido un error: " + str(e))
                return
            
            await edit_contest(app, message, contest_id, message_id)
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👍")])

        case _:
            await app.send_message(chat_id, "Opcion invalida...")

    conversations_contest.pop(message.from_user.id)
    infos_contest.pop(message.from_user.id)