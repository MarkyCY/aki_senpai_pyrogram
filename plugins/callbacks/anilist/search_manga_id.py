from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, LinkPreviewOptions
from pyrogram import filters

from API.AniList.api_anilist import search_manga_id
from plugins.others.translate import async_translate
from datetime import datetime

import re

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_callback_query(filters.regex(r"^show_manga_(\d+)_\d+$"))
async def search_manga(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    uid = call.from_user.id
    partes = call.data.split('_')
    manga_id = int(partes[2])
    ruid = int(partes[3])

    if ruid != uid:
        await app.answer_callback_query(call.id, "Tu no pusiste este comando...", True)
        return
    #parts = call.data.split("_")
    await show_manga(app, mid, cid, manga_id)
    return


def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format


async def show_manga(app, mid, chat_id, id):
    manga = await search_manga_id(id)
    name = manga['data']['Media']['title']['english']
    if (name is None):
        name = manga['data']['Media']['title']['romaji']
     
    status = manga['data']['Media']['status']
    isAdult = manga['data']['Media']['isAdult']
    genres = manga['data']['Media']['genres']
    match isAdult:
        case True:
            adult = "Si"
        case False:
            adult = "No"
        case _:
            adult = "Desconocido"
         
    html_regex = re.compile(r'<[^>]+>')
    if manga['data']['Media']['description'] is not None:
        tr_description = re.sub(html_regex, '', manga['data']['Media']['description'])
    else:
        tr_description = "No description."
    description = await async_translate(tr_description, source_language, target_language)

    if manga['data']['Media']['bannerImage'] is not None:
        image = manga['data']['Media']['bannerImage']
    else:
        image = manga['data']['Media']['coverImage']['large']
         
    msg = f"""
<strong>{name}</strong> 
<code>{', '.join(genres)}</code>
<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}

<strong>Imagen:</strong> {image}
"""

    if image is not None:
        await app.edit_message_text(chat_id, mid, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True, manual=True, safe=True))
    else:
        await app.edit_message_text(chat_id, mid, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))
    