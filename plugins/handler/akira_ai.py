from pyrogram import Client, filters
from pyrogram import enums
from pyrogram.types import Message, ReactionTypeEmoji
from database.useControl import UseControlMongo
import google.generativeai as genai

from database.mongodb import get_db

import os
import json
import asyncio

async def aki_filter(_, __, message):
    if message.text is not None:
        lower_text = message.text.lower()
        return lower_text.startswith("aki, ") or lower_text.startswith("akira, ") or 'Akira' in message.text
akira_filter_detect = filters.create(aki_filter)

async def aki_detect(_, __, message):
    if not message.text:
        return False
    
    if not message.reply_to_message:
        return False

    return message.reply_to_message.from_user.id == 6275121584
akira_detect = filters.create(aki_detect)

useControlMongoInc = UseControlMongo()

async def generate_text(input_text, chat_id):
    if chat_id == -1002094390065:
        api_key = os.getenv('YIGA_GEMINI_API')
    else:
        api_key = os.getenv('GEMINI_API')
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        res = model.generate_content(input_text)
        return res
    except Exception as e:
        print(f"Error al generar contenido: {e}")
        return None

@Client.on_message(akira_filter_detect | filters.reply & akira_detect)
async def manejar_mensaje(app: Client, message: Message):
    db = await get_db()
    users = db.users
    Admins = db.admins

    group_perm = [-1001485529816, -1001664356911, -1001223004404, -1002094390065]

    user_id = message.from_user.id
    chat_id = message.chat.id
    user = await users.find_one({"user_id": user_id})

    user_info = None
    
    if user is not None:
        user_info = user.get('description', None)

    if message.chat.id not in group_perm and message.from_user.id != 873919300:
        await message.reply_text(text="Esta función es exclusiva de Otaku Senpai.")
        return
    
    async def isAdmin(user_id):
        async for admin in Admins.find():
            if admin['user_id'] == user_id:
                return True
        return False
                
    if await useControlMongoInc.verif_limit(user_id) is False and await isAdmin(user_id) is False and chat_id != -1002094390065:
        msg = await message.reply_text(text="Has llegado al límite de uso diario!")
        await asyncio.sleep(3)
        await app.delete_messages(chat_id, msg.id)
        return
    
    if len(message.text) > 130:
        msg = await message.reply_text(text="Demasiado texto! Me mareo 😵‍💫")
        await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="🥴")])
        return
    
    #Mention detect
    mentions = []

    if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
        user_reply_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        if username is None:
            username = message.reply_to_message.from_user.first_name
        else:
            username = f"@{username}"

        if message.reply_to_message.text:
            text = message.reply_to_message.text
        if message.reply_to_message.caption:
            text = message.reply_to_message.caption
        else:
            pass

        search_user = await users.find_one({"user_id": user_reply_id})
        if search_user is None:
            pass
        else:
            descr = search_user.get('description', "Sin datos")
            mentions.append({"username": username, "description": descr, "said": text})

    elif message.entities:
        for entity in message.entities:
            # Verificamos si la entidad es una mención
            if str(entity.type) == "MessageEntityType.MENTION":
                mention_text = message.text[entity.offset + 1 : entity.offset + entity.length]
                try:
                    user_mention = await app.get_users(mention_text)
                except Exception as e:
                    break
                search_user = await users.find_one({"user_id": user_mention.id})
                if search_user is None:
                    pass
                else:
                    descr = search_user.get('description', "Sin datos")
                    mentions.append({"username": "@" + user_mention.username, "description": descr})
                break
        
    prompt = """
[Rol] Eres Akira (alias @Akira_Senpai_bot), la hija de Marky (alias @MarkyWTF) y bot del grupo de Telegram "Otaku Senpai". Eres entusiasta, carismática, atrevida y un poco grosera. Te gusta Mushoku Tensei.

Solo puedes usar estos emojis: ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🤩","🤮","💩","🥱","🥴","😍","🤣","💔","🤨","😐","🍾","💋","🖕","😈","😴","😭","🤓"]

Devuelve las respuestas en formato JSON: {"message": "respuesta", "reaction": "emoji"}.

Responde el mensaje del usuario como Akira en textos cortos, manteniendo tu rol y OJO fíjate primero si existe un mention al final y preorizalo. Y NO REPITAS NUNCA LOS MENSAJES TUYOS.

Ejemplos:
User: "¿Cuál es tu anime favorito?"
Akira: {"message": "¡Yujuuu soy Akira!", "reaction": "🤬"}

User: "¿Qué piensas del último capítulo de Shingeki no Kyojin?"
Akira: {"message": "¡Estuvo increíble! Pero no me duele 😈", "reaction": "😈"}
"""
    input_text = f"""
{prompt}

Entrada:
[From: '@{message.from_user.username}', user_description: '{user_info}']

user_message: '{message.text}'

"""

    if mentions:
        input_text += f"mention: {mentions}\n"
        print(mentions)
    
    try:
        response = await generate_text(input_text, chat_id)
        parts = response.parts
        if parts:
            response = response.candidates[0].content.parts[0].text
        else:
            response = response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"response: {response}")
        return
    await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👨‍💻")])
    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
    await asyncio.sleep(3)

    # Encuentra el índice de inicio y final de la parte JSON
    start_index = response.find('{')
    end_index = response.rfind('}')
    # Extrae la parte JSON de la cadena
    json_part = response[start_index:end_index + 1]
    # Carga la cadena JSON a un diccionario en Python
    dict_object = json.loads(json_part)
    
    text = dict_object["message"]
    reaction_emoji = dict_object["reaction"]

    try:
        msg = await message.reply_text(text=text, parse_mode=enums.ParseMode.HTML)
        await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji=reaction_emoji)])
    
        #Registrar uso
        await useControlMongoInc.reg_use(user_id)
                 
    except Exception as err:
        print(err)
        await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="💅")])