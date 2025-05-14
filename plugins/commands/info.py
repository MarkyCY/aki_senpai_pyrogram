from pyrogram import Client
from pyrogram.types import Message, ReplyParameters, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, InputMediaPhoto
from pyrogram import filters
import requests

from database.mongodb import get_db

from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SERVER_API = os.getenv('SERVER_API')

group_perm = [-1001485529816, -1001664356911]

def compare_dates(enter_timestamp):
    enter_date = datetime.fromtimestamp(enter_timestamp)  # Convertimos el timestamp a datetime
    today = datetime.now()  # Obtenemos la fecha actual

    difference = today - enter_date  # Calculamos la diferencia en días
    return difference.days  # Retornamos True si la diferencia es menor o igual a los días especificados

@Client.on_message(filters.command('info'))
async def info_command(app: Client, message: Message, user_data=None):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users
    chat_id = message.chat.id

    if message.command and len(message.command) > 1:
        elemento = message.command[1]

        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            try:
                get_user = await app.get_chat_member(message.chat.id, user_id)
            except:
                return
            user = get_user.user

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                try:
                    get_user = await app.get_chat_member(message.chat.id, username)
                except:
                    return
                user = get_user.user
    
    elif user_data is None:
        if message.reply_to_message is None:
            await message.reply_text('Por favor, responde a un mensaje')
            return
        
        else:
            user = message.reply_to_message.from_user
            
    else:
        user = message.reply_to_message.from_user

    user_action_id = user.id
    
    btns = [
        [
            InlineKeyboardButton("⚠️Advertencias", callback_data=f"warn_{user_action_id}"),
            InlineKeyboardButton("🪪Roles", callback_data=f"show_roles_{user_action_id}"),
        ],
        [
            InlineKeyboardButton("🔇Silenciar", callback_data=f"mute_{user_action_id}"),
            InlineKeyboardButton("⛔️Banear", callback_data=f"ban_{user_action_id}")
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    
    # Obtengo el rol del usuario en el chat
    try:
        chat_member = await app.get_chat_member(message.chat.id, user.id)
    except:
        return
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner'] or chat_id not in group_perm:
        markup = None
    role = role_name.capitalize()
    
    user_db = await users.find_one({"user_id": user.id})
    
    if user_db is None:
        await users.insert_one({
            "user_id": user.id
        })
        user_db = await users.find_one({"user_id": user.id})
    
    description = user_db.get('description', '-')

    msg=f"""🆔ID: {user.id}
👱Nombre: {user.first_name}
👤Nombre de usuario: @{user.username}
🪪Rol: {role}
⚠️Advertencias: {user_db.get('warnings', 0)}/3
ℹ️Descripción: {description}
"""
    
    date = user_db.get('enter_date', None)
    if date is not None:
        dt_object = datetime.fromtimestamp(date)
        msg += f"\n📅Fecha de entrada: {dt_object.strftime('%d/%m/%Y %I:%M %p')}\n"
        msg += f"⏰Días en el grupo: {compare_dates(date)} días"
    
    

    # if user_db.get("canva_json"):
    #     link_preview = LinkPreviewOptions(url=f"{SERVER_API}/canva/user_canva/{user.id}", prefer_large_media=True, show_above_text=True, manual=False, safe=False)
    #     photo = requests.get(f"{SERVER_API}/canva/user_canva/{user.id}")
    # else:
    #     link_preview = LinkPreviewOptions(is_disabled=True)

    if user_data is None:
        if user_db.get("canva_json"):
            await app.send_photo(
                message.chat.id, 
                photo=f"{SERVER_API}/canva/user_canva/{user.id}?t={datetime.now().timestamp()}",
                caption=msg, 
                reply_parameters=ReplyParameters(message_id=message.reply_to_message_id), 
                reply_markup=markup, 
                #link_preview_options=link_preview
                )
        else:
            await app.send_message(
                message.chat.id, 
                text=msg, 
                reply_parameters=ReplyParameters(message_id=message.reply_to_message_id), 
                reply_markup=markup,
                )
            
    else:
        if user_db.get("canva_json"):
            await app.edit_message_media(message.chat.id, message.id, media=InputMediaPhoto(media=f"{SERVER_API}/canva/user_canva/{user.id}?t={datetime.now().timestamp()}", caption=msg), reply_markup=markup)
        else:
            await app.edit_message_text(message.chat.id, message.id, text=msg, reply_markup=markup)