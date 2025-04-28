#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interfaces de configuração do Exportador BPA-I.
"""

import os
import PySimpleGUI as sg
import configparser

from modules.database import testar_conexao, salvar_configuracoes_db
from modules.validators import validar_cnes, validar_cnpj

def configurar_conexao():
    """Permite configurar os parâmetros de conexão com o banco de dados."""
    
    # Carregar configurações atuais
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    host, port, dbname, user, password, schema = "localhost", "5432", "bd0553", "postgres", "postgres", "sigh"
    
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'DATABASE' in config:
            host = config['DATABASE'].get('host', host)
            port = config['DATABASE'].get('port', port)
            dbname = config['DATABASE'].get('dbname', dbname)
            user = config['DATABASE'].get('user', user)
            password = config['DATABASE'].get('password', password)
            schema = config['DATABASE'].get('schema', schema)
    
    layout = [
        [sg.Text("Configurações de Conexão ao Banco de Dados", font=("Helvetica", 12, "bold"))],
        [sg.Text("Servidor:", size=(15, 1)), sg.Input(host, key="host", size=(30, 1))],
        [sg.Text("Porta:", size=(15, 1)), sg.Input(port, key="port", size=(30, 1))],
        [sg.Text("Nome do Banco:", size=(15, 1)), sg.Input(dbname, key="dbname", size=(30, 1))],
        [sg.Text("Usuário:", size=(15, 1)), sg.Input(user, key="user", size=(30, 1))],
        [sg.Text("Senha:", size=(15, 1)), sg.Input(password, key="password", size=(30, 1), password_char='*')],
        [sg.Text("Schema:", size=(15, 1)), sg.Input(schema, key="schema", size=(30, 1))],
        [sg.Button("Salvar", button_color=('white', '#4a6da7')), sg.Button("Testar Conexão"), sg.Button("Cancelar")]
    ]
    
    janela = sg.Window("Configuração do Banco de Dados", layout, modal=True)
    
    while True:
        evento, valores = janela.read()
        if evento in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        
        elif evento == "Testar Conexão":
            try:
                resultado, mensagem = testar_conexao(
                    valores["host"],
                    valores["port"],
                    valores["dbname"],
                    valores["user"],
                    valores["password"]
                )
                if resultado:
                    sg.popup("Conexão estabelecida com sucesso!", title="Teste de Conexão")
                else:
                    sg.popup(f"Erro ao conectar: {mensagem}", title="Erro de Conexão")
            except Exception as e:
                sg.popup(f"Erro ao conectar: {e}", title="Erro de Conexão")
        
        elif evento == "Salvar":
            try:
                # Validar a porta (deve ser um número)
                porta = int(valores["port"])
                if porta <= 0 or porta > 65535:
                    sg.popup("A porta deve ser um número entre 1 e 65535.", title="Validação")
                    continue
                
                # Salvar as configurações
                salvar_configuracoes_db(
                    valores["host"],
                    porta,
                    valores["dbname"],
                    valores["user"],
                    valores["password"],
                    valores["schema"]
                )
                
                sg.popup("Configurações salvas com sucesso!", title="Configurações")
                break
            except ValueError:
                sg.popup("A porta deve ser um número válido.", title="Validação")
    
    janela.close()

def configurar_parametros():
    """Permite configurar os parâmetros específicos da exportação BPA-I."""
    
    # Carregar configurações atuais
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    cnes = "2560372"
    cnpj = "25062282000182"
    nome_hospital = "Hospital XYZ"
    sigla_hospital = "HXYZ"
    destino = "Secretaria Municipal de Saude"
    tipo_destino = "M"
    
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'HOSPITAL' in config:
            cnes = config['HOSPITAL'].get('cnes', cnes)
            cnpj = config['HOSPITAL'].get('cnpj', cnpj)
            nome_hospital = config['HOSPITAL'].get('nome', nome_hospital)
            sigla_hospital = config['HOSPITAL'].get('sigla', sigla_hospital)
        
        if 'DESTINO' in config:
            destino = config['DESTINO'].get('nome', destino)
            tipo_destino = config['DESTINO'].get('tipo', tipo_destino)
    
    layout = [
        [sg.Text("Configurações do Estabelecimento", font=("Helvetica", 12, "bold"))],
        [sg.Text("CNES do Hospital:", size=(20, 1)), sg.Input(cnes, key="cnes", size=(20, 1))],
        [sg.Text("CNPJ do Hospital:", size=(20, 1)), sg.Input(cnpj, key="cnpj", size=(20, 1))],
        [sg.Text("Nome do Hospital:", size=(20, 1)), sg.Input(nome_hospital, key="nome_hospital", size=(30, 1))],
        [sg.Text("Sigla do Hospital:", size=(20, 1)), sg.Input(sigla_hospital, key="sigla_hospital", size=(10, 1))],
        [sg.Text("Órgão de Destino:", size=(20, 1)), sg.Input(destino, key="destino", size=(30, 1))],
        [sg.Text("Tipo de Destino:"), 
         sg.Radio("Municipal", "DESTINO", key="municipal", default=(tipo_destino=="M")), 
         sg.Radio("Estadual", "DESTINO", key="estadual", default=(tipo_destino=="E"))],
        [sg.Button("Salvar", button_color=('white', '#4a6da7')), sg.Button("Cancelar")]
    ]
    
    janela = sg.Window("Configuração dos Parâmetros", layout, modal=True)
    
    while True:
        evento, valores = janela.read()
        if evento in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        
        elif evento == "Salvar":
            # Validar CNES (7 dígitos)
            if not validar_cnes(valores["cnes"]):
                sg.popup("O CNES deve conter 7 dígitos numéricos.", title="Validação")
                continue
            
            # Validar CNPJ (14 dígitos)
            if not validar_cnpj(valores["cnpj"]):
                sg.popup("O CNPJ deve ser válido (14 dígitos numéricos).", title="Validação")
                continue
            
            # Verificar nome e sigla
            if not valores["nome_hospital"].strip():
                sg.popup("O nome do hospital não pode estar em branco.", title="Validação")
                continue
            
            if not valores["sigla_hospital"].strip():
                sg.popup("A sigla do hospital não pode estar em branco.", title="Validação")
                continue
            
            # Salvar os parâmetros
            tipo_destino = "M" if valores["municipal"] else "E"
            cnpj_limpo = ''.join(filter(str.isdigit, valores["cnpj"]))
            
            config = configparser.ConfigParser()
            if os.path.exists(config_path):
                config.read(config_path)
            
            if 'HOSPITAL' not in config:
                config['HOSPITAL'] = {}
            
            config['HOSPITAL']['cnes'] = valores["cnes"]
            config['HOSPITAL']['cnpj'] = cnpj_limpo
            config['HOSPITAL']['nome'] = valores["nome_hospital"]
            config['HOSPITAL']['sigla'] = valores["sigla_hospital"]
            
            if 'DESTINO' not in config:
                config['DESTINO'] = {}
            
            config['DESTINO']['nome'] = valores["destino"]
            config['DESTINO']['tipo'] = tipo_destino
            
            with open(config_path, 'w') as configfile:
                config.write(configfile)
            
            sg.popup("Parâmetros salvos com sucesso!", title="Configurações")
            break
    
    janela.close()