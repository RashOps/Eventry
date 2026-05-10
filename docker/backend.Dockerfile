# --- STAGE 1: Builder ---
FROM python:3.10-slim AS builder

WORKDIR /app

# Installation des dépendances système nécessaires pour les drivers DB (PostgreSQL notamment)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python dans un répertoire local
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- STAGE 2: Final Image ---
FROM python:3.10-slim

WORKDIR /app

# On récupère les binaires compilés du builder
COPY --from=builder /install /usr/local

# Installation de libpq pour PostgreSQL (nécessaire à l'exécution)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Sécurité : Création d'un utilisateur non-root
RUN addgroup --system appuser && adduser --system --group appuser
USER appuser

# Copie du code
COPY . .

# Configuration des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Commande de lancement (Optimisée pour la prod, surchargeable via docker-compose pour le dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]