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
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoConfig

# Set HF cache path properly
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")

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
            
        # Extract representation: [CLS] token representation
        # outputs[0] has shape (batch_size, seq_len, hidden_dim)
        cls_rep = outputs[0][:, 0, :]
        feat = self.dense(cls_rep)
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
    def __init__(self, model_path=None, base_model_name="sentence-transformers/all-MiniLM-L6-v2", device=None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.model = MultilingualJudgeBert(base_model_name=base_model_name)
        
        if model_path and os.path.exists(model_path):
            state = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state)
            
        self.model.to(self.device)
        self.model.eval()

    def predict_pair(self, original_text, simplified_text):
        """Inference on a single original-simplified sentence pair."""
        inputs = self.tokenizer(
            original_text,
            simplified_text,
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
            dec_idx = torch.argmax(outs["decision_logits"], dim=-1).item()
            err_idx = torch.argmax(outs["error_logits"], dim=-1).item()

        dec_str = REV_DECISION_MAP.get(dec_idx, "Not Preserved")
        err_str = REV_ERROR_MAP.get(err_idx, "none")
        
        return {
            "lmp_score": round(score, 2),
            "decision": dec_str,
            "error_category": err_str if dec_str != "Preserved" else "none"
        }

    def predict_df(self, df):
        """Batch prediction over a DataFrame containing 'original' and 'simplified'."""
        scores, decisions, error_cats = [], [], []
        
        for _, row in df.iterrows():
            res = self.predict_pair(row["original"], row["simplified"])
            scores.append(res["lmp_score"])
            decisions.append(res["decision"])
            error_cats.append(res["error_category"])
            
        res_df = df.copy()
        res_df["judgebert_pred_score"] = scores
        res_df["judgebert_pred_decision"] = decisions
        res_df["judgebert_pred_error"] = error_cats
        return res_df
