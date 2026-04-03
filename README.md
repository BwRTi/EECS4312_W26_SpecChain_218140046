# EECS4312_W26_SpecChain

## Application

This project studies **Wysa: Mental Health Support** on the Google Play Store.

- App name: `Wysa: Mental Health Support`
- App ID: `bot.touchkin`
- Store URL: `https://play.google.com/store/apps/details?id=bot.touchkin&hl=en_CA&pli=1`

## Dataset

- `data/reviews_raw.jsonl` contains the collected raw Google Play reviews.
- `data/reviews_clean.jsonl` contains the cleaned dataset used by the manual, automated, and hybrid pipelines.
- Raw dataset size: `1500` reviews
- Final cleaned dataset size: `1247` reviews

## Data Collection Method

The raw reviews were collected from Google Play using the Python package `google-play-scraper` in a Python 3.10 virtual environment.

Collection settings:

- Language: `en`
- Country: `ca`
- Sort order: `newest`
- Requested review count: `1500`

## Cleaning Method

The cleaning script removes duplicate reviews, empty entries, and very short reviews. It also normalizes the text by:

- removing punctuation
- removing special characters and emojis
- converting numbers to English text
- normalizing whitespace
- converting all text to lowercase
- removing stop words
- lemmatizing the remaining tokens

## Repository Structure

- `data/` stores raw reviews, cleaned reviews, metadata, and review-group files
- `personas/` stores manual, automated, and hybrid personas
- `spec/` stores manual, automated, and hybrid specifications
- `tests/` stores validation tests for each pipeline
- `metrics/` stores per-pipeline metrics and the comparison summary
- `prompts/` stores the prompt used in the automated pipeline
- `src/` stores all executable scripts
- `reflection/` stores the final reflection

## Required Environment

- Python `3.10`
- Operating system used for the commands in this README: `Windows`
- Shell used for the commands in this README: `PowerShell`

Required Python packages:

- listed in `requirements.txt`

The automated pipeline also uses the Groq API.

To run the automated Groq-based scripts, provide a Groq API key through one of these options:

1. Set `GROQ_API_KEY` as an environment variable
2. Edit the `GROQ_API_KEY` constant in `src/05_personas_auto.py`

The automated pipeline is configured to use:

- Provider: `Groq`
- Model: `meta-llama/llama-4-scout-17b-16e-instruct`

## Setup Commands

Create the virtual environment with Python 3.10:

```powershell
python -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The current direct project dependencies are:

- `google-play-scraper`
- `nltk`

Optional: set the Groq API key for automated generation:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Optional: instead of using an environment variable, you may edit the `GROQ_API_KEY` constant directly in:

```text
src/05_personas_auto.py
```

Note: the Groq integration in this project uses Python standard-library HTTP utilities, so no additional Groq Python package is required.

## Exact Commands to Run

Validate the repository structure:

```powershell
.\.venv\Scripts\python.exe .\src\00_validate_repo.py
```

Collect or refresh the raw review dataset:

```powershell
.\.venv\Scripts\python.exe .\src\01_collect_or_import.py
```

Clean the raw review dataset:

```powershell
.\.venv\Scripts\python.exe .\src\02_clean.py
```

Run the automated workflow from start to finish:

```powershell
.\.venv\Scripts\python.exe .\src\run_all.py
```

Important behavior:

- `src/run_all.py` **does not re-collect reviews by default** if `data/reviews_raw.jsonl` already exists.
- To force a fresh collection run:

```powershell
.\.venv\Scripts\python.exe .\src\run_all.py --collect
```

## Automated Pipeline Outputs

Running `src/run_all.py` produces or refreshes these automated artifacts:

- `data/review_groups_auto.json`
- `personas/personas_auto.json`
- `prompts/prompt_auto.json`
- `spec/spec_auto.md`
- `tests/tests_auto.json`
- `metrics/metrics_auto.json`
- `metrics/metrics_summary.json`

## Metrics Summary

The comparison across pipelines is stored in:

- `metrics/metrics_manual.json`
- `metrics/metrics_auto.json`
- `metrics/metrics_hybrid.json`
- `metrics/metrics_summary.json`

Open `metrics/metrics_summary.json` to compare persona count, requirements count, tests count, traceability, review coverage, testability, and ambiguity across the three pipelines.
