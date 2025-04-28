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
    """Busca no banco de dados todos os atendimentos e procedimentos da competência (mês/ano) especificada."""
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
        if mes == 12:
            ano_seguinte, mes_seguinte = ano + 1, 1
        else:
            ano_seguinte, mes_seguinte = ano, mes + 1
        ultimo_dia = datetime.date(ano_seguinte, mes_seguinte, 1) - datetime.timedelta(days=1)
        
        # Consulta SQL melhorada para tratar todas as relações entre tabelas
        query = f"""
        SET search_path TO {DB_SCHEMA};
        SELECT 
            -- Campos da ficha
            f.id_fia,
            f.data_atendimento,
            f.matricula AS cns_paciente,
            f.cid AS cid10,
            f.cod_municipio AS municipio_codigo,
            f.cod_caten AS carater_atend,
            f.numero_autorizacao AS num_autorizacao,
            f.idade_paciente AS idade,
            -- Valores padrão para campos de equipe não existentes
            0 AS equipe_seq,
            0 AS equipe_area,
            0 AS ine,
            f.cod_cep AS cep_paciente,
            f.cod_logradouro AS tipo_logradouro,
            f.num_end_resp AS numero_endereco,
            
            -- Dados do paciente
            p.nm_paciente AS nome_paciente,
            p.data_nasc AS data_nascimento,
            CASE WHEN p.cod_sexo = 1 THEN 'M' ELSE 'F' END AS sexo,
            p.cod_raca_etnia AS raca,
            p.cod_etnia_indigena AS etnia,
            p.cod_nacionalidade AS nacionalidade,
            p.cpf_paciente,
            p.fone_cel_1 AS telefone_celular,
            p.fone_res_1 AS telefone_residencial,
            p.email,
            
            -- Dados do prestador
            pr.nm_prestador AS nome_prestador,
            pr.cns AS cns_profissional,
            pr.cod_cbo_resp,
            
            -- Endereço
            e.pac_logradouro AS endereco,
            e.complemento,
            e.pac_bairro AS bairro,
            e.pac_cep AS cep_endereco,
            
            -- Dados do lançamento
            l.id_lancamento,
            l.quantidade,
            l.cod_cbo,
            l.cod_serv,
            l.data AS data_lancamento,
            l.cnpj_fabricante_aih,
            
            -- Procedimento
            proc.codigo_procedimento AS cod_procedimento
            
        FROM ficha_amb_int f
        LEFT JOIN pacientes p ON p.id_paciente = f.cod_paciente
        LEFT JOIN prestadores pr ON pr.id_prestador = f.cod_medico
        -- Join com endereços (apenas os ativos)
        LEFT JOIN (
            SELECT * FROM enderecos 
            WHERE ativo = true
        ) e ON e.cod_paciente = p.id_paciente
        -- Join com lançamentos
        LEFT JOIN lancamentos l ON l.cod_conta = f.id_fia
        -- Join com procedimentos
        LEFT JOIN procedimentos proc ON proc.id_procedimento = l.cod_proc
        WHERE f.data_atendimento BETWEEN %s AND %s
          AND f.ativo = true
          AND (l.ativo IS NULL OR l.ativo = true)
        ORDER BY f.data_atendimento, f.id_fia
        """
        
        # Executar a consulta
        cur.execute(query, (primeiro_dia, ultimo_dia))
        col_names = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        # Transformar resultado em lista de dicionários
        for row in rows:
            reg = dict(zip(col_names, row))
            registros.append(reg)

    except Exception as e:
        print(f"Erro ao consultar banco: {e}")
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