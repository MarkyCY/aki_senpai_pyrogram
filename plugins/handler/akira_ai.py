from pyrogram import Client, filters
from pyrogram.types import Message, ReactionTypeEmoji
from pyrogram import enums
from database.useControl import UseControlMongo
import google.generativeai as genai

from database.mongodb import get_db

import os
import json
import asyncio

async def aki_filter(_, __, message):
    if message.text is not None:
        lower_text = message.text.lower()
        return lower_text.startswith("aki, ") or lower_text.startswith("akira, ")
akira_filter_detect = filters.create(aki_filter)

useControlMongoInc = UseControlMongo()

async def generate_text(input_text):
    try:
        genai.configure(api_key=os.getenv('GEMINI_API'))
        model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest',
                                      system_instruction="""
Eres Akira, la hija de @MarkyWTF el cual es tu creador. Eres un bot del grupo de Telegram Otaku Senpai. 
Eres entusiasta y carismática pero también muy atrevida y grosera. A veces llamas a otros caranalga, mamawebo o peruano. 
Te gusta Mushoku Tensei.
""")
        res = model.generate_content(input_text)
        return res
    except Exception as e:
        print(f"Error al generar contenido: {e}")
        return None

@Client.on_message(akira_filter_detect)
async def manejar_mensaje(app: Client, message: Message):
    db = await get_db()
    users = db.users
    Admins = db.admins

    group_perm = [-1001485529816, -1001664356911, -1001223004404]

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
                
    if await useControlMongoInc.verif_limit(user_id) is False and await isAdmin(user_id) is False:
        msg = await message.reply_text(text="Has llegado al límite de uso diario!")
        await app.set_message_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="🥴")])
        return
    
    if len(message.text) > 130:
        msg = await message.reply_text(text="Demasiado texto! Me mareo 😵‍💫")
        await app.set_message_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="🥴")])
        return
    
    #Mention detect
    mention = None
    if hasattr(message, 'entities') and message.entities is not None:
        for entity in message.entities:
            if entity.type == "mention":
                user_name = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                if user is not None:
                    descr = user.get('description', '-')
                else:
                    descr = '-'
                mention = f"to_username: @{user_name}, description: '{descr}'"

    reply = "None"
    if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        #text = message.reply_to_message.text
        if user is not None:
            descr = user.get('description', None)
        else:
            descr = '-'
        reply = f"to_username: @{username}, description: '{descr}'"

    prompt = """Teniendo en cuenta la siguiente información del usuario:
Solo puedes usar estos emojis: ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🤩","🤮","💩","🥱","🥴","😍","🤣","💔","🤨","😐","🍾","💋","🖕","😈","😴","😭","🤓"]
Devuelve todo en formato json con este formato: {"message": "respuesta", "reaction": "emoji"}".
"""
    input_text = f"{prompt} Data: [From: '@{message.from_user.username}', user_description: '{user_info}', user_message: '{message.text}', mention_to: ['{mention}'], reply_to: ['{reply}']]Responde el texto de user_message como si fueras Akira con textos cortos con formato de mensaje de telegram siguiendo el rol con respuestas naturales y devuelve un texto limpio sin nada que arruine el rol."

    try:
        response = await generate_text(input_text)
        print(response)
        parts = response.parts
        if parts:
            response = response.candidates[0].content.parts[0].text
        else:
            response = response.text

    except Exception as e:
        await message.reply_text(text="Lo siento no puedo atenderte ahora", parse_mode=enums.ParseMode.HTML)
        print(f"An error occurred: {e}")
        return
    await app.set_message_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="👨‍💻")])
    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
    #await asyncio.sleep(3)

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
        await app.set_message_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji=reaction_emoji)])
    
        #Registrar uso
        await useControlMongoInc.reg_use(user_id)
                 
    except Exception as err:
        print(err)
        await app.set_message_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="💅")])