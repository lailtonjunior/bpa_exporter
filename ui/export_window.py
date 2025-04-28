#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de exportação do aplicativo BPA-I.
"""

import os
import PySimpleGUI as sg
import datetime
from pathlib import Path

from modules.database import buscar_registros_por_competencia
from modules.generator import gerar_arquivo_bpa
from modules.formatter import MES_NOME
from modules.validators import validar_dados_exportacao

def executar_interface():
    """Cria e exibe a interface gráfica para exportação do BPA-I."""
    # Configurar tema da interface
    sg.theme('SystemDefault')
    
    # Obter ano e mês atual para pré-selecionar
    data_atual = datetime.datetime.now()
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    
    # Lista de meses para o dropdown
    meses_lista = [f"{i:02d} - {MES_NOME[i]}" for i in range(1, 13)]
    mes_selecionado = f"{mes_atual:02d} - {MES_NOME[mes_atual]}"
    
    # Layout da janela
    layout = [
        [sg.Text("Exportação BPA-I - Boletim de Produção Ambulatorial Individualizado", font=("Helvetica", 14), justification='center', expand_x=True)],
        [sg.HorizontalSeparator()],
        [sg.Text("Selecione a competência para exportação:", font=("Helvetica", 11))],
        [
            sg.Text("Mês:", size=(8, 1)),
            sg.Combo(meses_lista, default_value=mes_selecionado, key="combo_mes", size=(20, 1), readonly=True),
            sg.Text("Ano:", size=(8, 1)),
            sg.Spin(values=list(range(2020, 2031)), initial_value=ano_atual, key="spin_ano", size=(6, 1))
        ],
        [sg.Text("_" * 80)],
        [sg.Text("Pasta de destino do arquivo:", font=("Helvetica", 11))],
        [
            sg.Input(key="pasta_saida", size=(50, 1), default_text=str(Path.home() / "Downloads")),
            sg.FolderBrowse("Procurar...", button_color=('white', '#4a6da7'))
        ],
        [sg.Text("_" * 80)],
        [sg.Text("Log de operações:", font=("Helvetica", 11))],
        [sg.Multiline(key="log", size=(70, 10), disabled=True, autoscroll=True, background_color='#f9f9f9')],
        [
            sg.Button("Exportar", size=(15, 1), button_color=('white', '#4a6da7'), font=("Helvetica", 11, "bold")),
            sg.Button("Limpar Log", size=(15, 1), font=("Helvetica", 11)),
            sg.Push(),
            sg.Button("Sair", size=(10, 1), button_color=("white", "firebrick"))
        ]
    ]
    
    janela = sg.Window("Exportador BPA-I", layout, finalize=True, resizable=True, icon=None)
    
    # Loop principal da interface
    while True:
        evento, valores = janela.read()
        
        if evento == sg.WINDOW_CLOSED or evento == "Sair":
            break
        
        elif evento == "Limpar Log":
            janela["log"].update("")
            
        elif evento == "Exportar":
            try:
                # Extrair mês e ano selecionados
                mes_texto = valores["combo_mes"].split(" - ")[0]
                mes_num = int(mes_texto)
                ano_num = int(valores["spin_ano"])
                
                # Verificar pasta de saída
                pasta = valores["pasta_saida"]
                if not pasta or not os.path.isdir(pasta):
                    janela["log"].print("Erro: Pasta de destino inválida!")
                    sg.popup("Por favor, selecione uma pasta de destino válida.", title="Atenção")
                    continue

                janela["log"].print(f"Iniciando exportação para {MES_NOME[mes_num]}/{ano_num}...")
                janela["log"].print(f"Buscando registros no banco de dados...")
                janela.refresh()  # Forçar atualização da interface para mostrar o log imediatamente

                # Buscar registros no banco
                registros = buscar_registros_por_competencia(ano_num, mes_num)

                if registros is None:
                    janela["log"].print("Erro ao consultar o banco de dados. Verifique a conexão.")
                    sg.popup("Erro de conexão com o banco de dados.\nVerifique as configurações e tente novamente.", title="Erro")
                elif len(registros) == 0:
                    janela["log"].print(f"Não foram encontrados registros para {MES_NOME[mes_num]}/{ano_num}.")
                    sg.popup(f"Não há registros para {MES_NOME[mes_num]}/{ano_num}.", title="Informação")
                else:
                    janela["log"].print(f"Encontrados {len(registros)} registros para exportação.")
                    
                    # Validar dados críticos
                    janela["log"].print(f"Validando dados para exportação...")
                    problemas = validar_dados_exportacao(registros)
                    if problemas:
                        # Se houver problemas, mostra os 5 primeiros como alerta e pergunta se deseja continuar
                        msg_problemas = "\n".join(problemas[:5])
                        if len(problemas) > 5:
                            msg_problemas += f"\n... e mais {len(problemas) - 5} problemas encontrados."
                        
                        janela["log"].print(f"Foram encontrados {len(problemas)} problemas nos dados:")
                        for prob in problemas[:5]:
                            janela["log"].print(f"  - {prob}")
                        
                        resposta = sg.popup_yes_no(f"Foram encontrados {len(problemas)} problemas nos dados:\n\n{msg_problemas}\n\nDeseja continuar mesmo assim?", title="Problemas Encontrados")
                        if resposta != "Yes":
                            janela["log"].print("Exportação cancelada pelo usuário.")
                            continue
                    
                    janela["log"].print(f"Gerando arquivo BPA-I...")
                    janela.refresh()  # Atualizar interface

                    try:
                        janela["log"].print(f"Processando {len(registros)} registros...")
                        janela["log"].print(f"Aplicando formatação nos campos...")
                        janela["log"].print(f"Calculando folhas e sequências...")
                        janela.refresh()
                        
                        caminho_arquivo = gerar_arquivo_bpa(registros, ano_num, mes_num, pasta)
                        if caminho_arquivo:
                            janela["log"].print(f"Arquivo gerado com sucesso: {caminho_arquivo}")
                            janela["log"].print(f"Total de registros: {len(registros)}")
                            janela["log"].print(f"Competência: {MES_NOME[mes_num]}/{ano_num}")
                            sg.popup(f"Exportação concluída com sucesso!\nArquivo gerado: {caminho_arquivo}", title="Sucesso")
                        else:
                            janela["log"].print("Não foi possível gerar o arquivo. Verifique o log para mais detalhes.")
                    except Exception as ex:
                        janela["log"].print(f"Erro durante a geração do arquivo: {ex}")
                        sg.popup(f"Ocorreu um erro durante a exportação:\n{ex}", title="Erro")
            except ValueError as e:
                janela["log"].print(f"Erro ao processar os dados: {e}")
                sg.popup(f"Erro ao processar os dados: {e}", title="Erro")
            except Exception as e:
                janela["log"].print(f"Erro inesperado: {e}")
                sg.popup(f"Ocorreu um erro inesperado: {e}", title="Erro")

    janela.close()