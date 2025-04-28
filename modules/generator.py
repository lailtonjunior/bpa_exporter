import psycopg2
import datetime
import os
import PySimpleGUI as sg
from pathlib import Path

# ========== Configurações e Parametrizações ==========

# Dados de conexão com o banco PostgreSQL (poderiam ser movidos para um arquivo de config)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "bd0553"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_SCHEMA = "sigh"

# Código fixo do CNES do hospital e CNPJ do hospital (14 dígitos)
CNES_CODE = "2560372"         # CNES do hospital (7 dígitos com DV)
HOSPITAL_CNPJ = "25062282000182"  # CNPJ do hospital para uso no cabeçalho e registros (se aplicável)

# Mapear nome do mês para abreviação de três letras (Português)
MES_ABREV = {
    1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
    7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
}

# Mapear número do mês para nome completo
MES_NOME = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# ========== Função de Conexão e Consulta ao Banco ==========

def buscar_registros_por_competencia(ano: int, mes: int):
    """Busca no banco de dados todos os atendimentos e procedimentos da competência (mês/ano) especificada.
    Retorna uma lista de dicionários com os campos necessários para o BPA-I."""
    conn = None
    registros = []
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        
        # Definir período inicial e final da competência
        primeiro_dia = datetime.date(ano, mes, 1)
        # último dia: avançar um mês e subtrair um dia
        if mes == 12:
            ano_seguinte, mes_seguinte = ano + 1, 1
        else:
            ano_seguinte, mes_seguinte = ano, mes + 1
        ultimo_dia = datetime.date(ano_seguinte, mes_seguinte, 1) - datetime.timedelta(days=1)
        
        # Consulta SQL para juntar as tabelas necessárias.
        # Selecionamos campos já formatados ou calculados conforme necessidade.
        query = f"""
        SET search_path TO {DB_SCHEMA};
        SELECT 
            f.id AS ficha_id,
            f.data_atendimento,
            f.matricula AS cns_paciente,        -- CNS do paciente (matricula)
            p.nome AS nome_paciente,
            p.cns AS cns_paciente_alt,          -- CNS do paciente também armazenado no cadastro (por segurança)
            p.sexo,
            p.raca,
            p.etnia,
            p.data_nascimento,
            p.endereco,
            p.numero,
            p.complemento,
            p.bairro,
            p.cep,
            p.tipo_logradouro,
            p.telefone,
            p.email,
            pr.cns AS cns_profissional,
            pr.cod_cbo_resp,
            pr.cod_cbo,
            l.cod_cbo AS cod_cbo_lanc,          -- CBO informado no lançamento (se houver)
            l.procedimento_id,
            proc.codigo AS cod_procedimento,
            l.quantidade,
            l.data AS data_procedimento,
            f.cid AS cid10,
            f.carater_atend  -- supondo que exista campo de caráter do atendimento
        FROM ficha_amb_int f
        JOIN lancamentos l ON l.ficha_id = f.id
        LEFT JOIN pacientes p ON p.id = f.paciente_id
        LEFT JOIN prestadores pr ON pr.id = f.prestador_id
        LEFT JOIN procedimentos proc ON proc.id = l.procedimento_id
        WHERE f.data_atendimento BETWEEN %s AND %s
          AND l.data BETWEEN %s AND %s;
        """
        cur.execute(query, (primeiro_dia, ultimo_dia, primeiro_dia, ultimo_dia))
        col_names = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        # Transformar resultado em lista de dicionários para fácil acesso por nome
        for row in rows:
            reg = dict(zip(col_names, row))
            registros.append(reg)
    except Exception as e:
        print(f"Erro ao consultar banco: {e}")
        # Podemos também levantar exceção para ser tratada acima, ou retornar lista vazia com erro
        registros = None
    finally:
        if conn:
            conn.close()
    return registros

# ========== Função para Geração do Arquivo BPA-I ==========

