# JudgeBERT-Indic-Tenancy-Labor-Consumer
### Explainable Multilingual Legal Meaning Preservation Using JUDGEBERT (PJ_08)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow.svg)](https://huggingface.co/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-ff4b4b.svg)](https://streamlit.io/)

---

## 📌 Project Overview
**CSET 346 – Natural Language Processing | Project PJ_08**  
**Team Members:**  
- **Eshaan Mishra** (S24CSEU0795) - Batch 52  
- **Fairy Tyagi** (S24CSEU0794) - Batch 52  
- **Ansh Dixit** (S24CSEU1018) - Batch 52  
- **Anvi Tyagi** (S24CSEU1026) - Batch 52  

**Instructor:** Dr. Surabhi Solanki  
**Reference Paper:** Beauchemin, D., Albert-Rochette, M., Khoury, R., & Déziel, P. L. (2025, November). *JUDGEBERT: Assessing Legal Meaning Preservation Between Sentences*. In *Proceedings of EMNLP 2025* (pp. 92–118).

---

## 🎯 Problem Statement & Motivation
Legal text simplification aims to make complex legal provisions intelligible to the public without corrupting legal obligations, rights, or conditions.

Generic semantic similarity metrics (BLEU, ROUGE, SBERT) notoriously fail on legal texts because substituting a single modal verb (e.g., *"shall"* $\to$ *"may"*), dropping an exception (e.g., *"unless otherwise agreed"*), or altering an operative date produces high surface/embedding similarity while drastically subverting legal enforceability.

This project extends the **JUDGEBERT** cross-encoder regression paradigm from French property-damage insurance contracts to a **multilingual (English + Hindi)** framework across **Tenancy Law**, **Employment, Labor & Contract Law**, and **Consumer Protection Law**, accompanied by an **explainable diagnostic engine**.

---

## 🔬 Core Architecture
```
[CLS] S_orig [SEP] S_simp [SEP] ---> Transformer Backbone (Cross-Attention)
                                                 |
                                            [CLS] Token
                                                 |
                                    Dense Projection + GELU
                                                 |
                 +-------------------------------+--------------------+
                 |                               |                    |
          Regression Head                 Decision Head          Error Head
       1.0 + 9.0 * Sigmoid(w^T h)        Softmax(W_c h)         Softmax(W_e)
           LMP: [1.0, 10.0]              3-Way Decision           9 Classes
```

1. **Joint Cross-Attention:** The cross-encoder reads both sentences simultaneously, detecting absent conditions and modality flips that bi-encoders average out.
2. **Bounded Scaled Sigmoid:** Guarantees continuous predictions are strictly bounded within the valid human LMP scale $[1.0, 10.0]$.
3. **Multi-Task Objective:** Jointly optimizes Huber regression loss and categorical cross-entropy for 3-way preservation decisions and error identification.
4. **Explainability Engine:** Identifies specific token-level legal perturbations (duty shifts, negation reversals, date discrepancies, entity swaps).

---

