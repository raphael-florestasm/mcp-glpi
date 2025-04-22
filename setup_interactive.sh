#!/bin/bash

# Função para verificar e instalar dependências do sistema
check_system_dependencies() {
    echo "Verificando dependências do sistema..."
    
    # Verificar a versão do Python disponível
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
    
    echo "Versão do Python detectada: $(python3 --version)"
    
    # Verificar se os pacotes necessários estão instalados
    if ! dpkg -l python3-venv &> /dev/null || ! dpkg -l python3-full &> /dev/null; then
        echo "Instalando pacotes necessários para o ambiente Python..."
        echo "Você será solicitado a fornecer sua senha para instalar os pacotes do sistema."
        
        sudo apt update
        sudo apt install -y python3-pip python3-venv python3-full
        
        if [ $? -ne 0 ]; then
            echo "⚠️ Falha ao instalar pacotes necessários."
            echo "Por favor, instale manualmente os seguintes pacotes e execute este script novamente:"
            echo "  sudo apt install python3-pip python3-venv python3-full"
            exit 1
        fi
    fi
}

# Função para gerar uma chave JWT aleatória
generate_jwt_secret() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Função para criar diretório de logs
create_log_dir() {
    mkdir -p logs
    echo "Diretório de logs criado."
}

# Verificar dependências do sistema primeiro
check_system_dependencies

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

# Remover ambiente virtual anterior se existir
if [ -d "venv" ]; then
    echo "Removendo ambiente virtual anterior..."
    rm -rf venv
fi

# Criar ambiente virtual Python com acesso aos pacotes do sistema
echo ""
echo "Configurando ambiente virtual Python..."
python3 -m venv --system-site-packages venv

# Verificar se a criação do ambiente virtual foi bem-sucedida
if [ ! -f "venv/bin/activate" ]; then
    echo "⚠️ Falha ao criar o ambiente virtual Python."
    echo ""
    echo "Tentando método alternativo..."
    python3 -m venv venv
    
    if [ ! -f "venv/bin/activate" ]; then
        echo "⚠️ Falha persistente na criação do ambiente virtual."
        echo ""
        echo "Por favor, tente os seguintes comandos manualmente:"
        echo "  sudo apt install python3-venv python3-full"
        echo "  python3 -m venv --system-site-packages venv"
        echo ""
        echo "Ou use o método Docker como descrito no README.md"
        exit 1
    fi
fi

source venv/bin/activate

# Atualizar pip e instalar dependências
echo ""
echo "Instalando dependências..."
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt

# Se a instalação falhar, tente com --break-system-packages
if [ $? -ne 0 ]; then
    echo "⚠️ Falha ao instalar as dependências. Tentando método alternativo..."
    echo ""
    deactivate
    rm -rf venv
    
    echo "Criando novo arquivo de requisitos ajustado..."
    # Remover restrições de versão muito específicas
    sed 's/==/>=/g' requirements.txt > requirements_min.txt
    
    echo "Criando ambiente virtual com pacotes do sistema..."
    python3 -m venv --system-site-packages venv
    source venv/bin/activate
    
    echo "Instalando dependências com requisitos mínimos..."
    python -m pip install --no-cache-dir -r requirements_min.txt
    
    if [ $? -ne 0 ]; then
        echo "⚠️ Todas as tentativas de instalação falharam."
        echo ""
        echo "Recomendamos usar o método Docker:"
        echo "1. Certifique-se de que o Docker está instalado:"
        echo "   sudo apt install docker.io docker-compose"
        echo ""
        echo "2. Configure e execute o Docker:"
        echo "   docker-compose up -d"
        exit 1
    fi
fi

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