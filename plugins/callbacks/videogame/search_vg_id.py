from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, LinkPreviewOptions
from pyrogram import filters

from plugins.others.translate import async_translate
from datetime import datetime

import re
import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

VG_API = os.getenv('VIDEOG_DB')

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_callback_query(filters.regex(r"^videogame_(\d+)_\d+$"))
async def cancel(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    uid = call.from_user.id
    partes = call.data.split('_')
    print(partes)
    vg_id = int(partes[1])
    ruid = int(partes[2])

    if ruid != uid:
        await app.answer_callback_query(call.id, "Tu no pusiste este comando...", True)
        return
    #parts = call.data.split("_")
    await show_vg(app, mid, cid, vg_id)
    return


def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format


async def show_vg(app, mid, chat_id, id):
    print("Buscando Game")
    
    params = {
        "key": VG_API
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.rawg.io/api/games/{id}", params=params) as response:
            if response.status == 200:
                res = await response.text()
            else:
                raise aiohttp.HttpProcessingError(
                    message=f"Error al realizar la solicitud: {response.status}",
                    code=response.status
                )
            
    res_json = json.loads(res)

    html_regex = re.compile(r'<[^>]+>')
    tr_description = re.sub(html_regex, '', res_json['description_raw'])[:500]
    description = await async_translate(tr_description, source_language, target_language)

    platforms = []
    for data in res_json['platforms']:
        platform = f"<code>{data['platform']['name']}</code>"
        platforms.append(platform)

    developers = []
    for data in res_json['developers']:
        developer = f"<code>{data['name']}</code>"
        developers.append(developer)

    tags = []
    for data in res_json['tags'][:min(len(res_json['tags']), 8)]:
        tag = f"<code>{data['name']}</code>"
        tags.append(tag)

    msg = f"""
<strong>{res_json['name']}</strong> 
{', '.join(platforms)}

<strong>Desarrolladores:</strong> {', '.join(developers)}

<strong>Descripción:</strong>
{description}

<strong>Lanzado:</strong> {res_json['released']}
<strong>Etiquetas:</strong> {', '.join(tags)}

<strong>Imagen:</strong> {res_json['background_image']}
"""
    image = res_json['background_image']
    #if res_json['background_image'] is not None:
    #    link_preview_options = LinkPreviewOptions(url=res_json['background_image'], prefer_large_media=True, show_above_text=True)
    #else:
    #    link_preview_options = LinkPreviewOptions(is_disabled=True)

    #bot.edit_message_text(msg, chat_id, message_id, parse_mode="html", link_preview_options=link_preview_options)
    await app.edit_message_text(chat_id, mid, text=msg, link_preview_options=LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True), parse_mode=enums.ParseMode.HTML)