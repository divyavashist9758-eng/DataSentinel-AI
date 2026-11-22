# DataSentinel AI: Development Log

## 2026-11-22 - Session Initial Setup & Architecture

### Environment Analysis
- Detected Python 3.13.14, Node v26.13.0, npm 11.20.0, Git 2.53.0.
- Docker command is not available in current host path (`docker: command not found`).
- Decision: Provide complete Dockerfiles and `docker-compose.yml` for containerized deployment, while implementing dual-mode database support (PostgreSQL for containerized/production setups, with zero-configuration SQLite support for immediate out-of-the-box local developer execution and unit testing).
- Disk Space: Detected low free space on C:\ (~60MB), while D:\ has ~136GB. Cleaned `C:\Users\divya\AppData\Local\pip\cache` to immediately recover 1.39 GB of free space.
- Pip flag: Using `--no-cache-dir` on pip installations to preserve host storage.

### Architectural Decisions
1. **Hybrid LLM Provider Architecture**:
   - Primary: Groq API (`llama-3.3-70b-versatile` or `llama-3.1-8b-instant`) / OpenAI compatible endpoint.
   - Deterministic Fallback: When no API key is configured or when rate limited, the system executes high-fidelity deterministic analytical agents so the entire LangGraph investigation graph runs smoothly and reliably without halting the platform.
2. **Non-Destructive Remediation**:
   - Original user uploads are strictly immutably stored with SHA-256 hashes.
   - Any approved remediation creates an audited, newly versioned dataset copy with before-and-after metric comparisons.
3. **Data Profiling & ML Detection**:
   - Automated profiling evaluates null rates, unique cardinalities, distribution quantiles, and computes a standardized 100-point Data Quality Score.
   - Isolation Forest detects multi-column anomalous records with transparent anomaly score metrics.
   - Statistical two-sample Kolmogorov-Smirnov (KS) test and Population Stability Index (PSI) quantify numerical feature drift.
