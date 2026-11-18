"""
Dedicated Tenancy-Only Pipeline:
Trains and evaluates Multilingual JUDGEBERT solely on the Tenancy Domain (319 pairs).
"""

import os
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import torch
import pandas as pd
import numpy as np

from src.train import train_model
from src.model import JudgeBertPredictor
from src.baselines import BaselineEvaluator
from src.evaluate import evaluate_predictions

def run_tenancy_benchmark():
    base_model = "sentence-transformers/all-MiniLM-L6-v2"
    output_dir = "models/tenancy_only"
    
    print("="*70)
    print("TRAINING MULTILINGUAL JUDGEBERT ON EXPANDED TENANCY CORPUS (1,015 PAIRS)")
    print("="*70)
    
    model_path = train_model(
        train_path="data/tenancy_train.csv",
        val_path="data/tenancy_val.csv",
        output_dir=output_dir,
        base_model=base_model,
        epochs=8,
        batch_size=8,
        lr=3e-5
    )
    
    predictor = JudgeBertPredictor(model_path=model_path, base_model_name=base_model)
    baseline_eval = BaselineEvaluator(sbert_model_name=base_model)
    
    test_df = pd.read_csv("data/tenancy_test.csv")
    print(f"\nEvaluating on Expanded Tenancy Test Set ({len(test_df)} pairs)...")
    
    # Baselines
    sbert_res = baseline_eval.run_sbert_baseline(test_df)
    lex_res = baseline_eval.run_lexical_baselines(test_df)
    
    merged = test_df.merge(sbert_res, on="id").merge(lex_res, on="id")
    
    # Evaluate baselines
    m_sbert = evaluate_predictions(merged, pred_score_col="sbert_lmp_pred")["overall"]
    m_bleu = evaluate_predictions(merged, pred_score_col="bleu_lmp_pred")["overall"]
    m_rouge = evaluate_predictions(merged, pred_score_col="rouge_l_lmp_pred")["overall"]
    
    # Evaluate JUDGEBERT
    jb_df = predictor.predict_df(test_df)
    jb_df["pred_decision"] = jb_df["judgebert_pred_decision"]
    eval_jb = evaluate_predictions(jb_df, pred_score_col="judgebert_pred_score")
    m_jb = eval_jb["overall"]
    m_jb_lang = eval_jb["by_language"]
    
    print("\n" + "="*80)
    print("TENANCY DOMAIN BENCHMARK RESULTS (SOTA EVALUATION)")
    print("="*80)
    print(f"{'Model':<24} | {'Pearson r':<10} | {'Spearman rho':<12} | {'RMSE':<8} | {'MAE':<8} | {'Accuracy':<8} | {'Macro-F1':<8}")
    print("-" * 88)
    print(f"{'BLEU':<24} | {m_bleu['pearson_r']:<10.4f} | {m_bleu['spearman_rho']:<12.4f} | {m_bleu['rmse']:<8.4f} | {m_bleu['mae']:<8.4f} | {m_bleu['accuracy']:<8.4f} | {m_bleu['macro_f1']:<8.4f}")
    print(f"{'ROUGE-L':<24} | {m_rouge['pearson_r']:<10.4f} | {m_rouge['spearman_rho']:<12.4f} | {m_rouge['rmse']:<8.4f} | {m_rouge['mae']:<8.4f} | {m_rouge['accuracy']:<8.4f} | {m_rouge['macro_f1']:<8.4f}")
    print(f"{'Generic SBERT':<24} | {m_sbert['pearson_r']:<10.4f} | {m_sbert['spearman_rho']:<12.4f} | {m_sbert['rmse']:<8.4f} | {m_sbert['mae']:<8.4f} | {m_sbert['accuracy']:<8.4f} | {m_sbert['macro_f1']:<8.4f}")
    print(f"{'JUDGEBERT (Tenancy-SOTA)':<24} | {m_jb['pearson_r']:<10.4f} | {m_jb['spearman_rho']:<12.4f} | {m_jb['rmse']:<8.4f} | {m_jb['mae']:<8.4f} | {m_jb['accuracy']:<8.4f} | {m_jb['macro_f1']:<8.4f}")
    
    print("\nBreakdown by Language (Tenancy Domain):")
    for lang, stats in m_jb_lang.items():
        print(f"  {lang.upper()}: Pearson r = {stats['pearson_r']:.4f} | Spearman rho = {stats['spearman_rho']:.4f} | RMSE = {stats['rmse']:.4f} | Accuracy = {stats['accuracy']:.4f} | Macro-F1 = {stats['macro_f1']:.4f}")
        
    results_payload = {
        "overall": {
            "BLEU": m_bleu,
            "ROUGE-L": m_rouge,
            "SBERT": m_sbert,
            "JUDGEBERT_Tenancy": m_jb
        },
        "by_language": m_jb_lang,
        "test_dataset_size": len(test_df),
        "train_dataset_size": len(pd.read_csv("data/tenancy_train.csv"))
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/tenancy_only_results.json", "w") as f:
        json.dump(results_payload, f, indent=2)
        
    print("\nResults successfully saved to experiments/results/tenancy_only_results.json")

if __name__ == "__main__":
    run_tenancy_benchmark()
