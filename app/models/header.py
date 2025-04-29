#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modelo para o cabeçalho do BPA-I
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class HeaderBPA:
    """
    Classe que representa o cabeçalho de um arquivo BPA-I
    
    Atributos:
        cnes (str): Código CNES do estabelecimento
        competencia (str): Competência no formato AAAAMM
        orgao_emissor (str): Órgão emissor
        mes_referencia (str): Mês de referência
        ano_referencia (str): Ano de referência
    """
    cnes: str
    competencia: str
    orgao_emissor: str
    mes_referencia: str
    ano_referencia: str
    
    def __post_init__(self):
        """
        Validações após a inicialização
        """
        # Garante que CNES tenha exatamente 7 dígitos
        if len(self.cnes) != 7:
            self.cnes = self.cnes.zfill(7)[:7]
        
        # Garante que competência tenha exatamente 6 dígitos (AAAAMM)
        if len(self.competencia) != 6:
            raise ValueError("Competência deve estar no formato AAAAMM")
        
        # Valida mês e ano de referência
        if len(self.mes_referencia) != 2:
            self.mes_referencia = self.mes_referencia.zfill(2)[:2]
        
        if len(self.ano_referencia) != 4:
            self.ano_referencia = self.ano_referencia.zfill(4)[:4]
    
    @property
    def formatted_competencia(self) -> str:
        """
        Retorna a competência formatada como MM/AAAA
        
        Returns:
            str: Competência formatada
        """
        ano = self.competencia[:4]
        mes = self.competencia[4:]
        return f"{mes}/{ano}"
    
    @property
    def data_geracao(self) -> str:
        """
        Retorna a data de geração formatada como AAAAMMDD
        
        Returns:
            str: Data de geração formatada
        """
        now = datetime.now()
        return now.strftime("%Y%m%d")
    
    @property
    def hora_geracao(self) -> str:
        """
        Retorna a hora de geração formatada como HHMMSS
        
        Returns:
            str: Hora de geração formatada
        """
        now = datetime.now()
        return now.strftime("%H%M%S")
        
    @classmethod
    def from_competencia(cls, cnes: str, competencia: str, orgao_emissor: str) -> 'HeaderBPA':
        """
        Cria um HeaderBPA a partir da competência
        
        Args:
            cnes: Código CNES do estabelecimento
            competencia: Competência no formato AAAAMM
            orgao_emissor: Órgão emissor
            
        Returns:
            HeaderBPA: Objeto de cabeçalho
        """
        ano = competencia[:4]
        mes = competencia[4:]
        
        return cls(
            cnes=cnes,
            competencia=competencia,
            orgao_emissor=orgao_emissor,
            mes_referencia=mes,
            ano_referencia=ano
        )