from database.mongodb import get_db
import datetime
from pyrogram import utils
import re

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

def get_until_date(time):
    match_duration = re.match(r'^(\d+)([dhm])$', time) if time else None
    reason = time if match_duration else None
    until_date = utils.zero_datetime()
    if reason:
        match = re.match(r'^(\d+)([dhm])$', reason)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit == 'h':
                until_date = datetime.datetime.now() + datetime.timedelta(hours=num)
            elif unit == 'd':
                until_date = datetime.datetime.now() + datetime.timedelta(days=num)
            elif unit == 'm':
                until_date = datetime.datetime.now() + datetime.timedelta(minutes=num)
                
    return until_date

async def role(app, chat_id, user_id):
    db = await get_db()
    users = db.users

    role = None
    admin = None

    Users = await users.find_one({"user_id": user_id})
    if 'role' in Users:
        role = Users['role']

    chat_member = await app.get_chat_member(chat_id, user_id)
    role_name = str(chat_member.status).split('.')[1]
    if role_name.lower() in ['administrator', 'owner']:
        admin = True
        
    return role, admin