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
principal_chat_id = -1001664356911
principal_thread_id = 53628

@Client.on_callback_query(filters.regex(r"^contest_up_[a-f\d]{24}_\d+$"))
async def up_contest(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    parts = call.data.split('_')
    contest_id = ObjectId(parts[2])
    message_id = int(parts[3])
    user_id = call.from_user.id
    

    db = await get_db()
    contest = db.contest
    Contest_Data = db.contest_data

    contest_sel = await contest.find_one({'_id': contest_id})

    contest_data = await Contest_Data.find_one({'contest_id': contest_id, 'user_id': user_id})
    if contest_data:
        contest_data_id = contest_data['_id']
    else:
        contest_data_id = ObjectId()

    msg = await app.get_messages(chat_id=chat_id, message_ids=message_id)

    # Buttons
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(str(i), callback_data=f"vote_{i}_{call.from_user.id}_{contest_data_id}") for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=f"vote_{i}_{call.from_user.id}_{contest_data_id}") for i in range(6, 11)]
        ]
    )

    text = f"Esta obra es envíada por <a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a> participando en el concurso: {contest_sel['title']}\n\nVoto:\n"
    match contest_sel['type']:
        case 'text':
            msg_text = msg.text
            words = msg_text.split()
            
            if len(words) < contest_sel['amount_text']:
                return await app.answer_callback_query(call.id, f"El mensaje debe tener al menos {contest_sel['amount_text']} palabras...")
            
            msg_text += "\n\n", text
            try:
                sent_message = await app.send_message(principal_chat_id, msg.text, message_thread_id=principal_thread_id, reply_markup=markup)
                data = {'_id': contest_data_id, 'contest_id': contest_sel['_id'], 'user_id': user_id, 'type': contest_sel['type'], 'm_id': sent_message.id, 'text': msg.text}
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                print(e)
                return
        case 'photo':
            try:
                sent_message = await app.send_photo(principal_chat_id, msg.photo.file_id, caption=text, message_thread_id=principal_thread_id, reply_markup=markup)
                data = {'_id': contest_data_id, 'contest_id': contest_sel['_id'], 'user_id': user_id, 'type': contest_sel['type'], 'm_id': sent_message.id, 'file_id': msg.photo.file_id}
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                print(e)
                return
        case 'video':
            try:
                sent_message = await app.send_video(principal_chat_id, msg.video.file_id, caption=text, message_thread_id=principal_thread_id, reply_markup=markup)
                data = {'_id': contest_data_id, 'contest_id': contest_sel['_id'], 'user_id': user_id, 'type': contest_sel['type'], 'm_id': sent_message.id, 'file_id': msg.video.file_id}
            except Exception as e:
                await app.send_message(chat_id, text="Ha ocurrido un error")
                print(e)
                return
            
    if contest_data:
        try:
            await app.unpin_chat_message(principal_chat_id, contest_data['m_id'])
        except Exception:
            pass
        await app.delete_messages(principal_chat_id, contest_data['m_id'])
        await Contest_Data.update_one({'contest_id': contest_id, 'user_id': user_id}, {'$set': data})
    else:
        await Contest_Data.insert_one(data)
            
    now = datetime.now()
    timestamp = int(now.timestamp())
    reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("⏮️Revertir", f"revert_up_{sent_message.id}_{timestamp}_{contest_id}")]]
    )
    try:
        await app.pin_chat_message(principal_chat_id, sent_message.id, True)
    except Exception:
        pass
    if contest_data:
        await app.edit_message_text(chat_id, call.message.id, "<strong>✔️Concurso actualizado!</strong>", parse_mode=enums.ParseMode.HTML)
    else:
        await app.edit_message_text(chat_id, call.message.id, "<strong>✔️Concurso subido!</strong>\nSi te equivocaste puedes revertir con el botón.\n⚠️Luego de 5 minutos no pudes revertir.", parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^up_contest_cancel"))
async def up_cancel_contest(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    await app.delete_messages(chat_id, call.message.id)

@Client.on_callback_query(filters.regex(r"^revert_up_(\d+)_\d+_[a-f\d]{24}$"))
async def up_revert_contest(app: Client, call: CallbackQuery):

    db = await get_db()
    Contest_Data = db.contest_data

    chat_id = call.message.chat.id
    parts = call.data.split('_')
    message_id = int(parts[2])
    timestamp_old = int(parts[3])
    contest_id = ObjectId(parts[4])
    user_id = call.from_user.id

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
    await Contest_Data.delete_one({'contest_id': contest_id, 'user_id': user_id})