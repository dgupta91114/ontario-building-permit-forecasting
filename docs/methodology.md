# Methodology and Analytic Plan

## Unit of analysis and target

The unit of analysis is a **CMA-month**. A row indexed by forecast origin month `t` predicts residential building-permit value at `t + 1`. The primary period is January 2018 through May 2026, subject to final source availability. The processed dataset is expected to contain approximately 440–445 complete CMA-month rows after lag construction.

## Source filters

The primary building-permit series uses:

- five selected Ontario CMAs;
- seasonally adjusted values;
- current dollars;
- total residential structures; and
- total type of work.

The code identifies official dimension labels from candidates in `config/config.yaml`, records the exact selected labels in `data/interim/cleaning_audit.json`, and fails rather than silently choosing an ambiguous label.

Ontario unemployment uses the seasonally adjusted unemployment rate for total gender and persons aged 15 years and over. The overnight rate is series V39079 and is summarized using the final observation in each month.

## Feature engineering and leakage control

Primary predictors are permit value at origin, permit lags at one, three, six, and 12 months, three-month rolling mean and standard deviation, cyclical target-month encodings, linear time index, pandemic-period indicator, CMA, lagged overnight rate, and lagged unemployment rate.

Macroeconomic variables are lagged by one month in the primary models. All lag and rolling features are computed within CMA. The most recent 12 target months form a final holdout. Every CMA row from the same target month stays in the same fold.

## Models

- Seasonal naive: same target calendar month one year earlier
- Elastic net: interpretable regularized linear model
- Random forest: nonlinear bagged-tree model
- XGBoost: nonlinear boosted-tree model

Numeric variables are median-imputed and standardized. CMA is one-hot encoded. Fitted models use `log1p` target transformation and return predictions to the original dollar scale.

## Validation

Hyperparameters are selected using expanding-window monthly folds inside the training period. The final holdout is never used for tuning. The model-selection rule favors the simplest model satisfying all governance conditions, not automatically the most complex algorithm.

## Evaluation formulas

For observations \(y_i\) and forecasts \(\hat{y}_i\):

- **MAE:** \(\frac{1}{n}\sum |y_i-\hat{y}_i|\)
- **RMSE:** \(\sqrt{\frac{1}{n}\sum (y_i-\hat{y}_i)^2}\)
- **sMAPE:** \(\frac{100}{n}\sum \frac{2|y_i-\hat{y}_i|}{|y_i|+|\hat{y}_i|}\)
- **WAPE:** \(100\frac{\sum |y_i-\hat{y}_i|}{\sum |y_i|}\)
- **MASE:** mean absolute error divided by the within-CMA mean absolute seasonal-naive change from the training period.

A split-conformal procedure produces nominal 90% prediction intervals. Interval coverage and mean width are reported.

## Statistical tests

- RQ1 uses descriptive analysis and a pooled ordinary least squares model with Newey-West/HAC standard errors.
- RQ2 uses paired t, Wilcoxon signed-rank, and a Diebold-Mariano-style loss-differential statistic, plus the prespecified 5% practical threshold.
- RQ3 reports paired error comparisons against seasonal naive.
- RQ4 uses one-way ANOVA on absolute forecast errors by CMA, accompanied by regional effect patterns and caution regarding temporal dependence.

## Robustness analyses for the final capstone

The final project should repeat the preferred comparison with and without the pandemic period, with robust treatment of extreme months, under alternate training-window lengths, and—if the source table supplies a compatible measure—using constant-dollar permit values.
