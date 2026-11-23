# DataSentinel AI: Production Deployment & Operations Guide

This guide details the deployment, environment configuration, database setup, containerization, and operations for **DataSentinel AI** — an Autonomous AI-Powered Data Quality, Observability, and Intelligence Platform.

> **CRITICAL POLICY NOTICE: DO NOT DEPLOY TO EXTERNAL CLOUD PROVIDERS**  
> Per security governance and explicit operational instructions, **external deployment to cloud hosts (Render, Railway, AWS, Vercel, Fly.io, Heroku, etc.) is prohibited**.  
> The system has been hardened and verified locally for production readiness. All commands below are designed for secure, self-hosted, on-premises or local containerized execution.

---

## 1. System Architecture Overview

DataSentinel AI operates as a unified data observability and agentic intelligence ecosystem:

```
                      +---------------------------------------+
                      |       Web Browser (Client)            |
                      +---------------------------------------+
                                          |
                                          | HTTPS / Port 80 (Nginx)
                                          v
                      +---------------------------------------+
                      |         Frontend (Nginx + SPA)        |
                      |   React 18 + TypeScript + Vite + CSS  |
                      +---------------------------------------+
                                          |
                                          | Reverse Proxy /api/ -> Port 8000
                                          v
                      +---------------------------------------+
                      |         FastAPI Application Server    |
                      |     (Python 3.12 / 3.13, Uvicorn)     |
                      +---------------------------------------+
                        |                 |                 |
       +----------------+                 |                 +-----------------+
       v                                  v                                   v
+---------------+             +-----------------------+              +-----------------+
| PostgreSQL 16 |             |   LangGraph Agentic   |              |  Local Storage  |
|  (Relational  |             |      Orchestrator     |              |  - Raw Uploads  |
|   Metadata)   |             |   (6 Multi-Agents +   |              |  - Remediated   |
+---------------+             |    Groq Llama 3.3)    |              |  - FAISS Store  |
                              +-----------------------+              +-----------------+
                                          |
                                          v
                              +-----------------------+
                              |      Redis 7.0        |
                              |   (Task Queue/Cache)  |
                              +-----------------------+
```

---

## 2. Infrastructure & System Prerequisites

### Bare-Metal / Virtual Machine Requirements
- **Operating System**: Linux (Ubuntu 22.04 LTS recommended), macOS (13+), or Windows 10/11 with WSL2 / PowerShell 7+.
- **CPU**: 4+ Cores recommended (2 Cores minimum).
- **RAM**: 8 GB RAM recommended (4 GB minimum for local SQLite execution).
- **Disk Storage**: 20 GB free space for Docker images, datasets, and FAISS vector indices.

### Software Runtimes
- **Python**: Version `3.11.x`, `3.12.x`, or `3.13.x` with `pip` and `virtualenv`.
- **Node.js**: Version `18.x` or `20.x` LTS with `npm` (v9+).
- **Database**: PostgreSQL 16+ (or SQLite 3 for zero-config local testing).
- **In-Memory Cache**: Redis 7.0+ (optional for basic standalone operations).
- **Docker**: Docker Engine 24+ and Docker Compose v2.20+ (when deploying via containers).

---

## 3. Environment Configuration (`.env`)

Create a `.env` file in the project root directory by copying `.env.example`:

```bash
cp .env.example .env
```

### Complete Environment Specification

| Variable Name | Required | Default / Example Value | Description |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Yes | `production` (or `development`) | Environment mode. In `production`, strict secret validation is enforced. |
| `DEBUG` | Yes | `False` (in prod), `True` (in dev) | Disables verbose exception traces in HTTP responses. |
| `PORT` | No | `8000` | Backend API port. |
| `HOST` | No | `0.0.0.0` | Backend listen interface. |
| `SECRET_KEY` | **Yes** | `sentinel_prod_jwt_super_secure_key_min_32_chars!` | Cryptographic HMAC secret for signing JWT tokens (min 32 chars). |
| `ALGORITHM` | No | `HS256` | JWT signature algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token validity window (default: 60 minutes). |
| `DATABASE_URL` | **Yes** | `postgresql://user:pass@localhost:5432/datasentinel_db` | Primary database URI. Fallback: `sqlite:///./datasentinel.db`. |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Cache and broker URL. |
| `STORAGE_DIR` | No | `./data` (or `/app/storage` in Docker) | Root directory for file uploads and remediations. |
| `MAX_UPLOAD_SIZE_MB` | No | `100` | Hard cap on uploaded dataset file sizes in Megabytes. |
| `CORS_ORIGINS` | **Yes** | `["http://localhost:5173","http://localhost:3000"]` | Whitelisted browser origins. Wildcards (`*`) are prohibited. |
| `GROQ_API_KEY` | Optional | `gsk_...` | Groq Cloud API key for Llama 3.3 70B agent reasoning. Local fallback used if blank. |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | LLM model target. |

---

## 4. Database Setup & Initialization

### Option A: PostgreSQL 16 (Recommended for Production)

1. Provision database and user:
```sql
CREATE USER datasentinel WITH PASSWORD 'sentinel_secure_password';
CREATE DATABASE datasentinel_db OWNER datasentinel;
GRANT ALL PRIVILEGES ON DATABASE datasentinel_db TO datasentinel;
```

2. Point `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://datasentinel:sentinel_secure_password@localhost:5432/datasentinel_db
```

