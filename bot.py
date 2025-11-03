# --------------------- bot.py sécurisé avec .env ---------------------
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os

# Charger les variables depuis .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")

if BOT_TOKEN is None:
    raise ValueError("Erreur: TELEGRAM_BOT_TOKEN non défini dans le fichier .env")

def start(update: Update, context: CallbackContext):
    msg = f"Bienvenue ! Cliquez ici pour accéder à votre compte Quotex et voir les signaux : {WEBAPP_URL}"
    update.message.reply_text(msg)

if __name__ == '__main__':
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

# --------------------- Instructions ---------------------
# 1. Installer python-dotenv: pip install python-dotenv
# 2. Créer un fichier .env à la racine du projet:
#    TELEGRAM_BOT_TOKEN=TON_TOKEN_REEL
#    WEBAPP_URL=http://adresse_de_ton_serveur:8000
# 3. Ajouter .env dans .gitignore pour ne pas le pousser sur GitHub
# 4. Lancer le bot: python bot.py
