from pyrogram import Client, filters, utils, enums
from pyrogram.types import Message, ChatPermissions

from plugins.others.safe_file import process_image
# from plugins.others.compare_img import compare_images
from dotenv import load_dotenv

load_dotenv()

import os
import base64
import io

groq_api = os.getenv('GROQ_API')

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


def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

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
        try:
            downloaded_file = await app.download_media(message.reply_to_message.sticker.thumbs[0].file_id)
        except Exception as e:
            os.remove(downloaded_file)
    elif message.reply_to_message.photo:
        try:
            downloaded_file = await app.download_media(message.reply_to_message.photo.file_id)
        except Exception as e:
            os.remove(downloaded_file)
    else:
        os.remove(downloaded_file)
        return await message.reply_text(text=f"Esto solo funciona con imagenes o stickers.")
    

    # safe, explain = detect_safe_search(downloaded_file)

    # resul_comp = await compare_images(downloaded_file)
    prompt = "Describe all elements in this image in detail, including text, objects, and context. Say if the content is apropiated for kids."
    
    description, safety = process_image(downloaded_file, None, prompt, groq_api)
    print(description, safety)

    os.remove(downloaded_file)

    if safety == "unsafe":
        ban = True

    # if safe is False:
    #     ban = True

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
            text=f"Contenido no deseado de <a href='tg://user?id={message.reply_to_message.from_user.id}'>{message.reply_to_message.from_user.first_name}</a>\n<blockquote>{description}</blockquote>", 
            parse_mode=enums.ParseMode.MARKDOWN,
            message_thread_id=82096
            )

        await app.delete_messages(chat_id, message.reply_to_message.id)

    else:
        await message.reply_text(f"Esta imagen está permitida\n <blockquote>{description}</blockquote>", parse_mode=enums.ParseMode.MARKDOWN,)
    