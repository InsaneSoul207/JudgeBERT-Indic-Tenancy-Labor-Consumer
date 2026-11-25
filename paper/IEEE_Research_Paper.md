# Explainable Multilingual Legal Meaning Preservation Using Cross-Encoder Transformers

**Eshaan Mishra** (`S24CSEU0795`), **Fairy Tyagi** (`S24CSEU0794`), **Ansh Dixit** (`S24CSEU1018`), **Anvi Tyagi** (`S24CSEU1026`)  
*Batch 52 — Department of Computer Science and Engineering, Bennett University, Greater Noida, India*  
`{eshaan.mishra, fairy.tyagi, ansh.dixit, anvi.tyagi}@bennett.edu.in`  
*Course:* `CSET 346 – Natural Language Processing` | *Project ID:* `PJ_08` | *Instructor:* Dr. Surabhi Solanki (`surabhi.solanki@bennett.edu.in`)

---

## Abstract

Legal text simplification aims to make dense statutory and contractual clauses intelligible to citizens while strictly preserving legal duties, rights, deadlines, and exceptions. Conventional evaluation metrics such as BLEU, ROUGE-L, and bi-encoder embeddings (e.g., Sentence-BERT) rely on surface lexical overlap or pooled vector similarity, causing them to fail when subtle lexical edits reverse legal liability—for example, diluting mandatory *deontic modals* (`"shall"` to `"may"`), omitting exclusionary caveats (`"unless otherwise agreed"`), or distorting statutory limitation periods. In this project (`PJ_08`), we extend the foundational French property-insurance **JUDGEBERT** framework (*Beauchemin et al., EMNLP 2025*) to a multilingual (English and Hindi) and multi-statutory Indian legal setting covering **Tenancy Law**, **Consumer Protection Law**, and **Employment, Labor & Contract Law**. We construct a balanced benchmark corpus of **2,695 statutory sentence pairs** (1,651 English; 1,044 Hindi) spanning ten annotation categories (nine failure modes plus preserved semantics). We architect a 22.87M-parameter multi-task cross-encoder built atop `all-MiniLM-L6-v2` with hybrid `[CLS]` and attention-masked mean pooling, scaled sigmoid regression (`[1.0, 10.0]`), ordinal decision and error-type heads calibrated via dual-head consistency constraints, and a lossless phonetic Devanagari-to-Latin transducer that eliminates WordPiece `[UNK]` token collapse (`92.4%` to `0.0%` Hindi test pairs) without changing the backbone architecture. On the held-out multi-domain test set ($N = 352$), generic SBERT reaches only Pearson $r = 0.2850$ and $40.06\%$ decision accuracy ($0.67\%$ recall on *Not Preserved*), whereas our GPU fine-tuned JUDGEBERT achieves **$r = 0.7436$**, Spearman **$\rho = 0.7424$**, RMSE **$2.4810$**, MAE **$1.3072$**, **$78.98\%$ accuracy**, and **$0.7367$ Macro-F1**—attaining **$r = 0.8673$** ($88.00\%$ accuracy) on Consumer Law, **$r = 0.7901$** on English clauses, and **$r = 0.6817$** ($+0.2907$ over our initial baseline) on Hindi statutes. Finally, zero-shot out-of-domain transfer collapses to $r = 0.2149$ ($35.28\%$ accuracy), demonstrating empirically that diverse multi-domain statutory training is indispensable for reliable legal NLP evaluation.

**Index Terms**—Legal Meaning Preservation, JUDGEBERT, Cross-Encoder, Multilingual Legal NLP, Hindi Devanagari Transliteration, Text Simplification, Indian Statutory Law, Explainable AI.

---

## I. Introduction

Statutory provisions, residential lease deeds, consumer e-commerce policies, and employment contracts rely on formal legal drafting characterized by nested conditionals, cross-referenced exceptions, and archaic phrasing. Although legal text simplification can broaden access to justice across linguistically diverse populations, deploying automated simplification systems without reliable meaning-preservation auditing introduces acute legal risk: a minor phrasing change can transform an enforceable statutory duty into a non-binding suggestion or reverse financial liability.

Standard NLP similarity measures fail systematically on this task. Surface overlap metrics (BLEU, ROUGE-L, Levenshtein) penalize valid paraphrasing while ignoring small polarity inversions, and generic bi-encoder sentence embeddings (e.g., Sentence-BERT) compress entire clauses into independent fixed vectors before taking a cosine product. Consider the illustrative tenancy clause:

- **Original:** *"The tenant shall pay rent by the 5th of every month, unless otherwise agreed in writing."*
- **Simplified:** *"The tenant may pay rent around the 5th of every month."*

Because lexical overlap (`"tenant"`, `"pay"`, `"rent"`, `"5th"`, `"month"`) remains high, generic SBERT assigns a high similarity score ($>0.85$), falsely suggesting semantic equivalence. From a legal standpoint, three critical breaches have occurred simultaneously: (1) a mandatory statutory obligation (`"shall"`) was downgraded into optional discretion (`"may"`); (2) an enforceable payment deadline (`"by the 5th"`) was weakened to an indeterminate window (`"around the 5th"`); and (3) a written contractual exception (`"unless otherwise agreed in writing"`) was deleted altogether.

To address these shortcomings, Beauchemin et al. [1] formalized **Legal Meaning Preservation (LMP)** and introduced **JUDGEBERT** on `FrJUDGE`, a corpus of 297 French sentence pairs derived from property-damage insurance contracts. However, the original study highlighted three open research gaps: (i) restriction to a single language (French) and single domain (property insurance), (ii) small dataset scale without out-of-domain generalization analysis, and (iii) lack of interpretable diagnostic explanations specifying *which* legal mechanism broke.

### Project Objectives and Contributions

Directly addressing the `CSET 346 (PJ_08)` project requirements and the open gaps identified by Beauchemin et al. [1], this work makes five contributions:

