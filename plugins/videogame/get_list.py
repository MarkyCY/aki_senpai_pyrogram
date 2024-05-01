from pyrogram import Client, filters, types
from pyrogram.types import Message, ReplyParameters, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

import aiohttp
import json
import os

load_dotenv()

VG_API = os.getenv('VIDEOG_DB')

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_message(filters.command('game'))
async def game_command(app: Client, message: Message):
    if len(message.text.split(' ')) <= 1:
        await message.reply_text(text=f"Debes poner el nombre del juego luego de /game")
        return
    
    get_name = message.text.split(" ")
    name = " ".join(get_name[1:])
    
    print("Buscando Games")
    params = {
        "key": VG_API,
        "search": name
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.rawg.io/api/games", params=params) as response:
            if response.status == 200:
                res = await response.text()
            else:
                raise aiohttp.HttpProcessingError(
                    message=f"Error al realizar la solicitud: {response.status}",
                    code=response.status
                )
    #print(res.text)
    res_json = json.loads(res)

    btns = []

    for res in res_json['results'][:min(len(res_json['results']), 8)]:
        btn = [InlineKeyboardButton(res['name'], callback_data=f"videogame_{res['id']}_{message.from_user.id}")]
        btns.append(btn)
    markup = types.InlineKeyboardMarkup(inline_keyboard=btns)

    await app.send_message(message.chat.id, text='Estos son los resultados de la busqueda de videojuegos:', reply_parameters=ReplyParameters(message_id=message.id), reply_markup=markup)