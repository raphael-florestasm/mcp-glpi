# Solução de Problemas do MCP GLPI Server

Este guia oferece soluções para problemas comuns encontrados durante a instalação e uso do MCP GLPI Server.

## Problemas de Instalação

### 1. Erro: "The virtual environment was not created successfully because ensurepip is not available"

Este erro ocorre quando os pacotes necessários para criar ambientes virtuais Python não estão instalados no sistema.

**Solução:**
```bash
# Para Ubuntu/Debian
sudo apt update
sudo apt install python3-venv python3-pip python3-full

# Tente novamente criar o ambiente virtual
python3 -m venv venv
```

### 2. Erro: "externally-managed-environment"

Esse erro ocorre em distribuições Linux mais recentes (como Ubuntu 22.04+) que usam ambientes Python gerenciados pelo sistema por padrão.

**Soluções:**

**Opção 1:** Usar um ambiente virtual com acesso aos pacotes do sistema
```bash
# Remova qualquer ambiente virtual existente
rm -rf venv

# Crie um novo ambiente virtual com acesso aos pacotes do sistema
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Instale as dependências
python -m pip install -r requirements.txt --no-cache-dir
```

**Opção 2:** Usar o Docker (recomendado para servidores)
```bash
# Certifique-se de que o Docker está instalado
sudo apt install docker.io docker-compose

# Configure e inicie o contêiner
cp .env.example .env
# Edite o arquivo .env com suas configurações
nano .env

# Inicie o contêiner
docker-compose up -d
```

**Opção 3:** Instalar globalmente (não recomendado para ambientes de produção)
```bash
pip install -r requirements.txt --break-system-packages
```

### 3. Erro ao ativar o ambiente virtual: "No such file or directory"

Este erro ocorre quando o script tenta ativar um ambiente virtual que não foi criado com sucesso.

**Solução:**
```bash
# Verifique se os pacotes necessários estão instalados
sudo apt install python3-venv python3-pip python3-full

# Crie o ambiente virtual manualmente
python3 -m venv venv
source venv/bin/activate

# Continue com a instalação
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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