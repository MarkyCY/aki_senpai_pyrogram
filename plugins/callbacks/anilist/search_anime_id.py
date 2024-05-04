from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, LinkPreviewOptions
from pyrogram import filters

from API.AniList.api_anilist import search_anime_id
from plugins.others.translate import async_translate
from datetime import datetime

import re

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_callback_query(filters.regex(r"^show_anime_(\d+)_\d+$"))
async def search_anime(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    uid = call.from_user.id
    partes = call.data.split('_')
    anime_id = int(partes[2])
    ruid = int(partes[3])

    if ruid != uid:
        await app.answer_callback_query(call.id, "Tu no pusiste este comando...", True)
        return
    #parts = call.data.split("_")
    await show_anime(app, mid, cid, anime_id)
    return


def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format


async def show_anime(app, mid, chat_id, id):
    anime = await search_anime_id(id)
    name = anime['data']['Media']['title']['english']
    if (name is None):
        name = anime['data']['Media']['title']['romaji']
     
    duration = anime['data']['Media']['duration']
    score = anime['data']['Media']['averageScore']
    episodes = anime['data']['Media']['episodes']
    status = anime['data']['Media']['status']
    isAdult = anime['data']['Media']['isAdult']
    nextAiringEpisode = anime['data']['Media']['nextAiringEpisode']
    genres = anime['data']['Media']['genres']
     
    match isAdult:
        case True:
            adult = "Si"
        case False:
            adult = "No"
        case _:
            adult = "Desconocido"
     
    html_regex = re.compile(r'<[^>]+>')
    tr_description = re.sub(html_regex, '', anime['data']['Media']['description'])[:500]
    description = await async_translate(tr_description, source_language, target_language)

    if anime['data']['Media']['bannerImage'] is not None:
        image = anime['data']['Media']['bannerImage']
    else:
        image = anime['data']['Media']['coverImage']['large']
    
    print(image)
    msg = f"""
<strong>{name}</strong> 
<code>{', '.join(genres)}</code>
<strong>Duración de cada Cap:</strong> {duration} min
<strong>Episodios:</strong> {episodes}

<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Puntuación:</strong> {score}/100
<strong>Para Adultos?:</strong> {adult}

<strong>Imagen:</strong> {image}
"""
    if nextAiringEpisode:
        msg += f"\n<strong>Próxima emisión:</strong>\nEpisodio <strong>{nextAiringEpisode['episode']}</strong> Emisión: <code>{timestamp_conv(nextAiringEpisode['airingAt'])}</code>\n"
     
    if image is not None:
        await app.edit_message_text(chat_id, mid, text=msg, link_preview_options=LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True), parse_mode=enums.ParseMode.HTML)
    else:
        await app.edit_message_text(chat_id, mid, text=msg, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))
    