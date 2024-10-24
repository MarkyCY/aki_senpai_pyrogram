from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.photo & filters.group & filters.bot & filters.user(1733263647))
def reverse_handler(app: Client, message: Message):
    
    text = message.caption.split(' ')

    if text[1] != "waifu":
        return
    
    return message.reply_text("wa")

@Client.on_message(filters.photo & filters.group & filters.bot & filters.user(1964681186))
def reverse_handler_husband(app: Client, message: Message):
    
    text = message.caption.split(' ')

    if text[1] != "husbando":
        return
    
    return message.reply_text("wa")