#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from joblib import load
from pathlib import Path

app = FastAPI(title="SQLi NLP Detector (CORS enabled)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = Path("models/sqli_charngram_logreg.joblib")  # switch to rf if desired
if not MODEL_PATH.exists():
    raise RuntimeError("Model file not found. Please run `python train.py` first.")

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
