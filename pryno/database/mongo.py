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

    def setup_collections(self):
        self.capped_collection('status')
        self.capped_collection('exec')
        self.capped_collection('wallet')

    def insert_status(self, status_dict):
        self.user_db.status.insert_one(status_dict)

    def insert_exec(self, exec_dict):
        self.user_db.exec.insert_one(exec_dict)

    def insert_wallet(self, wallet_dict):
        self.user_db.wallet.insert_one(wallet_dict)

    def insert_billing(self, bill_dict):
        self.user_db.billing.insert_one(bill_dict)

    def insert_profit(self, profit_dict):
        self.user_db.profit.insert_one(profit_dict)




if __name__ == "__main__":
    mongo_client = RyngoDB()
    sample = dict(test=True)
    # mongo_client.capped_collection('test2', max_size=100000)
    # mongo_client.setup_collections()
    # mongo_client.insert_status(sample)
    # mongo_client.insert_exec(sample)
    # mongo_client.insert_wallet(sample)
    # mongo_client.insert_billing(sample)
    # mongo_client.insert_profit(sample)

    
