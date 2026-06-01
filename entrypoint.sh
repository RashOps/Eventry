#!/bin/bash
set -e

export POSTGRES_USER=${SQL_USER:-admin}
export POSTGRES_PASSWORD=${SQL_PASSWORD:-admin1234}
export POSTGRES_DB=${SQL_DATABASE:-eventry_db}

echo "Starting initialization of databases..."

# 1. Initialisation de PostgreSQL
if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then
    echo "Initializing PostgreSQL data directory..."
    /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data
    
    echo "Creating database and user..."
    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/pg_init.log start

    until psql -h localhost -U user -d postgres -c "select 1" > /dev/null 2>&1; do
      echo "Waiting for postgres to be ready for config..."
      sleep 1
    done

    psql -h localhost -d postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
    psql -h localhost -d postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"

    if [ -f "/home/user/app/db/sql/init.sql" ]; then
        echo "Running init.sql..."
        PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -f /home/user/app/db/sql/init.sql
    fi

    /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/data stop
fi

# 2. Initialisation de MongoDB (sans auth pour HF Spaces)
if [ ! -f "/var/lib/mongodb/mongod.lock" ]; then
    echo "Initializing MongoDB..."
fi

echo "Initialization complete."
exec "$@"
