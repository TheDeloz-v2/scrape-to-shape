# scrape-to-shape

**Text Mining and Sentiment Analysis of Social Club Reviews**

This project focuses on building a streamlined pipeline for collecting, cleaning, and structuring user-generated reviews from a publicly accessible platform. It implements web scraping, natural language processing, and exploratory data analysis to extract insights from social club reviews.

> 📖 **Quick Start?** Check out [QUICKSTART.md](QUICKSTART.md) for a fast setup guide!

## Features

- 🔍 **Web Scraping**: Automated collection of reviews from Google Maps using Playwright
- 🧹 **Data Cleaning**: Text normalization, lemmatization, and preprocessing
- 📊 **EDA**: Exploratory data analysis with visualizations
- 🤖 **NLP**: Spanish language processing using spaCy

## Setup

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download)

### Automated Setup (Recommended)

**Linux/Mac/WSL:**
```bash
./setup_env.sh
```

**Windows:**
```bash
setup_env.bat
```

### Manual Setup

1. Create conda environment from `environment.yml`:
```bash
conda env create -f environment.yml
```

2. Activate the environment:
```bash
conda activate scrape-to-shape
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Download spaCy Spanish model:
```bash
python -m spacy download es_core_news_sm
```

### Alternative: Using pip and venv

If you prefer not to use conda, you can still use the traditional approach:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python -m spacy download es_core_news_sm
```

## Usage

### Run the Scraper

```bash
cd src/scraper
python main.py
```

### Run Jupyter Notebook

```bash
jupyter notebook
```

Then open `notebooks/EDA.ipynb` to explore the data analysis.

## Project Structure

```
scrape-to-shape/
├── environment.yml        # Conda environment definition
├── requirements.txt       # Pip dependencies (alternative)
├── setup_env.sh          # Installation script (Linux/Mac)
├── setup_env.bat         # Installation script (Windows)
├── data/
│   ├── raw/              # Raw scraped data
│   └── processed/        # Cleaned and processed data
├── src/
│   └── scraper/          # Scraping modules
│       ├── main.py       # Main scraper entry point
│       └── scrapper.py   # Scraping functions
└── notebooks/
    └── EDA.ipynb         # Exploratory Data Analysis
```

## Dependencies

- Python 3.10+
- Playwright for web scraping
- Pandas, NumPy for data processing
- spaCy for NLP
- Matplotlib, Seaborn for visualization

## License

This project is for educational purposes only.
