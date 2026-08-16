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
| 60.000 | 143145.480 | 137874.038 | -3.823 | -2.114 | 0.039 | 619.000 | 0.029 | -2.331 | 0.020 | 5.000 | False |

## RQ3 — Holdout model comparison

| model | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|
| xgboost | 60.000 | 56677.567 | 85342.139 | 0.449 | 29.670 | 18.847 |
| random_forest | 60.000 | 59360.981 | 93587.665 | 0.466 | 30.432 | 19.739 |
| elastic_net_history | 60.000 | 137874.038 | 244786.796 | 0.754 | 46.516 | 45.848 |
| seasonal_naive | 60.000 | 112354.467 | 198387.967 | 0.760 | 43.347 | 37.362 |
| elastic_net_macro | 60.000 | 143145.480 | 246563.267 | 0.882 | 50.723 | 47.601 |

## Prespecified model-selection outcome

- Selected model: **xgboost**
- Rule outcome: candidate accepted
- Holdout interval coverage: 0.950

## RQ4 — Regional reliability

| model | cma | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|---|
| elastic_net_history | Hamilton | 12.000 | 41863.204 | 51392.790 | 0.449 | 41.994 | 43.712 |
| elastic_net_history | Kitchener-Cambridge-Waterloo | 12.000 | 46163.418 | 53845.624 | 0.648 | 38.027 | 36.990 |
| elastic_net_history | London | 12.000 | 48281.192 | 57289.414 | 0.584 | 35.651 | 34.274 |
| elastic_net_history | Toronto | 12.000 | 516404.835 | 537947.678 | 1.028 | 61.193 | 47.209 |
| elastic_net_history | Windsor | 12.000 | 36657.540 | 37316.562 | 1.064 | 55.714 | 75.910 |
| elastic_net_macro | Hamilton | 12.000 | 42704.354 | 52958.708 | 0.458 | 42.655 | 44.590 |
| elastic_net_macro | Kitchener-Cambridge-Waterloo | 12.000 | 46060.747 | 53317.005 | 0.646 | 37.930 | 36.908 |
| elastic_net_macro | London | 12.000 | 47909.141 | 56353.970 | 0.579 | 35.313 | 34.010 |
| elastic_net_macro | Toronto | 12.000 | 520895.222 | 540103.202 | 1.037 | 62.002 | 47.619 |
| elastic_net_macro | Windsor | 12.000 | 58157.938 | 58588.891 | 1.688 | 75.717 | 120.432 |
| random_forest | Hamilton | 12.000 | 42833.712 | 52001.947 | 0.459 | 42.844 | 44.725 |
| random_forest | Kitchener-Cambridge-Waterloo | 12.000 | 51239.115 | 58476.559 | 0.719 | 42.016 | 41.057 |
| random_forest | London | 12.000 | 44576.979 | 52605.432 | 0.539 | 32.806 | 31.644 |
| random_forest | Toronto | 12.000 | 147160.945 | 186384.169 | 0.293 | 13.199 | 13.453 |
| random_forest | Windsor | 12.000 | 10994.152 | 12773.214 | 0.319 | 21.296 | 22.766 |
| seasonal_naive | Hamilton | 12.000 | 63569.083 | 111897.855 | 0.681 | 47.674 | 66.376 |
| seasonal_naive | Kitchener-Cambridge-Waterloo | 12.000 | 69265.667 | 82566.161 | 0.972 | 59.536 | 55.501 |
| seasonal_naive | London | 12.000 | 63717.500 | 86643.594 | 0.770 | 45.015 | 45.232 |
| seasonal_naive | Toronto | 12.000 | 341277.167 | 410932.017 | 0.679 | 27.418 | 31.199 |
| seasonal_naive | Windsor | 12.000 | 23942.917 | 32838.870 | 0.695 | 37.090 | 49.580 |
| xgboost | Hamilton | 12.000 | 40091.553 | 46550.257 | 0.430 | 41.027 | 41.862 |
| xgboost | Kitchener-Cambridge-Waterloo | 12.000 | 52075.538 | 62132.476 | 0.731 | 43.016 | 41.727 |
| xgboost | London | 12.000 | 46893.413 | 55382.193 | 0.567 | 34.775 | 33.289 |
| xgboost | Toronto | 12.000 | 135783.422 | 164978.614 | 0.270 | 12.433 | 12.413 |
| xgboost | Windsor | 12.000 | 8543.910 | 10193.218 | 0.248 | 17.101 | 17.693 |

## Interpretation checklist

- Report out-of-sample results, not training fit, as the primary evidence.
- Describe associations and predictive value; do not claim causal effects.
- State that building permits measure construction intentions rather than completed construction.
- Discuss unusually large projects as potential genuine events, not automatic data errors.
- Report negative or mixed results when the prespecified rule retains the benchmark.