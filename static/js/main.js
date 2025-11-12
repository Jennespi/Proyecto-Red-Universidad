// main.js - JavaScript principal para toda la aplicación
class MainApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupGlobalEventListeners();
        this.setupNavigation();
        this.setupForms();
        this.setupUIComponents();
        this.setupNotifications();
        this.setupSessionManagement();
    }

    // =============================================
    // MANEJO DE NAVEGACIÓN Y RUTAS
    // =============================================

    setupNavigation() {
        // Navegación suave para enlaces internos
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="/"]') || e.target.closest('a[href^="/"]')) {
                const link = e.target.closest('a');
                this.handleInternalNavigation(link);
            }
        });

        // Prevenir navegación en enlaces con data-prevent-default
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-prevent-default') || 
                e.target.closest('[data-prevent-default]')) {
                e.preventDefault();
            }
        });
    }

    handleInternalNavigation(link) {
        const href = link.getAttribute('href');
        
        // Si es un enlace de logout, manejar especial
        if (href === '/logout') {
            this.handleLogout(link);
            return;
        }

        // Si tiene data-confirm, pedir confirmación
        if (link.hasAttribute('data-confirm')) {
            const message = link.getAttribute('data-confirm') || '¿Estás seguro?';
            if (!confirm(message)) {
                return;
            }
        }

        // Mostrar loading para navegaciones que puedan tardar
        if (!link.hasAttribute('data-no-loading')) {
            this.showLoading();
        }
    }

    // =============================================
    // MANEJO DE FORMULARIOS
    // =============================================

    setupForms() {
        // Validación automática de formularios
        document.addEventListener('submit', (e) => {
            this.handleFormSubmit(e);
        });

        // Validación en tiempo real
        document.addEventListener('input', (e) => {
            if (e.target.matches('input[required], textarea[required], select[required]')) {
                this.validateField(e.target);
            }
        });

        // Manejo de campos de contraseña
        this.setupPasswordFields();
    }

    handleFormSubmit(e) {
        const form = e.target;
        
        // Prevenir envío si tiene data-prevent-default
        if (form.hasAttribute('data-prevent-default')) {
            e.preventDefault();
            return;
        }

        // Validar formulario antes de enviar
        if (!this.validateForm(form)) {
            e.preventDefault();
            this.showNotification('Por favor, completa todos los campos requeridos correctamente.', 'error');
            return;
        }

        // Mostrar loading en el botón de submit
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn && !form.hasAttribute('data-no-loading')) {
            this.disableSubmitButton(submitBtn);
        }
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        // Validación especial para contraseñas
        const passwordFields = form.querySelectorAll('input[type="password"]');
        if (passwordFields.length >= 2) {
            const password = passwordFields[0].value;
            const confirmPassword = passwordFields[1].value;
            
            if (password !== confirmPassword && password && confirmPassword) {
                this.showFieldError(passwordFields[1], 'Las contraseñas no coinciden');
                isValid = false;
            }
        }

        return isValid;
    }

    validateField(field) {
        this.clearFieldError(field);

        // Validaciones básicas
        if (field.hasAttribute('required') && !field.value.trim()) {
            this.showFieldError(field, 'Este campo es requerido');
            return false;
        }

        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                this.showFieldError(field, 'Por favor ingresa un email válido');
                return false;
            }
        }

        if (field.hasAttribute('minlength') && field.value.length < field.getAttribute('minlength')) {
            this.showFieldError(field, `Mínimo ${field.getAttribute('minlength')} caracteres`);
            return false;
        }

        if (field.hasAttribute('maxlength') && field.value.length > field.getAttribute('maxlength')) {
            this.showFieldError(field, `Máximo ${field.getAttribute('maxlength')} caracteres`);
            return false;
        }

        // Si pasa todas las validaciones
        this.showFieldSuccess(field);
        return true;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        field.classList.remove('success');
        
        let errorElement = field.parentNode.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    showFieldSuccess(field) {
        field.classList.remove('error');
        field.classList.add('success');
        this.clearFieldError(field);
    }

    clearFieldError(field) {
        field.classList.remove('error', 'success');
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    setupPasswordFields() {
        // Toggle visibilidad de contraseña
        document.addEventListener('click', (e) => {
            if (e.target.matches('.toggle-password') || e.target.closest('.toggle-password')) {
                const toggle = e.target.closest('.toggle-password');
                const input = toggle.previousElementSibling;
                
                if (input.type === 'password') {
                    input.type = 'text';
                    toggle.textContent = '👁️';
                } else {
                    input.type = 'password';
                    toggle.textContent = '👁️‍🗨️';
                }
            }
        });
    }

    disableSubmitButton(button) {
        const originalText = button.innerHTML;
        button.innerHTML = `
            <span class="loading-spinner-small"></span>
            Procesando...
        `;
        button.disabled = true;
        
        // Restaurar después de 10 segundos por si hay error
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 10000);
    }

    // =============================================
    // COMPONENTES DE INTERFAZ
    // =============================================

    setupUIComponents() {
        // Tooltips
        this.setupTooltips();
        
        // Modales
        this.setupModals();
        
        // Acordeones
        this.setupAccordions();
        
        // Tabs
        this.setupTabs();
    }

    setupTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip);
            element.addEventListener('mouseleave', this.hideTooltip);
        });
    }

    showTooltip(e) {
        const tooltipText = this.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
        
        this._currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this._currentTooltip) {
            this._currentTooltip.remove();
            this._currentTooltip = null;
        }
    }

    setupModals() {
        document.addEventListener('click', (e) => {
            // Abrir modal
            if (e.target.matches('[data-modal-open]')) {
                const modalId = e.target.getAttribute('data-modal-open');
                this.openModal(modalId);
            }
            
            // Cerrar modal
            if (e.target.matches('[data-modal-close], .modal-overlay')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });

        // Cerrar modal con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.active');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    setupAccordions() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.accordion-header') || e.target.closest('.accordion-header')) {
                const header = e.target.closest('.accordion-header');
                const accordion = header.parentNode;
                const content = header.nextElementSibling;
                
                accordion.classList.toggle('active');
                content.style.maxHeight = accordion.classList.contains('active') ? content.scrollHeight + 'px' : '0';
            }
        });
    }

    setupTabs() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tab-header') || e.target.closest('.tab-header')) {
                const tabHeader = e.target.closest('.tab-header');
                const tabsContainer = tabHeader.closest('.tabs');
                const tabIndex = Array.from(tabsContainer.querySelectorAll('.tab-header')).indexOf(tabHeader);
                
                this.switchTab(tabsContainer, tabIndex);
            }
        });
    }

    switchTab(tabsContainer, index) {
        const headers = tabsContainer.querySelectorAll('.tab-header');
        const contents = tabsContainer.querySelectorAll('.tab-content');
        
        headers.forEach(header => header.classList.remove('active'));
        contents.forEach(content => content.classList.remove('active'));
        
        headers[index].classList.add('active');
        contents[index].classList.add('active');
    }

    // =============================================
    // SISTEMA DE NOTIFICACIONES
    // =============================================

    setupNotifications() {
        // Auto-remover notificaciones flash después de 5 segundos
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            setTimeout(() => {
                this.fadeOut(message, () => message.remove());
            }, 5000);
        });
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Cerrar manualmente
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hideNotification(notification);
        });

        // Auto-remover
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }

        return notification;
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    // =============================================
    // MANEJO DE SESIÓN Y AUTENTICACIÓN
    // =============================================

    setupSessionManagement() {
        // Verificar sesión periódicamente (cada 5 minutos)
        setInterval(() => {
            this.checkSession();
        }, 300000);

        // Manejar inactividad del usuario (30 minutos)
        this.setupInactivityTimer(1800000);
    }

    checkSession() {
        // En una implementación real, harías una petición al servidor
        // para verificar si la sesión sigue activa
        console.log('Verificando sesión...');
    }

    setupInactivityTimer(timeout) {
        let inactivityTimer;
        
        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                this.handleInactivity();
            }, timeout);
        };
        
        // Resetear timer en eventos de usuario
        ['mousemove', 'keypress', 'click', 'scroll'].forEach(event => {
            document.addEventListener(event, resetTimer, { passive: true });
        });
        
        resetTimer();
    }

    handleInactivity() {
        // Mostrar advertencia de inactividad
        if (this.isUserOnProtectedPage()) {
            this.showNotification(
                'Tu sesión expirará pronto por inactividad. ¿Quieres continuar?',
                'warning',
                10000
            );
        }
    }

    isUserOnProtectedPage() {
        return !['/login', '/registro'].includes(window.location.pathname);
    }

    handleLogout(link) {
        if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
            this.showLoading();
            // La navegación normal continuará
        } else {
            if (link) link.blur();
        }
    }

    // =============================================
    // UTILIDADES GENERALES
    // =============================================

    setupGlobalEventListeners() {
        // Prevenir acciones dobles
        this.preventDoubleSubmission();
        
        // Manejar errores globales
        this.setupErrorHandling();
        
        // Mejoras de accesibilidad
        this.setupAccessibility();
    }

    preventDoubleSubmission() {
        let isSubmitting = false;
        
        document.addEventListener('submit', () => {
            if (isSubmitting) {
                event.preventDefault();
                return;
            }
            isSubmitting = true;
            
            // Resetear después de 3 segundos
            setTimeout(() => {
                isSubmitting = false;
            }, 3000);
        });
    }

    setupErrorHandling() {
        window.addEventListener('error', (e) => {
            console.error('Error global:', e.error);
            this.showNotification('Ha ocurrido un error inesperado.', 'error');
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Promise rechazada:', e.reason);
            this.showNotification('Error en la aplicación.', 'error');
            e.preventDefault();
        });
    }

    setupAccessibility() {
        // Mejorar focus para navegación por teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Saltar al contenido principal
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const mainContent = document.querySelector('main');
                if (mainContent) {
                    mainContent.setAttribute('tabindex', '-1');
                    mainContent.focus();
                }
            });
        }
    }

    showLoading(message = 'Cargando...') {
        // Implementar overlay de loading si es necesario
        console.log('Loading:', message);
    }

    hideLoading() {
        // Ocultar overlay de loading
        console.log('Loading completo');
    }

    fadeOut(element, callback) {
        element.style.transition = 'opacity 0.3s ease';
        element.style.opacity = '0';
        setTimeout(() => {
            if (callback) callback();
        }, 300);
    }

    // =============================================
    // API Y COMUNICACIÓN CON EL SERVIDOR
    // =============================================

    async apiCall(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API call failed:', error);
            this.showNotification('Error de conexión con el servidor', 'error');
            throw error;
        }
    }

    // =============================================
    // MANEJO DE FECHAS Y FORMATOS
    // =============================================

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    relativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Ahora mismo';
        if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
        if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
        if (diffDays < 7) return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
        
        return this.formatDate(dateString);
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.mainApp = new MainApp();
    
    // Exponer utilidades globalmente para uso en consola
    window.AppUtils = {
        showNotification: (message, type) => window.mainApp.showNotification(message, type),
        formatDate: (date) => window.mainApp.formatDate(date),
        formatDateTime: (date) => window.mainApp.formatDateTime(date),
        relativeTime: (date) => window.mainApp.relativeTime(date)
    };
});

// Manejar cuando la página se vuelve visible (pestaña activa)
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // La pestaña se volvió visible, podrías actualizar datos
        console.log('Página visible - actualizando...');
    }
});