# DataSentinel AI
### Autonomous AI-Powered Data Quality, Observability & Intelligence Platform

DataSentinel AI is an enterprise-grade autonomous data observability platform that acts as an autonomous AI Data Engineer. It combines statistical machine learning, Generative AI (Groq API / configurable LLM provider), multi-agent investigation workflows (LangGraph), and incident knowledge retrieval (RAG) to continuously monitor data pipelines, detect quality degradation and schema drift, isolate root causes, and recommend human-approved remediations.

---

## 🌟 Key Features

1. **Automated Data Ingestion & Storage**:
   - Ingestion of CSV, Excel (`.xlsx`, `.xls`), and JSON datasets.
   - Database connection inspection.
   - SHA-256 integrity validation, MIME verification, and configurable file size limits.
   - Non-destructive immutable raw storage.

2. **Deterministic Data Profiling & Transparent Scoring**:
   - Automated profiling of dataset dimensions, missing values, duplicates, and cardinality.
   - Quantile distribution and data type inference.
   - Transparent, documented 100-point Data Quality Score based on penalized defect weights.

3. **Machine Learning Anomaly & Outlier Engine**:
   - Multi-dimensional anomaly detection using Scikit-Learn **Isolation Forest**.
   - Statistical outlier detection via Interquartile Range (IQR) fences and Z-score distributions.
   - Baseline dataset comparison with anomaly scoring breakdowns.

4. **Schema Drift & Data Drift Monitoring**:
   - Structural mutation tracking: added/removed columns, type conversions, nullability shifts.
   - Continuous feature drift detection via two-sample **Kolmogorov-Smirnov (KS) test** and **Population Stability Index (PSI)**.
   - Versioned schema evolution history.

5. **LangGraph Multi-Agent Investigation System**:
   - Multi-step stateful investigation orchestrated through 6 specialized agents:
     - **Data Quality Agent**: Identifies quality score degradations and metric threshold failures.
     - **Anomaly Investigation Agent**: Analyzes multi-dimensional outlier clusters.
     - **Schema Analysis Agent**: Analyzes structural mutations against baseline schemas.
     - **Root Cause Analysis Agent**: Correlates findings to hypothesize pipeline failure root causes.
     - **Remediation Agent**: Proposes precise data healing actions.
     - **Report Generation Agent**: Formulates comprehensive markdown and JSON investigation dossiers.
   - High-fidelity deterministic local fallback when external LLM credentials are not provided.

6. **RAG Knowledge System**:
   - Vector similarity search over past postmortems, proven remediation runbooks, and enterprise quality standards.
   - Transparent citation tracking (`source: incident-104`).

7. **Human-in-the-Loop Remediation Engine**:
   - Preview proposed transformations (imputation, deduplication, type casting, outlier bounding).
   - Human approval/rejection lifecycle.
   - **Zero In-Place Overwrites**: Transformations run strictly on cloned copies, generating versioned datasets with before/after audit records.

8. **Enterprise Management & Modern UI**:
   - Incident lifecycle management with severity scoring (CRITICAL, HIGH, MEDIUM, LOW).
   - Modern React + TypeScript + Vite + Tailwind CSS dashboard with interactive Recharts visualizations.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Pydantic, PostgreSQL (Docker/Prod) / SQLite (Local dev), Uvicorn.
- **Machine Learning**: Scikit-learn, Pandas, NumPy, SciPy (KS-test, PSI, Isolation Forest).
- **Agentic AI & GenAI**: LangGraph, LangChain, Groq API (`llama-3.3-70b-versatile`), ChromaDB / Vector Search.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React, Axios.
- **Testing**: Pytest, HTTPX test client.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Clone or open repository
cd "DataSentinel AI"

# Copy environment variables
cp .env.example .env

# Install backend dependencies
pip install -r backend/requirements.txt

# Run backend server
python backend/run.py
```
Backend API will be running at `http://localhost:8000`
Interactive Swagger Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at `http://localhost:5173`

### 4. Running Automated Tests
```bash
pytest backend/tests -v
```

---

## 📋 Repository Structure
```
DataSentinel AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI REST endpoints
│   │   ├── core/           # Database, security, exceptions, logging
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic data schemas
│   │   ├── services/       # Business logic (ingestion, ML, drift, RAG, etc.)
│   │   ├── agents/         # LangGraph multi-agent investigation system
│   │   ├── config.py       # Pydantic settings
│   │   └── main.py         # FastAPI application entrypoint
│   ├── data/               # Local data storage (uploads, remediated, RAG)
│   ├── sample_data/        # Realistic synthetic testing datasets
│   ├── tests/              # Automated pytest test suite
│   ├── requirements.txt    # Python requirements
│   ├── Dockerfile          # Backend container file
│   └── run.py              # Local server launcher
├── frontend/
│   ├── src/
│   │   ├── components/     # UI widgets, layout, navigation, charts
│   │   ├── pages/          # 12 SaaS enterprise pages
│   │   ├── services/       # Axios API client
│   │   ├── types/          # TypeScript definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml
├── .env.example
├── ARCHITECTURE.md
├── TASKS.md
├── PROGRESS.md
└── DEVELOPMENT_LOG.md
```

---

## 🔒 Security & Data Integrity
- Passwords hashed using cryptographically secure salted SHA-256.
- Strict MIME type and SHA-256 verification on dataset uploads.
- Original user files are never modified in-place; all remediations generate cloned, versioned datasets.
- Full audit log recorded for every user action and remediation execution.
