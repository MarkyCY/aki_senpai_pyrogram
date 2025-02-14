from pyrogram import Client
from pyrogram.types import Message, ReplyParameters
from pyrogram import filters

from database.mongodb import get_db

@Client.on_message(filters.command('set_bio'))
async def set_bio_command(app: Client, message: Message):

    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    user_id = message.from_user.id
    args = message.text.split(None, 1)

    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'supergroup' or chat_type == 'group'):
        await app.send_message(message.chat.id, text="Este comando solo puede ser usado en grupos y en supergrupos")
        return

    if not message.reply_to_message:
        await message.reply_text(text="Debe hacer reply para este comando.")
        return

    if len(args) < 2:
        await message.reply_text(text="Proporcionar una descripción para el usuario.")
        return

    if user_id not in [873919300]:
        await message.reply_text(text="Solo mi padre puede usar ese comando por ahora :(")
        return

    description = args[1]
    notice = "Descripción actualizada correctamente."
    username = message.reply_to_message.from_user.username
    if len(description) > 250:
        description = description[:250]
        notice += "\n\nEsta descripción se redujo a 250 caracteres."

    user_id = message.reply_to_message.from_user.id
    await users.update_one({"user_id": user_id}, {"$set": {"username": username, "description": description}}, upsert=True)
    await message.reply(text=notice, reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))