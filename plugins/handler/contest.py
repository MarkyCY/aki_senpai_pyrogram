from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, enums

from database.mongodb import get_db

concursos_usuario = {}

async def is_player(user_id):

    db = await get_db()
    contest = db.contest

    contests = [doc async for doc in contest.find({'status': 'active'})]
    for concurso in contests:
        for suscriptor in concurso['subscription']:
            if suscriptor['user'] == user_id:
                # Si el usuario no está en el diccionario, agregarlo
                if user_id not in concursos_usuario:
                    concursos_usuario[user_id] = []
                # Agregar el ID del concurso a la lista del usuario
                data = (concurso['type'], concurso['_id'], concurso['title'])
                concursos_usuario[user_id].append(data)
    
    if concursos_usuario == {}:
        return None
    
    return concursos_usuario


async def contest_filter(_, __, message):
    isplayer = await is_player(message.from_user.id)
    return isplayer != None
    
contest_filter_detect = filters.create(contest_filter)


@Client.on_message(filters.private & contest_filter_detect & (filters.text | filters.photo | filters.video))
async def detect_contest(app: Client, message: Message):
    user_id = message.from_user.id

    concursos = concursos_usuario[user_id]
    concursos_usuario.pop(user_id)

    if message.text:
        type = 'text'
        words = message.text.split()
        if len(words) < 50:
            return
        
    if message.photo:
        type = 'photo'
        
    if message.video:
        type = 'video'

    buttons = [[]]
    for doc in concursos:
        if doc[0] == type:
            buttons[0].append(InlineKeyboardButton(f"{doc[2]}", callback_data=f"contest_up_{doc[1]}_{message.id}"))

    if buttons == [[]]:
        return
    
    buttons.append([InlineKeyboardButton(f"❌Cancelar", callback_data=f"up_contest_cancel")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.reply_text("Veo que estás participando en un concurso. Selecciona para que concurso es esta obra y si no es para ninguno solo cancela...", reply_markup=markup)