def gerar_arquivo_bpa(registros: list, ano: int, mes: int, caminho_pasta: str):
    """Gera o arquivo BPA-I no formato texto, seguindo o layout SIA/SUS, a partir dos registros fornecidos."""
    if registros is None:
        raise Exception("Não foi possível obter registros do banco de dados.")
    # Se não houver registros para o período, não gera arquivo (retorna mensagem indicando isso)
    if len(registros) == 0:
        return None  # indica que não há dados
    
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
            cod_proc = int(reg.get("cod_procedimento") or 0)
        except:
            # Se o código do procedimento tiver caracteres não numéricos, remover antes de converter
            cod_proc = int(''.join(filter(str.isdigit, str(reg.get("cod_procedimento") or "0"))) or 0)
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
    nome_org_origem = "Hospital XYZ"  # Substituir pelo nome real do hospital/origem
    header_fields.append(nome_org_origem.ljust(30)[:30])
    # 60-65: Sigla do órgão de origem (até 6 caracteres)
    sigla_org_origem = "HXYZ"        # Substituir por sigla real
    header_fields.append(sigla_org_origem.ljust(6)[:6])
    # 66-79: CNPJ/CPF do prestador de origem (14 dígitos, zeros à esquerda)
    header_fields.append(HOSPITAL_CNPJ.zfill(14))
    # 80-119: Nome do órgão de destino (até 40 caracteres)
    org_destino = "Secretaria Municipal de Saude"  # Destino (exemplo)
    header_fields.append(org_destino.ljust(40)[:40])
    # 120: Indicador do órgão destino: M = Municipal, E = Estadual
    header_fields.append("M")
    # 121-130: Versão do sistema (10 caracteres, livre)
    header_fields.append("BPA-EXPORT".ljust(10)[:10])
    # 131-132: Fim de linha (CRLF) será adicionado ao escrever no arquivo
    
    header_line = "".join(header_fields)
    
    # Abrir arquivo para escrita em modo texto (newline padrão do OS, assumindo Windows CRLF por compatibilidade)
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
            
            # Extrair campos do registro (com tratamento de nulos e formatação):
            data_atendimento = reg.get("data_atendimento")  # tipo date/datetime
            data_atend_str = data_atendimento.strftime("%Y%m%d") if data_atendimento else "00000000"
            competencia = f"{ano}{mes:02d}"  # AAAAMM (igual ao filtro, pode usar mesmo ano_mes_proc)
            
            # CNS do paciente
            cns_paciente = reg.get("cns_paciente") or reg.get("cns_paciente_alt") or ""
            cns_paciente = "".join(filter(str.isdigit, str(cns_paciente)))  # deixa só números
            # Preencher com espaços se vazio ou ajustar tamanho para 15
            cns_paciente = cns_paciente.ljust(15)[:15]
            
            # CNS do profissional
            cns_prof = reg.get("cns_profissional") or ""
            cns_prof = "".join(filter(str.isdigit, str(cns_prof)))
            cns_prof = cns_prof.ljust(15)[:15]  # 15 dígitos ou espaços
            # CBO do profissional
            cbo = None
            # Prioridade: cod_cbo_resp > cod_cbo (prestador) > cod_cbo_lanc (lancamento)
            if reg.get("cod_cbo_resp"):
                cbo = str(reg["cod_cbo_resp"])
            elif reg.get("cod_cbo"):
                cbo = str(reg["cod_cbo"])
            elif reg.get("cod_cbo_lanc"):
                cbo = str(reg["cod_cbo_lanc"])
            cbo = "".join(filter(str.isalnum, str(cbo))) if cbo else ""
            cbo = cbo.ljust(6)[:6]  # 6 caracteres (alfanumérico)
            
            # Código do procedimento (10 dígitos)
            cod_proc = reg.get("cod_procedimento") or ""
            cod_proc = "".join(filter(str.isdigit, str(cod_proc)))
            cod_proc = cod_proc.zfill(10)[:10]  # completar com zeros à esquerda
            
            # Quantidade
            qt = reg.get("quantidade") or 0
            qt = int(qt) if str(qt).isdigit() else 0
            qt_str = str(qt).zfill(6)  # 6 dígitos, zeros à esquerda
            
            # Idade
            idade = ""
            if reg.get("data_nascimento") and data_atendimento:
                dn = reg["data_nascimento"]
                # Calcular idade na data do atendimento
                idade_val = data_atendimento.year - dn.year - ((data_atendimento.month, data_atendimento.day) < (dn.month, dn.day))
                if idade_val < 0: 
                    idade_val = 0
                idade_val = min(idade_val, 130)
                idade = str(idade_val).zfill(3)
            elif reg.get("data_nascimento") is None:
                # Se não tem data de nascimento, deixar zeros
                idade = "000"
            else:
                idade = ""  # deixa em branco se não pôde calcular
            idade = idade.ljust(3)[:3] if idade != "" else "000"
            
            # Sexo
            sexo = (reg.get("sexo") or "").strip().upper()
            sexo = "M" if sexo.startswith("M") else ("F" if sexo.startswith("F") else " ")
            
            # Código IBGE do município de residência
            ibge_code = ""
            if reg.get("cep") or reg.get("endereco"):
                # Supondo que possamos inferir do CEP ou ter campo específico (não disponível diretamente)
                # Se houvesse campo p.cod_municipio_ibge, usaríamos ele.
                ibge_code = reg.get("cod_municipio_ibge") or ""
            ibge_code = str(ibge_code).zfill(6)[:6] if ibge_code else "      "  # 6 dígitos ou branco
            
            # CID-10
            cid10 = (reg.get("cid10") or "").replace(".", "").upper()
            cid10 = cid10.ljust(4)[:4]  # 4 caracteres (pode ficar branco se não houver)
            
            # Caráter do atendimento
            caten = str(reg.get("carater_atend") or "").zfill(2)[:2] if reg.get("carater_atend") else "  "
            
            # Número de autorização (APAC/AIH)
            naut = str(reg.get("num_autorizacao") or "")
            naut = naut.zfill(13)[:13] if naut else "             "  # 13 dígitos ou em branco
            
            # Raça e Etnia
            raca = ""
            if reg.get("raca"):
                val = str(reg["raca"]).strip()
                # Se for numérico ou código:
                if val.isdigit():
                    raca_val = int(val)
                    if raca_val in [1,2,3,4,5,99]:
                        raca = str(raca_val).zfill(2)
                else:
                    # Mapear textos para código
                    val_lower = val.lower()
                    if "branc" in val_lower: raca = "01"
                    elif "pret" in val_lower: raca = "02"
                    elif "pard" in val_lower: raca = "03"
                    elif "amar" in val_lower: raca = "04"
                    elif "ind" in val_lower: raca = "05"
                    elif "sem" in val_lower or "não inf" in val_lower: raca = "99"
            raca = raca if raca else "  "  # 2 caracteres ou branco
            etnia = ""
            if reg.get("etnia"):
                et = str(reg["etnia"]).strip()
                # Se for numérico (já código de etnia):
                if et.isdigit():
                    etnia = et.zfill(4)  # 4 dígitos
                else:
                    # (Opcional: mapear nome da etnia para código, se aplicável via tabela externa)
                    etnia = "".join(filter(str.isdigit, et))
                    etnia = etnia.zfill(4) if etnia else ""
            # Etnia só válida se raça for indígena (05); se não for, deixa em branco
            etnia = etnia[:4] if raca == "05" and etnia else "    "
            
            # Endereço e contato do paciente
            cep = "".join(filter(str.isdigit, str(reg.get("cep") or "")))
            cep = cep.zfill(8)[:8] if cep else "        "  # 8 dígitos ou branco
            tipo_logradouro = ""
            if reg.get("tipo_logradouro"):
                # Se já for código numérico de logradouro
                tl = str(reg["tipo_logradouro"])
                tipo_logradouro = tl.zfill(3)[:3] if tl.isdigit() else tl.ljust(3)[:3]
            else:
                # Tentar inferir do endereço (ex.: começa com "Rua", "Avenida", etc.) – opcional
                end = (reg.get("endereco") or "").strip().lower()
                if end.startswith("rua"): tipo_logradouro = "001"
                elif end.startswith("av") or end.startswith("avenida"): tipo_logradouro = "002"
                # ... outros tipos conforme necessidade
            tipo_logradouro = tipo_logradouro if tipo_logradouro else "   "
            
            endereco = (reg.get("endereco") or "").strip()
            endereco = endereco.ljust(30)[:30]
            complemento = (reg.get("complemento") or "").strip()
            complemento = complemento.ljust(10)[:10]
            numero = str(reg.get("numero") or "").strip()
            if numero == "" or numero.lower() in ["sn", "s/n"]:
                numero = "SN"  # sem número
            numero = numero.ljust(5)[:5]
            bairro = (reg.get("bairro") or "").strip()
            bairro = bairro.ljust(30)[:30]
            # Telefone (DDD + número)
            telefone = ""
            # Se tivermos DDD separado, combinar. Supondo telefone completo no campo "telefone":
            if reg.get("telefone"):
                tel = "".join(filter(str.isdigit, str(reg["telefone"])))
                telefone = tel[:11]  # pegar até 11 dígitos
            # Ou se não há campo telefone separado no paciente, deixar em branco
            telefone = telefone.ljust(11)[:11] if telefone else "           "
            # E-mail
            email = (reg.get("email") or "").strip()
            email = email.ljust(40)[:40]
            
            # Código da equipe (INE) – não disponível, preenchido com zeros ou branco
            ine = "".zfill(10)  # 10 dígitos (se não houver, deixa "0000000000")
            
            # Data de nascimento do paciente
            data_nasc_str = ""
            if reg.get("data_nascimento"):
                data_nasc_str = reg["data_nascimento"].strftime("%Y%m%d")
            else:
                data_nasc_str = "00000000"  # Se não tem data de nascimento, preencher com zeros
            
            # Montar todos os campos na ordem do layout BPA-I:
            campos = [
                "03",               # 1-2: prd-ident (linha de produção individualizada)
                CNES_CODE.zfill(7), # 3-9: prd-cnes (7 dígitos)
                competencia,        # 10-15: prd-cmp (AAAAMM)
                cns_prof,           # 16-30: prd_cnsmed (CNS do profissional, 15 dígitos)
                cbo,                # 31-36: prd_cbo (6 caracteres)
                data_atend_str,     # 37-44: prd_dtaten (AAAAMMDD)
                str(folha_atual).zfill(3),   # 45-47: prd-flh (folha, 3 dígitos)
                str(seq_na_folha).zfill(2),  # 48-49: prd-seq (sequência, 2 dígitos)
                cod_proc,           # 50-59: prd-pa (código procedimento, 10 dígitos)
                cns_paciente,       # 60-74: prd-cnspac (CNS paciente, 15 dígitos)
                sexo,               # 75: prd-sexo (1 caractere M/F)
                ibge_code,          # 76-81: prd-ibge (cód. IBGE município, 6 dígitos ou branco)
                cid10,              # 82-85: prd-cid (CID-10, 4 caracteres)
                idade,              # 86-88: prd-ldade (idade, 3 dígitos)
                qt_str,             # 89-94: prd-qt (quantidade, 6 dígitos)
                caten,              # 95-96: prd-caten (caráter atendimento, 2 dígitos)
                naut,               # 97-109: prd-naut (nº autorização, 13 dígitos)
                "BPA",              # 110-112: prd-org (origem das informações)
                (reg.get("nome_paciente") or "")[:30].ljust(30),  # 113-142: prd-nmpac (nome paciente)
                data_nasc_str,      # 143-150: prd-dtnasc (data nascimento do paciente)
                raca,               # 151-152: prd-raca (2 dígitos ou branco)
                etnia,              # 153-156: prd-etnia (4 dígitos ou branco)
                # Deixar em branco campos 157-177 (campos reservados ou não utilizados)
                "".ljust(21),       # 157-177: campos reservados
                HOSPITAL_CNPJ if HOSPITAL_CNPJ else "".ljust(14),  # 178-191: prd_cnpj (CNPJ, se aplicável)
                cep,                # 192-199: prd_cep_pcnte (CEP do paciente)
                tipo_logradouro,    # 200-202: prd_lograd_pcnte (tipo logradouro)
                endereco,           # 203-232: prd_end_pcnte (endereço)
                complemento,        # 233-242: prd_compl_pcnte (complemento)
                numero,             # 243-247: prd_num_pcnte (número ou "SN")
                bairro,             # 248-277: prd_bairro_pcnte (bairro)
                telefone,           # 278-288: prd_ddtel_pcnte (telefone)
                email,              # 289-328: prd_email_pcnte (email)
                ine,                # 329-338: prd_ine (código equipe, 10 dígitos)
                # 339-340: prd-fim (CRLF) será adicionado ao escrever a linha
            ]
            
            linha = "".join(campos)
            f.write(linha + "\r\n")
    return caminho_arquivo

