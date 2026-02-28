# 🚀 AI Resume Screener

An intelligent resume screening system that uses **Gemini AI** for data extraction, **ChromaDB** for semantic search, and a **hybrid scoring algorithm** to rank candidates against job descriptions.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?logo=google&logoColor=white)

---

## ✨ Features

- **PDF Resume Parsing** — Extracts text from PDF resumes with magic-byte validation for security
- **AI-Powered Extraction** — Uses Gemini 2.5 Flash to extract structured data (name, skills, experience)
- **Vector Search** — Stores resume embeddings in ChromaDB for semantic matching
- **Hybrid Scoring Algorithm** — Combines semantic similarity (40%) + skill match (40%) + experience (20%)
- **Bulk Upload** — Ingest multiple resumes in a single API call
- **Beautiful Dashboard** — Streamlit UI with real-time progress, candidate cards, and CSV export

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Streamlit   │────▶│   FastAPI     │────▶│  Gemini AI    │
│  Frontend    │     │   Backend     │     │  (Extraction) │
│  (app.py)    │◀────│  (main.py)    │     └───────────────┘
└─────────────┘     │               │
                    │               │────▶┌───────────────┐
                    │               │     │   ChromaDB     │
                    │               │◀────│ (Vector Store) │
                    └──────────────┘     └───────────────┘
```

| File | Role |
|---|---|
| `main.py` | FastAPI endpoints (`/upload/`, `/upload-bulk/`, `/match/`) |
| `app.py` | Streamlit dashboard UI |
| `gemini_service.py` | Gemini AI structured data extraction with retry logic |
| `embedding_service.py` | ChromaDB vector storage & semantic search |
| `ranking_service.py` | Hybrid scoring algorithm |
| `pdf_parser.py` | PDF validation & text cleaning |
| `schemas.py` | Pydantic models (`ExtractedResume`, `JobDescription`) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repo
git clone https://github.com/THEN01EXPLORER/ai-resume-screener.git
cd ai-resume-screener

# Create virtual environment
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### Running

Open **two terminals**:

```bash
# Terminal 1 — Start the FastAPI backend
uvicorn main:app --reload

# Terminal 2 — Start the Streamlit frontend
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload/` | Upload a single PDF resume |
| `POST` | `/upload-bulk/` | Upload multiple PDF resumes |
| `POST` | `/match/` | Rank all resumes against a job description |

---

## 🧮 Scoring Algorithm

The hybrid score is calculated as:

```
Final Score = (Semantic Similarity × 0.40) + (Skill Match × 0.40) + (Experience × 0.20)
```

- **Semantic Similarity** — Cosine distance from ChromaDB, converted to similarity
- **Skill Match** — Percentage of required skills found in the resume
- **Experience** — Full marks if meets minimum, 50% penalty otherwise

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **AI**: Google Gemini 2.5 Flash
- **Vector DB**: ChromaDB with SentenceTransformer (`all-MiniLM-L6-v2`)
- **PDF Parsing**: pdfplumber
- **Data Validation**: Pydantic

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
