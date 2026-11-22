# DataSentinel AI: Architecture Design

## 1. System Overview
DataSentinel AI is an enterprise-grade autonomous data quality, observability, and intelligence platform. It acts as an autonomous AI Data Engineer that ingests datasets, continuously profiles data health, detects statistical anomalies and feature drift, tracks schema changes across versions, conducts multi-agent root cause investigations using LangGraph, retrieves historical context via RAG, and provides human-in-the-loop approved remediations executed on non-destructive data copies with full audit trails.

```
                  ┌───────────────────────────────────────────────┐
                  │                 React Frontend                │
                  │   (Vite + TypeScript + Tailwind + Recharts)   │
                  └───────────────────────┬───────────────────────┘
                                          │ REST / JSON
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │             FastAPI Backend Core              │
                  │   (Auth, Ingestion, Profiling, Orchestration) │
                  └───────┬──────────────┬──────────────┬─────────┘
                          │              │              │
        ┌─────────────────┴─┐     ┌──────┴──────┐     ┌─┴────────────────┐
        ▼                   ▼     ▼             ▼     ▼                  ▼
┌───────────────┐   ┌───────────────┐   ┌─────────────────┐   ┌───────────────┐
│ Machine Learn.│   │  LangGraph    │   │ RAG Incident    │   │ Non-Destruct. │
│  - IsolationF.│   │  Multi-Agent  │   │ Knowledge Store │   │ Remediation   │
│  - KS-Test    │   │  - Quality    │   │ (Chroma/FAISS + │   │  - Preview    │
│  - PSI Drift  │   │  - Anomaly    │   │  MiniLM Vector) │   │  - Approvals  │
│  - Outlier IQR│   │  - Schema     │   └─────────────────┘   │  - New Copy   │
└───────────────┘   │  - Root Cause │                         └───────────────┘
                    │  - Remediation│
                    │  - Report Gen │
                    └───────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│ PostgreSQL /     │            │ Storage / Data   │
│ SQLite (Local)   │            │ (Raw & Cleaned)  │
└──────────────────┘            └──────────────────┘
```

## 2. Core Modules Architecture

### Module A: Data Ingestion & Storage
- **File Handlers**: CSV, Excel (`.xlsx`, `.xls`), JSON, and Database connection strings.
- **Validation**: Enforces MIME types, file size ceilings (configurable default 100MB), schema validity, and safe storage hashing.
- **Dataset Versioning**: Tracks dataset versions (`v1`, `v2`, `v3`) to monitor drift and schema evolution over time.

### Module B: Automated Data Profiling & Quality Scoring
- Deterministic profiling computing row/column count, duplicate row count, null percentages, data types, distinct value cardinalities, and numerical quantiles.
- **Quality Score Engine**: A transparent 100-point scoring algorithm penalizing:
  - Nulls ($P_{null}$): weighted by column critical thresholds.
  - Duplicates ($P_{dup}$): proportional to duplicate row ratio.
  - Data Type Inconsistencies ($P_{type}$).
  - Outlier density ($P_{outlier}$).
  $$Q = \max(0, 100 - (w_1 \cdot P_{null} + w_2 \cdot P_{dup} + w_3 \cdot P_{type} + w_4 \cdot P_{outlier}))$$

### Module C: Machine Learning & Anomaly Detection
- **Isolation Forest**: Multidimensional unsupervised anomaly detection with configurable contamination rates to pinpoint anomalous rows and multi-feature oddities.
- **Statistical Outlier Detection**: IQR (Interquartile Range) fences ($Q1 - 1.5\text{IQR}$, $Q3 + 1.5\text{IQR}$) and Z-score testing ($|z| > 3.0$) for numerical features.
- **Data Drift Detection**:
  - Two-sample Kolmogorov-Smirnov (KS) test for continuous numerical distributions ($p$-value threshold $< 0.05$).
  - Population Stability Index (PSI) with standard binning ($\text{PSI} > 0.25$ indicates significant drift).
  - Categorical chi-square / frequency deviation detection.

### Module D: Schema Drift Detection
- Compares column structure across dataset versions or historical schema baselines:
  - Added columns
  - Removed columns
  - Data type changes (e.g. `INTEGER` to `VARCHAR`)
  - Nullability threshold breaches (previously non-null columns now having missing data)
  - New unexpected categorical categories.

### Module E: LangGraph Agentic AI Investigation System
- Multi-step stateful investigation workflow orchestrated with LangGraph:
  1. **Data Quality Agent**: Analyzes overall quality metrics and flags SLA breaches.
  2. **Anomaly Investigation Agent**: Digs into flagged anomalous rows and feature outliers.
  3. **Schema Analysis Agent**: Analyzes structural mutations against baseline schemas.
  4. **Root Cause Analysis Agent**: Correlates quality, anomaly, and schema findings with temporal patterns to hypothesize root causes.
  5. **Remediation Agent**: Synthesizes actionable, non-destructive remediation transformations.
  6. **Report Generation Agent**: Synthesizes the end-to-end investigation dossier with confidence scores and executive summaries.
- **LLM Fallback & Resilience**: Dynamically connects to Groq API (or OpenAI/compatible), with robust structured fallback heuristics ensuring complete trace generation even without external API credentials.

### Module F: RAG Knowledge System
- Indexes past incident postmortems, proven remediation recipes, and company data quality guidelines.
- Vector store with cosine similarity retrieval over semantic embeddings.
- Injects verified historical incident precedents into investigation prompts to provide exact citations (`source: incident-104`).

### Module G: AI Remediation Engine (Human-in-the-Loop)
- Generates precise code/data transformation proposals for:
  - Missing value imputation (mean, median, mode, KNN, constant, drop)
  - Duplicate deduplication strategies
  - Type casting & invalid data cleansing
  - Outlier clipping or isolation
- **Zero In-Place Overwrites**: Original raw dataset remains strictly read-only.
- **Approval Workflow**: Pending $\rightarrow$ Approved/Rejected $\rightarrow$ Executed.
- Generates a newly versioned remediated dataset with before-and-after diff metrics and complete audit logging.

### Module H & I: Incidents, Analytics & Reporting
- Comprehensive lifecycle tracking (OPEN, INVESTIGATING, REMEDIATED, RESOLVED).
- Severity calculation (CRITICAL, HIGH, MEDIUM, LOW) based on impacted records and business criticality.
- PDF and CSV reporting export engine.
