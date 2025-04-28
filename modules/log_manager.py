#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento de logs do Exportador BPA-I.
"""

import os
import logging
import datetime
from pathlib import Path

class LogManager:
    """Classe para gerenciar logs do aplicativo."""
    
    def __init__(self, log_dir=None):
        """Inicializa o gerenciador de logs."""
        if log_dir is None:
            # Usar pasta logs no diretório raiz da aplicação
            self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        else:
            self.log_dir = log_dir
        
        # Garantir que o diretório de logs exista
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configurar logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configura e retorna um logger."""
        # Criar logger
        logger = logging.getLogger('exportador_bpa_i')
        logger.setLevel(logging.DEBUG)
        
        # Definir formato do log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Arquivo de log com data atual
        data_atual = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f'exportador_bpa_i_{data_atual}.log')
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message):
        """Registra uma mensagem informativa."""
        self.logger.info(message)
    
    def error(self, message):
        """Registra uma mensagem de erro."""
        self.logger.error(message)
    
    def warning(self, message):
        """Registra uma mensagem de aviso."""
        self.logger.warning(message)
    
    def debug(self, message):
        """Registra uma mensagem de depuração."""
        self.logger.debug(message)
    
    def get_log_files(self):
        """Retorna uma lista dos arquivos de log disponíveis."""
        return [f for f in os.listdir(self.log_dir) if f.startswith('exportador_bpa_i_') and f.endswith('.log')]