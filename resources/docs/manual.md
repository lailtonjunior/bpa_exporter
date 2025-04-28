# Manual do Usuário - Exportador BPA-I

## Introdução

O Exportador BPA-I é um aplicativo desktop desenvolvido para facilitar a exportação de dados ambulatoriais do sistema SIGH para o formato BPA-I (Boletim de Produção Ambulatorial Individualizado) utilizado pelo SIA/SUS.

Este manual orientará você na instalação, configuração e uso correto do aplicativo.

## Instalação

### Requisitos do Sistema

- Sistema Operacional: Windows 7 ou superior / Linux
- PostgreSQL 9.2 ou superior
- Python 3.6 ou superior

### Passos para Instalação

1. Certifique-se de ter o Python instalado em seu sistema
2. Baixe o arquivo ZIP do aplicativo e extraia em uma pasta de sua escolha
3. Abra um terminal ou prompt de comando na pasta extraída
4. Execute o comando: `pip install -r requirements.txt`
5. Após a instalação das dependências, execute: `python exportador.py`

## Configuração Inicial

Antes de usar o aplicativo pela primeira vez, é necessário configurar o acesso ao banco de dados e os parâmetros do estabelecimento.

### Configuração do Banco de Dados

1. No menu principal, clique em "Configurações" > "Conexão ao Banco"
2. Preencha os campos:
   - **Servidor**: endereço do servidor PostgreSQL (ex: localhost)
   - **Porta**: porta do servidor (normalmente 5432)
   - **Nome do Banco**: nome do banco de dados SIGH
   - **Usuário**: usuário com acesso ao banco
   - **Senha**: senha do usuário
   - **Schema**: nome do schema onde estão as tabelas (normalmente "sigh")
3. Clique em "Testar Conexão" para verificar se os dados estão corretos
4. Se o teste for bem-sucedido, clique em "Salvar"

### Configuração dos Parâmetros

1. No menu principal, clique em "Configurações" > "Parâmetros do BPA-I"
2. Preencha os campos:
   - **CNES do Hospital**: código CNES do estabelecimento (7 dígitos)
   - **CNPJ do Hospital**: CNPJ completo (14 dígitos)
   - **Nome do Hospital**: nome completo do estabelecimento
   - **Sigla do Hospital**: sigla ou abreviatura
   - **Órgão de Destino**: nome do órgão destinatário do arquivo
   - **Tipo de Destino**: Municipal ou Estadual
3. Clique em "Salvar"

## Utilização

### Exportar Arquivo BPA-I

1. No menu principal, clique em "Exportar BPA-I"
2. Selecione o mês e ano da competência desejada
3. Escolha a pasta onde o arquivo será salvo (por padrão, a pasta Downloads)
4. Clique em "Exportar"
5. Acompanhe o processo pelo log de operações
6. Ao final, será exibida uma mensagem de sucesso e o caminho do arquivo gerado

### Formato do Arquivo Gerado

O arquivo será salvo no formato PACERIV.XXX, onde XXX é a abreviação do mês (ex: PACERIV.JAN, PACERIV.FEV, etc.). Este arquivo segue rigorosamente o layout do BPA-I definido pelo SIA/SUS.

## Solução de Problemas

### Erro de Conexão

Se ocorrer um erro de conexão ao banco de dados:
1. Verifique se o servidor PostgreSQL está em execução
2. Certifique-se de que as credenciais estão corretas
3. Verifique se o firewall não está bloqueando a conexão
4. Teste a conexão usando outro cliente PostgreSQL

### Nenhum Registro Encontrado

Se a mensagem "Não há registros para o período" for exibida:
1. Verifique se há atendimentos cadastrados na competência selecionada
2. Verifique se a data dos atendimentos está corretamente registrada no banco
3. Confirme se os lançamentos de procedimentos estão vinculados às fichas

### Arquivo com Dados Incorretos

Se o arquivo for gerado mas conter dados incorretos:
1. Verifique as configurações de parâmetros (CNES, CNPJ, etc.)
2. Confira se os dados nas tabelas do banco estão atualizados
3. Verifique se há informações faltantes nos cadastros de pacientes ou profissionais

## Contato e Suporte

Para suporte técnico ou dúvidas sobre o aplicativo, entre em contato:
- Email: cer@cercolinas.com
- Telefone: (63) 99274-0467

## Observações Importantes

- Certifique-se de que os profissionais têm CNS e CBO cadastrados
- Os pacientes devem ter o CNS registrado corretamente
- Os procedimentos devem ter o código SIA/SUS válido
- Recomenda-se fazer um backup dos dados antes de qualquer exportação