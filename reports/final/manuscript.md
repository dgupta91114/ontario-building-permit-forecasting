[[TITLE_PAGE]]

<!-- PAGE -->

[[REPOSITORY]]

# Abstract

Monthly residential building-permit values help analysts assess likely construction activity. Yet large projects, unequal market sizes, and changing conditions make these values hard to forecast. This study tests whether an explainable model can improve next-month estimates for five Ontario census metropolitan areas. Permit values measure authorized construction intentions, not completed homes or actual spending. The goal is a useful regional planning signal with a clear benchmark and visible uncertainty. The study uses permit and unemployment data from Statistics Canada and the Bank of Canada overnight-rate target. The frozen source window runs from January 2018 through May 2026. It contains 505 regional permit records; lags and the future target leave 440 complete region-month rows. Three expanding time windows tune elastic net, random forest, and extreme gradient boosting against seasonal naive. The final test covers 60 rows from June 2025 through May 2026. The implemented Python workflow uses pandas, scikit-learn, statsmodels, XGBoost, and SHapley Additive exPlanations on a central processing unit. XGBoost achieves mean absolute error of CAD 53.678 million, root mean squared error of CAD 73.485 million, and mean absolute scaled error of 0.571. Its mean absolute error is 53.8% below seasonal naive, with gains in every region. Adding the two lagged macroeconomic inputs to elastic net improves error by only 0.40%, below the required 5%. Recent permit history provides the main signal. A constant-dollar check also selects XGBoost. A separate interval model covers all 60 test outcomes, but its ranges are wide. The contribution is an auditable forecasting process for municipal analysts, suppliers, and workforce planners. A monitored pilot could pair regional forecasts with uncertainty ranges and project review. Deployment and financial gains have not been measured. Only 12 distinct test months, data revisions, release delays, and model selection on the holdout limit generalization. Prospective tests using actual release vintages are needed before routine use.

<!-- PAGE -->

# Introduction

## Background and Context

Residential development creates decisions before a building is completed: municipal teams review expected workloads, suppliers consider material availability, and employers assess capacity. A permit-value series can inform these discussions because authorization occurs early in the construction process. However, approval does not establish when work starts, whether the full project proceeds, or how many dwellings become available. Statistics Canada distinguishes permit information from subsequent construction activity; this report maintains that distinction throughout (Statistics Canada, 2026a).

The study setting comprises Toronto, Hamilton, Kitchener-Cambridge-Waterloo, London, and Windsor. These census metropolitan areas (CMAs) provide five related but differently scaled monthly series. Toronto's typical authorized value is much larger than the other markets, so a forecast judged only by pooled dollar error may primarily reflect Toronto. A useful regional system must report both the total error burden and performance relative to each CMA's historical variation.

The practical difficulty is that permit values combine persistent activity with abrupt project timing. Recent levels may be informative, yet a major authorization can create a movement that a smooth extrapolation misses. Provincial unemployment and the overnight-rate target are plausible contextual predictors, but their incremental information must be established after accounting for permit history. A relationship that matters economically need not improve a forecast at the particular horizon and aggregation used here.

This capstone addresses that difficulty as a prediction problem. It compares a transparent historical control with regularized regression and tree ensembles, then evaluates regional reliability and model attribution. The workflow treats interpretability, reproducibility, and uncertainty as parts of the deliverable. Predictive usefulness is assessed on later observations; a high explanatory fit within historical data is insufficient evidence of future accuracy (Shmueli, 2010).

<!-- PAGE -->

## Problem Statement

The objective is to predict Y, next-month seasonally adjusted residential building-permit value for each of five Ontario CMAs, using X, current and lagged permits, rolling summaries, calendar and CMA indicators, lagged Ontario unemployment, and the overnight-rate target, within the January 2018–May 2026 source window. Success requires lower holdout mean absolute error (MAE) than seasonal naive, pooled mean absolute scaled error (MASE) below 1, and no degradation exceeding 10% in three or more CMAs.

## Purpose of the Study

The study describes regional temporal structure, measures the incremental predictive value of two macroeconomic variables, compares model families, and explains the preferred model's behavior. It uses quantitative secondary data and observational comparisons.

## Research Problems / Research Questions

RQ1: What trend, seasonal, persistence, and volatility patterns characterize monthly residential building-permit values across the five CMAs?

RQ2: Do lagged Ontario unemployment and the Bank of Canada overnight-rate target improve forecast accuracy beyond permit history, calendar information, and CMA effects?

RQ3: Which candidate produces the most accurate and stable one-month-ahead forecasts across the evaluated time periods and regions?

RQ4: Which inputs contribute most to the preferred model's predictions, and how does forecast reliability differ across CMAs?

Each question has a distinct evidence requirement. RQ1 uses exploratory summaries and a descriptive regression; RQ2 uses matched feature-set comparisons; RQ3 uses chronological validation and common-target errors; RQ4 combines attribution, regional errors, and interval coverage. Formal hypotheses and their evaluation samples appear in Materials and Method, preventing the full dataset size from being mistaken for the sample available to every test.

<!-- PAGE -->

## Contributions and Expected Value

The practical contribution is a repeatable way to turn public regional tables into forecasts with visible limits. An analyst receives a defined target, a benchmark comparison, regional error measures, and uncertainty bounds. These outputs support a discussion about plausible near-term activity without requiring the analyst to reproduce a national statistical extraction manually.

The technical contribution is the integration of established methods for this particular five-CMA setting. The pipeline checks source dimensions, constructs within-region lags, holds complete months together during validation, and applies an explicit acceptance rule. It also separates the fitted model used for the point-accuracy comparison from the model used to form calibrated intervals. These are implementation and evaluation contributions; the study does not claim a new forecasting algorithm or universal superiority of machine learning.