1. **Multilingual Multi-Statutory Corpus ($N = 2,695$ pairs):** We construct an annotated benchmark across **English** ($1,651$ pairs, $61.3\%$) and **Hindi Devanagari** ($1,044$ pairs, $38.7\%$)—more than **$9\times$ the size of FrJUDGE**—spanning three Indian statutory regimes: **Tenancy Law** ($1,031$ pairs), **Consumer Protection Law** ($958$ pairs), and **Employment, Labor & Contract Law** ($706$ pairs).
2. **Fine-Grained Legal Error Taxonomy:** Every sentence pair is annotated with a continuous `1.0–10.0` LMP score, an ordinal 3-way preservation decision (*Not Preserved*, *Partially Preserved*, *Preserved*), and a 10-class diagnostic label covering nine statutory failure modes (*Omission, Hallucination, Contradiction, Duty vs. Permission, Conditions, Exceptions, Scope, Dates & Numbers, Entities*) plus preserved pairs.
3. **Phonetic Devanagari Normalization & Multi-Task Cross-Encoder:** Retaining the compact 22.87M-parameter `all-MiniLM-L6-v2` cross-encoder backbone, we engineer a deterministic lossless Devanagari-to-Latin phonetic transducer reducing Hindi test `[UNK]` pairs from **$92.4\%$ ($145/157$) down to $0.0\%$ ($0/157$)**, paired with hybrid `[CLS]`+mean pooling, tempered class weighting, dual-head ordinal consistency loss, and $1.5\times$ Hindi gradient weighting.
4. **Neuro-Symbolic Bilingual Explainability Engine & Dashboard:** Alongside predicted scores and classes, a deterministic bilingual diagnostic module flags altered numbers, negated obligations, deontic modal weakening, omitted caveats, and entity swaps across English and Hindi in an interactive 6-tab Streamlit evaluation suite.
5. **Six-Experiment Empirical Suite:** We rigorously evaluate baseline failure, English vs. Hindi cross-lingual equity, `v1` vs. `v2` architectural ablations, zero-shot out-of-domain collapse (`Tenancy -> Consumer`), identical/unrelated sanity checks, single-domain corpus scaling (`319 -> 1,015`), and qualitative error diagnostics across **16 legally adversarial cases**.

---

## II. Related Work

### A. Generic Evaluation vs. Semantic Equivalence in Law

Lexical evaluation metrics such as sentence-level BLEU [4] and ROUGE-L [5] measure n-gram precision and longest common subsequence overlap; in simplification, structural rewriting rightly lowers n-gram identity even when statutory meaning is intact. SARI tracks word additions, deletions, and retentions against references, while BERTScore and MeaningBERT [6] leverage contextualized embeddings for general-domain adequacy. Bi-encoder architectures such as Sentence-BERT (SBERT) [2] and multilingual dual encoders (LaBSE, MuRIL [7]) produce isolated sentence vectors suited to semantic search, yet pooled cosine similarity lacks token-level alignment across conditional subordinate clauses, negations, and numerical thresholds. Legal-domain encoders including LEGAL-BERT [3] and multilingual transformers such as XLM-RoBERTa [8] provide specialized representations, though end-to-end supervised pairwise interaction remains essential to verify normative equivalence.

### B. The JUDGEBERT Cross-Encoder Paradigm

Beauchemin et al. [1] framed LMP assessment as supervised cross-attention regression over sentence pairs `[CLS] S_orig [SEP] S_simp [SEP]`, enabling every token of the simplified text to attend directly to every statutory token in the original sentence across all transformer layers. While their `RoBERTa-large` (355M parameters) model achieved $r \approx 0.65$ on 297 French insurance clauses, its single-language, single-domain scope and heavyweight parameter count motivated our investigation into compact (22.87M), multilingual, explainable cross-encoders across Indian statutory law.

---

## III. LMP Problem Formulation & Dataset Engineering

### A. Mathematical Formulation

Given an authoritative legal provision $S_{orig}$ and a candidate plain-language rewrite $S_{simp}$, JUDGEBERT learns a joint prediction tuple:

$$f_{\text{LMP}}(S_{orig}, S_{simp}) \rightarrow \left(\hat{y}_{\text{LMP}} \in [1.0, 10.0],\; \hat{y}_{\text{dec}} \in \mathcal{Y},\; \hat{y}_{\text{err}} \in \mathcal{E}\right)$$

where $\hat{y}_{\text{LMP}}$ estimates fidelity to the source legal provision and the categorical preservation decision maps continuous scores into three enforceable regimes:

- **Not Preserved (`0`):** $y_{\text{LMP}} \in [1.0, 4.0)$ — critical legal duty inverted, contradiction introduced, key parties swapped, or statutory deadline falsified.
- **Partially Preserved (`1`):** $y_{\text{LMP}} \in [4.0, 8.0)$ — core obligation retained, yet non-trivial procedural detail, minor exception, or clarificatory qualifier omitted or narrowed.
- **Preserved (`2`):** $y_{\text{LMP}} \in [8.0, 10.0]$ — faithful plain-language simplification retaining all enforceable rights, duties, actors, numbers, and conditions.

### B. Nine Statutory Failure Modes (`ERROR_MAP`)

To support diagnostic attribution alongside scalar scoring, invalid simplifications are categorized into nine distinct failure types (with index `0: none` denoting valid preservation, creating a 10-class auxiliary objective):

1. **`omission` (1):** Deletion of operative covenants, liability caps, or procedural remedies.
2. **`hallucination` (2):** Insertion of fabricated penalties, eviction grounds, fees, or deadlines absent from $S_{orig}$.
3. **`contradiction` (3):** Direct semantic inversion (`"shall not"` changed to `"may"` or `"is permitted"`).
4. **`duty_vs_permission` (4):** Weakening mandatory compliance (`"shall"` / `"अनिवार्य"` changed to `"may"` / `"चाहे तो"`).
5. **`condition` (5):** Dropping or distorting conditional triggers (`"provided that"`, `"if notified within..."`).
6. **`exception` (6):** Omitting statutory carve-outs (`"unless"`, `"except"`, `"सिवाय"`).
7. **`scope` (7):** Unlawfully expanding or narrowing statutory applicability (`"all establishments"` vs. `"only hazardous factories"`).
8. **`date_number` (8):** Altering monetary fines, notice periods, or age/tenure thresholds (`"15 days"` to `"6 months"`).
9. **`entity` (9):** Swapping legal roles and bearer of liability (`"Landlord"` $\leftrightarrow$ `"Tenant"`, `"Employer"` $\leftrightarrow$ `"Employee"`).

