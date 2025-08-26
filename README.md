# HubPDF - Hub de Ferramentas PDF Completo

![HubPDF Logo](https://via.placeholder.com/120x40/dc2626/ffffff?text=HubPDF)

HubPDF é uma plataforma completa de ferramentas para processamento de arquivos PDF, desenvolvida com foco em segurança, privacidade e facilidade de uso. Oferece um modelo freemium com integração ao Mercado Pago, suporte multilíngue (Português-Brasil e Inglês) e arquitetura security-first.

## 🚀 Funcionalidades Principais

### 🔧 Ferramentas PDF (6 MVP)
- **Mesclar PDFs**: Combine múltiplos arquivos PDF em um único documento
- **Dividir PDF**: Divida um PDF em múltiplos arquivos por intervalos de páginas
- **Compactar PDF**: Reduza o tamanho do arquivo PDF mantendo a qualidade
- **PDF para Imagens**: Converta páginas de PDF em imagens PNG/JPG
- **Imagens para PDF**: Crie um PDF a partir de múltiplas imagens
- **Extrair Texto**: Extraia todo o texto de um arquivo PDF

### 🔐 Segurança e Privacidade
- **Criptografia Argon2** para senhas
- **JWT** com tokens de acesso e refresh em cookies HttpOnly seguros
- **Proteção CSRF** para todos os formulários
- **Rate limiting** em uploads
- **Validação MIME** e tamanho de arquivo
- **Limpeza automática** de arquivos após 30 minutos
- **Sem PII em logs**

### 💰 Modelo de Negócio Freemium
- **Plano Gratuito**: 10MB max/arquivo, 8 ops/dia, marca d'água após 4ª operação
- **Plano Pro (R$ 14,90/mês)**: 100MB max/arquivo, 200 ops/dia, sem marca d'água
- **Plano Business (R$ 29,90/mês)**: 250MB max/arquivo, 500 ops/dia, recursos avançados

### 🌍 Multilíngue
- **Português-Brasil** (padrão)
- **Inglês** (opcional)
- Sistema de tradução baseado em JSON
- Switcher de idioma com cookie persistente

### 👨‍💼 Painel Administrativo
- **Dashboard** com KPIs (usuários, receita, assinaturas ativas)
- **Gerenciamento de usuários** (buscar, editar plano, resetar cotas)
- **Controle de assinaturas** (ajustar período, cancelar/estender)
- **Sistema de cupons** CRUD com códigos promocionais
- **Histórico de faturas** com link para Mercado Pago
- **Log de auditoria** para ações administrativas

## 🛠 Stack Tecnológica

### Backend
- **FastAPI** (Python web framework)
- **SQLite** com SQLAlchemy ORM (estruturado para migração PostgreSQL)
- **Authlib** para integração OAuth
- **PyJWT** para gerenciamento de tokens
- **Argon2** para hash de senhas
- **pypdf, pikepdf, pdf2image, pdfplumber** para operações PDF

### Frontend
- **Jinja2** templating engine
- **HTMX** para interações dinâmicas
- **Tailwind CSS** (CDN) para estilização
- **JavaScript** vanilla para funcionalidades client-side
- **Alpine.js** para componentes interativos

### Infraestrutura
- **Replit Core** para hospedagem
- **Variáveis de ambiente** para gerenciamento de secrets
- **BackgroundTasks** do FastAPI para processamento
- **PWA** com manifest.json e service worker

## ⚙️ Configuração no Replit Core

### 1. Variáveis de Ambiente Obrigatórias

Configure as seguintes variáveis no Replit Secrets:

```bash
# JWT e Segurança
JWT_SECRET=sua-chave-jwt-super-segura-aqui
WEBHOOK_SECRET=sua-chave-webhook-mercado-pago

# Google OAuth
GOOGLE_CLIENT_ID=seu-client-id-google.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=sua-chave-secreta-google
GOOGLE_REDIRECT_URI=https://seu-app.replit.app/auth/google/callback

# Mercado Pago
MP_ACCESS_TOKEN=seu-access-token-mercado-pago
MP_PUBLIC_KEY=sua-chave-publica-mercado-pago
MP_WEBHOOK_SECRET=sua-chave-webhook-mercado-pago

# Opcional
DEBUG=false
DOMAIN=seu-app.replit.app
DATABASE_URL=sqlite:///./hubpdf.db
