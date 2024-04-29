import os
import motor.motor_asyncio

async def get_db():
    client = motor.motor_asyncio.AsyncIOMotorClient("127.0.0.1", 27017)
    return client.otakusenpai
