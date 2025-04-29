#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de conexão com o banco de dados PostgreSQL
"""

import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.utils.config import get_settings

# Logger
logger = logging.getLogger(__name__)

# Configurações
settings = get_settings()

# Criação da URL de conexão
DATABASE_URL = (
    f"postgresql://{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

# Criação do engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600,   # Reconecta após 1 hora
    echo=settings.db_echo
)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Metadata para refletir tabelas existentes
metadata = MetaData()

# Função para obter conexão com o banco de dados
def get_db() -> Session:
    """
    Cria uma nova sessão do banco de dados e a fecha após o uso
    
    Returns:
        Uma sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para refletir uma tabela do banco de dados
def reflect_table(table_name: str):
    """
    Reflete uma tabela do banco de dados
    
    Args:
        table_name: Nome da tabela a ser refletida
        
    Returns:
        Objeto Table do SQLAlchemy
    """
    try:
        # Verifica se a tabela já está na metadata
        if table_name in metadata.tables:
            return metadata.tables[table_name]
        
        # Reflete a tabela específica
        schema = settings.db_schema
        metadata.reflect(bind=engine, only=[table_name], schema=schema)
        
        # Retorna a tabela com esquema
        full_table_name = f"{schema}.{table_name}"
        return metadata.tables.get(full_table_name)
    except Exception as e:
        logger.error(f"Erro ao refletir tabela {table_name}: {str(e)}")
        raise