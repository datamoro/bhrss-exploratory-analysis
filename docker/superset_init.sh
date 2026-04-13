#!/bin/bash
set -e

echo "=================================================="
echo "INICIALIZANDO SUPERSET"
echo "=================================================="

# Upgrade database
echo "Atualizando banco de dados do Superset..."
superset db upgrade

# Create admin user (ignore if exists)
echo "Criando usuario admin..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@health.com \
    --password admin || echo "Usuario admin ja existe"

# Initialize Superset
echo "Inicializando Superset..."
superset init

echo "=================================================="
echo "SUPERSET INICIADO COM SUCESSO!"
echo "=================================================="
echo ""
echo "Acesse: http://localhost:8089"
echo "Usuario: admin"
echo "Senha: admin"
echo ""
echo "Para conectar ao PostgreSQL use:"
echo "postgresql://dataengineer:SecurePass123!@health_postgres:5432/health_data"
echo ""
echo "=================================================="

# Start Superset
exec superset run -h 0.0.0.0 -p 8088 --with-threads