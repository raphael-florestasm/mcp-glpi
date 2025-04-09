#!/bin/bash

# Função para gerar uma chave JWT aleatória
generate_jwt_secret() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Função para criar diretório de logs
create_log_dir() {
    mkdir -p logs
    echo "Diretório de logs criado."
}

# Mensagem de boas-vindas
echo "================================================================="
echo "        Instalação Interativa do MCP GLPI Server                 "
echo "================================================================="
echo "Este assistente irá ajudá-lo a configurar o MCP GLPI Server."
echo "Você precisará fornecer algumas informações para a configuração."
echo "================================================================="
echo ""

# Perguntar informações do GLPI
echo "Configuração do GLPI:"
echo "--------------------"
read -p "URL do GLPI (ex: https://glpi.suaempresa.com.br): " glpi_url
read -p "App-Token do GLPI: " glpi_app_token
read -p "User-Token do GLPI (será prefixado com 'user_token '): " glpi_user_token_raw
glpi_user_token="user_token $glpi_user_token_raw"
read -p "ID da Entidade padrão do GLPI (ex: 1): " glpi_entity_id

# Configuração do servidor
echo ""
echo "Configuração do Servidor MCP:"
echo "----------------------------"
read -p "Host do MCP (padrão: 0.0.0.0): " mcp_host
mcp_host=${mcp_host:-0.0.0.0}
read -p "Porta do MCP (padrão: 8000): " mcp_port
mcp_port=${mcp_port:-8000}
read -p "Modo de depuração (True/False, padrão: True): " mcp_debug
mcp_debug=${mcp_debug:-True}

# Gerar chave JWT secreta
jwt_secret=$(generate_jwt_secret)
echo ""
echo "Chave JWT secreta gerada automaticamente."

# Criar arquivo .env
echo ""
echo "Criando arquivo .env com as configurações informadas..."
cat > .env << EOF
# GLPI Configuration
GLPI_URL=$glpi_url
GLPI_APP_TOKEN=$glpi_app_token
GLPI_USER_TOKEN=$glpi_user_token
GLPI_DEFAULT_ENTITY_ID=$glpi_entity_id

# Server Configuration
MCP_HOST=$mcp_host
MCP_PORT=$mcp_port
MCP_DEBUG=$mcp_debug

# Security
JWT_SECRET_KEY=$jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cache Configuration
CACHE_TTL=300  # 5 minutes in seconds

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mcp-server.log
EOF

# Criar diretório de logs
create_log_dir

# Criar ambiente virtual Python
echo ""
echo "Configurando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo ""
echo "Instalando dependências..."
pip install -r requirements.txt

# Tornar scripts executáveis
echo ""
echo "Configurando permissões..."
chmod +x *.sh

echo ""
echo "================================================================="
echo "Configuração concluída com sucesso!"
echo "================================================================="
echo ""
echo "Para iniciar o servidor:"
echo "1. Ative o ambiente virtual: source venv/bin/activate"
echo "2. Execute: uvicorn main:app --host $mcp_host --port $mcp_port --reload"
echo ""
echo "Ou simplesmente execute: ./start_server.sh"
echo ""
echo "O servidor estará disponível em: http://$mcp_host:$mcp_port"
echo "Documentação da API: http://$mcp_host:$mcp_port/docs"
echo "=================================================================" 