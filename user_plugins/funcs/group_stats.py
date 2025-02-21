from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions

from database.mongodb import get_db
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import aiohttp
import os

imgbb_api = os.getenv('IMGBB_API')

class User(BaseModel):
    user_id: int
    first_name: str | None
    messages: int
    avg_chars: float

class Admin(BaseModel):
    user_id: int
    first_name: str | None
    deleted: int
    kicked: int
    banned: int

class Document(BaseModel):
    members: dict
    messages: dict
    viewers: dict
    posters: dict
    period: dict
    top_users: list[User]
    top_admins: list[Admin]

async def guardar_datos(stats):
    db = await get_db()
    Stats = db.stats

    users = []

    # Extraer los datos de stats
    current_members = stats.members.current
    previous_members = stats.members.previous

    current_messages = stats.messages.current
    previous_messages = stats.messages.previous

    current_viewers = stats.viewers.current
    previous_viewers = stats.viewers.previous

    current_posters = stats.posters.current
    previous_posters = stats.posters.previous
    
    min_date = stats.period.min_date
    max_date = stats.period.max_date

    #region Top posters
    top_posters = stats.top_posters
    sorted_posters = sorted(top_posters, key=lambda x: x.messages, reverse=True)[:30]

    # Crear un diccionario con los usuarios por su ID
    users_dict = {user.id: user for user in stats.users}

    # Lista para almacenar los resultados (top posters con sus mensajes y avg_chars)
    top_users_data = []

    # Recorrer los 20 usuarios top y buscar su first_name en stats.users
    for poster in sorted_posters:
        user_id = poster.user_id
        messages = poster.messages  # mensajes
        avg_chars = poster.avg_chars  # caracteres por mensaje
        user = users_dict.get(user_id)
        
        if user and not user.bot and user_id != 7201359400:  # Solo agregar si el usuario no es un bot
            # Añadir solo el nombre al resultado junto con mensajes y avg_chars
            users.append(user.id)
            top_users_data.append({
                "user_id": user.id,
                "first_name": user.first_name,
                "messages": messages,
                "avg_chars": avg_chars
            })
    
    #region Top admins
    top_admins = stats.top_admins
    sorted_admins = sorted(top_admins, key=lambda x: x.deleted, reverse=True)
    
    top_admins_data = []

    for admin in sorted_admins:
        user_id = admin.user_id
        deleted = admin.deleted
        kicked = admin.kicked
        banned = admin.banned
        user = users_dict.get(user_id)

        if user and not user.bot and user_id != 7201359400:  # Solo agregar si el usuario no es un bot y no es otaku radio
            # Añadir solo el nombre al resultado junto con mensajes y avg_chars
            if user.id not in users:
                users.append(user.id)
            top_admins_data.append({
                "user_id": user.id,
                "first_name": user.first_name,
                "deleted": deleted,
                "kicked": kicked,
                "banned": banned
            })

    
    # Crear el documento a insertar
    document_data = Document(
        members={
            "current": current_members,
            "previous": previous_members
        },
        messages={
            "current": current_messages,
            "previous": previous_messages
        },
        viewers={
            "current": current_viewers,
            "previous": previous_viewers
        },
        posters={
            "current": current_posters,
            "previous": previous_posters
        },
        period={
            "min_date": min_date,
            "max_date": max_date
        },
        top_users=top_users_data,
        top_admins=top_admins_data
    )
    await Stats.update_one({"_id": "status_daily"}, {"$set": document_data.dict()}, upsert=True)
    return users

async def async_post_image(url, params, image_path):
    async with aiohttp.ClientSession() as session:
        with open(image_path, 'rb') as file:
            data = {'image': file}
            async with session.post(url, params=params, data=data) as response:
                return await response.json()


@Client.on_message(filters.command("stats"))
async def stats_show(app: Client, message: Message = None):
    print("Guardando estadísticas")
    db = await get_db()
    Users = db.users
    if message:
        await message.reply_text("Cargando...")
    stats = await app.invoke(functions.stats.GetMegagroupStats(
            channel= await app.resolve_peer(-1001485529816)
        ))
    
    users = await guardar_datos(stats)

    user_list = await app.get_users(users)

    for user in user_list:
        print("download phto", user.first_name)
        try:
            photo_download = await app.download_media(user.photo.small_file_id, file_name="user_photo.jpg")
            url = "https://api.imgbb.com/1/upload"
            params = {
                "key": imgbb_api,
            }
            response = await async_post_image(url, params, photo_download)

            usr_sel = await Users.find_one({"user_id": user.id})

            if usr_sel is None:
                continue
        except:
            continue

        await Users.update_one({"user_id": user.id}, {"$set": {"avatar": response["data"]["url"]}})
        print(response["data"]["url"])
        
    print("Finish Stats")


# 1 validation error for Document
# top_users.0.first_name
#   Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
#     For further information visit https://errors.pydantic.dev/2.7/v/string_type
# Traceback (most recent call last):
#   File "/home/ubuntu/akira/venv/lib/python3.11/site-packages/pyrogram/dispatcher.py", line 414, in handler_worker
#     await handler.callback(self.client, *args)
#   File "/home/ubuntu/akira/user_plugins/funcs/group_stats.py", line 160, in stats_show
#     users = await guardar_datos(stats)
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/ubuntu/akira/user_plugins/funcs/group_stats.py", line 114, in guardar_datos
#     document_data = Document(
#                     ^^^^^^^^^
#   File "/home/ubuntu/akira/venv/lib/python3.11/site-packages/pydantic/main.py", line 176, in __init__
#     self.__pydantic_validator__.validate_python(data, self_instance=self)
# pydantic_core._pydantic_core.ValidationError: 1 validation error for Document
# top_users.0.first_name
#   Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
#     For further information visit https://errors.pydantic.dev/2.7/v/string_type