
# SQL Injection (SQLi) Detector — NLP Starter Kit

**Purpose:** Defensive-only demonstration of detecting SQL injection patterns using character n‑gram TF‑IDF features with classical ML models (Logistic Regression & Random Forest). Includes a tiny FastAPI service for scoring.

> ⚠️ **Ethical use only.** This project is for research/education in defensive detection. It does **not** include exploit tooling. Follow your institution’s responsible use policy.

## Layout
```
sqli-detector/
├─ data/
├─ notebooks/
├─ models/
├─ app/
|  ├─ api_cors.py
│  ├─ api.py
│  └─ __init__.py
├─ train.py
├─ evaluate.py
├─ requirements.txt
├─ demo.html
└─ README.md
```

## Quick start
### 1) Create environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Train run(train.py)
```bash
python train.py
```
Saves:
- `models/sqli_charngram_logreg.joblib`
- `models/sqli_charngram_rf.joblib`

### 3)  Evaluate (optional) run(evaluate.py)
```bash
python evaluate.py
```
Saves:
- `models/confusion_matrix.png`
- `models/pr_curve.png`

### 4) Run API
```bash
uvicorn app.api:app --reload --port 8000
```
Note:-

Here you can you just go to your browser and type http://127.0.0.1:8000/docs
click on post session and then click on "try it out" you can you type an "SQL injection" 

example Input :-
{
  "text": "' OR 1=1 --"
}

Output:-	
Response body

{
  "attack_prob": 0.9286200428856001, # this is the probability that shows it is likely to be an sql injection
  "label": 1
}

Health:
```bash
curl http://127.0.0.1:8000/health
```
Score:
```bash
curl -X POST http://127.0.0.1:8000/score   -H "Content-Type: application/json"   -d "{"text":"' OR 1=1 --"}"
```


use:- 
Ctrl + C to stop the server 


### How do we run the demo website
- Run the demo.html file locally
- run the uvicorn server for api_cors, Here, is the code ```bash uvicorn app.api_cors:app --reload --port 8000 ```

### Notes
- Keep punctuation/case (do **not** lowercase).
- Prefer char n‑grams (3–5) for obfuscation robustness.
- Prioritize recall/F1 for the attack class (tune threshold as needed).
- For stronger validation, split by **data source** when available.

### Next steps
- Compare with Linear SVM or Gradient Boosting.
- Add heuristic features (quote/paren imbalance, comment tokens).
- Extend to XSS/command injection using same pipeline.


Note:-
if you need a demo in an actual webapplication then start the server with this command instead "uvicorn app.api_cors:app --reload --port 8000" and execute the demo.html seperately and check if it's working 

use:- 
Ctrl + C to stop the server 

#Issues that are needed to be addressed 
 currently the dataset is small we need to use a bigger one (becarefull while handling them you yourself might get infected with sqlinjections )
