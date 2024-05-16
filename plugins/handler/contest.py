from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from datetime import datetime, timedelta
from database.mongodb import get_db

# Diccionario para rastrear cuándo un usuario recibió el mensaje por última vez
last_message_time = {}

# Diccionario para rastrear los concursos activos
concursos_usuario = {}

async def is_player(user_id):

    db = await get_db()
    contest = db.contest
    admins = db.admins

    contests = [doc async for doc in contest.find({'status': 'active'})]
    
    # Verificar si el usuario es administrador
    Admin = [doc['user_id'] async for doc in admins.find()]
    if user_id in Admin:
        contests = [doc async for doc in contest.find()]

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


async def contest_word_filter(_, __, message):
    try:
        words = message.text.lower().split()
    except AttributeError:
        return False
    
    if 'concurso' in words:
        return True
    if 'amv' in words:
        return True
    return False
    
concurso_word_filter_detect = filters.create(contest_word_filter)


@Client.on_message(filters.group & concurso_word_filter_detect & (filters.text))
async def detect_concurso_word(app: Client, message: Message):
    user_id = message.from_user.id
    current_time = datetime.now()

    # Verifica si el usuario ya ha recibido el mensaje hoy
    if user_id in last_message_time:
        last_time = last_message_time[user_id]
        # Si no ha pasado un día completo, no envía el mensaje
        if (current_time - last_time) < timedelta(days=1):
            return

    # Guarda la hora actual como la última vez que se envió el mensaje
    last_message_time[user_id] = current_time
    # Envía el mensaje
    return await message.reply_text("Respecto al concurso de AMV: HAN LLEGADO MUCHOS VIDEOS Y POR POLITICAS DE YOUTUBE NO SE PUEDEN SUBIR TODOS A LA VEZ. ASÍ QUE SE EXTIENDE EL CONCURSO HASTA QUE TODOS PUEDAN SUBIRSE Y ESTRENARSE DE MANERA SIMULTÁNEA.")

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