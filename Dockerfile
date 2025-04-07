FROM python:3.10-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos de requisitos e instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o restante dos arquivos da aplicação
COPY . .

# Criar diretório de logs
RUN mkdir -p logs && \
    chmod -R 755 . && \
    chmod +x main.py

# Expor a porta padrão
EXPOSE 8000

# Executar o servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 