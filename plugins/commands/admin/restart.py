from pyrogram import Client, filters
from pyrogram.types import  Message

# import shutil
import os

@Client.on_message(filters.command('restart'))
async def restart_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id != -1001485529816:
        return await message.reply_text("Este comando es exclusivo de Otaku Senpai")

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")

    await message.reply_text("Reiniciando...")
    # shutil.rmtree("downloads", ignore_errors=True)
    os.system(f'pkill -f "python main.py" && bash startup.sh')

@Client.on_message(filters.command('kill'))
async def kill_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id != -1001485529816:
        return await message.reply_text("Este comando es exclusivo de Otaku Senpai")

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")

    await message.reply_text("Bye...")
    # shutil.rmtree("downloads", ignore_errors=True)
    os.system(f'pkill -f "python main.py"')