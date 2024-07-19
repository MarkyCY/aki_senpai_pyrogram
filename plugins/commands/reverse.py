from pyrogram import Client
from pyrogram.types import Message, ReactionTypeEmoji
from pyrogram import filters
from pyrogram import enums

import os
import json
import aiohttp

SAUCENAO = os.getenv('SAUCENAO')

async def async_post_image(url, params, image_path):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params, data={'file': open(image_path, 'rb')}) as response:
            return await response.text()

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

@Client.on_message(filters.regex('wakamole'))
async def reverse_command(app: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        await message.reply_text(text="Este comando es exclusivo de Otaku Senpai.")
        return
    
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text(text=f"Debes hacer reply a una imagen para poder describirla")
        return

    url = "https://saucenao.com/search.php"
    params = {
        "api_key": SAUCENAO,
        "output_type": "2",
        "testmode": "1"
    }

    downloaded_file = await app.download_media(message.reply_to_message, file_name="image.jpg", progress=progress)
        
    result = await async_post_image(url, params, downloaded_file)

    res = json.loads(result)

    await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👨‍💻")])

    print(f"Haciendo soliticud a SauceNAO... user: @{message.from_user.username}")

    if 'results' in res:
        characters = None
        source = None
        for result in res['results']:
            if 'characters' in result['data']:
                characters = result['data']['characters']
            if 'source' in result['data'] and source is None:
                source = result['data']['source']
            if characters is not None and source is not None:
                break
            
        if characters is not None:
            text = f"**Búsqueda: {characters}**\n**Fuente: {source}**"
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="⚡")])
            await message.reply_text(text=text, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            msg = await message.reply_text(text="No se encontraron personajes en la respuesta de la API.")
            await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="💅")])
    else:
        msg = await message.reply_text(text="No se encontraron resultados en la API.")
        await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="💅")])