### C. Multilingual Multi-Statutory Corpus Composition

The unified dataset integrates bilingual provisions enacted under central and state Indian statutes:

- **Tenancy Law ($1,031$ pairs):** *Transfer of Property Act 1882*, *Model Tenancy Act 2021*, and state Rent Control provisions covering security deposits, subletting prohibitions, notice periods, and essential repairs.
- **Consumer Protection Law ($958$ pairs):** *Consumer Protection Act 2019* and *Consumer Protection (E-Commerce) Rules 2020* addressing unfair trade practices, product liability, e-commerce grievance officers, and refund timelines.
- **Employment, Labor & Contract Law ($706$ pairs):** *Indian Contract Act 1872*, *Code on Wages 2019*, *Industrial Relations Code 2020*, *Payment of Gratuity Act 1972*, *Maternity Benefit Act 1961*, *EPF Act 1952*, *Payment of Bonus Act 1965*, *POSH Act 2013*, *ESI Act 1948*, *Contract Labour Act 1970*, and *Factories Act 1948*.

During corpus engineering (`v1` to `v2`), we audited and resolved critical data-pipeline defects in `src/build_multidomain_corpus.py`: (1) eliminated a self-feeding accumulation bug where re-running the builder re-ingested previous `full_dataset.csv` rows; (2) unified disparate domain labels under three canonical regimes; (3) stripped synthetic source tags (`[src]`) that risked shortcut memorization; and (4) diversified adversarial hallucinations beyond repetitive templates. After deduplication and stratified splitting (`74.7%` Train / `12.2%` Val / `13.1%` Test across `(domain, language, decision)` strata), **Table I** and **Table II** summarize exact corpus counts.

**TABLE I: Corpus Distribution Across Statutory Domain, Language (`EN` / `HI`), and Split**

| Legal Domain | Full (`en / hi / Total`) | Train (`en / hi / Total`) | Val (`en / hi / Total`) | Test (`en / hi / Total`) | Share |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tenancy Law** | 704 / 327 / **1,031** | 527 / 244 / **771** | 87 / 40 / **127** | 90 / 43 / **133** | 38.3% |
| **Consumer Protection Law** | 561 / 397 / **958** | 419 / 297 / **716** | 69 / 48 / **117** | 73 / 52 / **125** | 35.5% |
| **Employment, Labor & Contracts** | 386 / 320 / **706** | 288 / 238 / **526** | 48 / 38 / **86** | 50 / 44 / **94** | 26.2% |
| **Total Corpus (`full_dataset.csv`)** | **1,651 / 1,044 / 2,695** | **1,234 / 779 / 2,013*** | **204 / 126 / 330** | **213 / 139 / 352** | **100.0%** |

*Note: Inside `src/train.py`, contrastive identity and boundary-numeric pairs are augmented strictly within the training split only (`2,013` $\rightarrow$ `2,385` training examples), ensuring zero leakage into Validation (`330`) or Test (`352`). Separately, `data/sanity_checks.csv` holds `40` diagnostic anchors (`20` Identical [10 EN, 10 HI] + `20` Unrelated [10 EN, 10 HI]).*

**TABLE II: Preservation Decision Class Distribution Across Splits**

| Preservation Decision Class | Score Range | Full (`N=2,695`) | Train (`N=2,013`) | Val (`N=330`) | Test (`N=352`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Not Preserved (`0`)** | $[1.0, 4.0)$ | 1,161 (43.1%) | 869 (43.2%) | 143 (43.3%) | 149 (42.3%) |
| **Partially Preserved (`1`)** | $[4.0, 8.0)$ | 401 (14.9%) | 297 (14.8%) | 48 (14.5%) | 56 (15.9%) |
| **Preserved (`2`)** | $[8.0, 10.0]$ | 1,133 (42.0%) | 847 (42.1%) | 139 (42.1%) | 147 (41.8%) |

---

## IV. Methodology and Architecture

[FIGURE:fig1_architecture.png|End-to-end architecture of Explainable Multilingual JUDGEBERT combining deterministic Devanagari phonetic normalization, cross-attention encoding over 256 tokens, hybrid `[CLS]`+mean pooling, calibrated multi-task heads, and bilingual rule diagnostics.]

### A. Cross-Attention Backbone & Phonetic Devanagari Normalization

Instead of encoding sentences separately, `MultilingualJudgeBert` concatenates raw and simplified clauses with separator delimiters (`[CLS] S_orig [SEP] S_simp [SEP]`) up to `max_len = 256` tokens, enabling full quadratic cross-attention across `6` Transformer layers (`12` attention heads, `384` hidden channels, `1,536` FFN intermediate width) initialized from `sentence-transformers/all-MiniLM-L6-v2`.

Crucially, during our initial baseline audit (`v1`), we uncovered why Hindi performance lagged behind English (`r = 0.3910` vs. `0.7015`): `all-MiniLM-L6-v2` uses an uncased English WordPiece vocabulary (`30,522` tokens) lacking Devanagari dependent vowel signs (*matras*: `ु, े, ो, ं, ्`) and many consonant forms. As a result, **`145` out of `157` unique Hindi clauses in our validation/test evaluation (`92.4%`) triggered WordPiece `[UNK]` collapse**, turning distinct terms such as *"अनिवार्य"* (mandatory) and *"ऐच्छिक"* (optional) into identical unknown tokens.

To eliminate `[UNK]` loss while strictly preserving the single lightweight MiniLM backbone without swapping to external large models, we introduced `transliterate_devanagari_to_latin()` directly inside `src/model.py`. Whenever Unicode block `\u0900–\u097F` characters are detected, the deterministic phoneme transducer maps Devanagari consonants, independent vowels, matras, *anusvara* (`n`), *candrabindu*, *halant* virama suppression, and Devanagari digits (`०–९`) into clean ASCII Latin phonetics. Because Latin characters lie cleanly inside WordPiece's subword alphabet, **`[UNK]` rate on Hindi pairs drops from `92.4%` (`145/157`) to `0.0%` (`0/157`)**. Furthermore, while pure `[CLS]` pooling misses distributed spans across longer statutory clauses, `MultilingualJudgeBert` extracts a hybrid pooled representation:

$$\mathbf{h}_{\text{pool}} = 0.5\,\mathbf{h}_{[\text{CLS}]} + 0.5\,\left(\frac{\sum_{t=1}^{L} m_t \mathbf{h}_t}{\sum_{t=1}^{L} m_t}\right)$$

where $m_t \in \{0, 1\}$ denotes the attention mask, combining MiniLM's contrastive mean representation with `[CLS]` pair interaction before passing through a shared projection block (`Linear(384 → 384) + GELU + Dropout(0.2)`).

### B. Multi-Task Heads & Parameter Breakdown

From the `384`-dimensional projected vector $\mathbf{z}$, three parallel output heads execute simultaneously, with **all `22,866,446` network parameters unfrozen (`requires_grad = True`)** for full end-to-end statutory adaptation (**Table III**):

**1) Bounded Regression Head:** Forces predictions onto valid human bounds using scaled sigmoid regression:

