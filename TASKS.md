# DataSentinel AI: Task Master & Work Breakdown Structure

- [ ] **Phase 1: Environment & Project Setup**
  - [x] Inspect Python, Node, Git, Docker environment
  - [x] Install core backend dependencies (FastAPI, SQLAlchemy, Pandas, Scikit-learn, LangGraph, Groq, etc.)
  - [x] Create project architecture and continuity docs (ARCHITECTURE.md, TASKS.md, PROGRESS.md, DEVELOPMENT_LOG.md)
  - [ ] Configure environment variables & .gitignore

- [ ] **Phase 2: Backend Architecture & Database Models**
  - [ ] Implement database session manager with PostgreSQL & SQLite dual support
  - [ ] Create SQLAlchemy relational models (User, Dataset, Version, Schema, Profiling, Anomaly, Drift, Investigation, Incident, Remediation, AuditLog)
  - [ ] Implement Pydantic validation schemas
  - [ ] Build Authentication & Authorization (JWT tokens, password hashing, role enforcement)
  - [ ] Setup structured logging, custom error handling, and API router framework

- [ ] **Phase 3: Data Ingestion, Profiling & ML Detection Engine**
  - [ ] Implement File Ingestion Service (CSV, Excel, JSON, file hashing, size checks, storage)
  - [ ] Implement Automated Data Profiler (type inference, null counts, cardinalities, quantile summaries, 100-point quality score calculation)
  - [ ] Implement ML Engine: Isolation Forest anomaly detection for multidimensional outlier detection
  - [ ] Implement Statistical Outlier Detection (IQR fences, Z-scores)
  - [ ] Build baseline vs current dataset comparison utilities

- [ ] **Phase 4: Schema Drift & Historical Monitoring**
  - [ ] Implement Schema Comparator (added, removed, type change, nullability shift, categorical drift)
  - [ ] Implement Statistical Data Drift Detector (Two-sample KS test, Population Stability Index (PSI))
  - [ ] Implement schema version history tracking

- [ ] **Phase 5: LangGraph Multi-Agent Investigation System**
  - [ ] Define multi-agent state schema (`InvestigationState`)
  - [ ] Implement specialized agents: Data Quality Agent, Anomaly Agent, Schema Agent, Root Cause Agent, Remediation Agent, Report Agent
  - [ ] Connect agents in a LangGraph state graph with conditional routing
  - [ ] Implement LLM provider adapter (Groq API, OpenAI) with deterministic intelligent local fallback
  - [ ] Create investigation execution API and storage of trace runs

- [ ] **Phase 6: RAG Knowledge Retrieval System**
  - [ ] Build vector embedding and similarity search engine
  - [ ] Seed domain knowledge: common data quality rules, historical incident templates, remediation patterns
  - [ ] Integrate retrieval into the investigation agent workflow with traceable citations

- [ ] **Phase 7: Human-in-the-Loop Remediation Engine**
  - [ ] Generate discrete transformation proposals with risk level, confidence, and preview
  - [ ] Build approval/rejection endpoints with audit logging
  - [ ] Implement transformation execution engine producing a clean non-destructive dataset copy
  - [ ] Generate before/after verification metrics

- [ ] **Phase 8: Incident Management, Analytics & Reporting**
  - [ ] Implement incident lifecycle CRUD (OPEN, INVESTIGATING, REMEDIATED, RESOLVED)
  - [ ] Implement dashboard aggregation metrics (overall health, drift alerts, incident severity)
  - [ ] Implement exportable PDF / CSV reports

- [ ] **Phase 9: React + TypeScript + Tailwind Frontend**
  - [ ] Initialize React Vite project with TypeScript, Tailwind CSS, Lucide icons, Recharts
  - [ ] Build shared navigation, Layout, Navbar, Dark/Light theme, notification toasts
  - [ ] Build 12 comprehensive pages:
    1. Login & Registration
    2. Main Observability Dashboard
    3. Dataset Management
    4. Dataset Upload
    5. Dataset Profiling & Health Explorer
    6. Anomaly Explorer (Isolation Forest & Statistical)
    7. Data Drift Monitoring (KS-test & PSI charts)
    8. AI Investigation Center (LangGraph visual workflow & findings)
    9. Incident Management & SLA Tracking
    10. Remediation Approval Center (Diff preview & non-destructive execution)
    11. Executive & Technical Reports (PDF/CSV export)
    12. Settings & API Configurations

- [ ] **Phase 10: Testing, Verification & Production Packaging**
  - [ ] Comprehensive Pytest suite (Auth, Ingestion, Profiling, ML, Drift, Agents, RAG, Remediation, Incidents)
  - [ ] Sample realistic datasets (clean baseline, drifted, anomalous transactions)
  - [ ] Dockerfile for Backend & Frontend, docker-compose.yml
  - [ ] Final end-to-end verification and documentation update