The evidence package connects every reported outcome to a saved dataset, prediction file, or diagnostic. The full data dictionary appears in Appendix A, and Appendix B maps report claims to repository artifacts. Additional report diagnostics recompute training accuracy and summarize paired errors by calendar month; they are identified as supplementary and do not replace the original holdout results.

Expected value is conditional on a successful pilot. Lower forecast error may improve the information available for capacity discussions, but no monetary savings, inventory reductions, or planning-time improvements have been measured. A prospective pilot would need to record those outcomes directly. This distinction protects decision makers from interpreting an accuracy percentage as a business return.

The remainder of the report reviews relevant literature, explains materials and methods, presents the architecture, evaluates results, and describes implementation, limitations, and further improvements. All essential design choices and findings are included here so that the report can be read without the synopsis, interim submission, or presentation.

<!-- PAGE -->

# Literature Review

## Literature Review Approach

The review is a focused methodological synthesis rather than a systematic review or meta-analysis. Relevant sources were located through targeted web searches and reference links using construction-demand forecasting, economic indicators, time-series validation, forecast accuracy, elastic net, random forest, gradient boosting, interpretability, power, and conformal prediction as search concepts. Bibliographic details and claims were checked against publisher records, proceedings, author-hosted manuscripts, or official documentation.

Inclusion required a direct connection to the domain problem, a candidate method, evaluation design, statistical planning, or interpretation. Official documentation establishes the meaning and access conditions of the data. Articles provide methodological reasoning, but their empirical findings are not treated as Ontario estimates. Tables 1 and 2 summarize 12 relevant research sources, including their context, method, findings, and connection to the research questions.

## Summary of Key Literature

Goh (1996) studied Singapore residential construction demand using economic indicators and compared neural networks with multiple regression. The article provides a domain precedent for testing economic inputs and contrasting linear with nonlinear approaches. Its setting and target differ from Ontario monthly permit values, so it motivates candidate comparisons rather than establishing which model should win here. The accessible abstract establishes the comparative design; no unavailable numerical performance claim is imported.

Zou and Hastie (2005) developed elastic net to combine shrinkage with variable selection, including a grouping behavior for correlated predictors. Permit lags and rolling means are strongly related by construction, making regularization pertinent. Breiman (2001) demonstrated the value of averaging randomized trees, while Chen and Guestrin (2016) developed a scalable, regularized boosting system. Together these sources justify a small set of materially different learners.

<!-- PAGE -->

## Critical Synthesis and Research Gap

Evaluation design is central to the contribution. Tashman (2000) explained how forecast origins, fitting windows, and test periods affect comparability. Bergmeir et al. (2018) showed that ordinary cross-validation can be valid for particular autoregressive settings with uncorrelated errors. That conditional result does not establish that random row splits are appropriate for this dependent regional panel. The present study therefore uses complete chronological month blocks and distinguishes tuning, final refitting, and holdout assessment.

Hyndman and Koehler (2006) demonstrated weaknesses in familiar accuracy measures and proposed MASE for cross-series comparison. Their reasoning is especially pertinent when one CMA dominates dollar totals. MAE remains useful for economic scale, while MASE adds a historical within-region reference. Diebold and Mariano (1995) framed comparison in terms of paired predictive losses and dependence. Here, inferential calculations complement practical error thresholds; they cannot repair a short holdout or substitute for honest identification of the independent time units.

Lundberg and Lee (2017) introduced a common additive framework for feature attribution. Shmueli (2010) distinguished predictive, descriptive, and explanatory goals. Read together, these studies support explaining how a model uses permit history while avoiding claims that a large attribution is a causal driver. Correlated lags can divide or substitute for one another's apparent importance, so a ranked feature chart is interpreted as model behavior within the observed data.

Angelopoulos and Bates (2023) explained how conformal prediction forms uncertainty sets under explicit conditions. This motivates reporting bounds alongside point forecasts, but temporal dependence and shared provincial inputs make unconditional coverage promises inappropriate. Cohen (1992) likewise emphasizes planning power around the effect and sample actually being tested. The applied gap is an integrated, auditable regional forecasting process that addresses these concerns together. Deep learning and agentic systems were not implemented; the study's small monthly panel and structured numerical target did not require them.

<!-- PAGE -->

[[TABLE:literature1]]

The first six sources connect the domain question with evaluation discipline. Their principal implication is that a plausible predictor or sophisticated algorithm still needs a clearly defined target, a valid comparison period, and a sample appropriate to the stated inference. The relevance column records the specific design decision adopted here.

<!-- PAGE -->

[[TABLE:literature2]]

The remaining sources motivate regularization, nonlinear alternatives, attribution, and uncertainty. Their findings are methodological precedents. They do not constitute external validation of the five-CMA results. The report tests the adopted methods within its own frozen observations and identifies the conditions that remain unverified.

<!-- PAGE -->

# Materials and Method

## Data Sources, Inclusion, and Exclusion

[[TABLE:sources]]

Table 3 identifies the sources. The unit of analysis is one CMA in one calendar month. The retained geographical scope is Toronto, Hamilton, Kitchener-Cambridge-Waterloo, London, and Windsor; other geographies are excluded. Permit filters select total residential structures, all work types, value of permits, seasonally adjusted current values, dollar units, and the thousands scalar. Counts, non-residential categories, and unadjusted values are excluded from the primary analysis (Statistics Canada, 2026b).

