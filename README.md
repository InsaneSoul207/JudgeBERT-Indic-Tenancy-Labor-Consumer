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
Projects/
├── data/
│   ├── annotation_guidelines.md       # Formal LMP scoring rubric & taxonomy
│   ├── build_dataset.py               # Dataset generation & stratification script
│   ├── full_dataset.csv               # 340 curated legal sentence pairs
│   ├── train.csv / val.csv / test.csv # Stratified splits (70/15/15)
│   └── sanity_checks.csv              # 40 Identical and Unrelated anchor pairs
├── src/
│   ├── baselines.py                   # BLEU, ROUGE-L, Levenshtein, TF-IDF, SBERT
│   ├── model.py                       # Multilingual JUDGEBERT PyTorch module
│   ├── train.py                       # Fine-tuning loop with multi-task loss
│   ├── evaluate.py                    # Pearson r, Spearman rho, RMSE, MAE, F1
│   └── explainability.py              # Rule-guided legal feature attribution engine
├── experiments/
│   ├── run_all_experiments.py         # Automated runner for Experiments 1 through 5
│   └── results/                       # Empirical JSON results and CSV reports
├── demo/
│   └── app.py                         # Interactive Streamlit dashboard
├── paper/
│   └── IEEE_Research_Paper.md         # Comprehensive IEEE-style research paper
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
```bash
pip install torch transformers sentence-transformers scikit-learn pandas numpy streamlit
```

### 2. Generate Dataset
```bash
python data/build_dataset.py
```

### 3. Run Training and All 5 Experiments
```bash
python experiments/run_all_experiments.py
```

### 4. Launch the Interactive Web Dashboard
```bash
streamlit run demo/app.py
```

---

## 📊 Summary of Experimental Results

### Experiment 1: Generic Baselines vs. JUDGEBERT
| Model | Pearson $r$ $\uparrow$ | Spearman $\rho$ $\uparrow$ | RMSE $\downarrow$ | Decision Accuracy $\uparrow$ | Macro F1 $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **BLEU** | 0.2814 | 0.2541 | 3.6821 | 45.61% | 0.3812 |
| **ROUGE-L** | 0.3120 | 0.2985 | 3.5140 | 49.12% | 0.4105 |
| **Generic SBERT Cosine** | 0.2642 | 0.2315 | 3.8410 | 43.86% | 0.3520 |
| **JUDGEBERT (Ours)** | **0.8654** | **0.8412** | **1.7215** | **89.47%** | **0.8715** |

### Experiment 2: Multilingual Generalization
- **English ($r = 0.8812$, Acc = $90.0\%$)**
- **Hindi ($r = 0.8480$, Acc = $88.9\%$)**

### Experiment 3: Out-of-Domain Generalization (Tenancy $\to$ Consumer Law)
- **Zero-Shot Transfer Pearson $r = 0.8145$**, proving domain-invariant learning of legal modification patterns.

### Experiment 4: Sanity Check Robustness
- **Identical Pairs ($10.0$ expected):** JUDGEBERT predicts **$9.94 \pm 0.08$**
- **Unrelated Pairs ($1.0$ expected):** JUDGEBERT predicts **$1.12 \pm 0.15$**, whereas generic SBERT erroneously predicts **$4.85 \pm 0.92$**.

### Experiment 5: Qualitative Case Studies
- Analyzes 16 hard legal cases across all 9 failure categories (*duty vs. permission, dates/numbers, exceptions, omissions, conditions, entities, contradiction, scope, hallucination*), detailing exact legal enforceability impacts.
