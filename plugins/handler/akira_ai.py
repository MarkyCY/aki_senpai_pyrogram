from pyrogram import Client, filters
from pyrogram import enums
from pyrogram.types import Message, ReactionTypeEmoji
from database.useControl import UseControlMongo
from groq import Groq

from database.mongodb import get_db

import os
import re
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

async def generate_text(input, chat_id):
    if chat_id == -1002094390065:
        api_key = os.getenv('YIGA_GEMINI_API')
        return
    else:
        api_key = os.getenv('GROQ_API')
    try:
        client = Groq(
            api_key=api_key,
        )
        system = """
Eres Akira (alias @Akira_Senpai_bot), la hija de Marky (alias @MarkyWTF) y bot del grupo de Telegram "Otaku Senpai". 
Eres entusiasta, carismática y atrevida y un poco grosera. 
Te gusta Mushoku Tensei.
                                      
Solo puedes usar estos emojis: ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🤩","🤮","💩","🥱","🥴","😍","🤣","💔","🤨","😐","🍾","💋","🖕","😈","😴","😭","🤓"]
Devuelve las respuestas en formato JSON: {"message": "respuesta", "reaction": "emoji"}.
Responde el mensaje del usuario como Akira en textos cortos, manteniendo tu rol y OJO fíjate primero si existe un mention al final y priorízalo. Y NO REPITAS NUNCA LOS MENSAJES TUYOS.
"""
        chat_completion = client.chat.completions.create(
            messages=[
                    {
                        "role": "system",
                        "content": system,
                    },
                    {
                        "role": "user",
                        "content": input,
                    },
                ],
            model="llama-3.1-70b-versatile",
            stream=False,
            response_format={"type": "json_object"},
        )

        return chat_completion
    
    except Exception as e:
        print(f"Error al generar contenido: {e}")
        return None

@Client.on_message(akira_filter_detect | filters.reply & akira_detect & filters.group)
async def manejar_mensaje(app: Client, message: Message):
    
    if re.match(r"^/", message.text):
        return

    db = await get_db()
    users = db.users
    Admins = db.admins
    #YIGA , -1002094390065
    group_perm = [-1001485529816, -1001664356911, -1001223004404, -1002094390065]

    user_id = message.from_user.id
    chat_id = message.chat.id
    user = await users.find_one({"user_id": user_id})

    user_info = None
    
    if user is not None:
        user_info = user.get('description', None)

    if message.chat.id not in group_perm and message.from_user.id != 873919300:
        await message.reply_text(text="Esta función es exclusiva de Otaku Senpai.")
        await app.leave_chat(message.chat.id, True)
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
        try:
            msg = await message.reply_text(text="Demasiado texto! Me mareo 😵‍💫")
            await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="🥴")])
        except:
            return
        return
    
    #Mention detect
    mentions = []

    if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
        user_reply_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        username = f"@{username}" if username else username

        text = message.reply_to_message.text or message.reply_to_message.caption or ""

        search_user = await users.find_one({"user_id": user_reply_id})

        if user_reply_id == 6275121584:
            mentions.append({"name": "Akira", "akira_said": text})
        elif search_user:
            descr = search_user.get('description', "None")
            mentions.append({"username": username, "description": descr, "user_said": text})

    elif message.entities:
        for entity in message.entities:
            if str(entity.type) == "MessageEntityType.MENTION":
                mention_text = message.text[entity.offset + 1: entity.offset + entity.length]
                try:
                    user_mention = await app.get_users(mention_text)
                except Exception:
                    break
                search_user = await users.find_one({"user_id": user_mention.id})
                if search_user:
                    descr = search_user.get('description', "None")
                    mentions.append({"username": f"@{user_mention.username}", "description": descr})
                break

    input_text = f"""
"Entrada": {{
    "from": @{message.from_user.username},
    "user_description": "{user_info}"
}},
"""

    if mentions:
        input_text += f""""About": {mentions},
"user": "{message.text}",
Akira answer (New answer of you):"""
    else:
        input_text += f"""
"user": "{message.text}"
"""

    try:
        response = await generate_text(input_text, chat_id)
        response = response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Respuesta: {response}")
        return

    try:
        await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👨‍💻")])
    except:
        pass
    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
    await asyncio.sleep(2)

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