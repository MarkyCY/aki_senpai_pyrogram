    
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import enums

from plugins.commands.mh.list_free import get_mh_rooms


@Client.on_message(filters.command('show_room'))
async def add_anime_command(app: Client, message: Message):

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(text="Especifica que servidor deseas ver.\n\nUsage: `/show_room` <servidor> [`P3`|`FU`|`F1`]")
        return
    
    server_code = args[1].upper()
    if server_code not in ['P3', 'FU', 'F1']:
        await message.reply_text(text="Código de servidor inválido. Usa uno de: `P3`|`FU`|`F1`")
        return
    
    content = get_mh_rooms( server_code=server_code, show_all=True )
    
    await message.reply_text(text=content)