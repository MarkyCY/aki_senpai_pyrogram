from pyrogram import Client, filters
from pyrogram.types import Message

import asyncio


@Client.on_message(filters.photo & filters.group & filters.bot & (filters.user(1733263647) | filters.user(1964681186)))
async def reverse_handler(app: Client, message: Message):
    
    text = message.caption.split(' ')

    if text[1] != "waifu" and text[1] != "husbando":
        return
    
    await message.reply_text("wa")