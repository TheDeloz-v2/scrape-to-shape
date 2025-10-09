#!/bin/bash

# Script para configurar el entorno del proyecto scrape-to-shape con Conda

echo "=== Setting up scrape-to-shape environment with Conda ==="

# Verificar si conda está instalado
if ! command -v conda &> /dev/null
then
    echo "Error: Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Conda found: $(which conda)"

# Eliminar entorno existente si existe
if conda env list | grep -q "scrape-to-shape"; then
    echo "Removing existing scrape-to-shape environment..."
    conda env remove -n scrape-to-shape -y
fi

# Crear entorno desde environment.yml
echo "Creating conda environment from environment.yml..."
conda env create -f environment.yml

echo ""
echo "Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate scrape-to-shape

# Instalar playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Descargar modelo de spaCy en español
echo "Downloading spaCy Spanish model..."
python -m spacy download es_core_news_sm

echo ""
echo "=== Setup completed successfully! ==="
echo ""
echo "To activate the environment, run:"
echo "  conda activate scrape-to-shape"
echo ""
echo "To deactivate the environment, run:"
echo "  conda deactivate"
echo ""
echo "To run the scraper:"
echo "  conda activate scrape-to-shape"
echo "  cd src/scraper && python main.py"
echo ""
echo "To run Jupyter notebook:"
echo "  conda activate scrape-to-shape"
echo "  jupyter notebook"

