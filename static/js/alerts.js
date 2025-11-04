/**
 * HubPDF - Sistema de Alertas
 * Componente reutilizável para exibir alertas (success, error, warning, info)
 */

class AlertSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    /**
     * Inicializa o container de alertas
     */
    init() {
        // Criar container se não existir
        if (!document.getElementById('alert-container')) {
            this.container = document.createElement('div');
            this.container.id = 'alert-container';
            this.container.className = 'fixed top-4 right-4 z-50 space-y-3 max-w-md';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('alert-container');
        }
    }

    /**
     * Exibe um alerta
     * @param {Object} options - Opções do alerta
     * @param {string} options.message - Mensagem (pode conter HTML)
     * @param {string} options.type - Tipo: 'success', 'error', 'warning', 'info'
     * @param {number} options.duration - Duração em ms (0 = não fecha automaticamente)
     * @param {boolean} options.dismissible - Se pode ser fechado pelo usuário
     */
    show({ message, type = 'info', duration = 10000, dismissible = true }) {
        const alert = this.createAlert(message, type, dismissible);
        this.container.appendChild(alert);

        // Animação de entrada
        setTimeout(() => {
            alert.classList.add('alert-show');
        }, 10);

        // Auto-close
        if (duration > 0) {
            setTimeout(() => {
                this.close(alert);
            }, duration);
        }

        return alert;
    }

    /**
     * Cria o elemento HTML do alerta
     */
    createAlert(message, type, dismissible) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-animated`;
        
        // Ícones por tipo
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };

        // Cores por tipo
        const colors = {
            success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
            error: 'bg-red-50 border-red-200 text-red-800',
            warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
            info: 'bg-blue-50 border-blue-200 text-blue-800'
        };

        const iconColors = {
            success: 'text-emerald-500',
            error: 'text-red-500',
            warning: 'text-yellow-500',
            info: 'text-blue-500'
        };

        alert.className += ` ${colors[type]}`;

        alert.innerHTML = `
            <div class="flex items-start p-4 rounded-xl border-2 shadow-lg backdrop-blur-sm bg-white/90">
                <div class="flex-shrink-0">
                    <i data-lucide="${icons[type]}" class="h-5 w-5 ${iconColors[type]}"></i>
                </div>
                <div class="ml-3 flex-1">
                    <div class="text-sm font-medium alert-message">${message}</div>
                </div>
                ${dismissible ? `
                    <button class="ml-3 flex-shrink-0 alert-close" aria-label="Fechar">
                        <i data-lucide="x" class="h-5 w-5 text-slate-400 hover:text-slate-600"></i>
                    </button>
                ` : ''}
            </div>
        `;

        // Inicializar ícones Lucide
        if (typeof lucide !== 'undefined') {
            lucide.createIcons({ nameAttr: 'data-lucide' });
        }

        // Botão de fechar
        if (dismissible) {
            const closeBtn = alert.querySelector('.alert-close');
            closeBtn.addEventListener('click', () => this.close(alert));
        }

        return alert;
    }

    /**
     * Fecha um alerta
     */
    close(alert) {
        alert.classList.remove('alert-show');
        alert.classList.add('alert-hide');
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }

    /**
     * Atalhos para tipos específicos
     */
    success(message, duration = 5000) {
        return this.show({ message, type: 'success', duration });
    }

    error(message, duration = 10000) {
        return this.show({ message, type: 'error', duration });
    }

    warning(message, duration = 8000) {
        return this.show({ message, type: 'warning', duration });
    }

    info(message, duration = 6000) {
        return this.show({ message, type: 'info', duration });
    }

    /**
     * Limpa todos os alertas
     */
    clearAll() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// CSS para animações (injetado dinamicamente)
const alertStyles = document.createElement('style');
alertStyles.textContent = `
    .alert-animated {
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .alert-show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .alert-hide {
        opacity: 0;
        transform: translateX(100%);
    }

    .alert-message a {
        font-weight: 600;
        text-decoration: underline;
        transition: opacity 0.2s;
    }

    .alert-message a:hover {
        opacity: 0.8;
    }
`;
document.head.appendChild(alertStyles);

// Instância global
window.alerts = new AlertSystem();