# ========== Interface Gráfica (GUI) ==========

def tema_alternativo():
    """Define um tema alternativo para a interface gráfica."""
    return {
        'BACKGROUND': '#f0f0f0',
        'TEXT': '#000000',
        'INPUT': '#ffffff',
        'TEXT_INPUT': '#000000',
        'SCROLL': '#c7e78b',
        'BUTTON': ('#000000', '#A9DB49'),
        'PROGRESS': ('#01826B', '#D0D0D0'),
        'BORDER': 1,
        'SLIDER_DEPTH': 0,
        'PROGRESS_DEPTH': 0,
    }

def executar_interface():
    """Cria e exibe a interface gráfica do aplicativo."""
    # Configurar tema da interface
    sg.theme('SystemDefault')
    # sg.theme_add_new('MeuTema', tema_alternativo())
    # sg.theme('MeuTema')
    
    # Obter ano e mês atual para pré-selecionar
    data_atual = datetime.datetime.now()
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    
    # Lista de meses para o dropdown
    meses_lista = [f"{i:02d} - {MES_NOME[i]}" for i in range(1, 13)]
    mes_selecionado = f"{mes_atual:02d} - {MES_NOME[mes_atual]}"
    
    # Layout da janela
    layout = [
        [sg.Text("Exportação BPA-I - Boletim de Produção Ambulatorial Individualizado", font=("Helvetica", 14), justification='center', expand_x=True)],
        [sg.HorizontalSeparator()],
        [sg.Text("Selecione a competência para exportação:", font=("Helvetica", 11))],
        [
            sg.Text("Mês:", size=(8, 1)),
            sg.Combo(meses_lista, default_value=mes_selecionado, key="combo_mes", size=(20, 1), readonly=True),
            sg.Text("Ano:", size=(8, 1)),
            sg.Spin(values=list(range(2020, 2031)), initial_value=ano_atual, key="spin_ano", size=(6, 1))
        ],
        [sg.Text("_" * 80)],
        [sg.Text("Pasta de destino do arquivo:", font=("Helvetica", 11))],
        [
            sg.Input(key="pasta_saida", size=(50, 1), default_text=str(Path.home() / "Downloads")),
            sg.FolderBrowse("Procurar...", button_color=('white', '#4a6da7'))
        ],
        [sg.Text("_" * 80)],
        [sg.Text("Log de operações:", font=("Helvetica", 11))],
        [sg.Multiline(key="log", size=(70, 10), disabled=True, autoscroll=True, background_color='#f9f9f9')],
        [
            sg.Button("Exportar", size=(15, 1), button_color=('white', '#4a6da7'), font=("Helvetica", 11, "bold")),
            sg.Button("Limpar Log", size=(15, 1), font=("Helvetica", 11)),
            sg.Push(),
            sg.Button("Sair", size=(10, 1), button_color=("white", "firebrick"))
        ]
    ]
    
    janela = sg.Window("Exportador BPA-I", layout, finalize=True, resizable=True, icon=None)
    
    # Loop principal da interface
    while True:
        evento, valores = janela.read()
        
        if evento == sg.WINDOW_CLOSED or evento == "Sair":
            break
        
        elif evento == "Limpar Log":
            janela["log"].update("")
            
        elif evento == "Exportar":
            try:
                # Extrair mês e ano selecionados
                mes_texto = valores["combo_mes"].split(" - ")[0]
                mes_num = int(mes_texto)
                ano_num = int(valores["spin_ano"])
                
                # Verificar pasta de saída
                pasta = valores["pasta_saida"]
                if not pasta or not os.path.isdir(pasta):
                    janela["log"].print("Erro: Pasta de destino inválida!")
                    sg.popup("Por favor, selecione uma pasta de destino válida.", title="Atenção")
                    continue

                janela["log"].print(f"Iniciando exportação para {MES_NOME[mes_num]}/{ano_num}...")
                janela["log"].print(f"Buscando registros no banco de dados...")
                janela.refresh()  # Forçar atualização da interface para mostrar o log imediatamente

                # Buscar registros no banco
                registros = buscar_registros_por_competencia(ano_num, mes_num)

                if registros is None:
                    janela["log"].print("Erro ao consultar o banco de dados. Verifique a conexão.")
                    sg.popup("Erro de conexão com o banco de dados.\nVerifique as configurações e tente novamente.", title="Erro")
                elif len(registros) == 0:
                    janela["log"].print(f"Não foram encontrados registros para {MES_NOME[mes_num]}/{ano_num}.")
                    sg.popup(f"Não há registros para {MES_NOME[mes_num]}/{ano_num}.", title="Informação")
                else:
                    janela["log"].print(f"Encontrados {len(registros)} registros para exportação.")
                    janela["log"].print(f"Gerando arquivo BPA-I...")
                    janela.refresh()  # Atualizar interface

                    try:
                        caminho_arquivo = gerar_arquivo_bpa(registros, ano_num, mes_num, pasta)
                        if caminho_arquivo:
                            janela["log"].print(f"Arquivo gerado com sucesso: {caminho_arquivo}")
                            janela["log"].print(f"Total de registros: {len(registros)}")
                            janela["log"].print(f"Competência: {MES_NOME[mes_num]}/{ano_num}")
                            sg.popup(f"Exportação concluída com sucesso!\nArquivo gerado: {caminho_arquivo}", title="Sucesso")
                        else:
                            janela["log"].print("Não foi possível gerar o arquivo. Verifique o log para mais detalhes.")
                    except Exception as ex:
                        janela["log"].print(f"Erro durante a geração do arquivo: {ex}")
                        sg.popup(f"Ocorreu um erro durante a exportação:\n{ex}", title="Erro")
            except ValueError as e:
                janela["log"].print(f"Erro ao processar os dados: {e}")
                sg.popup(f"Erro ao processar os dados: {e}", title="Erro")
            except Exception as e:
                janela["log"].print(f"Erro inesperado: {e}")
                sg.popup(f"Ocorreu um erro inesperado: {e}", title="Erro")

    janela.close()

