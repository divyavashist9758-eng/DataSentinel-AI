# DataSentinel AI: Architecture Design

## 1. System Overview
DataSentinel AI is an enterprise-grade autonomous data quality, observability, and intelligence platform. It acts as an autonomous AI Data Engineer that ingests datasets, continuously profiles data health, detects statistical anomalies and feature drift, tracks schema changes across versions, conducts multi-agent root cause investigations using LangGraph, retrieves historical context via RAG, and provides human-in-the-loop approved remediations executed on non-destructive data copies with full audit trails.

```
                  ┌───────────────────────────────────────────────┐
                  │                 React Frontend                │
                  │   (Vite + TypeScript + Tailwind + Recharts)   │
                  └───────────────────────┬───────────────────────┘
                                          │ REST / JSON (JWT Bearer)
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │             FastAPI Backend Core              │
                  │   (Argon2id, RBAC, Ingestion, Profiling)      │
                  └───────┬──────────────┬──────────────┬─────────┘
                          │              │              │
        ┌─────────────────┴─┐     ┌──────┴──────┐     ┌─┴────────────────┐
        ▼                   ▼     ▼             ▼     ▼                  ▼
┌───────────────┐   ┌───────────────┐   ┌─────────────────┐   ┌───────────────┐
│ Machine Learn.│   │  LangGraph    │   │ RAG Incident    │   │ Non-Destruct. │
│  - IsolationF.│   │  Multi-Agent  │   │ Knowledge Store │   │ Remediation   │
│  - KS-Test    │   │  - Quality    │   │ (Vector/Cosine  │   │  - Preview    │
│  - PSI Drift  │   │  - Anomaly    │   │  Similarity)    │   │  - Approvals  │
│  - Outlier IQR│   │  - Schema     │   └─────────────────┘   │  - Cloned V2  │
└───────────────┘   │  - Root Cause │                         └───────────────┘
                    │  - Remediation│
                    │  - Report Gen │
                    └───────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│ PostgreSQL 16 /  │            │ Storage / Data   │
│ SQLite (Local)   │            │ (Raw & Cleaned)  │
└──────────────────┘            └──────────────────┘
```

## 2. Core Modules Architecture

### Module A: Security & Access Control Layer
- **Cryptographic Hashing**: **Argon2id** (RFC 9106, 64 MiB RAM, 3 iterations, 4 parallelism threads) using `argon2-cffi` with backwards-compatible legacy salted SHA-256 support.
- **Authentication**: Stateless JSON Web Tokens (**JWT**) with `HS256` signature verification, cryptographic `exp` checks, and subject validation.
- **Role-Based Access Control (RBAC)**: Enforces role boundaries:
  - `admin`: Full system administrative control.
  - `analyst`: Can upload datasets, trigger investigations, update incidents, and execute approved remediations.
  - `viewer`: Read-only access to datasets, profiles, metrics, and reports; prohibited from state-modifying actions.
- **Path Traversal & Storage Confinement**: Safe filename sanitization and `os.path.commonpath` confinement preventing arbitrary file access.
- **Magic Bytes Validation**: Rejects disguised executable binaries (Linux ELF, Windows PE, Mach-O, shell scripts).

### Module B: Data Ingestion & Storage
- **File Handlers**: CSV, Excel (`.xlsx`, `.xls`), and JSON.
- **Validation**: Enforces MIME types, file size ceilings (100MB default), and SHA-256 integrity verification.
- **Dataset Versioning & Immutability**: All original raw files are strictly immutable; version 1 remains intact permanently.

### Module C: Automated Data Profiling & Quality Scoring
- Deterministic profiling computing row/column count, duplicate row count, null percentages, data types, distinct value cardinalities, and numerical quantiles.
- **Quality Score Engine**: A transparent 100-point scoring algorithm penalizing missingness, duplicates, type inconsistencies, and outlier density:
  $$Q = \max(0, 100 - (w_1 \cdot P_{null} + w_2 \cdot P_{dup} + w_3 \cdot P_{type} + w_4 \cdot P_{outlier}))$$

### Module D: Machine Learning & Anomaly Detection
- **Isolation Forest**: Multi-dimensional unsupervised anomaly detection to pinpoint anomalous rows and feature oddities.
- **Statistical Outlier Detection**: IQR fences and Z-score distributions.
- **Data Drift Detection**:
  - Two-sample Kolmogorov-Smirnov (KS) test ($p$-value threshold $< 0.05$).
  - Population Stability Index (PSI) with standard quantile binning ($\text{PSI} > 0.25$ indicates significant drift).
- **Schema Drift Comparator**: Detects added/removed columns, type conversions, nullability shifts, and unexpected categories.

### Module E: LangGraph Multi-Agent Investigation System
- Stateful `StateGraph` workflow orchestrating 6 specialized agents:
  1. Data Quality Agent
  2. Anomaly Investigation Agent
  3. Schema Analysis Agent
  4. Root Cause Analysis Agent
  5. Remediation Agent
  6. Report Generation Agent
- External LLM provider: Groq API (`llama-3.3-70b-versatile`) with seamless deterministic intelligent local fallback.

### Module F: RAG Incident Knowledge Retrieval
- Semantic search across pre-seeded industry rules, historical postmortems, and remediation playbooks with traceable source citations.

### Module G: Human-in-the-Loop Remediation Engine
- Side-by-side Before/After preview diff on real records with estimated score improvement.
- Reviewer approval/rejection lifecycle with audit attribution.
- **Safe Execution**: Clones the dataset into a new versioned copy, executes the transformation, and triggers automated post-remediation profiling.

### Module H: PDF & CSV Report Generation
- ReportLab-powered PDF dossier generator with executive synthesis and agent traces.
- CSV trace export for programmatic auditing and reporting.
