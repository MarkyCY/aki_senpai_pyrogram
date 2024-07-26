from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram import filters

@Client.on_message(filters.command('report'))
async def report_command(app: Client, message: Message):
    # obtén la información del chat
    chat_type = str(message.chat.type).split('.')[1].lower()
    if not (chat_type == 'supergroup' or chat_type == 'group'):
        await message.reply_text(text=f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_id = message.chat.id
    chat_member = await app.get_chat_member(chat_id, message.from_user.id)
    member_status = str(chat_member.status).split('.')[1].lower()
    if member_status in ['administrator', 'owner']:
        await message.reply_text(text=f"Este comando no está disponible para administradores")
        return
    
    if not message.reply_to_message:
        await message.reply_text(text=f"Debes hacer reply a un mensaje para poder reportar a un usuario")
        return

    chat_str_id = str(message.chat.id)[4:]
    message_id = message.reply_to_message_id

    # admins = app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
    # admin_names = []
    # async for admin in admins:
    #     admin_names.append(admin.user)

    # for admin in admin_names:
    #     try:
    #         await app.send_message(admin.id, text=f"Reporte de @{message.from_user.username} a @{message.reply_to_message.from_user.username}:\n" + f'<a href="https://t.me/c/{chat_str_id}/{message_id}">https://t.me/c/{chat_str_id}/{message_id}</a>', parse_mode=enums.ParseMode.HTML)
    #         await app.forward_messages(admin.id, message.chat.id, message_id)
    #     except Exception as e:
    #         print(f"No se pudo enviar el mensaje a {admin.username}: {e}")

    try:
        await app.send_message(
            -1001664356911,
            text=f"Reporte de @{message.from_user.username} a @{message.reply_to_message.from_user.username}:\n" + f'<a href="https://t.me/c/{chat_str_id}/{message_id}">https://t.me/c/{chat_str_id}/{message_id}</a>', 
            parse_mode=enums.ParseMode.HTML,
            message_thread_id=82096
            )
        await app.forward_messages(-1001664356911, message.chat.id, message_id, message_thread_id=82096)
    except Exception as e:
        print(f"No se pudo enviar el mensaje de reporte a -1001664356911: {e}")