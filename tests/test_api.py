"""
Testes para a API do MCP GLPI Server.
"""

import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ajusta o path para importar o módulo principal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


@pytest.fixture
def client():
    """Fixture para criar um cliente de teste."""
    return TestClient(app)


def test_api_root(client):
    """Teste para verificar se a raiz da API está acessível."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MCP GLPI Server" in response.text


def test_api_docs(client):
    """Teste para verificar se a documentação da API está acessível."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_api_openapi(client):
    """Teste para verificar se o schema OpenAPI está acessível."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    json_data = response.json()
    assert "paths" in json_data
    assert "components" in json_data


def test_api_health(client):
    """Teste para verificar se o endpoint de saúde está funcionando."""
    # Adicionar endpoint de saúde se ainda não existir
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_version(client):
    """Teste para verificar se o endpoint de versão está funcionando."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_ticket_endpoints_exist(client):
    """Teste para verificar se os endpoints de tickets existem."""
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    
    ticket_endpoints = [
        "/api/v1/tickets",
        "/api/v1/tickets/{ticket_id}"
    ]
    
    for endpoint in ticket_endpoints:
        assert any(path.startswith(endpoint) for path in paths), f"Endpoint {endpoint} não encontrado"


def test_category_endpoints_exist(client):
    """Teste para verificar se os endpoints de categorias existem."""
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    
    category_endpoints = [
        "/api/v1/categories",
        "/api/v1/categories/{category_id}"
    ]
    
    for endpoint in category_endpoints:
        assert any(path.startswith(endpoint) for path in paths), f"Endpoint {endpoint} não encontrado"


def test_agent_endpoints_exist(client):
    """Teste para verificar se os endpoints do agente existem."""
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    
    agent_endpoints = [
        "/api/v1/agent/analyze",
        "/api/v1/agent/suggest-category",
        "/api/v1/agent/evaluate-priority",
        "/api/v1/agent/determine-action",
        "/api/v1/agent/execute-action"
    ]
    
    for endpoint in agent_endpoints:
        assert any(path.startswith(endpoint) for path in paths), f"Endpoint {endpoint} não encontrado"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 