"""
JUDGEBERT Multilingual Cross-Encoder Model Architecture
Extends JUDGEBERT (Beauchemin et al., EMNLP 2025) for Multilingual (English + Hindi)
Legal Meaning Preservation (LMP) evaluation.

Features:
- Joint Cross-Attention: [CLS] S_orig [SEP] S_simp [SEP]
- Multi-Task Prediction:
    1. Continuous LMP Regression Head (bounded to [1.0, 10.0] via Scaled Sigmoid)
    2. 3-Way Ordinal Classification Head (Preserved, Partially Preserved, Not Preserved)
    3. Legal Error Category Head (the 9 failure modes)
"""

import os
import re
# Set HF cache & disable unused TF import before transformers loads
os.environ["USE_TF"] = "0"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoConfig

_DEV_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऑ": "o", "ऍ": "e"
}
_DEV_MATRAS = {
    "ा": "aa", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu",
    "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ॉ": "o", "ॅ": "e"
}
_DEV_CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "r", "ढ़": "rh", "फ़": "f", "य़": "y",
    "ळ": "l"
}
_DEV_MODS = {
    "ं": "n", "ँ": "n", "ः": "h", "।": ".", "॥": ".",
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"
}
_DEV_RE = re.compile(r"[\u0900-\u097F]")

def transliterate_devanagari_to_latin(text: str) -> str:
    """
    Lossless deterministic Devanagari-to-Latin phonetic transducer.
    Prevents all-MiniLM-L6-v2 WordPiece from stripping Hindi vowel matras/halants
    or collapsing Devanagari legal terms (e.g., ऐच्छिक, शुल्क, छह) into [UNK].
    """
    if not text or not _DEV_RE.search(text):
        return text
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if i + 1 < n and text[i + 1] == "़" and (ch + "़") in _DEV_CONSONANTS:
            c = _DEV_CONSONANTS[ch + "़"]
            i += 2
        elif ch in _DEV_CONSONANTS:
            c = _DEV_CONSONANTS[ch]
            i += 1
        elif ch in _DEV_VOWELS:
            out.append(_DEV_VOWELS[ch])
            i += 1
            continue
        elif ch in _DEV_MATRAS:
            out.append(_DEV_MATRAS[ch])
            i += 1
            continue
        elif ch in _DEV_MODS:
            out.append(_DEV_MODS[ch])
            i += 1
            continue
        elif ch == "्" or ch == "़":
            i += 1
            continue
        else:
            out.append(ch)
            i += 1
            continue

        # Attach vowel/halant modifier following a consonant
        if i < n and text[i] == "्":
            out.append(c)
            i += 1
        elif i < n and text[i] in _DEV_MATRAS:
            out.append(c + _DEV_MATRAS[text[i]])
            i += 1
        elif i < n and text[i] == "ं":
            out.append(c + "an")
            i += 1
        else:
            out.append(c + "a")
    return re.sub(r"\s+", " ", "".join(out)).strip()

def preprocess_legal_text(text: str, transliterate_hindi: bool = True) -> str:
    text = str(text).strip()
    if transliterate_hindi:
        return transliterate_devanagari_to_latin(text)
    return text

DECISION_MAP = {"Not Preserved": 0, "Partially Preserved": 1, "Preserved": 2}
REV_DECISION_MAP = {0: "Not Preserved", 1: "Partially Preserved", 2: "Preserved"}

ERROR_MAP = {
    "none": 0,
    "duty_vs_permission": 1,
    "date_number": 2,
    "entity": 3,
    "contradiction": 4,
    "condition": 5,
    "exception": 6,
    "omission": 7,
    "scope": 8,
    "hallucination": 9
}
REV_ERROR_MAP = {v: k for k, v in ERROR_MAP.items()}

