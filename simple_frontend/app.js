// Simple frontend that talks to the existing FastAPI backend
// API base URL (FastAPI should be running from 1st_prototype/backend on port 8000)
const API_BASE = 'http://localhost:8000/api';

let authToken = null;
let currentUser = null;

function $(id) {
  return document.getElementById(id);
}

function show(el) {
  if (!el) return;
  el.classList.remove('hidden');
  el.style.display = ''; // clear inline display so CSS applies (e.g. #app-section uses flex)
}

function hide(el) {
  if (!el) return;
  el.classList.add('hidden');
  el.style.display = 'none'; // force hide so login and dashboard never show together
}

function setText(el, text) {
  el.textContent = text;
}

function showError(el, message) {
  setText(el, message);
  show(el);
}

function clearError(el) {
  setText(el, '');
  hide(el);
}

async function apiRequest(path, options = {}) {
  const headers = options.headers || {};
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  });
}

async function handleLogin(e) {
  e.preventDefault();
  const email = $('login-email').value.trim();
  const password = $('login-password').value;
  const errorEl = $('login-error');
  clearError(errorEl);

  try {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Login failed');
    }

    const data = await res.json();
    authToken = data.access_token;

    // Fetch current user
    const meRes = await apiRequest('/auth/me');
    if (!meRes.ok) {
      throw new Error('Failed to load user info');
    }
    const me = await meRes.json();
    currentUser = me;

    // Update UI
    setText($('user-name'), `${me.full_name} (${me.role})`);
    show($('user-info'));
    hide($('login-section'));
    show($('app-section'));

    // Sidebar is always visible when logged in. Show "User Management" only for admin.
    const sidebar = document.getElementById('sidebar');
    const navUsersBtn = document.getElementById('nav-users');
    if (sidebar) {
      const userRole = String(me.role || '').toLowerCase();
      if (userRole === 'administrator' && navUsersBtn) {
        navUsersBtn.classList.remove('hidden');
      } else if (navUsersBtn) {
        navUsersBtn.classList.add('hidden');
      }
    }
    setupAdminNav();

    await loadTickets();
    await loadNotifications();
  } catch (err) {
    showError(errorEl, err.message || 'Login failed');
  }
}

async function handleLogout() {
  authToken = null;
  currentUser = null;
  hide($('user-info'));
  hide($('app-section'));
  show($('login-section'));
}

