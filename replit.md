# HubPDF

## Overview

HubPDF is a web-based PDF manipulation platform developed as an academic project for the CST in Systems Analysis and Development course (Cruzeiro do Sul / BrazCubas). The system provides free, secure PDF processing tools with automatic file cleanup and privacy-first architecture. All conversions happen server-side with temporary storage that auto-expires after 30 minutes.

**Core Value Proposition:** Free, secure, privacy-focused PDF tools accessible via web browser without permanent data storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:**
- **Templating:** Jinja2 templates with server-side rendering
- **Styling:** Tailwind CSS (via CDN)
- **Interactivity:** HTMX 2.0.3 for dynamic content, Alpine.js for component state
- **Icons:** Lucide icons (migrating away from Feather icons)
- **PWA Support:** Service worker for offline capabilities and caching (static assets cached)

**Design Patterns:**
- Component-based templates extending `base.html`
- Internationalization helper `t()` for Portuguese (default) and optional English support
- CSRF tokens embedded in forms via meta tags
- Responsive design with mobile-first approach

### Backend Architecture

**Framework:** FastAPI with async request handling

**Core Components:**
1. **Authentication Layer:**
   - JWT-based authentication with access/refresh tokens
   - Google OAuth integration via Authlib
   - Argon2 password hashing for security
   - Anonymous user support with signed cookies (`anon_id`)
   - Case-insensitive email queries using `func.lower()`

2. **Authorization & Security:**
   - Role-based access control (user, admin)
   - Custom middleware stack:
     - `SecurityMiddleware`: Adds security headers (X-Frame-Options, CSP, etc.)
     - `RateLimitMiddleware`: Per-IP rate limiting (60 calls/min default)
     - `CSRFMiddleware`: CSRF protection using itsdangerous signed tokens
   - TrustedHostMiddleware for domain validation in production

3. **File Processing:**
   - Job-based conversion system with in-memory registry
   - Temporary file storage in `/tmp/{user_id}/{job_id}/`
   - Background cleanup task runs every 10 minutes (configurable via `TEMP_FILE_RETENTION_MINUTES`)
   - Watermarking service for free tier operations (currently disabled in beta)

4. **PDF Operations (Core Services):**
   - Merge PDFs
   - Split PDFs (by page ranges)
   - Compress/optimize PDFs
   - Convert PDF ↔ DOCX/XLSX/PPTX
   - Convert PDF ↔ images (PNG/JPG/ICO)
   - Extract text with OCR fallback
   - Generate text-only PDFs

5. **Quota Management:**
   - Plan-based limits (Free, Pro, Custom, Anonymous)
   - Daily operation tracking per user/anonymous session
   - File size limits configurable via `MAX_UPLOAD_MB` environment variable (default: 60MB)
   - Anonymous users: 1 operation/day with watermark (beta: unlimited without watermark)

6. **Billing Integration (Placeholder):**
   - Mercado Pago integration stubs for future paid plans
   - Subscription and invoice models defined but not actively enforced
   - Current deployment: All features free and unlimited (beta/academic phase)

**Router Structure:**
- `/auth/*`: Authentication (login, register, OAuth callbacks)
- `/tools/*`: PDF conversion endpoints
- `/admin/*`: Admin dashboard (user management, audit logs)
- `/billing/*`: Pricing page and payment webhooks
- `/health`: Health check endpoints for database and service status
- `/`: Root redirects to `/home`

### Data Storage

**Primary Database:**
- **Development:** SQLite with WAL mode (`data/app.db`)
- **Production:** PostgreSQL (Neon) with SSL required
- **Connection pooling:** SQLAlchemy with StaticPool for SQLite
- **Schema migration:** Manual SQL scripts (e.g., `scripts/add_email_index.sql`)

**Database Models:**
- `User`: Email (unique, lowercase), password hash, OAuth IDs, plan, role
- `Subscription`: Plan status, Mercado Pago IDs, billing periods
- `Invoice`: Payment records
- `QuotaUsage`: Daily operation tracking
- `AnonQuota`: Anonymous user quota tracking by hashed session ID
- `Coupon`: Discount codes (placeholder)
- `AuditLog`: Admin action tracking

**Key Design Decisions:**
- Unique email index: Case-insensitive (`users_email_lower_idx` on `LOWER(email)`)
- Anonymous tracking: Cookie-based sessions with UUID4, hashed before DB storage
- No permanent file storage: All uploads auto-delete after 30 minutes

### External Dependencies

**Third-Party Services:**
- **Neon PostgreSQL:** Cloud database with SSL enforcement
- **Google OAuth:** Authentication via `GOOGLE_CLIENT_ID/SECRET`
- **Mercado Pago:** Payment processing (not active in current deployment)
- **Replit:** Cloud deployment platform (mentions being removed)

**Python Libraries (Critical):**
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM and database abstraction
- `jinja2`: Template engine
- `PyPDF2`, `pikepdf`: PDF manipulation
- `PyMuPDF` (fitz): PDF rendering
- `python-docx`: DOCX conversion
- `Pillow`: Image processing
- `pdfminer.six`: Text extraction
- `pytesseract`: OCR fallback
- `argon2-cffi`: Password hashing
- `python-jose[cryptography]`: JWT handling
- `itsdangerous`: CSRF token signing
- `authlib`: OAuth client

**CDN Dependencies:**
- Tailwind CSS
- HTMX 2.0.3
- Alpine.js 3.x
- Lucide icons

**Environment Variables (Required):**
```
DATABASE_URL          # Postgres connection string with ?sslmode=require
SECRET_KEY            # App-wide secret
JWT_SECRET            # JWT signing key
CSRF_SECRET           # CSRF token signing
ANON_COOKIE_SECRET    # Anonymous session signing
GOOGLE_CLIENT_ID      # OAuth (optional)
GOOGLE_CLIENT_SECRET  # OAuth (optional)
MAX_UPLOAD_MB         # File size limit (default: 60)
```

**Deployment Constraints:**
- Replit Autoscale plan: May impose proxy-level upload limits beyond `MAX_UPLOAD_MB`
- Recommendation for larger files: Reserved VM or direct S3 presigned URLs
- Health check endpoint: `/healthz` returns `{"ok": true}`
- HTTPS enforcement: TrustedHostMiddleware validates allowed domains