"""
Comprehensive Experiment Suite for Project PJ_08:
Explainable Multilingual Legal Meaning Preservation Using JUDGEBERT

Runs and saves results for:
- Experiment 1: Generic Semantic Baselines vs. JUDGEBERT
- Experiment 2: Cross-Lingual Evaluation (English vs. Hindi)
- Experiment 3: Out-of-Domain Generalization (Tenancy -> Consumer Protection)
- Experiment 4: Sanity Checks (Identical vs. Unrelated Pairs)
- Experiment 5: Qualitative Error Analysis of 15+ Legally Difficult Cases
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

from src.baselines import BaselineEvaluator
from src.model import MultilingualJudgeBert, JudgeBertPredictor, DECISION_MAP, ERROR_MAP
from src.evaluate import evaluate_predictions, compute_regression_metrics, compute_classification_metrics
from src.explainability import analyze_legal_discrepancy
from src.train import train_model

def run_experiment_1(test_df, predictor, baselines_df):
    """
    Experiment 1: Generic Baselines vs. JUDGEBERT-based LMP Prediction.
    """
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT 1: Generic Baselines vs. JUDGEBERT LMP Prediction")
    print("="*70)
    
    # 1. Evaluate Lexical & Generic SBERT Baselines
    merged = test_df.merge(baselines_df, on="id")
    
    results = {}
    
    # BLEU
    res_bleu = evaluate_predictions(merged, pred_score_col="bleu_lmp_pred")
    results["BLEU"] = res_bleu["overall"]
    
    # ROUGE-L
    res_rouge = evaluate_predictions(merged, pred_score_col="rouge_l_lmp_pred")
    results["ROUGE-L"] = res_rouge["overall"]
    
    # Levenshtein
    res_lev = evaluate_predictions(merged, pred_score_col="levenshtein_lmp_pred")
    results["Levenshtein"] = res_lev["overall"]
    
    # TF-IDF
    res_tfidf = evaluate_predictions(merged, pred_score_col="tfidf_lmp_pred")
    results["TF-IDF_Cosine"] = res_tfidf["overall"]
    
    # SBERT Bi-encoder
    res_sbert = evaluate_predictions(merged, pred_score_col="sbert_lmp_pred")
    results["SBERT_Cosine"] = res_sbert["overall"]
    
    # 2. Evaluate JUDGEBERT
    judgebert_df = predictor.predict_df(test_df)
    judgebert_df["pred_decision"] = judgebert_df["judgebert_pred_decision"]
    res_judgebert = evaluate_predictions(judgebert_df, pred_score_col="judgebert_pred_score")
    results["JUDGEBERT"] = res_judgebert["overall"]
    
    # Print formatted summary table
    print(f"\n{'Metric':<20} | {'Pearson r':<10} | {'Spearman rho':<12} | {'RMSE':<8} | {'MAE':<8} | {'Accuracy':<8} | {'Macro F1':<8}")
    print("-" * 88)
    for model_name, m in results.items():
        print(f"{model_name:<20} | {m['pearson_r']:<10.4f} | {m['spearman_rho']:<12.4f} | {m['rmse']:<8.4f} | {m['mae']:<8.4f} | {m['accuracy']:<8.4f} | {m['macro_f1']:<8.4f}")
        
    print("\n" + "="*70)
    print("STRATIFIED EVALUATION BY LEGAL DOMAIN (JUDGEBERT)")
    print("="*70)
    by_dom = res_judgebert.get("by_domain", {})
    for dom_name, m in by_dom.items():
        print(f"Domain: {dom_name.upper():<22} | Pearson r: {m['pearson_r']:<8.4f} | Spearman: {m['spearman_rho']:<8.4f} | RMSE: {m['rmse']:<8.4f} | Accuracy: {m['accuracy']:<8.4f}")

    os.makedirs("experiments/results", exist_ok=True)
    results_payload = {
        "overall": results,
        "by_domain": by_dom,
        "by_language": res_judgebert.get("by_language", {})
    }
    with open("experiments/results/exp1_baselines_vs_judgebert.json", "w") as f:
        json.dump(results_payload, f, indent=2)
        
    return results, judgebert_df

def run_experiment_2(judgebert_df):
    """
    Experiment 2: Cross-Lingual Evaluation (English vs. Hindi).
    """
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT 2: English vs. Hindi Cross-Lingual Performance")
    print("="*70)
    
    eval_res = evaluate_predictions(judgebert_df, pred_score_col="judgebert_pred_score")
    by_lang = eval_res["by_language"]
    
    print(f"\n{'Language':<12} | {'Pearson r':<10} | {'Spearman rho':<12} | {'RMSE':<8} | {'MAE':<8} | {'Accuracy':<8} | {'Macro F1':<8}")
    print("-" * 80)
    for lang, m in by_lang.items():
        lang_label = "English (en)" if lang == "en" else "Hindi (hi)"
        print(f"{lang_label:<12} | {m['pearson_r']:<10.4f} | {m['spearman_rho']:<12.4f} | {m['rmse']:<8.4f} | {m['mae']:<8.4f} | {m['accuracy']:<8.4f} | {m['macro_f1']:<8.4f}")
        
    with open("experiments/results/exp2_multilingual_en_hi.json", "w") as f:
        json.dump(by_lang, f, indent=2)
        
    return by_lang

def run_experiment_3(df_all, base_model):
    """
    Experiment 3: Out-of-Domain Generalization.
    Train purely on Tenancy Law -> Test on Consumer Protection Law.
    """
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT 3: Out-of-Domain Generalization (Tenancy -> Consumer)")
    print("="*70)
    
    train_tenancy = df_all[df_all["domain"] == "tenancy"].reset_index(drop=True)
    test_consumer = df_all[df_all["domain"] == "consumer_protection"].reset_index(drop=True)
    
    os.makedirs("experiments/scratch", exist_ok=True)
    train_tenancy.to_csv("experiments/scratch/train_tenancy.csv", index=False)
    test_consumer.to_csv("experiments/scratch/test_consumer.csv", index=False)
    
    # Train OOD model
    ood_model_path = train_model(
        train_path="experiments/scratch/train_tenancy.csv",
        val_path="experiments/scratch/test_consumer.csv",
        output_dir="models/ood_tenancy",
        base_model=base_model,
        epochs=3,
        batch_size=16
    )
    
    ood_predictor = JudgeBertPredictor(model_path=ood_model_path, base_model_name=base_model)
    ood_preds = ood_predictor.predict_df(test_consumer)
    ood_preds["pred_decision"] = ood_preds["judgebert_pred_decision"]
    ood_res = evaluate_predictions(ood_preds, pred_score_col="judgebert_pred_score")
    
    print("\nOut-of-Domain Evaluation Results (Zero-Shot Consumer Law Transfer):")
    m = ood_res["overall"]
    print(f"Pearson r: {m['pearson_r']:.4f} | Spearman rho: {m['spearman_rho']:.4f} | RMSE: {m['rmse']:.4f} | Accuracy: {m['accuracy']:.4f} | Macro F1: {m['macro_f1']:.4f}")
    
    with open("experiments/results/exp3_domain_generalization.json", "w") as f:
        json.dump(ood_res["overall"], f, indent=2)
        
    return ood_res["overall"]

def run_experiment_4(predictor, baseline_eval):
    """
    Experiment 4: Sanity Checks on Identical and Unrelated Sentence Pairs.
    """
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT 4: Sanity Checks (Identical & Unrelated Pairs)")
    print("="*70)
    
    sanity_df = pd.read_csv("data/sanity_checks.csv")
    
    # SBERT predictions
    sbert_res = baseline_eval.run_sbert_baseline(sanity_df)
    sanity_df["sbert_lmp_pred"] = sbert_res["sbert_lmp_pred"]
    
    # JUDGEBERT predictions
    jb_preds = predictor.predict_df(sanity_df)
    sanity_df["judgebert_pred_score"] = jb_preds["judgebert_pred_score"]
    
    identical_pairs = sanity_df[sanity_df["sanity_type"] == "identical"]
    unrelated_pairs = sanity_df[sanity_df["sanity_type"] == "unrelated"]
    
    sanity_summary = {
        "identical": {
            "ground_truth": 10.0,
            "judgebert_mean": float(identical_pairs["judgebert_pred_score"].mean()),
            "judgebert_std": float(identical_pairs["judgebert_pred_score"].std()),
            "sbert_mean": float(identical_pairs["sbert_lmp_pred"].mean()),
            "sbert_std": float(identical_pairs["sbert_lmp_pred"].std())
        },
        "unrelated": {
            "ground_truth": 1.0,
            "judgebert_mean": float(unrelated_pairs["judgebert_pred_score"].mean()),
            "judgebert_std": float(unrelated_pairs["judgebert_pred_score"].std()),
            "sbert_mean": float(unrelated_pairs["sbert_lmp_pred"].mean()),
            "sbert_std": float(unrelated_pairs["sbert_lmp_pred"].std())
        }
    }
    
    print("\nSanity Check Results:")
    print(f"Identical Pairs (Expected = 10.0):")
    print(f"  JUDGEBERT Predicted Mean: {sanity_summary['identical']['judgebert_mean']:.2f} +/- {sanity_summary['identical']['judgebert_std']:.2f}")
    print(f"  SBERT Predicted Mean:     {sanity_summary['identical']['sbert_mean']:.2f} +/- {sanity_summary['identical']['sbert_std']:.2f}")
    
    print(f"\nUnrelated Pairs (Expected = 1.0):")
    print(f"  JUDGEBERT Predicted Mean: {sanity_summary['unrelated']['judgebert_mean']:.2f} +/- {sanity_summary['unrelated']['judgebert_std']:.2f}")
    print(f"  SBERT Predicted Mean:     {sanity_summary['unrelated']['sbert_mean']:.2f} +/- {sanity_summary['unrelated']['sbert_std']:.2f}")
    
    with open("experiments/results/exp4_sanity_checks.json", "w") as f:
        json.dump(sanity_summary, f, indent=2)
        
    return sanity_summary

def run_experiment_5(df_all, predictor, baseline_eval):
    """
    Experiment 5: Qualitative Error Analysis for 15+ Legally Difficult Cases.
    Examines failure modes across all 9 error types and compares SBERT vs. JUDGEBERT.
    """
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT 5: Qualitative Error Analysis (16 Hard Cases)")
    print("="*70)
    
    # Sample at least 15 diverse hard cases across error categories and both languages
    cases = []
    
    categories = [
        "duty_vs_permission", "date_number", "entity", "contradiction",
        "condition", "exception", "omission", "scope", "hallucination"
    ]
    
    for cat in categories:
        sub_en = df_all[(df_all["error_category"] == cat) & (df_all["language"] == "en")]
        if not sub_en.empty:
            cases.append(sub_en.iloc[0].to_dict())
            
        sub_hi = df_all[(df_all["error_category"] == cat) & (df_all["language"] == "hi")]
        if not sub_hi.empty:
            cases.append(sub_hi.iloc[0].to_dict())
            
    # Keep first 16 representative cases
    cases = cases[:16]
    cases_df = pd.DataFrame(cases)
    
    # Compute baseline SBERT scores
    sbert_res = baseline_eval.run_sbert_baseline(cases_df)
    cases_df["sbert_score"] = sbert_res["sbert_lmp_pred"].round(2)
    
    # Compute JUDGEBERT scores
    jb_res = predictor.predict_df(cases_df)
    cases_df["judgebert_score"] = jb_res["judgebert_pred_score"]
    cases_df["judgebert_decision"] = jb_res["judgebert_pred_decision"]
    
    # Add explainability diagnostics
    qualitative_records = []
    for idx, row in cases_df.iterrows():
        diag = analyze_legal_discrepancy(row["original"], row["simplified"], lang=row["language"])
        record = {
            "case_id": f"CASE-{idx+1:02d}",
            "language": row["language"],
            "domain": row["domain"],
            "error_category": row["error_category"],
            "original": row["original"],
            "simplified": row["simplified"],
            "ground_truth_lmp": row["lmp_score"],
            "sbert_score": row["sbert_score"],
            "judgebert_score": row["judgebert_score"],
            "judgebert_decision": row["judgebert_decision"],
            "explanation": diag["explanation"],
            "why_baseline_fails": (
                "Generic SBERT observes high lexical/semantic embedding cosine similarity and awards an inflated score, "
                f"completely blind to the legal subversion in {row['error_category']}."
                if row["sbert_score"] > 6.0 and row["lmp_score"] < 4.0 else
                "Moderate surface similarity mask."
            )
        }
        qualitative_records.append(record)
        
    print(f"\nCompleted qualitative analysis for {len(qualitative_records)} challenging legal cases.")
    
    # Print sample comparison
    print(f"\n{'ID':<8} | {'Lang':<5} | {'Category':<18} | {'True LMP':<8} | {'SBERT':<8} | {'JUDGEBERT':<10}")
    print("-" * 65)
    for r in qualitative_records[:8]:
        print(f"{r['case_id']:<8} | {r['language']:<5} | {r['error_category']:<18} | {r['ground_truth_lmp']:<8.1f} | {r['sbert_score']:<8.2f} | {r['judgebert_score']:<10.2f}")
        
    with open("experiments/results/exp5_error_analysis_15cases.json", "w", encoding="utf-8") as f:
        json.dump(qualitative_records, f, indent=2, ensure_ascii=False)
        
    # Also save as readable CSV
    pd.DataFrame(qualitative_records).to_csv("experiments/results/exp5_error_analysis_15cases.csv", index=False, encoding="utf-8")
    
    return qualitative_records

def main():
    base_model = "sentence-transformers/all-MiniLM-L6-v2"
    
    print("Starting Comprehensive Experiment Execution...")
    
    # 1. Train Enhanced Multilingual JUDGEBERT Model
    print("Step 1: Training Enhanced Multilingual JUDGEBERT...")
    best_model_path = train_model(
        train_path="data/train.csv",
        val_path="data/val.csv",
        output_dir="models",
        base_model=base_model,
        epochs=8,
        batch_size=16,
        lr=2.5e-5
    )
    
    # 2. Initialize Predictor & Baseline Evaluator
    predictor = JudgeBertPredictor(model_path=best_model_path, base_model_name=base_model)
    baseline_eval = BaselineEvaluator(sbert_model_name=base_model)
    
    test_df = pd.read_csv("data/test.csv")
    full_df = pd.read_csv("data/full_dataset.csv")
    
    # 3. Compute Baselines on Test Set
    print("\nComputing Lexical and Semantic Baselines on Test Set...")
    lexical_df = baseline_eval.run_lexical_baselines(test_df)
    sbert_df = baseline_eval.run_sbert_baseline(test_df)
    tfidf_df = baseline_eval.run_tfidf_baseline(test_df)
    
    baselines_df = lexical_df.merge(sbert_df, on="id").merge(tfidf_df, on="id")
    
    # 4. Run Experiment 1
    exp1_res, judgebert_df = run_experiment_1(test_df, predictor, baselines_df)
    
    # 5. Run Experiment 2
    exp2_res = run_experiment_2(judgebert_df)
    
    # 6. Run Experiment 3
    exp3_res = run_experiment_3(full_df, base_model)
    
    # 7. Run Experiment 4
    exp4_res = run_experiment_4(predictor, baseline_eval)
    
    # 8. Run Experiment 5
    exp5_res = run_experiment_5(full_df, predictor, baseline_eval)
    
    print("\n" + "="*70)
    print("ALL 5 EXPERIMENTS COMPLETED SUCCESSFULLY!")
    print("Results and artifacts saved to experiments/results/")
    print("="*70)

if __name__ == "__main__":
    main()
