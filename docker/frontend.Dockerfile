# --- STAGE 1: Build Stage ---
FROM node:22-alpine AS builder

WORKDIR /app

# Optimisation du cache pour les dépendances
COPY frontend/package*.json ./
RUN npm install

# Copie du code et build de l'application
COPY ./frontend .
RUN npm run build

# --- STAGE 2: Runtime Stage (L'image finale) ---
FROM nginx:stable-alpine

# Copier la configuration Nginx pour les SPA (Single Page Applications)
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copie uniquement les fichiers statiques compilés (dist est le standard pour Vite)
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
