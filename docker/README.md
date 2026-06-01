# Eventry Docker Folder

## Etapes de construction des Dockerfiles

### Backend Dockerfile
Ce dockerfile a été construit de base sans IA, après quelques recherches sur la [documentation officielle](https://docs.docker.com/build/concepts/dockerfile/) et la visualisation de vidéos youtube sur la création de Dockerfile.

````Image de base
# Image de base du containeur
FROM python:3.10-slim

# Répertoir de travail du containeur
WORKDIR /app

# Installation des dépendances
RUN apt-get update && apt-get install -y

# Copie uniquement le requirement pour optimiser le cache
COPY requirements.txt .
RUN pip isntall -r requirements.txt

# Le reste du code sera monté via le docker-compose.yml
COPY . .

# Expostion du port
EXPOSE 8000

# Lancement automatique de l'API
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]
````

### Utilisation de l'IA
Nous avons utilisé un LLM (Gemini) pour vérifier si notre dockerfile était complet et comment l'optimiser avec justification afin d'avoir un Dockerfile **production-ready**.

```Image optimisé
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
```
### Documentation sur l'utilisation de l'IA
La politque d'utilisation de l'IA sur cette partie est documentée dans le fichier `ia_logs_backend_dockerfile.md`.  


---
---
### Frontend Dockerfile
Le Dockerfile de base à été construit sans IA, avec nos connaissans et recherches effectuées. Bien que fonctionnel, ce dernier pésait plusieurs megaoctets et n'était pas optimisé.

```Image docker de base
# Image de base du containeur
FROM node:18-alpine

# Repertoire de travail du containeur
WORKDIR /app

# Copie uniquement le package.jon pour optimiser le cache
COPY package*.json .
RUN npm install

# Copie du reste du repertoire
COPY . .

# Exposition du port
EXPOSE 5173

# Lancement automatique du containeur
CMD [ "npm", "run", "dev", "--", "--host" ]
```
### Utilisation de l'IA
Nous avons utilisé un LLM (Gemini) pour vérifier si notre dockerfile était complet et comment l'optimiser avec justification afin d'avoir un Dockerfile **production-ready**.

```Image optimisée
# --- STAGE 1: Build Stage ---
FROM node:18-alpine AS builder

WORKDIR /app

# Optimisation du cache pour les dépendances
COPY package*.json ./
RUN npm ci --quiet

# Copie du code et build de l'application
COPY . .
RUN npm run build

# --- STAGE 2: Runtime Stage (L'image finale) ---
FROM nginx:stable-alpine

# On récupère uniquement les fichiers statiques compilés
# (Note: Le dossier 'dist' est le standard pour Vite)
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Documentation sur l'utilisation de l'IA
La politque d'utilisation de l'IA sur cette partie est documentée dans le fichier `ia_logs_frontend_dockerfile.md`.  