Unemployment filters select Ontario, unemployment rate, total gender, ages 15 years and over, seasonally adjusted data, and the estimate statistic (Statistics Canada, 2026c). The daily policy-rate series is summarized by its last observed value in each month. Macroeconomic predictors are then lagged by one reference month. Source access uses official downloadable tables and the Valet application programming interface (API), not webpage scraping (Bank of Canada, n.d.).

The source window is deliberately frozen at January 2018–May 2026 for continuity with the completed empirical study. Archives were downloaded on August 16, 2026 (UTC). May 2026 is the study cutoff, not a claim about the latest information available on the submission date. The report uses Canadian dollars (CAD); saved values are in thousands, while monetary result tables are converted to millions for readability.

<!-- PAGE -->

## Data Preparation and Exploratory Analysis

The permit cleaner streamed 38,338,128 national rows and retained 505 observations, representing 101 months in each selected CMA. The unemployment cleaner examined 5,457,537 rows and retained 101 monthly observations. The rate source contained 2,181 daily records, aggregated to 101 months. These scan counts describe source processing, not sample size. The analytical population remains the selected CMA-month records.

Joins use the reference month and enforce many-to-one relationships for province-wide macroeconomic inputs. Every selected source value is present. One London permit observation for April 2025 has the published E status, indicating use with caution. It is retained and disclosed because it is a usable official estimate. Blank status fields are not treated as missing permit values. Legitimate large authorizations remain in the data; deleting them would suppress a material source of forecasting risk.

Feature construction removes the first 12 origin months in each region and the final origin lacking a future target. Thus, 505 − 5(12 + 1) = 440 complete records remain. Origins cover January 2019–April 2026, and targets cover February 2019–May 2026. There are 88 targets per CMA, no duplicate CMA-target keys, and no missing modeled targets. Transformations operate within region before rows are sorted into chronological validation order.

Exploratory data analysis (EDA) describes scale, dispersion, persistence, and temporal shape through summary statistics, autocorrelations, plots, and a pooled descriptive regression. Because the source is already seasonally adjusted, the calendar profile measures residual calendar structure, not raw seasonal demand. EDA on the full analytic panel is descriptive; it does not supply a new feature search after viewing the holdout. Figures and tables in Results show regional behavior without forcing all markets onto Toronto's vertical scale.

The analysis contains public aggregates and no participant recruitment or individual-level identifiers. It supports regional interpretation only; a relationship in these aggregates cannot establish individual household or developer behavior.

<!-- PAGE -->

## Research Hypotheses

All reported hypothesis decisions use a nominal two-sided significance level of α = .05. Direction and practical usefulness are evaluated from the observed loss difference, not inferred from a small p value alone. Several comparisons are exploratory, and their assumptions are discussed explicitly.

RQ1: For each specified temporal coefficient β in a pooled ordinary least squares (OLS) regression of next-month permit value on current permits, calendar sine/cosine, time index, and CMA indicators, H₀: β = 0 and Hₐ: β ≠ 0. Autocorrelation and volatility summaries answer the descriptive parts of RQ1. The study does not perform a formal search for unknown structural break dates.

RQ2: Let d be the history-only elastic net's absolute error minus the macro-augmented elastic net's absolute error for the same target. H₀: E(d) = 0; Hₐ: E(d) ≠ 0. Positive d favors macroeconomic augmentation. Adoption additionally requires at least 5% lower pooled MAE. This hypothesis concerns the two added variables within elastic net; it does not establish their causal effects or evaluate a history-only XGBoost variant.

RQ3: For each fitted candidate, define d as seasonal naive's absolute error minus the candidate's absolute error. H₀: E(d) = 0; Hₐ: E(d) ≠ 0. The practical decision also requires MASE below 1 and an acceptable regional degradation count. A supplementary comparison of XGBoost with random forest tests the same loss-difference hypothesis without changing the model-selection rule.

RQ4: H₀ states that the preferred model's mean absolute error is equal across the five CMAs; Hₐ states that at least one regional mean differs. One-way analysis of variance (ANOVA) provides a nominal omnibus test. Feature attribution and interval coverage answer additional descriptive parts of RQ4 and are not presented as causal hypothesis tests. Failure to reject any null is not evidence that its effect is exactly zero.

<!-- PAGE -->

## Minimum Sample Size Calculations

[[TABLE:sample]]

Table 4 summarizes the planning assumptions. Calculations target power 1 − β = .80 at α = .05. They use planning effect sizes rather than effects selected after observing significance. Cohen (1992) provides the rationale for distinguishing effect size, significance, sample size, and power. The executable calculations are reproduced in the evidence package.

For RQ1, Fisher's transformation gives n = ceiling{[(1.960 + 0.842) / atanh(.30)]² + 3} = 85. This is an independent-pair correlation approximation, not an exact power analysis for the final panel regression. For RQ2, the solver finds the minimum n for a noncentral F test with numerator degrees of freedom 10, denominator n − 11, and noncentrality λ = .15n. The result is 118.

For RQ3, the paired t-test calculation solves for the smallest n attaining .80 power when standardized mean paired difference d = .35; rounding upward gives 67 pairs. For RQ4, a five-group noncentral F calculation with Cohen's f = .25 gives total n = 196. At equal allocation, rounding to whole region groups would require 40 observations per CMA, or 200 overall. These figures must be compared with the relevant evaluation sample rather than with all 440 modeling rows.

<!-- PAGE -->

## Sample Adequacy and Statistical Interpretation

