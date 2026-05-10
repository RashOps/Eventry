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