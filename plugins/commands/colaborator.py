from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

from database.mongodb import get_db

@Client.on_message(filters.command('set_mod'))
async def set_mod_command(app: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text(text="Debes hacer reply a un usuario")
        return
    
    db = await get_db()
    users = db.users
    
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply_text(text="Solo los administradores pueden usar este comando.")
        return

    if chat_id != -1001485529816:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    user = await users.find_one({'user_id': message.reply_to_message.from_user.id})
    if user['is_mod'] and user['is_mod'] is True:
        await message.reply_text(text="Este usuario ya es colaborador.")
        return

    filter = {"user_id": reply_user_id}

    try:
        await users.update_one(filter, {"$set": {"is_mod": True}}, upsert=True)
    except Exception as e:
        await message.reply_text(text="Error en la acción.")
        print(f"Error: {e}")
        return

    await message.reply_text(text="Usuario agregado como colaborador.")
    
@Client.on_message(filters.command('del_mod'))
async def del_mod_command(app: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text(text="Debes hacer reply a un usuario")
        return
    
    db = await get_db()
    users = db.users
    
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply_text(text="Solo los administradores pueden usar este comando.")
        return
    if chat_id != -1001485529816:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    user = await users.find_one({'user_id': message.reply_to_message.from_user.id})
    if user['is_mod'] and user['is_mod'] is False:
        await message.reply_text(text="Este usuario no es colaborador.")
        return

    filter = {"user_id": reply_user_id}

    try:
        await users.update_one(filter, {"$set": {"is_mod": False}}, upsert=True)
    except Exception as e:
        await message.reply_text(text="Error en la acción.")
        print(f"Error: {e}")
        return
    
    await message.reply_text(text=f"Usuario eliminado de colaborador.")