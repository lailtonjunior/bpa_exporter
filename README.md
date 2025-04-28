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

1. Clone o repositório:
git clone https://github.com/seu-usuario/exportador-bpa-i.git
cd exportador-bpa-i

2. Instale as dependências:
pip install -r requirements.txt

3. Execute o aplicativo:
python exportador.py

## Configuração

Antes de usar o aplicativo, configure:

1. **Configurações do Banco de Dados**:
- Host, Porta, Nome do Banco, Usuário, Senha
- Schema onde estão as tabelas

2. **Parâmetros do Estabelecimento**:
- CNES, CNPJ, Nome e Sigla do Hospital
- Órgão de destino do arquivo

## Uso

1. Inicie o aplicativo
2. Selecione o mês e ano da competência
3. Escolha a pasta onde o arquivo será salvo
4. Clique em "Exportar"
5. Acompanhe o processo pelo log
6. Verifique o arquivo gerado (PACERIV.XXX)

## Estrutura do Banco de Dados

O aplicativo espera encontrar as seguintes tabelas no schema configurado:

- **ficha_amb_int**: Tabela principal de atendimentos ambulatoriais
- **lancamentos**: Procedimentos realizados
- **pacientes**: Dados dos pacientes
- **prestadores**: Dados dos profissionais
- **procedimentos**: Catálogo de procedimentos SIA/SUS

## Layout do Arquivo

O arquivo gerado segue o layout oficial do BPA-I, com:

- Cabeçalho (#BPA#)
- Registros individualizados (tipo "03")
- Campos formatados conforme especificação SIA/SUS

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Suporte

Para suporte, abra um issue no repositório ou entre em contato pelo email: seu.email@exemplo.com
Esta estrutura organiza o código de forma modular e facilita a manutenção e evolução do sistema. Cada arquivo tem uma responsabilidade específica, seguindo o princípio de responsabilidade única, e os módulos são reutilizáveis