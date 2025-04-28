#!/bin/bash

# Script de instalação do Exportador BPA-I para Linux
# Autor: Seu Nome
# Data: 28/04/2025

echo "=== Instalador do Exportador BPA-I ==="
echo "Verificando requisitos..."

# Verificar se o Python está instalado
python_version=$(python3 --version 2>&1)
if [[ $python_version != *"Python 3."* ]]; then
    echo "ERRO: Python 3 não encontrado. Por favor, instale o Python 3.6 ou superior."
    exit 1
fi
echo "✓ Python encontrado: $python_version"

# Verificar se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "ERRO: pip3 não encontrado. Por favor, instale o pip para Python 3."
    exit 1
fi
echo "✓ pip3 encontrado."

# Verificar se o PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo "AVISO: PostgreSQL cliente não encontrado. O aplicativo requer acesso a um servidor PostgreSQL."
    echo "       Certifique-se de que você tenha acesso a um servidor PostgreSQL."
else
    psql_version=$(psql --version)
    echo "✓ PostgreSQL cliente encontrado: $psql_version"
fi

echo "Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências."
    exit 1
fi
echo "✓ Dependências instaladas com sucesso."

# Criar diretórios necessários
mkdir -p logs
mkdir -p resources/icons

echo "Criando atalho para execução..."
# Criar script de execução
cat > run_exportador.sh << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
python3 exportador.py
EOF

chmod +x run_exportador.sh

echo "Instalação concluída com sucesso!"
echo "Para iniciar o aplicativo, execute: ./run_exportador.sh"