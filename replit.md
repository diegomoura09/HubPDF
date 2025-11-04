# HubPDF - PDF Tools Hub

## Overview

HubPDF is a 100% free, educational web-based PDF processing platform built with FastAPI as an academic project for CST ADS (Análise e Desenvolvimento de Sistemas) at Cruzeiro do Sul / Braz Cubas university. The platform offers 7 essential PDF manipulation tools completely free: juntar PDFs, dividir PDFs, extrair páginas, comprimir PDFs, converter PDF para DOCX, extrair texto, and convert PDF para imagens. Built with focus on sustainability, LGPD compliance, and digital accessibility, it features a calm color palette (blue, green, gray tones), multilingual support (Portuguese-BR as default, English optional), Google OAuth integration, and admin dashboard for user management. All features are 100% free with unlimited operations and no watermarks. Developer: Diego Moura de Andrade. Contact: diego.andrade@cs.brazcubas.edu.br.

## Recent Changes (November 2024)

### Authentication & Database Improvements
- Fixed PostgreSQL (Neon) connection with mandatory SSL configuration
- Implemented case-insensitive email authentication with unique index on LOWER(email)
- Corrected authentication error messages to proper Portuguese-BR
- Created health check endpoints (/api/health, /api/health/db)

### Alert System Implementation
- Created reusable alert system (success, error, warning, info) with smooth animations
- Enhanced login page with client-side validation and async form submission
- Added dynamic error messages with HTML links (e.g., "E-mail não cadastrado. Clique aqui para se cadastrar")
- Backend supports dual-mode responses (JSON for API, HTML for traditional forms)
- Demo page available at /demo/alerts

### Platform Updates
- Transformed platform into 100% free educational tool by removing all paid plan references
- Contact form updated with 3 subjects: Feedback, Reportar Erro, Sugestões
- Simplified dashboard to show only welcome message and quick access to tools
- Removed all pricing pages, upgrade prompts, and subscription management UI
- Cleaned locales/pt.json to remove all paid-tier strings and messaging
- Added institutional messaging emphasizing free, educational, and non-commercial nature

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Web Framework**: FastAPI with Jinja2 templating for server-side rendering
- **Database**: SQLite for MVP with SQLAlchemy ORM (structured for easy PostgreSQL migration)
- **Authentication**: JWT-based auth with HttpOnly cookies, Argon2 password hashing, and Google OAuth integration
- **Authorization**: Role-based access control (RBAC) with user/admin roles

### Security Framework
- **Middleware Stack**: Custom security middleware for headers, rate limiting, and CSRF protection
- **File Security**: MIME type validation, file size limits, automatic cleanup after 30 minutes
- **Data Protection**: No PII in logs, secure token handling, webhook signature verification

### Business Logic
- **Quota System**: 100% free with unlimited operations (999999 ops/day) for all registered users
- **Watermark Logic**: No watermarks applied - completely free platform
- **File Processing**: PDF operations using native Python libraries (python-docx, pdfplumber, reportlab, PyPDF2, pikepdf)
- **Filename Preservation**: All conversions maintain original filename with descriptive suffixes (_merge, _compress, _split, _to_docx, etc)
- **7 Core Functions Only**: Juntar PDFs, Dividir PDFs, Extrair Páginas, Comprimir PDFs, PDF para DOCX, Extrair Texto, PDF para Imagens
- **Educational Focus**: Platform developed for academic purposes, no commercial aspects, LGPD compliant

### Frontend Architecture
- **UI Framework**: Tailwind CSS with HTMX for dynamic interactions
- **Color Scheme**: Calm tones of blue, green, gray, white, and black for professional appearance
- **Progressive Enhancement**: PWA-ready with manifest.json and service worker
- **Internationalization**: JSON-based translation system with cookie-based locale switching
- **Alert System**: Reusable JavaScript component (window.alerts) with 4 types, HTML support, auto-close, and animations
- **Form Validation**: Client-side validation with async submission and dynamic error display
- **Tools Modal**: "Todas as Ferramentas" button in header with 7 essential tools displayed in a clean grid
- **Credits**: Footer displays developer attribution (Diego Moura de Andrade - Cruzeiro do Sul / Braz Cubas)
- **Contact Form**: 3 subject options only - Feedback, Reportar Erro, Sugestões
- **Dashboard**: Simplified to show welcome message and quick tool access (no usage metrics or plan cards)

### Admin Panel
- **Dashboard**: KPIs tracking (users, operations, storage)
- **User Management**: Search, reset quotas with audit logging
- **Access**: Available in user profile dropdown menu for admin users
- **Note**: Plan management UI removed (all users are on free unlimited plan)

## External Dependencies

### Authentication Services
- **Google OAuth**: Social login integration using Authlib
- **JWT Management**: Access and refresh token rotation with secure cookie storage

### PDF Processing Libraries
- **PyPDF2**: Core PDF manipulation (merge, split, metadata, compression fallback)
- **pikepdf**: Advanced PDF compression with recompress_flate for size reduction
- **pdfplumber**: Text extraction from PDFs
- **python-docx**: PDF to DOCX conversions
- **reportlab**: PDF generation from text and document creation
- **PIL/Pillow**: Image processing for PDF conversion
- **pdf2image**: PDF to image conversion (PNG/JPG)

### Infrastructure Services
- **File Storage**: Temporary filesystem storage with automatic cleanup
- **Background Tasks**: FastAPI BackgroundTasks for file cleanup (structured for queue upgrade)
- **Rate Limiting**: In-memory rate limiting with IP-based tracking

### Development Tools
- **Validation**: Custom validators for file types, sizes, and user input
- **Security Utilities**: Argon2 password hashing, secure token generation, filename sanitization
- **Monitoring**: Audit logging for admin actions and user operations