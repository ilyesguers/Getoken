/**
 * Getoken Dashboard JavaScript
 */

// API Base URL
const API_BASE = '';

// Utility Functions
const utils = {
    async fetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 5000);
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-DZ', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Status Check
async function checkStatus() {
    try {
        const status = await utils.fetchAPI('/api/status');
        console.log('System Status:', status);
        return status;
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

// Account Management
async function createAccount() {
    if (!confirm('هل تريد إنشاء حساب جديد؟')) return;
    
    try {
        const result = await utils.fetchAPI('/api/accounts/create', {
            method: 'POST'
        });
        
        if (result.success) {
            utils.showToast('تم بدء إنشاء الحساب بنجاح', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            utils.showToast('خطأ: ' + result.message, 'danger');
        }
    } catch (error) {
        utils.showToast('حدث خطأ في الاتصال', 'danger');
    }
}

async function deleteAccount(id) {
    if (!confirm('هل أنت متأكد من حذف هذا الحساب؟')) return;
    
    try {
        const result = await utils.fetchAPI(`/api/accounts/${id}`, {
            method: 'DELETE'
        });
        
        if (result.success) {
            utils.showToast('تم حذف الحساب', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            utils.showToast('خطأ: ' + result.message, 'danger');
        }
    } catch (error) {
        utils.showToast('حدث خطأ في الاتصال', 'danger');
    }
}

// Task Management
async function startTask(id) {
    try {
        const result = await utils.fetchAPI(`/api/tasks/${id}/start`, {
            method: 'POST'
        });
        
        if (result.success) {
            utils.showToast('تم بدء المهمة', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    } catch (error) {
        utils.showToast('حدث خطأ في الاتصال', 'danger');
    }
}

async function pauseTask(id) {
    try {
        const result = await utils.fetchAPI(`/api/tasks/${id}/pause`, {
            method: 'POST'
        });
        
        if (result.success) {
            utils.showToast('تم إيقاف المهمة مؤقتاً', 'warning');
            setTimeout(() => location.reload(), 1000);
        }
    } catch (error) {
        utils.showToast('حدث خطأ في الاتصال', 'danger');
    }
}

async function cancelTask(id) {
    if (!confirm('هل أنت متأكد من إلغاء هذه المهمة؟')) return;
    
    try {
        const result = await utils.fetchAPI(`/api/tasks/${id}/cancel`, {
            method: 'POST'
        });
        
        if (result.success) {
            utils.showToast('تم إلغاء المهمة', 'danger');
            setTimeout(() => location.reload(), 1000);
        }
    } catch (error) {
        utils.showToast('حدث خطأ في الاتصال', 'danger');
    }
}

// Auto-refresh status
function startAutoRefresh(interval = 30000) {
    setInterval(checkStatus, interval);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Getoken Dashboard Loaded');
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
