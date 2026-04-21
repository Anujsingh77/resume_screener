# AI Resume Screener — Project

A full-stack AI-powered resume screening tool built with Python (Flask), NLP (spaCy + scikit-learn), and a clean HTML/CSS/JS frontend.

---

## Project Structure

```
resume_screener/
├── app.py                  ← Flask backend (main entry point)
├── requirements.txt        ← All Python dependencies
├── templates/
│   └── index.html          ← Frontend HTML (Jinja2 template)
├── static/
│   ├── css/style.css       ← Styling
│   └── js/main.js          ← Frontend JS (form + results rendering)
├── utils/
│   ├── pdf_extractor.py    ← Extracts text from uploaded PDFs
│   ├── nlp_processor.py    ← Skill extraction + TF-IDF scoring
│   └── scorer.py           ← Scoring algorithm + reasoning
└── uploads/                ← Temp folder for uploaded PDFs (auto-created)
```

---

## Step-by-Step Setup

### Step 1 — Install Python 3.10+
Download from https://python.org. Make sure to check "Add Python to PATH" on Windows.

Verify:
```
python --version
```

---

### Step 2 — Create a virtual environment
```bash
cd resume_screener
python -m venv venv
```

Activate it:
- Windows:  `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

---

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

This installs Flask, PyMuPDF, scikit-learn, spaCy, and everything else.

---

### Step 4 — Download the spaCy language model
```bash
python -m spacy download en_core_web_sm
```

This gives spaCy the English NLP model for skill extraction.

---

### Step 5 — Run the app
```bash
python app.py
```

Open your browser and go to: http://127.0.0.1:5000
## DEMO: https://resume-screener-j3x0.onrender.com/

---

## How It Works (for your resume report)

### 1. PDF Upload & Text Extraction
- User uploads one or more PDF resumes via the web form
- `pdf_extractor.py` uses **PyMuPDF** to extract raw text from each page
- Falls back to **pdfplumber** if PyMuPDF fails

### 2. Skill Extraction (NLP)
- `nlp_processor.py` runs two methods:
  - **Keyword matching**: Scans for 80+ known tech/soft skills using regex
  - **spaCy noun chunks**: Uses the `en_core_web_sm` model to extract noun phrases and match them against the skill list
- Same extraction runs on the job description to get "required skills"

### 3. TF-IDF Similarity (ML)
- Both the job description and the resume text are converted into **TF-IDF vectors** using scikit-learn
- **Cosine similarity** is computed between the two vectors
- This measures how much the resume content overlaps with the JD at a document level

### 4. Candidate Scoring
- `scorer.py` combines three signals:
  - **Skill overlap** (50% weight) — % of JD skills found in resume
  - **TF-IDF similarity** (35% weight) — document-level content match
  - **Experience heuristic** (15% weight) — years detected via regex
- Final score: 0–100
- Verdict: Strong fit / Good fit / Partial fit / Weak fit

### 5. Ranking & Display
- All candidates are sorted by score (highest first)
- Results show: score bar, matched/missing skills, education, experience, strengths, gaps

---

## Technologies Used

| Layer | Tool | Purpose |
|-------|------|---------|
| Backend | Flask | Web server + API routes |
| PDF parsing | PyMuPDF / pdfplumber | Extract text from PDFs |
| NLP | spaCy | Skill extraction via noun chunks |
| ML | scikit-learn TF-IDF | Document similarity scoring |
| Data | NumPy, Pandas | Numerical processing |
| Frontend | HTML/CSS/JS | User interface |

---

## Possible Extensions (for extra marks)

- Add **BERT embeddings** (sentence-transformers) for semantic skill matching
- Export results as **CSV/Excel** using Pandas
- Add **login + database** (SQLite/PostgreSQL) to store screening history
- Deploy to **Render / Railway / Heroku** for a live URL
- Integrate **Anthropic Claude API** for AI-generated candidate summaries

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` |
| `OSError: [E050] Can't find model 'en_core_web_sm'` | Run `python -m spacy download en_core_web_sm` |
| PDF uploads not working | Make sure files are valid PDFs, not scanned images without OCR |
| Port already in use | Run `python app.py` and change port: `app.run(port=5001)` |
