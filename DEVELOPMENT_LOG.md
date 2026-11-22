# DataSentinel AI: Development Log

## 2026-11-22 - Session Initial Setup & Architecture

### Environment Analysis
- Detected Python 3.13.14, Node v26.13.0, npm 11.20.0, Git 2.53.0.
- Docker command is not available in current host path (`docker: command not found`).
- Decision: Provide complete Dockerfiles and `docker-compose.yml` for containerized deployment, while implementing dual-mode database support (PostgreSQL for containerized/production setups, with zero-configuration SQLite support for immediate out-of-the-box local developer execution and unit testing).
- Disk Space: Detected low free space on C:\ (~60MB), while D:\ has ~136GB. Cleaned `C:\Users\divya\AppData\Local\pip\cache` to immediately recover 1.39 GB of free space.
- Pip flag: Using `--no-cache-dir` on pip installations to preserve host storage.

### Architectural Decisions & Bug Fixes
1. **JSON Serialization in SQLAlchemy**:
   - Encountered `TypeError: Object of type bool_ is not JSON serializable` and `Timestamp is not JSON serializable` when inserting NumPy booleans/floats and Pandas Timestamps into JSON columns.
   - Solution: Implemented `default_json_serializer` and configured `json_serializer=json_dumps_custom` on SQLAlchemy's `create_engine`, ensuring automatic, transparent coercion of all NumPy scalar types, arrays, and Pandas Timestamps to valid native Python JSON objects.
2. **Multi-Format Remediation Copying**:
   - Identified that remediated copies must match the source file format (JSON files saved as JSON, CSV as CSV, Excel as Excel) so subsequent automated profiling parses properly without MIME mismatches.
   - Updated `IngestionService.load_dataframe` to smartly inspect both explicit type and file extension.
3. **Cross-Dataset Baseline Drift Comparison**:
   - Enhanced `DriftEngine.run_drift_analysis` to allow comparing two versions within a single dataset, as well as comparing an incoming dataset version against a separate baseline benchmark dataset.
4. **Test Suite Verification**:
   - 9 out of 9 pytest suites passed with 100% success rate across Authentication, Ingestion, Profiling, Isolation Forest, KS-Test & PSI Drift, LangGraph Multi-Agent, RAG, Incidents, and Human-in-the-Loop Remediation.