# ========== Configuração e Execução do Aplicativo ==========

def configurar_conexao():
    """Permite configurar os parâmetros de conexão com o banco de dados."""
    global DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, DB_SCHEMA
    
    layout = [
        [sg.Text("Configurações de Conexão ao Banco de Dados", font=("Helvetica", 12, "bold"))],
        [sg.Text("Servidor:", size=(15, 1)), sg.Input(DB_HOST, key="host", size=(30, 1))],
        [sg.Text("Porta:", size=(15, 1)), sg.Input(DB_PORT, key="port", size=(30, 1))],
        [sg.Text("Nome do Banco:", size=(15, 1)), sg.Input(DB_NAME, key="dbname", size=(30, 1))],
        [sg.Text("Usuário:", size=(15, 1)), sg.Input(DB_USER, key="user", size=(30, 1))],
        [sg.Text("Senha:", size=(15, 1)), sg.Input(DB_PASS, key="password", size=(30, 1), password_char='*')],
        [sg.Text("Schema:", size=(15, 1)), sg.Input(DB_SCHEMA, key="schema", size=(30, 1))],
        [sg.Button("Salvar", button_color=('white', '#4a6da7')), sg.Button("Testar Conexão"), sg.Button("Cancelar")]
    ]
    
    janela = sg.Window("Configuração do Banco de Dados", layout, modal=True)
    
    while True:
        evento, valores = janela.read()
        if evento in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        
        elif evento == "Testar Conexão":
            try:
                conn = psycopg2.connect(
                    host=valores["host"],
                    port=valores["port"],
                    dbname=valores["dbname"],
                    user=valores["user"],
                    password=valores["password"]
                )
                conn.close()
                sg.popup("Conexão estabelecida com sucesso!", title="Teste de Conexão")
            except Exception as e:
                sg.popup(f"Erro ao conectar: {e}", title="Erro de Conexão")
        
        elif evento == "Salvar":
            # Salvar as configurações
            DB_HOST = valores["host"]
            DB_PORT = valores["port"]
            DB_NAME = valores["dbname"]
            DB_USER = valores["user"]
            DB_PASS = valores["password"]
            DB_SCHEMA = valores["schema"]
            
            # Salvar em arquivo de configuração (opcional)
            # Aqui você pode implementar um código para salvar as configurações em um arquivo
            
            sg.popup("Configurações salvas com sucesso!", title="Configurações")
            break
    
    janela.close()

