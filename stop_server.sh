#!/bin/bash

echo "================================================================="
echo "              Parando MCP GLPI Server                            "
echo "================================================================="

# Verificar se o arquivo de PID existe
if [ -f mcp_server.pid ]; then
    PID=$(cat mcp_server.pid)
    
    # Verificar se o processo ainda está rodando
    if ps -p $PID > /dev/null; then
        echo "Parando servidor com PID: $PID..."
        kill $PID
        echo "Servidor parado com sucesso."
    else
        echo "O servidor não está rodando (PID: $PID não encontrado)."
    fi
    
    # Remover arquivo de PID
    rm mcp_server.pid
else
    echo "Arquivo de PID não encontrado. O servidor pode não estar rodando."
    
    # Tentar encontrar e matar o processo pelo nome
    echo "Tentando encontrar processo do uvicorn..."
    UVICORN_PID=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')
    
    if [ -n "$UVICORN_PID" ]; then
        echo "Processo encontrado. Parando servidor com PID: $UVICORN_PID..."
        kill $UVICORN_PID
        echo "Servidor parado com sucesso."
    else
        echo "Nenhum processo do servidor encontrado."
    fi
fi

echo "=================================================================" 