3. Initialize schema and default admin account:
```bash
python -c "from app.core.database import init_db; init_db()"
```
*The database automatically creates all relational tables and seeds the default system administrator:*
- **Username**: `admin`
- **Email**: `admin@datasentinel.ai`
- **Default Password**: `admin123` *(Must be changed immediately via User Settings)*

### Option B: SQLite (Zero-Config Development & Testing)

Leave `DATABASE_URL` unset or set to:
```env
DATABASE_URL=sqlite:///./datasentinel.db
```
The database file `datasentinel.db` will be created automatically upon server startup.

---

## 5. Local Standalone Execution (Without Docker)

### Step 1: Run Backend Services

1. Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

2. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Launch the FastAPI server:
```bash
python backend/run.py
```
*API server will listen on `http://127.0.0.1:8000`.*  
*Interactive Swagger documentation available at `http://127.0.0.1:8000/docs`.*

### Step 2: Run Frontend Services

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start development server (or run production preview):
```bash
# Development server with Hot Module Replacement
npm run dev

# Or build and preview production assets
npm run build
npm run preview
```
*Frontend UI accessible at `http://localhost:5173`.*

---

## 6. Containerized Deployment (Docker Compose)

DataSentinel AI includes a complete multi-container orchestration suite via `docker-compose.yml`.

### Docker Architecture
- **`datasentinel-postgres`**: PostgreSQL 16 Alpine with persistent data volume and healthchecks.
- **`datasentinel-redis`**: Redis 7 Alpine with persistent volume.
- **`datasentinel-backend`**: Multi-stage Python 3.12 slim container with curl health probe.
- **`datasentinel-frontend`**: Multi-stage build (Node 20 -> Nginx Alpine) serving the optimized SPA.

### Step-by-Step Commands

1. Verify environment configuration:
```bash
# Ensure .env exists with strong credentials
cp .env.example .env
```

2. Build and launch all services in detached mode:
```bash
docker compose up -d --build
```

3. Verify service health and container status:
```bash
docker compose ps
```
*Expected status for all 4 containers: `Up (healthy)`.*

4. Tail real-time unified logs:
```bash
docker compose logs -f
```

5. Stop and clean up containers:
```bash
# Stop containers while preserving data volumes
docker compose down

# Stop and purge volumes (Caution: deletes all database records and uploads)
docker compose down -v
```

---

## 7. Security & Compliance Checklist

DataSentinel AI has been systematically hardened against OWASP Top 10 vulnerabilities:

1. **Password Security (Argon2id)**:
   - Uses RFC 9106 Argon2id parameters (Memory: 64 MiB, Time: 3 iterations, Parallelism: 4 threads).
   - Zero plaintext passwords in memory or logs.
   - Backward compatibility for legacy salted hashes with automatic rehash detection.
2. **Access Control (RBAC)**:
   - `admin`: Full administrative control, system metrics, audit inspection, and user management.
   - `analyst`: Can upload datasets, trigger investigations, approve and execute remediations.
   - `viewer`: Read-only access to dashboards, reports, and incident logs. Write endpoints reject with `403 Forbidden`.
3. **Session & Token Security**:
   - Cryptographically signed JWT tokens with strict claim verification (`exp`, `iat`, `sub`).
   - Default 60-minute expiry window.
   - No sensitive tokens in URLs or browser local storage leaks.
4. **Ingestion & File Confinement**:
   - Binary magic bytes analysis rejects ELF, PE (`MZ`), and executable script headers disguised as CSV/JSON.
   - Canonical path resolution (`os.path.commonpath`) prevents directory traversal attacks (`../`).
   - Non-destructive remediation architecture guarantees raw uploaded files are never overwritten.
5. **Network Hardening**:
   - Strict CORS policy rejecting wildcard origins (`*`) when credentials are enabled.
   - Host binding isolation: PostgreSQL (`127.0.0.1:5432`) and Redis (`127.0.0.1:6379`) are bound strictly to localhost and not exposed to the public internet.

---

## 8. Health Checks & Verification Endpoints

| Endpoint | Method | Expected Output | Description |
| :--- | :---: | :--- | :--- |
| `/health` | `GET` | `{"status":"healthy","service":"DataSentinel AI","version":"1.0.0"}` | Root system health check for load balancers. |
| `/api/v1/auth/health` | `GET` | `{"status":"healthy","service":"auth"}` | API V1 service probe. |
| `/api/v1/auth/me` | `GET` | `UserOut` object | Authenticated token validation probe. |

### Running the Independent Verification Suite

To run the automated verification suite verifying all 12 platform modules:
```bash
python backend/tests/verify_all.py
```

To run the automated Pytest test suite (17 tests):
```bash
python -m pytest backend/tests -v
```

---

## 9. Troubleshooting & FAQ

### Issue: "The term 'docker' is not recognized"
- **Cause**: Docker Desktop is not installed or the Docker daemon path is not in the system environment `PATH`.
- **Resolution**: Install Docker Desktop on Windows/macOS or `docker.io` on Ubuntu. If running locally without Docker, use **Section 5 (Local Standalone Execution)** with SQLite.

### Issue: "CRITICAL SECURITY ERROR: Production deployment requires a secure SECRET_KEY"
- **Cause**: In `ENVIRONMENT=production`, the default development secret was supplied.
- **Resolution**: Generate a secure 32+ character random secret and update `SECRET_KEY` in `.env`:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

### Issue: "Permission denied on file upload"
- **Cause**: Storage directory permissions are restricted.
- **Resolution**: Ensure the user running the process has write permissions on `./data/uploads` and `./data/remediated`.
