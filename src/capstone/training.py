from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, make_scorer
from sklearn.model_selection import GridSearchCV

from .config import project_root
from .conformal import split_conformal_interval
from .metrics import metric_row, paired_error_tests, seasonal_scales
from .models import make_model, parameter_grid
from .utils import write_json
from .validation import assert_month_integrity, expanding_month_splits, temporal_holdout_indices


def _features(cfg: dict[str, Any], include_macro: bool) -> tuple[list[str], list[str]]:
    numeric = list(cfg["features"]["primary_numeric_features"])
    if include_macro:
        numeric += list(cfg["features"]["macro_features"])
    categorical = list(cfg["features"]["categorical_features"])
    return numeric, categorical


def _fit_grid(
    name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    dates_train: pd.Series,
    numeric: list[str],
    categorical: list[str],
    cfg: dict[str, Any],
):
    estimator = make_model(name, numeric, categorical, int(cfg["project"]["random_seed"]))
    splits = expanding_month_splits(
        dates_train,
        int(cfg["validation"]["initial_train_months"]),
        int(cfg["validation"]["cv_test_months"]),
        int(cfg["validation"]["cv_step_months"]),
    )
    assert_month_integrity(dates_train, splits)
    scorer = make_scorer(mean_absolute_error, greater_is_better=False)
    search = GridSearchCV(
        estimator,
        parameter_grid(name, cfg),
        scoring=scorer,
        cv=splits,
        refit=True,
        n_jobs=1,
        return_train_score=False,
        error_score="raise",
    )
    search.fit(X_train, y_train)
    return search, splits


