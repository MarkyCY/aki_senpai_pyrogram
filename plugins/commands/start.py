from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
#from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
#import asyncio

from plugins.commands.rules import rules_command
from plugins.commands.contest.contest import contest_command

@Client.on_message(filters.command('start'))
async def start_command(app: Client, message: Message):
    chat_type = str(message.chat.type).split('.')[1].lower()
    try:
        elemento = message.command[1]

        if elemento == "rules":
            await rules_command(app, message)
            return        
        if elemento == "contests":
            await contest_command(app, message)
            return        
    except (IndexError, NameError):
        pass
    
    if chat_type == 'private':
        await message.reply_text(text="Hola soy Akira Senpai, para ver los concuros escribe: /concursos")
    else:
        await message.reply_text(text="Uhhh quieres participar? Contactame por PV y escribeme /concursos \n@Akira_Senpai_bot")