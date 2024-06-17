from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

from database.mongodb import get_db


async def add_collaborator(reply_user_id: int):
    db = await get_db()
    users = db.users

    try:
        await users.update_one({"user_id": reply_user_id}, {"$set": {"is_col": True}}, upsert=True)
        return "Usuario agregado como colaborador."
    except Exception as e:
        print(f"Error: {e}")
        return "Error en la acción."

async def remove_collaborator(reply_user_id: int):
    db = await get_db()
    users = db.users

    try:
        await users.update_one({"user_id": reply_user_id}, {"$set": {"is_col": False}}, upsert=True)
        return "Usuario eliminado de colaborador."
    except Exception as e:
        print(f"Error: {e}")
        return "Error en la acción."


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

    #if chat_id != -1001485529816:
    #    await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
    #    return
    
    reply_user_id = message.reply_to_message.from_user.id

    user = await users.find_one({'user_id': reply_user_id})
    if user and 'is_col' in user and user['is_col'] is True:
        await message.reply_text(text="Este usuario ya es colaborador.")
        return

    result = await add_collaborator(reply_user_id)
    await message.reply_text(text=result)

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

    #if chat_id != -1001485529816:
    #    await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
    #    return
    
    reply_user_id = message.reply_to_message.from_user.id

    user = await users.find_one({'user_id': reply_user_id})
    if not user or ('is_col' in user and user['is_col'] is False):
        await message.reply_text(text="Este usuario no es colaborador.")
        return

    result = await remove_collaborator(reply_user_id)
    await message.reply_text(text=result)