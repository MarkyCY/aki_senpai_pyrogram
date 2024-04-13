from pyromod import Client, Message
from pyrogram import filters
#from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

@Client.on_message(filters.command('start'))
async def start_command(app: Client, message: Message):
    chat_type = str(message.chat.type).split('.')[1].lower()
    if chat_type == 'private':
        await message.reply_text(text="Hola para subscribirte en el concurso solo escribe o toca: /sub")
    else:
        await message.reply_text(text="Uhhh quieres participar? Contactame por PV y escribeme /sub \n@Akira_Senpai_bot")