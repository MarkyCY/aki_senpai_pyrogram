import motor.motor_asyncio
import datetime
import os

mongo_uri = os.getenv('MONGO_URI')
Limit = os.getenv('LIMIT_USE')

class UseControlMongo:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client["otakusenpai"]
        self.collection = self.db["count_use"]

    async def verif_limit(self, user_id):
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        user_key = {"user_id": user_id, "date": today_str}
        user_record = await self.collection.find_one(user_key)

        if user_record is None:
            user_record = {"user_id": user_id, "date": today_str, "count": 0}
            await self.collection.insert_one(user_record)

        return user_record["count"] < int(Limit)

    async def reg_use(self, user_id):
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        user_key = {"user_id": user_id, "date": today_str}
        await self.collection.update_one(user_key, {"$inc": {"count": 1}}, upsert=True)