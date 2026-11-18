"""
Evaluation Metrics Suite for Legal Meaning Preservation (LMP)
Supports:
- Pearson correlation (r)
- Spearman rank correlation (rho)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- 3-Way Classification Metrics: Accuracy, Precision, Recall, Macro F1
- Stratified reporting by Language and Legal Domain
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_squared_error, mean_absolute_error, classification_report, accuracy_score, f1_score

def score_to_decision(score):
    """Maps continuous LMP score (1-10) to 3-way categorical decision."""
    if score >= 8.0:
        return "Preserved"
    elif score >= 4.0:
        return "Partially Preserved"
    else:
        return "Not Preserved"

def compute_regression_metrics(y_true, y_pred):
    """Computes Pearson r, Spearman rho, RMSE, and MAE."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    
    # Clip predictions to valid 1-10 scale
    y_pred_clipped = np.clip(y_pred, 1.0, 10.0)
    
    # Pearson
    if np.std(y_true) == 0 or np.std(y_pred_clipped) == 0:
        pearson_val = 0.0
    else:
        pearson_val, _ = pearsonr(y_true, y_pred_clipped)
        
    # Spearman
    if np.std(y_true) == 0 or np.std(y_pred_clipped) == 0:
        spearman_val = 0.0
    else:
        spearman_val, _ = spearmanr(y_true, y_pred_clipped)
        
    rmse_val = np.sqrt(mean_squared_error(y_true, y_pred_clipped))
    mae_val = mean_absolute_error(y_true, y_pred_clipped)
    
    return {
        "pearson_r": float(pearson_val),
        "spearman_rho": float(spearman_val),
        "rmse": float(rmse_val),
        "mae": float(mae_val)
    }

def compute_classification_metrics(y_true_decision, y_pred_decision):
    """Computes Accuracy, Macro F1, and per-class metrics for 3-way decision."""
    labels = ["Not Preserved", "Partially Preserved", "Preserved"]
    acc = accuracy_score(y_true_decision, y_pred_decision)
    macro_f1 = f1_score(y_true_decision, y_pred_decision, labels=labels, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true_decision, y_pred_decision, labels=labels, average="weighted", zero_division=0)
    report = classification_report(y_true_decision, y_pred_decision, labels=labels, output_dict=True, zero_division=0)
    
    return {
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "classification_report": report
    }

def evaluate_predictions(df_results, pred_score_col="pred_score"):
    """
    Evaluates a dataframe containing true 'lmp_score' and predicted score column.
    Produces overall metrics as well as breakdowns by language and domain.
    """
    df = df_results.copy()
    if "pred_decision" not in df.columns:
        df["pred_decision"] = df[pred_score_col].apply(score_to_decision)
        
    y_true = df["lmp_score"].tolist()
    y_pred = df[pred_score_col].tolist()
    y_true_dec = df["decision"].tolist()
    y_pred_dec = df["pred_decision"].tolist()
    
    reg_metrics = compute_regression_metrics(y_true, y_pred)
    cls_metrics = compute_classification_metrics(y_true_dec, y_pred_dec)
    
    overall = {**reg_metrics, **cls_metrics}
    
    # By Language
    by_lang = {}
    for lang, group in df.groupby("language"):
        reg = compute_regression_metrics(group["lmp_score"], group[pred_score_col])
        cls = compute_classification_metrics(group["decision"], group["pred_decision"])
        by_lang[lang] = {**reg, **cls}
        
    # By Domain
    by_domain = {}
    for dom, group in df.groupby("domain"):
        reg = compute_regression_metrics(group["lmp_score"], group[pred_score_col])
        cls = compute_classification_metrics(group["decision"], group["pred_decision"])
        by_domain[dom] = {**reg, **cls}
        
    return {
        "overall": overall,
        "by_language": by_lang,
        "by_domain": by_domain
    }
