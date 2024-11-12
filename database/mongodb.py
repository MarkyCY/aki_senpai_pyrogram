import os
import motor.motor_asyncio

from dotenv import load_dotenv
load_dotenv()

mongo_uri = os.getenv('MONGO_URI')
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)

async def get_db():
    return client.otakusenpai