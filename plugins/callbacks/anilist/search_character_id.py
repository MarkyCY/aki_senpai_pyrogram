from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, LinkPreviewOptions
from pyrogram import filters

from API.AniList.api_anilist import searchCharacterId
from plugins.others.translate import async_translate
from datetime import datetime
from html2text import html2text

import re

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_callback_query(filters.regex(r"^show_character_(\d+)$"))
async def cancel(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    uid = call.from_user.id
    anime_id = call.data.split('_')[-1]
    if not call.message.reply_to_message:
        app.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
        app.delete_message(cid, mid)
        return
    if call.message.reply_to_message.from_user.id != uid:
        app.answer_callback_query(call.id, "Tu no pusiste este comando...", True)
        return
    #parts = call.data.split("_")
    await show_character(app, cid, anime_id)
    return

def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format


async def show_character(app, chat_id, id):
    character = await searchCharacterId(id)

    full_name = character['data']['Character']['name']['full']
    native_name = character['data']['Character']['name']['native']
    image = character['data']['Character']['image']['large']
    description_notr = character['data']['Character']['description'][:500]
    description_plain_text = html2text(description_notr)
    description_no_tag = re.sub('<[^<]*', '', description_plain_text)
    description = await async_translate(description_no_tag, source_language, target_language)
    gender = character['data']['Character']['gender']
    date_of_birth = character['data']['Character']['dateOfBirth']
    age = character['data']['Character']['age']
    blood_type = character['data']['Character']['bloodType']
    is_favorite = character['data']['Character']['isFavourite']
    site_url = character['data']['Character']['siteUrl']
     
    msg = f"""
<strong>{full_name}</strong> ({native_name})
<strong>Género:</strong> {gender}
<strong>Fecha de Nacimiento:</strong> {date_of_birth['year']}-{date_of_birth['month']}-{date_of_birth['day']}
<strong>Edad:</strong> {age}
<strong>Tipo de Sangre:</strong> {blood_type}
<strong>Favorito:</strong> {'Sí' if is_favorite else 'No'}
<strong>Enlace:</strong> {site_url}

<strong>Descripción:</strong>
{description}
"""
    if image is not None:
        await app.send_message(chat_id, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True, manual=True, safe=True))
    else:
        await app.send_message(chat_id, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))