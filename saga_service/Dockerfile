# Utilise une image Python officielle
FROM python:3.11-slim

# Crée un dossier pour l'app
WORKDIR /app

# Copie les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose le port utilisé par Flask
EXPOSE 5000

# Commande pour démarrer l'app
CMD ["python", "app.py"]