from pyrogram import Client
from pyrogram.types import CallbackQuery
from pyrogram import filters

# from database.mongodb import get_db
from plugins.others.contest import *
import jwt


# Handler específico para el juego
@Client.on_callback_query(filters.regex(r"^akira_runner$"))
def handle_game_short_name(app: Client, call: CallbackQuery):
    user_id = str(call.from_user.id)
    # Aquí generas el token (implementación equivalente a createToken)
    token = createToken(user_id)
    # Responde la callback con la URL personalizada
    call.answer(url=f"https://proyectos-game-z2vizx-7c7e26-82-180-160-194.traefik.me/?token={token}")

def createToken(user_id):
    return jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")

#detector de los callbackquery
@Client.on_callback_query()
def handle_all_callbacks(app: Client, call: CallbackQuery):
    print(f"Callback data: {call.data} from user {call.from_user.id}")