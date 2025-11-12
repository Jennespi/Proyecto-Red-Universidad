// admin-logs.js
class AdminLogs {
    constructor() {
        this.currentPage = 1;
        this.filters = {};
        this.init();
    }

    init() {
        this.loadLogs();
        this.setupFilters();
        this.setupAutoRefresh();
    }

    loadLogs(page = 1, filters = {}) {
        const url = new URL('/admin/api/logs', window.location.origin);
        url.searchParams.set('pagina', page);
        
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                url.searchParams.set(key, filters[key]);
            }
        });

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar logs');
                return response.json();
            })
            .then(data => {
                this.renderLogs(data.logs);
                this.renderPagination(data.paginacion);
            })
            .catch(error => {
                console.error('Error:', error);
                this.showError('Error al cargar los logs');
            });
    }

    renderLogs(logs) {
        const container = document.querySelector('.logs-container');
        if (!container) return;

        if (!logs || logs.length === 0) {
            container.innerHTML = '<div class="no-logs">No se encontraron registros</div>';
            return;
        }

        container.innerHTML = logs.map(log => `
            <div class="log-item log-level-${this.getLogLevel(log.accion)}">
                <div class="log-header">
                    <span class="log-user">${log.usuario_nombre || 'Sistema'}</span>
                    <span class="log-time">${new Date(log.fecha_hora).toLocaleString()}</span>
                </div>
                <div class="log-action">${log.accion}</div>
                ${log.detalles ? `<div class="log-details">${log.detalles}</div>` : ''}
                ${log.ip_address ? `<div class="log-meta">IP: ${log.ip_address}</div>` : ''}
            </div>
        `).join('');
    }

    getLogLevel(action) {
        if (action.includes('ERROR') || action.includes('FALLO')) return 'error';
        if (action.includes('LOGIN') || action.includes('ACCESO')) return 'info';
        if (action.includes('CONFIG')) return 'warning';
        return 'default';
    }

    setupFilters() {
        const filterForm = document.querySelector('.logs-filters');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(filterForm);
                this.filters = Object.fromEntries(formData);
                this.loadLogs(1, this.filters);
            });

            // Limpiar filtros
            const clearBtn = document.querySelector('.clear-filters');
            if (clearBtn) {
                clearBtn.addEventListener('click', () => {
                    filterForm.reset();
                    this.filters = {};
                    this.loadLogs(1);
                });
            }
        }
    }

    setupAutoRefresh() {
        // Actualizar logs cada 60 segundos
        setInterval(() => {
            this.loadLogs(this.currentPage, this.filters);
        }, 60000);
    }

    renderPagination(pagination) {
        // Similar al de usuarios
    }

    showError(message) {
        if (window.adminDashboard) {
            window.adminDashboard.showNotification(message, 'error');
        }
    }
}

// Inicializar sistema de logs
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.logs-container')) {
        window.adminLogs = new AdminLogs();
    }
});