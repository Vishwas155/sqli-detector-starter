# #!/usr/bin/env python3
# from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel
# from joblib import load
# from pathlib import Path

# app = FastAPI(title="SQLi NLP Detector")

# MODEL_PATH = Path("models/sqli_charngram_rf.joblib")  # switch to rf if desired
# if not MODEL_PATH.exists():
#     raise RuntimeError("Model file not found. Please run `python train.py` first to create models/sqli_charngram_logreg.joblib")

# model = load(MODEL_PATH)

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/score")
# async def score(request: Request):
#     try:
#         try:
#             data = await request.json()
#             text = data.get("text", "")
#         except Exception:
#             text = (await request.body()).decode("utf-8").strip()

#         if not text:
#             raise HTTPException(status_code=400, detail="No text provided for scoring")

#         prob = float(model.predict_proba([text])[0][1])
#         return {"attack_prob": prob, "label": int(prob >= 0.5)}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from joblib import load
from pathlib import Path
from typing import Optional
# --
import time
import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
# ... other imports you had

# set up logging (optional)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="SQLi NLP Detector")

# --- Middleware to measure server processing time and add header ---
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    # create an id for traceability (optional)
    req_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        # measure even on exceptions
        elapsed_ms = (time.perf_counter() - start) * 1000
        logging.exception("Request %s %s failed after %.3f ms", req_id, request.url.path, elapsed_ms)
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    # set header (milliseconds with 3 decimal places)
    response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.3f}"
    response.headers["X-Request-Id"] = req_id
    # log basic info (method, path, status, elapsed)
    logging.info("%s %s %s %.3fms req_id=%s",
                 request.method, request.url.path, response.status_code, elapsed_ms, req_id)
    return response


MODEL_PATH = Path("models/sqli_charngram_logreg.joblib")
if not MODEL_PATH.exists():
    raise RuntimeError("Model file not found")

model = load(MODEL_PATH)

class Item(BaseModel):
    text: str

def sanitize_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = "".join(ch for ch in s if ord(ch) >= 32 or ch in ("\n", "\t"))
    return s.strip()

@app.post("/score")
async def score(request: Request, item: Optional[Item] = None):
    """
    Accepts either JSON like {"text":"..."} (shows in docs)
    or raw text body (fallback).
    """
    # If FastAPI parsed JSON into `item`, use that (docs will show this)
    if item is not None and item.text:
        text = item.text
    else:
        # Fallback: raw body (works for text/plain or malformed JSON)
        raw = await request.body()
        if not raw:
            raise HTTPException(status_code=400, detail="No text provided")
        text = raw.decode("utf-8", errors="replace")

    text = sanitize_text(text)
    try:
        prob = float(model.predict_proba([text])[0][1])
        return {"attack_prob": prob, "label": int(prob >= 0.5)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
