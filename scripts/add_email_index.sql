-- Migração: Adicionar índice único case-insensitive para email
-- Garantir que emails sejam únicos independente de maiúsculas/minúsculas

-- Remover índice antigo se existir
DROP INDEX IF EXISTS ix_users_email;

-- Criar índice único em lower(email)
CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_idx ON users (LOWER(email));

-- Comentário de confirmação
SELECT 'Índice users_email_lower_idx criado com sucesso!' AS status;
