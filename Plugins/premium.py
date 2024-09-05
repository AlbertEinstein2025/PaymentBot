from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from bot import Bot 
from pyrogram.types import InputMediaPhoto
import asyncio
from helper_func import *
from database.database import *
from Script import script
import pandas as pd
import openpyxl
import translation
import datetime
from fpdf import FPDF
import os
import requests
from pyrogram.types import ReplyKeyboardRemove

def download_image(image_url, local_filename):
    response = requests.get(image_url)
    with open(local_filename, 'wb') as f:
        f.write(response.content)

# Define the URL and local filename
image_url = 'https://graph.org/file/1b25775c841e6a3bffa1c.png'
local_filename = 'logo.png'

# Download the image
download_image(image_url, local_filename)

class PDF(FPDF):
    def header(self):
        # Add logo
        self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 102, 204)  # Dark blue color
        self.cell(0, 10, 'Payment Receipt', 0, 1, 'C')
        self.ln(20)  # Extra space after the title

    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)  # Gray color
        # Footer message
        self.cell(0, 10, 'Thank you for your payment!', 0, 0, 'C')

@Bot.on_message(filters.command("export") & filters.chat(OWNER_ID))
async def handle_export_payments(client, message):
    all_payments = used_utrs.find()

    payment_data = [payment for payment in all_payments]

    df = pd.DataFrame(payment_data)
    
    df = df.drop('_id', axis=1)

    if '_id' in df.columns:
        df = df.drop('_id', axis=1)
    df['UTR Number'] = df['UTR Number'].astype(str)

    # Apply formatting 
    def highlight_first_row(row):
        if row.name == 0:
            return ['background-color: lightgreen; font-weight: bold'] * len(row)
        else:
            return [''] * len(row)

    styled_df = df.style.apply(highlight_first_row, axis=1)
    styled_df = styled_df.set_properties(**{'text-align': 'center'})
    styled_df = styled_df.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])

    writer = pd.ExcelWriter("payments.xlsx", engine='openpyxl')
    styled_df.to_excel(writer, sheet_name='Payments', index=False)

    worksheet = writer.sheets['Payments']

    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)

        col_letter = openpyxl.utils.get_column_letter(col_idx + 1) 
        worksheet.column_dimensions[col_letter].width = column_length + 5

    writer.close()

    await message.reply_document("payments.xlsx")


@Bot.on_message(filters.command("start"))
async def start(client, message):
    id = message.from_user.id
    user_first_name = message.from_user.first_name
    bot_name = client.me.first_name
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    sticker_message = await message.reply_sticker("CAACAgUAAxkBAAJxl2bS6Qmo2EHxuHwXXTaAmNBgGjtyAALOCgAC32LpVMIQfTjljS_3NQQ", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(2.5)
    await sticker_message.delete()
    
    start_message = script.START_MESSAGE.format(user_first_name, bot_name) if user_first_name else script.START_MESSAGE2.format(bot_name)

    await message.reply_text(
        start_message,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('ᴛᴜᴛᴏʀɪᴀʟ♻️', url='https://t.me/YDUpdate/'),
                    InlineKeyboardButton('ᴀʙᴏᴜᴛ🤖', callback_data='about')
                ],
                [InlineKeyboardButton("✨ ᴄʜᴇᴄᴋ ᴘʟᴀɴs ✨", callback_data="premium_plans")]
            ]
        )
    )

# @Bot.on_callback_query(filters.regex(r'^help$'))
# async def help_callback(client, query):
#     await query.message.edit(
#         script.HELP_TXT.format(query.from_user.mention),
#         reply_markup=InlineKeyboardMarkup(
#             [
#                 [InlineKeyboardButton("💰 Buy Now", callback_data="buy_premium")],  # New callback for premium purchase
#                 [InlineKeyboardButton("🔙 Go Back", callback_data="back_to_start")]
#             ]
#         )
#     )

@Bot.on_callback_query(filters.regex(r'^about$'))
async def about_callback(client, query):
    await query.message.edit_text(
        script.ABOUT_TXT.format(client.me.first_name),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔙 Go Back", callback_data="back_to_start")]
            ]
        ),
        disable_web_page_preview=True
    )
@Bot.on_callback_query(filters.regex(r'^premium_plans$'))
async def premium_plans_callback(client, query):
    await query.message.edit(
        script.PREMIUM_PLANS.format(query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💰 Buy Now", callback_data="buy_premium")],  # New callback for premium purchase
                [InlineKeyboardButton("🔙 Go Back", callback_data="back_to_start")]
            ]
        )
    )

@Bot.on_callback_query(filters.regex(r'^buy_premium$'))
async def buy_premium(client, query):
    qr_code_url = "https://te.legra.ph/file/c752fe552eba09dd31cb0.jpg" 
    confirm_payment_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("🧾 Confirm Payment")],
            [KeyboardButton("🔙 Back")]
        ],
        resize_keyboard=True
    )

    await client.send_photo(
        query.message.chat.id,
        qr_code_url,
        caption=script.PAYMENT.format(query.from_user.mention),
        reply_markup=confirm_payment_keyboard
    )
    set_state(query.from_user.id, "waiting_for_utr")

