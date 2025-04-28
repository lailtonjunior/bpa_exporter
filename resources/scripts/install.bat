@echo off
echo === Instalador do Exportador BPA-I ===
echo Verificando requisitos...

:: Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado. Por favor, instale o Python 3.6 ou superior.
    pause
    exit /b 1
)
echo * Python encontrado

:: Verificar se o pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pip não encontrado. Por favor, reinstale o Python com pip.
    pause
    exit /b 1
)
echo * pip encontrado

echo Instalando dependências...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependências.
    pause
    exit /b 1
)
echo * Dependências instaladas com sucesso.

:: Criar diretórios necessários
if not exist logs mkdir logs
if not exist resources\icons mkdir resources\icons

echo Criando atalho para execução...
:: Criar script de execução
echo @echo off > executar_exportador.bat
echo python exportador.py >> executar_exportador.bat

echo Instalação concluída com sucesso!
echo Para iniciar o aplicativo, execute: executar_exportador.bat
pause