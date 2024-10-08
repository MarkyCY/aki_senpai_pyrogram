from pyrogram import Client
from pyrogram import enums

from database.mongodb import get_db

async def add_user(user_id, id):
    # Conectar a la base de datos
    db = await get_db()
    contest = db.contest

    # Consulta para seleccionar el documento a actualizar
    filter = {'_id': id}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$push': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = await contest.update_one(filter, update)

    return result

async def del_user(user_id, id):
    # Conectar a la base de datos
    db = await get_db()
    contest = db.contest

    # Consulta para seleccionar el documento a actualizar
    filter = {'_id': id}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$pull': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = await contest.update_one(filter, update)

    return result

async def disq_user(user_id, id):
    # Conectar a la base de datos
    db = await get_db()
    contest = db.contest

    filter = {'_id': id}

    update = {'$push': {'disqualified': {'user': user_id}}}
    
    result = await contest.update_one(filter, update)

    return result

async def un_disq_user(user_id, id):
    # Conectar a la base de datos
    db = await get_db()
    contest = db.contest

    filter = {'_id': id}

    update = {'$pull': {'disqualified': {'user': user_id}}}
    
    result = await contest.update_one(filter, update)

    return result

async def reg_user(user_id, username):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    await users.insert_one({"user_id": user_id, "username": username})

async def send_data_contest(JUECES, text, markup, img=None):
    for item in JUECES:
        try:
            if img:
                await Client.send_photo(chat_id=item, photo=img, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
            else:
                await Client.send_message(chat_id=item, text=text, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
        except Exception as err:
            print(f"{err}, {item}")