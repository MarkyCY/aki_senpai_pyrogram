    
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import get_db

@Client.on_message(filters.command('blacklist'))
async def blacklist_command(app: Client, message: Message, user_data=None):
    # Conectar a la base de datos
    db = await get_db()
    img_blacklist = db.img_blacklist

    if message.reply_to_message is None:
        return await message.reply_text('Por favor, responde a un mensaje')
    
    if message.reply_to_message.sticker is None:
        return await message.reply_text('Solo se pueden agregar stickers')
    
    file_id = message.reply_to_message.sticker.thumbs[0].file_id
    
    bl_item = await img_blacklist.find_one({"file_id": file_id})

    if bl_item is None:
        await img_blacklist.insert_one({"file_id": message.reply_to_message.sticker.file_unique_id})
        await app.download_media(file_id, file_name=f"revise/blacklist/{message.reply_to_message.sticker.file_unique_id}.jpg")
        return await message.reply_text('El archivo ha sido agregado a la lista de bloqueados')
    else:
        return await message.reply_text('El archivo ya está en la lista de bloqueados')
    