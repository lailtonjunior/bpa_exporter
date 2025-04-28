#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface principal do Exportador BPA-I.
"""

import os
import PySimpleGUI as sg
from pathlib import Path

from ui.export_window import executar_interface
from ui.config_windows import configurar_conexao, configurar_parametros

def menu_principal():
    """Exibe o menu principal do aplicativo."""
    
    # Definir layout do menu
    menu_def = [
        ['Arquivo', ['Exportar BPA-I', 'Sair']],
        ['Configurações', ['Conexão ao Banco', 'Parâmetros do BPA-I']],
        ['Ajuda', ['Sobre']]
    ]
    
    # Tentar carregar o ícone do aplicativo
    try:
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'resources', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            icon_image = sg.Image(filename=icon_path)
        else:
            icon_image = sg.Text("BPA-I", font=("Helvetica", 24), justification='center')
    except:
        icon_image = sg.Text("BPA-I", font=("Helvetica", 24), justification='center')
    
    layout = [
        [sg.Menu(menu_def)],
        [sg.Text("Exportador de BPA-I", font=("Helvetica", 20), justification='center', expand_x=True)],
        [sg.Text("Sistema de exportação de dados para o formato BPA-I", font=("Helvetica", 12), justification='center', expand_x=True)],
        [sg.VPush()],
        [sg.Push(), icon_image, sg.Push()],
        [sg.VPush()],
        [sg.Text("Selecione uma operação:", font=("Helvetica", 12), justification='center', expand_x=True)],
        [sg.Push(), sg.Button("Exportar BPA-I", size=(20, 2), button_color=('white', '#4a6da7'), font=("Helvetica", 12)), sg.Push()],
        [sg.VPush()],
        [sg.Text("Configurações:", font=("Helvetica", 12), justification='center', expand_x=True)],
        [sg.Push(), sg.Button("Configurar Conexão", size=(20, 1)), sg.Push()],
        [sg.Push(), sg.Button("Configurar Parâmetros", size=(20, 1)), sg.Push()],
        [sg.VPush()],
        [sg.Push(), sg.Button("Sair", size=(10, 1), button_color=("white", "firebrick")), sg.Push()]
    ]
    
    janela = sg.Window("Sistema de Exportação BPA-I", layout, size=(500, 400), finalize=True, resizable=True)
    
    while True:
        evento, valores = janela.read()
        
        if evento in (sg.WINDOW_CLOSED, "Sair", "Arquivo::Sair"):
            break
        
        elif evento in ("Exportar BPA-I", "Arquivo::Exportar BPA-I"):
            janela.hide()
            executar_interface()
            janela.un_hide()
        
        elif evento in ("Configurar Conexão", "Configurações::Conexão ao Banco"):
            configurar_conexao()
        
        elif evento in ("Configurar Parâmetros", "Configurações::Parâmetros do BPA-I"):
            configurar_parametros()
        
        elif evento == "Ajuda::Sobre":
            sg.popup("""
            Exportador BPA-I v1.0
            
            Sistema para exportação de dados ambulatoriais
            no formato BPA-I (Boletim de Produção Ambulatorial Individualizado)
            seguindo o layout SIA/SUS.
            
            © 2025 - Todos os direitos reservados
            """, title="Sobre o Sistema")
    
    janela.close()