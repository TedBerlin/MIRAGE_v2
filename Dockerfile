FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p data/raw_documents data/processed data/cache data/output

# Exposition des ports
EXPOSE 8005

# Variables d'environnement
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Commande de démarrage
CMD ["python", "web_interface.py"]