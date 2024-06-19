from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from plugins.commands.admin.ban import BanUser, UnbanUser
from plugins.commands.admin.mute import MuteUser, UnmuteUser
from plugins.commands.admin.warn import add_warning, remove_warning
from plugins.commands.admin.colaborator import add_collaborator, remove_collaborator
from plugins.commands.admin.moderator import add_moderator, remove_moderator
from plugins.commands.info import info_command

from database.mongodb import get_db


@Client.on_callback_query(filters.regex(r"^info_\d{8,11}$"))
async def info_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    user_data = await app.get_chat_member(chat_id, user_mute_id)

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    await info_command(app, call.message, user_data.user)
    return

# region Ban y Mute
@Client.on_callback_query(filters.regex(r"^ban_\d{8,11}$"))
async def ban_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton(
                "✅Desbanear", callback_data=f"unban_{user_mute_id}"),
            InlineKeyboardButton(
                "ℹ️ Ver info", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    ban = await BanUser(app, chat_id, user_mute_id)
    if ban is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido baneado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido banear al usuario.")


@Client.on_callback_query(filters.regex(r"^mute_\d{8,11}$"))
async def mute_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton(
                "🔊Desilenciar", callback_data=f"unmute_{user_mute_id}"),
            InlineKeyboardButton(
                "ℹ️ Ver info", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    mute = await MuteUser(app, chat_id, user_mute_id)
    if mute is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido muteado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido mutear al usuario.")


@Client.on_callback_query(filters.regex(r"^unban_\d{8,11}$"))
async def unban_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton(
                "ℹ️ Ver info", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    unban = await UnbanUser(app, chat_id, user_mute_id)
    if unban is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido desbaneado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido desbanear al usuario.")


@Client.on_callback_query(filters.regex(r"^unmute_\d{8,11}$"))
async def unmute_user(app: Client, call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_mute_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    btns = [
        [
            InlineKeyboardButton(
                "ℹ️ Ver info", callback_data=f"info_{user_mute_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    unmute = await UnmuteUser(app, chat_id, user_mute_id)
    if unmute is True:
        await app.edit_message_text(chat_id, call.message.id, "El usuario ha sido desmuteado con exito.", reply_markup=markup)
    else:
        await app.answer_callback_query(call.id, "No se ha podido desmutear al usuario.")

# region Warn
@Client.on_callback_query(filters.regex(r"^warn_\d{8,11}$"))
async def warn_user(app: Client, call: CallbackQuery):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_warn_id = int(parts[1])

    chat_member = await app.get_chat_member(chat_id, user_warn_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        await app.answer_callback_query(call.id, "No puedes usar este comando con administradores.")
        return

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    user = await users.find_one({"user_id": user_warn_id})

    user_data = await app.get_chat_member(chat_id, user_warn_id)

    btns = []

    if 'warnings' in user:
        warnings = user['warnings']
    else:
        warnings = 0

    if warnings > 0:
        btns.append(InlineKeyboardButton(
            "-1 Warn", callback_data=f"remove_warn_{user_warn_id}"))
    if warnings < 3:
        btns.append(InlineKeyboardButton(
            "+1 Warn", callback_data=f"add_warn_{user_warn_id}"))

    btns = [btns]

    btns.append([InlineKeyboardButton(
        "ℹ️ Ver info", callback_data=f"info_{user_warn_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    await app.edit_message_text(chat_id, call.message.id, f"Usuario {user_data.user.first_name} [`{user_warn_id}`] tiene {warnings} warns.", reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^add_warn_\d{8,11}$"))
async def add_warn_user(app: Client, call: CallbackQuery):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    user_data = await app.get_chat_member(chat_id, user_sel_id)

    user = await users.find_one({"user_id": user_sel_id})

    btns = []

    if 'warnings' in user:
        warnings = user['warnings'] + 1
    else:
        warnings = 0

    if warnings > 0:
        btns.append(InlineKeyboardButton(
            "-1 Warn", callback_data=f"remove_warn_{user_sel_id}"))
    if warnings < 3:
        btns.append(InlineKeyboardButton(
            "+1 Warn", callback_data=f"add_warn_{user_sel_id}"))

    btns = [btns]

    btns.append([InlineKeyboardButton(
        "ℹ️ Ver info", callback_data=f"info_{user_sel_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    add_warn = await add_warning(app, chat_id, user_sel_id)

    if warnings == 3:
        await app.send_message(call.message.chat.id, add_warn)

    await app.answer_callback_query(call.id, add_warn)

    await app.edit_message_text(chat_id, call.message.id, f"Usuario {user_data.user.first_name} [`{user_sel_id}`] tiene {warnings} warns.", reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^remove_warn_\d{8,11}$"))
async def remove_warn_user(app: Client, call: CallbackQuery):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    user_data = await app.get_chat_member(chat_id, user_sel_id)

    user = await users.find_one({"user_id": user_sel_id})

    btns = []

    if 'warnings' in user:
        warnings = user['warnings'] - 1
    else:
        warnings = 0

    if warnings > 0:
        btns.append(InlineKeyboardButton(
            "-1 Warn", callback_data=f"remove_warn_{user_sel_id}"))
    if warnings < 3:
        btns.append(InlineKeyboardButton(
            "+1 Warn", callback_data=f"add_warn_{user_sel_id}"))

    btns = [btns]

    btns.append([InlineKeyboardButton(
        "ℹ️ Ver info", callback_data=f"info_{user_sel_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    remove_warn = await remove_warning(user_sel_id)

    await app.answer_callback_query(call.id, remove_warn)

    await app.edit_message_text(chat_id, call.message.id, f"Usuario {user_data.user.first_name} [`{user_sel_id}`] tiene {warnings} warns.", reply_markup=markup)

# region Roles
@Client.on_callback_query(filters.regex(r"^show_roles_\d{8,11}$"))
async def show_roles_user(app: Client, call: CallbackQuery, user_sel_id=None):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if user_sel_id is None:
        parts = call.data.split('_')
        user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    user_data = await app.get_chat_member(chat_id, user_sel_id)

    user = await users.find_one({"user_id": user_sel_id})

    mod = False
    col = False

    if "is_mod" in user:
        mod = user['is_mod']
    if "is_col" in user:
        col = user['is_col']

    mod_btn = [
        InlineKeyboardButton("Moderador", callback_data=f"info_col")
    ]

    col_btn = [
        InlineKeyboardButton("Colaborador", callback_data=f"info_mod")
    ]

    if mod is True:
        mod_btn.append(InlineKeyboardButton(
            "✅", callback_data=f"rem_mod_{user_sel_id}"))
    else:
        mod_btn.append(InlineKeyboardButton(
            "❌", callback_data=f"add_mod_{user_sel_id}"))
        
    if col is True:
        col_btn.append(InlineKeyboardButton(
            "✅", callback_data=f"rem_col_{user_sel_id}"))
    else:
        col_btn.append(InlineKeyboardButton(
            "❌", callback_data=f"add_col_{user_sel_id}"))

    btns = [mod_btn, col_btn]

    btns.append([InlineKeyboardButton(
        "ℹ️ Ver info", callback_data=f"info_{user_sel_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    await app.edit_message_text(chat_id, call.message.id, f"Roles del usuario {user_data.user.first_name} [`{user_sel_id}`].", reply_markup=markup)



@Client.on_callback_query(filters.regex(r"^info_col$"))
async def info_col(app: Client, call: CallbackQuery):
    return await app.answer_callback_query(call.id, "Usando el boton de al lado puedes modificar el rol de Colaborador.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^info_mod$"))
async def info_mod(app: Client, call: CallbackQuery):
    return await app.answer_callback_query(call.id, "Usando el boton de al lado puedes modificar el rol de Moderador.", show_alert=True)



@Client.on_callback_query(filters.regex(r"^rem_col_\d{8,11}$"))
async def rem_col_user(app: Client, call: CallbackQuery):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    rem_col = await remove_collaborator(user_sel_id)

    await show_roles_user(app, call, user_sel_id)

    await app.answer_callback_query(call.id, rem_col)
@Client.on_callback_query(filters.regex(r"^add_col_\d{8,11}$"))
async def add_col_user(app: Client, call: CallbackQuery):

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    add_col = await add_collaborator(user_sel_id)

    await show_roles_user(app, call, user_sel_id)

    await app.answer_callback_query(call.id, add_col)
    
@Client.on_callback_query(filters.regex(r"^rem_mod_\d{8,11}$"))
async def rem_mod_user(app: Client, call: CallbackQuery):

    db = await get_db()
    users = db.users

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    rem_col = await remove_moderator(user_sel_id)

    await show_roles_user(app, call, user_sel_id)

    await app.answer_callback_query(call.id, rem_col)
@Client.on_callback_query(filters.regex(r"^add_mod_\d{8,11}$"))
async def add_mod_user(app: Client, call: CallbackQuery):

    chat_id = call.message.chat.id
    user_id = call.from_user.id

    parts = call.data.split('_')
    user_sel_id = int(parts[2])

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() not in ['administrator', 'owner']:
        return await app.answer_callback_query(call.id, "No tienes permisos para usar este comando.")

    add_col = await add_moderator(user_sel_id)

    await show_roles_user(app, call, user_sel_id)

    await app.answer_callback_query(call.id, add_col)
    