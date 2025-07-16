import logging
import json
import os
import qrcode
from io import BytesIO
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID
from cloudflare_manager import generate_subdomain, create_subdomain, get_random_clean_ip
from marzban_manager import login_admin, get_user, update_user_sni, build_v2ray_link

# Persistent user mapping: telegram_id -> marzban_username
USER_MAPPING_FILE = "user_mapping.json"

logging.basicConfig(level=logging.INFO)

def load_user_mapping():
    if not os.path.isfile(USER_MAPPING_FILE):
        return {}
    with open(USER_MAPPING_FILE, "r") as f:
        return json.load(f)

def save_user_mapping(mapping):
    with open(USER_MAPPING_FILE, "w") as f:
        json.dump(mapping, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! This bot automates V2Ray connection repair.\n"
        "Use /help for instructions."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/register [marzban_username]: Link your Telegram account.\n"
        "/fix_connection: Repair your V2Ray config."
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /register [marzban_username]")
        return
    marzban_username = args[0]
    telegram_id = str(update.effective_user.id)
    user_mapping = load_user_mapping()
    user_mapping[telegram_id] = marzban_username
    save_user_mapping(user_mapping)
    await update.message.reply_text(f"Registered Marzban username: {marzban_username}")

async def fix_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    user_mapping = load_user_mapping()
    marzban_username = user_mapping.get(telegram_id)
    if not marzban_username:
        await update.message.reply_text("Please register first using /register [marzban_username]")
        return
    # Step 1: Clean IP
    clean_ip = get_random_clean_ip()
    # Step 2: New subdomain
    subdomain = generate_subdomain()
    fqdn = create_subdomain(subdomain)
    # Step 3: Marzban config update
    token = login_admin()
    user_config = get_user(token, marzban_username)
    update_user_sni(token, marzban_username, fqdn)
    # Step 4: Send config
    v2ray_link = build_v2ray_link(user_config, clean_ip, fqdn)
    await update.message.reply_text(f"Your new V2Ray link:\n{v2ray_link}")
    # Bonus: QR code
    img = qrcode.make(v2ray_link)
    bio = BytesIO()
    bio.name = "qrcode.png"
    img.save(bio, "PNG")
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption="Scan this QR code to import.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("fix_connection", fix_connection))
    app.run_polling()

if __name__ == "__main__":
    main()
