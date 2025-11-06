# 🧩 HubPDF  
Sistema desenvolvido como parte do curso **CST em Análise e Desenvolvimento de Sistemas** (Cruzeiro do Sul / BrazCubas).  
O HubPDF oferece ferramentas simples e seguras para manipulação de arquivos PDF — totalmente gratuito, acessível via web e sem armazenamento permanente de dados.

## 🚀 Funcionalidades
- Converter imagens em PDF  
- Mesclar múltiplos PDFs  
- Dividir arquivos PDF  
- Comprimir e reduzir tamanho  
- Extrair texto  
- Garantia de privacidade (arquivos excluídos automaticamente)

## 🛠️ Tecnologias Utilizadas
- **Backend:** Python + FastAPI  
- **Frontend:** HTML, CSS, JavaScript (Tailwind CSS, HTMX, Alpine.js)
- **Servidor:** Uvicorn (ASGI)
- **Implantação:** Cloud deployment (domínio próprio)
- **Banco de dados:** PostgreSQL (Neon) / SQLite (desenvolvimento local)
- **Autenticação:** JWT + Google OAuth (opcional)

## 📦 Upload de Arquivos
- **Tamanho de arquivo:** Sem limitações (suporta arquivos grandes até 10GB)
- Sistema otimizado para processamento de arquivos de qualquer tamanho
- Validação de tipo de arquivo implementada para segurança
- Mensagens de erro em português brasileiro

## 🏃 Executando Localmente

### Pré-requisitos
- Python 3.10+
- pip ou uv (gerenciador de pacotes Python)

### Opção A: Usando uv (recomendado)
```bash
# Instalar uv
pip install uv

# Sincronizar dependências
uv sync

# Executar aplicação
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Opção B: Usando pip
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Configuração de Ambiente
1. Copie `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite `.env` com suas configurações:
   - `DATABASE_URL`: String de conexão do PostgreSQL
   - `SECRET_KEY`, `JWT_SECRET`, `CSRF_SECRET`: Segredos da aplicação
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: OAuth do Google (opcional)

3. Acesse a aplicação em `http://localhost:8000`

## 📁 Estrutura do Projeto
```
HubPDF/
├── app/                    # Código da aplicação
│   ├── routers/           # Rotas FastAPI
│   ├── services/          # Lógica de negócio
│   ├── models.py          # Modelos do banco de dados
│   └── ...
├── templates/             # Templates Jinja2
├── static/                # CSS, JavaScript, assets
├── docs/                  # Documentação do projeto
│   ├── examples/         # Arquivos de exemplo/teste
│   └── assets/           # Assets de documentação
├── scripts/              # Scripts de banco de dados
├── main.py               # Ponto de entrada da aplicação
└── pyproject.toml        # Dependências (uv/poetry)
```

## 📚 Documentação
- [Correções de Autenticação](docs/AUTHENTICATION_FIXES.md)
- [Sistema de Alertas](docs/SISTEMA_ALERTAS.md)
- [Arquivos de Exemplo](docs/examples/)

## 👨‍💻 Autor
**Diego Moura de Andrade**  
- GitHub: [diegomoura09](https://github.com/diegomoura09)  
- E-mail: diego.andrade@cs.brazcubas.edu.br  
- Sistema desenvolvido em atendimento a requisitos acadêmicos.  

## 🌐 Acesso Online
Acesse gratuitamente: [https://hubpdf.pro](https://hubpdf.pro)

## ⚖️ Licença
Distribuído sob a licença MIT.
