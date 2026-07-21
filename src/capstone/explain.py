from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

from .config import project_root
from .utils import write_json


def _unwrap_model(estimator):
    # Fitted TransformedTargetRegressor -> fitted Pipeline -> preprocessor/model.
    pipeline = estimator.regressor_
    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    return preprocessor, model


def explain_selected_model(
    data: pd.DataFrame,
    cfg: dict[str, Any],
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or project_root()
    tables = base / "outputs" / "tables"
    figures = base / "outputs" / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    selection = json.loads((tables / "model_selection.json").read_text(encoding="utf-8"))
    selected = selection["selected_model"]
    if selected == "seasonal_naive":
        note = {
            "selected_model": selected,
            "explanation": "Seasonal naive has no fitted feature-attribution model. Driver analysis remains descriptive (RQ1).",
        }
        write_json(note, tables / "rq4_explainability_note.json")
        return note

    model_path = base / "outputs" / "models" / f"{selected}.joblib"
    estimator = joblib.load(model_path)
    data = data.copy()
    data["target_date"] = pd.to_datetime(data["target_date"])
    holdout_months = int(cfg["validation"]["holdout_months"])
    unique = sorted(data["target_date"].unique())
    test_dates = set(unique[-holdout_months:])
    test = data[data["target_date"].isin(test_dates)].copy()

    numeric = list(cfg["features"]["primary_numeric_features"]) + list(cfg["features"]["macro_features"])
    categorical = list(cfg["features"]["categorical_features"])
    features = numeric + categorical
    X = test[features]
    y = test["permit_value_t_plus_1"]

    perm = permutation_importance(
        estimator,
        X,
        y,
        scoring="neg_mean_absolute_error",
        n_repeats=30,
        random_state=int(cfg["project"]["random_seed"]),
        n_jobs=1,
    )
    permutation = pd.DataFrame(
        {
            "feature": features,
            "mae_increase_mean": perm.importances_mean,
            "mae_increase_sd": perm.importances_std,
        }
    ).sort_values("mae_increase_mean", ascending=False)
    permutation.to_csv(tables / "rq4_permutation_importance.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    top = permutation.head(15).sort_values("mae_increase_mean")
    ax.barh(top["feature"], top["mae_increase_mean"], xerr=top["mae_increase_sd"])
    ax.set_title(f"Permutation Importance — {selected}")
    ax.set_xlabel("Increase in holdout MAE after permutation")
    fig.tight_layout()
    perm_path = figures / "rq4_permutation_importance.png"
    fig.savefig(perm_path, dpi=200)
    plt.close(fig)

    shap_status: dict[str, Any] = {"attempted": True, "success": False}
    try:
        import shap

        preprocessor, inner_model = _unwrap_model(estimator)
        transformed = preprocessor.transform(X)
        names = list(preprocessor.get_feature_names_out())
        background = transformed[: min(100, len(transformed))]
        explain_rows = transformed[: min(250, len(transformed))]
        if selected in {"random_forest", "xgboost"}:
            explainer = shap.TreeExplainer(inner_model)
        else:
            explainer = shap.LinearExplainer(inner_model, background)
        shap_values = explainer(explain_rows)
        values = np.asarray(shap_values.values)
        if values.ndim == 3:
            values = values[..., 0]
        importance = pd.DataFrame(
            {"transformed_feature": names, "mean_absolute_shap": np.abs(values).mean(axis=0)}
        ).sort_values("mean_absolute_shap", ascending=False)
        importance.to_csv(tables / "rq4_shap_importance.csv", index=False)

        shap.plots.beeswarm(shap_values, max_display=15, show=False)
        plt.tight_layout()
        shap_path = figures / "rq4_shap_beeswarm.png"
        plt.savefig(shap_path, dpi=200, bbox_inches="tight")
        plt.close()
        shap_status = {
            "attempted": True,
            "success": True,
            "explanation_scale": "log1p target model scale; ranking is used for global interpretation",
            "figure": str(shap_path.relative_to(base)),
        }
    except Exception as exc:  # SHAP is optional; preserve the auditable permutation fallback.
        shap_status = {"attempted": True, "success": False, "error": repr(exc)}

    write_json(
        {
            "selected_model": selected,
            "permutation_figure": str(perm_path.relative_to(base)),
            "shap": shap_status,
        },
        tables / "rq4_explainability_status.json",
    )
    return {"selected_model": selected, "permutation": permutation, "shap": shap_status}
