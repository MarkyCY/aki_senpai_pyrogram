from pytgcalls.types import VideoQuality, MediaStream, AudioQuality
from pytgcalls import exceptions
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from user_plugins.core.user_bot import pytgcalls
from plugins.others.admin_func import role as Role


@Client.on_message(filters.command("ping"))
async def ping(app: Client, message: Message):
    await message.reply_text(f"🤖 **Pong!**\n`{pytgcalls.ping} ms`")


@Client.on_message(filters.command("radio", ["."]))
async def radio_start(app: Client, message: Message):
    chat_id = message.chat.id
    text = message.text
    user_id = message.from_user.id

    # if chat_id != -1001485529816:
    #     return await message.reply_text("Este comando es exclusivo de Otaku Senpai")
    
    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    args = text.split(" ", 1)
    link_audio = None

    if len(args) == 1:
        link = 'http://gr01.cdnstream.com:8290'
    elif len(args) == 2:
        link = args[1]
    elif len(args) == 3:
        link = args[1]
        link_audio = args[2]
    
    print(args)
    print(link)
    print(link_audio)
        
    try:
        await pytgcalls.play(
            chat_id,
            MediaStream(
                link,
                audio_path=link_audio,
                audio_parameters=AudioQuality.LOW,
                video_flags=MediaStream.Flags.NO_LATENCY,
            ),
        )
    except exceptions.NoActiveGroupCall:
        return await message.reply_text("No hay una transmisión activa en el grupo")
    except Exception as e:
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
        [ # 📺
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