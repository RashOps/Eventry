#!/bin/bash
set -e

# Configuration des variables d'environnement pour l'init
export POSTGRES_USER=${SQL_USER:-admin}
export POSTGRES_PASSWORD=${SQL_PASSWORD:-password}
export POSTGRES_DB=${SQL_DATABASE:-eventry}

echo "Starting initialization of databases..."

# 1. Initialisation de PostgreSQL
if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then
    echo "Initializing PostgreSQL data directory..."
    /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data
    
    # Démarrage temporaire pour configurer
    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/pg_init.log start
    
    echo "Creating database and user..."
    psql -d postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
    psql -d postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"
    
    # Exécution du script d'initialisation s'il existe
    if [ -f "/home/user/app/db/sql/init.sql" ]; then
        echo "Running init.sql..."
        psql -U $POSTGRES_USER -d $POSTGRES_DB -f /home/user/app/db/sql/init.sql
    fi
    
    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data stop
fi

# 2. Initialisation de MongoDB
if [ ! -f "/var/lib/mongodb/mongod.lock" ]; then
    echo "Initializing MongoDB..."
    # MongoDB s'initialise au premier démarrage avec mongod --dbpath
    # On pourrait exécuter des scripts ici avec mongosh si nécessaire
fi

echo "Initialization complete."
exec "$@"
