from pyrogram import Client, filters, utils, enums
from pyrogram.types import Message, ChatPermissions

from plugins.others.safe_file import detect_safe_search
from plugins.others.compare_img import compare_images

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

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

@Client.on_message(filters.command("rev"))
async def revise_command(app: Client, message: Message):
    chat_id = message.chat.id
    group_perm = [-1001485529816, -1001664356911]

    ban = False

    if not message.reply_to_message:
        return
    
    if message.chat.id not in group_perm:
        await message.reply_text(text="Este comando es exclusivo de Otaku Senpai.")
        return

    if not message.reply_to_message.photo and not message.reply_to_message.sticker:
        await message.reply_text(text=f"Debes hacer reply a una imagen o sticker para poder revisarla")
        return
    
    if message.reply_to_message.sticker:
        downloaded_file = await app.download_media(message.reply_to_message.sticker.thumbs[0].file_id, file_name="revise.jpg")
    elif message.reply_to_message.photo:
        downloaded_file = await app.download_media(message.reply_to_message.photo.file_id, file_name="revise.jpg")
    else:
        return await message.reply_text(text=f"Esto solo funciona con imagenes o stickers.")

    safe, explain = detect_safe_search(downloaded_file)

    resul_comp = await compare_images(downloaded_file)

    if resul_comp is True:
        ban = True

    if safe is False:
        ban = True

    if ban is True:

        until_date=utils.zero_datetime()
        try:
            await app.restrict_chat_member(chat_id, message.reply_to_message.from_user.id, permissions, until_date=until_date)
        except Exception as e:
            pass

        await message.reply_text(f"El usuario {message.reply_to_message.from_user.first_name} ha sido muteado por no ser completamente seguro de su contenido.")
        await app.forward_messages(-1001664356911, message.chat.id, message.reply_to_message.id, message_thread_id=82096)
        await app.send_message(
            -1001664356911,
            text=f"Contenido no deseado de <a href='tg://user?id={message.reply_to_message.from_user.id}'>{message.reply_to_message.from_user.first_name}</a>{explain}", 
            parse_mode=enums.ParseMode.HTML,
            message_thread_id=82096
            )

        await app.delete_messages(chat_id, message.reply_to_message.id)

    else:
        await message.reply_text(f"Esta imagen está permitida\n {explain}")
    