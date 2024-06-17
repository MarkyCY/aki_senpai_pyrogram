from database.mongodb import get_db

async def isAdmin(user_id):
    db = await get_db()
    chat_admins = db.admins

    isAdmin = None
    admins = chat_admins.find()
    async for admin in admins:
        if admin['user_id'] == user_id:
            isAdmin = "Yes"
    return isAdmin

async def isModerator(user_id):
    db = await get_db()
    users = db.users

    isModerator = False
    Users = users.find({"is_mod": True})
    async for user in Users:
        if user['user_id'] == user_id:
            isModerator = True
    return isModerator

async def isCollaborator(user_id):
    db = await get_db()
    users = db.users

    isCollaborator = False
    Users = users.find({"is_col": True})
    async for user in Users:
        if user['user_id'] == user_id:
            isCollaborator = True
    return isCollaborator
