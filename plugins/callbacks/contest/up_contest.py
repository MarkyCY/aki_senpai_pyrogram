from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, enums

from database.mongodb import get_db
from plugins.others.contest import *
from bson import ObjectId

from datetime import datetime

def diference_min(timestamp_a, timestamp_b):
    dt_a = datetime.fromtimestamp(timestamp_a)
    dt_b = datetime.fromtimestamp(timestamp_b)
    
    diference = (dt_b - dt_a).total_seconds() / 60
        
    return diference

#Otaku -1001485529816 - 251988
#Marrano -1001664356911 - 53628
principal_chat_id = -1001485529816
principal_thread_id = 251988

@Client.on_callback_query(filters.regex(r"^contest_up_[a-f\d]{24}_\d+$"))
async def up_contest(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    message_id = int(parts[3])

    db = await get_db()
    contest = db.contest

    contest_sel = await contest.find_one({'_id': contest_id})

    msg = await app.get_messages(chat_id=chat_id, message_ids=message_id)

    text = f"Esta obra es envíada por <a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a> participando en el concurso: {contest_sel['title']}"
    match contest_sel['type']:
        case 'text':
            msg_text = msg.text
            msg_text += "\n\n", text
            try:
                sent_message = await app.send_message(principal_chat_id, msg.text, message_thread_id=principal_thread_id, reply_markup=None)
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                return
        case 'photo':
            try:
                sent_message = await app.send_photo(principal_chat_id, msg.photo.file_id, caption=text, message_thread_id=principal_thread_id, reply_markup=None)
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                return
        case 'video':
            try:
                sent_message = await app.send_video(principal_chat_id, msg.video.file_id, caption=text, message_thread_id=principal_thread_id, reply_markup=None)
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                return
            
    now = datetime.now()
    timestamp = int(now.timestamp())
    reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("⏮️Revertir", f"revert_up_{sent_message.id}_{timestamp}")]]
    )
    await app.pin_chat_message(principal_chat_id, sent_message.id)
    await app.edit_message_text(chat_id, call.message.id, "<strong>✔️Concurso subido!</strong>\nSi te equivocaste puedes revertir con el botón.\n⚠️Luego de 5 minutos no pudes revertir.", parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^up_contest_cancel"))
async def up_cancel_contest(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    await app.delete_messages(chat_id, call.message.id)

@Client.on_callback_query(filters.regex(r"^revert_up_(\d+)_\d+$"))
async def up_revert_contest(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    parts = call.data.split('_')
    message_id = int(parts[2])
    timestamp_old = int(parts[3])

    now = datetime.now()
    timestamp_now = int(now.timestamp())

    if diference_min(timestamp_old, timestamp_now) >= 5:
        await app.answer_callback_query(call.id, "Lo siento, ya no puedes revertir pues han pasado más de 5 minutos desde que se envió su obra.", True)
        return
    
    try:
        await app.delete_messages(principal_chat_id, message_id)
    except Exception:
        await app.answer_callback_query(call.id, "Lo siento, ya no puedes revertir pues ha ocurrido un error. Contacta con los administradores.", True)
        return
    await app.edit_message_text(chat_id, call.message.id, "Operación revertida con éxito, debes enviar otra obra del mismo tipo para valorar antes de que acabe el tiempo del concurso.")
