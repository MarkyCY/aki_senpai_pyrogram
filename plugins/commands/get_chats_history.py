import os, time
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram import filters

from google import genai
from google.genai import types

from groq import Groq
from user_plugins.core.user_bot import user_app


@Client.on_message(filters.command('resumen'))
async def resumen_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    args = message.text.split()

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    limit=200

    if len(args) > 1:
        try:
            limit = int(args[1])
        except ValueError:
            limit = 200

    
    text = ""
    print(f"Buscando mensajes...\nLimite de mensajes: {limit}")
    await message.reply_text("Dame un momento para leer el chat...")
    start_time = time.time()

    messages = []
    async for msg in user_app.get_chat_history(chat_id, limit=limit):
        messages.append(msg)
    
    for msg in reversed(messages):
        if msg.text is None or msg.text.startswith('/protecc') or msg.from_user.is_bot:
            continue

        message_thread = message.message_thread_id if message.message_thread_id else None
        if message_thread:
            if message_thread == msg.message_thread_id:
                print(f"Mensaje en el hilo: {msg.message_thread_id}")
                text += f"\nMsg_id: {msg.id}, "
                text += f"Name: {msg.from_user.first_name if msg.from_user and msg.from_user.first_name else (msg.from_user.username if msg.from_user   else 'Unknown')}:"
                text += f'"{msg.text}"\n'
        else:
            if msg.message_thread_id:
                continue
            print(f"Mensaje normal: 1")
            text += f"\nMsg_id: {msg.id}, "
            text += f"Name: {msg.from_user.first_name if msg.from_user and msg.from_user.first_name else (msg.from_user.username if msg.from_user else 'Unknown')}: "
            text += f'"{msg.text}"'

        if msg.reply_to_message and msg.reply_to_message.text:
            text += f", reply_to_msg_id: {msg.reply_to_message.id}"
        
    print(text[:200])
    
    if limit > 200:
        print("Usando GenAI...")
        res_ai = generate_genai(text)
    else:
        print("Usando Groq...")
        res_ai = generate_groq(text)

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"Tiempo transcurrido: {minutes} minutos y {seconds} segundos")

    result = f"{res_ai}\n\nTiempo transcurrido: {minutes} minutos y {seconds} segundos"
    
    if len(result) <= 4070:
        try:
            await message.reply_text(result)
        except Exception as e:
            print(e)
            await app.send_message(chat_id, result)
    else:
        print(result)
        chunks = []
        current_chunk = ""
        words = result.split()
        
        for word in words:
            if len(current_chunk) + len(word) + 1 <= 4070:
                current_chunk += word + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        for chunk in chunks:
            try:
                await message.reply_text(chunk)
            except Exception as e:
                print(e)
                await app.send_message(chat_id, chunk)
    

def generate_groq(text: str):
    client = Groq(api_key=os.getenv('GROQ_API'))
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": "Tu labor es resumir fácilmente los chats en español de la mejor manera, e informarle a los usuarios que ha pasado recientemente en el grupo como si tu conocieras a todos."},
            {"role": "user", "content": text}
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=False,
        reasoning_format="hidden"
    )

    return completion.choices[0].message.content


def generate_genai(text: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API"))

    model = "gemini-2.5-flash-preview-04-17"
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction="""Tu labor es resumir fácilmente los chats en español de la mejor manera, e informarle a los usuarios que ha pasado recientemente en el grupo como si tu conocieras a todos. Dame la respuesta a modo de lista con los sucesos más relevantes del chat y también cosas que puedan ser divertidas o dar chisme. Tu respuesta está será en formato de mensaje de telegram para un grupo así que todo debe ser bien legible, enumerado los titulos y con plecas (-) los subtitulos y dos saltos de linea entre eventos. Formato de respuesta: Titulo\n\nIntroducción:\n\n1. Titulo de evento:\n   - Evento bien descrito.\n   - Evento bien descrito.\n\n2. Otro Titulo de Evento:\n   - Evento bien descrito.\n   - Evento bien descrito.\n\nDespedida calida. IMPORTATE: NO USAR ASTERISCOS (*), SOLO - Y NUMEROS.""",
        thinking_config=types.ThinkingConfig(
            thinking_budget=2048  # Puedes ajustar este valor según tus necesidades
        )
    )

    response = client.models.generate_content(
        model=model,
        contents=text,
        config=generate_content_config,
    )
    return response.text