@Bot.on_message(filters.regex("🧾 Confirm Payment") & filters.private & filters.incoming, group=2)
async def handle_confirm_payment(client, message):
    user_id = message.from_user.id
    
    if get_state(user_id) == "waiting_for_utr":
        cancel_keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("❌ Cancel")]
            ],
            resize_keyboard=True
        )
        retry_btn = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Try Again ♻️", callback_data="buy_premium")]
            ]
        )

        await message.reply_text("<b>Please enter 12 Digit UTR number or click 'Cancel' to go back:</b>", reply_markup=cancel_keyboard)

        set_state(user_id, "processing_payment")
        await asyncio.sleep(200)

        if get_state(user_id) == "processing_payment":
            reset_state(user_id)
            await message.reply_text("<b>Times up! please try again 😮‍💨</b>", reply_markup=ReplyKeyboardRemove())
            await message.reply_text("<b>Don't worry, no need to pay again. Just click on Try Again Button and send your UTR number again to verify the payment.</b>", reply_markup=retry_btn)

@Bot.on_message(filters.regex("❌ Cancel") & filters.private & filters.incoming, group=3)
async def handle_cancel(client, message):
    user_id = message.from_user.id
    if get_state(user_id) == "processing_payment":
        reset_state(user_id)
        await message.reply_text("<b>Verification cancelled.</b>", reply_markup=ReplyKeyboardRemove())
        await start(client, message)

@Bot.on_message(filters.regex("🔙 Back") & filters.private & filters.incoming, group=2)
async def handle_back(client, message):
    user_id = message.from_user.id

    if get_state(user_id):
        reset_state(user_id)

    await start(client, message) 
    # message = await message.reply_text("<b>Back</b>", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}") 