The available dataset exceeds some planning counts but does not satisfy every inferential requirement. RQ1 has 88 analytic observations per region and 440 pooled rows; serial dependence limits the meaning of comparing these numbers with the 85 independent pairs assumed by the approximation. RQ2's original 118-row calculation concerns a 10-predictor regression F test. The implemented ablation is a paired forecast-error comparison on 60 holdout rows, so that planning calculation is not a direct power justification for the final test.

RQ3 has 60 paired CMA-month errors against a planned minimum of 67. RQ4 has 60 total regional errors, only 12 per CMA, against 196 planned independent observations. Under the original effect assumptions and independence, achieved power would be approximately .760 for RQ3 and .278 for RQ4. These are design-sensitivity calculations, not retrospective estimates of the probability that the conclusions are correct. Shared months and serial dependence further weaken any claim that row counts represent independent replication.

The original descriptive regression uses a heteroskedasticity and autocorrelation consistent (HAC) covariance estimate with three lags, following the general approach of Newey and West (1987). The saved code applies it to pooled row order. Its lag units are therefore rows rather than a complete regional time covariance structure. Likewise, the original Diebold–Mariano-style calculation operates on ordered pooled losses. Those p values are reported as nominal supporting diagnostics, not fully validated panel inference.

To make this limitation concrete, supplementary comparisons first average absolute errors across the five CMAs within each of the 12 holdout months. A paired t test then uses 12 monthly differences. This removes the claim that contemporaneous regions provide separate time replications, although it still assumes suitable independence across months. The report gives confidence intervals and labels these checks exploratory. No supplementary result was used to retune a model, change the study window, or rewrite the original acceptance rule.

<!-- PAGE -->

## Feature Engineering and Predictor Availability

For region g and origin reference month t, the outcome is y(g,t+1). History inputs are y(g,t), lags at 1, 3, 6, and 12 months, and the mean and sample standard deviation of y(g,t), y(g,t−1), and y(g,t−2). Target-month sine and cosine terms represent the annual calendar, a time index measures elapsed months since January 2018, and a fixed indicator marks targets from March 2020 through June 2021. Five one-hot CMA columns represent regional level differences.

The primary numeric set contains 11 features; macro augmentation adds two lagged percentages. The resulting full transformed matrix has 18 columns: 13 numeric variables and five CMA indicators. Unlagged macro values and geographic audit identifiers remain in the saved data but are excluded from model inputs. Appendix A defines these roles. The pandemic indicator is included in the fitted specification; its historically fixed dates were not independently established as a causal intervention boundary.

Median imputation, standard scaling, and categorical encoding are fitted inside each training pipeline. Although the selected analytic features are complete, these steps define consistent transformations. Unknown categories are ignored by the encoder; operational use should still reject an unvalidated new CMA. Targets are modeled as log(1 + y), converted back with exp(z) − 1, and truncated at zero. This inverse transformation is not a bias-corrected conditional mean; original-dollar accuracy determines its practical suitability.

For target t + 1, seasonal naive uses y(g,t−11), the same calendar month one year earlier. It does not use the 12-month origin lag, which would be one month misaligned. Chronological reference-month construction prevents use of future target values. However, official permits for month t are published later and may subsequently be revised. The backtest is therefore conditional on recorded reference-month data, not an archived real-time information set. Deployment must align forecasts with actual release availability and may require a nowcasting formulation.

<!-- PAGE -->

## Data Splitting and Validation

[[TABLE:splits]]

Table 5 specifies the date partitions. The latest 12 target months form the holdout. Earlier observations provide 76 training months, or 380 rows. Three expanding-window folds begin with 36 months, assess the next 12 months, and advance by 12 months. All five CMA observations for a given target month remain in the same partition.

Grid search minimizes mean validation MAE on the original target scale. Each candidate configuration is fitted only to the training portion of each fold, including preprocessing. The best configuration is then refitted on all 380 pre-holdout rows. Consequently, this is a sequence of one-month predictions, not a 12-step forecast generated from one starting date.

The final holdout supplies the family comparison and acceptance decision as well as the reported performance estimate. Hyperparameters were not fitted to it, but this use introduces selection optimism. A genuinely untouched prospective period is still needed. Random forest's stronger earlier validation MAE and XGBoost's stronger final holdout MAE are both disclosed, because ranking stability matters for operational adoption.

The separate interval procedure reserves the last 12 pre-holdout months for calibration and trains a clone on the preceding 64 months. Its predicted center is retained with its own bounds. Calibration observations also participated in earlier hyperparameter selection, which further limits a strict split-conformal guarantee.

<!-- PAGE -->

## Model Selection and Justification

[[TABLE:models]]

Seasonal naive is an interpretable annual reference requiring no estimated parameters. Elastic net provides a regularized linear predictor on the transformed target. Random forest averages trees, while XGBoost adds a sequence of corrective trees. These families test different complexity and interaction assumptions on the same structured task (Breiman, 2001; Chen & Guestrin, 2016; Zou & Hastie, 2005).

Table 6 documents the search. The grid contains four configurations for each fitted specification and three validation folds, yielding 48 fold fits across two elastic nets and two ensembles, plus final refits. Both tree families use the macro-augmented feature set. No separate neural, autoregressive integrated moving-average, or history-only tree model was evaluated; superiority is limited to the candidates actually tested. The small grids reflect the modest number of distinct months.

The acceptance algorithm orders candidates by pooled MASE and then MAE. It requires MASE < 1, MAE below seasonal naive, and no more than two CMAs with MAE degradation exceeding 10%. Evidence and reproducibility checks accompany release. If none qualifies, seasonal naive remains the control. The rule is transparent, but it still uses holdout outcomes to choose a family. Its prespecification reduces discretion without converting the selected error estimate into an independent external validation.

