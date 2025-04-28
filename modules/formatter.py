#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de formatação de dados para o layout BPA-I.
"""

import datetime
import os
import configparser
from pathlib import Path

# Mapear nome do mês para abreviação de três letras (Português)
MES_ABREV = {
    1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
    7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
}

# Mapear número do mês para nome completo
MES_NOME = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_cnes_hospital():
    """Obtém o código CNES do hospital do arquivo de configuração."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'HOSPITAL' in config:
            return config['HOSPITAL'].get('cnes', '2560372')
    return '2560372'  # Valor padrão

def obter_cnpj_hospital():
    """Obtém o CNPJ do hospital do arquivo de configuração."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'HOSPITAL' in config:
            return config['HOSPITAL'].get('cnpj', '25062282000182')
    return '25062282000182'  # Valor padrão

def obter_nome_hospital():
    """Obtém o nome do hospital do arquivo de configuração."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'HOSPITAL' in config:
            return config['HOSPITAL'].get('nome', 'Hospital XYZ')
    return 'Hospital XYZ'  # Valor padrão

def obter_sigla_hospital():
    """Obtém a sigla do hospital do arquivo de configuração."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'HOSPITAL' in config:
            return config['HOSPITAL'].get('sigla', 'HXYZ')
    return 'HXYZ'  # Valor padrão

def obter_info_destino():
    """Obtém as informações de destino do arquivo de configuração."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'DESTINO' in config:
            nome = config['DESTINO'].get('nome', 'Secretaria Municipal de Saude')
            tipo = config['DESTINO'].get('tipo', 'M')
            return nome, tipo
    return 'Secretaria Municipal de Saude', 'M'  # Valores padrão

def calcular_idade(data_nascimento, data_referencia):
    """Calcula a idade em anos entre duas datas."""
    if not data_nascimento or not data_referencia:
        return 0
    
    idade = data_referencia.year - data_nascimento.year
    # Verifica se já fez aniversário no ano de referência
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    
    # Limitar entre 0 e 130 anos
    return max(0, min(idade, 130))

def formato_data(data, formato="%Y%m%d"):
    """Formata uma data conforme o formato especificado."""
    if not data:
        return "00000000"
    try:
        return data.strftime(formato)
    except:
        return "00000000"

def limpar_numerico(valor, tamanho=0):
    """Remove caracteres não numéricos e preenche com zeros à esquerda."""
    if not valor:
        return "0" * tamanho if tamanho > 0 else ""
    
    # Remover caracteres não numéricos
    valor_limpo = "".join(filter(str.isdigit, str(valor)))
    
    # Preencher com zeros à esquerda se necessário
    if tamanho > 0:
        return valor_limpo.zfill(tamanho)[:tamanho]
    
    return valor_limpo

def ajustar_texto(texto, tamanho):
    """Ajusta um texto para o tamanho especificado, completando com espaços."""
    if not texto:
        return " " * tamanho
    
    # Remover caracteres de controle e ajustar para ASCII
    texto_limpo = "".join(c if c.isprintable() else " " for c in str(texto))
    
    # Preencher com espaços à direita
    return texto_limpo.ljust(tamanho)[:tamanho]

def mapear_tipo_logradouro(tipo_logradouro, endereco=None):
    """Mapeia ou infere o tipo de logradouro."""
    # Se já tiver um tipo de logradouro válido
    if tipo_logradouro:
        if str(tipo_logradouro).isdigit():
            return str(tipo_logradouro).zfill(3)[:3]
        return str(tipo_logradouro).ljust(3)[:3]
    
    # Tentar inferir do endereço
    if endereco:
        endereco_lower = endereco.lower().strip()
        if endereco_lower.startswith("rua"):
            return "001"
        elif endereco_lower.startswith("av") or endereco_lower.startswith("avenida"):
            return "002"
        elif endereco_lower.startswith("pç") or endereco_lower.startswith("praça"):
            return "003"
        # Adicionar outros tipos conforme necessário
    
    return "   "  # Em branco se não puder determinar

def mapear_raca(raca):
    """Mapeia o valor de raça para o código correspondente."""
    if not raca:
        return "  "  # Em branco
    
    # Se já for um valor numérico
    if str(raca).isdigit():
        raca_val = int(raca)
        if raca_val in [1, 2, 3, 4, 5, 99]:
            return f"{raca_val:02d}"
    
    # Mapear texto para código
    raca_lower = str(raca).lower()
    if "branc" in raca_lower:
        return "01"
    elif "pret" in raca_lower:
        return "02"
    elif "pard" in raca_lower:
        return "03"
    elif "amar" in raca_lower:
        return "04"
    elif "ind" in raca_lower:
        return "05"
    elif "sem" in raca_lower or "não inf" in raca_lower:
        return "99"
    
    return "  "  # Em branco se não puder determinar

def formatar_cns(cns):
    """Formata um número de CNS para o padrão BPA-I (15 dígitos)."""
    if not cns:
        return " " * 15
    # Limpa caracteres não numéricos
    cns_limpo = ''.join(filter(str.isdigit, str(cns)))
    # Ajusta para 15 dígitos, completando com espaços à direita
    return cns_limpo.ljust(15)[:15]

def formatar_cbo(cbo):
    """Formata um código CBO para o padrão BPA-I (6 caracteres)."""
    if not cbo:
        return " " * 6
    # Limpa caracteres não alfanuméricos
    cbo_limpo = ''.join(filter(str.isalnum, str(cbo)))
    # Ajusta para 6 caracteres
    return cbo_limpo.ljust(6)[:6]

def formatar_procedimento(codigo):
    """Formata um código de procedimento para o padrão BPA-I (10 dígitos)."""
    if not codigo:
        return "0" * 10
    # Limpa caracteres não numéricos
    codigo_limpo = ''.join(filter(str.isdigit, str(codigo)))
    # Ajusta para 10 dígitos, completando com zeros à esquerda
    return codigo_limpo.zfill(10)[:10]

def formatar_cpf(cpf):
    """Formata um CPF para o padrão BPA-I (11 dígitos)."""
    if not cpf:
        return " " * 11
    # Limpa caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    # Ajusta para 11 dígitos
    return cpf_limpo.zfill(11)[:11]