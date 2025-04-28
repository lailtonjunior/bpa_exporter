#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para geração do arquivo BPA-I.
"""

import os
import datetime

from modules.formatter import (
    MES_ABREV, obter_cnes_hospital, obter_cnpj_hospital, 
    obter_nome_hospital, obter_sigla_hospital, obter_info_destino,
    calcular_idade, formato_data, limpar_numerico, ajustar_texto,
    mapear_tipo_logradouro, mapear_raca, formatar_cns, formatar_cbo,
    formatar_procedimento, formatar_cpf
)

def gerar_arquivo_bpa(registros: list, ano: int, mes: int, caminho_pasta: str):
    """Gera o arquivo BPA-I no formato texto, seguindo o layout SIA/SUS, a partir dos registros fornecidos."""
    if registros is None:
        raise Exception("Não foi possível obter registros do banco de dados.")
    # Se não houver registros para o período, não gera arquivo (retorna mensagem indicando isso)
    if len(registros) == 0:
        return None  # indica que não há dados
    
    # Obter configurações
    CNES_CODE = obter_cnes_hospital()
    HOSPITAL_CNPJ = obter_cnpj_hospital()
    nome_hospital = obter_nome_hospital()
    sigla_hospital = obter_sigla_hospital()
    nome_destino, tipo_destino = obter_info_destino()
    
    # Construir nome do arquivo de acordo com o padrão PACERIV.MES
    mes_abrev = MES_ABREV.get(mes, "XXX")
    nome_arquivo = f"PACERIV.{mes_abrev.upper()}"
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    
    # Preparar cálculo do total de linhas e folhas para o cabeçalho
    total_linhas = len(registros)
    # Cada folha comporta 20 linhas (registros) no BPA-I
    linhas_por_folha = 20
    total_folhas = (total_linhas // linhas_por_folha) + (1 if total_linhas % linhas_por_folha != 0 else 0)
    
    # Calcular soma de verificação (somatório dos códigos de procedimento + quantidades)
    soma_proced_qt = 0
    for reg in registros:
        # Somar código do procedimento (numérico) e quantidade
        try:
            cod_proc = int(limpar_numerico(reg.get("cod_procedimento") or 0))
        except:
            # Se o código do procedimento tiver caracteres não numéricos, remover antes de converter
            cod_proc = int(limpar_numerico(reg.get("cod_procedimento") or "0") or 0)
        
        qt = int(reg.get("quantidade") or 0)
        soma_proced_qt += (cod_proc + qt)
    
    resto = soma_proced_qt % 1111
    controle = resto + 1111
    # Garante 4 dígitos (preencher com zeros à esquerda se necessário)
    controle_str = str(controle).zfill(4)
    
    # Montar linha de cabeçalho (Header) – 132 caracteres + CRLF
    ano_mes_proc = f"{ano}{mes:02d}"  # AAAAMM
    header_fields = []
    header_fields.append("01")             # 1-2: Identificador de header
    header_fields.append("#BPA#")          # 3-7: Indicador de início do cabeçalho
    header_fields.append(ano_mes_proc)     # 8-13: Ano e mês de processamento AAAAMM
    header_fields.append(str(total_linhas).zfill(6))   # 14-19: Total de linhas (6 dígitos)
    header_fields.append(str(total_folhas).zfill(6))   # 20-25: Total de folhas (6 dígitos)
    header_fields.append(controle_str)    # 26-29: Campo de controle (4 dígitos)
    # 30-59: Nome do órgão de origem (até 30 caracteres, completar com espaços)
    header_fields.append(ajustar_texto(nome_hospital, 30))
    # 60-65: Sigla do órgão de origem (até 6 caracteres)
    header_fields.append(ajustar_texto(sigla_hospital, 6))
    # 66-79: CNPJ/CPF do prestador de origem (14 dígitos, zeros à esquerda)
    header_fields.append(limpar_numerico(HOSPITAL_CNPJ, 14))
    # 80-119: Nome do órgão de destino (até 40 caracteres)
    header_fields.append(ajustar_texto(nome_destino, 40))
    # 120: Indicador do órgão destino: M = Municipal, E = Estadual
    header_fields.append(tipo_destino)
    # 121-130: Versão do sistema (10 caracteres, livre)
    header_fields.append(ajustar_texto("BPA-EXPORT", 10))
    # 131-132: Fim de linha (CRLF) será adicionado ao escrever no arquivo
    
    header_line = "".join(header_fields)
    
    # Abrir arquivo para escrita em modo texto (newline CRLF por compatibilidade)
    with open(caminho_arquivo, "w", newline="\r\n", encoding="utf-8") as f:
        # Escrever cabeçalho e nova linha
        f.write(header_line + "\r\n")
        
        # Iterar sobre os registros para escrever cada linha de detalhe (produção)
        linha_num = 0
        folha_atual = 1
        seq_na_folha = 0
        
        for reg in registros:
            linha_num += 1
            # Calcular folha atual e sequência:
            seq_na_folha += 1
            if seq_na_folha > linhas_por_folha:
                # nova folha
                folha_atual += 1
                seq_na_folha = 1
            
            # Extrair e formatar campos do registro
            data_atendimento = reg.get("data_atendimento") or reg.get("data_lancamento")
            data_atend_str = formato_data(data_atendimento)
            competencia = ano_mes_proc  # AAAAMM (igual ao filtro)
            
            # CNS do paciente
            cns_paciente = formatar_cns(reg.get("cns_paciente"))
            
            # CNS do profissional
            cns_prof = formatar_cns(reg.get("cns_profissional"))
            
            # CBO do profissional (prioridade: cod_cbo_resp > cod_cbo)
            cbo = formatar_cbo(reg.get("cod_cbo_resp") or reg.get("cod_cbo"))
            
            # Código do procedimento (10 dígitos)
            cod_proc = formatar_procedimento(reg.get("cod_procedimento"))
            
            # Quantidade
            qt = int(reg.get("quantidade") or 0)
            qt_str = str(qt).zfill(6)
            
            # Idade
            idade_val = 0
            if reg.get("idade"):
                try:
                    idade_val = int(reg.get("idade"))
                except:
                    # Se idade estiver em formato não numérico, tenta extrair parte numérica
                    idade_val = int(limpar_numerico(reg.get("idade")) or 0)
            elif reg.get("data_nascimento") and data_atendimento:
                idade_val = calcular_idade(reg["data_nascimento"], data_atendimento)
            
            # Limitar entre 0 e 130 anos
            idade_val = max(0, min(idade_val, 130))
            idade = str(idade_val).zfill(3)
            
            # Sexo
            sexo = (reg.get("sexo") or "").strip().upper()
            sexo = "M" if sexo == "M" else ("F" if sexo == "F" else " ")
            
            # Código IBGE do município de residência
            ibge_code = limpar_numerico(reg.get("municipio_codigo"), 6) or "      "
            
            # CID-10
            cid10 = (reg.get("cid10") or "").replace(".", "").upper()
            cid10 = cid10.ljust(4)[:4]
            
            # Caráter do atendimento
            caten = limpar_numerico(reg.get("carater_atend"), 2) or "  "
            
            # Número de autorização (APAC/AIH)
            naut = limpar_numerico(reg.get("num_autorizacao"), 13) or "             "
            
            # Raça/Cor e Etnia
            raca = mapear_raca(reg.get("raca"))
            
            etnia = ""
            if reg.get("etnia") and raca == "05":  # Etnia só válida se raça for indígena
                etnia = limpar_numerico(reg.get("etnia"), 4)
            else:
                etnia = "    "
            
            # Nome do paciente
            nome_paciente = ajustar_texto(reg.get("nome_paciente"), 30)
            
            # Data de nascimento
            data_nasc_str = formato_data(reg.get("data_nascimento"))
            
            # Endereço e contato
            cep = limpar_numerico(reg.get("cep_paciente") or reg.get("cep_endereco"), 8) or "        "
            tipo_logradouro = mapear_tipo_logradouro(reg.get("tipo_logradouro"), reg.get("endereco"))
            
            endereco = ajustar_texto(reg.get("endereco"), 30)
            complemento = ajustar_texto(reg.get("complemento"), 10)
            
            numero = str(reg.get("numero_endereco") or "").strip()
            if not numero or numero.lower() in ["sn", "s/n"]:
                numero = "SN"
            numero = numero.ljust(5)[:5]
            
            bairro = ajustar_texto(reg.get("bairro"), 30)
            
            # Telefone (prioridade: celular > residencial)
            telefone = limpar_numerico(reg.get("telefone_celular") or reg.get("telefone_residencial"), 11) or "           "
            
            # E-mail
            email = ajustar_texto(reg.get("email"), 40)
            
            # Código da equipe (INE)
            ine = limpar_numerico(reg.get("ine"), 10) or "0000000000"  # 10 zeros se não existir
            equipe_seq = limpar_numerico(reg.get("equipe_seq"), 8) or "00000000"  # 8 zeros se não existir
            equipe_area = limpar_numerico(reg.get("equipe_area"), 4) or "0000"    # 4 zeros se não existir
            
            # CNPJ do fabricante (OPM)
            cnpj_fabricante = limpar_numerico(reg.get("cnpj_fabricante_aih"), 14) or "              "
            
            # CPF do paciente
            cpf_paciente = formatar_cpf(reg.get("cpf_paciente"))
            
            # Montar todos os campos na ordem do layout BPA-I
            campos = [
                "03",                # 1-2: prd-ident (linha de produção individualizada)
                CNES_CODE.zfill(7),  # 3-9: prd-cnes (7 dígitos)
                competencia,         # 10-15: prd-cmp (AAAAMM)
                cns_prof,            # 16-30: prd_cnsmed (CNS do profissional, 15 dígitos)
                cbo,                 # 31-36: prd_cbo (6 caracteres)
                data_atend_str,      # 37-44: prd_dtaten (AAAAMMDD)
                str(folha_atual).zfill(3),  # 45-47: prd-flh (folha, 3 dígitos)
                str(seq_na_folha).zfill(2), # 48-49: prd-seq (sequência, 2 dígitos)
                cod_proc,            # 50-59: prd-pa (código procedimento, 10 dígitos)
                cns_paciente,        # 60-74: prd-cnspac (CNS paciente, 15 dígitos)
                sexo,                # 75: prd-sexo (1 caractere M/F)
                # ... continuação da lista de campos
                cns_paciente,        # 60-74: prd-cnspac (CNS paciente, 15 dígitos)
                sexo,                # 75: prd-sexo (1 caractere M/F)
                ibge_code,           # 76-81: prd-ibge (cód. IBGE município, 6 dígitos ou branco)
                cid10,               # 82-85: prd-cid (CID-10, 4 caracteres)
                idade,               # 86-88: prd-ldade (idade, 3 dígitos)
                qt_str,              # 89-94: prd-qt (quantidade, 6 dígitos)
                caten,               # 95-96: prd-caten (caráter atendimento, 2 dígitos)
                naut,                # 97-109: prd-naut (nº autorização, 13 dígitos)
                "BPA",               # 110-112: prd-org (origem das informações)
                nome_paciente,       # 113-142: prd-nmpac (nome paciente, 30 caracteres)
                data_nasc_str,       # 143-150: prd-dtnasc (data nascimento, 8 dígitos)
                raca,                # 151-152: prd-raca (2 dígitos ou branco)
                etnia,               # 153-156: prd-etnia (4 dígitos ou branco)
                "".ljust(21),        # 157-165: campos reservados ou não utilizados
                equipe_seq,          # 166-173: prd_equipe_Seq (código da sequência da equipe, 8 dígitos)
                equipe_area,         # 174-177: prd_equipe_Area (código da área da equipe, 4 dígitos)
                cnpj_fabricante,     # 178-191: prd_cnpj (CNPJ fabricante, 14 dígitos)
                cep,                 # 192-199: prd_cep_pcnte (CEP do paciente, 8 dígitos)
                tipo_logradouro,     # 200-202: prd_lograd_pcnte (tipo logradouro, 3 dígitos)
                endereco,            # 203-232: prd_end_pcnte (endereço, 30 caracteres)
                complemento,         # 233-242: prd_compl_pcnte (complemento, 10 caracteres)
                numero,              # 243-247: prd_num_pcnte (número ou "SN", 5 caracteres)
                bairro,              # 248-277: prd_bairro_pcnte (bairro, 30 caracteres)
                telefone,            # 278-288: prd_ddtel_pcnte (telefone, 11 dígitos)
                email,               # 289-328: prd_email_pcnte (email, 40 caracteres)
                ine,                 # 329-338: prd_ine (código equipe, 10 dígitos)
                cpf_paciente         # 339-349: prd_cpf_pcnte (CPF do paciente, 11 dígitos)
                # 350-351: prd-fim (CRLF) será adicionado ao escrever a linha
            ]
            
            linha = "".join(campos)
            f.write(linha + "\r\n")
    
    return caminho_arquivo