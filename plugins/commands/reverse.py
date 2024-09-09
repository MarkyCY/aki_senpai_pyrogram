from pyrogram import Client
from pyrogram.types import Message, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from pyrogram import filters
from pyrogram import enums

from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import os
import json
import aiohttp

SAUCENAO = os.getenv('SAUCENAO')
SAUCENAO_2 = os.getenv('SAUCENAO_2')


async def async_post_image(url, params, image_path):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params, data={'file': open(image_path, 'rb')}) as response:
            return await response.text()


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


@Client.on_message(filters.regex(r'(?i)wa'))
async def reverse_command(app: Client, message: Message):
    chat_id = message.chat.id

    if not message.reply_to_message:
        return

    if (message.reply_to_message.from_user.id != 1733263647 and message.reply_to_message.from_user.id != 1964681186):
        return
    
    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        await message.reply_text(text="Este comando es exclusivo de Otaku Senpai.")
        return

    if not message.reply_to_message.photo:
        await message.reply_text(text=f"Debes hacer reply a una imagen para poder describirla")
        return
    
    msg = await app.send_photo(chat_id, message.reply_to_message.photo.file_id)

    url = "https://saucenao.com/search.php"
    current_hour = datetime.now().hour
    if 2 <= current_hour < 20:
        params = {
            "api_key": SAUCENAO,
            "output_type": "2",
            "testmode": "0"
        }
    else:
        params = {
            "api_key": SAUCENAO_2,
            "output_type": "2",
            "testmode": "0"
        }

    downloaded_file = await app.download_media(message.reply_to_message, file_name="image.jpg", progress=progress)

    result = await async_post_image(url, params, downloaded_file)

    res = json.loads(result)

    #print(res)

    try:	
        await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👨‍💻")])
    except:
        pass

    print(
        f"Haciendo soliticud a SauceNAO... user: @{message.from_user.username}")

    try:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Google Lens', url=f'https://lens.google.com/uploadbyurl?url=https://saucenao.com{res["header"]["query_image_display"]}')]])
    except:
        pass
    
    if 'results' in res:
        characters = None
        source = None
        title = None

        text = "Búsqueda:\n\n"

        for i, result in enumerate(res['results']):
            if i >= 3:
                break

            if 'characters' in result['data']:
                characters = result['data']['characters']
            if 'title' in result['data']:
                title = result['data']['title']
            if 'source' in result['data'] and source is None:
                source = result['data']['source']

            text += f"<strong>Título:</strong> {title}\n<strong>Personaje:</strong> {characters}\n<strong>Fuente:</strong> {source}\n\n"

            if characters is not None and source is not None and title is not None:
                break

        if text != "Búsqueda:\n\n":
            try:
                await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="⚡")])
            except:
                pass
            add_media = InputMediaPhoto(message.reply_to_message.photo.file_id, text, parse_mode=enums.ParseMode.HTML)
            await app.edit_message_media(chat_id, msg.id, add_media, reply_markup=reply_markup)
            #await message.reply_text(text=text, parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)
        else:
            add_media = InputMediaPhoto(message.reply_to_message.photo.file_id, "No se encontraron personajes en la respuesta de la API.")
            await app.edit_message_media(chat_id, msg.id, add_media)
            #msg = await message.reply_text(text="No se encontraron personajes en la respuesta de la API.")
            #await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="💅")])
    else:
        add_media = InputMediaPhoto(message.reply_to_message.photo.file_id, "No se encontraron resultados en la API.")
        await app.edit_message_media(chat_id, msg.id, add_media)
        #msg = await message.reply_text(text="No se encontraron resultados en la API.")
        #await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="💅")])