/**
 * HubPDF - Main Application JavaScript
 * Handles file uploads, drag & drop, HTMX interactions, and UI enhancements
 */

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Main application initialization
 */
function initializeApp() {
    initializeCSRF();
    initializeFileUpload();
    initializeDropZones();
    initializeToasts();
    initializeMobileMenu();
    initializeProgressBars();
    initializeFormValidation();
    initializeTableSorting();
    initializeModals();
    
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    console.log('HubPDF app initialized');
}

/**
 * Initialize CSRF token handling
 */
function initializeCSRF() {
    // Get CSRF token from cookie and add to forms
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
        document.querySelectorAll('input[name="csrf_token"]').forEach(input => {
            input.value = csrfToken;
        });
        
        // Set up CSRF for HTMX requests
        if (typeof htmx !== 'undefined') {
            document.body.addEventListener('htmx:configRequest', function(evt) {
                const currentToken = getCookie('csrf_token') || csrfToken;
                if (currentToken) {
                    evt.detail.headers['X-CSRF-Token'] = currentToken;
                }
            });
        }
    }
}

/**
 * Get cookie value by name
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * File Upload Functionality
 */
function initializeFileUpload() {
    // Handle file input changes
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function(e) {
            handleFileSelection(e.target);
            validateFileSize(e.target);
        });
    });
}

/**
 * Handle file selection and display
 */
function handleFileSelection(input) {
    const files = Array.from(input.files);
    const fileListContainer = document.getElementById('file-list');
    const fileItemsContainer = document.getElementById('file-items');
    
    if (!fileListContainer || !fileItemsContainer) return;
    
    if (files.length > 0) {
        fileListContainer.classList.remove('hidden');
        fileItemsContainer.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileItem = createFileListItem(file, index);
            fileItemsContainer.appendChild(fileItem);
        });
        
        // Re-initialize Feather icons for new elements
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    } else {
        fileListContainer.classList.add('hidden');
    }
}

/**
 * Create file list item element
 */
function createFileListItem(file, index) {
    const li = document.createElement('li');
    li.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg border';
    
    const fileSize = formatFileSize(file.size);
    const fileIcon = getFileIcon(file.type);
    
    li.innerHTML = `
        <div class="flex items-center">
            <div class="file-icon ${getFileIconClass(file.type)}">
                <i data-feather="${fileIcon}" class="h-4 w-4"></i>
            </div>
            <div>
                <div class="text-sm font-medium text-gray-900">${escapeHtml(file.name)}</div>
                <div class="text-xs text-gray-500">${fileSize}</div>
            </div>
        </div>
        <button type="button" onclick="removeFile(${index})" class="text-red-600 hover:text-red-700">
            <i data-feather="x" class="h-4 w-4"></i>
        </button>
    `;
    
    return li;
}

/**
 * Get appropriate icon for file type
 */
function getFileIcon(mimeType) {
    if (mimeType === 'application/pdf') return 'file-text';
    if (mimeType.startsWith('image/')) return 'image';
    return 'file';
}

/**
 * Get CSS class for file icon
 */
