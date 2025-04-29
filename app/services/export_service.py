#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serviço para exportação de dados para diferentes formatos
"""

import os
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from app.utils.config import Settings

# Logger
logger = logging.getLogger(__name__)

class ExportService:
    """
    Serviço para exportação de dados para diferentes formatos
    """
    
    def __init__(self, settings: Settings):
        """
        Inicializa o serviço com as configurações da aplicação
        
        Args:
            settings: Configurações da aplicação
        """
        self.settings = settings
        self.export_dir = settings.export_dir
        
        # Garante que o diretório de exportação existe
        if not self.export_dir.exists():
            self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, records: List[Dict[str, Any]]) -> str:
        """
        Exporta os dados para um arquivo CSV
        
        Args:
            records: Lista de registros a serem exportados
            
        Returns:
            Caminho do arquivo CSV gerado
        """
        try:
            # Gera o nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bpa_export_{timestamp}.csv"
            filepath = self.export_dir / filename
            
            # Verifica se há registros para exportar
            if not records:
                logger.warning("Nenhum registro para exportar.")
                return str(filepath)
            
            # Cria o DataFrame e exporta para CSV
            df = pd.DataFrame(records)
            df.to_csv(filepath, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
            
            logger.info(f"Exportação para CSV concluída: {filepath}")
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {str(e)}")
            raise
    
    def export_to_xlsx(self, records: List[Dict[str, Any]]) -> str:
        """
        Exporta os dados para um arquivo XLSX
        
        Args:
            records: Lista de registros a serem exportados
            
        Returns:
            Caminho do arquivo XLSX gerado
        """
        try:
            # Gera o nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bpa_export_{timestamp}.xlsx"
            filepath = self.export_dir / filename
            
            # Verifica se há registros para exportar
            if not records:
                logger.warning("Nenhum registro para exportar.")
                return str(filepath)
            
            # Cria o DataFrame e exporta para XLSX
            df = pd.DataFrame(records)
            
            # Cria o escritor de Excel com o pandas
            writer = pd.ExcelWriter(filepath, engine='openpyxl')
            
            # Escreve os dados na planilha
            df.to_excel(writer, index=False, sheet_name='BPA_Export')
            
            # Ajusta as colunas para melhor visualização
            worksheet = writer.sheets['BPA_Export']
            for i, col in enumerate(df.columns):
                max_width = max(
                    df[col].astype(str).map(len).max(),  # Largura máxima do conteúdo
                    len(str(col))  # Largura do nome da coluna
                ) + 2  # Adiciona um pouco de espaço extra
                
                # Define a largura da coluna
                worksheet.column_dimensions[worksheet.cell(row=1, column=i+1).column_letter].width = max_width
            
            # Salva o arquivo
            writer.close()
            
            logger.info(f"Exportação para XLSX concluída: {filepath}")
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erro ao exportar para XLSX: {str(e)}")
            raise