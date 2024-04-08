import os
import motor.motor_asyncio

async def get_db():
    mongo_uri = os.getenv('MONGO_URI')
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    return client.otakusenpai