function getFileIconClass(mimeType) {
    if (mimeType === 'application/pdf') return 'pdf';
    if (mimeType.startsWith('image/')) return 'image';
    return 'generic';
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Validate file sizes based on user plan
 */
function validateFileSize(input) {
    const ABSOLUTE_MAX_SIZE = 60 * 1024 * 1024; // 60MB hard limit
    const maxSize = parseInt(input.dataset.maxSize) || (60 * 1024 * 1024); // Default 60MB
    const effectiveMaxSize = Math.min(maxSize, ABSOLUTE_MAX_SIZE); // Never exceed 60MB
    const files = Array.from(input.files);
    const oversizedFiles = files.filter(file => file.size > effectiveMaxSize);
    
    if (oversizedFiles.length > 0) {
        const maxSizeMB = Math.round(effectiveMaxSize / (1024 * 1024));
        
        // Check if file exceeded absolute limit
        const exceedsAbsoluteLimit = oversizedFiles.some(file => file.size > ABSOLUTE_MAX_SIZE);
        
        if (exceedsAbsoluteLimit) {
            const largestFile = oversizedFiles.reduce((max, file) => file.size > max.size ? file : max);
            const fileSizeFormatted = formatFileSize(largestFile.size);
            const errorMessage = `Este serviço gratuito aceita arquivos de até 60 MB. O seu arquivo possui ${fileSizeFormatted}. Por favor, envie um arquivo menor.`;
            
            if (window.alerts) {
                window.alerts.error(errorMessage);
            } else {
                showToast(errorMessage, 'error');
            }
        } else {
            if (window.alerts) {
                window.alerts.error(`Arquivo muito grande! Tamanho máximo: ${maxSizeMB}MB`);
            } else {
                showToast(`Arquivo muito grande! Tamanho máximo: ${maxSizeMB}MB`, 'error');
            }
        }
        
        // Remove oversized files
        const validFiles = files.filter(file => file.size <= effectiveMaxSize);
        const dt = new DataTransfer();
        validFiles.forEach(file => dt.items.add(file));
        input.files = dt.files;
        
        handleFileSelection(input);
    }
}

/**
 * Remove file from selection
 */
function removeFile(index) {
    const fileInput = document.querySelector('input[type="file"][multiple]');
    if (!fileInput) return;
    
    const files = Array.from(fileInput.files);
    files.splice(index, 1);
    
    const dt = new DataTransfer();
    files.forEach(file => dt.items.add(file));
    fileInput.files = dt.files;
    
    handleFileSelection(fileInput);
}

/**
 * Drag and Drop Functionality
 */
function initializeDropZones() {
    document.querySelectorAll('.dropzone, [data-dropzone]').forEach(dropzone => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => highlight(dropzone), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => unhighlight(dropzone), false);
        });
        
        dropzone.addEventListener('drop', handleDrop, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(element) {
    element.classList.add('dragover');
}

function unhighlight(element) {
    element.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    const fileInput = e.currentTarget.querySelector('input[type="file"]');
    
    if (fileInput && files.length > 0) {
        fileInput.files = files;
        handleFileSelection(fileInput);
        validateFileSize(fileInput);
    }
}

/**
 * Toast Notifications
 */
function initializeToasts() {
    // Auto-hide existing toasts
    document.querySelectorAll('.toast').forEach(toast => {
        setTimeout(() => hideToast(toast), 5000);
    });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <i data-feather="${getToastIcon(type)}" class="h-5 w-5"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">${escapeHtml(message)}</p>
            </div>
            <div class="ml-auto pl-3">
                <button onclick="hideToast(this.closest('.toast'))" class="text-gray-400 hover:text-gray-600">
                    <i data-feather="x" class="h-4 w-4"></i>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Re-initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => hideToast(toast), 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'alert-circle';
        case 'warning': return 'alert-triangle';
        default: return 'info';
    }
}

function hideToast(toast) {
    if (toast && toast.parentNode) {
        toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }
}

/**
 * Mobile Menu
 */
