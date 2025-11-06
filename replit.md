# HubPDF

## Overview

HubPDF is an academic web application for PDF manipulation and conversion, developed as part of the CST in Systems Analysis and Development course at Cruzeiro do Sul / BrazCubas. The platform provides free, secure, and privacy-focused PDF tools with automatic file cleanup and no permanent storage.

The system emphasizes security, LGPD compliance, and sustainable digital document management through features like PDF merging, splitting, compression, text extraction, and format conversion.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Framework
- **Backend**: FastAPI (Python) with ASGI server (Uvicorn)
- **Frontend**: Server-side rendered Jinja2 templates with progressive enhancement
- **Styling**: Tailwind CSS (CDN-based)
- **Interactivity**: HTMX for dynamic content, Alpine.js for client-side state, Lucide icons
- **PWA Support**: Service Worker and Web Manifest for offline capabilities

### Authentication & Authorization
- **Authentication Strategy**: JWT-based with optional Google OAuth
- **Password Security**: Argon2 hashing (via argon2-cffi)
- **Session Management**: HTTP-only cookies for JWT storage
- **CSRF Protection**: Signed tokens using itsdangerous with time-based expiration
- **Anonymous Users**: UUID-based anonymous sessions with signed cookies for unauthenticated usage tracking

**Design Decision**: JWT chosen over session-based auth for stateless scalability. Argon2 provides superior password hashing security compared to bcrypt. CSRF uses cryptographic signatures instead of session storage to remain stateless.

### Database Architecture
- **Development**: SQLite with WAL mode for concurrent access
- **Production**: PostgreSQL (Neon) with SSL required
- **ORM**: SQLAlchemy with declarative models
- **Schema**: Users, Subscriptions, Invoices, Quotas, Coupons, Audit Logs

**Design Decision**: SQLite for local development simplicity, PostgreSQL for production to handle concurrent writes and better query optimization. Connection pooling configured differently based on database type. Email uniqueness enforced via case-insensitive index (`LOWER(email)`) at database level.

### Security Middleware Stack
1. **SecurityMiddleware**: Adds security headers (X-Frame-Options, CSP-like headers, HSTS in production)
2. **RateLimitMiddleware**: IP-based rate limiting with burst allowance using in-memory tracking
3. **CSRFMiddleware**: Validates CSRF tokens on state-changing operations
4. **TrustedHostMiddleware**: Restricts allowed hosts in production
5. **CORSMiddleware**: Configures cross-origin policies

**Design Decision**: Layered middleware approach allows independent security concerns. Rate limiting in-memory for simplicity (can be upgraded to Redis). CSRF validation happens early to prevent processing of invalid requests.

### File Processing & Conversion
- **PDF Libraries**: PyMuPDF (fitz), pikepdf, PyPDF2, pdfplumber
- **Image Processing**: Pillow (PIL)
- **Text Extraction**: pdfminer.six with OCR fallback (pytesseract)
- **Office Formats**: python-docx for DOCX support
- **Temporary Storage**: User-scoped directories under `/tmp` with automatic cleanup

**Supported Operations**:
- PDF merge, split, compression
- PDF to/from images (PNG, JPG, ICO)
- PDF to Office formats (DOCX, XLSX)
- Images to PDF (JPG, PNG, WEBP, HEIC)
- Text extraction with watermarking

**Design Decision**: Multiple PDF libraries provide fallback options when one fails. Files stored in user-specific temporary directories (`/tmp/{user_id}/{job_id}`) prevent cross-user access. Background cleanup task runs every 10 minutes to remove files older than 30 minutes. Watermarking implemented for quota enforcement on free tier.

### Quota & Billing System
- **Free Tier**: Large file uploads (10GB limit), unlimited operations (beta), no watermarks (beta)
- **Pro Tier**: Large file uploads (10GB limit), unlimited operations
- **Business Tier**: Large file uploads (10GB limit), unlimited operations
- **Anonymous Users**: Large file uploads (10GB limit), 1 operation per day, always watermarked

