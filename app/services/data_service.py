#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serviço de acesso aos dados do banco de dados
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import func, select, join, text
from sqlalchemy.orm import Session

from app.database.connection import reflect_table

# Logger
logger = logging.getLogger(__name__)

class DataService:
    """
    Serviço para acesso aos dados no banco de dados
    """

    def __init__(self, db: Session):
        """
        Inicializa o serviço com uma sessão do banco de dados
        
        Args:
            db: Sessão do SQLAlchemy
        """
        self.db = db
        
        # Reflete as tabelas
        self.ficha_amb_int = reflect_table("ficha_amb_int")
        self.lancamentos = reflect_table("lancamentos")
    
    def get_records(self, competencia: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém os registros para exportação, combinando dados das tabelas ficha_amb_int e lancamentos
        
        Args:
            competencia: Competência no formato AAAAMM (opcional)
            
        Returns:
            Lista de registros (como dicionários)
        """
        try:
            # Monta a consulta SQL como string para maior flexibilidade
            # Seleciona campos específicos relevantes para o BPA-I de ambas as tabelas
            query = """
            SELECT 
                f.id_fia AS numero,
                f.cod_paciente,
                f.cod_convenio,
                f.cod_tp_sus,
                f.cod_grupo_sus,
                f.cod_esp_sus,
                f.data_atendimento,
                f.cod_especialidade,
                l.cod_cid AS cid,
                f.cod_hospital AS cnes,
                f.urgente_eletivo,
                f.tipo_atend,
                f.matricula AS cns_paciente,
                f.cod_medico,
                NULL AS cns_profissional,
                l.cod_cbo AS cbo,
                l.id_lancamento,
                l.cod_proc AS procedimento,
                l.quantidade,
                l.cod_cbo,
                l.tipo_operacao,
                '1' AS carater_atendimento,  -- Valor fixo '1' já que a coluna não existe
                l.data,
                EXTRACT(YEAR FROM f.data_atendimento) || LPAD(EXTRACT(MONTH FROM f.data_atendimento)::text, 2, '0') AS competencia
            FROM 
                sigh.ficha_amb_int f
            JOIN 
                sigh.lancamentos l ON f.id_fia = l.cod_conta
            WHERE
                l.ativo = true
                AND f.ativo = true
            """
            
            # Adiciona filtro por competência, se fornecido
            params = {}
            if competencia:
                query += " AND EXTRACT(YEAR FROM f.data_atendimento) || LPAD(EXTRACT(MONTH FROM f.data_atendimento)::text, 2, '0') = :competencia"
                params["competencia"] = competencia
            
            # Adiciona ordenação para facilitar o processamento
            query += " ORDER BY f.id_fia, l.id_lancamento"
            
            # Executa a consulta
            result = self.db.execute(text(query), params)
            
            # Converte o resultado para lista de dicionários
            records = [dict(row._mapping) for row in result]
            
            logger.info(f"Encontrados {len(records)} registros para exportação")
            
            return records
        except Exception as e:
            logger.error(f"Erro ao obter registros: {str(e)}")
            raise
    
    def get_statistics(self, competencia: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre os dados
        
        Args:
            competencia: Competência no formato AAAAMM (opcional)
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Consulta SQL para estatísticas
            query = """
            SELECT 
                EXTRACT(YEAR FROM f.data_atendimento) || LPAD(EXTRACT(MONTH FROM f.data_atendimento)::text, 2, '0') AS competencia,
                COUNT(DISTINCT f.id_fia) AS total_fichas,
                COUNT(l.id_lancamento) AS total_lancamentos,
                COUNT(DISTINCT f.cod_paciente) AS total_pacientes,
                COUNT(DISTINCT f.cod_medico) AS total_medicos,
                COUNT(DISTINCT l.cod_proc) AS total_procedimentos
            FROM 
                sigh.ficha_amb_int f
            JOIN 
                sigh.lancamentos l ON f.id_fia = l.cod_conta
            WHERE
                l.ativo = true
                AND f.ativo = true
            """
            
            # Adiciona agrupamento por competência
            query += " GROUP BY competencia"
            
            # Adiciona filtro por competência, se fornecido
            params = {}
            if competencia:
                query += " HAVING EXTRACT(YEAR FROM f.data_atendimento) || LPAD(EXTRACT(MONTH FROM f.data_atendimento)::text, 2, '0') = :competencia"
                params["competencia"] = competencia
            
            # Adiciona ordenação
            query += " ORDER BY competencia DESC"
            
            # Executa a consulta
            result = self.db.execute(text(query), params)
            
            # Converte o resultado em lista de dicionários
            stats_by_competencia = [dict(row._mapping) for row in result]
            
            # Obtenção da lista de competências disponíveis
            comp_query = """
            SELECT DISTINCT 
                EXTRACT(YEAR FROM f.data_atendimento) || LPAD(EXTRACT(MONTH FROM f.data_atendimento)::text, 2, '0') AS competencia,
                COUNT(DISTINCT f.id_fia) AS registros
            FROM 
                sigh.ficha_amb_int f
            WHERE 
                f.ativo = true
            GROUP BY 
                competencia
            ORDER BY 
                competencia DESC
            """
            
            # Executa a consulta de competências
            comp_result = self.db.execute(text(comp_query))
            competencias = [dict(row._mapping) for row in comp_result]
            
            # Monta o resultado final
            if competencia and stats_by_competencia:
                stats = stats_by_competencia[0]
                stats["competencias_disponiveis"] = competencias
                stats["competencia_atual"] = competencia
                return stats
            else:
                # Retorna um resumo geral
                total_fichas = sum(stat.get("total_fichas", 0) for stat in stats_by_competencia)
                total_lancamentos = sum(stat.get("total_lancamentos", 0) for stat in stats_by_competencia)
                total_pacientes = sum(stat.get("total_pacientes", 0) for stat in stats_by_competencia)
                total_medicos = sum(stat.get("total_medicos", 0) for stat in stats_by_competencia)
                total_procedimentos = sum(stat.get("total_procedimentos", 0) for stat in stats_by_competencia)
                
                return {
                    "total_fichas": total_fichas,
                    "total_lancamentos": total_lancamentos,
                    "total_pacientes": total_pacientes,
                    "total_medicos": total_medicos,
                    "total_procedimentos": total_procedimentos,
                    "competencias_disponiveis": competencias,
                    "competencia_atual": competencia,
                    "detalhes_por_competencia": stats_by_competencia
                }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise