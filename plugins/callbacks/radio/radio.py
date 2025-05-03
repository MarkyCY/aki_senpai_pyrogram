from pyrogram import Client
from pyrogram.types import CallbackQuery
from pyrogram import filters

from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality

from user_plugins.core.user_bot import pytgcalls
from plugins.others.admin_func import role as Role

# toggle_play_pause
# radio_prev
# radio_next

@pytgcalls.on_update(fl.stream_end)
async def stream_end(client, update):

    chat_id = update.chat_id

    await pytgcalls.play(
            chat_id,
            MediaStream(
                'http://gr01.cdnstream.com:8290',
                audio_parameters=AudioQuality.LOW,
                audio_flags=MediaStream.Flags.NO_LATENCY,
            ),
        )

@Client.on_callback_query(filters.regex(r"^radio_resume$"))
async def radio_resume(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await app.answer_callback_query(call.id, f"No tienes permisos.")
    
    try:    
        await pytgcalls.resume_stream(chat_id)
    except Exception as e:
        return await app.answer_callback_query(call.id, f"No se pudo reanudar el stream.")
    
    return await app.answer_callback_query(call.id, "Se ha reanudado el stream")


@Client.on_callback_query(filters.regex(r"^radio_pause$"))
async def radio_pause(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await app.answer_callback_query(call.id, f"No tienes permisos.")
    
    try:
        await pytgcalls.pause_stream(chat_id)
    except Exception as e:
        return await app.answer_callback_query(call.id, f"No se pudo pausar el stream.")
    
    return await app.answer_callback_query(call.id, "Se ha pausado el stream")


@Client.on_callback_query(filters.regex(r"^radio_mute$"))
async def radio_mute(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await app.answer_callback_query(call.id, f"No tienes permisos.")
    
    try:
        await pytgcalls.mute_stream(chat_id)
    except Exception as e:
        
        return await app.answer_callback_query(call.id, f"No se pudo silenciar el stream: {e}")
    
    await app.answer_callback_query(call.id, f"Se ha silenciado el stream")

@Client.on_callback_query(filters.regex(r"^radio_unmute$"))
async def radio_unmute(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    _, admin = await Role(app, chat_id, user_id)
    if admin is None and user_id != 642502067:
        return await app.answer_callback_query(call.id, f"No tienes permisos.")
    
    try:
        await pytgcalls.unmute_stream(chat_id)
    except Exception as e:
        return await app.answer_callback_query(call.id, f"No se pudo desilenciar el stream: {e}")
    
    await app.answer_callback_query(call.id, "Se ha desilenciado el stream")