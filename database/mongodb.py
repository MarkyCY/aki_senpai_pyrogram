import os
from pymongo import MongoClient

def get_db():
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    return client.otakusenpai