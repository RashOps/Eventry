# Utilisation d'Ubuntu 22.04 pour la compatibilité des paquets DB
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Installation des dépendances système et DB
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    supervisor \
    python3 \
    python3-pip \
    postgresql-15 \
    postgresql-client-15 \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update && apt-get install -y mongodb-org \
    && rm -rf /var/lib/apt/lists/*

# 2. Installation de UV pour la gestion Python (standard projet)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

# 3. Configuration de l'utilisateur Hugging Face (UID 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user
WORKDIR $HOME/app

# Création des répertoires de données et permissions
RUN mkdir -p /var/lib/postgresql/data /var/lib/mongodb /var/run/postgresql /tmp \
    && chown -R user:user /var/lib/postgresql /var/lib/mongodb /var/run/postgresql /tmp /etc/postgresql

# 4. Copie des fichiers du projet
COPY --chown=user:user . .

# 5. Installation des dépendances Python
RUN uv pip install --system --no-cache -r backend/requirements.txt

# 6. Scripts de configuration
RUN chmod +x entrypoint.sh
USER user

# Port exposé par Hugging Face
EXPOSE 7860

# Point d'entrée pour l'initialisation des bases
ENTRYPOINT ["./entrypoint.sh"]

# Commande finale via Supervisord
CMD ["/usr/bin/supervisord", "-c", "/home/user/app/supervisord.conf"]
