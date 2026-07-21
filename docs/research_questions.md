# Research Questions, Hypotheses, and Decision Rules

## RQ1 — Trend, seasonality, persistence, and volatility

**Question.** What trend, seasonal, persistence, and volatility patterns characterize monthly residential building-permit values across Toronto, Hamilton, Kitchener-Cambridge-Waterloo, London, and Windsor?

**Hypothesis.** Lagged permit values and annual seasonal terms have statistically significant relationships with next-month permit value.

**Evidence.** Descriptive statistics, coefficient of variation, lag-1 and lag-12 autocorrelation, seasonal profiles, and a pooled regression with heteroskedasticity- and autocorrelation-consistent standard errors.

## RQ2 — Incremental value of macroeconomic predictors

**Question.** Do the Bank of Canada target for the overnight rate and Ontario unemployment rate add statistically and practically significant predictive information beyond permit history, seasonality, and CMA effects?

**Hypothesis.** The macro-augmented model reduces rolling-origin or temporal-holdout mean absolute error by at least 5% relative to the otherwise identical history-only model.

**Decision rule.** Practical value requires at least a 5% MAE reduction and no severe regional instability. Statistical evidence is reported through paired error tests, but statistical significance alone is insufficient.

## RQ3 — Model accuracy and stability

**Question.** Which candidate model produces the most accurate and stable one-month-ahead forecasts across time and regions?

**Hypothesis.** At least one nonlinear tree-based model will achieve lower MASE than seasonal naive and elastic net.

**Primary metrics.** MAE, RMSE, MASE, sMAPE, and WAPE on the most recent 12-month holdout. Rolling-origin validation is used only for tuning.

## RQ4 — Explainability and regional reliability

**Question.** Which variables contribute most to the preferred model, and does forecast performance differ materially across the five CMAs?

**Hypothesis.** Permit-history and seasonal features will dominate global importance, and error distributions will differ by CMA.

**Evidence.** SHAP when technically supported, model-agnostic permutation importance as an auditable fallback, regional metric tables, error ANOVA, interval coverage, and regional reliability flags.
