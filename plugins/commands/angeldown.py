from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

@Client.on_message(filters.command('upload'))
async def angel_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")

    args = message.text.split(maxsplit=3)
    if len(args) < 2:
        return await message.reply_text("Proporciona la dirección.")

    dir = args[1].strip()

    await app.send_document(
        chat_id=chat_id,
        document=dir,
        caption=f"Archivo subido")