function initializeMobileMenu() {
    const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

/**
 * Progress Bars
 */
function initializeProgressBars() {
    // HTMX progress indicators
    document.addEventListener('htmx:xhr:progress', function(e) {
        const progressBar = document.querySelector('.upload-progress-bar');
        if (progressBar && e.detail.lengthComputable) {
            const percentComplete = (e.detail.loaded / e.detail.total) * 100;
            progressBar.style.width = percentComplete + '%';
        }
    });
    
    // Show/hide progress on HTMX requests
    document.addEventListener('htmx:beforeRequest', function(e) {
        const form = e.target.closest('form');
        if (form && form.querySelector('input[type="file"]')) {
            showUploadProgress();
        }
    });
    
    document.addEventListener('htmx:afterRequest', function(e) {
        hideUploadProgress();
    });
}

function showUploadProgress() {
    const progressContainer = document.createElement('div');
    progressContainer.className = 'upload-progress';
    progressContainer.innerHTML = '<div class="upload-progress-bar" style="width: 0%"></div>';
    
    const form = document.querySelector('form[enctype="multipart/form-data"]');
    if (form) {
        form.appendChild(progressContainer);
    }
}

function hideUploadProgress() {
    const progressContainer = document.querySelector('.upload-progress');
    if (progressContainer) {
        setTimeout(() => progressContainer.remove(), 1000);
    }
}

/**
 * Form Validation
 */
function initializeFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => validateField(field));
            field.addEventListener('input', () => clearFieldError(field));
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type || 'text';
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Password validation
    if (fieldType === 'password' && value && field.name === 'password') {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters long';
        }
    }
    
    // Confirm password validation
    if (field.name === 'confirm_password' && value) {
        const passwordField = field.form.querySelector('input[name="password"]');
        if (passwordField && value !== passwordField.value) {
            isValid = false;
            errorMessage = 'Passwords do not match';
        }
    }
    
    // Show/hide error
    if (isValid) {
        showFieldSuccess(field);
    } else {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    field.classList.remove('success');
    
    let errorElement = field.parentNode.querySelector('.form-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
}

function showFieldSuccess(field) {
    field.classList.remove('error');
    field.classList.add('success');
    
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
}

function clearFieldError(field) {
    field.classList.remove('error', 'success');
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Table Sorting
 */
function initializeTableSorting() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => sortTable(header));
    });
}

function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = !header.classList.contains('asc');
    
    // Remove sort classes from all headers
    header.parentNode.querySelectorAll('.sortable').forEach(h => {
        h.classList.remove('asc', 'desc');
    });
    
    // Add sort class to current header
    header.classList.add(isAscending ? 'asc' : 'desc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers first
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Modal Functionality
 */
function initializeModals() {
    // Close modals when clicking backdrop
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-backdrop')) {
            const modal = e.target.closest('.modal, [id$="-modal"]');
            if (modal) {
                closeModal(modal);
            }
        }
    });
    
    // Close modals with escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal:not(.hidden), [id$="-modal"]:not(.hidden)');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea, button');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

/**
 * Utility Functions
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * HTMX Event Handlers
 */
document.addEventListener('htmx:responseError', function(e) {
    showToast('Ocorreu um erro ao processar sua solicitação', 'error');
});

document.addEventListener('htmx:timeout', function(e) {
    showToast('Tempo limite esgotado. Por favor, tente novamente.', 'error');
});

document.addEventListener('htmx:beforeRequest', function(e) {
    // Disable submit buttons during request
    const submitButtons = e.target.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(btn => {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.innerHTML = '<i class="animate-spin h-4 w-4 mr-2" data-feather="loader"></i>Processando...';
    });
});

document.addEventListener('htmx:afterRequest', function(e) {
    // Re-enable submit buttons
    const submitButtons = e.target.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(btn => {
        btn.disabled = false;
        if (btn.dataset.originalText) {
            btn.textContent = btn.dataset.originalText;
            delete btn.dataset.originalText;
        }
    });
    
    // Re-initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
});

/**
 * Language Switcher
 */
function switchLanguage(locale) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/set-language';
    
    const languageInput = document.createElement('input');
    languageInput.type = 'hidden';
    languageInput.name = 'language';
    languageInput.value = locale;
    
    const redirectInput = document.createElement('input');
    redirectInput.type = 'hidden';
    redirectInput.name = 'redirect_url';
    redirectInput.value = window.location.pathname;
    
    form.appendChild(languageInput);
    form.appendChild(redirectInput);
    document.body.appendChild(form);
    form.submit();
}

/**
 * PWA Installation
 */
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallButton();
});

function showInstallButton() {
    const installButton = document.getElementById('install-app');
    if (installButton) {
        installButton.classList.remove('hidden');
        installButton.addEventListener('click', installApp);
    }
}

function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt');
            }
            deferredPrompt = null;
        });
    }
}

/**
 * Service Worker Registration
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export functions for global use
window.HubPDF = {
    showToast,
    hideToast,
    openModal,
    closeModal,
    switchLanguage,
    formatFileSize,
    validateForm,
    escapeHtml,
    debounce,
    throttle
};