@Bot.on_message(filters.text & filters.private & filters.incoming, group=2)
async def handle_utr_input(client, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    if get_state(user_id) == "processing_payment":
        utr_input = message.text

        if not utr_input or not utr_input.isdigit():
            return

        verifying_message = await message.reply_text("<b>Verifying UTR number...<b>")

        if not utr_input.isdigit() or len(utr_input) != 12:
            await verifying_message.edit_text("<b>Invalid UTR. Please enter a 12-digit number.</b>")
            return

        utr = int(utr_input)
        back_keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("🔙 Back")]
            ],
            resize_keyboard=True
        )

        await message.delete()
        
        # if await is_utr_used(utr):
        #    await verifying_message.edit_text("<b>This UTR has already been used. Please provide a different UTR.</b>", reply_markup=back_keyboard)
        #    return
        verification_result = verify_payment(utr)

        if verification_result:
            amount = verification_result['amount']
            status = verification_result['status']
            payer = verification_result['payer']
            app = verification_result['app']

            if status == "SUCCESS":
                plan_messages = {
                    15: "✅ You have successfully subscribed to the 1-week plan!",
                    39: "✅ You have successfully subscribed to the 1-month plan!",
                    75: "✅ You have successfully subscribed to the 2-months plan!",
                    110: "✅ You have successfully subscribed to the 3-months plan!",
                    199: "✅ You have successfully subscribed to the 6-months plan!",
                    360: "✅ You have successfully subscribed to the 1-Year plan!"
                }
                plan_time_inputs = {
                    15: "7day",
                    39: "1month",
                    75: "2month",
                    110: "3month",
                    199: "6month",
                    360: "1year"
                }

                if amount in plan_messages:
                    time_input = plan_time_inputs[amount]
                    success_message = plan_messages[amount]

                    # Call give_premium to update the user's premium status
                    current_time_ist, new_expiry_time_ist = await give_premium(user_id, time_input)
                    print(f"{user_id} ..... {time_input}")

                    # Generate PDF receipt
                    pdf = PDF()
                    pdf_filename = f"payment_receipt_{utr}.pdf"
                    pdf.add_page()

                    # Title Section
                    pdf.set_font('Arial', 'B', 14)
                    pdf.set_fill_color(0, 153, 255)  # Light blue background
                    pdf.cell(0, 10, 'Payment Receipt', 0, 1, 'C', 1)
                    pdf.ln(10)

                    # Customer Information Section
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_fill_color(204, 204, 255)  # Light purple background
                    pdf.cell(0, 10, 'Customer Information', 0, 1, 'L', 1)
                    pdf.set_font('Arial', '', 12)
                    pdf.set_fill_color(255, 255, 255)  # White background for text
                    pdf.cell(0, 10, f'Customer Name: {username}', ln=True)
                    pdf.cell(0, 10, f'Telegram ID: {user_id}', ln=True)
                    pdf.ln(10)

                    # Transaction Details Section
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_fill_color(204, 255, 204)  # Light green background
                    pdf.cell(0, 10, 'Transaction Details', 0, 1, 'L', 1)
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(0, 10, f'Payer Name: {payer}', ln=True)
                    pdf.cell(0, 10, f'Payment Amount: {amount}', ln=True)
                    pdf.cell(0, 10, f'Transaction ID: {utr}', ln=True)
                    pdf.cell(0, 10, f'Transaction Date: {current_time_ist.strftime("%Y-%m-%d %H:%M:%S IST")}', ln=True)
                    pdf.cell(0, 10, f'Paid by App: {app}', ln=True)
                    pdf.ln(10)

                    # Item Table
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_fill_color(255, 204, 204)  # Light red background
                    pdf.cell(50, 10, 'Item', border=1, fill=True)
                    pdf.cell(50, 10, 'Validity (days)', border=1, fill=True)
                    pdf.cell(50, 10, 'Amount (INR)', border=1, fill=True, ln=True)

                    pdf.set_font('Arial', '', 12)
                    pdf.set_fill_color(255, 255, 255)  # White background for table cells
                    pdf.cell(50, 10, "Premium Subscription", border=1, fill=True)
                    pdf.cell(50, 10, time_input, border=1, fill=True)
                    pdf.cell(50, 10, str(amount), border=1, fill=True, ln=True)

                    # Save PDF
                    pdf.output(pdf_filename)

                    for admin_id in ADMINS:
                        try:
                            await client.send_message(
                                chat_id=admin_id,
                                text=f"<b>New premium user!\n\nUser ID: {user_id}\nPlan: {success_message}\n\n Player Name: {payer}\n\n Amount : ₹{amount}</b>"
                            )
                        except Exception as e:
                            print(f"Error sending notification to admin {admin_id}: {e}")

                    expiry_time = new_expiry_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')
                    if current_time_ist and new_expiry_time_ist:
                        VERIFY_Text = script.PAYMENT_VERIFIED.format(amount, payer, app, success_message, expiry_time)
                    else:
                        VERIFY_Text = script.PAYMENT_VERIFIED2.format(amount, payer, app, success_message)

                    await verifying_message.edit_text(VERIFY_Text)
                    user = await client.get_users(user_id)
                    username = user.username
                    subscription_type = "YD Premium Plans"
                    user_mention = user.mention
                    
                    await add_used_utr(subscription_type, payer, username, user_id, utr, amount)
                    await client.send_message(LOG_CHANNEL_ID, 
                        text=f"#Added_Premium\n\n"
                            f"👤 User: {user_mention}\n"
                            f"🎭 User ID: {user_id}\n"
                            f"⏰ Premium Access: {time_input}\n\n"
                            f"⏳ Joining Date: {current_time_ist.strftime('%d-%m-%Y')}\n"
                            f"⏱️ Joining Time: {current_time_ist.strftime('%I:%M:%S %p')}\n\n"
                            f"⌛️ New Expiry Date: {new_expiry_time_ist.strftime('%d-%m-%Y')}\n"
                            f"⏱️ New Expiry Time: {new_expiry_time_ist.strftime('%I:%M:%S %p')}\n", disable_web_page_preview=True
                    )
                    
                    # Step 4: Send PDF receipt to the user
                    with open(pdf_filename, 'rb') as pdf_file:
                        await client.send_document(user_id, pdf_file, caption="Here is your payment receipt.")
                    
                    # Clean up
                    if os.path.exists(pdf_filename):
                        os.remove(pdf_filename)

                    await message.reply_text("<b>Thank you so much for subscribing to Premium 💖</b>", reply_markup=ReplyKeyboardRemove())
                else:
                    await verifying_message.edit_text(f"<b>Incorrect payment amount.\n\n<blockquote>Amount : {amount}</blockquote>\n\n<blockquote>Payer Name : {payer}</blockquote>.\n\nPlease check the plan and contact Admin @Mr_SpidyBot.</b>")
            elif status == "FAILED":
                await verifying_message.edit_text("<b>Payment verification failed. Please check the UTR and try again.</b>", reply_markup=ReplyKeyboardRemove())
                await start(client, message)
            else:
                await verifying_message.edit_text("<b>An unexpected error occurred. Please try again later.</b>", reply_markup=ReplyKeyboardRemove())
                await start(client, message)
        else:
            await verifying_message.edit_text("<b>An error occurred while verifying the payment. Please try again later.</b>", reply_markup=ReplyKeyboardRemove())
            await start(client, message)

        reset_state(user_id)


@Bot.on_callback_query(filters.regex(r'^back_to_start$'))
async def back_to_start_callback(client, query):
    START_MESSAGE = f"""
<b>Hi {query.from_user.first_name}, 

Welcome to {client.me.first_name} 😊

We offer a variety of exclusive subscriptions to suit your interests.

Click below to browse our plans and unlock the premium experience! ✨</b>"""

    await query.message.edit_text(
        START_MESSAGE,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('ᴛᴜᴛᴏʀɪᴀʟ♻️', url='https://t.me/YDUpdate/'),
                    InlineKeyboardButton('ᴀʙᴏᴜᴛ🤖', callback_data='about')
                ],
                [InlineKeyboardButton("✨ ᴄʜᴇᴄᴋ ᴘʟᴀɴs ✨", callback_data="premium_plans")]
            ]
        )
    )

# @Bot.on_callback_query(filters.regex(r'^close_message$'))
# async def close_message_callback(client, query):
#     await query.message.delete()
