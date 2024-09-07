from pyrogram import Client, filters
from pyrogram.types import Message

import asyncio
# @Client.on_message(filters.photo & filters.group & filters.bot & (filters.user(1733263647) | filters.user(1964681186) | filters.user(873919300)))
# async def reverse_handler(app: Client, message: Message):

#@Client.on_message(filters.group & (filters.user(1733263647) | filters.user(1964681186) | filters.user(873919300)))
@Client.on_message(filters.photo & filters.group & filters.bot & (filters.user(1733263647) | filters.user(1964681186)))
async def reverse_handler(app: Client, message: Message):
    
    text = message.caption.split(' ')

    if text[1] != "waifu" and text[1] != "husbando":
        return
    
    msg = await message.reply_text("wa")
    await asyncio.sleep(1)
    await msg.delete()