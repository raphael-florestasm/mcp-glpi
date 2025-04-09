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
echo "     Iniciando MCP GLPI Server em modo background               "
echo "================================================================="
echo "Host: $MCP_HOST"
echo "Porta: $MCP_PORT"
echo "Logs: nohup.out"
echo "================================================================="

# Iniciar servidor em background
nohup uvicorn main:app --host $MCP_HOST --port $MCP_PORT > nohup.out 2>&1 &

# Salvar PID para uso posterior
echo $! > mcp_server.pid
echo "Servidor iniciado com PID: $(cat mcp_server.pid)"
echo "Para parar o servidor, execute: ./stop_server.sh" 