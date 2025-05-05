import os
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram import filters
import time

from groq import Groq
from user_plugins.core.user_bot import user_app


@Client.on_message(filters.command('resumen'))
async def resumen_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    text = ""
    print("Buscando mensajes...")
    await message.reply_text("Dame un momento para leer el chat...")
    start_time = time.time()

    messages = []
    async for msg in user_app.get_chat_history(chat_id, limit=200):
        messages.append(msg)
    
    for msg in reversed(messages):
        if msg.text is None or msg.from_user.is_bot:
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
        
    #print(text)

    client = Groq(api_key=os.getenv('GROQ_API'))
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": "Tu labor es resumir fácilmente los chats en español de la mejor manera, e informarle a los usuarios que ha pasado recientemente en el grupo como si tu conocieras a todos. Sacalo en formato Markdown."},
            {"role": "user", "content": text}
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=False,
        reasoning_format="hidden"
    )

    

    print("Resumiendo...")
    res_ai = completion.choices[0].message.content
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"Tiempo transcurrido: {minutes} minutos y {seconds} segundos")
    result = f"{res_ai}\n\nTiempo transcurrido: {minutes} minutos y {seconds} segundos"
    await message.reply_text(result, parse_mode=enums.ParseMode.MARKDOWN)
    