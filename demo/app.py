"""
Interactive Streamlit Dashboard for PJ_08:
Multilingual Legal Meaning Preservation (LMP) using JUDGEBERT
"""

import os
os.environ["USE_TF"] = "0"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import streamlit as st
import pandas as pd
import numpy as np

from src.model import JudgeBertPredictor
from src.baselines import BaselineEvaluator
from src.explainability import analyze_legal_discrepancy

st.set_page_config(
    page_title="JUDGEBERT | Legal Meaning Preservation",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Multilingual Legal Meaning Preservation Using JUDGEBERT")
st.markdown("""
**Course:** CSET 346 – Natural Language Processing | **Project:** PJ_08  
**Team Members:** Eshaan Mishra (S24CSEU0795), Fairy Tyagi (S24CSEU0794), Ansh Dixit (S24CSEU1018), Anvi Tyagi (S24CSEU1026)  
**Instructor:** Dr. Surabhi Solanki  
*Extending JUDGEBERT (EMNLP 2025) to English and Hindi Legal Simplification Evaluation.*
""")

@st.cache_resource
def load_system():
    base_model = "sentence-transformers/all-MiniLM-L6-v2"
    model_path = "models/best_judgebert.pt"
    if not os.path.exists(model_path):
        model_path = None
    predictor = JudgeBertPredictor(model_path=model_path, base_model_name=base_model)
    baseline_eval = BaselineEvaluator(sbert_model_name=base_model)
    return predictor, baseline_eval

try:
    predictor, baseline_eval = load_system()
    model_ready = True
except Exception as e:
    model_ready = False
    st.error(f"Error initializing models: {e}")

tabs = st.tabs(["🔍 Interactive Pair Evaluator", "📊 Experiment 1: Baselines vs JUDGEBERT", "🌐 Experiment 2: Multilingual (EN vs HI)", "🏛️ Experiment 3: Out-of-Domain Generalization", "🛡️ Experiment 4: Sanity Checks", "📑 Experiment 5: Qualitative Error Analysis"])

PRESET_EXAMPLES = {
    "English: Duty vs Permission (shall -> may)": {
        "orig": "The tenant shall pay rent by the fifth of every month, unless otherwise agreed in writing.",
        "simp": "The tenant may pay rent around the fifth of every month.",
        "lang": "en",
        "domain": "tenancy"
    },
    "English: Exception Lost (unless dropped)": {
        "orig": "The tenant shall not keep domestic pets on the premises without obtaining prior written authorization from the landlord.",
        "simp": "The tenant is strictly forbidden from keeping any pets inside the rental property.",
        "lang": "en",
        "domain": "tenancy"
    },
    "English: Dates & Numbers Distortion (30 days -> 3 months)": {
        "orig": "The landlord shall return the security deposit within thirty days following formal handover of keys.",
        "simp": "The landlord must refund the deposit within three months after receiving the keys.",
        "lang": "en",
        "domain": "tenancy"
    },
    "English: Consumer Law Entity Swap": {
        "orig": "The manufacturer shall be strictly liable in a product liability action for harm caused to a consumer by a defective product.",
        "simp": "The consumer is strictly liable for any harm caused by defects in the purchased product.",
        "lang": "en",
        "domain": "consumer_protection"
    },
    "Hindi: Obligation Dilution (करेगा -> चाहे तो)": {
        "orig": "किरायेदार प्रत्येक अंग्रेजी कैलेंडर माह की पांचवीं तारीख तक निर्धारित बैंक खाते में मासिक किराये का भुगतान करेगा।",
        "simplified": "किरायेदार चाहे तो महीने की 5 तारीख के आसपास किराया दे सकता है।",
        "lang": "hi",
        "domain": "tenancy"
    },
    "Hindi: Consumer Law False Claim Contradiction": {
        "orig": "अनुचित व्यापार व्यवहार तथा भ्रामक विज्ञापनों पर रोक लगाना केंद्रीय उपभोक्ता संरक्षण प्राधिकरण का वैधानिक दायित्व है।",
        "simplified": "कंपनियों को उपभोक्ताओं को लुभाने के लिए झूठे और भ्रामक विज्ञापन देने की पूरी आजादी है।",
        "lang": "hi",
        "domain": "consumer_protection"
    },
    "Hindi: Labor Law Bonus Obligation Preserved (Valid Simplification)": {
        "orig": "प्रत्येक नियोजक प्रत्येक लेखा वर्ष के संबंध में प्रत्येक कर्मचारी को न्यूनतम बोनस का संदाय करेगा जो कर्मचारी द्वारा उस लेखा वर्ष के दौरान अर्जित वेतन या मजदूरी का 8.33 प्रतिशत होगा।",
        "simp": "मालिक को हर साल हर पात्र कर्मचारी को सालाना वेतन का कम से कम 8.33 प्रतिशत न्यूनतम बोनस के रूप में अनिवार्य रूप से देना होगा।",
        "lang": "hi",
        "domain": "employment_labor"
    },
    "English: Labor Law Gratuity Entity Swap (Employer -> Employee)": {
        "orig": "The employer shall arrange to pay the amount of gratuity within thirty days from the date it becomes payable to the person to whom the gratuity is payable.",
        "simp": "Employees are required to pay gratuity to the employer within 30 days of resigning.",
        "lang": "en",
        "domain": "employment_labor"
    },
    "Sanity: Identical Pair (Verbatim Match)": {
        "orig": "The Lessee covenants to keep the exterior walls, roof, and structural foundations in sound repair.",
        "simp": "The Lessee covenants to keep the exterior walls, roof, and structural foundations in sound repair.",
        "lang": "en",
        "domain": "tenancy"
    }
}

with tabs[0]:
    st.subheader("Evaluate an Original–Simplified Legal Sentence Pair")
    
    preset_choice = st.selectbox("Load a Curated Benchmark Case:", ["-- Custom Input --"] + list(PRESET_EXAMPLES.keys()))
    
    default_orig = ""
    default_simp = ""
    default_lang = "en"
    
    if preset_choice != "-- Custom Input --":
        selected = PRESET_EXAMPLES[preset_choice]
        default_orig = selected["orig"]
        default_simp = selected.get("simp", selected.get("simplified", ""))
        default_lang = selected["lang"]
        
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        orig_text = st.text_area("Original Legal Sentence (Source):", value=default_orig, height=120)
    with col_in2:
        simp_text = st.text_area("Simplified / Reformulated Sentence (Target):", value=default_simp, height=120)
        
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        lang = st.selectbox("Language:", ["en", "hi"], index=0 if default_lang == "en" else 1, format_func=lambda x: "English (en)" if x == "en" else "Hindi (hi)")
    with col_opt2:
        evaluate_btn = st.button("Evaluate Legal Meaning Preservation", type="primary", use_container_width=True)
        
    if evaluate_btn and orig_text.strip() and simp_text.strip():
        # Predictions
        jb_res = predictor.predict_pair(orig_text, simp_text)
        diag = analyze_legal_discrepancy(orig_text, simp_text, lang=lang)
        
        # Baselines
        df_single = pd.DataFrame([{"id": "DEMO-01", "original": orig_text, "simplified": simp_text}])
        sbert_score = baseline_eval.run_sbert_baseline(df_single)["sbert_lmp_pred"].iloc[0]
        lex_res = baseline_eval.run_lexical_baselines(df_single).iloc[0]
        
        st.divider()
        st.markdown("### 🏆 Prediction & Evaluation Summary")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("JUDGEBERT LMP Score", f"{jb_res['lmp_score']:.1f} / 10.0")
        
        dec_color = "🟢" if jb_res["decision"] == "Preserved" else ("🟡" if jb_res["decision"] == "Partially Preserved" else "🔴")
        c2.metric("Legal Decision", f"{dec_color} {jb_res['decision']}")
        
        c3.metric("Generic SBERT Baseline", f"{sbert_score:.1f} / 10.0")
        c4.metric("BLEU / ROUGE-L", f"{lex_res['bleu_lmp_pred']:.1f} | {lex_res['rouge_l_lmp_pred']:.1f}")
        
        st.markdown("---")
        st.subheader("🔬 Explainability & Legal Failure Diagnostic")
        
        col_exp1, col_exp2 = st.columns([1, 1])
        with col_exp1:
            st.info(f"**Primary Legal Error Category:** `{diag['error_category']}`")
            st.write(f"**Legal Rationale:** {diag['explanation']}")
            if diag["key_differences"]:
                st.write("**Identified Discrepancies:**")
                for diff in diag["key_differences"]:
                    st.markdown(f"- {diff}")
                    
        with col_exp2:
            st.warning("**Why Generic Semantic Similarity (SBERT) Fails Here:**")
            if sbert_score >= 6.5 and jb_res["lmp_score"] < 4.0:
                st.markdown("""
                > **Notice the Critical Divergence:**  
                > Generic SBERT yields an inflated semantic score because 90%+ of the vocabulary is identical.  
                > However, a vital operative shift (e.g., *shall $\to$ may*, dropped condition, or date change) occurred.  
                > **JUDGEBERT's cross-encoder cross-attention** correctly penalizes the clause, preserving legal enforceability!
                """)
            else:
                st.markdown("Scores are aligned; legal meaning is either faithfully preserved or completely different across surface tokens.")

with tabs[1]:
    st.subheader("Experiment 1: Generic Baselines vs. JUDGEBERT-based LMP Prediction")
    if os.path.exists("experiments/results/exp1_baselines_vs_judgebert.json"):
        with open("experiments/results/exp1_baselines_vs_judgebert.json", encoding="utf-8") as f:
            e1 = json.load(f)
        overall_data = e1.get("overall", e1)
        df_e1 = pd.DataFrame(overall_data).T
        cols = ["pearson_r", "spearman_rho", "rmse", "mae", "accuracy", "macro_f1"]
        st.dataframe(df_e1[cols].style.highlight_max(subset=["pearson_r", "spearman_rho", "accuracy", "macro_f1"], color="#bbf7d0").highlight_min(subset=["rmse", "mae"], color="#bbf7d0"))
        if "by_domain" in e1:
            st.markdown("#### Stratified Domain Breakdown (JUDGEBERT)")
            df_dom = pd.DataFrame(e1["by_domain"]).T
            st.dataframe(df_dom[cols].style.highlight_max(subset=["pearson_r", "spearman_rho", "accuracy", "macro_f1"], color="#bbf7d0"))
    else:
        st.info("Run `python experiments/run_all_experiments.py` to populate live experiment tables.")

with tabs[2]:
    st.subheader("Experiment 2: Cross-Lingual Evaluation (English vs. Hindi)")
    if os.path.exists("experiments/results/exp2_multilingual_en_hi.json"):
        with open("experiments/results/exp2_multilingual_en_hi.json", encoding="utf-8") as f:
            e2 = json.load(f)
        df_e2 = pd.DataFrame(e2).T
        st.dataframe(df_e2[["pearson_r", "spearman_rho", "rmse", "mae", "accuracy", "macro_f1"]])
    else:
        st.info("Live data will appear here upon completion of Experiment 2.")

with tabs[3]:
    st.subheader("Experiment 3: Out-of-Domain Generalization (Tenancy -> Consumer Law)")
    if os.path.exists("experiments/results/exp3_domain_generalization.json"):
        with open("experiments/results/exp3_domain_generalization.json", encoding="utf-8") as f:
            e3 = json.load(f)
        st.json(e3)
    else:
        st.info("Live data will appear here upon completion of Experiment 3.")

with tabs[4]:
    st.subheader("Experiment 4: Sanity Checks on Identical & Unrelated Sentence Pairs")
    if os.path.exists("experiments/results/exp4_sanity_checks.json"):
        with open("experiments/results/exp4_sanity_checks.json", encoding="utf-8") as f:
            e4 = json.load(f)
        st.json(e4)
    else:
        st.info("Live data will appear here upon completion of Experiment 4.")

with tabs[5]:
    st.subheader("Experiment 5: Qualitative Error Analysis of 16 Legally Difficult Cases")
    if os.path.exists("experiments/results/exp5_error_analysis_15cases.csv"):
        df_e5 = pd.read_csv("experiments/results/exp5_error_analysis_15cases.csv", encoding="utf-8")
        st.dataframe(df_e5[["case_id", "language", "error_category", "ground_truth_lmp", "sbert_score", "judgebert_score", "judgebert_decision", "explanation"]])
    else:
        st.info("Live data will appear here upon completion of Experiment 5.")
