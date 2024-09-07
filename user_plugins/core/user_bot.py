from pytgcalls import PyTgCalls
from pyrogram import Client

from dotenv import load_dotenv
load_dotenv()

import os

user_api_id = os.getenv('USER_API_ID')
user_api_hash = os.getenv('USER_API_HASH')

user_plugins = dict(root="user_plugins")

user_app = Client('user_bot', api_id=user_api_id, api_hash=user_api_hash, plugins=user_plugins)
pytgcalls = PyTgCalls(user_app)