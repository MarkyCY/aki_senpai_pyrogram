from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from database.mongodb import get_db
from plugins.others.contest import *
from bson import ObjectId

from plugins.others.contest import disq_user, un_disq_user, del_user

@Client.on_callback_query(filters.regex(r"^disq_\d{8,11}_[a-f\d]{24}$"))
async def disqualified(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    Disq = None

    db = await get_db()
    contest = db.contest
    Contest_Data = db.contest_data

    parts = call.data.split('_')
    u_disq = int(parts[1])
    contest_id = ObjectId(parts[2])

    contest = await contest.find_one({'_id': contest_id})

    if contest['disqualified']:
        for disq in contest['disqualified']:
            if disq['user'] == u_disq:
                Disq = True
                break

    if Disq is None:
        disq = await disq_user(u_disq, contest_id)

    try:
        await del_user(u_disq, contest_id)
        await Contest_Data.delete_one({'contest_id': contest_id, 'user_id': u_disq})
    except Exception as e:
        await app.answer_callback_query(call.id, f"Ha ocurrido un error: {str(e)}", True)
        return

    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅Permitir", callback_data=f"allow_{u_disq}_{contest_id}")],
        ]
    )
    msg = f"El <a href='tg://user?id={u_disq}'>usuario</a> ha sido descalificado para este concurso."
    
    await app.edit_message_caption(cid, mid, msg, reply_markup=markup)
    await app.send_message(u_disq, f"Oh no 😢, has sido descalificado del concuroso: {contest['title']}.")

@Client.on_callback_query(filters.regex(r"^allow_\d{8,11}_[a-f\d]{24}$"))
async def undo_disqualified(app: Client, call: CallbackQuery):
    cid = call.message.chat.id
    mid = call.message.id
    Disq = None

    db = await get_db()
    contest = db.contest

    parts = call.data.split('_')
    u_disq = int(parts[1])
    contest_id = ObjectId(parts[2])

    contest = await contest.find_one({'_id': contest_id})

    if contest['disqualified']:
        for disq in contest['disqualified']:
            if disq['user'] == u_disq:
                Disq = True
                break
    if Disq == True:
        undisq = await un_disq_user(u_disq, contest_id) 
    
        if undisq.modified_count == 0:
            await app.answer_callback_query(call.id, "No se ha permitido al usuario...", True)
            return

    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❌Descalificar", callback_data=f"disq_{u_disq}_{contest_id}")],
        ]
    )
    msg = f"El <a href='tg://user?id={u_disq}'>usuario</a> ha sido permitido para este concurso."
    
    await app.edit_message_caption(cid, mid, msg, reply_markup=markup)
    await app.send_message(u_disq, f"Pssst, has sido permitido para participar en el concurso: {contest['title']}. Debes suscribirte nuevamente para poder participar.")