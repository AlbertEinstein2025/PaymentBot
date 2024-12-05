import requests
import json
from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges
from pyrogram.errors import exceptions, FloodWait, UserAlreadyParticipant
from config import *
from bot import Bot

from datetime import datetime, timedelta
import pytz
from database.prem import db

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

async def give_premium(user_id, time_input):
    seconds_to_add = await get_seconds(time_input)

    if seconds_to_add > 0:
        current_time = datetime.utcnow()

        # Get the user's current expiry time from the database
        user_data, user_data2, user_data3 = await db.get_user(user_id)  # Unpack the tuple

        # Choose which user_data to use based on your logic
        # For example, prioritize the first database if data exists there
        relevant_user_data = user_data or user_data2  or user_data3

        current_expiry_time = relevant_user_data.get("expiry_time") if relevant_user_data else None

        if current_expiry_time and current_expiry_time > current_time:
            # User has remaining premium time, so add to the remaining time
            new_expiry_time = current_expiry_time + timedelta(seconds=seconds_to_add)
        else:
            # No remaining premium time, so set expiry to now + new duration
            new_expiry_time = current_time + timedelta(seconds=seconds_to_add)

        # Update the expiry time in the database
        user_data = {"id": user_id, "expiry_time": new_expiry_time}
        await db.update_user(user_data)

        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = current_time.astimezone(ist)
        new_expiry_time_ist = new_expiry_time.astimezone(ist)

        return current_time_ist, new_expiry_time_ist  # Return the times for later use
    else:
        return None, None  # Return None if invalid time format

def verify_payment(utr):

    url = f"https://0dns.me/Bharatpe/verify.php?token=e889275ce91a4c26b6ec898b514d44f7&txn_id={utr}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse JSON response
        data = json.loads(response.text)

        # Return a dictionary with the amount and status
        return {
            'amount': data.get('amount'),
            'status': data.get('status'),
            'payer': data.get('payer'),
            'app': data.get('app')
        }
    except requests.exceptions.RequestException as e:
        print(f"Error verifying payment: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None

CURRENT_STATE = {}

def get_state(user_id):
    return CURRENT_STATE.get(user_id)

def set_state(user_id, state):
    CURRENT_STATE[user_id] = state

def reset_state(user_id):
    if user_id in CURRENT_STATE:
        del CURRENT_STATE[user_id]



def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time
