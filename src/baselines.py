"""
Baseline Methods for Legal Meaning Preservation Evaluation
Includes:
1. Lexical Overlap:
   - BLEU (Sentence-level BLEU-2 / BLEU-4)
   - ROUGE-L (LCS-based F1)
   - Token Jaccard Similarity & Levenshtein Ratio
2. Generic Semantic Similarity (Bi-Encoder Embeddings):
   - SBERT Multilingual (`paraphrase-multilingual-MiniLM-L12-v2` or cached `all-MiniLM-L6-v2`)
   - LegalBERT (`nlpaueb/legal-bert-base-uncased` for domain comparison)
   - TF-IDF Cosine Similarity (fast deterministic lexical vector baseline)
"""

import re
import math
from collections import Counter
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def simple_tokenize(text):
    """Tokenizes both English and Hindi scripts by words and punctuation."""
    text = text.lower()
    # Match alphanumeric words or Devanagari characters
    tokens = re.findall(r'[\w\u0900-\u097F]+', text)
    return tokens

def compute_levenshtein_ratio(s1, s2):
    """Calculates Levenshtein similarity ratio between two strings [0.0, 1.0]."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
        
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,      # deletion
                           dp[i][j - 1] + 1,      # insertion
                           dp[i - 1][j - 1] + cost) # substitution
            
    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return max(0.0, (max_len - distance) / max_len)

def compute_bleu(ref_tokens, hyp_tokens, max_n=2):
    """Calculates smoothed sentence-level BLEU-N score [0.0, 1.0]."""
    if not ref_tokens or not hyp_tokens:
        return 0.0
    
    # Brevity penalty
    c = len(hyp_tokens)
    r = len(ref_tokens)
    bp = 1.0 if c > r else math.exp(1 - (r / c if c > 0 else 0))
    
    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = Counter([tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens) - n + 1)])
        hyp_ngrams = Counter([tuple(hyp_tokens[i:i+n]) for i in range(len(hyp_tokens) - n + 1)])
        
        overlap = 0
        total = sum(hyp_ngrams.values())
        if total == 0:
            precisions.append(1e-7)
            continue
            
        for ng, count in hyp_ngrams.items():
            overlap += min(count, ref_ngrams.get(ng, 0))
            
        precisions.append((overlap + 0.1) / (total + 0.1)) # Add-0.1 smoothing
        
    log_sum = sum(math.log(p) for p in precisions) / len(precisions)
    return bp * math.exp(log_sum)

def compute_rouge_l(ref_tokens, hyp_tokens):
    """Calculates Longest Common Subsequence (LCS) ROUGE-L F1 [0.0, 1.0]."""
    m, n = len(ref_tokens), len(hyp_tokens)
    if m == 0 or n == 0:
        return 0.0
    
    lcs = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if ref_tokens[i] == hyp_tokens[j]:
                lcs[i+1][j+1] = lcs[i][j] + 1
            else:
                lcs[i+1][j+1] = max(lcs[i+1][j], lcs[i][j+1])
                
    lcs_len = lcs[m][n]
    prec = lcs_len / n
    rec = lcs_len / m
    if prec + rec == 0:
        return 0.0
    return (2 * prec * rec) / (prec + rec)

def compute_jaccard(ref_tokens, hyp_tokens):
    """Calculates token Jaccard similarity [0.0, 1.0]."""
    s1 = set(ref_tokens)
    s2 = set(hyp_tokens)
    union = s1.union(s2)
    if not union:
        return 0.0
    return len(s1.intersection(s2)) / len(union)

class BaselineEvaluator:
    def __init__(self, sbert_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.sbert_name = sbert_model_name
        self.sbert_model = None
        
    def _load_sbert(self):
        if self.sbert_model is None:
            try:
                # Try loading multilingual SBERT or fallback to cached
                self.sbert_model = SentenceTransformer(self.sbert_name)
            except Exception as e:
                print(f"Could not load {self.sbert_name}, falling back to all-MiniLM-L6-v2: {e}")
                self.sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

    def run_lexical_baselines(self, df):
        """Computes BLEU, ROUGE-L, Levenshtein, and Jaccard for dataframe pairs."""
        results = []
        for _, row in df.iterrows():
            orig_tokens = simple_tokenize(row["original"])
            simp_tokens = simple_tokenize(row["simplified"])
            
            bleu = compute_bleu(orig_tokens, simp_tokens)
            rouge_l = compute_rouge_l(orig_tokens, simp_tokens)
            lev = compute_levenshtein_ratio(row["original"], row["simplified"])
            jaccard = compute_jaccard(orig_tokens, simp_tokens)
            
            # Map [0, 1] metrics to [1.0, 10.0] LMP scale: 1.0 + 9.0 * metric
            results.append({
                "id": row["id"],
                "bleu_raw": bleu,
                "bleu_lmp_pred": 1.0 + 9.0 * bleu,
                "rouge_l_raw": rouge_l,
                "rouge_l_lmp_pred": 1.0 + 9.0 * rouge_l,
                "levenshtein_raw": lev,
                "levenshtein_lmp_pred": 1.0 + 9.0 * lev,
                "jaccard_raw": jaccard,
                "jaccard_lmp_pred": 1.0 + 9.0 * jaccard
            })
        return pd.DataFrame(results)

    def run_sbert_baseline(self, df):
        """Computes SBERT Cosine Similarity bi-encoder baseline."""
        self._load_sbert()
        origs = df["original"].tolist()
        simps = df["simplified"].tolist()
        
        orig_embs = self.sbert_model.encode(origs, show_progress_bar=False, normalize_embeddings=True)
        simp_embs = self.sbert_model.encode(simps, show_progress_bar=False, normalize_embeddings=True)
        
        # Dot product of normalized vectors = cosine similarity
        cos_sims = np.sum(orig_embs * simp_embs, axis=1)
        # Clip to [0, 1] then map to [1, 10]
        cos_sims_clipped = np.clip(cos_sims, 0.0, 1.0)
        lmp_preds = 1.0 + 9.0 * cos_sims_clipped
        
        return pd.DataFrame({
            "id": df["id"].tolist(),
            "sbert_cosine": cos_sims,
            "sbert_lmp_pred": lmp_preds
        })

    def run_tfidf_baseline(self, df):
        """Computes character/word n-gram TF-IDF cosine similarity."""
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        all_texts = df["original"].tolist() + df["simplified"].tolist()
        vectorizer.fit(all_texts)
        
        orig_vecs = vectorizer.transform(df["original"].tolist())
        simp_vecs = vectorizer.transform(df["simplified"].tolist())
        
        # Row-wise dot product of normalized sparse matrices
        sims = np.asarray(orig_vecs.multiply(simp_vecs).sum(axis=1)).flatten()
        sims_clipped = np.clip(sims, 0.0, 1.0)
        lmp_preds = 1.0 + 9.0 * sims_clipped
        
        return pd.DataFrame({
            "id": df["id"].tolist(),
            "tfidf_cosine": sims,
            "tfidf_lmp_pred": lmp_preds
        })
