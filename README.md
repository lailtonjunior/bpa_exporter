# BPA Exporter

Uma aplicação para exportação de dados do Boletim de Produção Ambulatorial Individualizado (BPA-I), além de formatos CSV e XLSX, diretamente do banco de dados PostgreSQL.

Esta aplicação foi desenvolvida para substituir a versão anterior baseada em Flask, oferecendo melhor desempenho e organização utilizando FastAPI.

## Características

- Conexão com PostgreSQL usando SQLAlchemy, refletindo as tabelas `ficha_amb_int` e `lancamentos`
- Exportação para formatos CSV, XLSX e BPA-I
- Interface de linha de comando (CLI) para uso fácil
- API web para integração com outros sistemas
- Suporte a múltiplas competências
- Logs detalhados para acompanhamento
- Estrutura moderna e modular

## Requisitos

- Python 3.8+
- PostgreSQL
- Tabelas `sigh.ficha_amb_int` e `sigh.lancamentos` no banco de dados

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/bpa_exporter.git
   cd bpa_exporter
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o arquivo `.env`:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações de banco de dados
   ```

## Uso

### Via Linha de Comando (CLI)

#### Mostrar estatísticas
```bash
python run.py stats
# Especificar competência
python run.py stats --competencia 202501
```

#### Exportar para CSV
```bash
python run.py csv
# Especificar competência
python run.py csv --competencia 202501
```

#### Exportar para XLSX
```bash
python run.py xlsx
# Especificar competência
python run.py xlsx --competencia 202501
```

#### Exportar para BPA-I
```bash
python run.py bpa --competencia 202501 --cnes 1234567 --orgao "SECRETARIA MUNICIPAL DE SAUDE"
```

### Via API Web

1. Inicie o servidor:
   ```bash
   python main.py
   # ou
   uvicorn main:app --reload
   ```

2. Acesse a documentação da API:
   ```
   http://localhost:8000/docs
   ```

#### Endpoints Disponíveis

- `GET /`: Página inicial da API
- `GET /health`: Verificação de saúde da API
- `GET /export/csv`: Exporta dados para CSV (parâmetro opcional: `competencia`)
- `GET /export/xlsx`: Exporta dados para XLSX (parâmetro opcional: `competencia`)
- `POST /export/bpa`: Exporta dados para BPA-I (necessário enviar dados de cabeçalho no corpo da requisição)
- `GET /stats`: Obtém estatísticas sobre os dados (parâmetro opcional: `competencia`)

## Estrutura do Projeto

```
bpa_exporter/
│
├── app/                          # Pacote principal da aplicação
│   ├── database/                 # Conexão com banco de dados
│   ├── models/                   # Modelos de dados
│   ├── services/                 # Serviços de negócios
│   └── utils/                    # Utilidades
│
├── docs/                         # Documentação
│   └── layout_bpa.md             # Layout do arquivo BPA-I
│
├── exports/                      # Arquivos exportados
├── logs/                         # Arquivos de log
│
├── main.py                       # Aplicação principal (API)
├── run.py                        # Interface de linha de comando
├── requirements.txt              # Dependências
└── .env                          # Configurações (não versionado)
```

## Configuração de Banco de Dados

A aplicação utiliza o SQLAlchemy para se conectar ao PostgreSQL. As tabelas `sigh.ficha_amb_int` e `sigh.lancamentos` são refletidas automaticamente, sem necessidade de definir estruturas.

Para a correta geração do BPA-I, é necessário que as tabelas contenham os seguintes campos principais:

### Tabela `sigh.ficha_amb_int`
- `id_fia`: Identificador único da ficha
- `cod_paciente`: Código do paciente
- `matricula`: Cartão Nacional de Saúde (CNS) do paciente
- `data_atendimento`: Data do atendimento
- `cod_medico`: Código do médico/profissional
- `cod_cid`: Código CID da doença
- `cod_hospital`: Código CNES do estabelecimento
- `cod_tp_sus`: Código de tipo SUS
- `cod_grupo_sus`: Código de grupo SUS
- `cod_esp_sus`: Código de especialidade SUS
- `tipo_atend`: Tipo de atendimento (AMB, INT, etc.)

### Tabela `sigh.lancamentos`
- `id_lancamento`: Identificador único do lançamento
- `cod_conta`: Código da conta (referência para `id_fia` da tabela `ficha_amb_int`)
- `cod_proc`: Código do procedimento
- `quantidade`: Quantidade do procedimento
- `cod_cbo`: Código da ocupação do profissional
- `carater_atendimento`: Caráter do atendimento (1=Eletivo, 2=Urgência)

### Tabela `sigh.prestadores` (Associada)
- `id_prestador`: Identificador único do prestador
- `cns`: Cartão Nacional de Saúde (CNS) do profissional
- `cbo`: Código da ocupação do profissional

## Formatos de Exportação

### CSV e XLSX
Exporta os campos selecionados das tabelas `ficha_amb_int` e `lancamentos`, com formatação adequada.

### BPA-I
Exporta os dados no formato exigido pelo DATASUS para o BPA-I (Boletim de Produção Ambulatorial Individualizado), seguindo as especificações técnicas do layout oficial. Para mais detalhes, consulte o arquivo `docs/layout_bpa.md`.

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT.