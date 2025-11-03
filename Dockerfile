# Dockerfile pour CoBitcoin WebApp + Bot Telegram
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier tous les fichiers
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir fastapi uvicorn aiohttp python-telegram-bot python-dotenv

# Exposer le port 8000 pour la web app
EXPOSE 8000

# Commande par défaut pour lancer le backend FastAPI
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
