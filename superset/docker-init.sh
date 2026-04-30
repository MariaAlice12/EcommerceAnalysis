#!/bin/bash
set -e

echo "==> Inicializando banco de metadados do Superset..."
superset db upgrade

echo "==> Criando usuário admin..."
superset fab create-admin \
    --username "${ADMIN_USERNAME:-admin}" \
    --firstname "Admin" \
    --lastname "Superset" \
    --email "${ADMIN_EMAIL:-admin@example.com}" \
    --password "${ADMIN_PASSWORD:-admin}" 2>/dev/null || echo "Usuário admin já existe."

echo "==> Configurando roles e permissões..."
superset init

echo "==> Superset pronto! Iniciando servidor na porta 8088..."
exec gunicorn \
    --bind "0.0.0.0:8088" \
    --workers 1 \
    --worker-class gthread \
    --threads 20 \
    --timeout 120 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "superset.app:create_app()"