<!-- PAGE -->

## Accuracy Measures and Uncertainty

Let eᵢ = yᵢ − ŷᵢ for an evaluated row. MAE = (1/n)Σ|eᵢ| retains the target's units; root mean squared error (RMSE) = √[(1/n)Σeᵢ²] gives more weight to large misses. These measures are calculated on original permit values, not on log targets. Training errors describe fitted history, while validation and holdout errors measure predictions for later targets.

For each CMA g, the seasonal scaling denominator is s(g) = mean|y(g,u) − y(g,u−12)| over available pairs in the pre-holdout training targets. Pooled MASE = mean[|eᵢ|/s(gᵢ)]. Thus, each row contributes relative to its own CMA's training scale (Hyndman & Koehler, 2006). A holdout seasonal-naive MASE need not equal 1 because its numerator and scaling denominator come from different periods.

Symmetric mean absolute percentage error (sMAPE) is 100 × mean[2|y − ŷ|/(|y| + |ŷ|)]. Weighted absolute percentage error (WAPE) is 100 × Σ|e|/Σ|y|. A small numerical floor prevents division by zero. sMAPE weights relative row errors; WAPE is strongly influenced by higher-value targets. Percentage measures supplement dollar and scaled errors rather than define a single universal winner.

The interval branch uses absolute residuals from 60 calibration rows. With α = .10, the finite-sample quantile level is ceiling[61 × .90]/60 = 55/60. The implementation applies NumPy's higher empirical quantile, giving radius q = CAD 304.281 million. Bounds are max(0, ŷ − q) and ŷ + q. This rule is conservatively rounded and uses a pooled radius. Temporal dependence, reuse of calibration months in tuning, and regional scale differences mean empirical coverage must be reported without an automatic future guarantee (Angelopoulos & Bates, 2023).

<!-- PAGE -->

# Architecture Diagram/Workflow

## System Overview

The system converts official data into reproducible forecast evidence for RQ1–RQ4. Figure 1 shows the implemented stages and the separate point and interval branches. Solid boxes denote completed analytical components; the dashed box denotes a proposed operational pilot. Arrows indicate data or artifact flow, not causal relationships.

## Architecture Diagram

[[FIGURE:architecture]]

<!-- PAGE -->

## Workflow Components

Data ingestion downloads the two Statistics Canada tables and Bank of Canada rate observations. A manifest records endpoints, timestamps, and SHA-256 hashes. National CSV files are filtered in chunks so that only the needed records enter later stages. The report's compact dataset can therefore be inspected independently of the very large national files.

Data preprocessing validates labels, value basis, units, selected geography, and monthly joins. Source flags remain available for review. Feature engineering operates within CMA, derives the next-month target and lagged histories, and checks unique target keys. EDA then produces descriptive summaries, temporal graphics, and regression outputs. No relational database was created: versioned CSV and JSON files serve as the study's storage and access layer.

Model development uses a preprocessing pipeline and transformed-target wrapper for each fitted learner. Chronological grid search selects settings; refitting produces the saved estimators. Evaluation writes predictions for every model on the same 60 targets and derives pooled and regional errors. The model-selection file stores the acceptance outcome, while paired tests provide supporting diagnostics. These outputs answer the model comparison without relying on screenshots or manually copied calculations.

The interval branch clones the selected configuration, fits it before the calibration period, and calculates a shared residual radius. Its point predictions are stored in the same rows as the lower and upper bounds. Explanation uses permutation importance on original inputs and SHAP on the transformed fitted model. Those two explanation scales remain distinct in the captions and interpretation.

Reporting joins the evidence into tables, labeled figures, narrative, and appendices. A validation stage checks frozen hashes and recomputes metrics from saved predictions. The September report diagnostics add training errors and month-level comparisons in a separate evidence directory. Deployment as a live API or dashboard has not occurred. The proposed pilot adds issuance-date checks, an analyst-facing scorecard, and prospective monitoring to the existing batch analysis.

<!-- PAGE -->

## Tools and Technologies

The analytical environment uses Python 3.11 and runs on a central processing unit (CPU); the code does not require a graphics processing unit (GPU). pandas and NumPy support tabular processing and numerical transformations. scikit-learn supplies preprocessing, elastic net, random forest, and grid search. XGBoost supplies boosted trees; SciPy and statsmodels support statistical tests, power calculations, and descriptive regression. Matplotlib generates figures, SHAP provides attribution, and joblib stores fitted estimators.

Configuration in YAML fixes the five CMAs, analysis dates, feature sets, forecast horizon, validation windows, random seed 640, search grids, and acceptance thresholds. The fitted estimators use one worker, and the environment lock records dependency versions. Jupyter notebooks provide staged analytical entry points, while numbered scripts provide a repeatable execution sequence. The final report is generated as an editable Word document and exported to PDF; document rendering is separate from model fitting.

Git tracks the source code, compact dataset, configuration, frozen result tables, figures, and report artifacts. National raw files and fitted model binaries are excluded from ordinary version control because they are generated or large. Their provenance and regeneration steps remain documented. Raw archive hashes establish identity if an original copy is retained; they cannot retrieve an unavailable historical archive from a changing source endpoint.

The recorded August reproducibility report passed its dataset checks and 11 tests. For this final report, official metric values were independently recalculated from stored holdout predictions, saved estimators reproduced those predictions, and training metrics were obtained from those same estimators. The final quality audit records the checks actually run for this release. It does not describe a fresh national download or complete retraining as completed when only report evidence was verified.

