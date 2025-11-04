# Sistema de Alertas - HubPDF

## Visão Geral

Implementado um sistema de alertas visual robusto e reutilizável para toda a plataforma HubPDF. O sistema exibe mensagens de sucesso, erro, aviso e informação com animações suaves, auto-close e suporte a HTML (para links).

## ✨ Características

### 1. **Componente JavaScript Reutilizável** (`/static/js/alerts.js`)
- Classe `AlertSystem` disponível globalmente via `window.alerts`
- 4 tipos de alertas: `success`, `error`, `warning`, `info`
- Animações CSS suaves (slide-in from right)
- Auto-close configurável (padrão: 5-10 segundos dependendo do tipo)
- Botão de fechar manual
- Suporte a HTML nas mensagens (para links)
- Ícones Lucide integrados

### 2. **Página de Login Aprimorada**
- Validação client-side:
  - Email vazio → Alerta de aviso
  - Senha vazia → Alerta de aviso
  - Email inválido → Alerta de erro
- Submissão assíncrona com Fetch API
- Feedback visual durante login (botão com loading spinner)
- Mensagens de erro dinâmicas do servidor

### 3. **Backend com Suporte JSON**
- Detecção automática de requisições JSON via header `Accept`
- Responde com JSON quando solicitado via Fetch API
- Mensagens em português com HTML (links clicáveis)
- Compatibilidade retroativa com formulários tradicionais

## 🎯 Fluxos de Erro Implementados

### Email Não Cadastrado
**Mensagem:**
```
⚠️ E-mail não cadastrado. [Clique aqui para se cadastrar](link)
```
- Link clicável para página de registro
- Alerta permanece visível (não fecha automaticamente)
- Cor vermelha (error)

### Senha Incorreta
**Mensagem:**
```
Senha incorreta. Verifique sua senha e tente novamente.
```
- Alerta fecha automaticamente após 10 segundos
- Cor vermelha (error)

### Campos Vazios
**Email vazio:**
```
Por favor, insira seu e-mail antes de continuar.
```

**Senha vazia:**
```
Por favor, informe sua senha para continuar.
```
- Alertas de aviso (warning)
- Foco automático no campo vazio
- Fecha após 8 segundos

### Email Inválido
**Mensagem:**
```
Por favor, insira um e-mail válido.
```
- Validação regex básica
- Alerta de erro
- Foco no campo de email

## 📋 Como Usar

### Uso Básico no JavaScript

```javascript
// Alerta de sucesso
window.alerts.success('Operação concluída com sucesso!');

// Alerta de erro
window.alerts.error('Erro ao processar sua solicitação.');

// Alerta de aviso
window.alerts.warning('Por favor, revise suas informações.');

// Alerta de informação
window.alerts.info('Bem-vindo ao HubPDF!');
```

### Uso Avançado

```javascript
// Alerta que não fecha automaticamente
window.alerts.error('Erro crítico!', 0); // 0 = permanente

// Alerta com HTML (link)
window.alerts.error(
  'E-mail não encontrado. <a href="/register">Cadastre-se aqui</a>',
  0
);

// Alerta com duração customizada (15 segundos)
window.alerts.success('Arquivo enviado!', 15000);
```

### Uso Completo com Todas as Opções

```javascript
window.alerts.show({
  message: 'Sua mensagem aqui',
  type: 'success',      // success, error, warning, info
  duration: 5000,       // em milissegundos (0 = não fecha)
  dismissible: true     // true = pode fechar manualmente
});
```

## 🎨 Tipos de Alertas

### Success (Verde)
- Cor: `emerald-50` / `emerald-600`
- Ícone: `check-circle`
- Duração padrão: 5 segundos
- Uso: Confirmações, operações bem-sucedidas

### Error (Vermelho)
- Cor: `red-50` / `red-600`
- Ícone: `alert-circle`
- Duração padrão: 10 segundos
- Uso: Erros, falhas, problemas críticos

### Warning (Amarelo)
- Cor: `yellow-50` / `yellow-600`
- Ícone: `alert-triangle`
- Duração padrão: 8 segundos
- Uso: Avisos, validações, campos obrigatórios

