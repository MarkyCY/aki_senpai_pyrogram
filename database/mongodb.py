import os
import motor.motor_asyncio
from pymongo.server_api import ServerApi

async def get_db():
    mongo_uri = os.getenv('MONGO_URI')
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, server_api=ServerApi('1'))
    try:
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client.otakusenpai