Appendix B identifies commands and files needed to reproduce or inspect the analysis. This distinction between reproducibility instructions and executed verification lets an evaluator trace the evidence without assuming that all possible checks were rerun.

<!-- PAGE -->

# Results

## Model Performance

[[TABLE:training]]

Table 7 supplies the requested training and test accuracy together with the earlier validation comparison. Training values are resubstitution errors from each estimator fitted on 380 pre-holdout observations. The same estimators reproduce the archived holdout predictions; the report did not fit a new model to obtain these diagnostics. Cross-validation (CV) values average three earlier validation periods, and holdout values use the common final 60 targets.

Random forest has the lowest mean CV MAE at CAD 85.497 million, whereas XGBoost has the lowest holdout MAE at CAD 53.678 million. Thus, the observed ranking depends on the evaluation period. XGBoost's training MAE of CAD 65.078 million is higher than its final holdout MAE. That ordering is possible because error distributions and large-project realizations differ across periods; it does not establish that training data were ignored or that leakage is absent.

The comparison also reveals a substantial validation-to-holdout change for both elastic nets. Its practical implication is that one favorable final period should not be used to promise stable future accuracy. Historical fit, validation, and holdout each answer a different question. A prospective series of recorded forecasts is the appropriate next assessment of ranking and drift.

<!-- PAGE -->

## Holdout Comparison and Visual Evidence

[[TABLE:holdout]]

[[FIGURE:comparison]]

Table 8 and Figure 2 show XGBoost's 53.8% MAE reduction relative to seasonal naive, calculated as 100(116.200 − 53.678)/116.200 using unrounded values. XGBoost also has the lowest RMSE, MASE, and WAPE. Random forest has slightly lower sMAPE, so the selected model does not dominate every criterion. The two tree models' MASE values differ by only about 0.0006; selection should not be described as decisive evidence of universal superiority.

<!-- PAGE -->

## Results by Research Question: RQ1

[[FIGURE:history]]

Figure 3 plots the observed histories used as predictor origins, January 2019–April 2026. Separate vertical scales expose movement in all five regions while preserving their labels and units. Toronto's series occupies a much larger dollar range; several smaller markets show substantial changes relative to their own level. Large observed movements remain part of the forecasting problem rather than being removed to improve accuracy. Table 9 quantifies the scale and volatility differences, and Table 10 evaluates persistence and conditional temporal terms.

<!-- PAGE -->

## RQ1: Scale, Persistence, and Conditional Associations

[[TABLE:summary]]

[[TABLE:temporal]]

Toronto's mean is approximately 21 times Windsor's, but Hamilton has the largest coefficient of variation. Annual-lag autocorrelation is negative in four CMAs and only weakly positive in Hamilton. This does not support an assumption of uniformly strong annual persistence in already adjusted values.

The pooled OLS regression has R² = .923, reflecting regional level differences as well as current permits. The current-value coefficient is 0.315 (nominal p < .001), and the time coefficient is positive (575.298 thousand CAD per month; p = .007). Neither seasonal term is significant. At α = .05, the nominal tests reject the zero-coefficient nulls for current value and trend, but not for the calendar terms. These are descriptive results with the pooled-HAC limitations described earlier; R² is not holdout predictive accuracy.

<!-- PAGE -->

## RQ2: Incremental Macroeconomic Information

[[TABLE:rq2]]

Table 11 shows that the macro-augmented elastic net improves holdout MAE by CAD 0.300 million, equivalent to 0.396%. The gain falls well short of the prespecified 5% requirement. The original paired t test gives t(59) = 1.089, p = .280; the Wilcoxon signed-rank p value is .276, and the saved DM-style p value is .256. None rejects equal predictive loss at α = .05.

The supplementary calculation uses one pooled error difference per month. It gives t(11) = 1.118, p = .287, and a 95% interval for mean MAE reduction of CAD −0.291 to 0.891 million. Nine months favor the augmented model, but the average advantage is small relative to uncertainty. Monthly aggregation addresses shared regional timing; residual serial dependence and the short series remain limitations.

This evidence answers RQ2 narrowly: adding these two lagged macroeconomic series to the specified elastic-net history model does not establish practically useful one-month predictive improvement. It does not demonstrate that unemployment or policy rates are economically irrelevant. Their information may already be represented in recent permits, may operate at a different lag, or may be obscured by provincial aggregation and project timing.

The selected XGBoost model still contains both macro features. An elastic-net ablation and weak feature importance do not establish that removing them from XGBoost would preserve its performance. A history-only tree comparison belongs in a new prospective experiment.

<!-- PAGE -->

## RQ3: Forecast Behavior Over the Holdout

[[FIGURE:forecasts]]

Figure 4 shows the full-pre-holdout XGBoost point model, with a separate scale for each CMA. Its forecasts track regional levels while missing some abrupt monthly movements. The original paired comparison against seasonal naive gives t(59) = 3.170, p = .002; Wilcoxon p = .002. Those nominal results support the practical error reduction, subject to dependence and model-selection limitations.

<!-- PAGE -->

## RQ3 Stability and RQ4 Regional Reliability

[[TABLE:regional]]

[[TABLE:monthly]]

Table 12 shows that XGBoost reduces MAE in every CMA and exceeds the 10% degradation tolerance in none. Its regional MASE stays below 1, with Kitchener-Cambridge-Waterloo closest to that boundary at 0.924. Toronto accounts for about 42.9% of the selected model's total absolute error, so both scaled and monetary views remain necessary. The nominal regional ANOVA gives F(4, 55) = 12.725, p < .001; unequal scales and dependent months limit a strict inferential interpretation.