$$\hat{y}_{\text{LMP}} = 1.0 + 9.0 \times \sigma(\mathbf{w}_{\text{reg}}^T \mathbf{z} + b_{\text{reg}})$$

**2) Decision Classification Head:** Predicts 3-way logits over *Not Preserved*, *Partially Preserved*, and *Preserved*.

**3) Legal Error Head:** Predicts 10-way logits spanning valid preservation plus all nine failure types.

**TABLE III: Parameter Distribution Across JUDGEBERT Components (`100%` Unfrozen)**

| Architecture Component | Tensor Configuration | Weight Count | Share (%) | Trainable |
| :--- | :--- | :---: | :---: | :---: |
| **WordPiece & Positional Embeddings** | Vocab `30,522 × 384`, Pos `512 × 384`, Type `2 × 384` | 11,918,592 | 52.12% | Yes (100%) |
| **6-Layer MiniLM Transformer Blocks** | `6 ×` (`12` Attn Heads, `384` Hidden, `1,536` FFN) + Pooler | 10,794,624 | 47.21% | Yes (100%) |
| **Shared Dense Projection (`dense.0`)** | `Linear(384 → 384)` + `GELU` + `Dropout(0.2)` | 147,840 | 0.65% | Yes (100%) |
| **LMP Regression Head** | `Linear(384 → 1)` + Scaled Sigmoid `[1, 10]` | 385 | <0.01% | Yes (100%) |
| **Decision Head (`DECISION_MAP`)** | `Linear(384 → 3)` (3-Way Ordinal Classes) | 1,155 | <0.01% | Yes (100%) |
| **Legal Error Taxonomy Head (`ERROR_MAP`)** | `Linear(384 → 10)` (10 Error Categories) | 3,850 | 0.02% | Yes (100%) |
| **Total Model Parameters** | **End-to-End Fine-Tuned JUDGEBERT** | **22,866,446** | **100.0%** | **All (100%)** |

### C. Composite Multi-Task Loss, Contrastive Regularization & Hyperparameters

Inspection of `v1` showed complete collapse on the minority middle class *Partially Preserved* (`F1 = 0.00%`, only `14.8%` of training pairs) and weaker gradient signal on Hindi (`38.7%` of pairs). We solve both jointly in `src/train.py` using:

**Composite Loss Formula:** The objective combines Huber regression, tempered class-weighted cross-entropy, error-head cross-entropy, and dual-head consistency under Hindi gradient weighting:

$$\mathcal{L}_{\text{total}} = \mathbb{E}\left[ w_{\text{lang}} \cdot \left( \mathcal{L}_{\text{Huber}}(\hat{y}_{\text{LMP}}, y_{\text{LMP}}) + 0.85\,\mathcal{L}_{\text{CE}}^{\text{dec}} + 0.50\,\mathcal{L}_{\text{CE}}^{\text{err}} + 0.35\,\mathcal{L}_{\text{cons}} \right) \right]$$

where $\mathcal{L}_{\text{Huber}}$ is per-sample `SmoothL1Loss` against human LMP scores; $\mathcal{L}_{\text{CE}}^{\text{dec}}$ uses **tempered inverse-frequency class weighting** $w_c \propto (N / (K \cdot N_c))^{0.65}$ to elevate *Partially Preserved* recall without triggering majority false alarms; $\mathcal{L}_{\text{CE}}^{\text{err}}$ guides error-mode classification; $w_{\text{lang}} = 1.0 + 0.5\,\mathbb{I}_{\text{hi}}$ applies a **`1.5×` Hindi sample weight**; and $\mathcal{L}_{\text{cons}}$ enforces agreement between the continuous score and categorical distribution:

$$\mathcal{L}_{\text{cons}} = \text{MSE}\!\left(\frac{\hat{y}_{\text{LMP}} - 1.0}{9.0},\; 0.05\,p_0 + 0.52\,p_1 + 0.96\,p_2\right)$$

**Train-Only Contrastive Anchors:** Within the training split only (`2,013` $\rightarrow$ `2,385`), `_augment_train_contrastive_pairs` injects identical self-pairs anchored near $10.0$ and digit-perturbation/entity traps to sharpen boundary discrimination.

**Inference Decision Calibration Gate (`_calibrate_decision`):** At inference time, if $\hat{y}_{\text{LMP}} \in [4.0, 8.0)$ and $p_{\text{partial}} > 0.28$, the model predicts *Partially Preserved*; otherwise boundary predictions harmonizing $[1.0, 4.0)$ and $[8.0, 10.0]$ apply probability threshold $0.35$, eliminating contradictions between the numerical LMP score and discrete verdict. Optimization hyperparameters are detailed in **Table IV**.

**TABLE IV: GPU Fine-Tuning Hyperparameters and Optimization Schedule**

