#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rotas para gerenciar configurações do BPA Exporter
"""

import json
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.utils.config import get_settings, Settings

# Logger
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/config", tags=["Configurações"])

# Modelos de dados
class MappingField(BaseModel):
    """Modelo para campo de mapeamento"""
    table: str
    field: str
    fixedValue: str = ""

class MappingSection(BaseModel):
    """Modelo para seção de mapeamento"""
    fields: Dict[str, MappingField]

class MappingConfig(BaseModel):
    """Modelo para configuração de mapeamento"""
    header: Dict[str, MappingField]
    record: Dict[str, MappingField]
    
class DefaultValues(BaseModel):
    """Modelo para valores padrão configuráveis"""
    cnes: str = "2560372"
    orgao_emissor: str = "SECRETARIA MUNICIPAL DE SAUDE"
    carater_atendimento: str = "01"
    nacionalidade: str = "010"
    origem: str = "BPA"

# Rotas
@router.get("/bpa-mapping", response_model=MappingConfig)
async def get_bpa_mapping(settings: Settings = Depends(get_settings)):
    """
    Obtém a configuração atual de mapeamento BPA-I
    
    Returns:
        Configuração de mapeamento atual
    """
    try:
        # Tenta ler a configuração do arquivo
        try:
            with open(settings.export_dir / "bpa_mapping.json", "r", encoding="utf-8") as file:
                config = json.load(file)
                return MappingConfig(**config)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou for inválido, retorna a configuração padrão
            return get_default_mapping(settings)
    except Exception as e:
        logger.error(f"Erro ao obter configuração de mapeamento BPA-I: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração de mapeamento BPA-I: {str(e)}"
        )

@router.post("/bpa-mapping", response_model=MappingConfig)
async def save_bpa_mapping(
    config: MappingConfig,
    settings: Settings = Depends(get_settings)
):
    """
    Salva a configuração de mapeamento BPA-I
    
    Args:
        config: Configuração de mapeamento a ser salva
        
    Returns:
        Configuração de mapeamento salva
    """
    try:
        # Salva a configuração em arquivo
        with open(settings.export_dir / "bpa_mapping.json", "w", encoding="utf-8") as file:
            json.dump(config.dict(), file, ensure_ascii=False, indent=2)
        
        logger.info(f"Configuração de mapeamento BPA-I salva com sucesso")
        
        return config
    except Exception as e:
        logger.error(f"Erro ao salvar configuração de mapeamento BPA-I: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar configuração de mapeamento BPA-I: {str(e)}"
        )

@router.get("/defaults", response_model=DefaultValues)
async def get_defaults(settings: Settings = Depends(get_settings)):
    """
    Obtém os valores padrão configuráveis
    
    Returns:
        Valores padrão configuráveis
    """
    try:
        # Tenta ler os valores padrão do arquivo
        try:
            with open(settings.export_dir / "bpa_defaults.json", "r", encoding="utf-8") as file:
                defaults = json.load(file)
                return DefaultValues(**defaults)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou for inválido, retorna os valores padrão
            return DefaultValues(
                cnes=settings.default_cnes,
                orgao_emissor=settings.default_orgao_emissor,
                carater_atendimento="01",
                nacionalidade="010",
                origem="BPA"
            )
    except Exception as e:
        logger.error(f"Erro ao obter valores padrão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter valores padrão: {str(e)}"
        )

@router.post("/defaults", response_model=DefaultValues)
async def save_defaults(
    defaults: DefaultValues,
    settings: Settings = Depends(get_settings)
):
    """
    Salva os valores padrão configuráveis
    
    Args:
        defaults: Valores padrão a serem salvos
        
    Returns:
        Valores padrão salvos
    """
    try:
        # Salva os valores padrão em arquivo
        with open(settings.export_dir / "bpa_defaults.json", "w", encoding="utf-8") as file:
            json.dump(defaults.dict(), file, ensure_ascii=False, indent=2)
        
        logger.info(f"Valores padrão salvos com sucesso")
        
        return defaults
    except Exception as e:
        logger.error(f"Erro ao salvar valores padrão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar valores padrão: {str(e)}"
        )

@router.get("/database-schema")
async def get_database_schema(db: Session = Depends(get_db)):
    """
    Obtém o esquema das tabelas do banco de dados
    
    Returns:
        Esquema das tabelas do banco de dados
    """
    try:
        # Consulta as tabelas do banco de dados
        tables_query = """
        SELECT 
            table_name, 
            column_name, 
            data_type 
        FROM 
            information_schema.columns 
        WHERE 
            table_schema = 'sigh'
            AND table_name IN ('ficha_amb_int', 'lancamentos', 'prestadores', 'pacientes')
        ORDER BY 
            table_name, 
            ordinal_position
        """
        
        result = db.execute(tables_query)
        rows = result.fetchall()
        
        # Organiza os resultados por tabela
        schema = {}
        for row in rows:
            table_name, column_name, data_type = row
            
            if table_name not in schema:
                schema[table_name] = []
            
            schema[table_name].append({
                "name": column_name,
                "type": data_type
            })
        
        return schema
    except Exception as e:
        logger.error(f"Erro ao obter esquema do banco de dados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter esquema do banco de dados: {str(e)}"
        )

# Funções utilitárias
def get_default_mapping(settings: Settings) -> MappingConfig:
    """
    Obtém a configuração de mapeamento padrão
    
    Args:
        settings: Configurações da aplicação
        
    Returns:
        Configuração de mapeamento padrão
    """
    return MappingConfig(
        header={
            "cnes": MappingField(table="ficha_amb_int", field="cod_hospital", fixedValue=""),
            "competencia": MappingField(table="calculated", field="from_data_atendimento", fixedValue=""),
            "orgao_emissor": MappingField(table="fixed", field="", fixedValue=settings.default_orgao_emissor),
        },
        record={
            "cns_paciente": MappingField(table="ficha_amb_int", field="matricula", fixedValue=""),
            "cns_profissional": MappingField(table="prestadores", field="cns", fixedValue=""),
            "cbo": MappingField(table="lancamentos", field="cod_cbo", fixedValue=""),
            "data_atendimento": MappingField(table="ficha_amb_int", field="data_atendimento", fixedValue=""),
            "procedimento": MappingField(table="lancamentos", field="cod_proc", fixedValue=""),
            "quantidade": MappingField(table="lancamentos", field="quantidade", fixedValue=""),
            "cid": MappingField(table="lancamentos", field="cod_cid", fixedValue=""),
            "carater_atendimento": MappingField(table="fixed", field="", fixedValue="01"),
            "sexo_paciente": MappingField(table="fixed", field="", fixedValue=""),
            "nome_paciente": MappingField(table="fixed", field="", fixedValue=""),
            "data_nascimento": MappingField(table="fixed", field="", fixedValue=""),
            "tipo_atendimento": MappingField(table="calculated", field="from_tipo_atend", fixedValue=""),
            "origem": MappingField(table="fixed", field="", fixedValue="BPA"),
        }
    )