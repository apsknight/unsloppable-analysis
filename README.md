# Unsloppable Analysis

AI & Robotics Disruption Risk Assessment for NASDAQ 100 Companies using the Unsloppable Framework.

## Quick Start

### Prerequisites
- Python 3.12+
- SEC filing data in `/Users/apsknight/Documents/primary-vault/Investing/unsloppable_results/`

### Build the Site

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/unsloppable-analysis.git
cd unsloppable-analysis

# Build the site
python build.py
```

The static site will be generated in the `docs/` directory.

### Preview Locally

```bash
cd docs
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Project Structure

```
├── build.py              # Static site generator
├── templates/            # HTML templates
│   ├── index.html
│   └── company.html
├── docs/                 # Generated static site (for GitHub Pages)
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions workflow
└── README.md
```

## Deployment

This project is configured to deploy to GitHub Pages automatically:

1. Go to your repository settings
2. Enable GitHub Pages
3. Set source to "GitHub Actions"
4. Push to main branch

The workflow will automatically build and deploy the site.

## Data Source

The analysis is generated from SEC 10-K and 8-K filings using Claude (Opus model) with the Unsloppable Framework prompt.
