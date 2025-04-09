#!/bin/bash

# Função para verificar se um comando foi executado com sucesso
check_command() {
    if [ $? -ne 0 ]; then
        echo "Erro ao executar: $1"
        exit 1
    fi
}

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt-get update
check_command "apt-get update"
sudo apt-get upgrade -y
check_command "apt-get upgrade"

# Instalar dependências necessárias
echo "Instalando dependências..."
sudo apt-get install -y python3 python3-pip git python3-venv
check_command "apt-get install"

# Remover diretório existente se houver
if [ -d "mcp-glpi" ]; then
    echo "Removendo diretório existente..."
    rm -rf mcp-glpi
fi

# Clonar repositório
echo "Clonando repositório..."
git clone https://github.com/raphael-florestasm/mcp-glpi.git
check_command "git clone"
cd mcp-glpi

# Criar e ativar ambiente virtual
echo "Configurando ambiente virtual..."
python3 -m venv venv
check_command "python3 -m venv"
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências Python..."
pip install -r requirements.txt
check_command "pip install"

# Configurar .env
echo "Configurando arquivo .env..."
cp .env.example .env
# O arquivo .env será configurado manualmente com as credenciais corretas

# Tornar scripts executáveis
echo "Configurando permissões..."
chmod +x install.sh
chmod +x setup.sh

# Instalar o servidor
echo "Instalando servidor..."
./install.sh
check_command "./install.sh"

# Iniciar o servidor na porta 8000
echo "Iniciando servidor..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
check_command "uvicorn"

echo "Servidor iniciado com sucesso!"
echo "Logs disponíveis em: server.log" 