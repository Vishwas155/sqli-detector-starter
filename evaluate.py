#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, average_precision_score, precision_recall_curve
from joblib import load

DATA_PATH = Path("data/Sheet 1-New 2.csv")
MODEL_PATH = Path("models/sqli_charngram_logreg.joblib")  # change to rf if preferred
OUT_DIR = Path("models")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(DATA_PATH)

    # 🧹 Drop rows where text or label is missing
    df = df.dropna(subset=["text", "label"])

    # 🧼 Ensure all texts are strings (convert numbers, etc.)
    df["text"] = df["text"].astype(str).str.strip()

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )

    model = load(MODEL_PATH)
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    cm = confusion_matrix(y_test, preds)
    ConfusionMatrixDisplay(cm).plot()
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "confusion_matrix.png")
    plt.close()

    ap = average_precision_score(y_test, probs)
    p, r, _ = precision_recall_curve(y_test, probs)
    plt.plot(r, p)
    plt.title(f"PR Curve (AP={ap:.3f})")
    plt.xlabel("Recall"); plt.ylabel("Precision")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "pr_curve.png")
    plt.close()

    print(f"Saved figures to {OUT_DIR}/")
    print(f"Average Precision (PR-AUC): {ap:.3f}")
    print("Missing text rows:", df["text"].isna().sum())
    print("Missing label rows:", df["label"].isna().sum())


if __name__ == "__main__":
    main()
