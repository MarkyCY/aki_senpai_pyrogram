from pyrogram import Client
from pyrogram.types import Message, LinkPreviewOptions
from pyrogram import filters
from pyrogram import enums

from database.mongodb import get_db

import json


@Client.on_message(filters.command('staff'))
async def info_command(app: Client, message: Message):

    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'supergroup' or chat_type == 'group'):
        await message.reply_text(text="Este comando solo puede ser usado en grupos y en supergrupos")
        return

    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    # obtén la información del chat
    chat_id = message.chat.id
    #chat_info = bot.get_chat(chat_id)
    # obtén la lista de administradores del chat
    admins = app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
     
    # Divide a los administradores en propietario y otros administradores
    owner = None
    other_admins = []

     
    async for admin in admins:
        admin_status = str(admin.status).split('.')[1].lower()
        if admin_status == 'owner':
            owner = admin
        elif not admin.user.is_bot:
            other_admins.append(admin)
            # guarda el administrador en la base de datos si no existe
            #if chat_admins.find_one({"user_id": admin.user.id}) is None:
            #    chat_admins.insert_one({"user_id": admin.user.id, "username": admin.user.username})
     
    # envía un mensaje con la lista de administradores al chat
    message_text = f"👑Propietario:\n└ <a href='https://t.me/{owner.user.username}'>{owner.user.username} > {owner.custom_title}</a>\n\n⚜️ Administradores:"
    
    for user in other_admins[:-1]:
        message_text += f"\n├ <a href='https://t.me/{user.user.username}'>{user.custom_title}</a>"
     
    if other_admins:
        message_text += f"\n└ <a href='https://t.me/{other_admins[-1].user.username}'>{other_admins[-1].custom_title}</a>\n"

    if message.chat.id == -1001485529816:
        mods = [doc async for doc in users.find({"is_mod": True})]
        for i, user in enumerate(mods[:-1]):
            user_id = user['user_id']
            try:
                get_user = await app.get_chat_member(int(chat_id), int(user_id))
                if i == 0:
                    message_text += f"\n🔰Colaboradores:\n├ <a href='https://t.me/{get_user.user.username}'>{get_user.user.first_name}</a>"
                else:
                    message_text += f"\n├ <a href='https://t.me/{get_user.user.username}'>{get_user.user.first_name}</a>"
            except Exception as e:
                print(e)
        if mods:
            user = mods[-1]
            user_id = user['user_id']
            get_user = await app.get_chat_member(chat_id, int(user_id))
            message_text += f"\n└<a href='https://t.me/{get_user.user.username}'>{get_user.user.first_name}</a>"
     
    await message.reply_text(text=message_text, parse_mode=enums.ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))
        



async def isAdmin(user_id):
    # Conectar a la base de datos
    db = await get_db()
    chat_admins = db.admins

    isAdmin = None
    admins = chat_admins.find()
    for admin in admins:
        if admin['user_id'] == user_id:
            isAdmin = "Yes"
    return isAdmin


async def isModerator(user_id):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    isModerator = False
    Users = await users.find({"is_mod": True})
    for user in Users:
        if user['user_id'] == user_id:
            isModerator = True
    return isModerator


async def set_mod(message, app):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    if not message.reply_to_message:
        await message.reply_text(text="Debes hacer reply a un usuario")
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    chat_member = await app.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        await message.reply_text(text="Solo los administradores pueden usar este comando.")
        return

    if chat_id != -1001485529816:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    filter = {"user_id": reply_user_id}

    try:
        users.update_one(filter, {"$set": {"is_mod": True}}, upsert=True)
    except Exception as e:
        await message.reply_text(text="Error en la acción.")
        print(f"Error: {e}")
        return

    await message.reply_text(text="Usuario agregado como colaborador.")
    
async def del_mod(message, app):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    if not message.reply_to_message:
        await message.reply_text(text="Debes hacer reply a un usuario")
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        await message.reply_text(text="Solo los administradores pueden usar este comando.")
        return
    if chat_id != -1001485529816:
        await message.reply_text(text="Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    filter = {"user_id": reply_user_id}

    try:
        await users.update_one(filter, {"$set": {"is_mod": False}}, upsert=True)
    except Exception as e:
        await message.reply_text(text="Error en la acción.")
        print(f"Error: {e}")
        return
    
    await message.reply_text(text=f"Usuario eliminado de colaborador.")
