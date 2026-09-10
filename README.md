# 🤖 AI-Powered SQL Query Generator & Executor

An intelligent full-stack SQL query generation, execution, and explanation platform powered by **Google Gemini AI**, **FastAPI**, **Streamlit**, and **SQLAlchemy**.

---

## ✨ Features

- 🧠 **Natural Language to SQL**: Converts everyday English questions into optimized SQLite queries.
- 💡 **AI Query Explanation**: Provides step-by-step plain-English explanations of how the SQL query works.
- 🚀 **Interactive Execution**: Runs queries safely and renders results in a Pandas DataFrame table.
- 📥 **CSV Export**: Export and download query result sets in CSV format with a single click.
- 📂 **Custom Database Upload**: Upload your own SQLite database (`.db` or `.sqlite`) and hot-swap connections instantly.
- 🔍 **Schema Exploration**: Browse available tables, view column schemas, and preview the first 5 rows of any table.
- 📜 **Rolling Query History**: Retains the last 5 executed queries in session state for quick re-execution.
- 🛡️ **Security Guardrails**: Enforces read-only operations (`SELECT`, `WITH`, `PRAGMA`) and blocks destructive commands.

---

## 🏗️ Architecture & Workflows

For an in-depth architectural breakdown and sequence diagrams, see:
👉 **[ARCHITECTURE_AND_WORKFLOW.md](file:///Users/harshpatel/Desktop/AI%20Powered%20SQL%20query%20Generator/ARCHITECTURE_AND_WORKFLOW.md)**

---

## 📁 Project Structure

```
├── app.py                     # FastAPI backend REST API routes
├── ui.py                      # Streamlit interactive frontend application
├── query_generator.py         # Gemini AI query generation, parsing & execution logic
├── database.py                # Database connection management & schema reflection
├── chinook.db                 # Default sample SQLite database (Music store)
├── requirements.txt           # Project dependencies
├── .env                       # Environment configuration (API keys & DB path)
└── ARCHITECTURE_AND_WORKFLOW.md # Full architecture & workflow documentation
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create or verify `.env` in the root directory:
```env
GEMINI_API_KEY="your-google-gemini-api-key"
SQLITE_DB_PATH="chinook.db"
```

### 3. Run FastAPI Backend
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Swagger API docs: `http://127.0.0.1:8000/docs`

### 4. Run Streamlit UI
In another terminal:
```bash
streamlit run ui.py
```
App will open at: `http://localhost:8501`
