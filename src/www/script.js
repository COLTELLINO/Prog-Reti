/**
 * Funzioni JavaScript per il Web Server HTTP
 * Autore: Filippo Patrignani
 */


function logMessage(message, level = 'info') {
    const timestamp = new Date().toLocaleString('it-IT');
    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
}


async function testServerConnection() {
    try {
        logMessage('Testando connessione al server...');
        const response = await fetch('/', {
            method: 'HEAD',
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        
        if (response.ok) {
            logMessage('✅ Server raggiungibile e funzionante!');
            showNotification('Server Online', 'success');
            return true;
        } else {
            logMessage(`⚠️ Server risponde con errore: ${response.status}`, 'warn');
            showNotification(`Server Error: ${response.status}`, 'warning');
            return false;
        }
    } catch (error) {
        logMessage(`❌ Errore di connessione: ${error.message}`, 'error');
        showNotification('Connessione Fallita', 'error');
        return false;
    }
}


function showNotification(message, type = 'info') {
    
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    `;
    
    
    const colors = {
        success: '#4CAF50',
        error: '#F44336',
        warning: '#FF9800',
        info: '#2196F3'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    
    document.body.appendChild(notification);
    
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}


function addNotificationStyles() {
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background-color 0.2s;
            }
            
            .notification-close:hover {
                background-color: rgba(255,255,255,0.2);
            }
        `;
        document.head.appendChild(style);
    }
}


class ServerStats {
    constructor() {
        this.updateInterval = 10000; 
        this.isRunning = false;
    }
    
    async fetchStats() {
        try {
            const response = await fetch('/stats');
            if (response.ok) {
                
                logMessage('Statistiche aggiornate');
                return { status: 'online', requests: Math.floor(Math.random() * 1000) };
            }
        } catch (error) {
            logMessage(`Errore nel recupero statistiche: ${error.message}`, 'error');
            return { status: 'offline', requests: 0 };
        }
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        logMessage('Avviato monitoraggio statistiche');
        
        this.interval = setInterval(async () => {
            const stats = await this.fetchStats();
            this.updateUI(stats);
        }, this.updateInterval);
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.isRunning = false;
            logMessage('Fermato monitoraggio statistiche');
        }
    }
    
    updateUI(stats) {
        
        const requestsElement = document.getElementById('requests-count');
        if (requestsElement) {
            requestsElement.textContent = stats.requests;
        }
        
        const statusElement = document.querySelector('.status-indicator');
        if (statusElement) {
            statusElement.className = `status-indicator ${stats.status}`;
        }
    }
}


class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            domContentLoaded: 0,
            firstPaint: 0
        };
    }
    
    start() {
        
        window.addEventListener('load', () => {
            const navigation = performance.getEntriesByType('navigation')[0];
            this.metrics.pageLoadTime = Math.round(navigation.loadEventEnd - navigation.fetchStart);
            this.metrics.domContentLoaded = Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart);
            
            logMessage(`Pagina caricata in ${this.metrics.pageLoadTime}ms`);
            this.updatePerformanceUI();
        });
        
        
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name === 'first-paint') {
                        this.metrics.firstPaint = Math.round(entry.startTime);
                        logMessage(`First Paint: ${this.metrics.firstPaint}ms`);
                    }
                }
            });
            observer.observe({ entryTypes: ['paint'] });
        }
    }
    
    updatePerformanceUI() {
        const perfElement = document.getElementById('performance-info');
        if (perfElement) {
            perfElement.innerHTML = `
                <small>Load: ${this.metrics.pageLoadTime}ms | 
                DOM: ${this.metrics.domContentLoaded}ms | 
                FP: ${this.metrics.firstPaint}ms</small>
            `;
        }
    }
}


class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'auto';
        this.init();
    }
    
    init() {
        this.applyTheme();
        this.createThemeToggle();
    }
    
    applyTheme() {
        if (this.currentTheme === 'dark') {
            document.body.classList.add('dark-theme');
        } else if (this.currentTheme === 'light') {
            document.body.classList.remove('dark-theme');
        } else {
            
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.classList.toggle('dark-theme', prefersDark);
        }
    }
    
    toggleTheme() {
        const themes = ['light', 'dark', 'auto'];
        const currentIndex = themes.indexOf(this.currentTheme);
        this.currentTheme = themes[(currentIndex + 1) % themes.length];
        
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
        
        showNotification(`Tema cambiato: ${this.currentTheme}`, 'info');
    }
    
    createThemeToggle() {
        const toggle = document.createElement('button');
        toggle.innerHTML = '🌓';
        toggle.title = 'Cambia tema';
        toggle.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: rgba(102, 126, 234, 0.9);
            color: white;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            z-index: 1000;
        `;
        
        toggle.addEventListener('click', () => this.toggleTheme());
        toggle.addEventListener('mouseenter', () => {
            toggle.style.transform = 'scale(1.1)';
        });
        toggle.addEventListener('mouseleave', () => {
            toggle.style.transform = 'scale(1)';
        });
        
        document.body.appendChild(toggle);
    }
}


const debug = {
    logHttpHeaders: async function() {
        try {
            const response = await fetch(window.location.href);
            console.group('HTTP Headers');
            for (const [key, value] of response.headers.entries()) {
                console.log(`${key}: ${value}`);
            }
            console.groupEnd();
        } catch (error) {
            console.error('Errore nel recupero headers:', error);
        }
    },
    
    checkServerCapabilities: async function() {
        const tests = [
            { url: '/', description: 'Homepage' },
            { url: '/stats', description: 'Statistiche' },
            { url: '/nonexistent.html', description: '404 Test' },
            { url: '/icons/', description: 'Directory Listing' }
        ];
        
        console.group('Test Capacità Server');
        for (const test of tests) {
            try {
                const response = await fetch(test.url, { method: 'HEAD' });
                console.log(`✅ ${test.description}: ${response.status}`);
            } catch (error) {
                console.log(`❌ ${test.description}: Errore`);
            }
        }
        console.groupEnd();
    }
};


document.addEventListener('DOMContentLoaded', function() {
    logMessage('JavaScript caricato, inizializzazione in corso...');
    
    
    addNotificationStyles();
    
    
    const perfMonitor = new PerformanceMonitor();
    perfMonitor.start();
    
    
    const themeManager = new ThemeManager();
    
    
    if (window.location.pathname.includes('stats')) {
        const stats = new ServerStats();
        stats.start();
        
        
        window.addEventListener('beforeunload', () => stats.stop());
    }
    
    
    setTimeout(() => {
        testServerConnection();
    }, 2000);
    
    
    window.debug = debug;
    window.testServerConnection = testServerConnection;
    window.showNotification = showNotification;
    
    logMessage('Inizializzazione completata!');
});


if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        
        logMessage('Service Worker supportato dal browser');
    });
}
