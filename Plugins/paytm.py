from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from bot import Bot 
from pyrogram.types import InputMediaPhoto
import asyncio
from helper_func import *
from database.database import *
from Script import script
from config import PDF_LOGO
import translation
import datetime
from fpdf import FPDF
import os
import requests
import json

def generate_qr(user_id, amount):
    url = f"https://api.ispidy.com/paytm/qr_generator.php?id={user_id}&amount={amount}"
    response = requests.get(url).json()

    if response.get("success"):
        return response["qr_url"], response["txn_id"]
    return None, None

def send_qr_code(client, user_id, amount):  # Add `client` as an argument
    qr_url, txn_id = generate_qr(user_id, amount)

    if qr_url:
        client.send_photo(  # Use `client` instead of `bot`
            chat_id=user_id,
            photo=qr_url,
            caption=f"Please pay on the above QR CODE.\n\n"
                    f"The QR Code will expire in 5 minutes, so make sure to pay within 5 minutes.\n"
                    f"Payment will be automatically verified after the payment.",
        )
        start_verification(txn_id, user_id)
    else:
        client.send_message(user_id, "Failed to generate QR Code. Please try again later.")

def download_image(image_url, local_filename):
    response = requests.get(image_url)
    with open(local_filename, 'wb') as f:
        f.write(response.content)

imgage_url = PDF_LOGO
local_filename = 'logo.jpg'
download_image(imgage_url, local_filename)

class PDF(FPDF):
    def header(self):
        # Add logo
        self.image('logo.jpg', 10, 8, 20, 20)
        
        # Add the header text
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 0, 0)  # Red color
        self.cell(0, 10, 'YD Premium', 0, 1, 'C')
        self.ln(6)

        # Add text to the top right
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)  # Black color
        
        # Calculate X position to align text to the right
        page_width = self.w - 10  # Leave some margin from the right
        self.set_xy(page_width - 70, 8)  # Adjust X and Y position

        # Print the right-aligned text
        self.cell(0, 10, 'Group Name: YD Movie Zone', 0, 1, 'R')
        self.set_xy(page_width - 70, 13)
        self.cell(0, 10, 'Grp Username: @YDMovieZone', 0, 1, 'R')
        self.set_xy(page_width - 70, 18)
        self.cell(0, 10, 'Contact us: @Mr_SpidyBot', 0, 1, 'R')
        self.ln(6)
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'B', 11)
        self.set_text_color(128, 128, 128)
        # Footer message
        self.cell(0, 10, 'Thank you for your payment!', 0, 0, 'C')

    def add_border(self):
        # Add a border around the entire page
        self.set_draw_color(0, 102, 204)  # Dark blue color for the border
        self.set_line_width(1)  # Border thickness
        # Draw the border (x, y, width, height)
        self.rect(5, 5, self.w - 10, self.h - 10)

    def add_section_box(self, title, color):
        # Add a colored background box for a section title
        self.set_fill_color(*color)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.set_font('Arial', '', 12)
        self.set_fill_color(255, 255, 255)  # Reset to white for content


async def verify_txn_id(txn_id):
    url = f"https://api.ispidy.com/paytm/verify.php?txn_id={txn_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        amount = data.get('amount')
        status = data.get('status')
        utr = data.get('utr')

        if amount is None:
            return {"status": "FAILED", "message": "Payment not found or not completed."}

        try:
            amount = int(float(amount))
        except ValueError:
            return {"status": "FAILED", "message": "Invalid amount received."}

        return {
            'amount': amount,
            'status': status,
            'utr': utr
        }

    except requests.exceptions.RequestException as e:
        print(f"Error verifying payment: {e}")
        return {"status": "ERROR", "message": str(e)}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {"status": "ERROR", "message": "Invalid JSON response."}

async def generate_pdf_receipt(user_id, amount, txn_id, current_time_ist):

    pdf = PDF
    # Title Section
    pdf.set_font('Arial', 'B', 18)
    pdf.set_fill_color(255, 0, 0)  # Red background
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.cell(0, 15, 'Payment Receipt', 0, 1, 'C', 1)
    pdf.ln(10)

    # Customer Information Section
    pdf.add_section_box('Customer Information', (204, 204, 255))  # Light purple background
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(0, 10, f'Customer Name: N/A', ln=True)
    pdf.cell(0, 10, f'Telegram ID: {user_id}', ln=True)
    pdf.ln(10)

    # Transaction Details Section
    pdf.add_section_box('Transaction Details', (204, 255, 204))  # Light green background
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(0, 10, f'Payment Amount: {amount}', ln=True)
    pdf.cell(0, 10, f'Transaction ID: {txn_id}', ln=True)
    pdf.cell(0, 10, f'Transaction Date: {current_time_ist.strftime("%Y-%m-%d %H:%M:%S IST")}', ln=True)
    pdf.ln(10)

    # Save PDF
    pdf_filename = f"payment_receipt_{user_id}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

