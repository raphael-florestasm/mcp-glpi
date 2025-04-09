# MCP GLPI Server

Servidor MCP (Management Control Protocol) para integração com GLPI (Gestionnaire Libre de Parc Informatique). Esta solução permite gerenciar chamados e inventário de TI através de uma API REST, facilitando a automatização de processos e integração com outros sistemas.

## 🚀 Funcionalidades

- Integração completa com a API do GLPI
- Criação, consulta e atualização de chamados
- Gerenciamento de categorias de chamados
- Sistema de decisão inteligente para categorização e priorização
- Busca avançada por tickets e soluções
- API RESTful documentada com Swagger/OpenAPI

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Acesso a uma instância GLPI (versão 9.5 ou superior)
- Token de API do GLPI

## 💾 Instalação

### Método 1: Instalação Interativa (Recomendado)

A maneira mais simples de instalar o MCP GLPI Server é usando nosso assistente interativo:

```bash
# Clone o repositório
git clone https://github.com/raphael-florestasm/mcp-glpi.git
cd mcp-glpi

# Torne o script de instalação executável
chmod +x setup_interactive.sh

# Execute o script de instalação interativa
./setup_interactive.sh
```

O script irá guiá-lo através do processo de configuração, solicitando as informações necessárias:
1. URL do GLPI
2. App-Token do GLPI
3. User-Token do GLPI
4. ID da Entidade padrão
5. Configurações do servidor (host, porta)

O script automaticamente:
- Gera uma chave JWT segura
- Cria o arquivo .env com suas configurações
- Configura o ambiente virtual Python
- Instala todas as dependências
- Prepara o servidor para execução

### Método 2: Instalação manual

Se preferir configurar manualmente:

```bash
# Clone o repositório
git clone https://github.com/raphael-florestasm/mcp-glpi.git
cd mcp-glpi

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### Método 3: Usando Docker

```bash
# Clone o repositório
git clone https://github.com/raphael-florestasm/mcp-glpi.git
cd mcp-glpi

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Inicie o contêiner
docker-compose up -d
```

## ⚙️ Configuração do GLPI

Para utilizar este servidor MCP, você precisa configurar sua instância GLPI para fornecer acesso via API:

1. Acesse sua instância GLPI com um usuário administrador
2. Navegue até **Configuração** > **Geral** > **API**
3. Ative a API REST
4. Crie um token de aplicação (App-Token)
5. Crie um token de usuário para autenticação (User-Token)

Após obter os tokens, você pode fornecer essas informações durante a instalação interativa ou configurar manualmente no arquivo `.env`.

## 🚀 Iniciando o servidor

### Método Interativo (Após a instalação)

```bash
# Iniciar o servidor em modo de desenvolvimento
./start_server.sh

# Ou iniciar em background (modo daemon)
./start_server_daemon.sh

# Para parar o servidor que está rodando em background
./stop_server.sh
```

### Método Manual

```bash
# Ative o ambiente virtual se necessário
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Inicie o servidor
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Usando Docker

```bash
docker-compose up -d
```

O servidor estará disponível em:
- API: http://localhost:8000/api/v1
- Documentação: http://localhost:8000/docs
- Verificação de saúde: http://localhost:8000/api/v1/health

## 🧪 Testes

Para executar os testes do projeto:

```bash
pytest tests/
```

## 📚 Documentação da API

A documentação completa da API está disponível através da interface Swagger/OpenAPI em http://localhost:8000/docs após iniciar o servidor.

## 📁 Estrutura do Projeto

```
mcp-glpi/
├── main.py              # Ponto de entrada da aplicação
├── requirements.txt     # Dependências do projeto
├── Dockerfile           # Configuração para Docker
├── docker-compose.yml   # Configuração do Docker Compose
├── setup_interactive.sh # Script de instalação interativa
├── start_server.sh      # Script para iniciar o servidor
├── start_server_daemon.sh # Script para iniciar em background
├── stop_server.sh       # Script para parar o servidor
├── .env.example         # Exemplo de configuração
├── src/
│   ├── auth/            # Autenticação e sessão
│   ├── glpi/            # Integração com GLPI
│   └── agent/           # Lógica do agente MCP
├── api/                 # Rotas da API
├── config/              # Configurações
└── tests/               # Testes automatizados
```

## 🔧 Solução de Problemas

### Problemas de conexão com o GLPI

- Verifique se a URL do GLPI está correta e acessível
- Confirme se os tokens de API estão válidos e ativos
- Verifique se a API REST está habilitada no GLPI

### Erro na instalação de dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Problemas com permissões no Linux

```bash
chmod +x *.sh
chmod +x main.py
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie sua branch de funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Envie para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença Apache 2.0 - veja o arquivo LICENSE para mais detalhes.
