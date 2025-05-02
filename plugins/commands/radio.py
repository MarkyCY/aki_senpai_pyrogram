import re
from pytgcalls.types import VideoQuality, MediaStream, AudioQuality
from pytgcalls.types.raw import AudioParameters, AudioStream
from pytgcalls import exceptions
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from user_plugins.core.user_bot import pytgcalls
from plugins.others.admin_func import role as Role


@Client.on_message(filters.command("ping"))
async def ping(app: Client, message: Message):
    await message.reply_text(f"🤖 **Pong!**\n`{pytgcalls.ping} ms`")


@Client.on_message(filters.command("radiox", ["."]))
async def radio_start(app: Client, message: Message):
    chat_id = message.chat.id
    text = message.text
    user_id = message.from_user.id

    # if chat_id != -1001485529816:
    #     return await message.reply_text("Este comando es exclusivo de Otaku Senpai")

    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await message.reply_text("No tienes permisos para usar este comando.")

    OFFSET_RE = re.compile(r'^\d{1,2}:\d{2}:\d{2}$')

    parts = text.split()
    args = parts[1:]

    link = 'http://gr01.cdnstream.com:8290'
    link_audio = None
    offset = "00:00:00"

    for a in reversed(args):
        if OFFSET_RE.match(a):
            offset = a
            args.remove(a)
            break

    if len(args) >= 1:
        link = args[0]
    if len(args) >= 2:
        link_audio = args[1]

    headers = (
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0\\r\\n"
        "Accept: */*\\r\\n"
        "Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3\\r\\n"
        "Pragma: no-cache\\r\\n"
        "Cache-Control: no-cache\\r\\n"
        "Referer: https://teveo.cu/\\r\\n"
    )

    try:
        await pytgcalls.play(
            chat_id,
            MediaStream(
                link,
                audio_path=link_audio,
                audio_parameters=AudioQuality.LOW,
                video_parameters=VideoQuality.SD_360p,
                audio_flags=MediaStream.Flags.NO_LATENCY,
                video_flags=MediaStream.Flags.NO_LATENCY,
                ffmpeg_parameters=f"-re -ss {offset} -headers \"{headers}\"",
            ),
        )
    except exceptions.NoActiveGroupCall:
        return await message.reply_text("No hay una transmisión activa en el grupo")
    except Exception as e:
        print(e)
        return await message.reply_text(f"No se pudo iniciar la transmisión")

    btns = [
        [
            InlineKeyboardButton(
                "▶️", callback_data=f"radio_resume"),
            # InlineKeyboardButton(
            #     "⏮", callback_data=f"radio_prev"),
            # InlineKeyboardButton(
            #     "⏭", callback_data=f"radio_next"),
            InlineKeyboardButton(
                "⏸", callback_data=f"radio_pause"),
        ],
        [  # 📺
            InlineKeyboardButton(
                "🔇", callback_data=f"radio_mute"),
            InlineKeyboardButton(
                "🎧 Modo", callback_data=f"radio_change_video"),
            InlineKeyboardButton(
                "🔊", callback_data=f"radio_unmute"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    await message.reply_text("Se ha iniciado la transmisión", reply_markup=markup)


@Client.on_message(filters.command("stop", "."))
async def radio_stop(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # if chat_id != -1001485529816:
    #     return await message.reply_text("Este comando es exclusivo de Otaku Senpai")

    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await message.reply_text("No tienes permisos para usar este comando.")

    try:
        await pytgcalls.leave_call(chat_id)
    except exceptions.NotInCallError:
        return await message.reply_text("No hay una llamada activa")
    except exceptions.NoActiveGroupCall:
        return await message.reply_text("No hay una llamada activa en el grupo")

    await message.reply_text("Se ha detenido la transmisión")


@Client.on_message(filters.command("vol", ["."]))
async def radio_vol(app: Client, message: Message):
    chat_id = message.chat.id
    text = message.text
    user_id = message.from_user.id

    # if chat_id != -1001485529816:
    #     return await message.reply_text("Este comando es exclusivo de Otaku Senpai")

    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await message.reply_text("No tienes permisos para usar este comando.")

    if text != ".vol":
        value = text.split(" ", 1)[1]
    else:
        return await message.reply_text("Escriba un valor para el volumen")

    try:
        value = int(value)
    except Exception as e:
        return await message.reply_text("Escriba un valor válido para el volumen")

    if value > 200 or value < 0:
        return await message.reply_text("El volumen debe estar entre 0 y 200")

    await pytgcalls.change_volume_call(
        chat_id,
        value,
    )
