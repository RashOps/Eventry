# Utilisation d'Ubuntu 22.04
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Installation des outils de base
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    supervisor \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Ajout des dépôts officiels pour PostgreSQL 15 et MongoDB 6.0
# Ubuntu 22.04 n'a que Postgres 14 par défaut
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# 3. Installation des bases de données
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    mongodb-org \
    && rm -rf /var/lib/apt/lists/*

# 4. Installation de UV pour la gestion Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

# 5. Configuration de l'utilisateur Hugging Face (UID 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user
WORKDIR $HOME/app

# Création des répertoires de données et permissions
RUN mkdir -p /var/lib/postgresql/data /var/lib/mongodb /var/run/postgresql /tmp \
    && chown -R user:user /var/lib/postgresql /var/lib/mongodb /var/run/postgresql /tmp /etc/postgresql

# 6. Copie des fichiers du projet
COPY --chown=user:user . .

# 7. Installation des dépendances Python
RUN uv pip install --system --no-cache -r backend/requirements.txt

# 8. Scripts de configuration
RUN chmod +x entrypoint.sh start_fastapi.sh
USER user

# Port exposé par Hugging Face
EXPOSE 7860

# Point d'entrée pour l'initialisation des bases
ENTRYPOINT ["./entrypoint.sh"]

# Commande finale via Supervisord
CMD ["/usr/bin/supervisord", "-c", "/home/user/app/supervisord.conf"]
