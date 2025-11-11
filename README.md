# 🧩 HubPDF

Sistema web desenvolvido como parte do curso **CST em Análise e Desenvolvimento de Sistemas** (Cruzeiro do Sul / BrazCubas).  
O HubPDF oferece ferramentas simples e gratuitas para **manipulação de arquivos PDF**, com foco em **eficiência, acessibilidade e sustentabilidade digital**.

> 🌐 **Acesse agora:** [hubpdf.pro](https://hubpdf.pro)

---

## 🚀 Funcionalidades

### ✅ Ferramentas Disponíveis
- **📄 Converter Imagens para PDF** - Suporte para JPG, PNG, WEBP e HEIC  
- **🔗 Mesclar PDFs** - Combine múltiplos arquivos em um só  
- **✂️ Dividir PDFs** - Extraia páginas específicas ou divida em partes  
- **🗜️ Comprimir PDFs** - Reduza o tamanho sem perder qualidade  
- **📝 Extrair Texto** - Obtenha o texto de qualquer PDF  
- **🔄 PDF para Word/Excel** *(em desenvolvimento)*  
- **🔐 Adicionar Marca d'água** - Proteja seus documentos  

### 💡 Diferenciais
- **Upload ilimitado** - Sem restrições de tamanho de arquivo
- **100% gratuito** - Todas as ferramentas sem custo
- **Interface moderna** - Design responsivo e intuitivo
- **Segurança** - Arquivos processados e excluídos automaticamente
- **Sem cadastro obrigatório** - Use como visitante ou crie conta para mais recursos

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11** com FastAPI framework
- **Uvicorn** como servidor ASGI
- **SQLAlchemy** ORM para banco de dados
- **PostgreSQL** (Neon serverless)

### Frontend
- **HTML5** com templates Jinja2
- **Tailwind CSS** para estilização
- **HTMX** para interatividade dinâmica
- **Alpine.js** para componentes reativos
- **Lucide Icons** para ícones modernos

### Processamento de PDFs
- **PyPDF2** - Manipulação básica
- **pikepdf** - Otimização avançada
- **PyMuPDF** - Renderização e conversão
- **img2pdf** - Conversão de imagens
- **Pillow + pillow-heif** - Processamento de imagens
- **Ghostscript** - Compressão profissional

### Segurança & Autenticação
- **Argon2** para hash de senhas
- **JWT** para autenticação stateless
- **OAuth 2.0** com Google Login
- **CSRF Protection** via itsdangerous
- **Rate Limiting** por IP

---

## 📦 Upload de Arquivos

### Limites e Recomendações
- **Tamanho máximo:** Ilimitado (padrão: até 10GB configurável)
- **Formatos suportados:** PDF, JPG, PNG, WEBP, HEIC, DOCX, XLSX
- **Processamento:** Arquivos muito grandes podem levar mais tempo
- **Qualidade:** PDFs já muito comprimidos podem apresentar limitações

### Segurança dos Arquivos
- Arquivos são armazenados temporariamente durante o processamento
- Exclusão automática após 30 minutos
- Sem rastreamento ou armazenamento permanente
- Processamento local no servidor

---

## 🧭 Executando Localmente

### Pré-requisitos
- Python 3.10 ou superior  
- PostgreSQL (ou use SQLite para dev)
- Git instalado

### Instalação Rápida

**Opção 1 - Usando `uv` (recomendado):**
```bash
# Clone o repositório
git clone https://github.com/diegomoura09/HubPDF.git
cd HubPDF

# Instale dependências
pip install uv
uv sync

# Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Execute o servidor
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Opção 2 - Usando pip tradicional:**
```bash
git clone https://github.com/diegomoura09/HubPDF.git
cd HubPDF

pip install -r requirements.txt

cp .env.example .env
# Edite o .env

uvicorn main:app --host 0.0.0.0 --port 8000
```

### Configuração de Ambiente

Crie o arquivo `.env` com as seguintes variáveis:

```ini
# Ambiente
DEBUG=True
ENVIRONMENT=development

# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost/hubpdf
# Ou use SQLite para desenvolvimento:
# DATABASE_URL=sqlite:///./data/app.db

# Segurança
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET=sua-chave-jwt-aqui
CSRF_SECRET=sua-chave-csrf-aqui

# OAuth Google (opcional)
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret

# Mercado Pago (opcional)
MERCADOPAGO_ACCESS_TOKEN=seu-token-mp
```

**Acesse:** http://localhost:8000

---

## 📁 Estrutura do Projeto

```
HubPDF/
├── app/                        # Código principal da aplicação
│   ├── routers/                # Endpoints FastAPI
│   │   ├── auth.py             # Autenticação e login
│   │   ├── tools.py            # Ferramentas de PDF
│   │   └── admin.py            # Painel administrativo
│   ├── services/               # Lógica de negócio
│   │   ├── pdf_service.py      # Manipulação de PDFs
│   │   ├── auth_service.py     # Serviços de autenticação
│   │   └── compression_service.py  # Compressão avançada
│   ├── middleware.py           # Middlewares de segurança
│   ├── models.py               # Modelos SQLAlchemy
│   ├── database.py             # Configuração do banco
│   └── config.py               # Configurações gerais
├── templates/                  # Templates Jinja2
│   ├── auth/                   # Páginas de autenticação
│   ├── tools/                  # Páginas de ferramentas
│   └── base.html               # Template base
├── static/                     # Arquivos estáticos
│   ├── css/                    # Estilos customizados
│   ├── js/                     # JavaScript
│   └── images/                 # Imagens e ícones
├── scripts/                    # Scripts auxiliares
├── data/                       # Banco de dados SQLite (dev)
├── main.py                     # Ponto de entrada da aplicação
├── requirements.txt            # Dependências Python
└── README.md                   # Este arquivo
```

---

## 🔐 Segurança

O HubPDF implementa múltiplas camadas de segurança:

- **HTTPS Obrigatório** em produção
- **Headers de Segurança** (CSP, X-Frame-Options, HSTS)
- **Rate Limiting** para prevenir abuso
- **CSRF Protection** em todos os formulários
- **Sanitização de Inputs** para prevenir XSS
- **Senhas com Argon2** (resistente a GPU cracking)
- **Cookies Seguros** com flags HttpOnly e Secure

---

## 💬 FAQ

Dúvidas frequentes sobre o sistema? Acesse:  
👉 **[hubpdf.pro/faq](https://hubpdf.pro/faq)**

---

## 🌱 Extensão Universitária

Projeto desenvolvido como **intervenção extensionista** no eixo **Economia Sustentável**, alinhado aos Objetivos de Desenvolvimento Sustentável (ODS) da ONU:

- **ODS 8** – Trabalho decente e crescimento econômico  
- **ODS 12** – Consumo e produção responsáveis  

### Impacto Social
- Democratização de ferramentas de produtividade
- Redução de custos com software proprietário
- Economia de papel através de digitalização eficiente
- Inclusão digital e acessibilidade

---

## 👨‍💻 Autor

**Diego Moura de Andrade**  
Curso: CST em Análise e Desenvolvimento de Sistemas  
Instituição: Cruzeiro do Sul / BrazCubas  

📧 E-mail: diego.andrade@cs.brazcubas.edu.br  
🐙 GitHub: [@diegomoura09](https://github.com/diegomoura09)  
💼 LinkedIn: [linkedin.com/in/-andrade](https://linkedin.com/in/-andrade)  

*Sistema desenvolvido como parte das atividades de extensão universitária, sem fins lucrativos.*

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 🐛 Reportar Problemas

Encontrou um bug? [Abra uma issue](https://github.com/diegomoura09/HubPDF/issues) descrevendo:
- O que você esperava que acontecesse
- O que realmente aconteceu
- Passos para reproduzir o problema
- Screenshots (se aplicável)

---

## 📊 Status do Projeto

- ✅ **Versão Beta:** Funcional e estável
- 🚀 **Ferramentas Core:** 8 ferramentas principais
- 👥 **Usuários Ativos:** Sistema aberto para cadastro
- 🔄 **Atualizações:** Melhorias contínuas

---

## 🌐 Acesso Online

**Produção:** [hubpdf.pro](https://hubpdf.pro)  
**Repositório:** [github.com/diegomoura09/HubPDF](https://github.com/diegomoura09/HubPDF)

---

## ⚖️ Licença

Distribuído sob a **Licença MIT**. Veja `LICENSE` para mais informações.

Copyright © 2025 Diego Moura de Andrade

---

## 🙏 Agradecimentos

- Comunidade Python e FastAPI
- Universidade Cruzeiro do Sul / BrazCubas
- Todos os usuários e colaboradores do projeto

---

**Versão Atual:** 2.0 - Novembro/2025  
**Última Atualização:** 10/11/2025  
**Desenvolvido com ❤️ no Brasil** 🇧🇷
