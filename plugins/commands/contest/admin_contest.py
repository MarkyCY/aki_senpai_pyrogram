from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

conversations = {}
infos = {}

from database.mongodb import get_db

def conv_filter(conversation_level):
    def func(_, __, message):
        return conversations.get(message.from_user.id) == conversation_level

    return filters.create(func, "ConversationFilter")

@Client.on_message(filters.command('form') & filters.private)
async def contest_select(app: Client, message: Message):
    print("Contest: ", message.from_user.username)
    buttons = [
        [
            InlineKeyboardButton("🗒️Texto", callback_data="contest_type_0"),
            InlineKeyboardButton("🖼️Imágenes", callback_data="contest_type_1"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.reply_text('Seleccione el tipo de concurso', reply_markup=markup)
    conversations.update({message.from_user.id: "contest_type"})
    infos.update({message.from_user.id: {}})

@Client.on_callback_query(conv_filter("contest_type") & filters.regex(r"^contest_type_\d+$"))
async def type_callback(client, call):

    parts = call.data.split('_')

    if parts[2] == "0":
        type = "text"
    elif parts[2] == "1":
        type = "photo"

    infos.get(call.from_user.id).update({"type": type})

    match type:
        case "text":
            await client.send_message(call.from_user.id, text='Cantidad de Caractéres')
            conversations.update({call.from_user.id: "contest_amount_text"})
            return
        case "photo":
            await client.send_message(call.from_user.id, text='Cantidad de Imagenes')
            conversations.update({call.from_user.id: "contest_amount_photo"})
            return

@Client.on_message(conv_filter("contest_amount_photo") & filters.private)
async def photo_handler(client, message):

    try:
        amount = int(message.text)
    except ValueError:
        await message.reply_text('Ingrese un número para la cantidad de imágenes')
        return

    if amount < 1 or amount > 10:
        await message.reply_text('Ingrese un número entre 1 y 10 para la cantidad de imágenes')
        return

    infos.get(message.from_user.id).update({"amount_photo": amount})
    
    await message.reply_text('Nombre del concurso')
    conversations.update({message.from_user.id: "contest_title"})

@Client.on_message(conv_filter("contest_amount_text") & filters.private)
async def text_handler(client, message):
    print("text")
    try:
        amount = int(message.text)
    except ValueError:
        await message.reply_text('Ingrese un número para la cantidad de palabras')
        return

    if amount < 10 or amount > 500:
        await message.reply_text('Ingrese un número entre 10 y 500 para la cantidad de palabras')
        return

    infos.get(message.from_user.id).update({"amount_text": amount})
    
    await message.reply_text('Nombre del concurso')
    conversations.update({message.from_user.id: "contest_title"})


@Client.on_message(conv_filter("contest_title") & filters.private)
async def title_handler(client, message):

    title = message.text

    infos.get(message.from_user.id).update({"title": title})

    await message.reply_text('Descripción del concurso')
    conversations.update({message.from_user.id: "contest_description"})

@Client.on_message(conv_filter("contest_description") & filters.private)
async def description_handler(client, message):

    description = message.text
    count = len(description)

    if count < 50:
        await message.reply_text('Ingrese una descripción mayor a 50 caractéres')
        return
    
    infos.get(message.from_user.id).update({"description": description})

    buttons = [
        [
            InlineKeyboardButton("Si", callback_data="contest_status_1"),
            InlineKeyboardButton("No", callback_data="contest_status_0"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.reply_text('Está activo el concuso?', reply_markup=markup)
    conversations.update({message.from_user.id: "contest_status"})

@Client.on_callback_query(conv_filter("contest_status") & filters.regex(r"^contest_status_\d+$"))
async def status_callback(client, call):

    parts = call.data.split('_')

    if parts[2] == "0":
        status = "inactive"
    elif parts[2] == "1":
        status = "active"

    infos.get(call.from_user.id).update({"status": status})

    match status:
        case "inactive":
            await client.send_message(call.from_user.id, text='Fecha de Inicio')
            conversations.update({call.from_user.id: "contest_start"})
            return
        case "active":
            await client.send_message(call.from_user.id, text='Fecha de Fin')
            conversations.update({call.from_user.id: "contest_end"})
            return


@Client.on_message(conv_filter("contest_start") & filters.private)
async def start_handler(client, message):
    date = message.text
    
    infos.get(message.from_user.id).update({"subscription": [], "start_date": date})

    await client.send_message(message.from_user.id, text='Fecha de Fin')
    conversations.update({message.from_user.id: "contest_end"})
    return


@Client.on_message(conv_filter("contest_end") & filters.private)
async def end_handler(client, message):

    db = await get_db()
    contest = db.contest

    date = message.text

    infos.get(message.from_user.id).update({"end_date": date, "created_by": message.from_user.id})

    contest.insert_one(infos[message.from_user.id])
    conversations.pop(message.from_user.id)

    await message.reply_text('✔️ Concurso creado!')