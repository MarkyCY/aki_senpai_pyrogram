from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

from plugins.others.translate import async_translate
from database.mongodb import get_db

@Client.on_message(filters.command('tr'))
async def traduction_command(app: Client, message: Message):
    # Obtener el texto después del comando /tr
    if not message.reply_to_message:
        await message.reply(text="Debes hacer reply a un mensaje para poder traducir")
        return
    
    text_to_translate = message.reply_to_message.text

    # Idiomas de origen y destino
    source_language = 'auto'  # Auto detectar idioma de origen
    target_language = 'es'  # español

    try:
        # Realizar la traducción
        translation = await async_translate(text_to_translate, source_language, target_language)

        # Enviar la traducción al usuario
        await message.reply_text(text=f"Traducción 'ES': {translation}")

    except Exception as e:
        # Manejar cualquier error durante la traducción
        await message.reply_text(text=f"Ocurrió un error durante la traducción: {str(e)}")