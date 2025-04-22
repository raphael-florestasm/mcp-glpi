#!/bin/bash

# Função para verificar e instalar dependências do sistema
check_system_dependencies() {
    echo "Verificando dependências do sistema..."
    
    # Verificar a versão do Python disponível
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
    PYTHON_MINOR=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f2)
    
    echo "Versão do Python detectada: $(python3 --version)"
    
    # Verificar se o pip e venv estão instalados
    if ! command -v pip3 &> /dev/null || ! dpkg -l | grep -qE "python3-venv|python3-pip"; then
        echo "Instalando pacotes necessários para o ambiente Python..."
        echo "Você será solicitado a fornecer sua senha para instalar os pacotes do sistema."
        
        # Determinar o pacote python3-venv correto baseado na versão do Python
        VENV_PACKAGE="python3-venv"
        if [ -n "$PYTHON_VERSION" ]; then
            VENV_PACKAGE="python3-venv python3-full"
        fi
        
        sudo apt update
        sudo apt install -y python3-pip $VENV_PACKAGE
        
        if [ $? -ne 0 ]; then
            echo "⚠️ Falha ao instalar pacotes necessários."
            echo "Por favor, instale manualmente os seguintes pacotes e execute este script novamente:"
            echo "  - python3-pip"
            echo "  - $VENV_PACKAGE"
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

# Criar ambiente virtual Python
echo ""
echo "Configurando ambiente virtual Python..."
python3 -m venv venv

# Verificar se a criação do ambiente virtual foi bem-sucedida
if [ ! -f "venv/bin/activate" ]; then
    echo "⚠️ Falha ao criar o ambiente virtual Python."
    echo "Por favor, tente criar manualmente com o comando:"
    echo "  python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Atualizar pip e instalar dependências
echo ""
echo "Instalando dependências..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Se a instalação falhar, ofereça instruções alternativas
if [ $? -ne 0 ]; then
    echo "⚠️ Falha ao instalar as dependências."
    echo "Isso pode ocorrer em sistemas Ubuntu mais recentes com ambientes Python gerenciados externamente."
    echo ""
    echo "Tente o seguinte método alternativo:"
    echo "1. Crie um ambiente virtual fora do sistema:"
    echo "   python3 -m venv --system-site-packages venv"
    echo ""
    echo "2. Ative o ambiente virtual:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Instale as dependências com:"
    echo "   python -m pip install -r requirements.txt --no-cache-dir"
    echo ""
    echo "Ou use o método Docker descrito no README.md"
    exit 1
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