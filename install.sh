#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}    MCP-GLPI Server - Instalação     ${NC}"
echo -e "${YELLOW}=======================================${NC}"

# Verificar se é Linux
if [ "$(uname)" != "Linux" ]; then
    echo -e "${RED}Este script só funciona em sistemas Linux!${NC}"
    echo -e "${YELLOW}Para Windows ou Mac, siga as instruções manuais no README.md${NC}"
    exit 1
fi

# Atualizar sistema
echo -e "\n${YELLOW}[1/7]${NC} Atualizando o sistema..."
sudo apt update && sudo apt upgrade -y
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao atualizar o sistema. Verifique suas permissões sudo.${NC}"
    exit 1
fi

# Instalar dependências
echo -e "\n${YELLOW}[2/7]${NC} Instalando Python e dependências..."
sudo apt install -y python3 python3-pip python3-venv git
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar as dependências.${NC}"
    exit 1
fi

# Verificar versão do Python
python3_version=$(python3 --version | cut -d " " -f 2)
echo -e "Python versão: ${GREEN}$python3_version${NC}"
python3_major=$(echo $python3_version | cut -d. -f1)
python3_minor=$(echo $python3_version | cut -d. -f2)

if [ "$python3_major" -lt 3 ] || ([ "$python3_major" -eq 3 ] && [ "$python3_minor" -lt 8 ]); then
    echo -e "${RED}Python 3.8+ é necessário. Versão atual: $python3_version${NC}"
    exit 1
fi

# Criar e ativar ambiente virtual
echo -e "\n${YELLOW}[3/7]${NC} Configurando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo -e "\n${YELLOW}[4/7]${NC} Instalando pacotes Python necessários..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar as dependências Python.${NC}"
    exit 1
fi

# Criar diretórios necessários
echo -e "\n${YELLOW}[5/7]${NC} Criando estrutura de diretórios..."
mkdir -p logs

# Configurar o arquivo .env
echo -e "\n${YELLOW}[6/7]${NC} Configurando arquivo de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}Arquivo .env criado com configurações padrão.${NC}"
    echo -e "${YELLOW}IMPORTANTE: Edite o arquivo .env com suas configurações do GLPI!${NC}"
else
    echo -e "${YELLOW}Arquivo .env já existe. Mantendo configurações atuais.${NC}"
fi

# Configurar permissões
echo -e "\n${YELLOW}[7/7]${NC} Configurando permissões..."
chmod +x main.py
if [ -f setup.sh ]; then
    chmod +x setup.sh
fi

echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN} Instalação do MCP-GLPI Server concluída! ${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "\nPara iniciar o servidor, execute:"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo -e "${YELLOW}uvicorn main:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo -e "\nAcesse a documentação da API em: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}IMPORTANTE: Certifique-se de configurar corretamente o arquivo .env antes de iniciar o servidor!${NC}" 