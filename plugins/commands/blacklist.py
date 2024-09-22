    
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import get_db

group_perm = [-1001485529816, -1001664356911]

@Client.on_message(filters.command('blacklist'))
async def blacklist_command(app: Client, message: Message, user_data=None):

    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in group_perm:
        await message.reply_text(text="Este comando no está disponible en este grupo.")
        return

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply_text(text="Solo los administradores pueden usar este comando.")

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
    