**Design Decision**: Upload size limits removed to allow users to process large files (up to 10GB). File size validation disabled in routers. Quota tracking in database with daily reset logic. Anonymous users tracked via hashed cookie ID (not stored as PII). Watermarking service applies conditional branding based on user tier. Integration ready for Mercado Pago (Brazilian payment gateway) for future monetization.

### Job Processing
- **Current**: FastAPI BackgroundTasks for asynchronous operations
- **Design**: Structured for future queue system (Celery/RQ)
- **Job Registry**: In-memory job tracking with status updates
- **Progress Tracking**: JobResult dataclass with status enum (PENDING, RUNNING, COMPLETED, FAILED)
- **Download System**: Completed jobs provide download links via `/tools/api/jobs/{job_id}/download/{file_index}`

**Design Decision**: BackgroundTasks sufficient for MVP with low concurrency. Job IDs (UUID) allow client polling for status and provide security through unpredictability (mitigating unauthorized access risk). Architecture prepared for distributed queue by isolating job service interface. Download endpoints use FileResponse for efficient file serving.

**UI Pattern**: Tools using job system (compress, images-to-pdf) follow consistent pattern:
1. Upload and submit operation
2. Polling-based progress tracking with visual feedback
3. Success card with download button on completion
4. Error card with clear messaging on failure

### Internationalization (i18n)
- **Implementation**: Embedded Portuguese translations in `template_helpers.py`
- **Default Language**: Brazilian Portuguese (pt-BR)
- **Template Helper**: `t()` function for localized strings
- **Future**: Structure supports external JSON files (`locales/pt.json`, `locales/en.json`)

**Design Decision**: Embedded translations for simplicity during development. Template function `t()` abstracts translation lookup, allowing future migration to file-based or database-driven i18n without template changes.

## External Dependencies

### Third-Party Services
- **Database**: Neon (Serverless PostgreSQL) with SSL/TLS
- **OAuth Provider**: Google OAuth 2.0 (optional authentication method)
- **Payment Gateway**: Mercado Pago (Brazilian payment processor, integration prepared)

### CDN-Delivered Frontend Libraries
- **Tailwind CSS**: `cdn.tailwindcss.com` (JIT compilation)
- **HTMX**: `unpkg.com/htmx.org@2.0.3` (AJAX interactions)
- **Alpine.js**: `unpkg.com/alpinejs@3.x.x` (reactive components)
- **Lucide Icons**: `unpkg.com/lucide` (icon set)

**Design Decision**: CDN delivery reduces build complexity and deployment size. Version pinning (HTMX 2.0.3) ensures stability. Fallback mechanism not implemented (assumes CDN availability).

### Python Dependencies (Key Packages)
- **Web Framework**: FastAPI, Uvicorn, Starlette
- **Database**: SQLAlchemy, psycopg2-binary (PostgreSQL)
- **Security**: argon2-cffi, PyJWT, itsdangerous, python-multipart
- **PDF Processing**: PyMuPDF, pikepdf, PyPDF2, pdfplumber, pdf2image
- **Image Processing**: Pillow, pytesseract (OCR)
- **Office Formats**: python-docx, openpyxl, python-pptx
- **Utilities**: pydantic, pydantic-settings, python-dotenv

**Design Decision**: Multiple PDF libraries provide redundancy and feature coverage. OCR (pytesseract) requires system-level Tesseract installation. Pydantic used for settings validation and request schemas.

### Environment Configuration
Required environment variables (stored in Replit Secrets or `.env`):
- `DATABASE_URL`: PostgreSQL connection string with SSL
- `JWT_SECRET`: Secret for JWT signing
- `CSRF_SECRET`: Secret for CSRF token signing
- `ANON_COOKIE_SECRET`: Secret for anonymous session cookies
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: OAuth credentials
- `MP_ACCESS_TOKEN`, `MP_WEBHOOK_SECRET`: Mercado Pago integration
- `MAX_UPLOAD_MB`: Upload size limit (default: 10000 - 10GB)

**Design Decision**: Secrets management via environment variables follows 12-factor app principles. Fallback secrets for development with warnings to prevent production misconfiguration.