-- Script de seed para usuário de teste
-- Senha: hubpdf123!
-- Hash Argon2 (usado pelo HubPDF)

INSERT INTO users (email, password_hash, name, is_active, email_verified, role, plan, created_at, updated_at)
SELECT 
    'teste@hubpdf.dev',
    '$argon2id$v=19$m=65536,t=3,p=4$kQY9YsBNQFkdwmGl1XNcrQ$XPmdFtT9gwS7dvcRGcCKv01//zHLM05+iQe3V3IdSBU',
    'Usuário Teste',
    true,
    true,
    'user',
    'free',
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE LOWER(email) = 'teste@hubpdf.dev'
);

-- Confirmar inserção
SELECT 'Usuário de teste disponível: teste@hubpdf.dev (senha: hubpdf123!)' AS status;