def configurar_parametros():
    """Permite configurar os parâmetros específicos da exportação BPA-I."""
    global CNES_CODE, HOSPITAL_CNPJ
    
    layout = [
        [sg.Text("Configurações do Estabelecimento", font=("Helvetica", 12, "bold"))],
        [sg.Text("CNES do Hospital:", size=(20, 1)), sg.Input(CNES_CODE, key="cnes", size=(20, 1))],
        [sg.Text("CNPJ do Hospital:", size=(20, 1)), sg.Input(HOSPITAL_CNPJ, key="cnpj", size=(20, 1))],
        [sg.Text("Nome do Hospital:", size=(20, 1)), sg.Input("Hospital XYZ", key="nome_hospital", size=(30, 1))],
        [sg.Text("Sigla do Hospital:", size=(20, 1)), sg.Input("HXYZ", key="sigla_hospital", size=(10, 1))],
        [sg.Text("Órgão de Destino:", size=(20, 1)), sg.Input("Secretaria Municipal de Saude", key="destino", size=(30, 1))],
        [sg.Radio("Municipal", "DESTINO", key="municipal", default=True), sg.Radio("Estadual", "DESTINO", key="estadual")],
        [sg.Button("Salvar", button_color=('white', '#4a6da7')), sg.Button("Cancelar")]
    ]
    
    janela = sg.Window("Configuração dos Parâmetros", layout, modal=True)
    
    while True:
        evento, valores = janela.read()
        if evento in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        
        elif evento == "Salvar":
            # Validar CNES (7 dígitos)
            if not valores["cnes"].isdigit() or len(valores["cnes"]) != 7:
                sg.popup("O CNES deve conter 7 dígitos numéricos.", title="Validação")
                continue
            
            # Validar CNPJ (14 dígitos)
            cnpj = "".join(filter(str.isdigit, valores["cnpj"]))
            if len(cnpj) != 14:
                sg.popup("O CNPJ deve conter 14 dígitos numéricos.", title="Validação")
                continue
            
            # Salvar os parâmetros
            CNES_CODE = valores["cnes"]
            HOSPITAL_CNPJ = cnpj
            
            # Salvar outros parâmetros (implementação opcional)
            # Aqui você pode salvar os outros parâmetros em variáveis globais ou arquivo
            
            sg.popup("Parâmetros salvos com sucesso!", title="Configurações")
            break
    
    janela.close()

