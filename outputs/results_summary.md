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
| 60.000 | 75378.504 | 75678.450 | 0.396 | 1.089 | 0.280 | 767.000 | 0.276 | 1.136 | 0.256 | 5.000 | False |

## RQ3 — Holdout model comparison

| model | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|
| xgboost | 60.000 | 53677.992 | 73485.259 | 0.571 | 28.379 | 16.796 |
| random_forest | 60.000 | 59360.277 | 93306.657 | 0.572 | 28.078 | 18.574 |
| elastic_net_macro | 60.000 | 75378.504 | 118806.532 | 0.725 | 34.605 | 23.586 |
| elastic_net_history | 60.000 | 75678.450 | 119173.293 | 0.725 | 34.618 | 23.679 |
| seasonal_naive | 60.000 | 116199.633 | 204328.684 | 0.990 | 42.977 | 36.358 |

## Prespecified model-selection outcome

- Selected model: **xgboost**
- Rule outcome: candidate accepted
- Holdout interval coverage: 1.000

## RQ4 — Regional reliability

| model | cma | n | mae | rmse | mase | smape_pct | wape_pct |
|---|---|---|---|---|---|---|---|
| elastic_net_history | Hamilton | 12.000 | 39300.476 | 50701.818 | 0.506 | 37.790 | 38.550 |
| elastic_net_history | Kitchener-Cambridge-Waterloo | 12.000 | 49441.954 | 63579.947 | 0.880 | 38.172 | 37.102 |
| elastic_net_history | London | 12.000 | 56457.255 | 68815.066 | 0.894 | 39.676 | 37.579 |
| elastic_net_history | Toronto | 12.000 | 209219.324 | 242965.765 | 0.536 | 18.834 | 18.019 |
| elastic_net_history | Windsor | 12.000 | 23973.243 | 25107.935 | 0.809 | 38.616 | 46.632 |
| elastic_net_macro | Hamilton | 12.000 | 39319.747 | 50696.870 | 0.506 | 37.803 | 38.569 |
| elastic_net_macro | Kitchener-Cambridge-Waterloo | 12.000 | 49432.814 | 63525.250 | 0.880 | 38.163 | 37.095 |
| elastic_net_macro | London | 12.000 | 56361.515 | 68689.187 | 0.893 | 39.593 | 37.516 |
| elastic_net_macro | Toronto | 12.000 | 207650.390 | 242101.578 | 0.532 | 18.654 | 17.884 |
| elastic_net_macro | Windsor | 12.000 | 24128.054 | 25257.719 | 0.814 | 38.812 | 46.933 |
| random_forest | Hamilton | 12.000 | 38091.608 | 45522.509 | 0.490 | 37.241 | 37.364 |
| random_forest | Kitchener-Cambridge-Waterloo | 12.000 | 49801.106 | 61540.541 | 0.886 | 38.483 | 37.372 |
| random_forest | London | 12.000 | 50762.047 | 61924.503 | 0.804 | 35.103 | 33.788 |
| random_forest | Toronto | 12.000 | 149399.833 | 183692.724 | 0.382 | 12.690 | 12.867 |
| random_forest | Windsor | 12.000 | 8746.793 | 9667.614 | 0.295 | 16.871 | 17.014 |
| seasonal_naive | Hamilton | 12.000 | 67226.500 | 117420.193 | 0.865 | 47.856 | 65.942 |
| seasonal_naive | Kitchener-Cambridge-Waterloo | 12.000 | 73332.417 | 88366.049 | 1.305 | 59.490 | 55.030 |
| seasonal_naive | London | 12.000 | 67404.583 | 92355.582 | 1.068 | 44.888 | 44.866 |
| seasonal_naive | Toronto | 12.000 | 348705.167 | 421316.540 | 0.893 | 26.611 | 30.032 |
| seasonal_naive | Windsor | 12.000 | 24329.500 | 33433.744 | 0.821 | 36.039 | 47.325 |
| xgboost | Hamilton | 12.000 | 39300.040 | 44958.486 | 0.506 | 38.538 | 38.549 |
| xgboost | Kitchener-Cambridge-Waterloo | 12.000 | 51913.702 | 63445.344 | 0.924 | 40.085 | 38.957 |
| xgboost | London | 12.000 | 53637.566 | 63135.863 | 0.850 | 37.443 | 35.702 |
| xgboost | Toronto | 12.000 | 115212.708 | 129884.555 | 0.295 | 10.032 | 9.923 |
| xgboost | Windsor | 12.000 | 8325.943 | 9884.566 | 0.281 | 15.798 | 16.195 |

## Interpretation checklist

- Report out-of-sample results, not training fit, as the primary evidence.
- Describe associations and predictive value; do not claim causal effects.
- State that building permits measure construction intentions rather than completed construction.
- Discuss unusually large projects as potential genuine events, not automatic data errors.
- Report negative or mixed results when the prespecified rule retains the benchmark.