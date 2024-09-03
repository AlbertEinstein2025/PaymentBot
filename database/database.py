import sys
import pymongo, os
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
used_utrs = database['used_utrs']

async def is_utr_used(utr):
    found = used_utrs.find_one({'UTR Number': utr})
    return bool(found)

async def add_used_utr(subscription_type, payer, username, user_id, utr, amount):
    """
    Adds a UTR to the used_utrs collection along with user_id and username.

    Args:
        utr: The UTR to add.
        user_id: The Telegram user ID associated with the UTR.
        username: The Telegram username associated with the UTR (or None if not available).
    """
    used_utrs.insert_one({
        'Subscription Type': subscription_type,
        'Name': payer,
        'Username': username,
        'User ID': user_id,
        'UTR Number': utr,
        'Amount': amount,
        
    })

async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return