| Hyperparameter / Setting | Configured Value | Engineering Justification |
| :--- | :--- | :--- |
| **Optimizer & Weight Decay** | `AdamW` ($\text{weight\_decay} = 0.01$) | Decoupled L2 shrinkage on non-bias/LayerNorm weights (`no_decay` excluded) |
| **Learning Rate & Schedule** | Peak `lr = 3.5e-5`, Cosine Annealing | `get_cosine_schedule_with_warmup` with `10%` linear warmup |
| **Epochs & Selection Criterion** | `12` epochs (Best Checkpoint: **Epoch 11**) | Peak Val Pearson $r = 0.7569$ (`EN 0.7936`, `HI 0.7028`, `Acc 80.30%`, `F1 0.7570`) |
| **Batch Size & Sequence Length** | `batch_size = 16`, `max_len = 256` | Prevents truncation of long multi-clause Indian statutes & Hindi transliterations |
| **Dropout & Gradient Clipping** | `dropout = 0.2`, `clip_grad_norm_ = 1.0` | Regularizes dense projection head; stabilizes gradient norm under `1.5×` loss weighting |
| **Compute Hardware** | NVIDIA GeForce RTX 4060 Laptop GPU | CUDA `torch 2.5.1+cu121` (`USE_TF=0`) |

### D. Bilingual Rule-Guided Explainability & Deployment

To fulfill `PJ_08`'s explainability mandate, `src/explainability.py` executes `analyze_legal_discrepancy(orig, simp, lang, pred_score, pred_error)` across five symbolic statutory rules: (1) numeric/deadline extraction (catching altered fines, percentages, and periods); (2) bilingual negation polarity checks (`not`/`cannot` vs. `नहीं`/`वर्जित`); (3) deontic modality lexicons (`shall`/`must` vs. `may`, `अनिवार्य`/`करेगा` vs. `चाहे तो`/`सकता है`); (4) conditional/exception markers (`unless`/`except` vs. `सिवाय`/`बशर्ते`); and (5) party-role swaps (`Landlord` $\leftrightarrow$ `Tenant`, `Employer` $\leftrightarrow$ `Worker`, `Consumer` $\leftrightarrow$ `Manufacturer`). The unified pipeline powers a 6-tab **Streamlit Interactive Evaluation Dashboard** (`demo/app.py`).

---

## V. Experimental Evaluation and Empirical Results

### A. Experiment 1: Generic Baselines vs. JUDGEBERT (`N = 352`)

We benchmark JUDGEBERT against four lexical similarity baselines (sentence-level BLEU, ROUGE-L, Levenshtein Ratio, TF-IDF Cosine) and generic Sentence-BERT (`all-MiniLM-L6-v2` bi-encoder cosine scaled to `[1.0, 10.0]`) on the stratified multi-domain test set ($N = 352$). We also show our `v1` baseline (`N = 317` prior to corpus deduplication fixes and phonetic Hindi normalization) for direct progression clarity (**Table V** and **Table VI**).

**TABLE V: Unified Multi-Domain Test Set Comparison (`N = 352` Final; `N = 317` for `v1`)**

| Model / Baseline | Pearson $r$ $\uparrow$ | Spearman $\rho$ $\uparrow$ | RMSE $\downarrow$ | MAE $\downarrow$ | Accuracy $\uparrow$ | Macro-F1 $\uparrow$ | Partial F1 $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BLEU (Sentence-level)** | 0.1163 | 0.2798 | 4.6914 | 3.6280 | 44.32% | 0.3792 | 0.2391 |
| **ROUGE-L (LCS F1)** | 0.1528 | 0.3166 | 4.1143 | 3.2714 | 38.07% | 0.3591 | 0.2485 |
| **Levenshtein Ratio** | 0.0987 | 0.2538 | 4.0795 | 3.3656 | 36.36% | 0.3465 | 0.2234 |
| **TF-IDF Cosine** | 0.2047 | 0.3584 | 3.8649 | 3.0537 | 41.19% | 0.4044 | 0.3412 |
| **Generic SBERT Cosine** | 0.2850 | 0.3189 | 4.2048 | 3.2696 | 40.06% | 0.2978 | 0.2690 |
| **JUDGEBERT v1 (Baseline)** | 0.5843 | 0.5412 | 2.9771 | 1.8824 | 67.82% | 0.4876 | 0.0000 |
| **Multilingual JUDGEBERT (v2)** | **0.7436** | **0.7424** | **2.4810** | **1.3072** | **78.98%** | **0.7367** | **0.5421** |

Notice Generic SBERT's fatal failure mode: its F1 on *Not Preserved* clauses collapses to **$0.0133$ (`0.67%` recall)** because legal breaches share most surface vocabulary with original clauses. By contrast, JUDGEBERT achieves **$0.8449$ F1 on Not Preserved**, **$0.8231$ F1 on Preserved**, and raises minority **Partially Preserved F1 from `0.00%` (`v1`) to `54.21%`**, delivering a **$2.61\times$ higher Pearson correlation** and **$60.0\%$ lower MAE** ($3.2696 \to 1.3072$) than SBERT.

[FIGURE:fig2_exp1_baselines_domains.png|Experiment 1 comparison: (Left) Pearson correlation and Macro-F1 across baselines vs. JUDGEBERT; (Right) Domain-wise stratified test performance across Consumer, Tenancy, and Labor Law.]

**TABLE VI: Stratified Test Performance Across Indian Statutory Legal Domains (`N = 352`)**

| Statutory Legal Domain | Test ($N$) | Pearson $r$ $\uparrow$ | Spearman $\rho$ $\uparrow$ | RMSE $\downarrow$ | MAE $\downarrow$ | Accuracy $\uparrow$ | Macro-F1 $\uparrow$ | Partial F1 $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Consumer Protection Law** | 125 | **0.8673** | **0.8697** | **1.8093** | **0.8384** | **88.00%** | **0.8358** | **0.6857** |
| **Tenancy Law** | 133 | **0.7284** | **0.7142** | **2.4709** | **1.3625** | **75.94%** | **0.7151** | **0.5306** |
| **Employment, Labor & Contracts** | 94 | **0.6153** | **0.5631** | **3.1715** | **1.8524** | **71.28%** | **0.6250** | **0.3478** |

Consumer Protection achieves the highest precision ($r = 0.8673$, $88.00\%$ accuracy, MAE $= 0.84$), followed by Tenancy ($r = 0.7284$) and Employment & Labor ($r = 0.6153$, where multi-statute cross-references create higher syntactic variance and a smaller split of $94$ test pairs).

### B. Experiment 2 & `v1` vs. `v2` Ablation: Cross-Lingual Transfer (EN vs. HI)

