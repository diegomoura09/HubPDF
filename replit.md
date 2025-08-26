# HubPDF - PDF Tools Hub

## Overview

HubPDF is a comprehensive web-based PDF processing platform built with FastAPI that offers secure PDF manipulation tools through a freemium business model. The application provides essential PDF operations like merging, splitting, compressing, and converting PDFs to/from images, while maintaining strict security and privacy standards. It features multilingual support (Portuguese-BR as default, English optional), Google OAuth integration, Mercado Pago payment processing, and a complete admin dashboard for user and subscription management.

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
- **Quota System**: Plan-based limits (Free: 8 ops/day, Pro: 200 ops/day, Business: 500 ops/day)
- **Watermark Logic**: Applied to free plan after 4th operation
- **File Processing**: PDF operations using PyPDF2, pikepdf, and PIL with temporary file management

### Frontend Architecture
- **UI Framework**: Tailwind CSS with HTMX for dynamic interactions
- **Progressive Enhancement**: PWA-ready with manifest.json and service worker
- **Internationalization**: JSON-based translation system with cookie-based locale switching

### Admin Panel
- **Dashboard**: KPIs tracking (users, revenue, subscriptions)
- **User Management**: Search, edit plans, reset quotas with audit logging
- **Billing Management**: Subscription control, coupon system, invoice tracking

## External Dependencies

### Payment Processing
- **Mercado Pago**: Subscription management, checkout preferences, webhook handling
- **Integration**: Creates payment links, processes callbacks, manages subscription lifecycle

### Authentication Services
- **Google OAuth**: Social login integration using Authlib
- **JWT Management**: Access and refresh token rotation with secure cookie storage

### PDF Processing Libraries
- **PyPDF2**: Core PDF manipulation (merge, split, metadata)
- **pikepdf**: Advanced PDF operations and compression
- **pdfplumber**: Text extraction capabilities
- **PIL/Pillow**: Image processing for PDF conversion
- **pdf2image**: PDF to image conversion (optional dependency)

### Infrastructure Services
- **File Storage**: Temporary filesystem storage with automatic cleanup
- **Background Tasks**: FastAPI BackgroundTasks for file cleanup (structured for queue upgrade)
- **Rate Limiting**: In-memory rate limiting with IP-based tracking

### Development Tools
- **Validation**: Custom validators for file types, sizes, and user input
- **Security Utilities**: Argon2 password hashing, secure token generation, filename sanitization
- **Monitoring**: Audit logging for admin actions and user operations