# 🧩 HubPDF

Sistema web desenvolvido como parte do curso **CST em Análise e Desenvolvimento de Sistemas** (Cruzeiro do Sul / BrazCubas).  
O HubPDF oferece ferramentas simples e gratuitas para **manipulação de arquivos PDF**, com foco em **eficiência, acessibilidade e sustentabilidade digital**.

---

## 🚀 Funcionalidades
- Converter imagens em PDF  
- Mesclar múltiplos PDFs  
- Dividir arquivos PDF  
- Comprimir e reduzir tamanho  
- Extrair texto de documentos  
- Converter PDF para Word e Excel *(em desenvolvimento)*  
- Interface responsiva e compatível com celulares  

---

## 🛠️ Tecnologias Utilizadas
**Backend:** Python + FastAPI  
**Frontend:** HTML, CSS e JavaScript (CSS, HTMX)  
**Servidor:** Uvicorn  
**Implantação:** Replit Cloud com domínio próprio  
**Banco de dados:** PostgreSQL  

---

## 📦 Upload de Arquivos
- **Tamanho ilimitado**, podendo haver lentidão em arquivos muito grandes.  
- Arquivos com baixa qualidade ou já muito reduzidos podem apresentar falhas na leitura.  
- Sistema validado para os formatos principais: PDF, JPG, PNG, DOCX e XLSX.  

---

## 🧭 Executando Localmente

### Pré-requisitos
- Python 3.10 ou superior  
- `pip` ou `uv` instalado  

### Opção A – Usando `uv` (recomendado)
```bash
pip install uv
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Opção B – Usando pip
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Configuração de Ambiente
Crie o arquivo `.env` com suas variáveis:

```ini
DATABASE_URL=postgresql://...
SECRET_KEY=...
JWT_SECRET=...
CSRF_SECRET=...
```

Acesse: **http://localhost:8000**

---

## 📁 Estrutura do Projeto
```
HubPDF/
├── app/                    # Código principal
│   ├── routers/            # Rotas e endpoints FastAPI
│   ├── services/           # Funções de manipulação de PDF
│   ├── models.py           # Modelos e ORM
│   └── ...
├── templates/              # Páginas HTML
├── static/                 # CSS, JS, imagens
├── scripts/                # Scripts auxiliares
├── main.py                 # Ponto de entrada
└── README.md               # Este arquivo
```

---

## 💬 FAQ
Acesse o FAQ do sistema em:  
👉 **https://hubpdf.pro/faq**

---

## 🌱 Extensão Universitária
Projeto desenvolvido como intervenção extensionista no eixo **Economia Sustentável**, alinhado aos Objetivos de Desenvolvimento Sustentável:

- **ODS 8** – Trabalho decente e crescimento econômico  
- **ODS 12** – Consumo e produção responsáveis  

---

## 👨‍💻 Autor
**Diego Moura de Andrade**  
Curso: CST em Análise e Desenvolvimento de Sistemas  
E-mail: diego.andrade@cs.brazcubas.edu.br  
GitHub: [diegomoura09](https://github.com/diegomoura09)  
LinkedIn: [linkedin.com/in/diegomouradeandrade](https://linkedin.com/in/diegomouradeandrade)  

*Sistema desenvolvido como parte das atividades de extensão universitária, sem fins lucrativos.*

---

## 🌐 Acesso Online
Acesse gratuitamente: **https://hubpdf.pro**

---

## ⚖️ Licença
Distribuído sob a licença MIT.

---

**Versão Atual:** Novembro/2025  
**Repositório oficial:** [github.com/diegomoura09/HubPDF](https://github.com/diegomoura09/HubPDF)
