#!/bin/bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 requests==2.31.0 pydantic==2.4.2 python-jose==3.3.0 passlib==1.7.4 python-multipart==0.0.6 cachetools==5.3.1 loguru==0.7.2 pytest==7.4.3 httpx==0.25.1

# Create necessary directories
mkdir -p src/auth src/glpi src/agent api config logs

# Set permissions
chmod -R 755 .
chmod +x main.py

echo "Setup completed successfully!"
echo "To start the server, run:"
echo "source venv/bin/activate"
echo "uvicorn main:app --host 0.0.0.0 --port 8000 --reload" 