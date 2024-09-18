API_HASH = "d58456be9931f3f6b8154a626fc1b3c6"

API_ID = 25412293

BOT_TOKEN = "7281069995:AAH6WTlC1uIX6xP_Qn_S-gVJkiM3YZyE_Z0"

QR_CODE = "https://te.legra.ph/file/c752fe552eba09dd31cb0.jpg" 

PDF_LOGO = 'https://envs.sh/qua.png'

try:
    ADMINS=[]
    for x in ("2006425984 1053777957".split()): 
        ADMINS.append(int(x))
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

DB_URI = "mongodb+srv://dextin:zaxscd123@leakedjalwa.9yauwbt.mongodb.net/?retryWrites=true&w=majority&appName=LeakedJalwa"

DB_NAME = "YDPaymentBot"

OWNER_ID = 1053777957

LOG_CHANNEL_ID = -1002086314209 # Log Channel to store user premium data

SECONDDB_URI = "mongodb+srv://spidy:MongoDB1432@cluster1.ssqidl2.mongodb.net/?retryWrites=true&w=majority"
DATABASE_URI = "mongodb+srv://Spidy:MongoDB1432@autofilter.zqu7rr3.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "YourDemandZone"
COLLECTION_NAME = 'YourDemandZone'

tempDict = {'indexDB': DATABASE_URI}
