#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BPA Exporter - Aplicação principal

Aplicação FastAPI para exportação de dados para BPA-I, CSV e XLSX.
Substitui a versão anterior em Flask, oferecendo melhor desempenho e organização.
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.header import HeaderBPA
from app.services.export_service import ExportService
from app.services.bpa_service import BPAService
from app.services.data_service import DataService
from app.utils.config import Settings, get_settings
from app.routes import config_routes

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bpa_exporter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="BPA Exporter",
    description="Exportador de dados para BPA-I, CSV e XLSX",
    version="2.0.0"
)

# Configuração CORS para permitir acesso ao frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas de configuração
app.include_router(config_routes.router)

# Modelos de entrada
class HeaderData(BaseModel):
    """Modelo para os dados de cabeçalho do BPA-I"""
    cnes: str = Field(..., min_length=1, max_length=7, description="Código CNES do estabelecimento")
    competencia: str = Field(..., min_length=6, max_length=6, description="Competência (formato AAAAMM)")
    orgao_emissor: str = Field(..., description="Órgão emissor")

# Rotas
@app.get("/")
async def root():
    """Rota principal da API"""
    return {
        "message": "BPA Exporter API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/export/csv")
async def export_csv(
    db: Session = Depends(get_db),
    competencia: Optional[str] = Query(None, description="Competência no formato AAAAMM"),
    settings: Settings = Depends(get_settings)
):
    """
    Exporta os dados para formato CSV
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
        
    Returns:
        Arquivo CSV para download
    """
    try:
        # Inicializa serviços
        data_service = DataService(db)
        export_service = ExportService(settings)
        
        # Obtém os dados
        records = data_service.get_records(competencia)
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum registro encontrado para exportação"
            )
        
        # Exporta para CSV
        csv_path = export_service.export_to_csv(records)
        
        logger.info(f"Arquivo CSV gerado com sucesso: {csv_path}")
        
        return FileResponse(
            path=csv_path,
            filename=os.path.basename(csv_path),
            media_type="text/csv"
        )
    except Exception as e:
        logger.error(f"Erro ao exportar para CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar para CSV: {str(e)}"
        )

@app.get("/export/xlsx")
async def export_xlsx(
    db: Session = Depends(get_db),
    competencia: Optional[str] = Query(None, description="Competência no formato AAAAMM"),
    settings: Settings = Depends(get_settings)
):
    """
    Exporta os dados para formato XLSX
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
        
    Returns:
        Arquivo XLSX para download
    """
    try:
        # Inicializa serviços
        data_service = DataService(db)
        export_service = ExportService(settings)
        
        # Obtém os dados
        records = data_service.get_records(competencia)
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum registro encontrado para exportação"
            )
        
        # Exporta para XLSX
        xlsx_path = export_service.export_to_xlsx(records)
        
        logger.info(f"Arquivo XLSX gerado com sucesso: {xlsx_path}")
        
        return FileResponse(
            path=xlsx_path,
            filename=os.path.basename(xlsx_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logger.error(f"Erro ao exportar para XLSX: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar para XLSX: {str(e)}"
        )

@app.post("/export/bpa")
async def export_bpa(
    header_data: HeaderData,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Exporta os dados para formato BPA-I
    
    Args:
        header_data: Dados do cabeçalho do BPA-I
        
    Returns:
        Arquivo BPA-I para download
    """
    try:
        # Inicializa serviços
        data_service = DataService(db)
        bpa_service = BPAService(settings)
        
        # Cria o objeto de cabeçalho usando o método da classe
        header = HeaderBPA.from_competencia(
            cnes=header_data.cnes,
            competencia=header_data.competencia,
            orgao_emissor=header_data.orgao_emissor
        )
        
        # Obtém os dados da competência especificada
        records = data_service.get_records(header_data.competencia)
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhum registro encontrado para a competência {header_data.competencia}"
            )
        
        # Gera o arquivo BPA-I
        bpa_path = bpa_service.generate_bpa(records, header)
        
        logger.info(f"Arquivo BPA-I gerado com sucesso: {bpa_path}")
        
        return FileResponse(
            path=bpa_path,
            filename=os.path.basename(bpa_path),
            media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Erro ao exportar para BPA-I: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar para BPA-I: {str(e)}"
        )

@app.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    competencia: Optional[str] = Query(None, description="Competência no formato AAAAMM")
):
    """
    Obtém estatísticas sobre os dados disponíveis
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
        
    Returns:
        Estatísticas dos dados
    """
    try:
        # Inicializa serviço de dados
        data_service = DataService(db)
        
        # Obtém estatísticas
        stats = data_service.get_statistics(competencia)
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

# Configuração para servir arquivos estáticos (frontend)
try:
    app.mount("/app", StaticFiles(directory="frontend/dist", html=True), name="app")
except Exception as e:
    logger.warning(f"Frontend não encontrado: {str(e)}")

# Execução direta da aplicação (para desenvolvimento)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)