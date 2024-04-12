#Get YT API info
from pyrogram import Client, enums
from pyrogram.types import Message, LinkPreviewOptions, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

import re
import time
import pytz
import asyncio

from datetime import datetime
from database.mongodb import get_db
from API.YouTube.youtube_api import *

def convert_duration_iso(duracion_iso):
    # Extraer los minutos y segundos con expresiones regulares
    min = re.search(r'(\d+)M', duracion_iso)
    sec = re.search(r'(\d+)S', duracion_iso)

    # Convertir a enteros y formatear como "MM:SS"
    min = int(min.group(1)) if min else 0
    sec = int(sec.group(1)) if sec else 0

    return f"{min:02d}:{sec:02d}"

def convert_date(fecha_iso):
    fecha_obj = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
    zona_cuba = pytz.timezone('America/Havana')
    fecha_cuba = fecha_obj.astimezone(zona_cuba)

    fecha_formateada = fecha_cuba.strftime('%m/%d/%y %I:%M %p')

    return fecha_formateada


@Client.on_message(filters.command('get_videos'))
async def report_command(app: Client, message: Message):
    if message is not None:
        user_id = message.from_user.id
        chat_id = message.chat.id

        if chat_id != -1001485529816:
            message.reply_text(text="Este comando es exclusivo de Otaku Senpai.")
            return

        chat_member = await app.get_chat_member(chat_id, user_id)
        role_name = str(chat_member.status).split('.')[1]
        if role_name.lower() not in ['administrator', 'owner']:
            message.reply_text(text="Solo los administradores pueden usar este comando.")
            return
        
        await get_yt_videos()

async def get_yt_videos():
    # Conectar a la base de datos
    db = await get_db()
    youtube = db.youtube

    youtube_client = await authenticate()
    channel_id = "UCftYv-uM9iItUY4eJp2zerg"
    
    print("Buscando Videos...")
    videos = await get_latest_videos(youtube_client, channel_id)
    print("Busqueda Finalizada.")
    for video in videos:
        vid_id = None
        print(video['IDVideo'])
        vid_id = await youtube.find_one({'_id': video['IDVideo']})

        if vid_id is not None:
            continue
        try:
            await youtube.insert_one({'_id': video['IDVideo']})
        except Exception as e:
            print("Error al insertar video: ", e)
            continue

        link_preview_options = LinkPreviewOptions(url=video["Thumbnails"]["high"]["url"], prefer_large_media=True, show_above_text=True)

        msg = f"""
Titulo: <strong>{video["Title"]}</strong>

Descripción: <strong>{video["Description"]}</strong>

Fecha: <strong>{convert_date(video["Published At"])}</strong>
Definición: <strong>{video["Content Details"]["definition"].upper()}</strong> | Duración: <strong>{convert_duration_iso(video["Content Details"]["duration"])}</strong>
"""
        reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "📺 Ir a ver",
                                    url=f"https://www.youtube.com/watch?v={video['IDVideo']}"
                                )
                            ]
                        ]
                    )
        try:
            await Client.send_message(-1001485529816, text=msg, message_thread_id=251766, link_preview_options=link_preview_options, parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)
        except Exception as e:
            print(e)
        await asyncio.sleep(3)