def _regional_metrics(predictions: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    scales = seasonal_scales(train)
    rows = []
    for (model, cma), part in predictions.groupby(["model", "cma"]):
        rows.append(
            {
                "model": model,
                "cma": cma,
                **{k: v for k, v in metric_row(
                    part["actual"], part["prediction"], part["cma"], scales, model
                ).items() if k not in {"model"}},
            }
        )
    return pd.DataFrame(rows)


def _select_model(metrics: pd.DataFrame, regional: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    naive = metrics.loc[metrics["model"] == "seasonal_naive"].iloc[0]
    tolerance = float(cfg["validation"]["regional_degradation_tolerance_pct"])
    candidates = metrics.loc[metrics["model"] != "seasonal_naive"].sort_values(["mase", "mae"])
    reasons = []
    for _, row in candidates.iterrows():
        model = row["model"]
        if not np.isfinite(row["mase"]) or row["mase"] >= 1.0:
            reasons.append(f"{model}: pooled MASE was not below 1.0")
            continue
        if row["mae"] >= naive["mae"]:
            reasons.append(f"{model}: pooled MAE did not beat seasonal naive")
            continue
        reg_model = regional[regional["model"] == model].set_index("cma")
        reg_naive = regional[regional["model"] == "seasonal_naive"].set_index("cma")
        joined = reg_model[["mae"]].join(reg_naive[["mae"]], lsuffix="_model", rsuffix="_naive")
        joined["degradation_pct"] = 100.0 * (joined["mae_model"] - joined["mae_naive"]) / joined["mae_naive"]
        materially_worse = int((joined["degradation_pct"] > tolerance).sum())
        if materially_worse >= 3:
            reasons.append(f"{model}: materially worse in {materially_worse} CMAs")
            continue
        return {
            "selected_model": model,
            "rule_outcome": "candidate accepted",
            "pooled_mase": float(row["mase"]),
            "pooled_mae": float(row["mae"]),
            "naive_mae": float(naive["mae"]),
            "materially_worse_cmas": materially_worse,
            "rejected_candidates": reasons,
        }
    return {
        "selected_model": "seasonal_naive",
        "rule_outcome": "no fitted candidate met all prespecified criteria",
        "pooled_mase": float(naive["mase"]),
        "pooled_mae": float(naive["mae"]),
        "naive_mae": float(naive["mae"]),
        "materially_worse_cmas": 0,
        "rejected_candidates": reasons,
    }


def train_and_evaluate(data: pd.DataFrame, cfg: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    base = root or project_root()
    table_dir = base / "outputs" / "tables"
    model_dir = base / "outputs" / "models"
    table_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    frame = data.copy()
    frame["target_date"] = pd.to_datetime(frame["target_date"])
    frame = frame.sort_values(["target_date", "cma"]).reset_index(drop=True)
    train_idx, test_idx = temporal_holdout_indices(
        frame["target_date"], int(cfg["validation"]["holdout_months"])
    )
    train = frame.iloc[train_idx].copy()
    test = frame.iloc[test_idx].copy()
    y_train = train["permit_value_t_plus_1"]
    y_test = test["permit_value_t_plus_1"]
    scales = seasonal_scales(train)

    prediction_parts = [
        pd.DataFrame(
            {
                "target_date": test["target_date"].values,
                "cma": test["cma"].values,
                "actual": y_test.values,
                "prediction": test["seasonal_naive_pred"].values,
                "model": "seasonal_naive",
            }
        )
    ]
    fitted: dict[str, Any] = {}
    search_summaries: dict[str, Any] = {}

    # RQ2 history-only versus macro-augmented elastic net.
    for label, include_macro in [("elastic_net_history", False), ("elastic_net_macro", True)]:
        numeric, categorical = _features(cfg, include_macro)
        features = numeric + categorical
        search, splits = _fit_grid(
            "elastic_net",
            train[features],
            y_train,
            train["target_date"],
            numeric,
            categorical,
            cfg,
        )
        pred = np.maximum(search.predict(test[features]), 0.0)
        prediction_parts.append(
            pd.DataFrame(
                {
                    "target_date": test["target_date"].values,
                    "cma": test["cma"].values,
                    "actual": y_test.values,
                    "prediction": pred,
                    "model": label,
                }
            )
        )
        fitted[label] = {"estimator": search.best_estimator_, "features": features}
        search_summaries[label] = {
            "best_params": search.best_params_,
            "best_cv_mae": float(-search.best_score_),
            "cv_splits": len(splits),
        }
        joblib.dump(search.best_estimator_, model_dir / f"{label}.joblib")

    # RQ3 model families use the macro-augmented feature set.
    numeric, categorical = _features(cfg, True)
    all_features = numeric + categorical
    for name in ["random_forest", "xgboost"]:
        search, splits = _fit_grid(
            name,
            train[all_features],
            y_train,
            train["target_date"],
            numeric,
            categorical,
            cfg,
        )
        pred = np.maximum(search.predict(test[all_features]), 0.0)
        prediction_parts.append(
            pd.DataFrame(
                {
                    "target_date": test["target_date"].values,
                    "cma": test["cma"].values,
                    "actual": y_test.values,
                    "prediction": pred,
                    "model": name,
                }
            )
        )
        fitted[name] = {"estimator": search.best_estimator_, "features": all_features}
        search_summaries[name] = {
            "best_params": search.best_params_,
            "best_cv_mae": float(-search.best_score_),
            "cv_splits": len(splits),
        }
        joblib.dump(search.best_estimator_, model_dir / f"{name}.joblib")

    predictions = pd.concat(prediction_parts, ignore_index=True)
    pred_path = table_dir / "holdout_predictions.csv"
    predictions.to_csv(pred_path, index=False)

    metric_rows = []
    for model, part in predictions.groupby("model"):
        metric_rows.append(metric_row(part["actual"], part["prediction"], part["cma"], scales, model))
    metrics = pd.DataFrame(metric_rows).sort_values(["mase", "mae"])
    metrics_path = table_dir / "rq3_model_metrics.csv"
    metrics.to_csv(metrics_path, index=False)

    regional = _regional_metrics(predictions, train)
    regional_path = table_dir / "rq4_regional_metrics.csv"
    regional.to_csv(regional_path, index=False)

    # RQ2: macro elastic net versus otherwise identical history-only elastic net.
    wide = predictions.pivot_table(
        index=["target_date", "cma", "actual"], columns="model", values="prediction"
    ).reset_index()
    rq2_tests = paired_error_tests(
        wide["actual"], wide["elastic_net_macro"], wide["elastic_net_history"]
    )
    rq2_tests["practical_threshold_pct"] = float(cfg["validation"]["practical_mae_improvement_pct"])
    rq2_tests["meets_practical_threshold"] = bool(
        rq2_tests["improvement_pct_a_vs_b"] >= rq2_tests["practical_threshold_pct"]
    )
    pd.DataFrame([rq2_tests]).to_csv(table_dir / "rq2_incremental_value.csv", index=False)

    # Pair every fitted model with the seasonal-naive benchmark.
    comparison_rows = []
    for model in [m for m in predictions["model"].unique() if m != "seasonal_naive"]:
        tests = paired_error_tests(wide["actual"], wide[model], wide["seasonal_naive"])
        tests["model_a"] = model
        tests["model_b"] = "seasonal_naive"
        comparison_rows.append(tests)
    pd.DataFrame(comparison_rows).to_csv(table_dir / "rq3_paired_error_tests.csv", index=False)

    # RQ4 omnibus test of absolute-error differences among regions for each model.
    anova_rows = []
    for model, part in predictions.groupby("model"):
        part = part.assign(abs_error=np.abs(part["actual"] - part["prediction"]))
        groups = [g["abs_error"].values for _, g in part.groupby("cma")]
        stat, p_value = stats.f_oneway(*groups)
        anova_rows.append({"model": model, "f_statistic": stat, "p_value": p_value, "n": len(part)})
    pd.DataFrame(anova_rows).to_csv(table_dir / "rq4_error_anova.csv", index=False)

    selection = _select_model(metrics, regional, cfg)
    selected = selection["selected_model"]
    if selected != "seasonal_naive":
        model_info = fitted[selected]
        selected_estimator = model_info["estimator"]
        selected_features = model_info["features"]
        _, point, lower, upper, radius = split_conformal_interval(
            selected_estimator,
            train[selected_features],
            y_train,
            train["target_date"],
            test[selected_features],
            alpha=float(cfg["validation"]["conformal_alpha"]),
            calibration_months=12,
        )
    else:
        point = test["seasonal_naive_pred"].to_numpy(dtype=float)
        train_resid = np.abs(
            train["permit_value_t_plus_1"].to_numpy(dtype=float)
            - train["seasonal_naive_pred"].to_numpy(dtype=float)
        )
        q = float(np.quantile(train_resid, 1 - float(cfg["validation"]["conformal_alpha"]), method="higher"))
        lower = np.maximum(point - q, 0.0)
        upper = point + q
        radius = q

    interval = pd.DataFrame(
        {
            "target_date": test["target_date"].values,
            "cma": test["cma"].values,
            "actual": y_test.values,
            "selected_model": selected,
            "prediction": point,
            "lower_90": lower,
            "upper_90": upper,
        }
    )
    interval["covered"] = (
        (interval["actual"] >= interval["lower_90"])
        & (interval["actual"] <= interval["upper_90"])
    )
    interval.to_csv(table_dir / "selected_model_intervals.csv", index=False)
    selection["conformal_radius"] = radius
    selection["holdout_interval_coverage"] = float(interval["covered"].mean())
    selection["train_target_months"] = int(train["target_date"].nunique())
    selection["holdout_target_months"] = int(test["target_date"].nunique())
    write_json(selection, table_dir / "model_selection.json")
    write_json(search_summaries, table_dir / "hyperparameter_search.json")

    split_manifest = {
        "train_start": train["target_date"].min(),
        "train_end": train["target_date"].max(),
        "test_start": test["target_date"].min(),
        "test_end": test["target_date"].max(),
        "train_rows": len(train),
        "test_rows": len(test),
        "train_months": train["target_date"].nunique(),
        "test_months": test["target_date"].nunique(),
    }
    write_json(split_manifest, table_dir / "temporal_split_manifest.json")

    return {
        "predictions": predictions,
        "metrics": metrics,
        "regional_metrics": regional,
        "selection": selection,
        "train": train,
        "test": test,
        "fitted": fitted,
    }
