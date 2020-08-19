"""Core module for database related operations"""

from pryno.util import settings
import pymongo
import json
import os


class RyngoDB():
    def __init__(self):
        self.client = self.make_client()
        self.kollecta_db = self.make_client(db='kollecta').kollecta
        self.pryno_db = self.client.pryno
        self.user_db = getattr(self.client, settings.CLIENT_NAME)


    def make_client(self, db = 'rynotrove'):
        """Utility funciton to load MongoClient"""
        with open('pryno/database/mongo-credentials.json', 'r') as f:
            creds = json.load(f)
        client = pymongo.MongoClient(creds.get('conn-string-' + db))
        return client

    def register_user(self, user_tuple):
        self.client.pryno.users.insert_one(user_tuple)

    def capped_collection(self, coll_name, max_size = 50000000, db = 'user'):
        if db == 'pryno':
            self.pryno_db.create_collection(coll_name, capped=True, size=max_size)
        else:
            self.user_db.create_collection(coll_name, capped=True, size=max_size)

    def setup_collections(self):
        self.capped_collection('status')
        self.capped_collection('trade_history')
        self.capped_collection('profit_details')

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

    def insert_profit_details(self, profit_dict):
        self.user_db.profit_details.insert_one(profit_dict)

    def get_latest_instrument(self):
        self.kollecta_db.instrument.find_one(sort=[( '_id', pymongo.DESCENDING )])

    def get_latest_kstatus(self):
        self.kollecta_db.status.find_one(sort=[( '_id', pymongo.DESCENDING )])

    def get_latest_trade(self):
        self.kollecta_db.trade.find_one(sort=[( '_id', pymongo.DESCENDING )])


if __name__ == "__main__":
    mongo_client = RyngoDB()
    sample = dict(test=True)
    # mongo_client.capped_collection('test2', max_size=100000)
    # mongo_client.setup_collections()
    mongo_client.insert_status(sample)
