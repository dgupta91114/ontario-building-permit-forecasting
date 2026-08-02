# Generated Results Summary

> This file is generated from the analysis outputs. Confirm all interpretations against the tables and figures before copying text into the final paper.

## Dataset

- Analytic observations: **440 CMA-months**
- Target period: **2019-02-01T00:00:00 to 2026-05-01T00:00:00**
- Selected CMAs: **Hamilton, Kitchener-Cambridge-Waterloo, London, Toronto, Windsor**

## Sample-size calculations

| research_question | method | key_parameters | minimum_n |
|---|---|---|---|
| RQ1 | Correlation / Fisher z | alpha=.05; power=.80; r=.30; two-sided | 85.000 |
| RQ2 | Multiple regression F test | alpha=.05; power=.80; f-squared=.15; tested predictors=10 | 118.000 |
| RQ3 | Paired forecast-error t test | alpha=.05; power=.80; paired d=.35; two-sided | 67.000 |
| RQ4 | One-way ANOVA | alpha=.05; power=.80; Cohen f=.25; groups=5 | 196.000 |

## RQ2 — Incremental predictive value of macroeconomic variables

| n | mae_a | mae_b | improvement_pct_a_vs_b | paired_t_statistic | paired_t_p_value | wilcoxon_statistic | wilcoxon_p_value | dm_style_statistic | dm_style_p_value | practical_threshold_pct | meets_practical_threshold |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 60.000 | 20272.914 | 20272.914 | 0.000 |  |  | 0.000 |  | 0.000 | 1.000 | 5.000 | False |

## RQ3 — Holdout model comparison

| model | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|
| xgboost | 60.000 | 13975.867 | 17836.165 | 0.651 | 5.457 | 5.447 |
| random_forest | 60.000 | 14468.678 | 18659.799 | 0.671 | 5.649 | 5.639 |
| seasonal_naive | 60.000 | 17944.437 | 22183.453 | 0.848 | 7.211 | 6.994 |
| elastic_net_history | 60.000 | 20272.914 | 25113.949 | 0.940 | 7.943 | 7.901 |
| elastic_net_macro | 60.000 | 20272.914 | 25113.949 | 0.940 | 7.943 | 7.901 |

## Prespecified model-selection outcome

- Selected model: **xgboost**
- Rule outcome: candidate accepted
- Holdout interval coverage: 0.867

## RQ4 — Regional reliability

| model | cma | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|---|
| elastic_net_history | Hamilton | 12.000 | 18690.544 | 21566.823 | 0.967 | 8.096 | 7.866 |
| elastic_net_history | Kitchener-Cambridge-Waterloo | 12.000 | 19180.943 | 24048.014 | 0.957 | 7.622 | 7.450 |
| elastic_net_history | London | 12.000 | 23526.664 | 26159.380 | 1.017 | 8.776 | 8.552 |
| elastic_net_history | Toronto | 12.000 | 13183.769 | 16683.252 | 0.645 | 6.356 | 6.432 |
| elastic_net_history | Windsor | 12.000 | 26782.652 | 33874.377 | 1.112 | 8.868 | 8.703 |
| elastic_net_macro | Hamilton | 12.000 | 18690.544 | 21566.823 | 0.967 | 8.096 | 7.866 |
| elastic_net_macro | Kitchener-Cambridge-Waterloo | 12.000 | 19180.943 | 24048.014 | 0.957 | 7.622 | 7.450 |
| elastic_net_macro | London | 12.000 | 23526.664 | 26159.380 | 1.017 | 8.776 | 8.552 |
| elastic_net_macro | Toronto | 12.000 | 13183.769 | 16683.252 | 0.645 | 6.356 | 6.432 |
| elastic_net_macro | Windsor | 12.000 | 26782.652 | 33874.377 | 1.112 | 8.868 | 8.703 |
| random_forest | Hamilton | 12.000 | 12288.274 | 15631.234 | 0.636 | 5.333 | 5.172 |
| random_forest | Kitchener-Cambridge-Waterloo | 12.000 | 13841.291 | 17305.853 | 0.690 | 5.444 | 5.376 |
| random_forest | London | 12.000 | 16218.149 | 19292.288 | 0.701 | 5.977 | 5.895 |
| random_forest | Toronto | 12.000 | 10918.737 | 13961.952 | 0.534 | 5.274 | 5.327 |
| random_forest | Windsor | 12.000 | 19076.937 | 25099.483 | 0.792 | 6.216 | 6.199 |
| seasonal_naive | Hamilton | 12.000 | 20061.161 | 24017.007 | 1.038 | 9.018 | 8.443 |
| seasonal_naive | Kitchener-Cambridge-Waterloo | 12.000 | 21940.343 | 24384.799 | 1.094 | 8.846 | 8.522 |
| seasonal_naive | London | 12.000 | 20701.835 | 26069.648 | 0.895 | 7.615 | 7.525 |
| seasonal_naive | Toronto | 12.000 | 12070.778 | 16745.591 | 0.590 | 5.632 | 5.889 |
| seasonal_naive | Windsor | 12.000 | 14948.069 | 18139.780 | 0.621 | 4.947 | 4.857 |
| xgboost | Hamilton | 12.000 | 13847.075 | 15694.681 | 0.716 | 5.981 | 5.828 |
| xgboost | Kitchener-Cambridge-Waterloo | 12.000 | 13510.479 | 17494.649 | 0.674 | 5.312 | 5.248 |
| xgboost | London | 12.000 | 16868.540 | 19033.858 | 0.729 | 6.230 | 6.132 |
| xgboost | Toronto | 12.000 | 9375.334 | 10916.791 | 0.459 | 4.492 | 4.574 |
| xgboost | Windsor | 12.000 | 16277.908 | 23596.486 | 0.676 | 5.267 | 5.290 |

## Interpretation checklist

- Report out-of-sample results, not training fit, as the primary evidence.
- Describe associations and predictive value; do not claim causal effects.
- State that building permits measure construction intentions rather than completed construction.
- Discuss unusually large projects as potential genuine events, not automatic data errors.
- Report negative or mixed results when the prespecified rule retains the benchmark.