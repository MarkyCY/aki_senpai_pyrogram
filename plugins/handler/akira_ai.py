from pyrogram import Client
from pyrogram.types import Message, ReactionTypeEmoji
from pyrogram import filters

from database.mongodb import get_db
from plugins.handler.AI_Assets.filters import akira_filter_detect, akira_detect
from plugins.handler.AI_Assets.groq_client import GroqClient
from plugins.handler.AI_Assets.utils import (
    handle_mentions,
    validate_message,
    process_response,
    check_permissions,
    check_usage_limits
)
from database.useControl import UseControlMongo

use_control = UseControlMongo()
groq_client = GroqClient(
    system_prompt_path="plugins/handler/AI_Assets/system_prompt.txt",
    tools_config="plugins/handler/AI_Assets/tools_config.json",
    emoji_list="plugins/handler/AI_Assets/emojis.json"
)

@Client.on_message(akira_filter_detect | filters.reply & akira_detect & filters.group)
async def handle_message(client: Client, message: Message):
    try:
        # Validación inicial
        if not await validate_message(message):
            return

        db = await get_db()
        users_collection = db.users
        Admins = db.admins
        
        admins = [doc['user_id'] async for doc in Admins.find()]
        premium = False
        if message.from_user.id in admins:
            premium = True
        
        # Verificación de permisos y límites
        if not await check_permissions(message) or not await check_usage_limits(message, admins):
            return

        # Procesar menciones
        mentions = await handle_mentions(client, message, users_collection)
        
        # Construir prompt
        user_info = (await users_collection.find_one({"user_id": message.from_user.id}) or {}).get('description', "")
        input_text = groq_client.build_prompt(message, user_info, mentions)

        # Generar respuesta
        response = await groq_client.generate_response(input_text, message.chat.id, premium)
        if not response:
            raise ValueError("Empty response from AI")

        # Procesar y enviar respuesta
        await process_response(client, message, response)

        # Registrar uso
        await use_control.reg_use(message.from_user.id)

    except Exception as e:
        await handle_errors(client, message, e)

async def handle_errors(client: Client, message: Message, error: Exception):
    error_message = f"❌ Error: {str(error)}"
    print(f"Error: {error_message}")
    try:
        await client.send_message(-1001664356911, error_message, message_thread_id=82096)
    except Exception as e:
        print(f"Error handling error: {e}")