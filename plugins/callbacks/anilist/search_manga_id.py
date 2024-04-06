from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, LinkPreviewOptions
from pyrogram import filters

from API.AniList.api_anilist import search_manga_id
from plugins.others.translate import async_translate
from datetime import datetime

import re

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_callback_query(filters.regex(r"^show_manga_(\d+)$"))
async def cancel(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    uid = call.from_user.id
    manga_id = call.data.split('_')[-1]
    if not call.message.reply_to_message:
        app.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
        app.delete_message(cid, mid)
        return
    if call.message.reply_to_message.from_user.id != uid:
        app.answer_callback_query(call.id, "Tu no pusiste este comando...", True)
        return
    #parts = call.data.split("_")
    await show_manga(app, cid, manga_id)
    return


def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format


async def show_manga(app, chat_id, id):
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
"""

    if image is not None:
        await app.send_message(chat_id, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True, manual=True, safe=True))
    else:
        await app.send_message(chat_id, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))
    