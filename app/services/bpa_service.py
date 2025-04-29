#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serviço para geração de arquivos BPA-I
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from app.models.header import HeaderBPA
from app.utils.config import Settings

# Logger
logger = logging.getLogger(__name__)

class BPAService:
    """
    Serviço para geração de arquivos BPA-I
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
    
    def generate_bpa(self, records: List[Dict[str, Any]], header: HeaderBPA) -> str:
        """
        Gera um arquivo BPA-I
        
        Args:
            records: Lista de registros a serem exportados
            header: Dados do cabeçalho
            
        Returns:
            Caminho do arquivo BPA-I gerado
        """
        try:
            # Gera o nome do arquivo com competência
            filename = f"BPA_I_{header.cnes}_{header.competencia}.txt"
            filepath = self.export_dir / filename
            
            # Verifica se há registros para exportar
            if not records:
                logger.warning("Nenhum registro para exportar.")
                return str(filepath)
            
            # Preparação dos dados para o formato BPA-I
            with open(filepath, 'w', encoding='utf-8') as file:
                # Escreve o cabeçalho do arquivo (tipo 01)
                header_line = self._format_header(header)
                file.write(header_line + '\n')
                
                # Escreve os registros (tipo 03 - BPA-I individualizado)
                for i, record in enumerate(records, 1):
                    line = self._format_record_bpa_i(record, i, header)
                    file.write(line + '\n')
            
            logger.info(f"Arquivo BPA-I gerado com sucesso: {filepath}")
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo BPA-I: {str(e)}")
            raise
    
    def _format_header(self, header: HeaderBPA) -> str:
        """
        Formata a linha de cabeçalho do arquivo BPA-I (tipo 01)
        
        Args:
            header: Dados do cabeçalho
            
        Returns:
            Linha de cabeçalho formatada
        """
        try:
            # Formato padrão do cabeçalho do BPA-I conforme layout oficial
            # Campos conforme documentação técnica
            cbc_hdr = "01"                             # Tipo de registro (01 = cabeçalho)
            cbc_hdr_id = "#BPA#"                       # Indicador do início do cabeçalho
            cbc_mvm = header.competencia               # Competência (AAAAMM)
            cbc_lin = "000000"                         # Número de linhas do BPA
            cbc_flh = "000000"                         # Quantidade de folhas
            cbc_smt_vrf = "0000"                       # Campo de controle
            cbc_rsp = header.orgao_emissor.ljust(30)   # Órgão responsável pela informação
            cbc_sgl = "".ljust(6)                      # Sigla do órgão
            cbc_cgccpf = "00000000000000"              # CGC/CPF (14 posições)
            cbc_dst = "SECRETARIA MUNICIPAL DE SAUDE".ljust(40)  # Órgão destino
            cbc_dst_in = "M"                           # Indicador do órgão destino (M=Municipal)
            cbc_versao = "V2.0.0".ljust(10)            # Versão do sistema
            
            # Constrói a linha completa do cabeçalho
            header_line = (
                f"{cbc_hdr}"
                f"{cbc_hdr_id}"
                f"{cbc_mvm}"
                f"{cbc_lin}"
                f"{cbc_flh}"
                f"{cbc_smt_vrf}"
                f"{cbc_rsp}"
                f"{cbc_sgl}"
                f"{cbc_cgccpf}"
                f"{cbc_dst}"
                f"{cbc_dst_in}"
                f"{cbc_versao}"
            )
            
            return header_line
        except Exception as e:
            logger.error(f"Erro ao formatar cabeçalho: {str(e)}")
            raise
    
    def _format_record_bpa_i(self, record: Dict[str, Any], seq: int, header: HeaderBPA) -> str:
        """
        Formata uma linha de registro do arquivo BPA-I (tipo 03)
        
        Args:
            record: Registro a ser formatado
            seq: Número sequencial do registro
            header: Dados do cabeçalho
            
        Returns:
            Linha de registro formatada
        """
        try:
            # Identificador do registro tipo 03 (BPA-I)
            prd_ident = "03"
            
            # CNES do estabelecimento
            prd_cnes = str(header.cnes).zfill(7)
            
            # Competência (AAAAMM)
            prd_cmp = header.competencia
            
            # CNS do Profissional (15 posições)
            prd_cnsmed = str(record.get('cns_profissional', '')).ljust(15)[:15]
            
            # CBO do profissional (6 posições)
            prd_cbo = str(record.get('cbo', '')).ljust(6)[:6]
            
            # Data de atendimento (AAAAMMDD)
            prd_dtaten = ""
            data_raw = record.get('data_atendimento') or record.get('data')
            if data_raw:
                if isinstance(data_raw, str):
                    # Se a data já é uma string, formata adequadamente
                    data_parts = data_raw.split('-')
                    if len(data_parts) == 3:
                        prd_dtaten = f"{data_parts[0]}{data_parts[1]}{data_parts[2]}"
                else:
                    # Se é um objeto date/datetime
                    prd_dtaten = data_raw.strftime("%Y%m%d")
            
            # Número da folha do BPA (3 posições)
            prd_flh = str(seq % 999).zfill(3)
            
            # Número sequencial da linha na folha (2 posições)
            prd_seq = str(seq % 99).zfill(2)
            
            # Código do procedimento (10 posições)
            prd_pa = str(record.get('procedimento', '')).zfill(10)[:10]
            
            # CNS do paciente (15 posições)
            prd_cnspac = str(record.get('cns_paciente', '')).ljust(15)[:15]
            
            # Sexo do paciente (1 posição)
            prd_sexo = str(record.get('sexo', 'M'))[:1]
            
            # Código IBGE do município (6 posições)
            prd_ibge = "".ljust(6)
            
            # CID-10 (4 posições)
            prd_cid = str(record.get('cid', '')).ljust(4)[:4]
            
            # Idade do paciente (3 posições)
            prd_idade = "000"
            
            # Quantidade (6 posições)
            try:
                qtd = float(record.get('quantidade', 1) or 1)
                prd_qt = str(int(qtd * 100)).zfill(6)  # Formata como 4 dígitos inteiros + 2 decimais
            except (ValueError, TypeError):
                prd_qt = "000100"  # 1.00 padrão
            
            # Caráter do atendimento (2 posições)
            prd_caten = str(record.get('carater_atendimento', '01')).zfill(2)[:2]
            
            # Número da autorização (13 posições)
            prd_naut = "".ljust(13)
            
            # Origem das informações (3 posições)
            prd_org = "BPA"
            
            # Nome completo do paciente (30 posições)
            prd_nmpac = str(record.get('nome_paciente', '')).ljust(30)[:30]
            
            # Data de nascimento do paciente (8 posições)
            prd_dtnasc = str(record.get('data_nascimento', '')).ljust(8)[:8]
            
            # Raça/Cor do paciente (2 posições)
            prd_raca = "99"  # 99 = Sem informação
            
            # Etnia do paciente (4 posições)
            prd_etnia = "".ljust(4)
            
            # Nacionalidade do paciente (3 posições)
            prd_nac = "010"  # 010 = Brasileiro
            
            # Código do serviço (3 posições)
            prd_srv = "".ljust(3)
            
            # Código da classificação (3 posições)
            prd_clf = "".ljust(3)
            
            # Código da sequência da equipe (8 posições)
            prd_equipe_seq = "".ljust(8)
            
            # Código da área da equipe (4 posições)
            prd_equipe_area = "".ljust(4)
            
            # Constrói a linha completa do registro
            record_line = (
                f"{prd_ident}"
                f"{prd_cnes}"
                f"{prd_cmp}"
                f"{prd_cnsmed}"
                f"{prd_cbo}"
                f"{prd_dtaten}"
                f"{prd_flh}"
                f"{prd_seq}"
                f"{prd_pa}"
                f"{prd_cnspac}"
                f"{prd_sexo}"
                f"{prd_ibge}"
                f"{prd_cid}"
                f"{prd_idade}"
                f"{prd_qt}"
                f"{prd_caten}"
                f"{prd_naut}"
                f"{prd_org}"
                f"{prd_nmpac}"
                f"{prd_dtnasc}"
                f"{prd_raca}"
                f"{prd_etnia}"
                f"{prd_nac}"
                f"{prd_srv}"
                f"{prd_clf}"
                f"{prd_equipe_seq}"
                f"{prd_equipe_area}"
            )
            
            return record_line
        except Exception as e:
            logger.error(f"Erro ao formatar registro BPA-I: {str(e)}")
            # Em caso de erro, retorna uma linha vazia para não interromper o processo
            return ""