## 📁 Repository Structure
```
JudgeBERT-Indic-Tenancy-Labor-Consumer/
├── data/
│   ├── annotation_guidelines.md       # Formal LMP scoring rubric & taxonomy
│   ├── full_dataset.csv               # 2,695 multi-domain pairs (Tenancy, Labor, Consumer)
│   ├── train.csv / val.csv / test.csv # Stratified splits (2,013 / 330 / 352)
│   └── sanity_checks.csv              # 40 Identical and Unrelated anchor pairs
├── src/
│   ├── build_multidomain_corpus.py    # Multi-domain statutory dataset builder
│   ├── hindi_legal_enhancement.py     # Hindi deontic, exception & labor enhancements
│   ├── baselines.py                   # BLEU, ROUGE-L, Levenshtein, TF-IDF, SBERT
│   ├── model.py                       # JUDGEBERT + Devanagari Phonetic Layer + Mean/CLS Pool
│   ├── train.py                       # GPU fine-tuning loop (consistency + 1.5x Hindi boost)
│   ├── evaluate.py                    # Pearson r, Spearman rho, RMSE, MAE, Macro-F1
│   └── explainability.py              # Rule-guided legal feature attribution engine
├── experiments/
│   ├── run_all_experiments.py         # Automated runner for Experiments 1 through 5
│   └── results/                       # Verified empirical JSON results & CSV reports
├── demo/
│   └── app.py                         # Interactive Streamlit dashboard
├── paper/
│   ├── IEEE_Research_Paper.md         # Comprehensive IEEE-style research paper
│   └── generate_docs.py               # Generates Word (.docx) and PDF deliverables
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
```bash
pip install torch transformers sentence-transformers scikit-learn pandas numpy streamlit
```

### 2. Build the Multi-Domain Corpus ($N=2,695$)
```bash
python src/build_multidomain_corpus.py
```

### 3. Run GPU Training and All 5 Experiments
```bash
python experiments/run_all_experiments.py
```

### 4. Launch the Interactive Web Dashboard
```bash
streamlit run demo/app.py
```

---

## 📊 Summary of Empirical Results (Held-Out Test Set, $N=352$)

### Experiment 1: Generic Baselines vs. JUDGEBERT
| Model | Pearson $r$ $\uparrow$ | Spearman $\rho$ $\uparrow$ | RMSE $\downarrow$ | MAE $\downarrow$ | Decision Accuracy $\uparrow$ | Macro F1 $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BLEU** | 0.1163 | 0.2798 | 4.6914 | 3.6280 | 44.32% | 0.3792 |
| **ROUGE-L** | 0.1528 | 0.3166 | 4.1143 | 3.2714 | 38.07% | 0.3591 |
| **Generic SBERT Cosine** | 0.2850 | 0.3189 | 4.2048 | 3.2696 | 40.06% | 0.2978 |
| **JUDGEBERT (Ours - Overall)** | **0.7436** | **0.7424** | **2.4810** | **1.3072** | **78.98%** | **0.7367** |

#### Domain Breakdown (JUDGEBERT)
- **Consumer Protection ($N=125$):** Pearson **$r = 0.8673$** | Accuracy = **$88.00\%$** | Macro-F1 = **$0.8358$**
- **Tenancy Law ($N=133$):** Pearson **$r = 0.7284$** | Accuracy = **$75.94\%$** | Macro-F1 = **$0.7151$**
- **Employment, Labor & Contracts ($N=94$):** Pearson **$r = 0.6153$** | Accuracy = **$71.28\%$** | Macro-F1 = **$0.6250$**

### Experiment 2: Multilingual Generalization
- **English ($N=213$):** Pearson **$r = 0.7901$** | Spearman **$\rho = 0.7908$** | Accuracy = **$80.75\%$** | MAE = **$1.14$**
- **Hindi ($N=139$):** Pearson **$r = 0.6817$** | Spearman **$\rho = 0.6573$** | Accuracy = **$76.26\%$** | MAE = **$1.56$** *(vs. $0.3910$ before phonetic Devanagari normalization)*

### Experiment 3: Out-of-Domain Generalization (Tenancy $\to$ Consumer Law)
- **Zero-Shot Transfer Pearson $r = 0.2149$** (Accuracy = $35.28\%$), proving multi-statutory training is critical compared to in-domain **$r = 0.8673$**.

### Experiment 4: Sanity Check Robustness
- **Identical Pairs ($10.0$ expected):** JUDGEBERT predicts **$9.63 \pm 0.02$** across English & Hindi clauses
- **Unrelated Pairs ($1.0$ expected):** JUDGEBERT predicts **$2.99 \pm 2.56$**, whereas generic SBERT erroneously predicts **$5.62 \pm 2.46$**.

### Experiment 5: Qualitative Case Studies
- Evaluates 16 adversarial statutory traps across all 9 legal error modes (*duty vs. permission, dates/numbers, exceptions, omissions, conditions, entities, contradiction, scope, hallucination*) across English and Hindi.
