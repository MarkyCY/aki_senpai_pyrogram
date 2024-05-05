from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

conversations = {}
infos = {}

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
async def type_handler(client, call):

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

    infos.get(message.from_user.id).update({"contest_amount_photo": amount})
    
    await message.reply_text('Nombre del concurso')
    conversations.update({message.from_user.id: "contest_title"})

@Client.on_message(conv_filter("contest_amount_text") & filters.private)
async def text_handler(client, message):
    print("text")
    try:
        amount = int(message.text)
    except ValueError:
        await message.reply_text('Ingrese un número para la cantidad de caracteres')
        return

    if amount < 200 or amount > 2000:
        await message.reply_text('Ingrese un número entre 200 y 2000 para la cantidad de caractéres')
        return

    infos.get(message.from_user.id).update({"contest_amount_text": amount})
    
    await message.reply_text('Nombre del concurso')
    conversations.update({message.from_user.id: "contest_title"})


@Client.on_message(conv_filter("contest_title") & filters.private)
async def title_handler(client, message):

    title = message.text

    infos.get(message.from_user.id).update({"contest_title": title})

    await message.reply_text('Descripción del concurso')
    conversations.update({message.from_user.id: "contest_description"})

@Client.on_message(conv_filter("contest_description") & filters.private)
async def description_handler(client, message):

    description = message.text
    count = len(description)

    if count < 50:
        await message.reply_text('Ingrese una descripción mayor a 50 caractéres')
        return


    infos.get(message.from_user.id).update({"contest_description": description})
    print(infos)
    conversations.pop(message.from_user.id)