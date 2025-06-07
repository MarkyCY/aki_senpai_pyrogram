from pyrogram import Client, filters, utils, enums
from pyrogram.types import Message, ChatPermissions, LinkPreviewOptions

from database.mongodb import get_db
from datetime import datetime
# from plugins.others.img_error import img_error

# from plugins.others.safe_file import detect_safe_search
# from plugins.others.compare_img import compare_images

import os, re

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

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

def compare_dates(enter_timestamp, days=10):
    enter_date = datetime.fromtimestamp(enter_timestamp)  # Convertimos el timestamp a datetime
    today = datetime.now()  # Obtenemos la fecha actual

    difference = today - enter_date  # Calculamos la diferencia en días

    return difference.days <= days  # Retornamos True si la diferencia es menor o igual a los días especificados

async def is_new(user_id):
    db = await get_db()
    users = db.users

    user = await users.find_one({"user_id": user_id})

    if user is None:
        return True

    if user and "enter_date" in user:
        return compare_dates(user["enter_date"])
    else:
        return False


async def new_member(_, __, message):
    isplayer = await is_new(message.from_user.id)
    return isplayer != False
    
new_member_detect = filters.create(new_member)

# @Client.on_message(filters.group)
@Client.on_message(filters.group & new_member_detect & (filters.text | filters.photo | filters.sticker))
async def detect_new_user(app: Client, message: Message):
    chat_id = message.chat.id

    group_perm = [-1001485529816, -1001664356911]

    if chat_id not in group_perm:
        return

    entities = message.entities or []
    text = message.text or message.caption or ""
    mute = None

    # Ordenar entidades en orden inverso para evitar conflictos de offsets
    sorted_entities = sorted(
        entities,
        key=lambda x: (-x.offset, -x.length),
        reverse=False
    )

    for entity in sorted_entities:
        start = entity.offset
        end = start + entity.length
        entity_type = re.sub(r'MessageEntityType\.', '', str(entity.type)).lower()
        original = text[start:end]
        if entity_type == "url":
            url = entity.url
            mute = True
            reason = f"Link: [{original}]({url})"

            if original.startswith('https://t.me/OtakuSenpai2020') or (url and url.startswith('https://t.me/OtakuSenpai2020')):
                mute = False

            explain = f"Los nuevos usuarios no tienen permiso para enviar enlaces en el grupo hasta que pasen 5 días desde su entrada al grupo. \n\nInfo: https://t.me/OtakuSenpai2020/251766/2172877"
        elif entity_type == "mention":
            mute = True
            reason = f"Mention: {original}"
            explain = f"Los nuevos usuarios no tienen permiso para hacer menciones en el grupo hasta que pasen 5 días desde su entrada al grupo. \n\nInfo: https://t.me/OtakuSenpai2020/251766/2172877"
            try:
                get_user = await app.get_chat_member('OtakuSenpai2020', original)
                if get_user:
                    mute = False
            except:
                pass

    reply = message.reply_markup
    if reply and hasattr(reply, 'inline_keyboard'):
        for row in reply.inline_keyboard:
            for button in row:
                if hasattr(button, 'url'):
                    mute = True
                    reason = f"Link en botón: {button.url}"
                    explain = f"Los nuevos usuarios no tienen permiso para enviar enlaces en el grupo hasta que pasen 5 días desde su entrada al grupo. \n\nInfo: https://t.me/OtakuSenpai2020/251766/2172877"
                    if button.url.startswith('https://t.me/OtakuSenpai2020'):
                        mute = False

    # if message.sticker:
    #     downloaded_file = await app.download_media(message.sticker.thumbs[0].file_id)
    #     if img_error(downloaded_file, message.sticker.thumbs[0].file_id):
    #         os.remove(downloaded_file)
    #         print("Imagen en lista negra")
    #         return
    # if message.photo:
    #     downloaded_file = await app.download_media(message.photo.file_id)

    # try:
    #     safe, explain = detect_safe_search(downloaded_file)
    #     resul_comp = await compare_images(downloaded_file)
    # except Exception as e:
    #     os.remove(downloaded_file)
    #     return

    # os.remove(downloaded_file)

    # if resul_comp is True:
    #     mute = True

    # if safe is False:
    #     mute = True

    if mute is not True:
        return
    
    db = await get_db()
    users = db.users
     
    user = await users.find_one({"user_id": message.from_user.id})

    until_date=utils.zero_datetime()

    if user is None:
        try:
            await app.ban_chat_member(chat_id, message.from_user.id, until_date=until_date)
        except Exception as e:
            pass
        notify = f"El usuario <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ha sido baneado por no ser completamente seguro de su contenido."
        action = "Baneado"
    else:
        try:
            await app.restrict_chat_member(chat_id, message.from_user.id, permissions, until_date=until_date)
        except Exception as e:
            pass
        notify = f"El usuario <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ha sido muteado por no ser completamente seguro de su contenido."
        action = "Muteado"
             
    await message.reply_text(f"{notify} \n\n{explain}", parse_mode=enums.ParseMode.HTML)
    await app.forward_messages(-1001664356911, message.chat.id, message.id, message_thread_id=82096)
    await app.send_message(
        -1001664356911,
        #text=f"Contenido no deseado de <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>{explain}", 
        text=f"Contenido no deseado de <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n\nRazón: \n{reason}\n\nAcción: {action}",
        parse_mode=enums.ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        message_thread_id=82096
        )
     
    await app.delete_messages(chat_id, message.id)