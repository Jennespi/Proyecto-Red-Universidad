// admin-users.js
class AdminUsers {
    constructor() {
        this.currentPage = 1;
        this.searchTerm = '';
        this.init();
    }

    init() {
        this.loadUsers();
        this.setupEventListeners();
        this.setupSearch();
    }

    loadUsers(page = 1, search = '') {
        const url = new URL('/admin/api/usuarios', window.location.origin);
        url.searchParams.set('pagina', page);
        if (search) {
            url.searchParams.set('busqueda', search);
        }

        this.showLoading();

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar usuarios');
                return response.json();
            })
            .then(data => {
                this.renderUsers(data.usuarios);
                this.renderPagination(data.paginacion);
                this.hideLoading();
            })
            .catch(error => {
                console.error('Error:', error);
                this.showError('Error al cargar los usuarios');
                this.hideLoading();
            });
    }

    renderUsers(users) {
        const tbody = document.querySelector('.users-table tbody');
        if (!tbody) return;

        if (!users || users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-data">
                        No se encontraron usuarios
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr data-user-id="${user.id}">
                <td>${user.id}</td>
                <td>
                    <div class="user-info">
                        <span class="username">${user.username}</span>
                        ${user.ultimo_acceso ? `
                            <small class="last-access">
                                Último acceso: ${new Date(user.ultimo_acceso).toLocaleDateString()}
                            </small>
                        ` : ''}
                    </div>
                </td>
                <td>${user.email}</td>
                <td>
                    <span class="role-badge role-${user.rol}">${user.rol}</span>
                </td>
                <td>
                    <span class="status-badge ${user.activo ? 'active' : 'inactive'}">
                        ${user.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>${new Date(user.fecha_registro).toLocaleDateString()}</td>
                <td>
                    <div class="user-actions">
                        <button class="btn btn-sm btn-edit" onclick="adminUsers.editUser(${user.id})">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-toggle-status ${user.activo ? 'btn-warning' : 'btn-success'}" 
                                onclick="adminUsers.toggleUserStatus(${user.id}, ${user.activo})">
                            ${user.activo ? 'Desactivar' : 'Activar'}
                        </button>
                        ${user.rol !== 'admin' ? `
                            <button class="btn btn-sm btn-danger" onclick="adminUsers.deleteUser(${user.id})">
                                Eliminar
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderPagination(pagination) {
        const paginationContainer = document.querySelector('.pagination');
        if (!paginationContainer) return;

        const { pagina_actual, total_paginas } = pagination;
        
        let html = '';
        
        if (pagina_actual > 1) {
            html += `<button class="btn-pagination" onclick="adminUsers.loadUsers(${pagina_actual - 1})">← Anterior</button>`;
        }
        
        html += `<span class="pagination-info">Página ${pagina_actual} de ${total_paginas}</span>`;
        
        if (pagina_actual < total_paginas) {
            html += `<button class="btn-pagination" onclick="adminUsers.loadUsers(${pagina_actual + 1})">Siguiente →</button>`;
        }
        
        paginationContainer.innerHTML = html;
    }

    setupSearch() {
        const searchInput = document.querySelector('.search-users');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchTerm = e.target.value;
                    this.loadUsers(1, this.searchTerm);
                }, 500);
            });
        }
    }

    editUser(userId) {
        // Implementar edición de usuario
        console.log('Editar usuario:', userId);
        // Aquí iría el modal de edición
    }

    toggleUserStatus(userId, currentStatus) {
        if (!confirm(`¿Estás seguro de que quieres ${currentStatus ? 'desactivar' : 'activar'} este usuario?`)) {
            return;
        }

        fetch(`/admin/api/usuarios/${userId}/estado`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                activo: !currentStatus
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al actualizar estado');
            return response.json();
        })
        .then(data => {
            this.showNotification(`Usuario ${!currentStatus ? 'activado' : 'desactivado'} correctamente`, 'success');
            this.loadUsers(this.currentPage, this.searchTerm);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Error al actualizar el usuario', 'error');
        });
    }

    deleteUser(userId) {
        if (!confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.')) {
            return;
        }

        fetch(`/admin/api/usuarios/${userId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al eliminar usuario');
            return response.json();
        })
        .then(data => {
            this.showNotification('Usuario eliminado correctamente', 'success');
            this.loadUsers(this.currentPage, this.searchTerm);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Error al eliminar el usuario', 'error');
        });
    }

    showLoading() {
        // Implementar spinner de carga
    }

    hideLoading() {
        // Ocultar spinner de carga
    }

    showNotification(message, type) {
        // Reutilizar el sistema de notificaciones del dashboard
        if (window.adminDashboard) {
            window.adminDashboard.showNotification(message, type);
        }
    }

    setupEventListeners() {
        // Event listeners adicionales
    }
}

// Inicializar gestión de usuarios
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.users-table')) {
        window.adminUsers = new AdminUsers();
    }
});