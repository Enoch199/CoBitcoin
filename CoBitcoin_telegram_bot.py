import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import asyncio

BOT_TOKEN = os.getenv("COBITCOIN_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_USER_ID", "")
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_ACCOUNT_ID = os.getenv("COINBASE_ACCOUNT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur CoBitcoin Bot !\n\nCommandes disponibles :\n/claim - Chercher des Bitcoin gratuits\n/account - Voir ton solde\n/withdraw - Retirer vers ton portefeuille\n/referral - Gagner plus avec ton lien")

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Recherche de Bitcoin gratuits en cours (2 min)...")
    await asyncio.sleep(10)  # simulation rapide
    await update.message.reply_text("✅ 0.00001000 BTC trouvés et ajoutés à ton compte !")

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Solde actuel : 0.00001000 BTC")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ Envoie ton adresse Bitcoin pour retirer tes gains.")
    # Ici tu peux ajouter la logique d'envoi réel via Coinbase API

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    ref_link = f"https://t.me/CoBitcoinBot?start={username}"
    await update.message.reply_text(f"👥 Ton lien de parrainage :\n{ref_link}\n\nInvite 3 amis avant de retirer !")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("claim", claim))
app.add_handler(CommandHandler("account", account))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("referral", referral))

print("✅ Bot CoBitcoin en ligne...")
app.run_polling()
