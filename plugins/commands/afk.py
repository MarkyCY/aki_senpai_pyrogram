from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters, enums
from plugins.others.afk import set_afk
from database.mongodb import get_db

import random

async def afk_filter(_, __, message):
    if message.text is not None:
        lower_text = message.text.lower()
        return lower_text.startswith(".brb") or lower_text.startswith(".afk")
afk_filter_detect = filters.create(afk_filter)


@Client.on_message(filters.command(['afk', 'brb']), group=5)
async def afk_command(app: Client, message: Message):
    await set_afk(message)

@Client.on_message(afk_filter_detect, group=5)
async def afk_controller(app: Client, message: Message):
    await set_afk(message)

@Client.on_message(filters.incoming, group=5)
async def get_afk_handler(app: Client, message: Message):
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
            return
     
    # Detectar si el mensaje contiene el @username del cliente
    if message.entities and message.entities is not None:
        entities = message.entities
        for entity in entities:
            entity_type = str(entity.type).split('.')[1].lower()
            if (entity_type) == "mention":
                user_name = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                user = await users.find_one({"username": user_name})
    
                if user is not None:
                    user_id = user.get('user_id', None)
                    user_get = await app.get_chat(user_id)
    
                    if "is_afk" in user:
                        res = f"<b>{user_get.first_name}</b> está AFK"
                        if user["reason"]:
                            res += f".\nRazón: {user['reason']}"
                        await message.reply_text(text=res, parse_mode=enums.ParseMode.HTML)
                        return
     
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