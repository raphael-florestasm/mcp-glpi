#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}    MCP-GLPI Server - Validação      ${NC}"
echo -e "${YELLOW}=======================================${NC}"

# Verificar se Python está instalado
echo -e "\n${YELLOW}[1/7]${NC} Verificando instalação do Python..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | cut -d " " -f 2)
    echo -e "Python versão: ${GREEN}$python_version${NC}"
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
        echo -e "${RED}Python 3.8+ é necessário. Versão atual: $python_version${NC}"
        fail_count=$((fail_count+1))
    else
        echo -e "${GREEN}✓ Versão do Python OK${NC}"
        pass_count=$((pass_count+1))
    fi
else
    echo -e "${RED}Python não encontrado.${NC}"
    fail_count=$((fail_count+1))
fi

# Verificar ambiente virtual
echo -e "\n${YELLOW}[2/7]${NC} Verificando ambiente virtual..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Ambiente virtual encontrado${NC}"
    pass_count=$((pass_count+1))
else
    echo -e "${YELLOW}⚠ Ambiente virtual não encontrado. Você pode criá-lo com: python3 -m venv venv${NC}"
    warn_count=$((warn_count+1))
fi

# Verificar instalação de dependências
echo -e "\n${YELLOW}[3/7]${NC} Verificando dependências do Python..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓ Arquivo requirements.txt encontrado${NC}"

    if [ -d "venv" ]; then
        # Ativar o ambiente virtual para verificar pacotes
        source venv/bin/activate

        missing_deps=0
        while IFS= read -r line; do
            if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then
                package=$(echo "$line" | cut -d'=' -f1)
                if ! pip show "$package" &> /dev/null; then
                    echo -e "${RED}✗ Dependência não instalada: $package${NC}"
                    missing_deps=$((missing_deps+1))
                fi
            fi
        done < requirements.txt

        if [ $missing_deps -eq 0 ]; then
            echo -e "${GREEN}✓ Todas as dependências estão instaladas${NC}"
            pass_count=$((pass_count+1))
        else
            echo -e "${YELLOW}⚠ $missing_deps dependências faltando. Execute: pip install -r requirements.txt${NC}"
            warn_count=$((warn_count+1))
        fi

        # Desativar ambiente virtual
        deactivate
    else
        echo -e "${YELLOW}⚠ Não foi possível verificar dependências (ambiente virtual não encontrado)${NC}"
        warn_count=$((warn_count+1))
    fi
else
    echo -e "${RED}✗ Arquivo requirements.txt não encontrado${NC}"
    fail_count=$((fail_count+1))
fi

# Verificar arquivo de configuração
echo -e "\n${YELLOW}[4/7]${NC} Verificando arquivo de configuração..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Arquivo .env encontrado${NC}"
    
    # Verificar variáveis obrigatórias no .env
    missing_vars=0
    for var in "GLPI_URL" "GLPI_APP_TOKEN" "GLPI_USER_TOKEN" "MCP_HOST" "MCP_PORT"; do
        if ! grep -q "^$var=" .env; then
            echo -e "${RED}✗ Variável $var não encontrada no arquivo .env${NC}"
            missing_vars=$((missing_vars+1))
        fi
    done
    
    if [ $missing_vars -eq 0 ]; then
        echo -e "${GREEN}✓ Todas as variáveis obrigatórias estão configuradas${NC}"
        pass_count=$((pass_count+1))
    else
        echo -e "${YELLOW}⚠ $missing_vars variáveis obrigatórias faltando no arquivo .env${NC}"
        warn_count=$((warn_count+1))
    fi
else
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠ Arquivo .env não encontrado, mas .env.example está presente. Execute: cp .env.example .env${NC}"
        warn_count=$((warn_count+1))
    else
        echo -e "${RED}✗ Arquivo .env ou .env.example não encontrado${NC}"
        fail_count=$((fail_count+1))
    fi
fi

# Verificar estrutura do projeto
echo -e "\n${YELLOW}[5/7]${NC} Verificando estrutura do projeto..."
structure_errors=0

for dir in "src" "src/auth" "src/glpi" "src/agent" "api" "config"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}✗ Diretório $dir não encontrado${NC}"
        structure_errors=$((structure_errors+1))
    fi
done

for file in "main.py" "api/routes.py" "src/auth/session.py" "src/glpi/client.py"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Arquivo $file não encontrado${NC}"
        structure_errors=$((structure_errors+1))
    fi
done

if [ $structure_errors -eq 0 ]; then
    echo -e "${GREEN}✓ Estrutura do projeto verificada com sucesso${NC}"
    pass_count=$((pass_count+1))
else
    echo -e "${RED}✗ $structure_errors erros na estrutura do projeto${NC}"
    fail_count=$((fail_count+1))
fi

# Verificar permissões de execução
echo -e "\n${YELLOW}[6/7]${NC} Verificando permissões..."
permission_errors=0

for script in "main.py" "install.sh"; do
    if [ -f "$script" ]; then
        if [ ! -x "$script" ]; then
            echo -e "${YELLOW}⚠ Arquivo $script não tem permissão de execução. Execute: chmod +x $script${NC}"
            permission_errors=$((permission_errors+1))
        fi
    fi
done

if [ $permission_errors -eq 0 ]; then
    echo -e "${GREEN}✓ Permissões verificadas com sucesso${NC}"
    pass_count=$((pass_count+1))
else
    echo -e "${YELLOW}⚠ $permission_errors arquivos sem permissão de execução${NC}"
    warn_count=$((warn_count+1))
fi

# Verificar testes
echo -e "\n${YELLOW}[7/7]${NC} Verificando testes..."
if [ -d "tests" ]; then
    test_files=$(find tests -name "test_*.py" | wc -l)
    if [ $test_files -gt 0 ]; then
        echo -e "${GREEN}✓ Testes encontrados: $test_files arquivos de teste${NC}"
        pass_count=$((pass_count+1))
    else
        echo -e "${YELLOW}⚠ Diretório de testes existe, mas nenhum arquivo de teste encontrado${NC}"
        warn_count=$((warn_count+1))
    fi
else
    echo -e "${YELLOW}⚠ Diretório de testes não encontrado${NC}"
    warn_count=$((warn_count+1))
fi

# Resumo
echo -e "\n${YELLOW}=======================================${NC}"
echo -e "${YELLOW}            RESULTADO                 ${NC}"
echo -e "${YELLOW}=======================================${NC}"
echo -e "${GREEN}✓ Passou: $pass_count testes${NC}"
echo -e "${YELLOW}⚠ Avisos: $warn_count${NC}"
echo -e "${RED}✗ Falhas: $fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    if [ $warn_count -eq 0 ]; then
        echo -e "\n${GREEN}Todos os testes passaram! O sistema está pronto para uso.${NC}"
    else
        echo -e "\n${YELLOW}O sistema está funcional, mas com alguns avisos.${NC}"
        echo -e "${YELLOW}Sugestão: Corrija os avisos para garantir o funcionamento ideal.${NC}"
    fi
else
    echo -e "\n${RED}Existem falhas críticas que impedem o funcionamento correto do sistema.${NC}"
    echo -e "${RED}Por favor, corrija os erros antes de prosseguir.${NC}"
fi 