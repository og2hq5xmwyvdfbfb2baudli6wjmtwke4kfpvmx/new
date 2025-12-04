import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8247238867:AAFegzRzyLUkK5CHVK535L4ZshwHxXsCHVo"
ADMIN_ID = 6541825979
USDT_ADDRESS = "TUmPVgYgFSw2cSigkCS276Rxxomm9mvdAh"
MIN_DEPOSIT = 50.0
RATE = 0.40

# =========================
# USER DATABASE (IN MEMORY)
# =========================
users = {}  # user_id -> {"username": str, "balance": float, "active": bool}

logging.basicConfig(level=logging.INFO)


# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # Create database entry if not exists
    if uid not in users:
        users[uid] = {
            "username": user.username,
            "balance": 0.0,
            "active": False
        }

    msg = f"""
👋 Hello **{user.first_name}!**

Welcome to our official virtual credit service.

💠 We offer **Digital Virtual Credits**  
💠 Rate: **$0.40 = 1 Credit**  
💠 Minimum deposit to activate: **${MIN_DEPOSIT}**

After activation you can:
- Buy credits  
- Use premium tools  
- Check balance  
- Unlock full bot access  

Choose an option below:
"""

    buttons = [
        [InlineKeyboardButton("💳 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("📊 My Balance", callback_data="balance")],
        [InlineKeyboardButton("ℹ️ Rate Info", callback_data="rate")]
    ]

    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )


# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "deposit":
        await query.edit_message_text(
            f"""
💳 **Deposit Instructions**

To activate your account, send at least **${MIN_DEPOSIT}**.

Send **USDT (TRC20)** to:

`{USDT_ADDRESS}`

After payment, send the screenshot to Admin.

👨‍💼 **Admin Contact:**  
@mdabi_admin
            """,
            parse_mode="Markdown"
        )

    elif query.data == "balance":
        balance = users[user_id]["balance"]
        status = "Active ✅" if users[user_id]["active"] else "Not Active ❌"

        await query.edit_message_text(
            f"""
📊 **Your Account Status**

Status: **{status}**  
Balance: **${balance:.2f}**

Minimum Deposit: **${MIN_DEPOSIT}**
Rate: **$0.40 = 1 Credit**
            """,
            parse_mode="Markdown"
        )

    elif query.data == "rate":
        await query.edit_message_text(
            f"""
💱 **Credit Rate Information**

➡️ **$1 = 2.5 Credits**  
➡️ **1 Credit = $0.40**

Examples:
- $10 → 25 Credits  
- $50 → 125 Credits

Credits allow access to premium tools and digital services.
            """,
            parse_mode="Markdown"
        )


# =========================
# ADMIN: ADD BALANCE
# =========================
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addbalance user_id amount")
        return

    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid format.")
        return

    if user_id not in users:
        await update.message.reply_text("User not found.")
        return

    users[user_id]["balance"] += amount

    # Activate account automatically if balance reaches minimum
    if users[user_id]["balance"] >= MIN_DEPOSIT:
        users[user_id]["active"] = True

    await update.message.reply_text(
        f"Added **${amount:.2f}** to user {user_id}.\n"
        f"New Balance: **${users[user_id]['balance']:.2f}**",
        parse_mode="Markdown"
    )


# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addbalance", add_balance))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
