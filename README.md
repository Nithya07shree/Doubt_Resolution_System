# Multi-Agent AI Doubt Resolution System

A production-grade, highly resilient **Multi-Agent Doubt Resolution System** that takes complex academic student queries, processes them sequentially through five specialized AI agents, audits overall output quality with an automatic internal retry loop, computes high-resolution word-level text differences, and logs every resolution session to SQLite. Serves a rich, modern, glassmorphic Next.js App Router workspace with a visual diff viewer, responsive loader, and side-navigation query history log.

---

## System Architecture

The workflow consists of five sequential agents communicating structured inputs and outputs, verified by an active Quality Validator before saving and rendering results:

```
[Student query input]
         │
         ▼
 ┌──────────────┐
 │ Sanitization │ (HTML stripping & prompt injection check)
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ IntentAgent  │ (Profiles subject topic, skill level, and intent style)
 └──────┬───────┘
        │
        ▼
 ┌──────────────────┐
 │ ExplanationAgent │ (Authers exhaustive, detailed academic answer)
 └──────┬───────────┘
        │
        ▼
 ┌─────────────────────┐
 │ SimplificationAgent │ (Translates academic answer into physical analogies)
 └──────┬──────────────┘
        │
        ▼
 ┌──────────────┐
 │ ExampleAgent │ (Crafts concrete, actionable step-by-step examples)
 └──────┬───────┘
        │
        ▼
 ┌─────────────────┐
 │ ValidationAgent │ ◄───────┐  [If valid=False, triggers feedback loop]
 └──────┬──────────┘         │  (Max exactly ONE correction retry loop)
        │ ──[invalid]────────┘
        │
    [valid]
        │
        ▼
 ┌─────────────────┐
 │   Diff Engine   │ (Computes word additions/deletions via difflib)
 └──────┬──────────┘
        │
        ▼
 ┌─────────────────┐
 │ SQLite Database │ (Writes session payload, tokens, and latency thread-safely)
 └──────┬──────────┘
        │
        ▼
 ┌─────────────────┐
 │ Next.js Front   │ (Renders active loaders, PR-style diffs, and historical queries)
 └─────────────────┘
```

---

## Project Layout

```
doubt_resolution_system/
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI routing, CORS, sanitization
│   │   ├── config.py               # Pydantic environment configurations
│   │   ├── database.py             # SQLite connection pools & session handling
│   │   ├── logger.py               # Structured console & timestamped file logging
│   │   ├── models.py               # SQLAlchemy db tables
│   │   ├── schemas.py              # Pydantic schema validation models
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py       # OpenAI initialization & tenacity retries
│   │   │   ├── intent_agent.py     # Classifies topics & skill levels
│   │   │   ├── explanation_agent.py# RIGOROUS deep academic prose
│   │   │   ├── simplification_agent.py # Translates concepts into relatable analogies
│   │   │   ├── example_agent.py    # Actions details using code/math
│   │   │   └── validation_agent.py # Quality assurance evaluation report
│   │   └── utils/
│   │       └── diff_engine.py      # word-level difference calculations
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── package.json
    ├── tailwind.config.js
    ├── postcss.config.js
    └── app/
        ├── layout.tsx
        ├── globals.css
        ├── page.tsx                # Sidebar history & workflow loaders workspace
        └── components/
            ├── AgentCard.tsx       # Elegant cards with latency & copy options
            └── DiffViewer.tsx      # Renders red/green pull-request-style highlights
```

---

## Setup & Launch Instructions

### Prerequisites
- Python 3.9+
- Node.js 18.0+

---

### Step 1: Configure & Start Backend Server

1. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```

2. **Create a Virtual Environment & Activate It**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
     
   - **macOS/Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Configs**:
   Copy `.env.example` to `.env` and enter your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   DATABASE_URL=sqlite:///./doubt_resolution.db
   ALLOWED_ORIGINS=["http://localhost:3000"]
   ```

5. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *The API will boot up on `http://127.0.0.1:8000`. Documentation will be accessible at `http://127.0.0.1:8000/docs`.*

---

### Step 2: Configure & Start Frontend Dashboard

1. **Navigate to the Frontend Directory**:
   Open a new terminal window:
   ```bash
   cd frontend
   ```

2. **Install Node Packages**:
   ```bash
   npm install
   ```

3. **Launch the Next.js Dev Server**:
   ```bash
   npm run dev
   ```
   *The beautiful dashboard workspace will open on `http://localhost:3000`.*

---

## Reliability & Resilience Details

1. **Tenacity Transient Retries**:
   `BaseAgent` is equipped with automatic exponential backoff retries when interfacing with OpenAI's API:
   - Activates specifically on `RateLimitError` and `APIConnectionError`.
   - Starts at 1s wait, doubling up to a maximum of 3 attempts.
2. **Graceful Pipeline Fallbacks**:
   If network errors persist or keys are configured incorrectly, the base execution handles exceptions safely. Rather than crashing the entire pipeline, it captures a detailed stack trace into `backend/log-{timestamp}.log` and returns a friendly pedagogical fallback message, keeping the system online.
3. **Structured Validation Retry Loop**:
   When generating answers, `ValidationAgent` evaluates content against completeness standards. If validation fails (valid = false), the system initiates exactly ONE internal feedback cycle, appending constructive criticism to correct explanations, simplifications, and examples dynamically before proceeding.
4. **Input Sanitization**:
   Strict regex logic parses and neutralizes typical prompt injections, escaping HTML tags to prevent cross-site scripting (XSS) at the router level.