def menu_principal():
    """Exibe o menu principal do aplicativo."""
    
    # Definir layout do menu
    menu_def = [
        ['Arquivo', ['Exportar BPA-I', 'Sair']],
        ['Configurações', ['Conexão ao Banco', 'Parâmetros do BPA-I']],
        ['Ajuda', ['Sobre']]
    ]
    
    layout = [
        [sg.Menu(menu_def)],
        [sg.Text("Exportador de BPA-I", font=("Helvetica", 20), justification='center', expand_x=True)],
        [sg.Text("Sistema de exportação de dados para o formato BPA-I", font=("Helvetica", 12), justification='center', expand_x=True)],
        [sg.Image(data=None)],  # Aqui você poderia colocar uma imagem/logo
        [sg.Text("")],
        [sg.Button("Exportar BPA-I", size=(20, 2), button_color=('white', '#4a6da7'), font=("Helvetica", 12))],
        [sg.Text("")],
        [sg.Button("Configurar Conexão", size=(20, 1))],
        [sg.Button("Configurar Parâmetros", size=(20, 1))],
        [sg.Text("")],
        [sg.Button("Sair", size=(10, 1), button_color=("white", "firebrick"))]
    ]
    
    janela = sg.Window("Sistema de Exportação BPA-I", layout, size=(500, 400), finalize=True)
    
    while True:
        evento, valores = janela.read()
        
        if evento in (sg.WINDOW_CLOSED, "Sair"):
            break
        
        elif evento in ("Exportar BPA-I", "Arquivo::Exportar BPA-I"):
            janela.hide()
            executar_interface()
            janela.un_hide()
        
        elif evento in ("Configurar Conexão", "Configurações::Conexão ao Banco"):
            configurar_conexao()
        
        elif evento in ("Configurar Parâmetros", "Configurações::Parâmetros do BPA-I"):
            configurar_parametros()
        
        elif evento == "Ajuda::Sobre":
            sg.popup("""
            Exportador BPA-I v1.0
            
            Sistema para exportação de dados ambulatoriais
            no formato BPA-I (Boletim de Produção Ambulatorial Individualizado)
            seguindo o layout SIA/SUS.
            
            © 2025 - Todos os direitos reservados
            """, title="Sobre o Sistema")
    
    janela.close()

if __name__ == "__main__":
    menu_principal()
    # Alternativamente, se preferir iniciar diretamente a tela de exportação:
    # executar_interface()
    sg.popup("Por favor, selecione a pasta de destino")