from pyrogram import utils
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message, InlineKeyboardButton, InlineKeyboardMarkup

#from database.mongodb import get_db
from plugins.others.admin_func import get_until_date
from plugins.others.admin_func import isModerator

group_perm = [-1001485529816, -1001664356911]

async def MuteUser(app, chat_id, user_id, message=None, name=None, until_date=utils.zero_datetime()):
    # Configurar los permisos de restricción (mutear al usuario)
    permissions = ChatPermissions(
        can_send_messages = False,
        can_send_audios = False,
        can_send_documents = False,
        can_send_photos = False,
        can_send_videos = False,
        can_send_video_notes = False,
        can_send_voice_notes = False,
        can_send_polls = False,
        can_send_other_messages = False,
        can_add_web_page_previews = False,
        can_change_info = False,
        can_invite_users = False,
        can_pin_messages = False,
        can_manage_topics = False,
        can_send_media_messages = False
        )

    # Obtener la fecha de expiración
    if until_date == utils.zero_datetime():
        muted_till = "Indefinido"
    else:
        muted_till = until_date.strftime("%d/%m/%Y %I:%M %p")

    # Mutear al usuario
    try:
        await app.restrict_chat_member(chat_id, user_id, permissions, until_date=until_date)
    except Exception as e:
        print(e)
        return False
    
    if message:
        btns = [
            [
                InlineKeyboardButton(
                    "🔊Desilenciar", callback_data=f"unmute_{user_id}"),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=btns)
        await message.reply(f"El usuario {name} ha sido muteado hasta: `{muted_till}`.", reply_markup=markup)

    return True

async def UnmuteUser(app, chat_id, user_id, name=None, message=None):
    # Configurar los permisos de restricción (desmutear al usuario)
    permissions = ChatPermissions(
        can_send_messages = True,
        can_send_audios = True,
        can_send_documents = True,
        can_send_photos = True,
        can_send_videos = True,
        can_send_video_notes = True,
        can_send_voice_notes = True,
        can_send_polls = True,
        can_send_other_messages = True,
        can_add_web_page_previews = True,
        can_change_info = True,
        can_invite_users = True,
        can_pin_messages = True,
        can_manage_topics = True,
        can_send_media_messages = True
        )

    # Desmutear al usuario
    try:
        await app.restrict_chat_member(chat_id, user_id, permissions)
    except Exception as e:
        print(e)
        return False

    if message:
        await message.reply(f"El usuario {name} ha sido desmuteado.")
        return
    
    return True

@Client.on_message(filters.command('mute'))
async def mute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    until_date = utils.zero_datetime()
    if not message.reply_to_message and message.command and len(message.command) > 1:
        elemento = message.command[1]
        
        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user_mute_id = get_user.user.id
            name = get_user.user.first_name
            if len(message.command) > 2:
                time = message.command[2]
                until_date = get_until_date(time)
            

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user_mute_id = get_user.user.id
                name = get_user.user.first_name
                if len(message.command) > 2:
                    time = message.command[2]
                    until_date = get_until_date(time)
    
    elif not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas mutear.")
        return
    
    else:
        user_mute_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name
        
        if message.command and len(message.command) > 1:
            time = message.command[1]
            until_date = get_until_date(time)

    # Obtener la ID del chat
    chat_id = message.chat.id
    user_id = message.from_user.id

    isMod = await isModerator(user_id)

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner'] and isMod is False:
        return await message.reply("No tienes permisos para usar este comando.")

    if role_name.lower() in ['administrator', 'owner']:
        chat_member = await app.get_chat_member(chat_id, user_mute_id)
        role_name = str(chat_member.status).split('.')[1]
        if role_name.lower() in ['administrator', 'owner']:
            await message.reply("No puedes usar este comando con administradores.")
            return

        await MuteUser(app, chat_id, user_mute_id, message=message, name=name, until_date=until_date)
        return
    
    #Moderadores de Otaku Senpai en otros grupos
    if chat_id not in group_perm:
        return await message.reply("No tienes permisos para usar este comando.")
    
    chat_member = await app.get_chat_member(chat_id, user_mute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return

    btns = [
        [
            InlineKeyboardButton(
                "🔇Silenciar", callback_data=f"mod_mute_{user_mute_id}_{user_id}"),
        ]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    return await message.reply("Es necesario que otro moderador o administrador apoye esta acción.", reply_markup=markup)

@Client.on_message(filters.command('unmute'))
async def unmute_command(app: Client, message: Message):
    # Asegúrate de que el comando sea respondido a un mensaje
    if not message.reply_to_message and message.command and len(message.command) > 1:
        elemento = message.command[1]

        # Si el elemento es un ID de usuario
        if elemento.isdigit() and 8 <= len(elemento) <= 11:
            user_id = int(elemento)
            get_user = await app.get_chat_member(message.chat.id, user_id)
            user_unmute_id = get_user.user.id
            name = get_user.user.first_name

        # Si el elemento es un nombre de usuario
        elif elemento.startswith('@'):
                username = elemento.replace('@', '')
                get_user = await app.get_chat_member(message.chat.id, username)
                user_unmute_id = get_user.user.id
                name = get_user.user.first_name
    
    elif not message.reply_to_message:
        await message.reply("Por favor, responde al mensaje del usuario que deseas mutear.")
        user_unmute_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name
        return
    
    else:
        user_unmute_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name

    # Obtener la ID del chat
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        await message.reply("No tienes permisos para usar este comando.")
        return

    chat_member = await app.get_chat_member(chat_id, user_unmute_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await message.reply("No puedes usar este comando con administradores.")
        return
    
    await UnmuteUser(app, chat_id, user_unmute_id, name, message)