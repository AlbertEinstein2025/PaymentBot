import os

class script(object):
    START_MESSAGE = """
<b>Hi {},

Welcome to {} 😊

<blockquote>We offer a variety of exclusive subscriptions to suit your interests.

Click below to browse our plans and unlock the premium experience! ✨</blockquote></b>"""

    START_MESSAGE2 = """
<b>Hi, 

Welcome to {} 😊

<blockquote>We offer a variety of exclusive subscriptions to suit your interests.

Click below to browse our plans and unlock the premium experience! ✨</blockquote></b>"""


    ABOUT_TXT = """<b>
🤖 Mʏ Nᴀᴍᴇ : {}
😎 Cʀᴇᴀᴛᴏʀ : <a href='https://t.me/Mr_SPIDY'>⚝𝗠𝗿.𝗦𝗣𝗜𝗗𝗬⚝</a>

<blockquote>Tʜɪꜱ ɪꜱ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ᴘᴀʏᴍᴇɴᴛ ᴠᴇʀɪғɪᴇʀ + ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇʀ ʙᴏᴛ.

Jᴜꜱᴛ ᴍᴀᴋᴇ ᴀ ᴘᴀʏᴍᴇɴᴛ ᴀɴᴅ ᴠᴇʀɪғʏ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ᴠɪᴀ ᴘʀᴏᴠɪᴅɪɴɢ ʏᴏᴜʀ ᴛʀᴀɴꜱᴄᴀᴛɪᴏɴ UTR ID ɴᴜᴍʙᴇʀ.

Aғᴛᴇʀ ᴄᴏᴍᴘʟᴇᴛɪᴏɴ ᴏғ ᴘᴀʏᴍᴇɴᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ, Iᴛ ᴡɪʟʟ ᴅɪʀᴇᴄᴛʟʏ ᴀᴅᴅᴇᴅ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄ ᴏɴ ʙᴏᴛʜ Bᴏᴛꜱ @YDAutoBot & @EvaMariaXbot.

Fᴏʀ ᴀɴʏ ǫᴜᴇʀɪᴇꜱ ᴍꜱɢ: @Mr_SpidyBot

🛠️ A ᴘʀᴏᴊᴇᴄᴛ ʙʏ <a href='https://t.me/YourDemandZone'>YᴏᴜʀDᴇᴍᴀɴᴅZᴏɴᴇ ⚡️</a></b>"""

    PREMIUM_PLANS = """
<b>👋 ʜᴇʏ {},

<blockquote>🎖️ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ :</blockquote>
 ❏ 𝟶𝟷𝟻₹    ➠    𝟶𝟷 ᴡᴇᴇᴋꜱ
 ❏ 𝟶𝟹𝟿₹    ➠    𝟶𝟷 ᴍᴏɴᴛʜ
 ❏ 𝟶𝟽𝟻₹    ➠    𝟶𝟸 ᴍᴏɴᴛʜ
 ❏ 𝟷𝟷𝟶₹    ➠    𝟶𝟹 ᴍᴏɴᴛʜ
 ❏ 𝟷𝟿𝟿₹    ➠    𝟶𝟼 ᴍᴏɴᴛʜ
 ❏ 𝟹𝟼𝟶₹    ➠    𝟷𝟸 ᴍᴏɴᴛʜ

Cʜᴏᴏꜱᴇ ᴀɴʏ ᴘʟᴀɴ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ᴅᴇꜱɪʀᴇ.
Tʜᴀɴᴋ ʏᴏᴜ! 💝</b>"""

    PAYMENT = """
<b>👋 ʜᴇʏ {},

<blockquote><u>Tᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ʏᴏᴜʀ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ:</u>

𝟷. Scan the QR Code or copy the UPI ID Below.
𝟸. Make your payment.
𝟹. Send UTR number to confirm.
𝟺. Premium will directly added to you acc.</blockquote>

🆔 UPI ID: 
`bharatpe.8p0y0j5O2k82600@fbpe` (Tap to copy)</b>"""

    PAYMENT_VERIFIED = """
<b>🎉 Payment Verified! 🎉

<blockquote>Amount Received: ₹{}
Payer: {}</blockquote>

<blockquote>{}

🥳 Congratulations! Your premium subscription is now active on Both Bots until {new_expiry_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')}. ✨</blockquote>

To Check Your Plan: Go to Both Bot and send /myplan for getting subscription info.⚡️</b>"""

    PAYMENT_VERIFIED2 = """
<b>🎉 Payment Verified! 🎉

Amount Received: ₹{}
Payer: {}

{}

There was an error activating your premium subscription. Please contact the admin @Mr_SpidyBot.

To Check Your Plan: Go to Bot and send /myplan for subscription info.⚡️</b>"""