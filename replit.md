# HubPDF - Sistema de Ferramentas PDF

## Overview

HubPDF is a comprehensive web-based PDF manipulation platform developed as an academic project for the CST in Systems Analysis and Development program (Cruzeiro do Sul / BrazCubas). The application provides free, secure, and sustainable digital tools for PDF document manipulation, including merging, splitting, compressing, converting, and extracting text from PDF files.

The platform features a modern, responsive web interface built with FastAPI backend and HTMX-powered frontend, supporting both authenticated users and anonymous visitors with quota management. The system is designed for deployment on cloud platforms with PostgreSQL database support and includes comprehensive security middleware, OAuth authentication, and optional payment integration via Mercado Pago.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework**: FastAPI (Python)
- Asynchronous ASGI application with lifespan management
- Pure ASGI middleware implementation to avoid request body consumption issues
- Structured logging with JSON format for production monitoring
- Background task system for temporary file cleanup (30-minute retention)

**Application Structure**:
- Modular router-based organization (`/auth`, `/tools`, `/billing`, `/admin`, `/health`)
- Service layer pattern for business logic separation
- Dependency injection for database sessions and user authentication
- Template rendering via Jinja2 with centralized helper system

**PDF Processing Engine**:
- Multi-strategy compression system with automatic heuristic analysis
- Three compression levels (light/balanced/strong) with optional grayscale and rasterization
- Ghostscript integration for image-heavy PDFs with configurable DPI and JPEG quality
- qpdf + pikepdf for structural optimization and metadata removal
- Fallback rasterization for native text/vector PDFs with minimal compression
- Image-to-PDF conversion supporting JPG, PNG, WEBP, and HEIC/HEIF formats
- Advanced features: watermarking, page size options, orientation control, margin configuration

**File Processing**:
- Unlimited file upload size (configurable via MAX_UPLOAD_MB environment variable, default 10GB)
- Temporary file management with job-based directory structure under `/tmp`
- Asynchronous job processing with in-memory registry and status tracking
- Support for batch operations and multi-file uploads

**Security Layers**:
1. **SecurityMiddleware**: Adds security headers (CSP, X-Frame-Options, HSTS)
2. **RateLimitMiddleware**: Token bucket algorithm for rate limiting per IP
3. **CSRFMiddleware**: CSRF protection using itsdangerous signed tokens
4. **RequestLoggingMiddleware**: Structured request/response logging
5. **TrustedHostMiddleware**: Domain whitelist enforcement
6. **CORSMiddleware**: Cross-origin request configuration

**Authentication & Authorization**:
- JWT-based authentication with access and refresh tokens
- Argon2 password hashing via dedicated PasswordManager service
- Google OAuth integration using authlib
- Role-based access control (user/admin roles)
- Anonymous user tracking via signed cookies with quota enforcement

**Database Schema**:
- Users: email (lowercase, unique index), password_hash, name, role, plan, google_id
- Subscriptions: Mercado Pago integration, plan tracking, billing periods
- Invoices: Payment history and transaction records
- Coupons: Promotional codes with validity and usage limits
- QuotaUsage: Daily operation tracking per user
- AnonQuota: Anonymous visitor quota management
- AuditLog: Admin action tracking for compliance

### Frontend Architecture

**Technology Stack**:
- HTML5 with Jinja2 templating
- Tailwind CSS via CDN for utility-first styling
- HTMX for dynamic, SPA-like interactions without JavaScript frameworks
- Alpine.js for reactive components
- Lucide icons (replaced Feather icons)

**Design System**:
- Modern 2025 teal/slate color palette with CSS custom properties
- Responsive grid layouts with mobile-first approach
- Custom button system with primary/outline variants
- Alert system with auto-dismiss and HTML content support
- Progressive Web App (PWA) support via manifest.json and service worker

**Client-Side Features**:
- Drag-and-drop file upload with visual feedback
- Client-side form validation with Portuguese error messages
- Real-time progress tracking for long-running operations
- Infinite file size uploads (HTMX validation completely disabled)
- Toast notifications and alert system

**Service Worker**:
- Static asset caching for offline functionality
- Network-first strategy for API endpoints
- Stale-while-revalidate for pages
- Version-based cache management (v3.4.0)

### Database Architecture

**Primary Database**: PostgreSQL (Neon) with SSL required
- Connection pooling with NullPool for Neon compatibility
- WAL mode and pragma optimizations
- SSL enforcement via connection string parameters

**Local Development**: SQLite with WAL journaling
- File-based storage in `data/app.db`
- StaticPool for thread safety with check_same_thread=False
- Pragma optimizations for performance

**Schema Management**:
- SQLAlchemy ORM with declarative base
- Migration scripts in `scripts/` directory
- Case-insensitive email index: `users_email_lower_idx` on `LOWER(email)`
- Foreign key constraints enabled

### External Dependencies

**Third-Party Services**:
1. **Google OAuth**: Client ID/secret for social authentication
2. **Mercado Pago**: Payment gateway integration with webhook support
3. **Neon PostgreSQL**: Serverless Postgres database with SSL

**Python Libraries (Key Dependencies)**:
- **FastAPI**: Web framework with async support
- **SQLAlchemy**: ORM and database toolkit
- **Uvicorn**: ASGI server
- **pikepdf**: PDF manipulation and optimization
- **PyPDF2**: PDF reading and merging
- **img2pdf**: Image-to-PDF conversion
- **Pillow + pillow-heif**: Image processing with HEIC support
- **pdfminer.six**: Text extraction from PDFs
- **authlib**: OAuth client implementation
- **argon2-cffi**: Password hashing
- **itsdangerous**: Signed tokens for CSRF and anonymous cookies
- **python-magic**: MIME type detection

**System Dependencies**:
- **Ghostscript**: PDF compression and rasterization
- **qpdf**: PDF linearization and optimization
- **Tesseract** (optional): OCR for scanned documents

**Frontend CDN Resources**:
- Tailwind CSS: `cdn.tailwindcss.com`
- HTMX: `unpkg.com/htmx.org@2.0.3`
- Lucide Icons: `unpkg.com/lucide@latest`
- Alpine.js: `unpkg.com/alpinejs@3.x.x`

**Deployment Platform**:
- Designed for cloud deployment (references to Replit have been neutralized)
- Environment variable configuration via `.env`
- Custom domain support (hubpdf.pro)
- Health check endpoints for monitoring (`/health`, `/health/db`, `/healthz`)

**Configuration Management**:
- Pydantic Settings for type-safe environment variable handling
- Separate development/production configurations
- Sensitive credentials stored in environment variables
- Feature flags for beta features (e.g., unlimited operations, no watermarks)