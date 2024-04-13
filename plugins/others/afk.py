from pyrogram import Client
from pyrogram import enums
#from pyrogram.types import Message, LinkPreviewOptions
#from pyrogram import filters

from database.mongodb import get_db

import random

async def set_afk(message):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    user_id = message.from_user.id
    args = message.text.split(" ", 1)
    notice = ""
    
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nSu motivo de afk se redujo a 100 caracteres."
    else:
        reason = ""

    # Actualizar MongoDB
    await users.update_one(
        {"user_id": user_id},
        {"$set": {"is_afk": True, "reason": reason}},
        upsert=True
    )

    fname = message.from_user.first_name
    res = "{} ahora está AFK!{}".format(fname, notice)

    await message.reply_text(text=res)

async def get_afk(app, message):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        userc_id = message.reply_to_message.chat.id
        user = await users.find_one({"user_id": user_id})
    
        if user is not None and "is_afk" in user and int(userc_id) != int(user_id):
            res = f"<b>{fst_name}</b> está AFK"
            if user["reason"]:
                res += f".\nRazón: {user['reason']}"
            await message.reply_text(text=res, parse_mode=enums.ParseMode.HTML)
     
    # Detectar si el mensaje contiene el @username del cliente
    if hasattr(message, 'entities') and message.entities is not None:
        async for entity in message.entities:
            if entity.type == "mention":
                user_name = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                user = await users.find_one({"username": user_name})
    
                if user is not None:
                    user_id = user.get('user_id', None)
                    user_get = app.get_chat(user_id)
    
                    if "is_afk" in user:
                        res = f"<b>{user_get.first_name}</b> está AFK"
                        if user["reason"]:
                            res += f".\nRazón: {user['reason']}"
                        await message.reply_text(text=res, parse_mode=enums.ParseMode.HTML)
     
    #Revisar si está afk
    user_id = message.from_user.id
    user = message.from_user
    if not user:  # Ignorar canales
        return

    # Verificar si el usuario estaba en modo afk
    user_afk = await users.find_one({"user_id": user_id})
     
    if user_afk is not None and "is_afk" in user_afk:
        # Eliminar la entrada de afk de MongoDB
        await users.update_one({"user_id": user_id}, {"$unset": {"is_afk": "", "reason": ""}})
        #users.update_one({"user_id": user_id}, {"$unset": {"reason": ""}})

        # Enviar un mensaje de bienvenida de vuelta al usuario
        try:
            options = [
                '{} regresaste calv@!', 'Ah mira volvió {}!', 'Has vuelto {} mamawebo'
            ]
            chosen_option = random.choice(options)
            await message.reply_text(text=chosen_option.format(user.first_name))
        except Exception as e:
            print(f"Error al enviar mensaje de bienvenida: {e}")