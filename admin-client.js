/**
 * Admin Panel Client-Side Logic
 * Handles authentication, config loading, and form submission
 */

const API_BASE = 'http://localhost:3000/api';

// State management
let authToken = localStorage.getItem('authToken');
let currentConfig = null;

// DOM Elements (will be initialized on DOMContentLoaded)
let loginScreen, adminScreen, loginForm, configForm, loginError;
let userInfo, logoutBtn, messageContainer, jsonModal;
let viewJsonBtn, resetBtn, refreshBackupsBtn;

// ============================================
// Utility Functions
// ============================================

function showMessage(message, type = 'success') {
  const messageEl = document.createElement('div');
  messageEl.className = `message ${type}`;
  messageEl.textContent = message;
  messageContainer.appendChild(messageEl);

  setTimeout(() => {
    messageEl.remove();
  }, 5000);
}

function showError(element, message) {
  element.textContent = message;
  element.classList.add('active');

  setTimeout(() => {
    element.classList.remove('active');
  }, 5000);
}

async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }

  return data;
}

function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  const lastKey = keys.pop();
  const target = keys.reduce((o, k) => o[k] = o[k] || {}, obj);
  target[lastKey] = value;
}

function getNestedValue(obj, path) {
  return path.split('.').reduce((o, k) => o?.[k], obj);
}

// ============================================
// Authentication
// ============================================

