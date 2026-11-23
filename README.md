# DataSentinel AI
### Autonomous AI-Powered Data Quality, Observability & Intelligence Platform

DataSentinel AI is an enterprise-grade autonomous data observability platform that acts as an autonomous AI Data Engineer. It combines statistical machine learning, Generative AI (Groq API / configurable LLM provider), multi-agent investigation workflows (LangGraph), and incident knowledge retrieval (RAG) to continuously monitor data pipelines, detect quality degradation and schema drift, isolate root causes, and recommend human-approved remediations.

---

## 🌟 Key Architecture & Capabilities

1. **Security & Cryptographic Hardening**:
   - Primary password hashing with **Argon2id** (RFC 9106, 64 MiB RAM, 3 iterations, 4 parallelism threads) with seamless backwards compatibility.
   - Strict stateless JWT Bearer token authentication with cryptographic expiration validation and signature pinning.
   - Role-Based Access Control (**RBAC**) strictly enforcing permission boundaries for `admin`, `analyst`, and `viewer` roles.
   - Content signature validation prohibiting disguised executable binaries (ELF, PE, Mach-O, scripts).
   - Strict path traversal prevention ensuring uploads and reads remain confined within authorized storage zones.

2. **Automated Data Ingestion & Immutability Guarantee**:
   - Secure ingestion of CSV, Excel (`.xlsx`, `.xls`), and JSON datasets.
   - SHA-256 cryptographic digest calculation and MIME type verification.
   - Configurable upload quota (100MB default).
   - **Zero In-Place Overwrites**: Original raw user datasets are strictly immutable.

3. **Deterministic Data Profiling & Transparent Scoring**:
   - Automated profiling of dataset dimensions, missing cells, duplicate rows, and column cardinalities.
   - Quantile distribution analysis and type inference.
   - Transparent, documented 100-point Data Quality Score based on penalized defect weights.

4. **Machine Learning Anomaly & Outlier Engine**:
   - Multi-dimensional anomaly detection using Scikit-Learn **Isolation Forest**.
   - Statistical outlier detection via Interquartile Range (IQR) fences and Z-score distributions.
   - Feature importance rankings and anomalous record inspector.

5. **Schema Drift & Data Drift Monitoring**:
   - Structural mutation tracking: added/removed columns, type conversions, nullability shifts.
   - Continuous feature drift detection via two-sample **Kolmogorov-Smirnov (KS) test** and **Population Stability Index (PSI)** with quantile binning.
   - Versioned schema evolution history.

6. **LangGraph Multi-Agent Investigation System**:
   - Stateful multi-agent workflow orchestrated through 6 specialized agents in a LangGraph `StateGraph`:
     - **Data Quality Agent**: Identifies quality score degradations and metric threshold failures.
     - **Anomaly Investigation Agent**: Analyzes multi-dimensional outlier clusters.
     - **Schema Analysis Agent**: Analyzes structural mutations against baseline schemas.
     - **Root Cause Analysis Agent**: Correlates findings to hypothesize pipeline failure root causes.
     - **Remediation Agent**: Proposes precise data healing actions.
     - **Report Generation Agent**: Formulates comprehensive markdown and JSON investigation dossiers.
   - High-fidelity deterministic local fallback when external LLM credentials are not provided.

7. **RAG Incident Knowledge Retrieval**:
   - Vector similarity search over past postmortems, proven remediation runbooks, and enterprise quality standards.
   - Transparent citation tracking (`Source: kb-rem-05`, `Source: kb-inc-104`).

8. **Human-in-the-Loop Remediation Engine**:
   - Preview proposed transformations with side-by-side Before/After record diffs.
   - Human review lifecycle (Pending, Approved, Rejected, Executed).
   - Transformations run strictly on cloned copies, generating versioned datasets with before/after audit records.

9. **Enterprise Management & Modern UI**:
   - Incident lifecycle management with severity scoring (CRITICAL, HIGH, MEDIUM, LOW) and timeline audit.
   - Modern React 18 + TypeScript + Vite + Tailwind CSS dashboard with interactive Recharts visualizations.
   - Authenticated PDF (ReportLab) and CSV dossier exports.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2, Argon2id (`argon2-cffi`), PostgreSQL 16 (Docker/Prod) / SQLite (Local dev), Uvicorn.
- **Machine Learning**: Scikit-learn, Pandas, NumPy, SciPy (KS-test, PSI, Isolation Forest).
- **Agentic AI & GenAI**: LangGraph, LangChain, Groq API (`llama-3.3-70b-versatile`), TF-IDF / Vector Search.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React, Axios.
- **Testing**: Pytest (17 automated unit, integration, and security tests).

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### 2. Local Backend Setup
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
- Backend API: `http://localhost:8000`
- Swagger Interactive Documentation: `http://localhost:8000/docs`

### 3. Local Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Frontend Application: `http://localhost:5173`

### 4. Docker & Containerized Production Deployment
```bash
docker compose up -d --build
```
- Frontend Application: `http://localhost:3000`
- Backend REST API: `http://localhost:8000`

### 5. Running Automated Tests
```bash
# Run complete test suite (17 tests: auth, ingestion, ML, drift, LangGraph, RAG, security)
python -m pytest backend/tests -v

# Run independent end-to-end verification harness
python backend/tests/verify_all.py
```

### 6. Sample Data Walkthrough
Pre-seeded synthetic business data is available in `backend/sample_data/`:
1. `customers_clean.csv`: Benchmark baseline dataset (clean records, proper types, zero nulls).
2. `customers_drifted.csv`: Drifted customer data (distribution shifts, null breaches, categorical anomalies).
3. `transactions_anomalous.json`: Transaction records with multi-dimensional numerical outliers.

---

## 📋 Repository Structure
```
DataSentinel AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI REST endpoints
│   │   ├── core/           # Database, security (Argon2id, JWT), exceptions, logging
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic data schemas
│   │   ├── services/       # Ingestion, profiling, ML, drift, RAG, remediation, reports
│   │   ├── agents/         # LangGraph 6-agent multi-agent investigation system
│   │   ├── config.py       # Pydantic settings & environment validation
│   │   └── main.py         # FastAPI application entrypoint
│   ├── data/               # Local data storage (uploads, remediated, RAG)
│   ├── sample_data/        # Realistic synthetic testing datasets
│   ├── tests/              # 17 automated tests (unit, integration, and security)
│   ├── requirements.txt    # Python requirements
│   ├── Dockerfile          # Backend production container
│   └── run.py              # Local server launcher
├── frontend/
│   ├── src/
│   │   ├── components/     # UI widgets, layout, navigation, charts, modals
│   │   ├── pages/          # 12 SaaS enterprise pages
│   │   ├── services/       # Axios API client
│   │   ├── types/          # TypeScript definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── nginx.conf          # Production Nginx reverse-proxy and SPA routing
│   └── Dockerfile          # Frontend production container
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── DEPLOYMENT.md
├── ARCHITECTURE.md
├── TASKS.md
├── PROGRESS.md
└── DEVELOPMENT_LOG.md
```
