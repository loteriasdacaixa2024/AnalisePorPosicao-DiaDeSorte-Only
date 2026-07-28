// Sistema: Análise por Posição - Dia de Sorte
// Desenvolvido para: Márcio Fernando Maia

// ==================== CONFIGURAÇÕES GLOBAIS ====================

const API_BASE_URL = window.location.origin;

// ==================== FUNÇÕES DE AUTENTICAÇÃO ====================

/**
 * Verifica se o usuário está autenticado
 */
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

/**
 * Obtém o token de acesso
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Obtém o refresh token
 */
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

/**
 * Salva os tokens no localStorage
 */
function saveTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
    }
}

/**
 * Remove os tokens (logout)
 */
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

/**
 * Renova o access token usando o refresh token
 */
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            saveTokens(data.access_token, null);
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Erro ao renovar token:', error);
        return false;
    }
}

// ==================== FUNÇÕES DE API ====================

/**
 * Realiza requisição autenticada à API
 */
async function fetchAPI(url, options = {}) {
    const token = getAccessToken();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        let response = await fetch(`${API_BASE_URL}${url}`, mergedOptions);
        
        // Se token expirou, tenta renovar
        if (response.status === 401 && token) {
            const renewed = await refreshAccessToken();
            
            if (renewed) {
                // Tenta novamente com o novo token
                mergedOptions.headers['Authorization'] = `Bearer ${getAccessToken()}`;
                response = await fetch(`${API_BASE_URL}${url}`, mergedOptions);
            } else {
                // Falha ao renovar, fazer logout
                clearTokens();
                window.location.href = '/login';
                return null;
            }
        }
        
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// ==================== FUNÇÕES DE UI ====================

/**
 * Mostra alerta na página
 */
function showAlert(message, type = 'info', duration = 5012) {
    const alertContainer = document.getElementById('alertContainer');
    
    if (!alertContainer) {
        console.warn('Container de alertas não encontrado');
        return;
    }
    
    const alertId = `alert-${Date.now()}`;
    
    const alert = document.createElement('div');
    alert.id = alertId;
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    const icons = {
        'success': 'fa-check-circle',
        'danger': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    
    alert.innerHTML = `
        <i class="fas ${icons[type] || icons.info} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remover após duração
    if (duration > 0) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, duration);
    }
}

/**
 * Mostra loading em um elemento
 */
function showLoading(element, text = 'Carregando...') {
    if (!element) return;
    
    element.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">${text}</span>
            </div>
            <p class="mt-2 text-muted">${text}</p>
        </div>
    `;
}

/**
 * Mostra mensagem de erro em um elemento
 */
function showError(element, message = 'Erro ao carregar dados') {
    if (!element) return;
    
    element.innerHTML = `
        <div class="text-center py-5 text-danger">
            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Mostra mensagem de vazio em um elemento
 */
function showEmpty(element, message = 'Nenhum resultado encontrado') {
    if (!element) return;
    
    element.innerHTML = `
        <div class="text-center py-5 text-muted">
            <i class="fas fa-inbox fa-3x mb-3"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Modal de confirmação customizado
 */
function showConfirmDialog(message, onConfirm, onCancel = null) {
    const modalId = `confirmModal-${Date.now()}`;
    
    const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle text-warning me-2"></i>
                            Confirmação
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="${modalId}-cancel">
                            Cancelar
                        </button>
                        <button type="button" class="btn btn-primary" id="${modalId}-confirm">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    
    document.getElementById(`${modalId}-confirm`).addEventListener('click', () => {
        modal.hide();
        if (onConfirm) onConfirm();
    });
    
    document.getElementById(`${modalId}-cancel`).addEventListener('click', () => {
        modal.hide();
        if (onCancel) onCancel();
    });
    
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.remove();
    });
    
    modal.show();
}

/**
 * Modal de alerta customizado
 */
function showAlertDialog(message, type = 'info') {
    const modalId = `alertModal-${Date.now()}`;
    
    const icons = {
        'success': { icon: 'fa-check-circle', color: 'text-success' },
        'danger': { icon: 'fa-exclamation-circle', color: 'text-danger' },
        'warning': { icon: 'fa-exclamation-triangle', color: 'text-warning' },
        'info': { icon: 'fa-info-circle', color: 'text-info' }
    };
    
    const config = icons[type] || icons.info;
    
    const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas ${config.icon} ${config.color} me-2"></i>
                            Aviso
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                            OK
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.remove();
    });
    
    modal.show();
}

// ==================== FUNÇÕES UTILITÁRIAS ====================

/**
 * Formata data para padrão brasileiro
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString('pt-BR');
}

/**
 * Formata número com separadores de milhar
 */
function formatNumber(number) {
    return new Intl.NumberFormat('pt-BR').format(number);
}

/**
 * Debounce para otimizar buscas
 */
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

/**
 * Copia texto para clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copiado para a área de transferência!', 'success', 2000);
        return true;
    } catch (error) {
        console.error('Erro ao copiar:', error);
        showAlert('Erro ao copiar para área de transferência', 'danger');
        return false;
    }
}

/**
 * Download de arquivo
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Valida email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Marca link ativo no navbar
 */
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href === currentPath || (currentPath !== '/' && href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    // Marcar link ativo no navbar
    setActiveNavLink();
    
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    console.log('✅ Scripts.js carregado com sucesso');
});

// ==================== EXPORTAR FUNÇÕES GLOBAIS ====================

window.AppUtils = {
    // Auth
    isAuthenticated,
    getAccessToken,
    getRefreshToken,
    saveTokens,
    clearTokens,
    refreshAccessToken,
    
    // API
    fetchAPI,
    
    // UI
    showAlert,
    showLoading,
    showError,
    showEmpty,
    showConfirmDialog,
    showAlertDialog,
    
    // Utils
    formatDate,
    formatNumber,
    debounce,
    copyToClipboard,
    downloadFile,
    isValidEmail,
    setActiveNavLink
};