Table 13 shows lower monthly pooled error than seasonal naive in 10 of 12 months. The supplementary interval for its mean advantage excludes zero under the monthly t-test assumptions. Against random forest, the corresponding interval includes zero and p = .439. Therefore, the study supports a practical preference for XGBoost under its rule, not a demonstrated significant advantage over the competing tree model.

<!-- PAGE -->

## RQ4: Interpretation of the Preferred Model

[[FIGURE:permutation]]

[[FIGURE:shap]]

Figures 5 and 6 identify current permits, the rolling mean, and recent lags as the strongest signals. Permutation measures the change in original-dollar MAE; SHAP decomposes the fitted log-scale prediction. Their numerical magnitudes are not interchangeable. The rate's zero permutation importance and nonzero SHAP attribution illustrate that feature use need not imply incremental predictive value. Correlated inputs and permutations across regions can distort rankings. These charts explain fitted behavior and support the history-dominant interpretation without establishing causality.

<!-- PAGE -->

## RQ4: Prediction Intervals and Decision Precision

[[TABLE:coverage]]

The separate interval fit covers all 60 holdout outcomes, compared with the nominal target of 90%. Its pooled half-width before truncation is CAD 304.281 million. Toronto's average interval width is CAD 608.562 million; lower bounds for smaller markets often reach zero. Table 14 demonstrates why coverage alone is insufficient: a very broad interval can contain observations while providing limited help for a precise commitment.

The interval branch was trained on 320 observations and calibrated on 60 later pre-holdout observations. Its own holdout MAE is CAD 51.354 million and MASE is 0.544. These supplementary values identify that branch; the headline MAE of CAD 53.678 million belongs to the 380-row point-model refit. Bounds must remain attached to their own predicted center, rather than being drawn around the headline model's different forecasts.

All 12 observations are covered in each CMA, but there are too few distinct months to establish stable regional calibration. Shared economic conditions, model selection, and tuning reuse also weaken exchangeability. A 100% historical coverage figure is therefore not a probability guarantee for an individual future month. Useful monitoring needs both coverage and width, preferably alongside regional scale and decision requirements.

 They are not precise monthly budgets. A pilot should record whether a forecast range is narrow enough to influence a real decision; an interval that is statistically conservative may still have little operational value.

<!-- PAGE -->

## Overall Interpretation and Practical Significance

[[TABLE:sensitivity]]

Table 15 presents the constant-dollar comparison. That analysis retains the 440-row design and again selects XGBoost, with MASE 0.449 and MAE reduction of approximately 49.6% against its own seasonal-naive benchmark. The macro-augmented elastic net is 3.82% worse than history-only in that analysis. Agreement in the selected family strengthens the conclusion that the main ranking is not unique to current-dollar measurement. Absolute errors across price bases should not be interpreted as a direct improvement comparison.

Across the four questions, regional scale and persistence differ, the macroeconomic ablation misses its practical threshold, tree ensembles improve the tested holdout, and current permit history dominates attribution. These results support an explainable planning workflow, with XGBoost as the preferred evaluated configuration and random forest as a competitive alternative. The literature supplies the methodological justification; the Ontario estimates come from this study's data and saved predictions.

The strongest practical result is a reduction in historical forecast error with transparent regional checks. The weakest operational evidence concerns actual issuance timing, interval usefulness, and measured user benefit. None has been validated by a deployed user trial. Successful implementation therefore depends on more than selecting the smallest error in Table 8: it requires reliable data availability, retained forecast vintages, review of unusual authorizations, and a process for reassessing performance as new months arrive.

<!-- PAGE -->

# Implementation and User Benefit

## Deployment Approach

The completed implementation is a scripted batch analysis: source acquisition, filtering, feature engineering, model fitting, evaluation, interval construction, attribution, and report generation. It produces versioned files and saved models. It is not a running public API or deployed dashboard. A practical next step is a shadow pilot in which forecasts are issued and archived without automatically triggering procurement, staffing, or policy decisions.

A monthly pilot would begin when the required official releases become available. The data owner would capture release timestamps and revisions, validate source dimensions, and identify the latest information actually available for each forecast. The model owner would generate regional outputs using a versioned specification. An analyst would review unusual values and local project context before publishing an internal scorecard. Subsequent releases would provide the actual values used to evaluate those archived forecasts.

## System Integration

The initial integration can use the existing CSV outputs in a spreadsheet or business-intelligence tool. Required fields include CMA, forecast issuance date, target reference month, data-vintage identifier, model version, point estimate, uncertainty bounds from the matching interval model, benchmark estimate, and recent regional performance. Release-time metadata must be added during the pilot because the historical analysis primarily records reference months.

 A scheduled run should stop if required dates are missing, values have incompatible units, a new geography appears, or key uniqueness checks fail. Successful runs should retain the inputs and outputs needed to reconstruct what the analyst saw. Revisions must create new vintages rather than silently replacing an issued forecast's evidence.

The existing seasonal-naive control should remain visible in every evaluation cycle.

<!-- PAGE -->

## User Interaction

An analyst would select a CMA and target month, review the point and range together, compare the seasonal-naive reference, and inspect recent regional error. An annotation should identify unusual project context and whether the data were revised. The proposed interface should distinguish forecast issue date from target reference month so that a historical backtest is not mistaken for a current forecast.

## Benefits to Users

Expected benefits are consistent preparation, clearer regional comparisons, and an explicit uncertainty discussion. A pilot should measure preparation time, forecast availability, analyst usage, whether the information changed a decision, and prospective error and coverage. Financial savings require a separate evaluation with relevant costs and a credible comparison workflow; they cannot be derived by multiplying budgets by the 53.8% accuracy improvement.

