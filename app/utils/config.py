#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurações da aplicação utilizando Pydantic para validação
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

from pydantic import PostgresDsn, validator, Field
from pydantic_settings import BaseSettings

# Diretório base da aplicação
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações do banco de dados
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_echo: bool = Field(False, env="DB_ECHO")
    db_schema: str = Field("sigh", env="DB_SCHEMA")
    
    # Tabelas a serem refletidas
    db_tables: Dict[str, str] = {
        "ficha_amb_int": "ficha_amb_int",
        "lancamentos": "lancamentos"
    }
    
    # Configurações de exportação
    export_dir: Path = Field(BASE_DIR / "exports", env="EXPORT_DIR")
    
    # Configurações do BPA-I
    default_cnes: str = Field("2560372", env="DEFAULT_CNES")
    default_orgao_emissor: str = Field("SESAU", env="DEFAULT_ORGAO_EMISSOR")
    
    # Outras configurações
    app_name: str = Field("BPA Exporter", env="APP_NAME")
    app_version: str = Field("2.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    
    # Validador para garantir que o diretório de exportação exista
    @validator("export_dir")
    def export_dir_exists(cls, v: Path) -> Path:
        """Valida se o diretório de exportação existe, criando-o se necessário"""
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v
    
    # Configuração do modelo
    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Obtém as configurações da aplicação (cached)
    
    Returns:
        Settings: Objeto de configurações
    """
    return Settings()