To isolate the impact of phonetic Devanagari normalization (`[UNK]` reduction $92.4\% \to 0.0\%$), $1.5\times$ Hindi loss weighting, hybrid `[CLS]`+mean pooling, and tempered class balancing, **Table VII** compares `v1` and `v2` across English and Hindi test splits.

**TABLE VII: English vs. Hindi Performance and `v1` $\to$ `v2` Architectural Ablation**

| Language & Architecture | Test ($N$) | Pearson $r$ | Spearman $\rho$ | RMSE | MAE | Accuracy | Macro-F1 | Partial F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English (`v1` Baseline)** | 197 | 0.7015 | 0.6311 | 2.5915 | 1.5475 | 71.57% | 0.5226 | 0.0000 |
| **English (`v2` Final Model)** | 213 | **0.7901** | **0.7908** | **2.1976** | **1.1406** | **80.75%** | **0.7575** | **0.5556** |
| **Hindi (`v1` Baseline, raw Devanagari)** | 120 | 0.3910 | 0.3429 | 3.5197 | 2.4322 | 61.67% | 0.4310 | 0.0000 |
| **Hindi (`v2` Final, Phonetic + Weighted)** | 139 | **0.6817** | **0.6573** | **2.8614** | **1.5626** | **76.26%** | **0.7037** | **0.5143** |

Resolving WordPiece `[UNK]` collapse alongside `1.5×` gradient weighting produced a **+0.2907 Pearson correlation surge in Hindi** (`0.3910` $\rightarrow$ `0.6817`) and **+0.2727 Macro-F1 gain** (`0.4310` $\rightarrow$ `0.7037`), narrowing the English–Hindi accuracy gap from `9.9` points down to just `4.5` points (`80.75%` vs. `76.26%`).

[FIGURE:fig3_v1_v2_multilingual_ablation.png|Ablation comparison between v1 and v2 across Overall, English, Hindi, and Partially Preserved F1 metrics.]

### C. Experiment 3: Out-of-Domain Generalization (`Tenancy` $\to$ `Consumer`)

To test whether narrow single-domain legal models transfer zero-shot to unseen legislation, we trained an isolated JUDGEBERT exclusively on Tenancy Law pairs and evaluated it zero-shot across the entire Consumer Protection corpus ($N = 958$) (**Table VIII**).

**TABLE VIII: Zero-Shot Out-of-Domain Generalization (`Tenancy` $\to$ `Consumer Protection`)**

| Model Regime | Evaluation Target ($N$) | Pearson $r$ | Spearman $\rho$ | RMSE | MAE | Accuracy | Macro-F1 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Single-Domain (`Tenancy` only)** | Consumer Law (Zero-Shot, `958`) | 0.2149 | 0.1579 | 3.4215 | 3.1329 | 35.28% | 0.3503 |
| **Multi-Domain JUDGEBERT (Ours)** | Consumer Law (Held-out Test, `125`) | **0.8673** | **0.8697** | **1.8093** | **0.8384** | **88.00%** | **0.8358** |

Single-domain training collapses when encountering consumer-specific concepts (*unfair trade practice*, *e-commerce intermediary*, *product defect*) absent from tenancy statutes ($r = 0.2149$, accuracy $= 35.28\%$), confirming that multi-domain statutory pretraining/fine-tuning is necessary for cross-statutory deployment.

### D. Experiment 4: Identical and Unrelated Sanity Checks (`N = 40`)

Using `data/sanity_checks.csv` (`20` identical English/Hindi tenancy pairs; `20` completely mismatched cross-domain pairs), we examine calibration stability (**Table IX**).

**TABLE IX: Identical and Unrelated Statutory Pair Sanity Check Bounds (`N = 40`)**

| Sanity Check Category ($N$) | Ground Truth | Generic SBERT Cosine | JUDGEBERT v1 | JUDGEBERT v2 (Final) |
| :--- | :---: | :---: | :---: | :---: |
| **Identical Statutory Pairs (`20`, EN+HI)** | 10.00 | 10.00 $\pm$ 0.00 | 8.91 $\pm$ 0.52 | **9.63 $\pm$ 0.02** |
| **Unrelated Cross-Domain Pairs (`20`, EN+HI)** | 1.00 | 5.62 $\pm$ 2.46 *(Fail)* | 3.45 $\pm$ 1.63 | **2.99 $\pm$ 2.56** |

Because unrelated statutory clauses share domain terminology (`"section"`, `"notice"`, `"authority"`), SBERT averages **`5.62`** (misclassifying unrelated texts inside the *Partially Preserved* band). Multi-task JUDGEBERT tightens identical score consistency to **`9.63 ± 0.02`** while suppressing unrelated pairs to **`2.99`**.

[FIGURE:fig4_ood_sanity_cases.png|Left: Experiment 3 out-of-domain collapse vs. multi-domain mastery; Right: Experiment 4 sanity-check separation on identical vs. unrelated clauses.]

### E. Experiment 5: Qualitative Error Analysis Across 16 Legal Cases

We evaluate 16 legally adversarial clauses (`CASE-01` through `CASE-16`, equally balanced across English and Hindi) spanning eight failure mechanisms. **Table X** reports Ground Truth (`GT`), Generic SBERT, JUDGEBERT (`JB`) scores/verdicts, and neuro-symbolic rule diagnostics (`exp5_error_analysis_15cases.json`).

**TABLE X: Qualitative Analysis Across 16 Difficult Bilingual Statutory Failure Cases**

