# Quick Start Guide

## 🚀 Quick Installation with Conda

### Option 1: Automated Script (Recommended)

```bash
# On Linux/Mac/WSL
./setup_env.sh

# On Windows
setup_env.bat
```

### Option 2: Manual Commands

```bash
# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate scrape-to-shape

# Install Playwright browsers
playwright install chromium

# Download spaCy Spanish model
python -m spacy download es_core_news_sm
```

## 📝 Basic Usage

### 1. Activate the environment

```bash
conda activate scrape-to-shape
```

### 2. Run the scraper

```bash
cd src/scraper
python main.py
```

The data will be saved to `data/raw/google_maps_all_reviews.csv`

### 3. Exploratory analysis

```bash
# From the project root
jupyter notebook
```

Then open `notebooks/EDA.ipynb`

## 🔧 Useful Commands

### List conda environments
```bash
conda env list
```

### Update dependencies
```bash
conda env update -f environment.yml --prune
```

### Remove the environment
```bash
conda env remove -n scrape-to-shape
```

### Export current environment
```bash
conda env export > environment_backup.yml
```

## 🐛 Troubleshooting

### Issue: "conda: command not found"
**Solution:** Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

### Issue: "Environment not found"
**Solution:** Make sure to create the environment first with `conda env create -f environment.yml`

### Issue: "Playwright browsers not found"
**Solution:** Run `playwright install chromium` after activating the environment

### Issue: "spaCy model not found"
**Solution:** Run `python -m spacy download es_core_news_sm`

## 📚 Project Structure

```
scrape-to-shape/
├── environment.yml         # Conda environment definition
├── requirements.txt        # Pip dependencies (alternative)
├── setup_env.sh           # Installation script (Linux/Mac)
├── setup_env.bat          # Installation script (Windows)
├── data/
│   ├── raw/               # Raw scraped data
│   └── processed/         # Cleaned and processed data
├── src/
│   └── scraper/
│       ├── main.py        # Scraper entry point
│       └── scrapper.py    # Scraping functions
└── notebooks/
    └── EDA.ipynb          # Exploratory Data Analysis
```

## 💡 Tips

1. **Always activate the environment** before working:
   ```bash
   conda activate scrape-to-shape
   ```

2. **To deactivate** the environment when you're done:
   ```bash
   conda deactivate
   ```

3. **To see installed packages**:
   ```bash
   conda list
   ```

4. **To update a specific package**:
   ```bash
   conda update package_name
   # or with pip:
   pip install --upgrade package_name
   ```

