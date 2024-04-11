from pyrogram import Client, filters, types
from pyrogram.types import Message, ReplyParameters

from API.AniList.api_anilist import search_anime


source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

@Client.on_message(filters.command('anime'))
async def anime_command(app: Client, message: Message):
    if len(message.text.split(' ')) <= 1:
        await message.reply_text(text=f"Debes poner el nombre del anime luego de /anime")
        return
    
    print('Haciendo Solicitud a la api')
    referral_all = message.text.split(" ")
    anime_name = " ".join(referral_all[1:])
    anime = await search_anime(anime_name)
    
    btns = []
    for res in anime['data']['Page']['media'][:min(len(anime['data']['Page']['media']), 8)]:
        if res['title']['english'] is not None:
            title = res['title']['english']
        else:
            title = res['title']['romaji']

        btn = [types.InlineKeyboardButton(str(title), callback_data=f"show_anime_{res['id']}_{message.from_user.id}")]
        btns.append(btn)
    markup = types.InlineKeyboardMarkup(inline_keyboard=btns)

    await app.send_message(message.chat.id, text='Estos son los resultados de la busqueda de animes:', reply_parameters=ReplyParameters(message_id=message.id), reply_markup=markup)