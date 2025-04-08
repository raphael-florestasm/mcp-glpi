#!/bin/bash

# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências necessárias
sudo apt-get install -y python3 python3-pip git

# Clonar repositório
git clone https://github.com/raphael-florestasm/mcp-glpi.git
cd mcp-glpi

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# O arquivo .env será configurado manualmente com as credenciais corretas

# Tornar scripts executáveis
chmod +x install.sh
chmod +x setup.sh

# Instalar o servidor
./install.sh

# Iniciar o servidor na porta 8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 