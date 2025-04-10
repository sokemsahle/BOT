import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Constants for URLs
REQUISITION_URL = 'https://a118375.socialsolutionsportal.com/apricot-intake/0aaaa575-68a7-49c6-a295-ab071f04531f'
MY_APRICOT_URL = 'https://apricot.socialsolutions.com/bulletins/list'
FOSTER_FORM_URL = 'https://docs.google.com/document/d/1PJvVw1tUMcw1tM1YUq0joJ3qQym5UbI_/edit?usp=sharing&ouid=106277595220510562770&rtpof=true&sd=true'
OVERTIME_CALCULATOR_URL = 'https://v0-overtime-pay-calculator-sahlesokem-gmailcoms-projects.vercel.app'  # Replace with your actual link
PASSWORD = "13579"

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🚗 Driver Log Form", url="https://a118375.socialsolutionsportal.com/apricot-intake/507c7ab5-2953-4272-b586-77401b98693d")],  # Driver Log Form button
        [InlineKeyboardButton("📄 Requisition Form", url=REQUISITION_URL)],
        [InlineKeyboardButton("📂 My Apricot", url=MY_APRICOT_URL)],
        [InlineKeyboardButton("📞 Important Phone Numbers", callback_data='Important phone numbers')],
        [InlineKeyboardButton("📧 Important Emails", callback_data='Emails')],
        [InlineKeyboardButton("📝 Foster Family Care Agreement Form", url=FOSTER_FORM_URL)],
        [InlineKeyboardButton("🕒 Overtime Calculator", callback_data='overtime_calculator')],  # Password-protected button
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(
        '*Welcome!*\n\nPlease choose an option from the menu below:',
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    # Track both user and bot messages
    context.user_data.setdefault('messages', []).extend([message.message_id, update.message.message_id])

async def dynamic_menu(update: Update, context: CallbackContext) -> None:
    """Send a dynamic menu to the user."""
    keyboard = [
        [InlineKeyboardButton("📄 Requisition Form", url=REQUISITION_URL)],
        [InlineKeyboardButton("📂 My Apricot", url=MY_APRICOT_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Here is the dynamic menu:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'Important phone numbers':
        message = await query.edit_message_text(
            text="📞 *Important Phone Numbers:*\n\n"
                 "• 0904002403 - Talya Restaurant\n"
                 "• 0993008851 - Social Worker",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == 'Emails':
        message = await query.edit_message_text(
            text="📧 *Important Emails:*\n\n"
                 "• sokem@shamidaethiopia.com\n"
                 "• hello@shamidaethiopia.com",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == 'overtime_calculator':
        # Ask for a password
        await query.edit_message_text(
            text="🔒 *Password Required:*\n\nPlease enter the password to access the Overtime Calculator.",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['awaiting_password'] = True  # Set a flag to await password input
    elif query.data == 'clean_messages':
        for message_id in context.user_data.get('messages', []):
            try:
                await query.message.chat.delete_message(message_id)
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")
        context.user_data['messages'] = []  # Clear the list of message IDs
        return
    # Track the edited message
    context.user_data.setdefault('messages', []).append(query.message.message_id)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages, including password input."""
    if context.user_data.get('awaiting_password'):
        password = update.message.text
        if password == PASSWORD:  # Check if the password is correct
            await update.message.reply_text(
                text=f"✅ Access Granted! [Click here to open the Overtime Calculator]({OVERTIME_CALCULATOR_URL})",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Respond with incorrect password message
            error_message = await update.message.reply_text(
                text="❌ Incorrect password. Please try again."
            )
            # Delete the user's message and the bot's error message
            try:
                await update.message.delete()  # Delete the user's message
                await error_message.delete()  # Delete the bot's error message
            except Exception as e:
                print(f"Failed to delete messages: {e}")
        context.user_data['awaiting_password'] = False  # Reset the flag
    else:
        await update.message.reply_text("I didn't understand that command.")

async def clear(update: Update, context: CallbackContext) -> None:
    """Command to clear all messages sent during the interaction and restart."""
    chat_id = update.message.chat_id
    # Add the user's message to the tracked messages
    context.user_data.setdefault('messages', []).append(update.message.message_id)
    for message_id in context.user_data.get('messages', []):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            # Log the error and continue
            if "message to delete not found" in str(e).lower():
                print(f"Message {message_id} already deleted or not found.")
            else:
                print(f"Failed to delete message {message_id}: {e}")
    context.user_data['messages'] = []  # Clear the list of message IDs

    # Restart by calling the start function
    await start(update, context)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', dynamic_menu))  # Add the dynamic menu command
    application.add_handler(CommandHandler('clear', clear))  # Add the clear command
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle password input

    application.run_polling()

if __name__ == '__main__':
    main()