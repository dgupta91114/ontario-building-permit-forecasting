# Final-Draft Project Status and Repository Review

**Status reviewed:** August 16, 2026

**Working repository:** `ontario-building-permit-forecasting/`

**Protected packaged snapshot:** `Version-2 With additional work/` (outside this repository)

This internal record supersedes the earlier synthetic-only status. No prior submission DOCX/PDF or Version 2 artifact was changed. Their SHA-256 hashes are recorded in `reports/submission_artifact_baseline.json` and were reverified after the final draft was generated.

## Official data completion

- Downloaded Statistics Canada Tables 34-10-0292-01 and 14-10-0287-01 and Bank of Canada V39079.
- Frozen official URLs, download timestamps, and archive hashes in `data/raw/download_manifest.json`.
- Reworked full-table extraction and audit to stream multi-gigabyte files with bounded memory.
- Verified the official combined permit dimension `Seasonal adjustment, value type`, the `Type of building` field, and the unemployment `Statistics = Estimate` filter.
- Selected January 2018 through May 2026, the newest complete permit window available for the draft.
- Retained 505 source CMA-months: 101 for each of Toronto, Hamilton, Kitchener-Cambridge-Waterloo, London, and Windsor.
- Produced 440 complete modeling rows: 88 per CMA, with targets from February 2019 through May 2026.
- Verified no duplicate CMA-target rows, no missing targets, and no synthetic observations in the official dataset.
- Retained and disclosed one official Statistics Canada `E` status observation for London in April 2025.

## Completed empirical analysis

- RQ1 descriptive statistics, persistence, seasonal profiles, trend figures, and pooled HAC regression
- RQ2 history-only versus macro-augmented elastic-net comparison
- RQ3 seasonal naive, elastic net, random forest, and XGBoost temporal-holdout comparison
- RQ4 regional metrics, error ANOVA, permutation importance, SHAP, and conformal intervals
- Actual-versus-predicted, absolute-error, and interval-coverage diagnostics
- Separate constant-dollar sensitivity run
- Official source, configuration, processed-data, and results provenance manifest

## Primary official findings

- XGBoost met the prespecified governance rule with holdout MAE **53,677.99**, MASE **0.571**, and WAPE **16.80%**.
- Seasonal naive produced MAE **116,199.63** and MASE **0.990**.
- XGBoost reduced MAE by **53.8%** relative to seasonal naive; the paired t-test p-value was **.0024**.
- XGBoost achieved MASE below one in all five CMAs and was not materially worse than seasonal naive in any CMA.
- Macro augmentation improved elastic-net MAE by only **0.40%**, did not reach the 5% practical threshold, and was not statistically significant.
- Recent permit value, the three-month rolling mean, and permit lags dominated permutation importance; the macroeconomic features contributed little.
- Overall 90% conformal interval coverage was **100%**, but the intervals were wide and should be described as conservative.
- Constant-dollar analysis also selected XGBoost, with MASE **0.449**, MAE **56,677.57**, and **95%** interval coverage.

## Draft report and verification

- Generated `reports/final_draft/QM640_Capstone_Final_Report_Draft_Debodip_Gupta.docx` from a protected working copy of the supplied interim template.
- The draft contains 3,710 narrative words, 11 official tables, six official figures, APA-oriented formatting, references, limitations, recommendations, and appendices.
- The mentor name was confirmed from the prior report and inserted as Dr. Sanhita Karmakar; no placeholders remain.
- Enforced Times New Roman across document styles, paragraphs, tables, headings, headers, and hyperlink runs.
- Added 18 genuine external Word hyperlinks: the GitHub repository and all 17 reference URLs/DOIs.
- Inspected the DOCX package for hidden text, comments, custom XML, and AI-assistant identifiers; none were present.
- Local structural/originality validation found no template instructions, long quotations, duplicated long sentences, or missing required sections.
- The expanded unit suite passes 11 tests.
- The end-to-end pipeline succeeds from frozen raw inputs with `python run_pipeline.py --skip-download`.
- `scripts/08_reproducibility_check.py` passes and confirms zero demo rows.
- Package versions are recorded in `environment-lock.txt`.

## GitHub publication status

- Repository: <https://github.com/dgupta91114/ontario-building-permit-forecasting>
- Branch: `main`
- Official-analysis and draft-report upload commit: `853b5a7` (`Complete official capstone analysis and draft report`)
- Push completed successfully on August 16, 2026.
- The upload includes the official processed dataset, current- and constant-dollar results, figures, source-label audits, reproducibility evidence, final DOCX draft, report generator, and validation scripts.
- The upload excludes raw multi-gigabyte government downloads, virtual environments, caches, model binaries, transient Word lock files, and local assistant/prompt/chat artifacts.
- Prior synopsis and interim submission DOCX/PDF artifacts remained unchanged, as verified against their recorded SHA-256 hashes.

## Evidence boundary

The current `data/processed/modeling_dataset.csv`, main `outputs/tables/`, main `outputs/figures/`, and final-report draft are official empirical artifacts. Synthetic software-validation artifacts remain isolated under `data/demo/` and `outputs/demo_dry_run/`; they must not be substituted into the report.

## Remaining manual submission actions

1. Confirm the remaining title-page metadata.
2. Open the DOCX in Microsoft Word and inspect pagination, table wrapping, captions, and image clarity.
3. Upload the draft to a student-selected plagiarism checker and confirm similarity does not exceed 7%.
4. Address any mentor or originality feedback without changing the frozen evidence unless an analytic correction is required.
5. Convert the reviewed DOCX to PDF, inspect the PDF page by page, and submit only the PDF before the deadline.

## Interpretation safeguards

- Building permits measure construction intentions, not completed construction or housing supply.
- Large projects may create genuine spikes and were not automatically removed.
- The study is predictive rather than causal.
- Point forecasts must be presented with uncertainty and regional performance.
- Negative RQ2 evidence is reported rather than reframed as support for macroeconomic predictors.
