API_HASH = "e490b538a8edddec7367959ca407e7ad"

API_ID = 20707655

BOT_TOKEN = "7281069995:AAGyURd154T-hJ3YxGOMvzkzBEFyy0NKNqE"

# ADMINS = [1276033190 1053777957]
try:
    ADMINS=[]
    for x in ("1276033190 1053777957".split()): 
        ADMINS.append(int(x))
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

DB_URI = "mongodb+srv://dextin:zaxscd123@leakedjalwa.9yauwbt.mongodb.net/?retryWrites=true&w=majority&appName=LeakedJalwa"

DB_NAME = "YDPaymentBot"

OWNER_ID = 1276033190

LOG_CHANNEL_ID = -1002086314209 # Log Channel to store user premium data

SECONDDB_URI = "mongodb+srv://spidy:MongoDB1432@cluster1.ssqidl2.mongodb.net/?retryWrites=true&w=majority"
DATABASE_URI = "mongodb+srv://Spidy:MongoDB1432@autofilter.zqu7rr3.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "YourDemandZone"
COLLECTION_NAME = 'YourDemandZone'

tempDict = {'indexDB': DATABASE_URI}
