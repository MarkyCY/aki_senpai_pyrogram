from pyromod import Client, Message
from pyrogram import enums
from pyrogram import filters
from pyrogram.file_id import FileId
from pyrogram.raw.functions.stickers import RemoveStickerFromSet
from pyrogram.raw.types import InputDocument
#from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

@Client.on_message(filters.command('sticker_info'))
async def sticker_info_command(app: Client, message: Message):
    chat_id = message.chat.id
    # Si el mensaje tiene un reply y es un sticker
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker_id = message.reply_to_message.sticker.file_id
        await app.send_message(chat_id, f"El ID del sticker es: <code>{sticker_id}</code>", reply_to_message_id=message.reply_to_message_id, parse_mode=enums.ParseMode.HTML)

    # Si el mensaje tiene un reply pero no es un sticker
    elif message.reply_to_message and not message.reply_to_message.sticker:
        await app.send_message(chat_id, "Este comando solo puede ser usado con stickers. Por favor, haz reply a un sticker.", reply_to_message_id=message.reply_to_message_id)

    # Si el mensaje no tiene un reply
    else:
        await app.send_message(chat_id, "Por favor, haz reply a un sticker para obtener su ID.")

@Client.on_message(filters.command('del_sticker'))
async def del_sticker_command(app: Client, message: Message):
    chat_id = message.chat.id
    
    if not (message.reply_to_message and message.reply_to_message.sticker):
        await app.send_message(chat_id, "Por favor, haz reply a un sticker para obtener su ID.")
        return
    

    sticker_id = message.reply_to_message.sticker.file_id
    decoded = FileId.decode(sticker_id)


    try:
        sticker_to_remove = InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )
        print(sticker_to_remove)
        result = await app.invoke(RemoveStickerFromSet(sticker=sticker_to_remove))
        
        if result:
            await app.send_message(chat_id, "El sticker se ha eliminado del pack.", reply_to_message_id=message.reply_to_message_id)
    except Exception as e:
        print(e)
        await app.send_message(chat_id, "No se pudo eliminar el sticker.", reply_to_message_id=message.reply_to_message_id)