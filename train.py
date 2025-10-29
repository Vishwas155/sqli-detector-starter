#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from joblib import dump
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report
import numpy as np

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

DATA_PATH = Path("data/Sheet 1-New 2.csv")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def build_pipe(model):
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3,5), lowercase=False)),
        ("clf", model)
    ])

def main():
    df = pd.read_csv(DATA_PATH)
    
    # Replace NaN values with empty strings
    df = df.fillna("")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )

    # Baseline: Logistic Regression
    logreg = LogisticRegression(max_iter=1000, solver="liblinear", class_weight="balanced")
    logreg_pipe = build_pipe(logreg)
    logreg_pipe.fit(X_train, y_train)
    y_pred_lr = logreg_pipe.predict(X_test)
    print("=== Logistic Regression (char n-gram TF-IDF) ===")
    # in the classification report we added zero_division=0
    print(classification_report(y_test, y_pred_lr, digits=3, zero_division=0))
    dump(logreg_pipe, MODELS_DIR / "sqli_charngram_logreg.joblib")
    print("Saved -> models/sqli_charngram_logreg.joblib\\n")
    # a new line is added here cross validation metrics 
    lr_cv_scores = cross_val_score(logreg_pipe, df["text"], df["label"],cv=cv, scoring="f1")
    print(f"LR 5-fold F1 (attack-weighted): mean={lr_cv_scores.mean():.3f} ± {lr_cv_scores.std():.3f}")

    # Proposed: Random Forest
    rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,              # limit depth
    min_samples_leaf=2,        # avoid pure leaves
    class_weight="balanced_subsample",
    n_jobs=-1,
    random_state=42
    )
    rf_pipe = build_pipe(rf)
    rf_pipe.fit(X_train, y_train)
    y_pred_rf = rf_pipe.predict(X_test)
    print("=== Random Forest (char n-gram TF-IDF) ===")
    # in the classification report we added zero_division=0
    print(classification_report(y_test, y_pred_rf, digits=3, zero_division=0))
    dump(rf_pipe, MODELS_DIR / "sqli_charngram_rf.joblib")
    print("Saved -> models/sqli_charngram_rf.joblib")
    # a new line is added here  cross validation metrics
    rf_cv_scores = cross_val_score(rf_pipe, df["text"], df["label"],cv=cv, scoring="f1")
    print(f"RF 5-fold F1: mean={rf_cv_scores.mean():.3f} ± {rf_cv_scores.std():.3f}")

if __name__ == "__main__":
    main()
