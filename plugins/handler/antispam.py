from pyrogram import Client, filters, utils, enums
from pyrogram.types import Message, ChatPermissions
from collections import defaultdict
from plugins.others.img_error import img_error

import time
import os

from datetime import datetime
from plugins.others.safe_file import detect_safe_search
from plugins.others.compare_img import compare_images

permissions = ChatPermissions(
can_send_messages = False,
can_send_audios = False,
can_send_documents = False,
can_send_photos = False,
can_send_videos = False,
can_send_video_notes = False,
can_send_voice_notes = False,
can_send_polls = False,
can_send_other_messages = False, #Stickers, Juegos Etc.
can_add_web_page_previews = False,
can_change_info = False,
can_invite_users = False,
can_pin_messages = False,
can_manage_topics = False,
can_send_media_messages = False,
)

# Diccionario para rastrear mensajes recientes por usuario
user_activity = defaultdict(list)

@Client.on_message(filters.group & (filters.sticker | filters.photo))
async def antispam(app: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    group_perm = [-1001485529816, -1001664356911]

    if chat_id not in group_perm:
        return

    downloaded_file = None
    downloaded_file2 = None
    ban = None
    
    current_hour = datetime.now().hour
    if 23 <= current_hour or current_hour < 8:
        time_limit = 5 # 10 segundos
        times = 3 # 1 veces
    else:
        #time_limit = 5
        #times = 2
        return

    # Limpiar actividades antiguas
    user_activity[user_id] = [activity for activity in user_activity[user_id] if current_time - activity['time'] <= time_limit]
    
    # # Verificar si es un mensaje de texto
    # if message.text:
    #     # Contar cuántas veces se ha enviado el mismo mensaje
    #     repeated_messages = sum(1 for activity in user_activity[user_id] if activity['type'] == 'text' and activity['content'] == message.text)
    #     if repeated_messages >= 3:
    #         print(f"[ANTISPAM] Usuario {message.from_user.first_name} está enviando mensajes repetidos más de 3 veces.")
    
    # Verificar si es un sticker
    if message.sticker:
        # Contar cuántas veces se ha enviado el mismo sticker
        repeated_stickers = sum(1 for activity in user_activity[user_id] if activity['type'] == 'sticker')
        if repeated_stickers >= times:
            print(f"[ANTISPAM] Usuario {message.from_user.first_name} está enviando stickers repetidos más de 3 veces.")
            downloaded_file = await app.download_media(message.sticker.thumbs[0].file_id)
            
            if await img_error(downloaded_file, message.sticker.thumbs[0].file_id):
                return
    # Verificar si es una imagen
    if message.photo:
        # Contar cuántas veces se ha enviado la misma imagen
        repeated_photos = sum(1 for activity in user_activity[user_id] if activity['type'] == 'photo')
        if repeated_photos >= times:
            print(f"[ANTISPAM] Usuario {message.from_user.first_name} está enviando la misma imagen más de 3 veces.")
            downloaded_file2 = await app.download_media(message.photo.file_id)

            if downloaded_file2 is None:
                return
    
    # Verificar si envió demasiadas actividades (mensajes/stickers/imagenes) en un corto período de tiempo
    if len(user_activity[user_id]) >= times:
        print(f"[ANTISPAM] Usuario {message.from_user.first_name} está enviando demasiados mensajes, stickers o imágenes en poco tiempo.")
        if downloaded_file:
            try:
                safe, explain = detect_safe_search(downloaded_file)
                resul_comp = await compare_images(downloaded_file)
            except Exception as e:
                print(e)
                return os.remove(downloaded_file)

            os.remove(downloaded_file)

            if resul_comp is True:
                ban = True

            if safe is False:
                ban = True

        if downloaded_file2:
            try:
                safe, explain = detect_safe_search(downloaded_file2)
                resul_comp = await compare_images(downloaded_file2)
            except Exception as e:
                print(e)
                return os.remove(downloaded_file2)

            os.remove(downloaded_file2)

            if resul_comp is True:
                ban = True

            if safe is False:
                ban = True
    
    # Añadir la actividad actual a la lista
    # if message.text:
    #     user_activity[user_id].append({'type': 'text', 'content': message.text, 'time': current_time})
    if message.sticker:
        user_activity[user_id].append({'type': 'sticker', 'mid': message.id, 'time': current_time})
    if message.photo:
        user_activity[user_id].append({'type': 'photo', 'mid': message.id, 'time': current_time})

    if ban is True:
        until_date=utils.zero_datetime()
        try:
            await app.restrict_chat_member(chat_id, message.from_user.id, permissions, until_date=until_date)
            #await app.ban_chat_member(chat_id, message.from_user.id, until_date=until_date)
        except Exception as e:
            pass
             
        await message.reply_text(f"El usuario {message.from_user.first_name} ha sido muteado por spam u otro tipo de contenido inapropiado.")
        await app.forward_messages(-1001664356911, message.chat.id, message.id, message_thread_id=82096)
        await app.send_message(
            -1001664356911,
            text=f"Contenido no deseado de <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>{explain}", 
            parse_mode=enums.ParseMode.HTML,
            message_thread_id=82096
            )
        
        mid_values = [activity['mid'] for activity in user_activity[user_id]]
        user_activity[user_id] = []

        #await app.delete_user_history(chat_id, user_id) Eliminar todos los mensajes del usuario
        await app.delete_messages(chat_id, mid_values)