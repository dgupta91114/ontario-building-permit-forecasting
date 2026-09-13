> **Final-report status (September 13, 2026):** The [40-page final report PDF](reports/final/QM640_Capstone_Final_Report_Debodip_Gupta.pdf) and [editable DOCX](reports/final/QM640_Capstone_Final_Report_Debodip_Gupta.docx) are complete for the Summer 2026 submission. See the [rubric map, validation, and submission checklist](reports/final/README.md). The assignment's external plagiarism check remains outstanding; no similarity percentage is claimed.
>
> **Official-analysis status:** The current processed dataset, tables, figures, and report use frozen official Statistics Canada and Bank of Canada sources through May 2026. Earlier synthetic software-validation outputs are isolated under `data/demo/` and `outputs/demo_dry_run/` and are not used in the empirical report.

# Forecasting Ontario Residential Building-Permit Values

This repository supports the QM640 Data Analytics Capstone synopsis:

> **Forecasting Ontario Residential Building-Permit Values Using Explainable Time-Series and Machine-Learning Models**

The project develops one-month-ahead forecasts for residential building-permit values in five Ontario census metropolitan areas (CMAs): Toronto, Hamilton, Kitchener-Cambridge-Waterloo, London, and Windsor. It uses only public, aggregated government data.

## Research questions

1. **RQ1 — Descriptive structure:** What trend, seasonality, persistence, volatility, and structural-change patterns characterize monthly residential building-permit values across the five CMAs?
2. **RQ2 — Incremental value:** Do the Bank of Canada target for the overnight rate and Ontario unemployment rate improve forecast accuracy beyond permit history, seasonality, and CMA effects?
3. **RQ3 — Model comparison:** Which candidate model produces the most accurate and stable one-month-ahead forecasts across time and regions?
4. **RQ4 — Explainability and reliability:** Which variables contribute most to the preferred model, and does forecast performance differ materially across CMAs?

## Official data sources

- Statistics Canada Table 34-10-0292-01: Building permits, by type of structure and type of work  
  <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3410029201>
- Statistics Canada Table 14-10-0287-01: Labour force characteristics, monthly, seasonally adjusted and trend-cycle  
  <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701>
- Bank of Canada Valet API series V39079: Target for the overnight rate  
  <https://www.bankofcanada.ca/valet/observations/V39079/json?start_date=2018-01-01>

The downloader calls the official Statistics Canada Web Data Service to retrieve full-table CSV ZIP files. The processed modeling dataset is small and may be committed to the repository after it is generated. Raw ZIP files are ignored by Git because they are reproducibly downloadable and can be large.

## Repository structure

```text
.
├── .github/workflows/tests.yml
├── config/config.yaml
├── data/
│   ├── demo/                 # synthetic test data only
│   ├── interim/              # cleaned source tables
│   ├── processed/            # final modeling dataset
│   └── raw/                  # downloaded official files (not committed)
├── docs/
│   ├── data_dictionary.csv
│   ├── methodology.md
│   ├── reproducibility_checklist.md
│   ├── research_questions.md
│   └── source_manifest.csv
├── notebooks/
├── outputs/
│   ├── figures/
│   ├── models/
│   └── tables/
├── scripts/
├── src/capstone/
├── tests/
├── Makefile
├── pyproject.toml
├── requirements.txt
└── run_pipeline.py
```

## Quick start

### 1. Create an environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows PowerShell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2. Inspect source labels before filtering

Statistics Canada occasionally revises labels. Run the audit first:

```bash
python scripts/00_inspect_sources.py
```

The script downloads the official tables, lists columns and candidate dimension values, and writes audit files to `outputs/tables/source_audit/`. If a label changes, edit only `config/config.yaml`; do not hard-code changes in analysis notebooks.

### 3. Run the complete pipeline

```bash
python run_pipeline.py
```

Equivalent staged commands are available through the Makefile:

```bash
make download
make data
make eda
make model
make explain
make report
make test
```

### 4. Review generated evidence

Key files are written to:

- `data/processed/modeling_dataset.csv`
- `outputs/tables/rq1_summary_by_cma.csv`
- `outputs/tables/rq2_incremental_value.csv`
- `outputs/tables/rq3_model_metrics.csv`
- `outputs/tables/rq4_regional_metrics.csv`
- `outputs/tables/sample_size_calculations.csv`
- `outputs/tables/model_selection.json`
- `outputs/figures/`
- `outputs/results_summary.md`

## Leakage controls

Each row represents a forecast origin month `t`; the target is permit value at `t + 1`. Only information available by the forecast origin is used. The code:

- constructs targets with a within-CMA lead;
- creates lag and rolling features within each CMA;
- uses lagged macroeconomic values in the primary models;
- keeps every CMA observation from the same month in the same train/test fold;
- reserves the most recent 12 target months as a final temporal holdout;
- tunes models only on earlier rolling-origin folds.

The seasonal-naive forecast for target month `t + 1` is the value from the same calendar month one year earlier. Because rows are indexed by origin month `t`, this is generated from the permit series at `t - 11`; the code computes this explicitly to avoid an off-by-one error.

## Models and decision rules

Candidate models are:

1. Seasonal-naive benchmark
2. Elastic-net regression
3. Random forest
4. Extreme gradient boosting (XGBoost)

The preferred model must satisfy the prespecified governance rule in the synopsis: it should achieve pooled MASE below 1.0, improve pooled MAE over seasonal naive, avoid material degradation in most CMAs, and pass reproducibility checks. If no candidate meets these conditions, seasonal naive remains the recommended model.

## Important cautions

- Building permits measure construction intentions, not completed construction or housing supply.
- Large projects can cause legitimate spikes; they should not automatically be deleted as errors.
- The study is predictive, not causal.
- The synthetic data under `data/demo/` are only for software testing and must not be used in the final analysis.
- Before final project submission, commit the processed dataset, data dictionary, source manifest, code, configuration, and generated results to <https://github.com/dgupta91114/ontario-building-permit-forecasting>.

## Reproducibility

Run this command from a clean environment:

```bash
python scripts/08_reproducibility_check.py
```

It validates required files, checks hashes, runs unit tests, and confirms that the processed dataset can be regenerated from the source manifest.

## License and citation

Code is released under the MIT License. Government data remain subject to the terms and attribution requirements of their source agencies. See `CITATION.cff` for a repository citation template.
