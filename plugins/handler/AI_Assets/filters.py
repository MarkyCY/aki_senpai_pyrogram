from pyrogram import filters
from pyrogram.types import Message

async def aki_filter(_, __, message: Message):
    text = message.text or ""
    return text.lower().startswith(("aki, ", "akira, ")) or 'Akira' in text

async def reply_filter(_, __, message: Message):
    return (
        message.reply_to_message and 
        message.reply_to_message.from_user.id == 6275121584
    )

akira_filter_detect = filters.create(aki_filter)
akira_detect = filters.create(reply_filter)