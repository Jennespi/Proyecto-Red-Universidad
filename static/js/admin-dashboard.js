// admin-dashboard.js
class AdminDashboard {
    constructor() {
        this.charts = {};
        this.isLoading = false;
        this.init();
    }

    init() {
        this.loadCharts();
        this.setupRealTimeUpdates();
        this.setupEventListeners();
        this.showLoadingState();
    }

    // Mostrar estado de carga
    showLoadingState() {
        const chartContainer = document.querySelector('.chart-container');
        if (chartContainer) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'chart-loading';
            loadingDiv.innerHTML = `
                <div class="loading-spinner"></div>
                <p>Cargando datos...</p>
            `;
            chartContainer.appendChild(loadingDiv);
        }
    }

    // Ocultar estado de carga
    hideLoadingState() {
        const loadingDiv = document.querySelector('.chart-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    // Cargar todas las gráficas
    loadCharts() {
        this.loadActivityChart();
        this.loadRealTimeStats();
    }

    // Gráfica principal de actividad con datos reales
    loadActivityChart() {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        this.isLoading = true;
        
        fetch('/admin/api/actividad?dias=7')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                this.createActivityChart(ctx, data);
                this.isLoading = false;
                this.hideLoadingState();
            })
            .catch(error => {
                console.error('Error loading activity data:', error);
                this.showError('No se pudieron cargar los datos de actividad');
                this.isLoading = false;
                this.hideLoadingState();
            });
    }

    createActivityChart(ctx, data) {
        if (this.charts.activity) {
            this.charts.activity.destroy();
        }

        // Verificar que tenemos datos válidos
        if (!data || !data.labels || !data.data) {
            this.showError('Datos de actividad no disponibles');
            return;
        }

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Actividad Diaria',
                    data: data.data,
                    borderColor: '#00733B',
                    backgroundColor: 'rgba(0, 115, 59, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#00733B',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Actividad: ${context.parsed.y} eventos`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Eventos de Actividad'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    }
                }
            }
        });
    }

    // Actualizar estadísticas en tiempo real desde BD
    loadRealTimeStats() {
        this.updateStats();
        // Actualizar cada 30 segundos
        setInterval(() => this.updateStats(), 30000);
    }

    updateStats() {
        fetch('/admin/api/estadisticas')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al obtener estadísticas');
                }
                return response.json();
            })
            .then(data => {
                this.updateStatCards(data);
            })
            .catch(error => {
                console.error('Error updating stats:', error);
                this.showError('Error al actualizar estadísticas');
            });
    }

    updateStatCards(stats) {
        const statElements = {
            'total_usuarios': '.stat-card:nth-child(1) .stat-number',
            'total_mensajes': '.stat-card:nth-child(2) .stat-number',
            'actividad_hoy': '.stat-card:nth-child(3) .stat-number'
        };

        Object.keys(statElements).forEach(key => {
            const element = document.querySelector(statElements[key]);
            if (element && stats[key] !== undefined) {
                const currentValue = parseInt(element.textContent) || 0;
                const newValue = stats[key];
                
                if (currentValue !== newValue) {
                    this.animateValue(element, currentValue, newValue, 1000);
                }
            }
        });

        // Actualizar registros activos (calculado)
        const activeElement = document.querySelector('.stat-card:nth-child(4) .stat-number');
        if (activeElement) {
            const totalUsuarios = stats.total_usuarios || 0;
            const actividadHoy = stats.actividad_hoy || 0;
            const newValue = totalUsuarios + actividadHoy;
            const currentValue = parseInt(activeElement.textContent) || 0;
            
            if (currentValue !== newValue) {
                this.animateValue(activeElement, currentValue, newValue, 1000);
            }
        }
    }

    animateValue(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateValue = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const value = Math.floor(start + (end - start) * easeOutQuart);
            
            element.textContent = value.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateValue);
            }
        };
        
        requestAnimationFrame(updateValue);
    }

    // Configurar event listeners
    setupEventListeners() {
        // Botón de actualizar gráfica
        const refreshBtn = document.querySelector('.btn-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshCharts();
            });
        }

        // Actualizar automáticamente cada 2 minutos
        setInterval(() => {
            if (!this.isLoading) {
                this.refreshCharts();
            }
        }, 120000);
    }

    refreshCharts() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showNotification('Actualizando datos...', 'info');
        
        Promise.all([
            this.loadActivityChart(),
            this.updateStats()
        ]).finally(() => {
            this.isLoading = false;
            this.showNotification('Datos actualizados correctamente', 'success');
        });
    }

    // Sistema de notificaciones
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `admin-notification admin-notification-${type}`;
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

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);

        // Cerrar manualmente
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification);
        });
    }

    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    showError(message) {
        this.showNotification(message, 'error');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.adminDashboard = new AdminDashboard();
});