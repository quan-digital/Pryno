"""Core module for database related operations"""

from pryno.util import settings
import pymongo
import json
import os


class RyngoDB():
    def __init__(self):
        self.client = self.make_client()
        self.kollecta_db = self.client.kollecta
        self.pryno_db = self.client.pryno
        self.user_db = getattr(self.client, settings.CLIENT_NAME)


    def make_client(self):
        """Utility funciton to load MongoClient"""
        with open('mongo-credentials.json', 'r') as f:
            creds = json.load(f)
        client = pymongo.MongoClient(creds.get('conn-string'))
        return client

    def register_user(self, user_tuple):
        self.client.pryno.users.insert_one(user_tuple)

    def capped_collection(self, coll_name, max_size = 100000, db = 'user'):
        if db == 'pryno':
            self.pryno_db.create_collection(coll_name, capped=True, size=max_size)
        else:
            self.user_db.create_collection(coll_name, capped=True, size=max_size)





if __name__ == "__main__":
    mongo_client = RyngoDB()
    # mongo_client.capped_collection('test2', max_size=100000)
