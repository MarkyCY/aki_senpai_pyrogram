from database.mongodb import get_db

async def set_afk(message):
    # Conectar a la base de datos
    db = await get_db()
    users = db.users

    user_id = message.from_user.id
    args = message.text.split(" ", 1)
    notice = ""
    
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nSu motivo de afk se redujo a 100 caracteres."
    else:
        reason = ""

    # Actualizar MongoDB
    await users.update_one(
        {"user_id": user_id},
        {"$set": {"is_afk": True, "reason": reason}},
        upsert=True
    )

    fname = message.from_user.first_name
    res = "{} ahora está AFK!{}".format(fname, notice)

    await message.reply_text(text=res)

