#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicativo de Exportação BPA-I
Sistema para exportação de dados ambulatoriais no formato BPA-I 
(Boletim de Produção Ambulatorial Individualizado) seguindo o layout SIA/SUS.
"""

import os
import sys
import configparser
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos da aplicação
from ui.main_window import menu_principal
from modules.database import carregar_configuracoes_db

def main():
    """Função principal que inicia o aplicativo."""
    # Verificar se o arquivo de configuração existe
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if not os.path.exists(config_path):
        # Criar arquivo de configuração padrão se não existir
        config = configparser.ConfigParser()
        config['DATABASE'] = {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'bd0553',
            'user': 'postgres',
            'password': 'postgres',
            'schema': 'sigh'
        }
        config['HOSPITAL'] = {
            'cnes': '2560372',
            'cnpj': '25062282000182',
            'nome': 'Hospital XYZ',
            'sigla': 'HXYZ'
        }
        config['DESTINO'] = {
            'nome': 'Secretaria Municipal de Saude',
            'tipo': 'M'  # M = Municipal, E = Estadual
        }
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    
    # Carregar configurações do banco de dados
    carregar_configuracoes_db()
    
    # Iniciar a interface gráfica
    menu_principal()

if __name__ == "__main__":
    main()