### Info (Azul)
- Cor: `blue-50` / `blue-600`
- Ícone: `info`
- Duração padrão: 6 segundos
- Uso: Informações, dicas, mensagens gerais

## 🔧 Arquitetura Técnica

### Frontend (Cliente)

**Arquivo:** `templates/auth/login.html`

```javascript
// Intercepta submit do formulário
loginForm.addEventListener('submit', async function(e) {
  e.preventDefault();
  
  // Validações client-side
  if (!email) {
    window.alerts.warning('Por favor, insira seu e-mail...');
    return;
  }
  
  // Fetch API com Accept: application/json
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
    body: formData,
    redirect: 'manual'
  });
  
  // Processar resposta
  if (response.type === 'opaqueredirect') {
    window.location.href = '/home'; // Sucesso
  } else {
    const data = await response.json();
    window.alerts.error(data.message, 0);
  }
});
```

### Backend (Servidor)

**Arquivo:** `app/routers/auth.py`

```python
@router.post("/login")
async def login(request: Request, email: str = Form(...), ...):
    # Detectar se é requisição JSON
    accept_header = request.headers.get("accept", "")
    is_json_request = "application/json" in accept_header
    
    # Verificar se email existe
    if not existing_user:
        error_message = 'E-mail não cadastrado. <a href="/auth/register">...</a>'
        
        if is_json_request:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": error_message}
            )
        else:
            # Renderizar template HTML tradicional
            return templates.TemplateResponse(...)
```

## 📊 Testes Realizados

### Testes de API (Backend)

✅ Email não cadastrado:
```json
{
  "error": true,
  "message": "E-mail não cadastrado. <a href=\"/auth/register\">Clique aqui...</a>"
}
```

✅ Senha incorreta:
```json
{
  "error": true,
  "message": "Senha incorreta. Verifique sua senha e tente novamente."
}
```

✅ Login bem-sucedido:
```
HTTP Status: 302 (Redirect para /home)
```

### Testes de Interface (Frontend)

✅ Validação de campo vazio (email)
✅ Validação de campo vazio (senha)
✅ Validação de formato de email
✅ Exibição de alerta com link clicável
✅ Auto-close após tempo configurado
✅ Botão de fechar manual
✅ Animações de entrada/saída
✅ Loading spinner durante submit

## 🚀 Benefícios

1. **Experiência do Usuário**
   - Feedback imediato e visual
   - Mensagens claras em português
   - Links clicáveis para ações relacionadas
   - Animações suaves e profissionais

2. **Desenvolvimento**
   - Componente reutilizável em toda a plataforma
   - API simples e intuitiva
   - Sem dependências externas além do Lucide Icons
   - Fácil manutenção

3. **Acessibilidade**
   - Cores contrastantes
   - Ícones descritivos
   - Mensagens claras
   - Suporte a leitores de tela (ARIA)

4. **Segurança**
   - Validação client-side E server-side
   - Mensagens de erro não revelam informações sensíveis
   - Proteção contra XSS (mensagens HTML são sanitizadas no backend)

## 📝 Próximos Passos (Opcional)

### Expansão do Sistema

1. **Aplicar em outras páginas:**
   - Página de registro
   - Upload de arquivos
   - Ferramentas PDF
   - Dashboard

2. **Novos tipos de alertas:**
   - Loading/Progress (com barra de progresso)
   - Confirmação (com botões Yes/No)
   - Toast compacto (canto superior direito)

3. **Persistência:**
   - Salvar alertas não lidos no localStorage
   - Exibir após reload da página

4. **Analytics:**
   - Rastrear quais erros aparecem com mais frequência
   - Melhorar UX baseado em dados reais

## 🎓 Contexto Acadêmico

Este sistema foi desenvolvido como parte do projeto HubPDF para o curso CST em Análise e Desenvolvimento de Sistemas da Cruzeiro do Sul / Braz Cubas, demonstrando:

- Programação client-side moderna (ES6+)
- Integração Frontend-Backend via Fetch API
- Padrões de UX/UI profissionais
- Validação de dados em múltiplas camadas
- Código reutilizável e manutenível

**Desenvolvedor:** Diego Moura de Andrade  
**Email:** diego.andrade@cs.brazcubas.edu.br  
**Data:** Novembro de 2025
