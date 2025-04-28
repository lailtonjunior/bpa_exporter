#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de validação de dados para o Exportador BPA-I.
"""

def validar_cnpj(cnpj):
    """Valida um CNPJ."""
    # Limpar o CNPJ, deixando apenas os dígitos
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    
    # Verificar se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verificar se todos os dígitos são iguais
    if len(set(cnpj)) == 1:
        return False
    
    # Aqui poderia implementar o algoritmo completo de validação do CNPJ
    # Para simplificar, apenas verificamos o comprimento e a diversidade de dígitos
    
    return True

def validar_cnes(cnes):
    """Valida um código CNES."""
    # Limpar o CNES, deixando apenas os dígitos
    cnes = ''.join(filter(str.isdigit, str(cnes)))
    
    # Verificar se tem 7 dígitos
    if len(cnes) != 7:
        return False
    
    # Aqui poderia implementar a validação do dígito verificador do CNES
    # Para simplificar, apenas verificamos o comprimento
    
    return True

def validar_cns(cns):
    """Valida um número de Cartão Nacional de Saúde (CNS)."""
    # Limpar o CNS, deixando apenas os dígitos
    cns = ''.join(filter(str.isdigit, str(cns)))
    
    # Verificar se tem 15 dígitos
    if len(cns) != 15:
        return False
    
    # Aqui poderia implementar o algoritmo completo de validação do CNS
    # Para simplificar, apenas verificamos o comprimento
    
    return True

def validar_cbo(cbo):
    """Valida um código CBO (Classificação Brasileira de Ocupações)."""
    # Limpar o CBO, deixando apenas alfanuméricos
    cbo = ''.join(filter(str.isalnum, str(cbo)))
    
    # Verificar se tem 6 caracteres
    if len(cbo) != 6:
        return False
    
    return True

def validar_campo_data(data_str):
    """Valida uma data no formato AAAAMMDD."""
    if not data_str or len(data_str) != 8:
        return False
    
    if not data_str.isdigit():
        return False
    
    # Extrair componentes da data
    try:
        ano = int(data_str[0:4])
        mes = int(data_str[4:6])
        dia = int(data_str[6:8])
        
        # Validações básicas
        if ano < 1900 or ano > 2100:
            return False
        
        if mes < 1 or mes > 12:
            return False
        
        # Dias por mês (simplificado)
        dias_por_mes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if dia < 1 or dia > dias_por_mes[mes]:
            return False
        
        # Para fevereiro em anos não bissextos
        if mes == 2 and dia == 29:
            if not (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)):
                return False
        
        return True
    except:
        return False

def validar_procedimento(codigo):
    """Valida um código de procedimento SIA/SUS."""
    # Limpar o código, deixando apenas os dígitos
    codigo = ''.join(filter(str.isdigit, str(codigo)))
    
    # Verificar se tem 10 dígitos
    if len(codigo) != 10:
        return False
    
    # Aqui poderia implementar a validação do dígito verificador
    # Para simplificar, apenas verificamos o comprimento
    
    return True

def validar_competencia(competencia):
    """Valida uma competência no formato AAAAMM."""
    if not competencia or len(competencia) != 6 or not competencia.isdigit():
        return False
    
    ano = int(competencia[0:4])
    mes = int(competencia[4:6])
    
    # Validações básicas
    if ano < 1990 or ano > 2100:
        return False
    
    if mes < 1 or mes > 12:
        return False
    
    return True