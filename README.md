# Exportador BPA-I

Aplicativo desktop para exportação de dados ambulatoriais no formato BPA-I (Boletim de Produção Ambulatorial Individualizado) para o SIA/SUS, utilizando Python com interface gráfica simples.

## Funcionalidades

- Seleção de competência (mês/ano) para filtrar atendimentos
- Escolha da pasta de destino para o arquivo de exportação
- Geração de arquivo de texto seguindo o layout BPA-I do SIA/SUS
- Interface gráfica intuitiva com feedback visual
- Configuração flexível de parâmetros do banco de dados e estabelecimento

## Requisitos

- Python 3.6 ou superior
- PostgreSQL 9.2 ou superior
- Bibliotecas: psycopg2, PySimpleGUI

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:
pip install -r requirements.txt
3. Execute o aplicativo:
python exportador.py

## Configuração

Antes de usar o aplicativo pela primeira vez, configure:

1. **Configurações do Banco de Dados**:
- Host, Porta, Nome do Banco, Usuário, Senha
- Schema onde estão as tabelas

2. **Parâmetros do Estabelecimento**:
- CNES, CNPJ, Nome e Sigla do Hospital
- Órgão de destino do arquivo

## Uso

1. No menu principal, clique em "Exportar BPA-I"
2. Selecione o mês e ano da competência
3. Escolha a pasta onde o arquivo será salvo
4. Clique em "Exportar"
5. Acompanhe o processo pelo log
6. Verifique o arquivo gerado (PACERIV.XXX)

## Estrutura do Projeto
exportador-bpa-i/
│
├── exportador.py             # Script principal com a interface e ponto de entrada
├── config.ini                # Arquivo de configuração para armazenar parâmetros
│
├── modules/                  # Pasta para módulos separados do sistema
│   ├── init.py           # Torna o diretório um pacote Python
│   ├── database.py           # Módulo de conexão e consultas ao banco de dados
│   ├── formatter.py          # Módulo para formatação dos dados no padrão BPA-I
│   ├── generator.py          # Módulo responsável pela geração do arquivo
│   └── validators.py         # Validações de campos e dados
│
├── ui/                       # Componentes de interface do usuário
│   ├── init.py
│   ├── main_window.py        # Janela principal
│   ├── export_window.py      # Tela de exportação
│   └── config_windows.py     # Telas de configuração
│
└── requirements.txt          # Dependências do projeto

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.