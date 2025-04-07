"""
Testes para verificar a configuração básica do ambiente.
"""

import os
import sys
import importlib.util
import pytest
from pathlib import Path


def test_environment_variables():
    """Teste para verificar se as variáveis de ambiente necessárias estão definidas."""
    # Verifica se o arquivo .env existe
    assert os.path.exists(".env") or os.path.exists(".env.example"), \
        "Arquivo .env ou .env.example não encontrado"
    
    # Se usarmos o arquivo .env.example, copiamos para .env temporariamente para o teste
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        with open(".env.example", "r") as example:
            with open(".env", "w") as env:
                env.write(example.read())
        temp_env_created = True
    else:
        temp_env_created = False
    
    # Carregamos as variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pytest.skip("python-dotenv não está instalado")
    
    # Verificamos as variáveis obrigatórias
    required_vars = [
        "GLPI_URL", 
        "GLPI_APP_TOKEN", 
        "GLPI_USER_TOKEN",
        "MCP_HOST",
        "MCP_PORT"
    ]
    
    for var in required_vars:
        assert var in os.environ, f"Variável de ambiente {var} não encontrada"
    
    # Removemos o arquivo .env temporário se foi criado
    if temp_env_created:
        os.remove(".env")


def test_required_modules():
    """Teste para verificar se os módulos necessários estão disponíveis."""
    required_modules = [
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "requests",
        "pydantic",
        "python-jose",
        "passlib"
    ]
    
    for module in required_modules:
        module_name = module.replace("-", "_")
        spec = importlib.util.find_spec(module_name)
        assert spec is not None, f"Módulo {module} não está instalado"


def test_project_structure():
    """Teste para verificar se a estrutura básica do projeto está correta."""
    required_dirs = [
        "src",
        "src/auth",
        "src/glpi",
        "src/agent",
        "api",
        "config"
    ]
    
    for dir_path in required_dirs:
        assert os.path.isdir(dir_path), f"Diretório {dir_path} não encontrado"
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "api/routes.py",
        "src/auth/session.py",
        "src/glpi/client.py"
    ]
    
    for file_path in required_files:
        assert os.path.isfile(file_path), f"Arquivo {file_path} não encontrado"


def test_logs_directory():
    """Teste para verificar se o diretório de logs existe e tem permissões corretas."""
    # Verifica se o diretório de logs existe, se não, cria
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
    
    assert logs_dir.exists(), "Diretório de logs não existe"
    
    # Verifica se o diretório tem permissão de escrita
    assert os.access(logs_dir, os.W_OK), "Diretório de logs não tem permissão de escrita"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 