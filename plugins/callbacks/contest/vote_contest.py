from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from database.mongodb import get_db
from plugins.others.contest import *
from bson import ObjectId

import re

@Client.on_callback_query(filters.regex(r"^vote_(10|[1-9])_\d{8,11}_[a-f\d]{24}$"))
async def up_contest(app: Client, call: CallbackQuery):

    db = await get_db()
    Contest_Data = db.contest_data

    JUECES = {873919300, 759372927, 1881435398, 938816655, 5897689654, 5346671352, 1221472021}

    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.id
    
    parts = call.data.split('_')
    vote = int(parts[1])
    u_vote = parts[2]
    contest_data_id = ObjectId(parts[3])

    emojis = {"1": "1️⃣","2": "2️⃣","3": "3️⃣","4": "4️⃣","5": "5️⃣","6": "6️⃣","7": "7️⃣","8": "8️⃣","9": "9️⃣","10": "🔟"}
    if uid not in JUECES:
        await app.answer_callback_query(call.id, f"Tu no eres un juez...")
        return

    
    contest = await Contest_Data.find_one({'_id': contest_data_id})
    if contest is None:
        await app.answer_callback_query(call.id, f"No existe esta entrega en la base de datos...")
        return
         
    if 'vote' in contest and str(uid) in contest['vote']:
        await app.answer_callback_query(call.id, f"Votado actualizado de: {contest['vote'][str(uid)]} a {vote}")
    else:
        await app.answer_callback_query(call.id, f"Has Votado: {vote}")
         
    if contest['type'] == 'photo' or contest['type'] == 'video':
        msg = call.message.caption
    if contest['type'] == 'text':
        msg = call.message.text

    name = call.from_user.first_name

    if re.search(r'(' + re.escape(name) + r'\d+️⃣|' + re.escape(name) + r'🔟)', msg):
        msg = re.sub(r'(' + re.escape(name) + r'\d+️⃣|' + re.escape(name) + r'🔟)', f'{name}{emojis[str(vote)]}', msg)
    else:
        msg += f'\n{name}{emojis[str(vote)]}'
    #msg = f"Foto de concurso:\nHas votado: {emojis[partes[2]]}"
     
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(str(i), callback_data=f"vote_{i}_{u_vote}_{contest_data_id}") for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=f"vote_{i}_{u_vote}_{contest_data_id}") for i in range(6, 11)],
            [
                InlineKeyboardButton("❌Descalificar", callback_data=f"disq_{u_vote}_{contest['contest_id']}"),
            ]
        ]
    )
     
    if contest['type'] == 'photo' or contest['type'] == 'video':
        await app.edit_message_caption(cid, mid, msg, reply_markup=markup)
    if contest['type'] == 'text':
        await app.edit_message_text(cid, mid, msg, reply_markup=markup)
     
    await Contest_Data.update_one(
       { "_id": contest_data_id },
       { "$set": { "vote." + str(uid): int(vote) } }
    )
         
    return
