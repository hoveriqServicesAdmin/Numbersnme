/**
 * Admin Modal Manager
 * Provides admin login and appointments dashboard across all pages
 */

const AdminModal = {
    isOpen: false,
    isAuthenticated: false,
    currentView: 'login', // 'login' or 'dashboard'
    isFullscreen: false,
    isCollapsed: false,

    init() {
        this.createStyles();
        this.createHTML();
        this.attachEventListeners();
        this.tryRestoreSession();
    },

    createStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Admin Modal Styles */
            .admin-modal-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                z-index: 9998;
                backdrop-filter: blur(2px);
            }

            .admin-modal-overlay.show {
                display: block;
            }

            .admin-modal-container {
                position: fixed;
                top: 0;
                right: 0;
                width: 450px;
                height: 100vh;
                background: #0c2022;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                transform: translateX(100%);
                transition: transform 0.3s ease, width 0.3s ease, height 0.3s ease;
                box-shadow: -4px 0 20px rgba(0,0,0,0.3);
            }

            .admin-modal-container.show {
                transform: translateX(0);
            }

            .admin-modal-container.fullscreen {
                width: 100vw;
                height: 100vh;
                top: 0;
                left: 0;
                right: auto;
                border-radius: 0;
            }

            .admin-modal-container.collapsed {
                width: 60px;
            }

            .admin-modal-container.collapsed .admin-modal-content {
                display: none;
            }

            .admin-modal-container.collapsed .admin-modal-footer {
                display: none;
            }

            .admin-modal-header {
                padding: 16px 20px;
                border-bottom: 1px solid rgba(212,175,55,0.18);
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }

            .admin-modal-header h3 {
                margin: 0;
                color: #d4af37;
                font-size: 1.1rem;
            }

            .admin-modal-header-buttons {
                display: flex;
                gap: 8px;
            }

            .admin-modal-btn-icon {
                background: none;
                border: none;
                color: rgba(255,255,255,0.6);
                font-size: 1.2rem;
                cursor: pointer;
                padding: 4px 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: color 0.2s, background 0.2s;
                border-radius: 6px;
            }

            .admin-modal-btn-icon:hover {
                color: #d4af37;
                background: rgba(212,175,55,0.1);
            }

            .admin-modal-container.collapsed .admin-modal-header h3 {
                display: none;
            }

            .admin-modal-content {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }

            .admin-modal-footer {
                padding: 14px 20px;
                border-top: 1px solid rgba(212,175,55,0.18);
                background: rgba(0,0,0,0.2);
            }

            /* Admin Login Section */
            .admin-login-form .form-group {
                margin-bottom: 14px;
            }

            .admin-login-form label {
                display: block;
                margin-bottom: 5px;
                color: rgba(255,255,255,0.8);
                font-size: 0.9rem;
                font-weight: 500;
            }

            .admin-login-form input {
                width: 100%;
                padding: 10px 12px;
                border: 1px solid rgba(212,175,55,0.2);
                border-radius: 8px;
                background: #edf5f3;
                color: #1b2930;
                font-family: inherit;
                font-size: 0.9rem;
                box-sizing: border-box;
            }

            .admin-login-form input:focus {
                outline: none;
                border-color: #d4af37;
                box-shadow: 0 0 0 2px rgba(212,175,55,0.16);
            }

            .admin-status-box {
                display: none;
                margin-bottom: 14px;
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 0.85rem;
                line-height: 1.4;
            }

            .admin-status-box.show {
                display: block;
            }

            .admin-status-box.error {
                background: rgba(220,53,69,0.15);
                border: 1px solid rgba(220,53,69,0.35);
                color: #ff9292;
            }

            .admin-status-box.success {
                background: rgba(40,167,69,0.15);
                border: 1px solid rgba(40,167,69,0.35);
                color: #8fe3a0;
            }

            .admin-btn,
            .admin-ghost-btn {
                border: none;
                border-radius: 8px;
                font-family: inherit;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease, background 0.2s ease;
                padding: 10px 14px;
                font-size: 0.9rem;
            }

            .admin-btn {
                width: 100%;
                background: linear-gradient(135deg, #d4af37, #b8962e);
                color: #182224;
            }

            .admin-btn:hover {
                transform: translateY(-1px);
            }

            .admin-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .admin-ghost-btn {
                background: transparent;
                color: #d4af37;
                border: 1px solid rgba(212,175,55,0.24);
            }

            .admin-ghost-btn:hover {
                background: rgba(212,175,55,0.1);
            }

            /* Dashboard Sections */
            .admin-dashboard-section {
                display: none;
            }

            .admin-dashboard-section.active {
                display: block;
            }

            .admin-summary-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 12px;
                margin-bottom: 16px;
            }

            .admin-summary-item {
                background: rgba(212,175,55,0.08);
                border: 1px solid rgba(212,175,55,0.14);
                border-radius: 8px;
                padding: 12px;
            }

            .admin-summary-item .label {
                color: rgba(255,255,255,0.6);
                font-size: 0.8rem;
                margin-bottom: 4px;
            }

            .admin-summary-item .value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #d4af37;
            }

            .admin-appointments-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .admin-appointment-card {
                background: rgba(212,175,55,0.08);
                border: 1px solid rgba(212,175,55,0.14);
                border-radius: 8px;
                padding: 12px;
            }

            .admin-appointment-card h4 {
                margin: 0 0 6px;
                color: #d4af37;
                font-size: 0.9rem;
            }

            .admin-appointment-card p {
                margin: 3px 0;
                color: rgba(255,255,255,0.75);
                font-size: 0.8rem;
            }

            .admin-welcome {
                color: rgba(255,255,255,0.75);
                font-size: 0.9rem;
                margin-bottom: 14px;
                padding-bottom: 14px;
                border-bottom: 1px solid rgba(212,175,55,0.18);
            }

            .admin-welcome strong {
                color: #d4af37;
            }

            .admin-toolbar-buttons {
                display: flex;
                gap: 8px;
                margin-bottom: 14px;
            }

            .admin-toolbar-buttons .admin-ghost-btn {
                flex: 1;
                padding: 8px 10px;
                font-size: 0.85rem;
            }

            /* Admin Login Button in Header */
            .admin-login-btn {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 8px 14px;
                border-radius: 20px;
                background: linear-gradient(135deg, rgba(212,175,55,0.15), rgba(212,175,55,0.08));
                border: 1px solid rgba(212,175,55,0.25);
                color: #d4af37;
                cursor: pointer;
                font-weight: 500;
                font-size: 0.85rem;
                transition: all 0.3s;
                font-family: inherit;
                white-space: nowrap;
                flex-shrink: 0;
                margin-left: 8px;
            }

            .admin-login-btn:hover {
                background: linear-gradient(135deg, rgba(212,175,55,0.25), rgba(212,175,55,0.15));
                border-color: #d4af37;
                transform: scale(1.05);
            }

            .admin-login-btn svg {
                width: 14px;
                height: 14px;
            }

            @media (max-width: 1024px) {
                .admin-login-btn {
                    padding: 6px 10px;
                    font-size: 0.75rem;
                    gap: 4px;
                }

                .admin-login-btn svg {
                    width: 12px;
                    height: 12px;
                }
            }

            @media (max-width: 768px) {
                .admin-login-btn {
                    padding: 6px 8px;
                    font-size: 0.7rem;
                    gap: 3px;
                }

                .admin-login-btn svg {
                    width: 11px;
                    height: 11px;
                }

                .admin-login-btn span {
                    display: none;
                }
            }

            /* Prevent overlapping - adjust body when modal is open */
            body.admin-modal-open {
                overflow: hidden;
            }

            @media (min-width: 1024px) {
                body.admin-modal-open:not(.admin-modal-fullscreen) {
                    margin-right: 450px;
                }
            }

            body.admin-modal-fullscreen {
                overflow: hidden;
            }

            @media (max-width: 600px) {
                .admin-modal-container {
                    width: 100%;
                    right: 0;
                }
            }

            @media (max-width: 1023px) {
                .admin-modal-container {
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    },

    createHTML() {
        const html = `
            <div class="admin-modal-overlay" id="admin-modal-overlay"></div>
            <div class="admin-modal-container" id="admin-modal-container">
                <div class="admin-modal-header">
                    <h3 id="admin-modal-title">Admin Panel</h3>
                    <div class="admin-modal-header-buttons">
                        <button class="admin-modal-btn-icon" id="admin-modal-collapse-btn" title="Collapse">▬</button>
                        <button class="admin-modal-btn-icon" id="admin-modal-fullscreen-btn" title="Fullscreen">⛶</button>
                        <button class="admin-modal-btn-icon" id="admin-modal-close-btn" title="Close">✕</button>
                    </div>
                </div>
                <div class="admin-modal-content" id="admin-modal-content">
                    <!-- Login View -->
                    <section id="admin-login-view" class="admin-dashboard-section active">
                        <div class="admin-login-form">
                            <div id="admin-login-status" class="admin-status-box"></div>
                            <div class="form-group">
                                <label for="admin-username">Username</label>
                                <input type="text" id="admin-username" placeholder="Enter username" autocomplete="username">
                            </div>
                            <div class="form-group">
                                <label for="admin-password">Password</label>
                                <input type="password" id="admin-password" placeholder="Enter password" autocomplete="current-password">
                            </div>
                            <button type="button" class="admin-btn" id="admin-login-submit-btn">Sign In</button>
                        </div>
                    </section>

                    <!-- Dashboard View -->
                    <section id="admin-dashboard-view" class="admin-dashboard-section">
                        <div id="admin-dashboard-status" class="admin-status-box"></div>
                        <div class="admin-welcome">Signed in as <strong id="admin-username-display">Sangitha</strong></div>

                        <div class="admin-summary-grid">
                            <div class="admin-summary-item">
                                <div class="label">Total Appointments</div>
                                <div class="value" id="admin-sum-total">0</div>
                            </div>
                            <div class="admin-summary-item">
                                <div class="label">Upcoming</div>
                                <div class="value" id="admin-sum-upcoming">0</div>
                            </div>
                            <div class="admin-summary-item">
                                <div class="label">Today</div>
                                <div class="value" id="admin-sum-today">0</div>
                            </div>
                        </div>

                        <div class="admin-toolbar-buttons">
                            <button type="button" class="admin-ghost-btn" id="admin-refresh-btn">Refresh</button>
                            <button type="button" class="admin-ghost-btn" id="admin-logout-btn">Log Out</button>
                        </div>

                        <div style="color: rgba(255,255,255,0.75); font-size: 0.85rem; margin-bottom: 12px;">
                            <strong style="color: #d4af37;">Recent Appointments</strong>
                        </div>
                        <div class="admin-appointments-list" id="admin-appointments-list">
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Loading appointments...</p>
                        </div>
                    </section>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    },

    attachEventListeners() {
        // Open/Close modal
        document.getElementById('admin-modal-close-btn').addEventListener('click', () => this.close());
        document.getElementById('admin-modal-overlay').addEventListener('click', () => this.close());

        // Login form
        document.getElementById('admin-login-submit-btn').addEventListener('click', () => this.handleLogin());
        document.getElementById('admin-password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });

        // Dashboard
        document.getElementById('admin-refresh-btn').addEventListener('click', () => this.loadAppointments(true));
        document.getElementById('admin-logout-btn').addEventListener('click', () => this.handleLogout());
    },

    open() {
        this.isOpen = true;
        document.body.classList.add('admin-modal-open');
        if (this.isFullscreen) {
            document.body.classList.add('admin-modal-fullscreen');
        }
        document.getElementById('admin-modal-overlay').classList.add('show');
        document.getElementById('admin-modal-container').classList.add('show');
    },

    close() {
        this.isOpen = false;
        document.body.classList.remove('admin-modal-open', 'admin-modal-fullscreen');
        document.getElementById('admin-modal-overlay').classList.remove('show');
        document.getElementById('admin-modal-container').classList.remove('show');
    },

    showStatus(elementId, type, message) {
        const el = document.getElementById(elementId);
        el.className = `admin-status-box show ${type}`;
        el.textContent = message;
    },

    hideStatus(elementId) {
        const el = document.getElementById(elementId);
        el.className = 'admin-status-box';
        el.textContent = '';
    },

    switchView(view) {
        document.querySelectorAll('.admin-dashboard-section').forEach(el => el.classList.remove('active'));
        document.getElementById(`admin-${view}-view`).classList.add('active');
        this.currentView = view;
    },

    toggleCollapse() {
        const container = document.getElementById('admin-modal-container');
        this.isCollapsed = !this.isCollapsed;
        container.classList.toggle('collapsed', this.isCollapsed);

        // Exit fullscreen if collapsing
        if (this.isCollapsed && this.isFullscreen) {
            this.isFullscreen = false;
            container.classList.remove('fullscreen');
            document.body.classList.remove('admin-modal-fullscreen');
        }
    },

    toggleFullscreen() {
        const container = document.getElementById('admin-modal-container');
        this.isFullscreen = !this.isFullscreen;
        container.classList.toggle('fullscreen', this.isFullscreen);

        if (this.isFullscreen) {
            document.body.classList.add('admin-modal-fullscreen');
        } else {
            document.body.classList.remove('admin-modal-fullscreen');
        }

        // Exit collapse if going fullscreen
        if (this.isFullscreen && this.isCollapsed) {
            this.isCollapsed = false;
            container.classList.remove('collapsed');
        }
    },

    async handleLogin() {
        this.hideStatus('admin-login-status');
        const username = document.getElementById('admin-username').value.trim();
        const password = document.getElementById('admin-password').value;
        const btn = document.getElementById('admin-login-submit-btn');

        if (!username || !password) {
            this.showStatus('admin-login-status', 'error', 'Username and password required.');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Signing In...';

        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Login failed.');
            }

            this.isAuthenticated = true;
            this.switchView('dashboard');
            document.getElementById('admin-username-display').textContent = data.username || 'Sangitha';
            await this.loadAppointments(false);
            this.showStatus('admin-dashboard-status', 'success', `Welcome, ${data.username || 'Sangitha'}!`);
            document.getElementById('admin-username').value = '';
            document.getElementById('admin-password').value = '';
        } catch (error) {
            this.showStatus('admin-login-status', 'error', error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    },

    async handleLogout() {
        await fetch('/api/admin/logout', {
            method: 'POST',
            credentials: 'same-origin'
        });
        this.isAuthenticated = false;
        this.switchView('login');
        this.hideStatus('admin-dashboard-status');
    },

    async loadAppointments(showSuccess) {
        this.hideStatus('admin-dashboard-status');
        try {
            const response = await fetch('/api/admin/appointments', { credentials: 'same-origin' });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Unable to load appointments.');
            }

            document.getElementById('admin-sum-total').textContent = data.summary?.total ?? 0;
            document.getElementById('admin-sum-upcoming').textContent = data.summary?.upcoming ?? 0;
            document.getElementById('admin-sum-today').textContent = data.summary?.today ?? 0;

            const appointments = (data.appointments || []).slice(0, 5);
            const listHtml = appointments.map(apt => `
                <div class="admin-appointment-card">
                    <h4>${apt.booking_ref}</h4>
                    <p><strong>${apt.name || apt.first_name + ' ' + apt.last_name}</strong></p>
                    <p>📅 ${apt.appointment_date || '—'}</p>
                    <p>📞 ${apt.phone || '—'}</p>
                </div>
            `).join('');

            document.getElementById('admin-appointments-list').innerHTML = listHtml || '<p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">No appointments found.</p>';

            if (showSuccess) {
                this.showStatus('admin-dashboard-status', 'success', 'Appointments refreshed.');
            }
        } catch (error) {
            this.showStatus('admin-dashboard-status', 'error', error.message);
        }
    },

    async tryRestoreSession() {
        try {
            const response = await fetch('/api/admin/appointments', { credentials: 'same-origin' });
            if (response.ok) {
                this.isAuthenticated = true;
                const data = await response.json();
                document.getElementById('admin-username-display').textContent = data.username || 'Sangitha';
                this.switchView('dashboard');
                await this.loadAppointments(false);
            }
        } catch (error) {
            // Not authenticated
        }
    },

    addHeaderButton() {
        // Find the right section in header and add admin login button
        const rightSections = document.querySelectorAll('.site-header-primary-section-right');
        rightSections.forEach(section => {
            if (!section.querySelector('.admin-login-btn')) {
                const btn = document.createElement('button');
                btn.className = 'admin-login-btn';
                btn.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    <span>Admin</span>
                `;
                btn.addEventListener('click', () => this.open());
                section.appendChild(btn);
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    AdminModal.init();
    AdminModal.addHeaderButton();
});

