#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de configuração e instalação do BPA Exporter

Este script facilita a criação da estrutura de diretórios e arquivos
necessários para o BPA Exporter.
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

def create_directory_structure():
    """Cria a estrutura de diretórios do projeto"""
    print("Criando estrutura de diretórios...")
    
    # Lista de diretórios para criar
    directories = [
        "app",
        "app/database",
        "app/models",
        "app/services",
        "app/utils",
        "docs",
        "exports",
        "logs"
    ]
    
    # Cria os diretórios
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Diretório '{directory}' criado.")
    
    # Cria arquivos __init__.py em cada diretório
    for directory in directories:
        if directory.startswith("app"):
            init_path = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    module_name = directory.replace("/", ".")
                    f.write(f'"""\nMódulo {module_name}\n"""\n')
                print(f"  ✓ Arquivo '{init_path}' criado.")
    
    print("Estrutura de diretórios criada com sucesso.")

def create_env_file():
    """Cria o arquivo .env se ele não existir"""
    env_example_path = ".env.example"
    env_path = ".env"
    
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        print("Criando arquivo .env a partir de .env.example...")
        shutil.copy(env_example_path, env_path)
        print(f"  ✓ Arquivo '{env_path}' criado.")
        print("IMPORTANTE: Edite o arquivo .env com suas configurações de banco de dados.")
    elif not os.path.exists(env_path):
        print("ATENÇÃO: Arquivo .env.example não encontrado. Não foi possível criar .env")
    else:
        print("Arquivo .env já existe.")

def check_requirements():
    """Verifica as dependências do projeto"""
    print("Verificando dependências...")
    
    # Verifica se o arquivo requirements.txt existe
    if os.path.exists("requirements.txt"):
        print("  ✓ Arquivo 'requirements.txt' encontrado.")
        
        # Pergunta se o usuário deseja instalar as dependências
        if input("Deseja instalar as dependências? (s/n) ").lower() == 's':
            print("Instalando dependências...")
            os.system(f"{sys.executable} -m pip install -r requirements.txt")
            print("Dependências instaladas com sucesso.")
    else:
        print("ATENÇÃO: Arquivo 'requirements.txt' não encontrado.")

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="Script de configuração do BPA Exporter")
    parser.add_argument("--skip-dirs", action="store_true", help="Pula a criação da estrutura de diretórios")
    parser.add_argument("--skip-env", action="store_true", help="Pula a criação do arquivo .env")
    parser.add_argument("--skip-req", action="store_true", help="Pula a verificação de dependências")
    
    args = parser.parse_args()
    
    print("=== Configuração do BPA Exporter ===")
    
    if not args.skip_dirs:
        create_directory_structure()
    
    if not args.skip_env:
        create_env_file()
    
    if not args.skip_req:
        check_requirements()
    
    print("Configuração concluída!")
    print("Para executar o BPA Exporter, use:")
    print("  - Interface de linha de comando: python run.py")
    print("  - API web: python main.py")
    
    print("=================================")

if __name__ == "__main__":
    main()