async function handleCreateTicket(e) {
  e.preventDefault();
  const title = $('ticket-title').value.trim();
  const category = $('ticket-category').value;
  const priority = $('ticket-priority').value;
  const description = $('ticket-description').value.trim();

  const errorEl = $('create-error');
  const successEl = $('create-success');
  clearError(errorEl);
  hide(successEl);

  if (!title || !category || !description) {
    showError(errorEl, 'Please fill in all required fields.');
    return;
  }

  try {
    const res = await apiRequest('/tickets', {
      method: 'POST',
      body: JSON.stringify({ title, category, priority, description }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to create ticket');
    }

    $('ticket-form').reset();
    show(successEl);
    setText(successEl, 'Ticket created successfully.');
    await loadTickets();
  } catch (err) {
    showError(errorEl, err.message || 'Failed to create ticket');
  }
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString();
}

async function loadTickets() {
  const statusFilter = $('status-filter').value;
  const tbody = $('tickets-body');
  tbody.innerHTML = '<tr><td colspan="7" class="empty">Loading...</td></tr>';

  const params = new URLSearchParams();
  if (statusFilter) {
    params.set('status_filter', statusFilter);
  }

  try {
    const res = await apiRequest(`/tickets?${params.toString()}`);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to load tickets');
    }
    const tickets = await res.json();

    if (!tickets.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty">No tickets yet</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    // Check if user can update tickets (admin or support staff)
    const canUpdateTickets = currentUser && currentUser.role === 'administrator';
    
    for (const t of tickets) {
      const tr = document.createElement('tr');
      
      // Build status cell content
      let statusContent = '';
      if (canUpdateTickets) {
        // Create dropdown HTML
        const statuses = [
          { value: 'open', label: 'Open' },
          { value: 'in_progress', label: 'In Progress' },
          { value: 'resolved', label: 'Resolved' }
        ];
        
        let optionsHtml = '';
        statuses.forEach(s => {
          const selected = s.value === t.status ? 'selected' : '';
          optionsHtml += `<option value="${s.value}" ${selected}>${s.label}</option>`;
        });
        
        statusContent = `<select class="status-select" data-ticket-id="${t.id}">${optionsHtml}</select>`;
      } else {
        statusContent = t.status.replace('_', ' ');
      }
      
      tr.innerHTML = `
        <td>${(t.id || '').slice(0, 8)}</td>
        <td>${t.title}</td>
        <td>${t.category}</td>
        <td>${t.priority}</td>
        <td>${statusContent}</td>
        <td>${formatDate(t.created_at)}</td>
        <td>-</td>
      `;
      
      // Add event listener if dropdown exists
      if (canUpdateTickets) {
        const statusSelect = tr.querySelector('.status-select');
        if (statusSelect) {
          statusSelect.addEventListener('change', (e) => {
            updateTicketStatus(t.id, e.target.value);
          });
        }
      }
      
      tbody.appendChild(tr);
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty">Error: ${err.message}</td></tr>`;
  }
}

async function loadNotifications() {
  const panel = document.getElementById('notifications-panel');
  const listEl = document.getElementById('notifications-list');
  if (!panel || !listEl) return;

  try {
    const res = await apiRequest('/notifications');
    if (!res.ok) return;
    const notifications = await res.json();
    const unread = notifications.filter((n) => !n.read);

    if (unread.length === 0) {
      hide(panel);
      return;
    }

    listEl.innerHTML = '';
    unread.forEach((n) => {
      const li = document.createElement('li');
      li.className = 'notification-item';
      li.innerHTML = `
        <span class="notification-message">${n.message} <strong>${escapeHtml(n.ticket_title || '')}</strong></span>
        <button type="button" class="btn btn-secondary btn-sm notification-dismiss" data-id="${n.id}">Dismiss</button>
      `;
      li.querySelector('.notification-dismiss').addEventListener('click', () => markNotificationRead(n.id, li));
      listEl.appendChild(li);
    });
    show(panel);
  } catch (err) {
    hide(panel);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function markNotificationRead(notificationId, listItemEl) {
  try {
    const res = await apiRequest(`/notifications/${notificationId}/read`, { method: 'PATCH' });
    if (res.ok && listItemEl) listItemEl.remove();
    const listEl = document.getElementById('notifications-list');
    if (listEl && listEl.children.length === 0) {
      hide(document.getElementById('notifications-panel'));
    }
  } catch (err) {
    console.error(err);
  }
}

async function updateTicketStatus(ticketId, newStatus) {
  try {
    let body = { status: newStatus };
    if (newStatus === 'resolved') {
      const notes = window.prompt('Optional: Add resolution notes to include in the email to the user:');
      if (notes !== null && notes.trim()) {
        body.resolution_notes = notes.trim();
      }
    }
    const res = await apiRequest(`/tickets/${ticketId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to update ticket status');
    }

    // Reload tickets to show updated status
    await loadTickets();
  } catch (err) {
    alert(`Error updating status: ${err.message}`);
    // Reload to reset dropdown to original value
    await loadTickets();
  }
}

// Admin functions
function setupAdminNav() {
  $('nav-tickets').addEventListener('click', () => {
    show($('tickets-view'));
    hide($('users-view'));
    $('nav-tickets').classList.add('active');
    $('nav-users').classList.remove('active');
  });

  $('nav-users').addEventListener('click', () => {
    hide($('tickets-view'));
    show($('users-view'));
    $('nav-tickets').classList.remove('active');
    $('nav-users').classList.add('active');
    loadUsers();
  });
}

async function loadUsers() {
  const tbody = $('users-body');
  const errorEl = $('users-error');
  clearError(errorEl);
  tbody.innerHTML = '<tr><td colspan="7" class="empty">Loading...</td></tr>';

  try {
    const res = await apiRequest('/users');
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to load users');
    }
    const users = await res.json();

    if (!users.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty">No users found</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    for (const u of users) {
      const tr = document.createElement('tr');
      
      // Role dropdown
      const roleSelect = document.createElement('select');
      roleSelect.className = 'status-select';
      roleSelect.dataset.userId = u.id;
      const roles = [
        { value: 'end_user', label: 'End User' },
        { value: 'support_staff', label: 'Support Staff' },
        { value: 'administrator', label: 'Administrator' }
      ];
      roles.forEach(r => {
        const option = document.createElement('option');
        option.value = r.value;
        option.textContent = r.label;
        if (r.value === u.role) {
          option.selected = true;
        }
        roleSelect.appendChild(option);
      });
      roleSelect.addEventListener('change', (e) => {
        updateUserRole(u.id, e.target.value);
      });

      // Active checkbox
      const activeCheckbox = document.createElement('input');
      activeCheckbox.type = 'checkbox';
      activeCheckbox.checked = u.is_active;
      activeCheckbox.className = 'active-checkbox';
      activeCheckbox.dataset.userId = u.id;
      activeCheckbox.addEventListener('change', (e) => {
        updateUserActive(u.id, e.target.checked);
      });

      tr.innerHTML = `
        <td>${(u.id || '').slice(0, 8)}</td>
        <td>${u.email}</td>
        <td>${u.full_name}</td>
        <td></td>
        <td></td>
        <td>${formatDate(u.created_at)}</td>
        <td></td>
      `;
      
      tr.querySelector('td:nth-child(4)').appendChild(roleSelect);
      tr.querySelector('td:nth-child(5)').appendChild(activeCheckbox);
      tbody.appendChild(tr);
    }
  } catch (err) {
    showError(errorEl, err.message || 'Failed to load users');
    tbody.innerHTML = `<tr><td colspan="7" class="empty">Error: ${err.message}</td></tr>`;
  }
}

async function updateUserRole(userId, newRole) {
  try {
    const res = await apiRequest(`/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify({ role: newRole }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to update user role');
    }

    await loadUsers();
  } catch (err) {
    alert(`Error updating role: ${err.message}`);
    await loadUsers();
  }
}

async function updateUserActive(userId, isActive) {
  try {
    const res = await apiRequest(`/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to update user status');
    }

    await loadUsers();
  } catch (err) {
    alert(`Error updating user status: ${err.message}`);
    await loadUsers();
  }
}

function init() {
  $('login-form').addEventListener('submit', handleLogin);
  $('logout-btn').addEventListener('click', handleLogout);
  $('ticket-form').addEventListener('submit', handleCreateTicket);
  $('refresh-btn').addEventListener('click', (e) => {
    e.preventDefault();
    loadTickets();
  });
  $('status-filter').addEventListener('change', loadTickets);
  $('refresh-users-btn').addEventListener('click', (e) => {
    e.preventDefault();
    loadUsers();
  });

  const dismissAllBtn = document.getElementById('notifications-dismiss-all');
  if (dismissAllBtn) {
    dismissAllBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const listEl = document.getElementById('notifications-list');
      if (!listEl) return;
      const ids = Array.from(listEl.querySelectorAll('.notification-dismiss')).map((btn) => btn.dataset.id);
      for (const id of ids) {
        await markNotificationRead(id, null);
      }
      listEl.innerHTML = '';
      hide(document.getElementById('notifications-panel'));
    });
  }
}

document.addEventListener('DOMContentLoaded', init);

