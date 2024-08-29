# Utilise une image de base officielle Python
FROM python:3.12

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier de dépendances dans le répertoire de travail
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie l'intégralité du code de l'application dans le répertoire de travail
COPY . .

# Expose le port sur lequel l'application va tourner
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "app:main:app", "--host", "0.0.0.0", "--port", "8000"]