async def paytm_automation(client, message, txn_id, user_id, amount):
    verification_result = await verify_txn_id(txn_id)

    if verification_result:
        print(f"DEBUG: txn_id={txn_id}, user_id={user_id}, amount={amount}, verification_result={verification_result}")
        status = verification_result['status']

        if status == "SUCCESS":
            plan_messages = {
                1: "✅ You have successfully subscribed to the 1-day plan!",
                2: "✅ You have successfully subscribed to the 2-day plan!",
                3: "✅ You have successfully subscribed to the 3-day plan!"
            }
            plan_time_inputs = {
                1: "1day",
                2: "2day",
                3: "3day"
            }

            if amount in plan_messages:
                time_input = plan_time_inputs[amount]
                success_message = plan_messages[amount]

                # Activate Premium Plan
                current_time_ist, new_expiry_time_ist = await give_premium(user_id, time_input)

                # Generate PDF Receipt
                pdf_filename = await generate_pdf_receipt(user_id, amount, txn_id, current_time_ist)

                # Send Confirmation Message
                expiry_time = new_expiry_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')
                VERIFY_Text = script.PAYTM_VERIFIED.format(amount, success_message, expiry_time)

                await message.edit_text(VERIFY_Text)
                await client.send_document(user_id, pdf_filename, caption="Here is your payment receipt.")

                # Notify Admins
                user = await client.get_users(user_id)
                user_mention = user.mention
                for admin_id in ADMINS:
                    try:
                        await client.send_message(
                            chat_id=admin_id,
                            text=f"<b><u>New premium user!</u>\n\nUser: {user_mention}\n"
                                 f"User ID: <a href='tg://openmessage?user_id={user_id}'>{user_id}</a>\n"
                                 f"Amount: ₹{amount}\nPlan: {success_message}</b>"
                        )
                    except Exception as e:
                        print(f"Error sending notification to admin {admin_id}: {e}")

                # Log Payment
                await add_used_txnid("YD Premium Plans", user.username, user_id, txn_id, amount)

                # Send Thank You Message
                await client.send_message(user_id, "<b>Thank you so much for subscribing to Premium 💖</b>")

                # Cleanup
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)
            else:
                await message.edit_text(f"❌ Incorrect payment amount: ₹{amount}\nPlease contact @Mr_SpidyBot.")
        else:
            await message.edit_text("❌ Payment verification failed. Please check and try again.")

@Bot.on_callback_query(filters.regex(r'^paytm_premium$'))
async def paytm_premium(client, query):
    choose_plan = script.CHOOSE_PLAN
    await query.message.reply_text(
        choose_plan,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('₹1 = 1 day', callback_data='paytm_1')],
                [InlineKeyboardButton('₹2 = 2 days', callback_data='paytm_2')],
                [InlineKeyboardButton('₹3 = 3 days', callback_data='paytm_3')],
            ]
        )
    )

@Bot.on_callback_query(filters.regex(r'^paytm_(\d+)$'))
async def generate_qr_code(client, query):
    amount = int(query.matches[0].group(1))
    user_id = query.from_user.id

    url = f"https://api.ispidy.com/paytm/qr_generator.php?id={user_id}&amount={amount}"
    response = requests.get(url).json()

    if response.get("success"):
        qr_url = response["qr_url"]
        txn_id = response["txn_id"]

        verifying_message = await query.message.reply_photo(
            photo=qr_url,
            caption=f"Please pay using the above QR CODE.\n\n"
                    f"The QR Code will expire in 5 minutes, so make sure to pay within 5 minutes.\n"
                    f"Payment will be **automatically verified** after the payment.\n\n"
                    f"🔹 If you've already paid, click the **Payment Done** button below.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Payment Done", callback_data=f"verify_{txn_id}_{user_id}_{amount}")]]
            )
        )

        # ✅ Corrected parameter for verify_payment_later
        asyncio.create_task(verify_payment_later(client, verifying_message, txn_id, user_id))

    else:
        await query.answer("Failed to generate QR Code. Please try again later.", show_alert=True)

@Bot.on_callback_query(filters.regex(r'^verify_(\S+)_(\d+)_(\d+)$'))
async def manual_payment_verification(client, query):
    txn_id, user_id, amount = query.matches[0].groups()
    user_id, amount = int(user_id), int(amount)

    if not txn_id:  # Ensures txn_id is valid
        await query.answer("❌ Invalid Transaction ID. Please try again.", show_alert=True)
        return

    verification_result = await verify_txn_id(txn_id)

    if not verification_result:
        await query.answer("❌ Error verifying payment. Please try again later.", show_alert=True)
        return

    if verification_result.get("status") == "SUCCESS":
        await paytm_automation(client, query.message, txn_id, user_id, amount)
    elif verification_result.get("status") == "FAILED":
        await query.answer("❌ Payment not found or not completed. Please try again later.", show_alert=True)
    else:
        await query.answer("❌ Payment verification failed. Contact support if the issue persists.", show_alert=True)


async def verify_payment_later(client, message, txn_id, user_id, amount):
    max_attempts = 5  # Check up to 5 times (every 1 minute)
    last_status = None  # Track the last payment status

    for attempt in range(max_attempts):
        await asyncio.sleep(60)  # Wait for 1 minute

        verification_result = await verify_txn_id(txn_id)
        if verification_result:
            status = verification_result['status']

            if status == "SUCCESS":
                await paytm_automation(client, message, txn_id, user_id, amount)
                return  # Stop further checks

            last_status = status  # Update last known status

    # After 5 minutes, decide the final message based on the last status
    if last_status == "FAILED":
        await client.send_message(user_id, "<b>Payment failed. Please try again.</b>")
    elif last_status:  # Only send if some status was received
        await client.send_message(user_id, "<b>Payment not received within 5 minutes. Please try again.</b>")

    # Delete the QR message
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete QR message: {e}")
