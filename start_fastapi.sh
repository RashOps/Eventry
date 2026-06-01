#!/bin/bash
echo "[fastapi] Waiting for PostgreSQL..."
until pg_isready -h localhost -U "${SQL_USER:-admin}" -d "${SQL_DATABASE:-eventry}"; do
  sleep 1
done
echo "[fastapi] Waiting for MongoDB..."
until mongosh --quiet --eval 'db.runCommand({ping:1})' > /dev/null 2>&1; do
  sleep 1
done
echo "[fastapi] DBs ready. Starting uvicorn..."
cd /home/user/app/backend
exec python3 -m uvicorn src.main:app --host 0.0.0.0 --port 7860