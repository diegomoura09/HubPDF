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
- Python + FastAPI  
- HTML, CSS e JavaScript  
- Uvicorn  
- Replit Cloud Deployment  
- Banco de dados Neon (PostgreSQL remoto)

## 📦 Limites de Upload
- **Tamanho máximo por arquivo:** 60 MB (padrão)
- Configurável via variável de ambiente `MAX_UPLOAD_MB`
- Validação implementada em frontend (JavaScript) e backend (FastAPI)
- Mensagens de erro em português brasileiro

### Configuração do Limite de Upload
Para alterar o limite padrão, defina a variável de ambiente:
```bash
MAX_UPLOAD_MB=100  # Exemplo: aumentar para 100 MB
```

### Observação sobre Deployment no Replit
O plano **Autoscale** do Replit pode impor limites adicionais de upload via proxy. Se você precisar enviar arquivos maiores que 60 MB após configurar `MAX_UPLOAD_MB`, considere:
- Migrar para um plano **Reserved VM** no Replit
- Implementar upload direto para serviços de armazenamento (ex: AWS S3 com presigned URLs)  

## 👨‍💻 Autor
**Diego Moura de Andrade**  
- GitHub: [diegomoura09](https://github.com/diegomoura09)  
- E-mail: diego.andrade@cs.brazcubas.edu.br  
- Sistema desenvolvido em atendimento a requisitos acadêmicos.  

## 🌐 Acesso Online
Acesse gratuitamente: [https://hubpdf.pro](https://hubpdf.pro)

## ⚖️ Licença
Distribuído sob a licença MIT.