## Example Use Case

[[TABLE:example]]

Table 16 uses a recorded historical output to illustrate the proposed scorecard. For Kitchener-Cambridge-Waterloo, the interval-model estimate for June 2025 was about CAD 99.3 million, and the observed value was CAD 159.8 million. The range reaches from zero to approximately CAD 403.6 million. A supplier could use this as one scenario input alongside its confirmed orders, while an analyst investigates project timing. This is a retrospective demonstration of output interpretation, not evidence that a customer used the system or achieved an operational gain.

<!-- PAGE -->

# Limitations and Further Improvements

## Limitations

The geographical scope is five Ontario CMAs, with only 88 analytic target months per region. The panel includes pandemic disruption and relatively few annual cycles. Findings may not generalize to other regions, non-residential permits, different horizons, or housing completions. An aggregate regional association cannot be translated into a project-level or household-level causal claim.

The series are revised official estimates, and one London value is flagged for caution. More fundamentally, reference-month order is not release-date availability. Because month-t permits may be published after month t + 1 begins or ends, this experiment cannot be advertised as a fully real-time next-calendar-month forecast. A source-vintage backtest could produce different errors and may require nowcasting or a later horizon.

The holdout contains 60 region-month rows but only 12 distinct months. Planned evaluation sample sizes for RQ3 and RQ4 are not met. Shared macroeconomic series, regional shocks, and serial dependence make independent-row p values optimistic or otherwise unreliable. The original pooled HAC and DM-style implementations do not establish a complete panel covariance correction. Supplementary monthly comparisons remain small-sample diagnostics, and no multiple-testing adjustment was prespecified.

## Impact of Limitations

Model-family selection and reported performance use the same holdout. The apparent winner may consequently have benefited from that period's noise. The log-target inverse transform may introduce original-scale bias, and no broader model-family search was performed. Correlated-feature attributions can be unstable even when predictions are useful.

Finally, broad pooled intervals limit decision precision and do not establish prospective conditional coverage. Calibration months participated in tuning, and temporal exchangeability is unverified. The defensible conclusion is that the tested configuration improves this historical benchmark comparison and merits further evaluation, while real-time usefulness and user impact remain open empirical questions.

<!-- PAGE -->

## Future Improvements

The highest-priority improvement is an archived release-vintage evaluation. Each forecast should use only data actually published by its issue timestamp, retain any later revisions separately, and specify whether the task is forecasting or nowcasting.

Next, collect a longer sequence of prospective months before retuning. A new evaluation design should separate family selection from final assessment and choose power assumptions for the actual loss-comparison method. Dependence-aware resampling or panel covariance methods should operate on genuine month blocks, with uncertainty about their small-sample performance acknowledged. Regional scale should also be considered before interpreting omnibus differences in absolute dollar error.

Additional controlled experiments could compare history-only XGBoost, local unemployment, mortgage-rate measures, construction-cost indicators, and alternative forecast horizons. Region-adaptive intervals and rolling calibration may improve decision precision, but require prospective checks of coverage and width.

## Future Scope

Expansion to additional Ontario or Canadian CMAs would test transportability and provide more cross-sectional variety. A shadow pilot can then assess whether the system improves preparation efficiency and decisions without assuming that lower forecast error automatically yields savings.

## Conclusion

This study implements an auditable public-data workflow for next-reference-month residential permit values in five Ontario CMAs. XGBoost reduces holdout MAE by 53.8% against seasonal naive and meets the stated regional acceptance rule; macro augmentation of elastic net does not establish practical value. Recent permit history supplies the main predictive signal, and constant-dollar sensitivity supports the selected family. The appropriate next application is a monitored, release-aware planning pilot with uncertainty, benchmark comparisons, and prospective validation.

<!-- PAGE -->

# Bibliography

# References

[[REFERENCES:1]]

<!-- PAGE -->

[[REFERENCES:2]]

<!-- PAGE -->

[[REFERENCES:3]]

<!-- PAGE -->

# Appendix A: Data Dictionary

[[TABLE:dictionary]]

Note. The saved modeling dataset has 23 columns. The dictionary groups related lag and calendar columns for compact presentation. Monetary fields are in CAD thousands; report result tables divide those values by 1,000 to show CAD millions. Only the 11 primary numeric fields, two lagged macro fields when specified, and CMA enter fitted models. Raw macro values, geographic identifiers, quality flags, keys, target, and benchmark are retained for derivation or audit, not silently added as predictors.

<!-- PAGE -->

# Appendix B: Reproducibility and Evidence Map

[[TABLE:evidence]]

To reproduce the empirical pipeline, install the recorded environment and local package, then run the numbered data, sample-size, EDA, model, explanation, diagnostics, and sensitivity scripts. New downloads may contain revisions, so exact historical reproduction additionally requires matching the original archive hashes. The compact dataset and archived predictions permit metric verification without those national downloads.

To reproduce the final document, run scripts/14_prepare_final_report_evidence.py with the original saved estimators, then scripts/15_generate_final_report.py and export the resulting DOCX to PDF. The report generator can reuse committed diagnostic outputs when estimator binaries are unavailable. Run scripts/16_validate_final_report.py to check the generated PDF and document structure. These commands separate empirical verification, report creation, and submission checks.

All result tables and charts are original computations or visualizations of the identified public-data analysis. Literature summaries are paraphrased with source attribution. Source archives, code, and report changes are versioned independently so that the final submission can be traced to a specific evidence state.