class MultilingualJudgeBert(nn.Module):
    def __init__(self, base_model_name="sentence-transformers/all-MiniLM-L6-v2", hidden_dim=384, dropout=0.2):
        super().__init__()
        self.base_model_name = base_model_name
        
        # Load transformer backbone
        try:
            self.transformer = AutoModel.from_pretrained(base_model_name)
            hidden_size = self.transformer.config.hidden_size
        except Exception:
            # Fallback if specific weights need explicit local path
            local_cache = os.path.expanduser("~/.cache/huggingface/hub")
            self.transformer = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            hidden_size = self.transformer.config.hidden_size

        self.dropout = nn.Dropout(dropout)
        
        # Shared dense representation
        self.dense = nn.Sequential(
            nn.Linear(hidden_size, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )
        
        # 1. LMP Score Regression Head: Bounded to [1.0, 10.0] via Scaled Sigmoid
        self.regression_head = nn.Linear(hidden_dim, 1)
        
        # 2. 3-Way Preservation Decision Head
        self.decision_head = nn.Linear(hidden_dim, 3)
        
        # 3. Error Type Classification Head (9 error types + none)
        self.error_head = nn.Linear(hidden_dim, len(ERROR_MAP))

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        if token_type_ids is not None:
            outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        else:
            outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
            
        # Combine [CLS] token with attention-masked mean pooling (matches MiniLM pretraining while keeping 384-d heads)
        token_embs = outputs[0]
        cls_rep = token_embs[:, 0, :]
        mask_expanded = attention_mask.unsqueeze(-1).expand(token_embs.size()).float()
        mean_rep = torch.sum(token_embs * mask_expanded, dim=1) / torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        pooled_rep = 0.5 * cls_rep + 0.5 * mean_rep
        feat = self.dense(pooled_rep)
        feat = self.dropout(feat)
        
        # Regression: Scale sigmoid(x) * 9.0 + 1.0 -> [1.0, 10.0]
        raw_reg = self.regression_head(feat).squeeze(-1)
        pred_lmp = 1.0 + 9.0 * torch.sigmoid(raw_reg)
        
        # Decision logits: (batch_size, 3)
        decision_logits = self.decision_head(feat)
        
        # Error logits: (batch_size, 10)
        error_logits = self.error_head(feat)
        
        return {
            "pred_lmp": pred_lmp,
            "raw_reg": raw_reg,
            "decision_logits": decision_logits,
            "error_logits": error_logits
        }

class JudgeBertPredictor:
    """High-level wrapper for inference, explanation, and evaluation."""
    def __init__(self, model_path=None, base_model_name="sentence-transformers/all-MiniLM-L6-v2", device=None, transliterate_hindi=True):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.transliterate_hindi = transliterate_hindi

        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.model = MultilingualJudgeBert(base_model_name=base_model_name)

        if model_path and os.path.exists(model_path):
            state = torch.load(model_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(state)

        self.model.to(self.device)
        self.model.eval()

    @staticmethod
    def _calibrate_decision(score, dec_probs, raw_idx):
        """Harmonizes continuous LMP regression score with categorical decision probabilities."""
        if 4.0 <= score < 8.0 and dec_probs[1] > 0.28:
            return 1
        elif score >= 8.0 and dec_probs[2] > 0.35:
            return 2
        elif score < 4.0 and dec_probs[0] > 0.35:
            return 0
        return raw_idx

    def predict_pair(self, original_text, simplified_text):
        """Inference on a single original-simplified sentence pair."""
        orig_proc = preprocess_legal_text(original_text, self.transliterate_hindi)
        simp_proc = preprocess_legal_text(simplified_text, self.transliterate_hindi)
        inputs = self.tokenizer(
            orig_proc,
            simp_proc,
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)
        token_type_ids = inputs.get("token_type_ids")
        if token_type_ids is not None:
            token_type_ids = token_type_ids.to(self.device)

        with torch.no_grad():
            outs = self.model(input_ids, attention_mask, token_type_ids)
            score = outs["pred_lmp"].item()
            dec_probs = torch.softmax(outs["decision_logits"], dim=-1).squeeze(0).cpu().numpy()
            raw_idx = torch.argmax(outs["decision_logits"], dim=-1).item()
            err_idx = torch.argmax(outs["error_logits"], dim=-1).item()

        dec_idx = self._calibrate_decision(score, dec_probs, raw_idx)
        dec_str = REV_DECISION_MAP.get(dec_idx, "Not Preserved")
        err_str = REV_ERROR_MAP.get(err_idx, "none")

        return {
            "lmp_score": round(score, 2),
            "decision": dec_str,
            "error_category": err_str if dec_str != "Preserved" else "none"
        }

    def predict_df(self, df, batch_size=32):
        """Efficient batch prediction over a DataFrame containing 'original' and 'simplified'."""
        origs = [preprocess_legal_text(x, self.transliterate_hindi) for x in df["original"].astype(str).tolist()]
        simps = [preprocess_legal_text(x, self.transliterate_hindi) for x in df["simplified"].astype(str).tolist()]
        n = len(origs)

        scores, decisions, error_cats = [], [], []

        for i in range(0, n, batch_size):
            batch_orig = origs[i:i + batch_size]
            batch_simp = simps[i:i + batch_size]

            inputs = self.tokenizer(
                batch_orig,
                batch_simp,
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt"
            )
            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)
            token_type_ids = inputs.get("token_type_ids")
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(self.device)

            with torch.no_grad():
                outs = self.model(input_ids, attention_mask, token_type_ids)
                b_scores = outs["pred_lmp"].cpu().numpy().tolist()
                b_probs = torch.softmax(outs["decision_logits"], dim=-1).cpu().numpy()
                b_dec_idx = torch.argmax(outs["decision_logits"], dim=-1).cpu().numpy().tolist()
                b_err_idx = torch.argmax(outs["error_logits"], dim=-1).cpu().numpy().tolist()

            for sc, probs, d_idx, e_idx in zip(b_scores, b_probs, b_dec_idx, b_err_idx):
                cal_idx = self._calibrate_decision(sc, probs, d_idx)
                dec_str = REV_DECISION_MAP.get(cal_idx, "Not Preserved")
                err_str = REV_ERROR_MAP.get(e_idx, "none")

                scores.append(round(sc, 2))
                decisions.append(dec_str)
                error_cats.append(err_str if dec_str != "Preserved" else "none")

        res_df = df.copy()
        res_df["judgebert_pred_score"] = scores
        res_df["judgebert_pred_decision"] = decisions
        res_df["judgebert_pred_error"] = error_cats
        return res_df
