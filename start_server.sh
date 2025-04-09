#!/bin/bash

# Ativar ambiente virtual
source venv/bin/activate

# Carregar variáveis do arquivo .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Arquivo .env não encontrado. Execute ./setup_interactive.sh primeiro."
    exit 1
fi

echo "================================================================="
echo "        Iniciando MCP GLPI Server                               "
echo "================================================================="
echo "Host: $MCP_HOST"
echo "Porta: $MCP_PORT"
echo "================================================================="

# Iniciar servidor
uvicorn main:app --host $MCP_HOST --port $MCP_PORT --reload 