#!/bin/bash

# Script para instalação do MCP GLPI Server usando Docker no Ubuntu
# Este método é recomendado para servidores Ubuntu 22.04+ para evitar problemas
# com ambientes Python gerenciados externamente

# Cores para melhor visualização
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar se o Docker está instalado
check_docker() {
    echo -e "${YELLOW}Verificando instalação do Docker...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker não encontrado. Instalando...${NC}"
        sudo apt update
        sudo apt install -y docker.io docker-compose
        
        # Iniciar e habilitar o serviço Docker
        sudo systemctl enable docker
        sudo systemctl start docker
        
        # Adicionar usuário atual ao grupo docker para evitar uso de sudo
        sudo usermod -aG docker $USER
        echo -e "${YELLOW}Você pode precisar fazer logout/login para que as mudanças no grupo docker tenham efeito${NC}"
    else
        echo -e "${GREEN}Docker já está instalado!${NC}"
    fi
}

# Função para gerar uma chave JWT aleatória
generate_jwt_secret() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Verificar e instalar Docker se necessário
check_docker

# Mensagem de boas-vindas
echo "================================================================="
echo "     Instalação do MCP GLPI Server via Docker (Ubuntu)           "
echo "================================================================="
echo "Este assistente irá configurar o MCP GLPI Server usando Docker."
echo "Essa abordagem evita problemas com ambientes Python no Ubuntu."
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
read -p "Porta do MCP (padrão: 8000): " mcp_port
mcp_port=${mcp_port:-8000}
read -p "Modo de depuração (True/False, padrão: True): " mcp_debug
mcp_debug=${mcp_debug:-True}

# Gerar chave JWT secreta
jwt_secret=$(generate_jwt_secret)
echo ""
echo -e "${GREEN}Chave JWT secreta gerada automaticamente.${NC}"

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
MCP_HOST=0.0.0.0
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
mkdir -p logs
echo "Diretório de logs criado."

# Verificar se o arquivo docker-compose.yml existe
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Arquivo docker-compose.yml não encontrado.${NC}"
    echo "Criando arquivo docker-compose.yml padrão..."
    
    cat > docker-compose.yml << EOF
version: '3'

services:
  mcp-glpi:
    build: .
    restart: always
    ports:
      - "$mcp_port:8000"
    volumes:
      - ./logs:/app/logs
    env_file:
      - .env
EOF
fi

# Verificar se o Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Arquivo Dockerfile não encontrado.${NC}"
    echo "Criando Dockerfile padrão..."
    
    cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
fi

# Iniciar o contêiner Docker
echo ""
echo -e "${YELLOW}Iniciando o MCP GLPI Server via Docker...${NC}"
docker-compose up -d

# Verificar se o contêiner está em execução
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=================================================================${NC}"
    echo -e "${GREEN}MCP GLPI Server iniciado com sucesso via Docker!${NC}"
    echo -e "${GREEN}=================================================================${NC}"
    echo ""
    echo "O servidor está disponível em: http://localhost:$mcp_port"
    echo "Documentação da API: http://localhost:$mcp_port/docs"
    echo ""
    echo "Comandos úteis:"
    echo "  - Ver logs: docker-compose logs -f"
    echo "  - Parar o servidor: docker-compose down"
    echo "  - Reiniciar o servidor: docker-compose restart"
    echo -e "${GREEN}=================================================================${NC}"
else
    echo ""
    echo -e "${RED}=================================================================${NC}"
    echo -e "${RED}Ocorreu um erro ao iniciar o contêiner Docker.${NC}"
    echo -e "${RED}=================================================================${NC}"
    echo ""
    echo "Por favor, verifique os logs para mais informações:"
    echo "docker-compose logs"
    echo ""
    echo "Ou tente executar manualmente:"
    echo "docker-compose up"
    echo -e "${RED}=================================================================${NC}"
fi 