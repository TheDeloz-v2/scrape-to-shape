@echo off
REM Script para configurar el entorno del proyecto scrape-to-shape con Conda en Windows

echo === Setting up scrape-to-shape environment with Conda ===

REM Verificar si conda está instalado
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Conda is not installed or not in PATH
    echo Please install Miniconda or Anaconda first:
    echo   https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Conda found.

REM Eliminar entorno existente si existe
conda env list | find "scrape-to-shape" >nul
if %errorlevel% equ 0 (
    echo Removing existing scrape-to-shape environment...
    call conda env remove -n scrape-to-shape -y
)

REM Crear entorno desde environment.yml
echo Creating conda environment from environment.yml...
call conda env create -f environment.yml

echo.
echo Activating environment...
call conda activate scrape-to-shape

REM Instalar playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Descargar modelo de spaCy en español
echo Downloading spaCy Spanish model...
python -m spacy download es_core_news_sm

echo.
echo === Setup completed successfully! ===
echo.
echo To activate the environment, run:
echo   conda activate scrape-to-shape
echo.
echo To deactivate the environment, run:
echo   conda deactivate
echo.
echo To run the scraper:
echo   conda activate scrape-to-shape
echo   cd src\scraper ^&^& python main.py
echo.
echo To run Jupyter notebook:
echo   conda activate scrape-to-shape
echo   jupyter notebook

pause

