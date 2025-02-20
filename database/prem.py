import datetime
import pytz
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import * 

client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]

#direct importing from utils causing loop, directly added here so no error should come.
def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:]

        if value:
            value = int(value)

        return value, unit

async def get_seconds(time_string):
    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0

class Database:
    
    def __init__(self):
        self.col = mydb.users
        self.users = mydb.uersz      

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )
    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        """
        Check if the user has premium access across all databases.
        """
        user_data_list = await self.get_user(user_id)
        
        for user_data in user_data_list:
            if user_data:
                expiry_time = user_data.get("expiry_time")
                if expiry_time:
                    if isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                        return True
                    else:
                        # Expiry time exists but has passed; reset it
                        await self.col.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False

    async def remove_premium_access(self, user_id):
        """Remove premium access for the user from all databases."""
        # Flag to check if any update was made
        updated = False

        # List of collections to iterate over
        collections = [self.users]

        for collection in collections:
            result = await collection.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
            # If any collection updates successfully, set the flag to True
            if result.modified_count > 0:
                updated = True

        return updated

db = Database()
