"""Core module for database related operations"""

from pryno.util import settings
import pymongo
import json
import os

def get_client():
    """Utility funciton to load MongoClient"""

    # load credentials
    with open('mongo-credentials.json', 'r') as f:
        creds = json.load(f)
    client = pymongo.MongoClient(creds.get('conn-string'))
    return client

def register_client(user_tuple):
    client = get_client()
    client.pryno.users.insert_one(user_tuple)

if __name__ == "__main__":
    register_client(dict(pussy="vagina"))
