import asyncio, re
from typing import Dict, List
from pyrogram.types import Message, ReactionTypeEmoji
from pyrogram import Client, enums
from database.useControl import UseControlMongo

useControlMongoInc = UseControlMongo()

async def validate_message(message: Message) -> bool:
    if not message.text or message.text.startswith("/"):
        return False
    return True

async def check_permissions(message: Message) -> bool:
    group_perm = [-1001485529816, -1001664356911, -1001223004404, -1002094390065]
    if message.chat.id not in group_perm and message.from_user.id != 873919300:
        await message.reply("Esta función es exclusiva de Otaku Senpai.")
        return False
    return True

async def check_usage_limits(message: Message, admins) -> bool:
    user_id = message.from_user.id
    
    if user_id in admins:
        return True
    if await useControlMongoInc.verif_limit(user_id) is False:
        msg = await message.reply("Has llegado al límite de uso diario!")
        await asyncio.sleep(3)
        await msg.delete()
        return False
    return True

async def handle_mentions(client: Client, message: Message, users_collection) -> List[Dict]:
    mentions = []
    if message.reply_to_message:
        user_reply_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        username = f"@{username}" if username else username

        text = message.reply_to_message.text or message.reply_to_message.caption or ""

        search_user = await users_collection.find_one({"user_id": user_reply_id})

        if user_reply_id == 6275121584:
            mentions.append({"name": "Akira", "akira_said": text})
        elif search_user:
            descr = search_user.get('description', "None")
            mentions.append(
                {"username": username, "description": descr, "user_said": text})

    return mentions

async def process_response(client: Client, message: Message, response: str):
    reaction_emoji = re.search(r'\[/(.*?)/\]', response).group(1) if re.search(r'\[/(.*?)/\]', response) else None
    text = re.sub(r'\[/.*?/\]', '', response).strip()

    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await asyncio.sleep(2)

    msg = await message.reply(text=text, parse_mode=enums.ParseMode.MARKDOWN)
    if reaction_emoji:
        await client.set_reaction(message.chat.id, message.id, reaction=[ReactionTypeEmoji(emoji=reaction_emoji)])