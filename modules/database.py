#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de conexão com o banco de dados e consultas SQL para o Exportador BPA-I.
"""

import os
import psycopg2
import configparser
import datetime
from pathlib import Path

# Configurações globais do banco de dados
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "bd0553"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_SCHEMA = "sigh"

def carregar_configuracoes_db():
    """Carrega as configurações do banco de dados do arquivo config.ini."""
    global DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, DB_SCHEMA
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'DATABASE' in config:
            DB_HOST = config['DATABASE'].get('host', DB_HOST)
            DB_PORT = config['DATABASE'].getint('port', DB_PORT)
            DB_NAME = config['DATABASE'].get('dbname', DB_NAME)
            DB_USER = config['DATABASE'].get('user', DB_USER)
            DB_PASS = config['DATABASE'].get('password', DB_PASS)
            DB_SCHEMA = config['DATABASE'].get('schema', DB_SCHEMA)

def testar_conexao(host=None, port=None, dbname=None, user=None, password=None):
    """Testa a conexão com o banco de dados usando os parâmetros fornecidos."""
    try:
        conn = psycopg2.connect(
            host=host or DB_HOST,
            port=port or DB_PORT,
            dbname=dbname or DB_NAME,
            user=user or DB_USER,
            password=password or DB_PASS
        )
        conn.close()
        return True, "Conexão bem-sucedida"
    except Exception as e:
        return False, str(e)

def buscar_registros_por_competencia(ano: int, mes: int):
    """
    Busca no banco de dados todos os atendimentos e procedimentos da competência (mês/ano) especificada.
    Retorna uma lista de dicionários com os campos necessários para o BPA-I.
    """
    conn = None
    registros = []
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        
        # Definir período inicial e final da competência
        primeiro_dia = datetime.date(ano, mes, 1)
        # último dia: avançar um mês e subtrair um dia
        if mes == 12:
            ano_seguinte, mes_seguinte = ano + 1, 1
        else:
            ano_seguinte, mes_seguinte = ano, mes + 1
        ultimo_dia = datetime.date(ano_seguinte, mes_seguinte, 1) - datetime.timedelta(days=1)
        
        # Consulta SQL para juntar as tabelas necessárias
        query = f"""
        SET search_path TO {DB_SCHEMA};
        SELECT 
            f.id AS ficha_id,
            f.data_atendimento,
            f.matricula AS cns_paciente,        -- CNS do paciente (matricula)
            p.nome AS nome_paciente,
            p.cns AS cns_paciente_alt,          -- CNS do paciente também armazenado no cadastro (por segurança)
            p.sexo,
            p.raca,
            p.etnia,
            p.data_nascimento,
            p.endereco,
            p.numero,
            p.complemento,
            p.bairro,
            p.cep,
            p.tipo_logradouro,
            p.telefone,
            p.email,
            pr.cns AS cns_profissional,
            pr.cod_cbo_resp,
            pr.cod_cbo,
            l.cod_cbo AS cod_cbo_lanc,          -- CBO informado no lançamento (se houver)
            l.procedimento_id,
            proc.codigo AS cod_procedimento,
            l.quantidade,
            l.data AS data_procedimento,
            f.cid AS cid10,
            f.carater_atend  -- supondo que exista campo de caráter do atendimento
        FROM ficha_amb_int f
        JOIN lancamentos l ON l.ficha_id = f.id
        LEFT JOIN pacientes p ON p.id = f.paciente_id
        LEFT JOIN prestadores pr ON pr.id = f.prestador_id
        LEFT JOIN procedimentos proc ON proc.id = l.procedimento_id
        WHERE f.data_atendimento BETWEEN %s AND %s
          AND l.data BETWEEN %s AND %s;
        """
        cur.execute(query, (primeiro_dia, ultimo_dia, primeiro_dia, ultimo_dia))
        col_names = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        # Transformar resultado em lista de dicionários para fácil acesso por nome
        for row in rows:
            reg = dict(zip(col_names, row))
            registros.append(reg)
    except Exception as e:
        print(f"Erro ao consultar banco: {e}")
        # Podemos também levantar exceção para ser tratada acima, ou retornar lista vazia com erro
        registros = None
    finally:
        if conn:
            conn.close()
    return registros

def salvar_configuracoes_db(host, port, dbname, user, password, schema):
    """Salva as configurações do banco de dados no arquivo config.ini."""
    global DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, DB_SCHEMA
    
    # Atualizar variáveis globais
    DB_HOST = host
    DB_PORT = port
    DB_NAME = dbname
    DB_USER = user
    DB_PASS = password
    DB_SCHEMA = schema
    
    # Salvar em arquivo
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
    config = configparser.ConfigParser()
    
    # Se o arquivo já existe, ler primeiro para preservar outras seções
    if os.path.exists(config_path):
        config.read(config_path)
    
    # Atualizar seção DATABASE
    if 'DATABASE' not in config:
        config['DATABASE'] = {}
    
    config['DATABASE']['host'] = host
    config['DATABASE']['port'] = str(port)
    config['DATABASE']['dbname'] = dbname
    config['DATABASE']['user'] = user
    config['DATABASE']['password'] = password
    config['DATABASE']['schema'] = schema
    
    # Salvar o arquivo
    with open(config_path, 'w') as configfile:
        config.write(configfile)