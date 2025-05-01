from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

import psutil


@Client.on_message(filters.command('ram'))
async def ram_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    mem = psutil.virtual_memory()
    print(mem)
    # Calcular el uso de la RAM en porcentaje
    uso_ram = mem.percent
    await message.reply_text(f"Uso de RAM: {uso_ram:.2f}%")