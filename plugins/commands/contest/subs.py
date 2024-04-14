from pyrogram import Client
from pyrogram.types import Message, LinkPreviewOptions
from pyrogram import filters
from pyrogram import enums

from database.mongodb import get_db
from plugins.others.contest import *


@Client.on_message(filters.command('subs'))
async def subs_command(app: Client, message: Message):
    db = await get_db()
    contest = db.contest

    res = await contest.find_one({'contest_num': 2})
    text = "Suscriptores:\n"
    for i, val in enumerate(res['subscription']):
        i = i + 1

        chat_member = await app.get_chat_member(-1001485529816, val['user'])
        if chat_member.user.username is not None:
            text += f"\n{i}- <a href='https://t.me/{chat_member.user.username}'>{chat_member.user.first_name}</a>" 
        else:
            text += f"\n{i}- <a href='tg://user?id={chat_member.user.id}'>{chat_member.user.first_name}</a>" 
    await message.reply_text(text=text, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))