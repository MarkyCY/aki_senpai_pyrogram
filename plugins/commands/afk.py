from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

from plugins.others.afk import set_afk, get_afk


async def afk_filter(_, __, message):
    if message.text is not None:
        lower_text = message.text.lower()
        return lower_text.startswith(".brb") or lower_text.startswith(".afk")
afk_filter_detect = filters.create(afk_filter)


@Client.on_message(filters.command(['afk', 'brb']))
async def afk_command(app: Client, message: Message):
    await set_afk(message)

@Client.on_message(afk_filter_detect)
async def afk_controller(app: Client, message: Message):
    await set_afk(message)

@Client.on_message()
async def get_afk_handler(app: Client, message: Message):
    await get_afk(app, message)