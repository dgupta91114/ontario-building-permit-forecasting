"""Recheck frozen results and add report diagnostics without changing the official run."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestPower, FTestAnovaPower

from capstone.config import load_config, project_root
from capstone.metrics import metric_row, seasonal_scales
from capstone.sample_size import calculate_sample_sizes
from capstone.validation import temporal_holdout_indices, expanding_month_splits


def main():
    root = project_root()
    out = root / "reports/final/evidence"
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    tables = root / "outputs/tables"
    manifest = json.loads((root / "outputs/official_run_manifest.json").read_text())
    checks = []
    for rel, expected in manifest["sha256"].items():
        path = root / rel.replace("\\", "/")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"Frozen evidence changed: {rel}"
        checks.append({"path": rel.replace("\\", "/"), "sha256": actual, "matches": True})
    data = pd.read_csv(root / "data/processed/modeling_dataset.csv", parse_dates=["target_date", "ref_date"])
    data = data.sort_values(["target_date", "cma"]).reset_index(drop=True)
    tr, te = temporal_holdout_indices(data.target_date, 12)
    train, test = data.iloc[tr], data.iloc[te]
    scales = seasonal_scales(train)
    predictions = pd.read_csv(tables / "holdout_predictions.csv")
    official = pd.read_csv(tables / "rq3_model_metrics.csv").set_index("model")
    search = json.loads((tables / "hyperparameter_search.json").read_text())
    rows = []
    for name in official.index:
        recorded = predictions[predictions.model == name].copy()
        recomputed = metric_row(recorded.actual, recorded.prediction, recorded.cma, scales, name)
        for key in ["mae", "rmse", "mase", "smape_pct", "wape_pct"]:
            assert np.isclose(recomputed[key], official.loc[name, key], rtol=1e-10)
        if name == "seasonal_naive":
            train_pred = train.seasonal_naive_pred.to_numpy()
            cv_mae = np.mean([np.mean(np.abs(train.iloc[v].permit_value_t_plus_1 - train.iloc[v].seasonal_naive_pred))
                              for _, v in expanding_month_splits(train.target_date, 36, 12, 12)])
        else:
            estimator = joblib.load(root / f"outputs/models/{name}.joblib")
            features = list(cfg["features"]["primary_numeric_features"])
            if name != "elastic_net_history":
                features += list(cfg["features"]["macro_features"])
            features += list(cfg["features"]["categorical_features"])
            train_pred = np.maximum(estimator.predict(train[features]), 0)
            test_pred = np.maximum(estimator.predict(test[features]), 0)
            saved = recorded.sort_values(["target_date", "cma"]).prediction.to_numpy()
            assert np.allclose(test_pred, saved, rtol=1e-7, atol=.05), name
            cv_mae = search[name]["best_cv_mae"]
        fit = metric_row(train.permit_value_t_plus_1, train_pred, train.cma, scales, name)
        rows.append({"model": name, "train_n": len(train), "train_mae": fit["mae"],
                     "train_rmse": fit["rmse"], "cv_mae": float(cv_mae), "test_n": len(test),
                     "test_mae": recomputed["mae"], "test_rmse": recomputed["rmse"]})
    training = pd.DataFrame(rows)
    training.to_csv(out / "training_validation_test_metrics.csv", index=False)

    # Supplementary paired comparisons: reduce each calendar month to one pooled loss.
    # These do not pretend that twelve months establish asymptotic/independent inference.
    predictions["abs_error"] = np.abs(predictions.actual - predictions.prediction)
    monthly = predictions.groupby(["target_date", "model"]).abs_error.mean().unstack()
    monthly.to_csv(out / "monthly_pooled_absolute_errors.csv")
    supplemental = []
    for a, b in [("elastic_net_macro", "elastic_net_history"), ("xgboost", "seasonal_naive"), ("xgboost", "random_forest")]:
        d = (monthly[b] - monthly[a]).to_numpy()
        t, p = stats.ttest_1samp(d, 0)
        ci = stats.t.interval(.95, len(d)-1, loc=d.mean(), scale=stats.sem(d))
        supplemental.append({"model_a": a, "model_b": b, "unique_months": len(d),
                             "mean_mae_reduction": float(d.mean()), "t_statistic": float(t), "p_value": float(p),
                             "ci95_lower": float(ci[0]), "ci95_upper": float(ci[1]),
                             "positive_months": int((d > 0).sum())})
    pd.DataFrame(supplemental).to_csv(out / "supplementary_month_level_comparisons.csv", index=False)
    planned = calculate_sample_sizes()
    assert planned.minimum_n.tolist() == [85, 118, 67, 196]
    planned.to_csv(out / "verified_sample_size_calculations.csv", index=False)
    powers = {"paired_power_n60_d035": float(TTestPower().power(effect_size=.35, nobs=60, alpha=.05)),
              "anova_power_n60_f025_k5": float(FTestAnovaPower().power(effect_size=.25, nobs=60, alpha=.05, k_groups=5))}
    intervals = pd.read_csv(tables / "selected_model_intervals.csv")
    coverage = float(((intervals.actual >= intervals.lower_90) & (intervals.actual <= intervals.upper_90)).mean())
    assert coverage == 1.0
    interval_metrics = metric_row(intervals.actual, intervals.prediction, intervals.cma, scales, "xgboost_interval_fit")
    baseline = json.loads((root / "reports/submission_artifact_baseline.json").read_text())
    for item in baseline["files"]:
        assert hashlib.sha256((root / item["path"]).read_bytes()).hexdigest().lower() == item["sha256"].lower()
    audit = {"verified_on": "2026-09-13", "frozen_artifacts": checks, "official_metrics_recomputed": True,
             "saved_model_predictions_match": True, "prior_submission_artifacts_unchanged": True,
             "train_rows": len(train), "holdout_rows": len(test), "unique_holdout_months": 12,
             "power_under_independence_assumption": powers, "interval_fit_metrics": interval_metrics,
             "interval_coverage": coverage, "supplementary_status": "Report diagnostics; no retuning or replacement of frozen results"}
    (out / "evidence_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (out / "cleaning_audit.json").write_bytes((root / "data/interim/cleaning_audit.json").read_bytes())

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.facecolor": "white"})
    colors = ["#1b4965", "#347d8f", "#7b6a9e", "#ae6b31", "#777777"]
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set(xlim=(0, 10), ylim=(0, 10)); ax.axis("off")
    def box(x, y, w, h, title, detail, dashed=False):
        ax.add_patch(FancyBboxPatch((x,y), w,h, boxstyle="round,pad=.10", facecolor="#edf3f7" if not dashed else "#fff6e8",
                                   edgecolor="#1b4965" if not dashed else "#9b632a", linewidth=1.3, linestyle="--" if dashed else "-"))
        ax.text(x+w/2, y+h*.72, title, ha="center", va="center", weight="bold", fontsize=11)
        ax.text(x+w/2, y+h*.32, detail, ha="center", va="center", fontsize=9.2)
    def arrow(a,b): ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>", mutation_scale=14,color="#1b4965",linewidth=1.3))
    box(.4,8.6,9.2,1.0,"Official public inputs", "Statistics Canada: permits + Ontario unemployment | Bank of Canada: V39079")
    box(.4,7.05,9.2,1.0,"Freeze, filter, and validate", "Archive hashes → dimension filters → monthly joins → quality flags")
    box(.4,5.5,9.2,1.0,"Exploratory analysis and feature construction", "Within-CMA lags + rolling history + calendar + macro lags | 440 CMA-months")
    arrow((5,8.5),(5,8.12)); arrow((5,6.95),(5,6.57)); arrow((5,5.4),(5,5.13))
    box(.4,3.7,4.3,1.3,"Point-model branch", "380 pre-holdout rows\nThree chronological tuning folds\nRefit → 60-row holdout comparison")
    box(5.3,3.7,4.3,1.3,"Interval branch", "320 proper-fit + 60 calibration rows\nSeparate XGBoost fit\nPredict point and bounds together")
    arrow((5,5.1),(2.55,5.08)); arrow((5,5.1),(7.45,5.08))
    box(.4,1.9,9.2,1.1,"Evidence and decision support", "Benchmark gate | Regional errors | SHAP + permutation | CSV tables + report")
    arrow((2.55,3.58),(2.55,3.1)); arrow((7.45,3.58),(7.45,3.1))
    box(.4,.25,9.2,1.0,"Proposed operational pilot", "Release-date checks → analyst scorecard → prospective monitoring", dashed=True)
    arrow((5,1.8),(5,1.35))
    fig.tight_layout(); fig.savefig(out / "architecture.png", dpi=240); fig.savefig(out / "architecture.svg"); plt.close(fig)
    svg=out / "architecture.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")

    labels = {"xgboost":"XGBoost", "random_forest":"Random forest", "elastic_net_macro":"Elastic net + macro",
              "elastic_net_history":"Elastic net history", "seasonal_naive":"Seasonal naive"}
    fig, axes = plt.subplots(1,2,figsize=(9,4.1))
    frame = official.reset_index()
    for ax, metric, label in [(axes[0],"mae","MAE (CAD millions)"),(axes[1],"mase","MASE")]:
        values = frame[metric] / (1000 if metric=="mae" else 1)
        ax.barh([labels[x] for x in frame.model], values, color=colors)
        ax.invert_yaxis(); ax.set_xlabel(label); ax.grid(axis="x",alpha=.15)
        ax.set_xlim(0, max(values)*1.2)
        for i,v in enumerate(values): ax.text(v+max(values)*.015,i,f"{v:.3f}",va="center",fontsize=9)
    fig.tight_layout(); fig.savefig(out / "model_comparison.png",dpi=220); plt.close(fig)

    fig, axes = plt.subplots(5,1,figsize=(8.5,6.2),sharex=True)
    for ax,(cma,part),color in zip(axes, data.groupby("cma"),colors):
        ax.plot(part.ref_date,part.permit_value_t/1000,color=color,linewidth=1)
        ax.set_ylabel(cma.replace("Kitchener-Cambridge-Waterloo","KCW"),rotation=0,ha="right",va="center",fontsize=9)
        ax.grid(alpha=.2); ax.tick_params(axis="y",labelsize=8)
    axes[0].set_title("Observed permit history by CMA (CAD millions; separate vertical scales)",fontsize=11)
    fig.tight_layout(); fig.savefig(out / "regional_history.png",dpi=220); plt.close(fig)

    perm = pd.read_csv(tables / "rq4_permutation_importance.csv").head(7).iloc[::-1]
    shap = pd.read_csv(tables / "rq4_shap_importance.csv")
    fig, ax = plt.subplots(figsize=(8.5,3.4))
    ax.barh(perm.feature,perm.mae_increase_mean/1000,color="#1b4965")
    ax.set_xlabel("Increase in holdout MAE after permutation (CAD millions)")
    ax.grid(axis="x",alpha=.2); fig.tight_layout(); fig.savefig(out / "permutation.png",dpi=220); plt.close(fig)
    top=shap.head(7).iloc[::-1]
    fig, ax=plt.subplots(figsize=(8.5,3.0))
    ax.barh(top.transformed_feature,top.mean_absolute_shap,color="#347d8f")
    ax.set_xlabel("Mean absolute SHAP contribution (log1p-target units)")
    ax.grid(axis="x",alpha=.2); fig.tight_layout(); fig.savefig(out / "shap_importance.png",dpi=220); plt.close(fig)
    point=predictions[predictions.model=="xgboost"].copy()
    point["target_date"]=pd.to_datetime(point.target_date)
    fig, axes=plt.subplots(5,1,figsize=(8.5,7.0),sharex=True)
    for ax,(region,part) in zip(axes,point.groupby("cma")):
        ax.plot(part.target_date,part.actual/1000,"o-",color="#1b4965",markersize=3,label="Observed")
        ax.plot(part.target_date,part.prediction/1000,"s--",color="#b56e28",markersize=3,label="XGBoost")
        ax.set_ylabel(region.replace("Kitchener-Cambridge-Waterloo","KCW"),rotation=0,ha="right",va="center",fontsize=10)
        ax.grid(alpha=.2); ax.tick_params(axis="y",labelsize=9)
    axes[0].legend(loc="upper right",fontsize=9,ncol=2)
    axes[0].set_title("Holdout point forecasts (CAD millions; separate vertical scales)",fontsize=11)
    import matplotlib.dates as mdates
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2)); axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout(); fig.savefig(out / "holdout_forecasts.png",dpi=220); plt.close(fig)
    print(json.dumps({"audit": audit, "training": rows, "month_level": supplemental, "shap_columns":list(shap.columns)}, indent=2))


if __name__ == "__main__":
    main()