| ID | Lang | Failure Mode | GT | SBERT | JB Score | JB Verdict | Neuro-Symbolic Comparison & Analysis |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **C-01** | EN | Duty vs. Perm | 2.6 | 4.64 | **1.58** | Not Preserved | *"shall maintain"* $\to$ *"may check"*; both JB & rule flag modal loss. |
| **C-02** | HI | Duty vs. Perm | 2.5 | 8.44 | **1.43** | Not Preserved | *"कराएगा"* $\to$ *"चाहे तो देख सकता"*; JB catches trap missed by rules. |
| **C-03** | EN | Date / Number | 1.9 | 9.52 | **1.66** | Not Preserved | *"within 15 days"* $\to$ *"within six months"*; JB + digit rule flag breach. |
| **C-04** | HI | Date / Number | 1.8 | 9.05 | **2.06** | Not Preserved | *"15 दिनों"* $\to$ *"1 वर्ष"*; both JB & digit rule catch timeline shift. |
| **C-05** | EN | Entity Swap | 1.2 | 6.57 | **1.72** | Not Preserved | Tax liability shifted *Lessor* $\to$ *tenant*; JB detects despite SBERT `6.57`. |
| **C-06** | HI | Entity Swap | 1.3 | 8.96 | **1.45** | Not Preserved | Tax shifted *मकान मालिक* $\to$ *किरायेदार*; JB + Hindi entity rule agree. |
| **C-07** | EN | Contradiction | 1.0 | 3.50 | **1.46** | Not Preserved | *"shall not conduct"* $\to$ *"authorized"*; JB + negation rule flag inversion. |
| **C-08** | HI | Contradiction | 1.0 | 8.11 | **1.37** | Not Preserved | Prohibitive rule inverted; SBERT fooled at `8.11`, JB predicts `1.37`. |
| **C-09** | EN | Condition | 2.1 | 7.77 | **1.74** | Not Preserved | Emergency entry *"in case of pipe bursts"* broadened to *"any reason"*. |
| **C-10** | HI | Condition | 2.0 | 8.41 | **1.49** | Not Preserved | *"पानी का पाइप फटने...आपात स्थिति"* erased $\to$ *"बिना किसी कारण"*. |
| **C-11** | EN | Exception | 4.2 | 8.01 | **1.71** | Not Preserved | *"except guide dogs"* dropped; JB + rule overlay both flag missing exception. |
| **C-12** | HI | Exception | 4.5 | 8.91 | *9.51†* | *Preserved†* | **Error case:** JB neural head missed omitted *"सिवाय"*, **but rule overlay caught it** (`['सिवाय']` omitted). |
| **C-13** | EN | Omission | 5.8 | 7.32 | **4.22** | Part. Preserved | Periodic whitewashing detail simplified; JB correctly lands inside `[4, 8)`. |
| **C-14** | HI | Omission | 6.0 | 9.30 | **7.81** | Part. Preserved | *"हर 2 वर्ष में पुताई"* omitted; JB + numeric rule both flag partial loss. |
| **C-15** | EN | Scope | 2.5 | 6.03 | **2.05** | Not Preserved | Joint & several liability diluted to individual share; JB flags accurately. |
| **C-16** | HI | Scope | 1.8 | 8.36 | **1.44** | Not Preserved | Subletting liability wrongly erased; JB predicts `1.44` despite SBERT `8.36`. |

*†In `CASE-12` (`HI Exception`), notice a key neuro-symbolic insight: although the neural regression head over-predicted (`9.51`), the deterministic bilingual exception detector caught the deleted caveat `"सिवाय"`. Conversely, in six lexical-paraphrase traps (`CASE-02, 05, 09, 10, 13, 15`), the neural cross-encoder correctly flagged severe meaning distortions where heuristic keyword rules stayed silent—proving strong complementarity between neural cross-attention and rule verification.*

### F. Experiment 6: Single-Domain Scaling Study (`Tenancy` $319 \to 1,015$ Pairs)

Before training our unified three-domain model, we conducted an isolated scaling benchmark expanding Tenancy Law from an initial $319$-pair pilot (`N=759` train / `131` test at `1,015` pairs total) (**Table XI**, `tenancy_only_results.json`).

**TABLE XI: Single-Domain Tenancy Corpus Scaling Benchmark (`319` $\to$ `1,015` Pairs)**

| Tenancy Model Variant | Eval Subset ($N$) | Pearson $r$ | Spearman $\rho$ | RMSE | Accuracy | Macro-F1 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Generic SBERT Cosine** | Overall Tenancy (`131`) | 0.2688 | 0.2410 | 4.2677 | 35.88% | 0.2822 |
| **Pilot JUDGEBERT (319 Pairs)** | Overall Tenancy (Pilot) | 0.4434 | 0.3800 | 3.3800 | 11.10% | — |
| **JUDGEBERT Tenancy (1,015 Pairs)** | Overall Tenancy (`131`) | 0.5131 | 0.4341 | 3.0884 | 62.60% | 0.4564 |
| **JUDGEBERT Tenancy (1,015 Pairs)** | English Split (`90`) | 0.6057 | 0.5457 | 2.7456 | 66.67% | 0.4841 |
| **JUDGEBERT Tenancy (1,015 Pairs)** | Hindi Split (`41`, pre-translit.) | 0.3517 | 0.3192 | 3.7320 | 53.66% | 0.3750 |

Expanding sample count by $3.2\times$ boosted single-domain accuracy by $5.6\times$ (`11.10%` $\rightarrow$ `62.60%`), yet raw-Devanagari Hindi (`0.3517`) lagged sharply until we introduced multi-domain data and phonetic transduction (`v2` multi-domain Hindi $r = 0.6817$, Tenancy overall $r = 0.7284$).

---

## VI. Literature Contextualization

**Table XII** situates our models alongside prior legal and general meaning-preservation benchmarks reported in literature. Because Beauchemin et al. [1] evaluate French property insurance (`FrJUDGE`) rather than Indian statutory clauses, literature rows serve as contextual reference points rather than same-corpus comparisons.

**TABLE XII: Literature Contextualization Against Prior Meaning Preservation Benchmarks**