async function login(username, password) {
  try {
    console.log('Attempting login...', username);
    const data = await apiRequest('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    console.log('Login successful:', data);
    authToken = data.token;
    localStorage.setItem('authToken', authToken);
    localStorage.setItem('user', JSON.stringify(data.user));

    showAdminScreen(data.user);
    loadConfig();
  } catch (error) {
    console.error('Login error:', error);
    showError(loginError, error.message);
  }
}

async function logout() {
  try {
    await apiRequest('/logout', { method: 'POST' });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    authToken = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    showLoginScreen();
  }
}

async function verifyAuth() {
  if (!authToken) {
    showLoginScreen();
    return;
  }

  try {
    const data = await apiRequest('/verify');
    showAdminScreen(data.user);
    loadConfig();
  } catch (error) {
    console.error('Auth verification failed:', error);
    logout();
  }
}

function showLoginScreen() {
  loginScreen.classList.add('active');
  adminScreen.classList.remove('active');
}

function showAdminScreen(user) {
  loginScreen.classList.remove('active');
  adminScreen.classList.add('active');
  userInfo.textContent = `👤 ${user.username} (${user.role})`;
}

// ============================================
// Config Management
// ============================================

async function loadConfig() {
  try {
    const data = await apiRequest('/config');
    currentConfig = data.config;
    populateForm(currentConfig);
    loadBackups();
    loadThemes(); // Load available themes
  } catch (error) {
    showMessage(`Failed to load config: ${error.message}`, 'error');
  }
}

async function loadThemes() {
  try {
    const data = await apiRequest('/themes');
    const themeSelector = document.getElementById('theme_selector');

    // Clear existing options
    themeSelector.innerHTML = '';

    // Add themes to dropdown
    data.themes.forEach(theme => {
      const option = document.createElement('option');
      option.value = theme.id;
      option.textContent = `${theme.name} (${theme.category})`;
      themeSelector.appendChild(option);
    });

    // Set default theme (beach)
    themeSelector.value = 'beach';

    // Add change event listener
    themeSelector.addEventListener('change', (e) => {
      const selectedTheme = data.themes.find(t => t.id === e.target.value);
      if (selectedTheme) {
        displayThemePreview(selectedTheme);
      }
    });

    // Display initial preview
    const defaultTheme = data.themes.find(t => t.id === 'beach');
    if (defaultTheme) {
      displayThemePreview(defaultTheme);
    }
  } catch (error) {
    showMessage(`Failed to load themes: ${error.message}`, 'error');
  }
}

function displayThemePreview(theme) {
  const previewContainer = document.getElementById('theme_preview');
  previewContainer.innerHTML = `
    <div class="theme-info">
      <h4>${theme.name}</h4>
      <p>${theme.description}</p>
      <div class="theme-meta">
        <span><strong>Category:</strong> ${theme.category}</span>
        <span><strong>Version:</strong> ${theme.version}</span>
      </div>
      <div class="theme-colors">
        ${Object.entries(theme.colorScheme).map(([key, value]) => `
          <div class="color-swatch">
            <div class="color-box" style="background-color: ${value}"></div>
            <span>${key}: ${value}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function populateForm(config) {
  // Couple details
  document.getElementById('couple_name1').value = config.couple.name1;
  document.getElementById('couple_name2').value = config.couple.name2;
  document.getElementById('couple_fullNames').value = config.couple.fullNames;

  // Event details
  document.getElementById('event_title').value = config.event.title;
  document.getElementById('event_subtitle').value = config.event.subtitle;
  document.getElementById('event_date').value = config.event.date;
  document.getElementById('event_dayOfWeek').value = config.event.dayOfWeek;
  document.getElementById('event_time').value = config.event.time;

  // Venue details
  document.getElementById('venue_name').value = config.event.venue.name;
  document.getElementById('venue_address').value = config.event.venue.address;
  document.getElementById('venue_googleMapsLink').value = config.event.venue.googleMapsLink;

  // Content
  document.getElementById('content_heroMessage').value = config.content.heroMessage;
  document.getElementById('content_ourStoryTitle').value = config.content.ourStoryTitle;
  document.getElementById('content_ourStory').value = config.content.ourStory;
  document.getElementById('content_rsvpTitle').value = config.content.rsvpTitle;
  document.getElementById('content_rsvpMessage').value = config.content.rsvpMessage;
  document.getElementById('content_rsvpWhatsApp').value = config.content.rsvpWhatsApp;
  document.getElementById('content_rsvpWhatsAppMessage').value = config.content.rsvpWhatsAppMessage;
  document.getElementById('content_hashtag').value = config.content.hashtag;
  document.getElementById('content_galleryTitle').value = config.content.galleryTitle;

  // Footer
  document.getElementById('footer_thankYouMessage').value = config.footer.thankYouMessage;
  document.getElementById('footer_contactEmail').value = config.footer.contactEmail;
  document.getElementById('footer_year').value = config.footer.year;

  // Colors
  document.getElementById('color_primary').value = config.styling.colorScheme.primary;
  document.getElementById('color_secondary').value = config.styling.colorScheme.secondary;
  document.getElementById('color_accent').value = config.styling.colorScheme.accent;

  // Animations
  document.getElementById('animations_enableLanterns').checked = config.animations.enableLanterns;
  document.getElementById('animations_lanternCount').value = config.animations.lanternCount;
  document.getElementById('animations_enableScrollAnimations').checked = config.animations.enableScrollAnimations;
}

function getFormConfig() {
  const formData = new FormData(configForm);
  const config = JSON.parse(JSON.stringify(currentConfig)); // Deep clone

  // Update config from form
  for (const [name, value] of formData.entries()) {
    if (name.includes('.')) {
      setNestedValue(config, name, value);
    }
  }

  // Handle checkboxes separately
  config.animations.enableLanterns = document.getElementById('animations_enableLanterns').checked;
  config.animations.enableScrollAnimations = document.getElementById('animations_enableScrollAnimations').checked;

  // Convert lantern count to number
  config.animations.lanternCount = parseInt(config.animations.lanternCount);

  return config;
}

async function saveConfig() {
  try {
    const config = getFormConfig();
    const data = await apiRequest('/config', {
      method: 'POST',
      body: JSON.stringify({ config })
    });

    showMessage(`✅ ${data.message}`);
    currentConfig = config;

    // Reload the invitation page in the background
    setTimeout(() => {
      showMessage('💡 Refresh your invitation page to see the changes!', 'success');
    }, 1000);
  } catch (error) {
    showMessage(`❌ Failed to save: ${error.message}`, 'error');
  }
}

// ============================================
// Backups Management
// ============================================

async function loadBackups() {
  try {
    const data = await apiRequest('/config/backups');
    displayBackups(data.backups);
  } catch (error) {
    console.error('Failed to load backups:', error);
  }
}

function displayBackups(backups) {
  const backupsList = document.getElementById('backups-list');

  if (backups.length === 0) {
    backupsList.innerHTML = '<p style="color: #999;">No backups available</p>';
    return;
  }

  backupsList.innerHTML = backups.map(backup => `
    <div class="backup-item">
      <div class="backup-info">
        <div class="backup-filename">${backup.filename}</div>
        <div class="backup-timestamp">${new Date(backup.timestamp).toLocaleString()}</div>
      </div>
      <div class="backup-actions">
        <button class="btn btn-small btn-primary" onclick="restoreBackup('${backup.filename}')">
          Restore
        </button>
      </div>
    </div>
  `).join('');
}

async function restoreBackup(filename) {
  if (!confirm(`Are you sure you want to restore from ${filename}?`)) {
    return;
  }

  try {
    const data = await apiRequest(`/config/restore/${filename}`, {
      method: 'POST'
    });

    showMessage(`✅ ${data.message}`, 'success');
    await loadConfig();
  } catch (error) {
    showMessage(`❌ Failed to restore: ${error.message}`, 'error');
  }
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing admin panel...');

  // Initialize DOM elements
  loginScreen = document.getElementById('login-screen');
  adminScreen = document.getElementById('admin-screen');
  loginForm = document.getElementById('login-form');
  configForm = document.getElementById('config-form');
  loginError = document.getElementById('login-error');
  userInfo = document.getElementById('user-info');
  logoutBtn = document.getElementById('logout-btn');
  messageContainer = document.getElementById('message-container');
  jsonModal = document.getElementById('json-modal');
  viewJsonBtn = document.getElementById('view-json-btn');
  resetBtn = document.getElementById('reset-btn');
  refreshBackupsBtn = document.getElementById('refresh-backups-btn');

  console.log('DOM elements initialized:', { loginForm, loginScreen, adminScreen });

  // Attach event listeners
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      console.log('Login form submitted');
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      login(username, password);
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }

  if (configForm) {
    configForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveConfig();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to reset the form to the last saved state?')) {
        populateForm(currentConfig);
      }
    });
  }

  if (viewJsonBtn) {
    viewJsonBtn.addEventListener('click', () => {
      const config = getFormConfig();
      document.getElementById('json-display').textContent = JSON.stringify(config, null, 2);
      jsonModal.classList.add('active');
    });
  }

  const modalClose = document.querySelector('.modal-close');
  if (modalClose) {
    modalClose.addEventListener('click', () => {
      jsonModal.classList.remove('active');
    });
  }

  if (jsonModal) {
    jsonModal.addEventListener('click', (e) => {
      if (e.target === jsonModal) {
        jsonModal.classList.remove('active');
      }
    });
  }

  if (refreshBackupsBtn) {
    refreshBackupsBtn.addEventListener('click', loadBackups);
  }

  // Make restoreBackup available globally
  window.restoreBackup = restoreBackup;

  // Verify authentication
  verifyAuth();
});
