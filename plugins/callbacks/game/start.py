from pyrogram import Client
from pyrogram.types import CallbackQuery, Message
from pyrogram import filters
from pyrogram.raw.functions.messages import SetGameScore

# from database.mongodb import get_db
from plugins.others.contest import *

async def awa(_, __, message):
    #if message.game_short_name == "akira_runner":
    return message.game_short_name == "akira_runner"
    
awa_detect = filters.create(awa)

@Client.on_callback_query()
async def awa(app: Client, call: CallbackQuery):
    print(f"Callback data: {call}")

# Handler específico para el juego
@Client.on_callback_query(awa_detect)
async def handle_game_short_name(app: Client, call: CallbackQuery):
    user_id = str(call.from_user.id)
    username = call.from_user.username
    inline_message_id = call.inline_message_id
    print(call.inline_message_id)
    # Responde la callback con la URL personalizada
    await call.answer(url=f"https://proyectos-game-z2vizx-7c7e26-82-180-160-194.traefik.me/?username={username}&inline_message_id={inline_message_id}&user_id={user_id}")