"""
Centralized template helpers for HubPDF
"""
from fastapi.templating import Jinja2Templates
import json

# Create centralized templates instance
templates = Jinja2Templates(directory="templates")

# Portuguese translations (embedded - no i18n system needed)
PT_TRANSLATIONS = {
  "title": "HubPDF",
  "subtitle": "Hub de Ferramentas PDF",
  "meta_description": "Hub completo de ferramentas PDF gratuitas com processamento seguro e sustentável",
  
  "nav_home": "Início",
  "nav_tools": "Ferramentas",
  "nav_dashboard": "Painel",
  "nav_about": "Sobre",
  "nav_contact": "Contato",
  "nav_privacy": "Privacidade",
  "nav_terms": "Termos",
  "nav_admin": "Admin",
  
  "btn_login": "Entrar",
  "btn_register": "Registrar",
  "btn_logout": "Sair",
  "btn_download": "Baixar",
  "btn_get_started": "Começar",
  "btn_start_editing": "Começar a Editar",
  "btn_view_dashboard": "Ver Painel",
  "btn_use_tool": "Usar Ferramenta",
  "btn_try_again": "Tentar Novamente",
  "btn_get_help": "Obter Ajuda",
  "btn_go_to_dashboard": "Ir para Painel",
  "btn_start_using_tools": "Começar a Usar",
  "btn_send_message": "Enviar Mensagem",
  "btn_merge_pdfs": "Mesclar PDFs",
  "btn_split_pdf": "Dividir PDF",
  "btn_compress_pdf": "Compactar PDF",
  "btn_convert_to_images": "Converter para Imagens",
  "btn_create_pdf": "Criar PDF",
  "btn_extract_text": "Extrair Texto",
  
  "hero_title": "Todas as ferramentas PDF que você precisa",
  "hero_description": "Plataforma gratuita para processar seus arquivos PDF com segurança e privacidade. Desenvolvida em cumprimento de projeto acadêmico, sistema sem fins lucrativos.",
  
  "features_title": "Ferramentas Digitais",
  "features_description": "Aproveite as ferramentas gratuitas disponíveis para trabalhar com arquivos PDF",
  
  "tools_title": "Ferramentas PDF",
  "tools_description": "Selecione a ferramenta que você precisa para processar seus arquivos PDF",
  
  "tool_merge": "Mesclar PDFs",
  "tool_merge_description": "Combine múltiplos arquivos PDF em um único documento",
  "tool_merge_short_description": "Combine múltiplos PDFs",
  
  "tool_split": "Dividir PDF",
  "tool_split_description": "Divida um PDF em múltiplos arquivos por intervalos de páginas",
  "tool_split_short_description": "Divida PDF por páginas",
  
  "tool_compress": "Compactar PDF",
  "tool_compress_description": "Reduza o tamanho do arquivo PDF mantendo a qualidade",
  "tool_compress_short_description": "Reduza o tamanho do arquivo",
  
  "tool_pdf_to_images": "PDF para Imagens",
  "tool_pdf_to_images_description": "Converta páginas de PDF em imagens PNG, JPG ou JPEG",
  "tool_pdf_to_images_short_description": "Converta PDF em imagens",
  
  "tool_images_to_pdf": "Imagens para PDF",
  "tool_images_to_pdf_description": "Crie um PDF a partir de múltiplas imagens",
  "tool_images_to_pdf_short_description": "Crie PDF de imagens",
  
  "tool_extract_text": "Extrair Texto",
  "tool_extract_text_description": "Extraia todo o texto de um arquivo PDF",
  "tool_extract_text_short_description": "Extraia texto do PDF",
  
  "security_title": "Segurança e Privacidade",
  "security_description": "Seus arquivos são processados com máxima segurança e privacidade",
  "security_encryption": "Criptografia",
  "security_encryption_description": "Todos os uploads são criptografados em trânsito",
  "security_temporary": "Temporário",
  "security_temporary_description": "Arquivos são excluídos automaticamente após 30 minutos",
  "security_privacy": "Privacidade",
  "security_privacy_description": "Nunca armazenamos ou compartilhamos seus documentos",
  
  "pricing_title": "100% Gratuito e Educacional",
  "pricing_subtitle": "Ferramentas PDF sem custos ou limitações",
  "pricing_description": "Plataforma educacional desenvolvida para uso público e sem fins lucrativos",
  "pricing_contact_text": "Tem dúvidas sobre o HubPDF?",
  
  "plan_free": "Gratuito",
  
  "free_forever": "100% Gratuito",
  
  "dashboard": "Painel",
  "dashboard_welcome": "Bem-vindo, {name}!",
  "quick_actions": "Ações Rápidas",
  "upgrade_notice_title": "Plataforma Gratuita",
  "upgrade_notice_description": "Todas as ferramentas disponíveis gratuitamente para uso ilimitado.",
  "upgrade_for_more": "Ver Ferramentas",
  "watermark_notice_title": "Plataforma Educacional",
  "watermark_notice_description": "Sistema desenvolvido sem fins lucrativos para uso público.",
  "view_all_tools": "Ver todas as ferramentas",
  "usage_today": "Uso hoje",
  
  "login_title": "Entre na sua conta",
  "login_subtitle": "Ainda não tem conta?",
  "login_register_link": "Registre-se aqui",
  "login_with_google": "Entrar com Google",
  
  "register_title": "Crie sua conta",
  "register_subtitle": "Já tem uma conta?",
  "register_login_link": "Entre aqui",
  "register_with_google": "Registrar com Google",
  "register_terms_prefix": "Eu aceito os",
  "register_terms_and": "e a",
  
  "email_label": "Email",
  "email_placeholder": "seu@email.com",
  "password_label": "Senha",
  "password_placeholder": "••••••••",
  "confirm_password_label": "Confirmar Senha",
  "confirm_password_placeholder": "••••••••",
  "name_label": "Nome Completo",
  "name_placeholder": "Seu nome",
  "forgot_password": "Esqueceu a senha?",
  "or": "ou",
  
  "select_pdf_file": "Selecione um arquivo PDF",
  "select_pdf_files": "Selecione arquivos PDF",
  "select_image_files": "Selecione arquivos de imagem",
  "upload_file": "Escolher arquivo",
  "upload_files": "Escolher arquivos",
  "or_drag_and_drop": "ou arraste e solte",
  "pdf_files_only": "Apenas arquivos PDF",
  "image_files_only": "Apenas arquivos de imagem",
  "selected_files": "Arquivos selecionados",
  "drag_to_reorder": "Arraste para reordenar",
  
  "page_ranges_label": "Intervalos de páginas",
  "page_ranges_placeholder": "1-3,5,7-9",
  "page_ranges_help": "Ex: 1-3,5,7-9 (intervalos separados por vírgula)",
  
  "output_format": "Formato de saída",
  "format_help": "PNG oferece melhor qualidade, JPG arquivos menores",
  
  "processing": "Processando",
  "instructions": "Instruções",
  
  "merge_instruction_1": "Selecione múltiplos arquivos PDF para mesclar",
  "merge_instruction_2": "Os arquivos serão mesclados na ordem selecionada",
  "merge_instruction_3": "O resultado será um único arquivo PDF",
  "merge_instruction_4": "Processamento gratuito e ilimitado",
  
  "split_instruction_1": "Selecione um arquivo PDF para dividir",
  "split_instruction_2": "Digite os intervalos de páginas (ex: 1-3,5,7-9)",
  "split_instruction_3": "Cada intervalo será um arquivo PDF separado",
  "split_instruction_4": "O resultado será um arquivo ZIP com os PDFs",
  
  "compress_instruction_1": "Selecione um arquivo PDF para compactar",
  "compress_instruction_2": "O arquivo será otimizado para menor tamanho",
  "compress_instruction_3": "A qualidade será preservada sempre que possível",
  "compress_instruction_4": "Ideal para envios por email ou upload",
  
  "pdf_to_images_instruction_1": "Selecione um arquivo PDF para converter",
  "pdf_to_images_instruction_2": "Cada página será convertida em uma imagem",
  "pdf_to_images_instruction_3": "Escolha o formato: PNG para qualidade, JPG para tamanho",
  "pdf_to_images_instruction_4": "O resultado será um arquivo ZIP com as imagens",
  
  "images_to_pdf_instruction_1": "Selecione múltiplas imagens para converter",
  "images_to_pdf_instruction_2": "As imagens serão organizadas em páginas",
  "images_to_pdf_instruction_3": "A ordem das imagens será preservada",
  "images_to_pdf_instruction_4": "Formatos aceitos: JPG, PNG, GIF, BMP",
  
  "extract_text_instruction_1": "Selecione um arquivo PDF para extrair texto",
  "extract_text_instruction_2": "Todo texto legível será extraído",
  "extract_text_instruction_3": "Textos em imagens não serão extraídos",
  "extract_text_instruction_4": "O resultado será um arquivo de texto",
  
  "watermark_text": "Gerado com HubPDF",
  
  "msg_error": "Ocorreu um erro",
  "quota_exceeded": "Sistema temporariamente indisponível. Tente novamente em alguns instantes.",
  "file_too_large": "Arquivo muito grande. Tamanho máximo: {max_size}MB",
  
  
  "need_help": "Precisa de ajuda?",
  "contact_support": "Entre em contato",
  "contact_us": "Fale conosco",
  
  "date": "Data",
  "description": "Descrição",
  "status": "Status",
  
  "status_active": "Ativo",
  "status_cancelled": "Cancelado",
  "status_expired": "Expirado",
  "status_pending": "Pendente",
  "status_paid": "Pago",
  "status_failed": "Falhou",
  
  "admin_dashboard": "Painel Administrativo",
  "admin_dashboard_description": "Gerencie usuários, assinaturas e visualize estatísticas",
  "back_to_admin": "Voltar ao Admin",
  
  "total_users": "Total de Usuários",
  "active_users": "Usuários Ativos",
  "active_subscriptions": "Assinaturas Ativas",
  "revenue_30_days": "Receita (30 dias)",
  "recent_registrations": "Registros Recentes",
  "last_7_days": "Últimos 7 dias",
  "new_users": "novos usuários",
  "user_growth_chart_placeholder": "Gráfico de crescimento de usuários em breve",
  "recent_admin_actions": "Ações Administrativas Recentes",
  "view_all": "Ver todas",
  "no_recent_actions": "Nenhuma ação recente",
  
  "manage_users": "Gerenciar Usuários",
  "view_edit_users": "Visualizar e editar usuários",
  "manage_subscriptions": "Gerenciar Assinaturas",
  "view_edit_subscriptions": "Visualizar e editar assinaturas",
  "manage_coupons": "Gerenciar Cupons",
  "create_edit_coupons": "Criar e editar cupons",
  "view_invoices": "Ver Faturas",
  
  "search_users_placeholder": "Buscar por nome ou email...",
  "search": "Buscar",
  "clear": "Limpar",
  "user": "Usuário",
  "joined": "Cadastro",
  "actions": "Ações",
  "active": "Ativo",
  "inactive": "Inativo",
  "deactivate": "Desativar",
  "activate": "Ativar",
  "reset_quota": "Resetar Cota",
  "promote": "Promover",
  "admin": "Admin",
  "no_users_found": "Nenhum usuário encontrado",
  "previous": "Anterior",
  "next": "Próximo",
  "confirm_reset_quota": "Tem certeza que deseja resetar a cota diária deste usuário?",
  "confirm_promote_user": "Tem certeza que deseja promover este usuário a administrador?",
  
  "total_subscriptions": "Total de Assinaturas",
  "all_statuses": "Todos os Status",
  "filter": "Filtrar",
  "period": "Período",
  "start": "Início",
  "end": "Fim",
  "extend": "Estender",
  "cancel": "Cancelar",
  "details": "Detalhes",
  "no_subscriptions_found": "Nenhuma assinatura encontrada",
  "extend_subscription": "Estender Assinatura",
  "extend_by_days": "Estender por (dias)",
  "confirm_cancel_subscription": "Tem certeza que deseja cancelar esta assinatura?",
  "subscription_details_coming_soon": "Detalhes da assinatura em breve",
  
  "create_and_manage_promo_codes": "Criar e gerenciar códigos promocionais",
  "create_coupon": "Criar Cupom",
  "code": "Código",
  "discount": "Desconto",
  "validity": "Validade",
  "usage": "Uso",
  "created": "Criado",
  "from": "De",
  "until": "Até",
  "unlimited": "Ilimitado",
  "no_coupons_found": "Nenhum cupom encontrado",
  "create_first_coupon": "Criar primeiro cupom",
  "create_new_coupon": "Criar Novo Cupom",
  "coupon_code": "Código do Cupom",
  "coupon_code_placeholder": "Ex: DESCONTO20",
  "discount_percentage": "Porcentagem de Desconto",
  "valid_from": "Válido de",
  "valid_until": "Válido até",
  "usage_limit": "Limite de Uso",
  "unlimited_if_empty": "Ilimitado se vazio",
  
  "total_invoices": "Total de Faturas",
  "total_revenue": "Receita Total",
  "paid_invoices": "Faturas Pagas",
  "pending_invoices": "Faturas Pendentes",
  "failed_invoices": "Faturas Falhadas",
  "invoice_id": "ID da Fatura",
  "due_date": "Vencimento",
  "paid_date": "Data do Pagamento",
  "view_in_mp": "Ver no MP",
  "no_invoices_found": "Nenhuma fatura encontrada",
  "invoice_details": "Detalhes da Fatura",
  "loading_invoice_details": "Carregando detalhes da fatura",
  "loading": "Carregando",
  "invoice_details_placeholder": "Detalhes completos da fatura em breve",
  
  "audit_logs": "Logs de Auditoria",
  
  "action_reset_quota": "resetou a cota de",
  "action_activate": "ativou",
  "action_deactivate": "desativou",
  "action_promote": "promoveu",
  "action_extend_subscription": "estendeu a assinatura de",
  "action_cancel_subscription": "cancelou a assinatura de",
  "action_create_coupon": "criou o cupom",
  "action_activate_coupon": "ativou o cupom",
  "action_deactivate_coupon": "desativou o cupom",
  
  "target_user": "usuário",
  "target_subscription": "assinatura",
  "target_coupon": "cupom",
  
  "about_title": "Sobre o HubPDF",
  "about_subtitle": "Ferramentas Digitais Sustentáveis",
  "about_description_1": "O HubPDF é um sistema web desenvolvido com foco em segurança, privacidade e eficiência no processamento de documentos digitais. A plataforma foi criada como projeto acadêmico extensionista do curso CST em Análise e Desenvolvimento de Sistemas da Cruzeiro do Sul / Braz Cubas, com objetivo de oferecer soluções tecnológicas acessíveis e sustentáveis para a sociedade.",
  "about_mission_title": "Missão",
  "about_mission_description": "Facilitar o acesso à tecnologia e incentivar o uso consciente de ferramentas digitais que reduzam o desperdício de recursos físicos e promovam a sustentabilidade documental.",
  "about_features_title": "Objetivo",
  "about_feature_1": "Oferecer ferramentas confiáveis e gratuitas para manipulação simples de PDFs",
  "about_feature_2": "Evitar dependência de softwares pagos ou complexos",
  "about_feature_3": "Garantir exclusão automática de arquivos após o uso",
  "about_feature_4": "Atender às diretrizes da Lei nº 13.709/2018 (LGPD), respeitando a privacidade do usuário",
  "about_feature_5": "",
  "about_security_title": "Segurança e Privacidade",
  "about_security_description": "Todos os arquivos são processados de forma local e excluídos automaticamente, sem qualquer registro permanente.",
  "about_contact_title": "Contato",
  "about_contact_description": "Dúvidas ou sugestões? Acesse a página",
  
  "privacy_policy_title": "Política de Privacidade – HubPDF",
  "privacy_last_updated": "Base Legal: Lei nº 13.709/2018 (LGPD)",
  "privacy_section_1_title": "",
  "privacy_section_1_content": "O HubPDF não coleta, armazena nem compartilha arquivos enviados para processamento. Os documentos são tratados de forma local e excluídos automaticamente após o uso.",
  "privacy_section_2_title": "Cookies",
  "privacy_section_2_content": "São utilizados apenas cookies técnicos, necessários para funcionamento básico do site. Não usamos cookies de rastreamento, publicidade ou perfilamento.",
  "privacy_section_3_title": "Segurança",
  "privacy_section_3_content": "Os arquivos são processados com criptografia local e exclusão imediata. Nenhum dado é armazenado em servidores ou acessado por pessoas.",
  "privacy_section_4_title": "Contato sobre Privacidade",
  "privacy_section_4_content": "E-mail: diego.andrade@cs.brazcubas.edu.br",
  "privacy_section_5_title": "",
  "privacy_section_5_content": "",
  "privacy_contact_title": "Página",
  "privacy_contact_content": "",
  
  "terms_of_service_title": "Termos de Uso – HubPDF",
  "terms_last_updated": "Desenvolvido por: Diego Moura de Andrade – CST ADS, Cruzeiro do Sul / Braz Cubas",
  "terms_section_1_title": "Natureza do Serviço",
  "terms_section_1_content": "O HubPDF é uma ferramenta gratuita e educacional para processamento de PDFs (mesclar, dividir, converter, etc.), sem fins comerciais.",
  "terms_section_2_title": "Uso Responsável",
  "terms_section_2_content": "O usuário compromete-se a utilizar a plataforma apenas para fins legais e éticos, não enviando arquivos ilícitos, confidenciais de terceiros ou protegidos por direitos autorais.",
  "terms_section_3_title": "Limitação de Responsabilidade",
  "terms_section_3_content": "Os arquivos são processados automaticamente e excluídos após o uso. O sistema é fornecido \"como está\", sem garantias de funcionamento contínuo ou suporte técnico.",
  "terms_section_4_title": "Atualizações",
  "terms_section_4_content": "Os termos podem ser alterados a qualquer momento, sem aviso prévio. A versão mais recente estará sempre disponível nesta página.",
  "terms_section_5_title": "",
  "terms_section_5_content": "",
  "terms_contact_title": "",
  "terms_contact_content": "",
  
  "contact_title": "Entre em Contato",
  "contact_subtitle": "Use o formulário abaixo para enviar sua mensagem.",
  "contact_info_title": "Informações de Contato",
  "contact_email_title": "E-mail direto",
  "contact_hours_title": "",
  "contact_hours_content": "",
  "contact_support_title": "",
  "contact_support_content": "",
  "contact_form_title": "Envie uma Mensagem",
  "contact_name_label": "Nome",
  "contact_email_label": "Email",
  "contact_subject_label": "Assunto",
  "contact_message_label": "Mensagem",
  "contact_subject_feedback": "Feedback",
  "contact_subject_report_error": "Reportar Erro",
  "contact_subject_suggestions": "Sugestões",
  
  "faq_title": "Perguntas Frequentes",
  "faq_question_1": "Como funciona a segurança dos arquivos?",
  "faq_answer_1": "Todos os arquivos são criptografados durante o upload e processamento, e são automaticamente excluídos após 30 minutos.",
  "faq_question_2": "Posso cancelar minha assinatura a qualquer momento?",
  "faq_answer_2": "Sim, você pode cancelar sua assinatura a qualquer momento através do painel de controle.",
  "faq_question_3": "Qual a diferença entre os planos?",
  "faq_answer_3": "Os planos diferem no tamanho máximo de arquivo, número de operações diárias e presença de marca d'água.",
  "faq_question_4": "Como funciona o período de teste?",
  "faq_answer_4": "Você pode testar todas as funcionalidades do plano Pro por 7 dias gratuitamente.",
  
  "footer_description": "Ferramentas Digitais Sustentáveis",
  "footer_tools": "Ferramentas",
  "footer_company": "HubPDF – Ferramentas Digitais Sustentáveis",
  "footer_note": "Sistema gratuito desenvolvido por Diego Moura de Andrade – CST ADS, Cruzeiro do Sul / Braz Cubas.",
  "footer_copyright": "© 2025 HubPDF – Sistema gratuito desenvolvido por Diego Moura de Andrade (CST ADS – Cruzeiro do Sul / Braz Cubas)"
}

def t(key: str, default: str | None = None, **kwargs) -> str:
    """Translation function - returns Portuguese text (platform is Portuguese-only)"""
    text = PT_TRANSLATIONS.get(key, default or key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text

def price_brl(value: float) -> str:
    """Format price in Brazilian Real (BRL) format with comma as decimal separator"""
    txt = f"{value:,.2f}"
    return "R$ " + txt.replace(",", "X").replace(".", ",").replace("X", ".")

# Register global functions
templates.env.globals["price_brl"] = price_brl
templates.env.globals["t"] = t
