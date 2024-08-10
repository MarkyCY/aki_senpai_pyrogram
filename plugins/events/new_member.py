from pyrogram import Client, filters, utils, enums
from pyrogram.types import Message, ChatPermissions

from database.mongodb import get_db
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

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

def compare_dates(enter_timestamp, days=30):
    enter_date = datetime.fromtimestamp(enter_timestamp)  # Convertimos el timestamp a datetime
    today = datetime.now()  # Obtenemos la fecha actual

    difference = today - enter_date  # Calculamos la diferencia en días

    return difference.days <= days  # Retornamos True si la diferencia es menor o igual a los días especificados

async def is_new(user_id):
    db = await get_db()
    users = db.users

    user = await users.find_one({"user_id": user_id})

    if user and "enter_date" in user:
        return compare_dates(user["enter_date"])
    else:
        return False


async def new_member(_, __, message):
    isplayer = await is_new(message.from_user.id)
    return isplayer != False
    
new_member_detect = filters.create(new_member)

@Client.on_message(filters.group & new_member_detect & (filters.photo | filters.sticker))
async def detect_new_user(app: Client, message: Message):
    chat_id = message.chat.id

    group_perm = [-1001485529816, -1001664356911]

    if message.chat.id not in group_perm:
        return
    
    ban = None

    if message.sticker:
        downloaded_file = await app.download_media(message.sticker.thumbs[0].file_id, file_name="revise.jpg")
    if message.photo:
        downloaded_file = await app.download_media(message.photo.file_id, file_name="revise.jpg")

    safe, explain = detect_safe_search(downloaded_file)

    resul_comp = await compare_images(downloaded_file)

    if resul_comp is True:
        ban = True

    if safe is False:
        ban = True

    if ban is True:

        until_date=utils.zero_datetime()
        try:
            await app.restrict_chat_member(chat_id, message.from_user.id, permissions, until_date=until_date)
        except Exception as e:
            pass

        await message.reply_text(f"El usuario {message.from_user.first_name} ha sido muteado por no ser completamente seguro de su contenido.")
        await app.forward_messages(-1001664356911, message.chat.id, message.id, message_thread_id=82096)
        await app.send_message(
            -1001664356911,
            text=f"Contenido no deseado de <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>", 
            parse_mode=enums.ParseMode.HTML,
            message_thread_id=82096
            )

        await app.delete_messages(chat_id, message.id)

    else:
        await message.reply_text(f"Esta imagen está permitida\n {explain}")