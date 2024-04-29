import os
import motor.motor_asyncio

async def get_db():
    mongo_uri = os.getenv('MONGO_URI')
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    try:
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client.otakusenpai
