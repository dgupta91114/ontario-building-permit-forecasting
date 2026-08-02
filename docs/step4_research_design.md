# Step 4 - Research Design and Methodology

## Research design

This capstone uses a quantitative, longitudinal, predictive design with public government data. The unit of analysis is a census metropolitan area-month. The seasonal-naive forecast is the control condition. Elastic net, random forest, and XGBoost are experimental alternatives evaluated on identical chronological holdout observations.

## Technique selection

The target is continuous, so the study uses regression and time-series forecasting rather than classification. Elastic net is the interpretable linear benchmark and helps manage correlated lag features. Random forest is included as a nonlinear ensemble that is more stable than a single decision tree. XGBoost is included as a regularized boosting model. Neural networks are excluded from the primary comparison because the planned sample is below 500 observations and a larger architecture would create unnecessary overfitting and interpretability risk.

## Statistical methods

- Descriptive statistics: mean, median, standard deviation, interquartile range, coefficient of variation, minima, maxima, and autocorrelation.
- RQ1: Newey-West heteroskedasticity and autocorrelation consistent regression plus time-series diagnostics.
- RQ2: nested history-only versus macro-augmented elastic-net comparison with a prespecified 5% practical MAE threshold.
- RQ3: paired t test, Wilcoxon signed-rank test, and Diebold-Mariano-style loss-differential test.
- RQ4: regional absolute-error analysis using ANOVA and a planned robust/nonparametric sensitivity test.
- Regression diagnostics: residual plots, Q-Q plots, residual autocorrelation, VIF, adjusted R-squared, AIC, and BIC where appropriate.

## Evaluation metrics

- MAE
- RMSE
- MASE
- sMAPE
- WAPE
- Prediction-interval coverage

Model selection is based on out-of-sample performance, not training fit. The selected model must have pooled MASE below 1.0, beat seasonal naive on MAE, avoid material degradation in three or more CMAs, and pass reproducibility checks.

## Validation and experiment design

Random k-fold cross-validation is not used for the primary comparison because it would violate temporal ordering. The project uses expanding-window cross-validation within the training period and a final 12-month holdout. All preprocessing, imputation, scaling, encoding, and hyperparameter selection occur inside training folds.

## Data preparation

- Freeze raw files and record URL, extraction time, file size, and SHA-256 hash.
- Audit official category labels before filtering.
- Convert dates to monthly timestamps and validate one row per CMA-month.
- Create within-CMA lags and rolling features only after sorting.
- Fit imputation/scaling/encoding on training data only.
- Retain valid outliers in the primary analysis; use robust metrics and sensitivity transformations.
- Do not impute missing targets.

## Explainability and governance

Permutation importance and SHAP are used to describe model behavior. They are not treated as causal estimates. Final outputs include regional reliability metrics, prediction intervals, and explicit warnings that building permits measure construction intentions rather than completed construction or housing affordability.
