from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _xgb_regressor(random_state: int):
    from xgboost import XGBRegressor

    return XGBRegressor(
        objective="reg:squarederror",
        random_state=random_state,
        n_jobs=1,
        tree_method="hist",
        eval_metric="mae",
    )


def make_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, numeric_features),
            ("categorical", categorical, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def make_model(
    name: str,
    numeric_features: list[str],
    categorical_features: list[str],
    random_state: int,
):
    preprocessor = make_preprocessor(numeric_features, categorical_features)
    if name == "elastic_net":
        estimator = ElasticNet(max_iter=10000, tol=1e-4, selection="cyclic")
    elif name == "random_forest":
        estimator = RandomForestRegressor(random_state=random_state, n_jobs=1)
    elif name == "xgboost":
        estimator = _xgb_regressor(random_state)
    else:
        raise ValueError(f"Unknown model: {name}")

    pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
    return TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def parameter_grid(name: str, cfg: dict[str, Any]) -> dict[str, list[Any]]:
    if name == "elastic_net":
        model_cfg = cfg["models"]["elastic_net"]
        return {
            "regressor__model__alpha": model_cfg["alpha"],
            "regressor__model__l1_ratio": model_cfg["l1_ratio"],
        }
    if name == "random_forest":
        model_cfg = cfg["models"]["random_forest"]
        return {
            "regressor__model__n_estimators": model_cfg["n_estimators"],
            "regressor__model__max_depth": model_cfg["max_depth"],
            "regressor__model__min_samples_leaf": model_cfg["min_samples_leaf"],
            "regressor__model__max_features": model_cfg["max_features"],
        }
    if name == "xgboost":
        model_cfg = cfg["models"]["xgboost"]
        return {
            "regressor__model__n_estimators": model_cfg["n_estimators"],
            "regressor__model__max_depth": model_cfg["max_depth"],
            "regressor__model__learning_rate": model_cfg["learning_rate"],
            "regressor__model__subsample": model_cfg["subsample"],
            "regressor__model__colsample_bytree": model_cfg["colsample_bytree"],
        }
    raise ValueError(f"Unknown model: {name}")
