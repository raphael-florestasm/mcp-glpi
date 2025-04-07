# MCP GLPI Server

Servidor MCP (Management Control Protocol) para integração com GLPI.

## Requisitos

- Python 3.8+
- pip
- virtualenv ou venv

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mcp-glpi.git
cd mcp-glpi
```

2. Crie e ative um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Uso

Para iniciar o servidor em modo de desenvolvimento:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

O servidor estará disponível em:
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs

## Estrutura do Projeto

```
mcp-glpi/
├── main.py              # Ponto de entrada da aplicação
├── requirements.txt     # Dependências do projeto
├── .env.example        # Exemplo de configuração
├── src/
│   ├── auth/           # Autenticação e sessão
│   ├── glpi/           # Integração com GLPI
│   └── agent/          # Lógica do agente MCP
├── api/                # Rotas da API
└── config/             # Configurações
```

## Configuração

As seguintes variáveis de ambiente são necessárias:

- `GLPI_URL`: URL do servidor GLPI
- `GLPI_APP_TOKEN`: Token de aplicação do GLPI
- `GLPI_USER_TOKEN`: Token de usuário do GLPI
- `MCP_HOST`: Host do servidor MCP (padrão: 0.0.0.0)
- `MCP_PORT`: Porta do servidor MCP (padrão: 8000)
- `MCP_DEBUG`: Modo debug (padrão: True)

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
