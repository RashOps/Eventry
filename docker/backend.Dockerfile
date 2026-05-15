# --- STAGE 1: Builder ---
FROM python:3.10-slim AS builder

WORKDIR /app

# Installation des dépendances système nécessaires pour les drivers DB (PostgreSQL notamment)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Inclusion du backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- STAGE 2: Final Image ---
FROM python:3.10-slim

WORKDIR /app

# Récupération des binaires compilés depuis le builder
COPY --from=builder /install /usr/local

# Installation de libpq pour PostgreSQL (nécessaire à l'exécution)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Sécurité : Création d'un utilisateur non-root
RUN addgroup --system appuser && adduser --system --group appuser
USER appuser

# CORRECTIF : Copie uniquement le contenu du dossier backend, pas toute la racine
COPY ./backend .

# Configuration des variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