| Model / Reference | Corpus / Language | Parameters | Pearson $r$ | Accuracy | Explainable |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **JUDGEBERT (v2 — Consumer Test)** | Indian Consumer Statutes (`EN+HI`, `N=125`) | **22.87M** | **0.8673** | **88.00%** | **Yes (Rule Overlay)** |
| **JUDGEBERT (v2 — English Test)** | Multi-Statutory English (`N=213`) | **22.87M** | **0.7901** | **80.75%** | **Yes (Rule Overlay)** |
| **JUDGEBERT (v2 — Overall Test)** | Multi-Statutory Unified (`EN+HI`, `N=352`) | **22.87M** | **0.7436** | **78.98%** | **Yes (Rule Overlay)** |
| **JUDGEBERT (v2 — Tenancy Test)** | Indian Tenancy Statutes (`EN+HI`, `N=133`) | **22.87M** | **0.7284** | **75.94%** | **Yes (Rule Overlay)** |
| **JUDGEBERT (v2 — Hindi Test)** | Multi-Statutory Hindi (`N=139`) | **22.87M** | **0.6817** | **76.26%** | **Yes (Rule Overlay)** |
| **Beauchemin et al. (EMNLP 2025) [1]** | `FrJUDGE` French Insurance (`N=297`) | 355M (RoBERTa-lg) | ~0.6500 | ~68.00% | No |
| **JUDGEBERT (v2 — Labor Test)** | Indian Labor & Contracts (`EN+HI`, `N=94`) | **22.87M** | **0.6153** | **71.28%** | **Yes (Rule Overlay)** |
| **MeaningBERT (Lit. Baseline) [6]** | General English Corpus | ~110M | ~0.4200 | ~52.00% | No |
| **Generic SBERT (Ours Test)** | Multi-Statutory Unified (`N=352`) | 22.7M (Bi-Enc.) | 0.2850 | 40.06% | No |

Notably, our compact **22.87M-parameter** cross-encoder is **15.5× smaller** than RoBERTa-large (355M) yet exhibits stronger correlation across English, Hindi, Tenancy, Consumer Protection, and the overall unified test split.

---

## VII. Discussion, Limitations, and Future Work

Our empirical analysis confirms the core research hypothesis of `PJ_08`: **cross-attention over concatenated statutory pairs, stabilized via phonetic Hindi normalization and ordinal consistency losses, captures binding legal semantics far more faithfully than generic similarity models.** Three core technical takeaways stand out:

1. **Tokenizer Script Mismatch Often Masquerades as Poor Language Transfer:** The `0.3910` $\rightarrow$ `0.6817` Hindi surge demonstrates that before replacing compact architectures with larger models, fixing WordPiece `[UNK]` collapse (`92.4%` $\rightarrow$ `0.0%`) unlocks latent cross-attention capacity across scripts.
2. **Tempered Class Weighting Resolves Ordinal Collapse:** Raising exponent weighting $(N/(K \cdot N_c))^{0.65}$ with consistency regularization lifted minority *Partially Preserved* F1 from `0.00%` (`v1`) to `54.21%` (`v2`) (`68.57%` in Consumer Law) without harming extreme verdicts.
3. **Neuro-Symbolic Pairing Improves Safety:** Qualitative analysis (`CASE-12`) reveals that even strong neural models can occasionally misread rare Hindi exclusion particles (*"सिवाय"*), making deterministic statutory checks an essential safety guardrail.

**Limitations & Future Directions:** (i) *Partially Preserved* F1 (`54.21%`) still trails *Not Preserved* (`84.49%`) and *Preserved* (`82.31%`) due to genuine annotation boundary ambiguity near `4.0` and `8.0`; (ii) evaluation remains sentence-level, omitting cross-section statutory schedules or multi-paragraph context windows; and (iii) rare Devanagari negation/exception phrasing (`CASE-12`) warrants targeted contrastive hard-negative mining and gradient-based token saliency (Integrated Gradients) in future iterations.

---

## VIII. Conclusion and Deliverables

We designed, fine-tuned, and validated **Explainable Multilingual JUDGEBERT (`PJ_08`)**, extending legal meaning preservation beyond French insurance to **2,695 English and Hindi statutory pairs** across Indian Tenancy, Consumer Protection, and Employment & Labor laws. Across six empirical evaluations, our 22.87M-parameter cross-encoder decisively outperformed lexical baselines and generic SBERT ($r = 0.7436$ vs. $0.2850$; $78.98\%$ vs. $40.06\%$ accuracy), boosted Hindi correlation from $0.3910$ to $0.6817$ via lossless phonetic normalization, proved the necessity of multi-domain data via zero-shot OOD evaluation ($r = 0.2149$), and paired quantitative verdicts with bilingual rule explanations.

**Deliverables Checklist (`CSET 346 – PJ_08`):**
1. **Source Code & Experimental Artifacts (GitHub):** `https://github.com/InsaneSoul207/JudgeBERT-Indic-Tenancy-Labor-Consumer`
2. **IEEE Research Report (Markdown, Word `.docx`, PDF `.pdf`):** `paper/IEEE_Research_Paper.{md,docx,pdf}`
3. **Presentation Deck & Live Evaluation App:** `Milestone1_JUDGEBERT_LMP.pptx` and 6-tab Streamlit dashboard (`demo/app.py`)

---

## References

[1] D. Beauchemin, M. Albert-Rochette, R. Khoury, and P.-L. Déziel, "JUDGEBERT: Assessing Legal Meaning Preservation Between Sentences," in *Proc. 2025 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, Nov. 2025, pp. 92–118.  
[2] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in *Proc. Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2019, pp. 3982–3992.  
[3] I. Chalkidis, M. Fergadiotis, P. Malakasiotis, N. Aletras, and I. Androutsopoulos, "LEGAL-BERT: The Muppets straight out of Law School," in *Findings of EMNLP*, 2020, pp. 2898–2904.  
[4] K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu, "BLEU: a Method for Automatic Evaluation of Machine Translation," in *Proc. 40th Annu. Meeting Assoc. Comput. Linguist. (ACL)*, 2002, pp. 311–318.  
[5] C.-Y. Lin, "ROUGE: A Package for Automatic Evaluation of Summaries," in *Text Summarization Branches Out (ACL Workshop)*, 2004, pp. 74–81.  
[6] D. Beauchemin, N. Garneau, E. Sénécal, R. Khoury, and L. Lamontagne, "MeaningBERT: Assessing Meaning Preservation Between Sentences," *Frontiers in Artificial Intelligence*, vol. 6, 2023.  
[7] S. Khanuja et al., "MuRIL: Multilingual Representations for Indian Languages," *arXiv preprint arXiv:2103.10730*, 2021.  
[8] A. Conneau et al., "Unsupervised Cross-lingual Representation Learning at Scale," in *Proc. 58th Annu. Meeting Assoc. Comput. Linguist. (ACL)*, 2020, pp. 8440–8451.  
