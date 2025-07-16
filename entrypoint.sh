#!/bin/bash

# Start PostgreSQL service

service postgresql start
sleep 3 #Waits for db to be setup

# Init database if needed
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'\"" | grep -q 1 || \
su - postgres -c "psql -c \"CREATE DATABASE $POSTGRES_DB\""


su - postgres -c "psql -c \"ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';\""

#Launch app
exec python3 app.py
