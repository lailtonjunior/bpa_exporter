#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar o BPA Exporter em modo CLI

Este script permite executar a exportação para os formatos
CSV, XLSX e BPA-I diretamente da linha de comando, sem
necessidade de iniciar o servidor web.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.services.data_service import DataService
from app.services.export_service import ExportService
from app.services.bpa_service import BPAService
from app.models.header import HeaderBPA
from app.utils.config import get_settings

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

def get_db() -> Session:
    """
    Cria uma nova sessão do banco de dados
    
    Returns:
        Uma sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def export_csv(competencia=None):
    """
    Exporta os dados para CSV
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
    """
    try:
        # Obtém a sessão do banco e configurações
        db = get_db()
        settings = get_settings()
        
        # Inicializa serviços
        data_service = DataService(db)
        export_service = ExportService(settings)
        
        logger.info(f"Iniciando exportação para CSV. Competência: {competencia or 'Todas'}")
        
        # Obtém os dados
        records = data_service.get_records(competencia)
        
        if not records:
            logger.warning("Nenhum registro encontrado para exportação.")
            return
        
        # Exporta para CSV
        csv_path = export_service.export_to_csv(records)
        
        logger.info(f"Exportação para CSV concluída: {csv_path}")
        print(f"Arquivo CSV gerado com sucesso: {csv_path}")
    
    except Exception as e:
        logger.error(f"Erro ao exportar para CSV: {str(e)}")
        print(f"Erro ao exportar para CSV: {str(e)}")
    
    finally:
        db.close()

def export_xlsx(competencia=None):
    """
    Exporta os dados para XLSX
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
    """
    try:
        # Obtém a sessão do banco e configurações
        db = get_db()
        settings = get_settings()
        
        # Inicializa serviços
        data_service = DataService(db)
        export_service = ExportService(settings)
        
        logger.info(f"Iniciando exportação para XLSX. Competência: {competencia or 'Todas'}")
        
        # Obtém os dados
        records = data_service.get_records(competencia)
        
        if not records:
            logger.warning("Nenhum registro encontrado para exportação.")
            return
        
        # Exporta para XLSX
        xlsx_path = export_service.export_to_xlsx(records)
        
        logger.info(f"Exportação para XLSX concluída: {xlsx_path}")
        print(f"Arquivo XLSX gerado com sucesso: {xlsx_path}")
    
    except Exception as e:
        logger.error(f"Erro ao exportar para XLSX: {str(e)}")
        print(f"Erro ao exportar para XLSX: {str(e)}")
    
    finally:
        db.close()

def export_bpa(competencia, cnes, orgao_emissor):
    """
    Exporta os dados para BPA-I
    
    Args:
        competencia: Competência no formato AAAAMM
        cnes: Código CNES do estabelecimento
        orgao_emissor: Órgão emissor
    """
    try:
        # Obtém a sessão do banco e configurações
        db = get_db()
        settings = get_settings()
        
        # Inicializa serviços
        data_service = DataService(db)
        bpa_service = BPAService(settings)
        
        logger.info(f"Iniciando exportação para BPA-I. Competência: {competencia}")
        
        # Verifica os argumentos obrigatórios
        if not competencia or not cnes or not orgao_emissor:
            logger.error("Competência, CNES e órgão emissor são obrigatórios para exportação BPA-I.")
            print("Competência, CNES e órgão emissor são obrigatórios para exportação BPA-I.")
            return
        
        # Cria o objeto de cabeçalho
        header = HeaderBPA.from_competencia(
            cnes=cnes,
            competencia=competencia,
            orgao_emissor=orgao_emissor
        )
        
        # Obtém os dados da competência especificada
        records = data_service.get_records(competencia)
        
        if not records:
            logger.warning(f"Nenhum registro encontrado para a competência {competencia}")
            print(f"Nenhum registro encontrado para a competência {competencia}")
            return
        
        # Gera o arquivo BPA-I
        bpa_path = bpa_service.generate_bpa(records, header)
        
        logger.info(f"Exportação para BPA-I concluída: {bpa_path}")
        print(f"Arquivo BPA-I gerado com sucesso: {bpa_path}")
    
    except Exception as e:
        logger.error(f"Erro ao exportar para BPA-I: {str(e)}")
        print(f"Erro ao exportar para BPA-I: {str(e)}")
    
    finally:
        db.close()

def show_stats(competencia=None):
    """
    Exibe estatísticas sobre os dados disponíveis
    
    Args:
        competencia: Competência no formato AAAAMM (opcional)
    """
    try:
        # Obtém a sessão do banco e configurações
        db = get_db()
        
        # Inicializa serviço de dados
        data_service = DataService(db)
        
        logger.info(f"Obtendo estatísticas. Competência: {competencia or 'Todas'}")
        
        # Obtém estatísticas
        stats = data_service.get_statistics(competencia)
        
        # Exibe as estatísticas
        print(f"\n=== ESTATÍSTICAS BPA EXPORTER ===")
        print(f"Total de fichas: {stats['total_fichas']}")
        print(f"Total de lançamentos: {stats['total_lancamentos']}")
        
        print(f"\nCompetências disponíveis:")
        for comp in stats['competencias_disponiveis']:
            print(f"  - {comp['competencia']}: {comp['registros']} registros")
        
        if competencia:
            print(f"\nCompetência atual: {competencia}")
        
        print("=" * 34)
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        print(f"Erro ao obter estatísticas: {str(e)}")
    
    finally:
        db.close()

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="BPA Exporter - Exportação de dados para BPA-I, CSV e XLSX")
    
    # Cria subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando de estatísticas
    stats_parser = subparsers.add_parser("stats", help="Exibe estatísticas sobre os dados")
    stats_parser.add_argument("--competencia", help="Competência no formato AAAAMM")
    
    # Comando de exportação CSV
    csv_parser = subparsers.add_parser("csv", help="Exporta dados para CSV")
    csv_parser.add_argument("--competencia", help="Competência no formato AAAAMM")
    
    # Comando de exportação XLSX
    xlsx_parser = subparsers.add_parser("xlsx", help="Exporta dados para XLSX")
    xlsx_parser.add_argument("--competencia", help="Competência no formato AAAAMM")
    
    # Comando de exportação BPA-I
    bpa_parser = subparsers.add_parser("bpa", help="Exporta dados para BPA-I")
    bpa_parser.add_argument("--competencia", required=True, help="Competência no formato AAAAMM")
    bpa_parser.add_argument("--cnes", required=True, help="Código CNES do estabelecimento")
    bpa_parser.add_argument("--orgao", required=True, help="Órgão emissor")
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    # Executa o comando apropriado
    if args.command == "stats":
        show_stats(args.competencia)
    
    elif args.command == "csv":
        export_csv(args.competencia)
    
    elif args.command == "xlsx":
        export_xlsx(args.competencia)
    
    elif args.command == "bpa":
        export_bpa(args.competencia, args.cnes, args.orgao)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()