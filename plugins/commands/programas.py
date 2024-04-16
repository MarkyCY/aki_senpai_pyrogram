from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import enums

from API.YouTube.youtube_api import authenticate_calendar, list_events
from plugins.others.contest import *


@Client.on_message(filters.command('programas'))
async def programs_command(app: Client, message: Message):
    # Primero, autenticar y construir el servicio de Google Calendar
    service = await authenticate_calendar()
    # Luego, llamar a list_calendars() para obtener y mostrar la lista de calendarios
    text = await list_events(service)

    await message.reply_text(text=text, parse_mode=enums.ParseMode.HTML)