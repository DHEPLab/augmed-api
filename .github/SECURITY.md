# Security

This document summarizes the key security controls and best practices for the AugMed App (frontend + backend).

## 1. Transport Security
- **HTTPS only**  
  All traffic to `https://augmed1.dhep.org` is encrypted with TLS.  
- **HSTS**  
  The backend API enforces HTTP Strict Transport Security to prevent downgrade attacks.

## 2. Authentication & Authorization
- **JWT-based auth**  
  Users authenticate via a JSON Web Token (JWT) issued by the backend.  
- **httpOnly cookies**  
  JWTs are stored in httpOnly cookies to mitigate XSS-based token theft.  
- **Route protection**  
  All API endpoints under `/api/*` require a valid JWT and check user ownership.

## 3. CORS
- **Restricted origin**  
  Backend CORS policy only allows requests from the official frontend origin (`https://augmed1.dhep.org`).  
- **Preflight checks**  
  `OPTIONS` requests are handled and validated before allowing any state-changing method.

## 4. Secrets & Config
- **Environment variables**  
  All secrets (database URLs, JWT signing keys, third-party API keys) are injected via environment variables—never checked into source control.  
- **.env exclusions**  
  The repository’s `.gitignore` excludes any local `.env` or secret files.

## 5. Dependency Management
- **Regular audits**  
  - Frontend: `npm audit` (or `yarn audit`) run on each CI build.  
  - Backend: `pip-audit` (or `safety`) scans Python dependencies for known vulnerabilities.  
- **Pinned versions**  
  `package.json` and `requirements.txt` use exact version pins to ensure reproducible installs.

## 6. Input Validation & Output Encoding
- **Schema validation**  
  Backend request bodies are validated against JSON schemas via `flask_json_schema`.  
- **ORM usage**  
  All database access uses SQLAlchemy with parameterized queries to prevent SQL injection.  
- **Escape output**  
  Frontend templates escape any user-provided content to avoid XSS.

## 7. Content Security Policy (CSP)
- The frontend sets a strict CSP header to disallow inline scripts and only allow trusted script sources.

## 8. Logging & Monitoring
- **Audit logs**  
  Security-related events (login, token validation failures, analytics submissions) are logged centrally.  
- **Error handling**  
  Stack traces and internal errors are never exposed to end users; they are captured in server logs only.

## 9. Database Migrations
- **Alembic migrations**  
  Schema changes are tracked and applied via Alembic; no manual DDL in production.

---

> For any security concerns, please contact the DHEP Lab’s security team at `dhep.lab@gmail.com`.  
