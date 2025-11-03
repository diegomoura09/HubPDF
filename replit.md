# HubPDF - PDF Tools Hub

## Overview

HubPDF is a streamlined web-based PDF processing platform built with FastAPI that offers 7 essential PDF manipulation tools completely free during the beta period. The application provides core PDF operations: juntar PDFs, dividir PDFs, extrair páginas, comprimir PDFs, converter PDF para DOCX, extrair texto, and convert PDF para imagens. Built with security and simplicity in mind, it features a calm color palette (blue, green, gray tones), multilingual support (Portuguese-BR as default, English optional), Google OAuth integration, and admin dashboard for user management. All features are 100% free with unlimited operations and no watermarks during beta.

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
- **Quota System**: Beta mode with unlimited operations (999999 ops/day) for all registered users
- **Watermark Logic**: No watermarks applied during beta period
- **File Processing**: PDF operations using native Python libraries (python-docx, pdfplumber, reportlab, PyPDF2, pikepdf)
- **Filename Preservation**: All conversions maintain original filename with descriptive suffixes (_merge, _compress, _split, _to_docx, etc)
- **7 Core Functions Only**: Juntar PDFs, Dividir PDFs, Extrair Páginas, Comprimir PDFs, PDF para DOCX, Extrair Texto, PDF para Imagens

### Frontend Architecture
- **UI Framework**: Tailwind CSS with HTMX for dynamic interactions
- **Color Scheme**: Calm tones of blue, green, gray, white, and black for professional appearance
- **Progressive Enhancement**: PWA-ready with manifest.json and service worker
- **Internationalization**: JSON-based translation system with cookie-based locale switching
- **Tools Modal**: "Todas as Ferramentas" button in header with 7 essential tools displayed in a clean grid
- **Credits**: Footer displays developer attribution (Diego Moura de Andrade - Cruzeiro do Sul / Braz Cubas)

### Admin Panel
- **Dashboard**: KPIs tracking (users, operations, storage)
- **User Management**: Search, edit plans, reset quotas with audit logging
- **Access**: Available in user profile dropdown menu for admin users

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