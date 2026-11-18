"""
Compile and split a dedicated Tenancy-Only dataset (319 pairs).
"""
import pandas as pd
import numpy as np

def build_tenancy_corpus():
    df1 = pd.read_csv("data/full_dataset.csv")
    df2 = pd.read_csv("data/real_scraped_dataset.csv")

    t1 = df1[df1["domain"] == "tenancy"].copy()
    t2 = df2[df2["domain"] == "tenancy"].copy()

    # Combine
    cols = ["id", "language", "domain", "original", "simplified", "lmp_score", "decision", "error_category", "explanation"]
    combined = pd.concat([t1[cols], t2[cols]], ignore_index=True)
    combined = combined.drop_duplicates(subset=["original", "simplified"]).reset_index(drop=True)

    # Stratified Train/Val/Test Split (70/15/15)
    train_dfs, val_dfs, test_dfs = [], [], []
    for (lang, dec), group in combined.groupby(["language", "decision"]):
        shuffled = group.sample(frac=1.0, random_state=42).reset_index(drop=True)
        n = len(shuffled)
        n_train = int(0.70 * n)
        n_val = int(0.15 * n)
        
        train_dfs.append(shuffled.iloc[:n_train])
        val_dfs.append(shuffled.iloc[n_train:n_train+n_val])
        test_dfs.append(shuffled.iloc[n_train+n_val:])

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    val_df = pd.concat(val_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)

    combined.to_csv("data/tenancy_full.csv", index=False, encoding="utf-8")
    train_df.to_csv("data/tenancy_train.csv", index=False, encoding="utf-8")
    val_df.to_csv("data/tenancy_val.csv", index=False, encoding="utf-8")
    test_df.to_csv("data/tenancy_test.csv", index=False, encoding="utf-8")

    print(f"Total Dedicated Tenancy Pairs: {len(combined)}")
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    print("\nLanguage breakdown:")
    print(combined["language"].value_counts())
    print("\nDecision breakdown:")
    print(combined["decision"].value_counts())

if __name__ == "__main__":
    build_tenancy_corpus()
