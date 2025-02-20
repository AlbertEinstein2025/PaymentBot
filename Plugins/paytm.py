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

async def send_qr_code(client, user_id, amount):
    qr_url, txn_id = generate_qr(user_id, amount)

    if qr_url:
        message = await client.send_photo(
            chat_id=user_id,
            photo=qr_url,
            caption=(
                "Please pay using the above QR CODE.\n\n"
                "The QR Code will expire in 5 minutes, so make sure to pay within that time.\n"
                "Payment will be automatically verified after the payment."
            ),
        )

        # Store the message ID for deletion
        qr_message_id = message.message_id  

        # Start the verification process in the background
        asyncio.create_task(verify_payment_later(client, qr_message_id, txn_id, user_id, amount))

        # Delete the QR code after 5 minutes if payment is not verified
        async def delete_qr_after_delay():
            await asyncio.sleep(300)  # Wait for 5 minutes
            try:
                print(f"Deleting QR message {qr_message_id} for user {user_id}")  # Debugging
                await client.delete_messages(user_id, qr_message_id)
            except Exception as e:
                print(f"Error deleting QR code message: {e}")

        asyncio.create_task(delete_qr_after_delay())  # Run deletion in the background

    else:
        await client.send_message(user_id, "❌ Failed to generate QR Code. Please try again later.")

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
        self.cell(0, 10, 'Grp Username: @YDMovieZone2', 0, 1, 'R')
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

async def paytm_automation(client, message, txn_id, user_id, amount):
    
    if await is_txnid_used(txn_id):
        await client.delete_messages(user_id, qr_message_id)
        await client.send_message(
            chat_id=user_id,
            text="<b>This QR has already been used, Thank You</b>"
        )
        return

    verification_result = await verify_txn_id(txn_id)
    if verification_result:
        status, utr = verification_result['status'], verification_result['utr']
        

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

               # Initialize PDF
                pdf = PDF()
                pdf.add_page()

                # Add border
                pdf.add_border()

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
                pdf.cell(0, 10, f'Payment Amount: ₹{amount}', ln=True)
                pdf.cell(0, 10, f'Transaction ID: {utr}', ln=True)
                pdf.cell(0, 10, f'Transaction Date: {current_time_ist.strftime("%Y-%m-%d %H:%M:%S IST")}', ln=True)
                pdf.ln(10)

                # Item Table
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(255, 204, 204)  # Light red background
                pdf.set_text_color(0, 0, 0)  # Black text
                pdf.cell(50, 10, 'Item', border=1, fill=True)
                pdf.cell(50, 10, 'Validity (days)', border=1, fill=True)
                pdf.cell(50, 10, 'Amount (INR)', border=1, fill=True, ln=True)

                pdf.set_font('Arial', '', 12)
                pdf.set_fill_color(255, 255, 255)  # White background for table cells
                pdf.cell(50, 10, "Premium Subscription", border=1, fill=True)
                pdf.cell(50, 10, time_input, border=1, fill=True)
                pdf.cell(50, 10, str(amount), border=1, fill=True, ln=True)

                # Save PDF
                pdf_filename = f"payment_receipt_{user_id}.pdf"
                pdf.output(pdf_filename)

                # Send Confirmation Message
                expiry_time = new_expiry_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')
                if current_time_ist and new_expiry_time_ist:
                    VERIFY_Text = script.PAYTM_VERIFIED.format(amount, success_message, expiry_time)
                else:
                    VERIFY_Text = script.PAYTM_VERIFIED2.format(amount, success_message)

                await client.send_message(
                    chat_id=user_id,
                    text=VERIFY_Text
                )
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

                # Step 4: Send PDF receipt to the user
                with open(pdf_filename, 'rb') as pdf_file:
                    await client.send_document(user_id, pdf_file, caption="Here is your payment receipt.")
                
                # Clean up
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)

            else:
                await message.edit_text(f"❌ Incorrect payment amount: ₹{amount}\nPlease contact @Mr_SpidyBot.")
        else:
            await message.edit_text("❌ Payment verification failed. Please check and try again.")

@Bot.on_callback_query(filters.regex(r'^paytm_premium$'))
async def paytm_premium(client, query):
    await query.message.edit_text("<b>Loading PayTM plans...</b>")

    await asyncio.sleep(1)  # Small delay to avoid flickering issues

    choose_plan = script.CHOOSE_PLAN
    await query.message.edit_text(
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
    amount = int(query.matches[0].group(1))  # Extract amount from callback data
    user_id = query.from_user.id

    # Delete the plan selection message
    await query.message.delete()

    # Generate QR Code
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

        # Verify payment asynchronously
        asyncio.create_task(verify_payment_later(client, verifying_message, txn_id, user_id, amount))

    else:
        await query.answer("❌ Failed to generate QR Code. Please try again later.", show_alert=True)

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
        # Stop verify_payment_later since payment is successful
        await stop_verify_payment_later(user_id)

        await paytm_automation(client, query.message, txn_id, user_id, amount)

    elif verification_result.get("status") == "FAILED":
        await query.answer("❌ Payment not found or not completed. Please try again later.", show_alert=True)

    else:
        await query.answer("❌ Payment verification failed. Contact support if the issue persists.", show_alert=True)

verify_tasks = {}  # Dictionary to store running verification tasks

async def verify_payment_later(client, message, txn_id, user_id, amount):
    max_attempts = 10 
    last_status = None  

    for attempt in range(max_attempts):
        await asyncio.sleep(30)  # Wait for 1 minute before checking

        verification_result = await verify_txn_id(txn_id)
        if verification_result:
            status = verification_result['status']

            if status == "SUCCESS":
                await paytm_automation(client, message, txn_id, user_id, amount)
                verify_tasks.pop(txn_id, None)  # Cleanup
                return  # Stop further checks

            last_status = status  

    # After 5 minutes, send failure message and stop verification
    if last_status == "FAILED":
        await client.send_message(user_id, "<b>Payment not found or failed. Please try again.</b>")
    else:
        await client.send_message(user_id, "<b>Payment not received within 5 minutes. Please try again.</b>")

    asyncio.create_task(stop_verify_payment_later(txn_id))  # Run in background

    verify_tasks.pop(txn_id, None)  # Cleanup

async def stop_verify_payment_later(txn_id):
    """Cancel verification task if needed."""
    task = verify_tasks.pop(txn_id, None)
    if task and not task.done():
        task.cancel()

