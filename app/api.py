#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from joblib import load
from pathlib import Path

app = FastAPI(title="SQLi NLP Detector")

MODEL_PATH = Path("models/sqli_charngram_logreg.joblib")  # switch to rf if desired
if not MODEL_PATH.exists():
    raise RuntimeError("Model file not found. Please run `python train.py` first to create models/sqli_charngram_logreg.joblib")

model = load(MODEL_PATH)

class Item(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(item: Item):
    try:
        prob = float(model.predict_proba([item.text])[0][1])
        return {"attack_prob": prob, "label": int(prob >= 0.5)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
