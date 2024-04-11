from pyrogram import Client, filters, types
from pyrogram.types import Message, ReplyParameters

from API.AniList.api_anilist import searchCharacter


source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_message(filters.command('character'))
async def character_command(app: Client, message: Message):
    if len(message.text.split(' ')) <= 1:
        await message.reply_text(text=f"Debes poner el nombre del anime luego de /anime")
        return
    
    print('Haciendo Solicitud a la api')
    referral_all = message.text.split(" ")
    character_name = " ".join(referral_all[1:])
    character = await searchCharacter(character_name)
    
    btns = []
    for res in character['data']['Page']['characters'][:min(len(character['data']['Page']['characters']), 8)]:
        if res['name']['full'] is not None:
            name = res['name']['full']
        else:
            name = res['name']['native']

        btn = [types.InlineKeyboardButton(str(name), callback_data=f"show_character_{res['id']}_{message.from_user.id}")]
        btns.append(btn)
    markup = types.InlineKeyboardMarkup(inline_keyboard=btns)

    await app.send_message(message.chat.id, text='Estos son los resultados de la busqueda de personajes:', reply_parameters=ReplyParameters(message_id=message.id), reply_markup=markup)