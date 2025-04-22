# Solução de Problemas do MCP GLPI Server

Este guia oferece soluções para problemas comuns encontrados durante a instalação e uso do MCP GLPI Server.

## Problemas de Instalação

### 1. Erro: "The virtual environment was not created successfully because ensurepip is not available"

Este erro ocorre quando os pacotes necessários para criar ambientes virtuais Python não estão instalados no sistema.

**Solução Passo a Passo:**
```bash
# 1. Instale os pacotes necessários do sistema (NÃO use pip para isso)
sudo apt update
sudo apt install python3-venv python3-pip python3-full

# 2. Verifique se a instalação foi bem-sucedida
dpkg -l | grep python3-venv
dpkg -l | grep python3-full

# 3. Agora tente criar o ambiente virtual
python3 -m venv --system-site-packages venv
```

> ⚠️ **IMPORTANTE**: NUNCA tente instalar `python3-venv` usando pip. Este é um pacote do sistema que deve ser instalado via `apt`.

### 2. Erro: "externally-managed-environment"

Esse erro acontece em distribuições Ubuntu mais recentes (22.04+) que implementam o PEP 668, que previne a instalação de pacotes Python globalmente via pip para proteger o sistema operacional.

**Solução Completa:**

**Passo 1:** Certifique-se de que os pacotes necessários do sistema estão instalados
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-full
```

**Passo 2:** Remova qualquer ambiente virtual anterior com problemas
```bash
rm -rf venv
```

**Passo 3:** Crie um ambiente virtual usando a flag `--system-site-packages`
```bash
python3 -m venv --system-site-packages venv
```

**Passo 4:** Ative o ambiente virtual
```bash
source venv/bin/activate
```

**Passo 5:** Instale as dependências sem usar o cache e com versões mínimas
```bash
# Criar versão mais flexível do arquivo de requisitos
sed 's/==/>=/g' requirements.txt > requirements_min.txt

# Instalar dependências
python -m pip install --no-cache-dir -r requirements_min.txt
```

**Método Alternativo - Docker (Recomendado para sistemas com problemas persistentes):**
```bash
# Instalar Docker se ainda não estiver instalado
sudo apt update
sudo apt install -y docker.io docker-compose

# Configurar e executar
cp .env.example .env
# Edite o arquivo .env com suas configurações
nano .env  

# Iniciar o contêiner
docker-compose up -d
```

### 3. Erro ao ativar o ambiente virtual: "No such file or directory"

Este erro indica que o ambiente virtual não foi criado corretamente ou o caminho está incorreto.

**Solução:**
```bash
# Verifique se os pacotes necessários estão instalados
sudo apt install -y python3-venv python3-pip python3-full

# Remova qualquer ambiente virtual anterior problemático
rm -rf venv myproject-env

# Crie um novo ambiente virtual (com nome consistente)
python3 -m venv --system-site-packages venv

# Verifique se o arquivo de ativação existe
ls -la venv/bin/activate

# Ative o ambiente virtual com o caminho correto
source venv/bin/activate
```

## Problemas com Python 3.12

A versão Python 3.12 introduziu mudanças adicionais na forma como os ambientes são gerenciados. Se você está usando Python 3.12 no Ubuntu, considere estas opções adicionais:

### Opção 1: Usar pipx para aplicações isoladas
```bash
# Instale pipx
sudo apt install pipx

# Use pipx para instalar ferramentas Python em ambientes isolados
pipx install <nome-do-pacote>
```

### Opção 2: Usar o Docker (recomendado)
O uso do Docker evita completamente os problemas com o gerenciamento de pacotes Python do sistema:

```bash
# Iniciar o MCP GLPI Server via Docker
docker-compose up -d
```

## Problemas de Conexão

### 1. Não consegue conectar ao GLPI

**Soluções:**
- Verifique se a URL do GLPI está correta e acessível
- Teste a URL em um navegador para garantir que está funcionando
- Verifique se não há regras de firewall bloqueando a conexão

### 2. Erro de autenticação da API do GLPI

**Soluções:**
- Confirme se os tokens de API estão corretos
- Verifique se a API REST está habilitada no GLPI
- Certifique-se de que o usuário associado ao token tem permissões suficientes

## Problemas de Permissão

### 1. Erro ao executar scripts

**Solução:**
```bash
# Torne os scripts executáveis
chmod +x *.sh
chmod +x *.py

# Execute o script desejado
./setup_interactive.sh
```

## Problemas do Docker

### 1. Erro ao iniciar o contêiner Docker

**Soluções:**
- Verifique se o Docker está instalado e em execução
```bash
sudo systemctl status docker
```

- Certifique-se de que o arquivo .env está configurado corretamente
- Verifique se as portas necessárias estão disponíveis

```bash
# Verifique se a porta já está em uso
sudo lsof -i :8000
```

## Logs e Diagnóstico

Para diagnosticar problemas, verifique os logs do servidor:

```bash
# Se estiver usando o método de instalação direta
cat logs/mcp-server.log

# Se estiver usando Docker
docker-compose logs
```

## Reinstalação Limpa

Se você continuar enfrentando problemas, uma reinstalação limpa pode ajudar:

```bash
# Remova diretórios e arquivos existentes
rm -rf venv
rm .env

# Execute novamente o script de instalação
./setup_interactive.sh
```

Se precisar de mais ajuda, abra uma issue no repositório do GitHub ou entre em contato com a equipe de suporte. 