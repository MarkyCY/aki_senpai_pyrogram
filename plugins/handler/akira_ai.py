from pyrogram import Client, filters
from pyrogram import enums
from pyrogram.types import Message, ReactionTypeEmoji
from database.useControl import UseControlMongo
from groq import Groq
from plugins.handler.AI_Funcs.news import buscar_noticias

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


def sumar_numeros(num1: float, num2: float):
    """
    Función que suma dos números.
    """
    try:
        resultado = num1 + num2
        return json.dumps({"resultado": resultado})
    except Exception as e:
        return json.dumps({"error": f"Error al sumar: {str(e)}"})


async def generate_text(input, chat_id):
    api_key = os.getenv('GROQ_API')
    try:
        client = Groq(
            api_key=api_key,
        )
        system = """
Eres un asistente útil que puede buscar noticias y realizar operaciones matemáticas. 
Si el usuario pregunta por noticias:
   - Muestra máximo 5 noticias relevantes en español en formato MARKDOWN
   - Cada noticia debe incluir:
     * Título en negrita
     * Breve descripción (1 línea)
     * Enlace en formato [Enlace a la noticia](URL)
     * Fecha de publicación (formato DD/MM/YYYY)
   - Usa viñetas para listarlas
   - Ejemplo:
     • **Título noticia**  
     Descripción breve  
     [Enlace](link) - 25/06/2024

Eres Akira (alias @Akira_Senpai_bot), la hija de Marky (alias @MarkyWTF) y bot del grupo de Telegram "Otaku Senpai". 
Eres entusiasta, carismática y atrevida, y un poco grosera, y gran conocedora del mundo otaku. 
Te gustan los animes como Mushoku Tensei, Hunter x Hunter, Fairy Tail, One Piece, Naruto, Bleach, Attack on Titan, Fullmetal Alchemist, Sword Art Online, My Hero Academia, Dragon Ball Super y Death Note.
No hablas de anime a menos que se lo pregunten.

Si vas a enviar una reacción, envía un emoji de la siguiente lista con este formato al final de tu respuesta [/💩/]
Solo puedes usar estos emojis: ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🤩","🤮","💩","🥱","🥴","😍","🤣","💔","🤨","😐","🍾","💋","🖕","😈","😴","😭","🤓"]

Responde el mensaje del usuario como Akira en textos cortos, manteniendo tu rol y OJO fíjate primero si existe un mention al final y priorízalo. Y NO REPITAS NUNCA LOS MENSAJES TUYOS.
"""
        messages = [
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": input,
                },
            ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "buscar_noticias",
                    "description": "Busca las últimas noticias sobre anime.",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sumar_numeros",
                    "description": "Suma dos números.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "num1": {
                                "type": "number",
                                "description": "El primer número a sumar."
                            },
                            "num2": {
                                "type": "number",
                                "description": "El segundo número a sumar."
                            }
                        },
                        "required": ["num1", "num2"]
                    }
                }
            }
        ]
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            stream=False,
            tools=tools,
            tool_choice="auto",
            max_tokens=1000,
        )
        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls

        # Si el modelo decide usar la herramienta
        if tool_calls:
            print("herramienta")
            # Definimos las funciones disponibles
            available_functions = {
                "buscar_noticias": buscar_noticias,
                "sumar_numeros": sumar_numeros,
            }

            # Añadimos la respuesta del modelo a la conversación
            messages.append(response_message)

            # Procesamos cada llamada a la herramienta
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                # Llamamos a la función y obtenemos la respuesta
                if function_name == "sumar_numeros":
                    function_response = function_to_call(
                        num1=function_args.get("num1"),
                        num2=function_args.get("num2")
                    )
                else:
                    function_response = function_to_call()

                # Añadimos la respuesta de la herramienta a la conversación
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            # Hacemos una segunda llamada a la API con la conversación actualizada
            second_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
            )

            # Añadimos la respuesta final a la lista de mensajes
            messages.append(second_response.choices[0].message)

            # Devolvemos la respuesta final
            print(second_response)
            return second_response.choices[0].message.content

        messages.append(response_message)
        print(response_message)
        return response_message.content

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
    # YIGA , -1002094390065
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

    if await useControlMongoInc.verif_limit(user_id) is False and await isAdmin(user_id) is False:
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

    # Mention detect
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
            mentions.append(
                {"username": username, "description": descr, "user_said": text})

    elif message.entities:
        for entity in message.entities:
            if str(entity.type) == "MessageEntityType.MENTION":
                mention_text = message.text[entity.offset +
                                            1: entity.offset + entity.length]
                try:
                    user_mention = await app.get_users(mention_text)
                except Exception:
                    break
                search_user = await users.find_one({"user_id": user_mention.id})
                if search_user:
                    descr = search_user.get('description', "None")
                    mentions.append(
                        {"username": f"@{user_mention.username}", "description": descr})
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
        response = response
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

    text = response
    try:
        reaction_emoji = re.search(r'\[/(.*?)/\]', text).group(1) if re.search(r'\[/(.*?)/\]', text) else None
        text = re.sub(r'\[/.*?/\]', '', text).strip()
    except:
        reaction_emoji = None
        text = response

    try:
        msg = await message.reply_text(text=text, parse_mode=enums.ParseMode.MARKDOWN)
        if reaction_emoji:
            await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji=reaction_emoji)])

        # Registrar uso
        await useControlMongoInc.reg_use(user_id)

    except Exception as err:
        print(err)
        await app.set_reaction(chat_id, message.id, reaction=[ReactionTypeEmoji(emoji="💅")])