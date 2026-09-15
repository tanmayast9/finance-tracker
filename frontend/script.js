// Finance App JavaScript Frontend
const API_BASE = (window.location.port === '5000' && /^(localhost|127\.0\.0\.1)$/.test(window.location.hostname) ? '' : 'http://localhost:5000') + '/api';
let authToken = null;
let userProfile = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile().then(() => {
        if (!userProfile) return;
        setupEventListeners();
        showPage('dashboard');
        setupTheme();
    });
});

// Load User Profile from database (called after login/signup and when opening Profile)
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE}/users/profile`, {
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            userProfile = await response.json();
            populateProfileForm();
            loadDashboard();
        } else if (response.status === 401) {
            logout();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/analytics/dashboard`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('monthIncome').textContent = `₹${data.income.toFixed(2)}`;
            document.getElementById('monthExpense').textContent = `₹${data.expenses.toFixed(2)}`;
            document.getElementById('savings').textContent = `₹${data.savings.toFixed(2)}`;
            document.getElementById('accountBalance').textContent = `₹${data.account_balance.toFixed(2)}`;
            
            // Update recent transactions
            updateRecentTransactions(data.latest_transactions);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateRecentTransactions(transactions) {
    const tbody = document.querySelector('#recentTransactions tbody');
    tbody.innerHTML = '';
    
    transactions.forEach(trans => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${new Date(trans.date).toLocaleDateString()}</td>
            <td>${trans.description}</td>
            <td>${trans.category}</td>
            <td class="${trans.type === 'expense' ? 'danger' : 'success'}" style="color: ${trans.type === 'expense' ? '#dc2626' : '#16a34a'}; font-weight: 500;">
                ${trans.type === 'expense' ? '-' : '+'}₹${trans.amount.toFixed(2)}
            </td>
        `;
    });
}

// Load full transactions list for Transactions page
async function loadTransactionsPage() {
    const searchTerm = document.getElementById('searchTransaction')?.value?.trim() || '';
    const tbody = document.querySelector('#transactionsTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Loading...</td></tr>';
    try {
        let url = `${API_BASE}/transactions/?per_page=100`;
        if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--danger)">Failed to load transactions.</td></tr>';
            return;
        }
        const data = await response.json();
        const transactions = data.transactions || [];
        tbody.innerHTML = '';
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No transactions yet.</td></tr>';
            return;
        }
        const symbol = (userProfile && userProfile.currency === 'INR') ? '₹' : (userProfile && userProfile.currency === 'USD') ? '$' : '';
        transactions.forEach(trans => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${new Date(trans.date).toLocaleDateString()}</td>
                <td><span class="${trans.type === 'expense' ? 'danger' : 'success'}">${trans.type === 'expense' ? 'Expense' : 'Income'}</span></td>
                <td>${trans.category || '-'}</td>
                <td class="${trans.type === 'expense' ? 'danger' : 'success'}" style="color: ${trans.type === 'expense' ? '#dc2626' : '#16a34a'}; font-weight: 500;">
                    ${trans.type === 'expense' ? '-' : '+'}${symbol || ''}${Number(trans.amount).toFixed(2)}
                </td>
                <td>${(trans.description || '').slice(0, 50)}${(trans.description || '').length > 50 ? '…' : ''}</td>
                <td></td>
            `;
        });
    } catch (error) {
        console.error('Error loading transactions:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--black)">Error loading transactions.</td></tr>';
    }
}

// Load categories by type (expense or income), ensure defaults exist if empty
async function loadCategories(type) {
    const endpoint = `${API_BASE}/categories/${type}`;
    let response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (!response.ok) return [];
    let data = await response.json();
    let categories = data.categories || [];
    if (categories.length === 0) {
        await fetch(`${API_BASE}/categories/init-defaults`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        response = await fetch(endpoint, { headers: { 'Authorization': `Bearer ${authToken}` } });
        if (!response.ok) return [];
        data = await response.json();
        categories = data.categories || [];
    }
    return categories;
}

function populateCategorySelect(selectId, categories, placeholder) {
    const select = document.getElementById(selectId);
    select.innerHTML = '';
    const option = document.createElement('option');
    option.value = '';
    option.textContent = placeholder || 'Select category...';
    select.appendChild(option);
    categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = cat.icon ? `${cat.icon} ${cat.name}` : cat.name;
        select.appendChild(opt);
    });
}

// Get or create first account for the user (required for adding transactions)
async function getOrCreateFirstAccount() {
    let response = await fetch(`${API_BASE}/users/accounts`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (!response.ok) return null;
    const data = await response.json();
    const accounts = data.accounts || [];
    if (accounts.length > 0) return accounts[0].id;
    // Create default account if none exist
    response = await fetch(`${API_BASE}/users/accounts`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ account_name: 'Default Account', account_type: 'bank' })
    });
    if (!response.ok) return null;
    const created = await response.json();
    return created.account_id || null;
}

// Add Transaction
async function addTransaction(event) {
    event.preventDefault();
    
    const accountId = await getOrCreateFirstAccount();
    if (!accountId) {
        alert('Could not load or create an account. Please try again.');
        return;
    }
    
    const categoryId = document.getElementById('transCategory').value;
    if (!categoryId) {
        alert('Please select a category.');
        return;
    }
    
    const transaction = {
        amount: parseFloat(document.getElementById('transAmount').value),
        category_id: parseInt(categoryId, 10),
        account_id: accountId,
        description: document.getElementById('transDescription').value.trim() || '',
        transaction_date: document.getElementById('transDate').value
    };
    
    try {
        const endpoint = document.getElementById('transType').value === 'expense' ? 
            `${API_BASE}/expenses/` : `${API_BASE}/income/`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });
        
        const result = await response.json().catch(() => ({}));
        if (response.ok) {
            closeModal('addTransactionModal');
            loadDashboard();
            loadTransactionsPage();
            alert('Transaction added successfully!');
        } else {
            alert(result.error || 'Failed to add transaction.');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        alert('Network error. Please try again.');
    }
}

// Load budgets and display on Budget page
async function loadBudgetsPage() {
    const grid = document.getElementById('budgetGrid');
    if (!grid) return;
    grid.innerHTML = '<p style="text-align:center;color:var(--silver-mid)">Loading budgets...</p>';
    try {
        const response = await fetch(`${API_BASE}/budgets/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) {
            grid.innerHTML = '<p style="text-align:center;color:var(--danger)">Failed to load budgets.</p>';
            return;
        }
        const data = await response.json();
        const budgets = data.budgets || [];
        const symbol = (userProfile && userProfile.currency === 'INR') ? '₹' : (userProfile && userProfile.currency === 'USD') ? '$' : '';
        if (budgets.length === 0) {
            grid.innerHTML = '<p style="text-align:center;color:var(--silver-mid)">No budgets yet. Create one with the button above.</p>';
            return;
        }
        grid.innerHTML = budgets.map(b => {
            const pct = Math.min(100, Math.round(b.percentage || 0));
            const isOver = (b.spent || 0) > (b.limit || 0);
            const fillColor = isOver ? '#dc2626' : (pct >= (b.alert_threshold || 80) ? '#f59e0b' : '#16a34a');
            return `
                <div class="budget-item card" data-budget-id="${b.id}">
                    <h4>${b.category || 'Category'}</h4>
                    <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                        <span>${symbol}${Number(b.spent || 0).toFixed(2)} spent of ${symbol}${Number(b.limit || 0).toFixed(2)}</span>
                        <span style="font-weight:500">${symbol}${Number(b.remaining || 0).toFixed(2)} left</span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%;background:${fillColor}"></div></div>
                    <p style="font-size:0.85rem;color:var(--silver-mid);margin-top:0.5rem;">${pct}% used</p>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading budgets:', error);
        grid.innerHTML = '<p style="text-align:center;color:var(--danger)">Error loading budgets.</p>';
    }
}

// Add Budget
async function addBudget(event) {
    event.preventDefault();
    
    const budget = {
        category_id: document.getElementById('budgetCategory').value,
        amount_limit: parseFloat(document.getElementById('budgetLimit').value),
        alert_threshold: parseFloat(document.getElementById('budgetThreshold').value)
    };
    
    try {
        const response = await fetch(`${API_BASE}/budgets/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(budget)
        });
        
        const result = await response.json().catch(() => ({}));
        if (response.ok) {
            closeModal('addBudgetModal');
            document.getElementById('budgetCategory').value = '';
            document.getElementById('budgetLimit').value = '';
            document.getElementById('budgetThreshold').value = '80';
            loadBudgetsPage();
            alert('Budget created successfully!');
        } else {
            alert(result.error || 'Failed to create budget.');
        }
    } catch (error) {
        console.error('Error creating budget:', error);
        alert('Network error. Please try again.');
    }
}

// Update Profile (saves full name, phone, currency; then switches to text-only view)
async function updateProfile(event) {
    event.preventDefault();
    
    const salaryDayVal = document.getElementById('salaryDay').value;
    const d = parseInt(salaryDayVal, 10);
    const profile = {
        full_name: document.getElementById('fullName').value.trim(),
        phone: (document.getElementById('phone').value || '').trim(),
        currency: document.getElementById('currency').value,
        monthly_income: parseFloat(document.getElementById('monthlyIncome').value) || 0,
        salary_day: (salaryDayVal === '' || isNaN(d)) ? null : Math.min(31, Math.max(1, d))
    };
    
    try {
        const response = await fetch(`${API_BASE}/users/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profile)
        });
        
        if (response.ok) {
            await loadUserProfile();
            showProfileView();
            alert('Profile updated successfully!');
        } else {
            const data = await response.json().catch(() => ({}));
            alert(data.error || 'Failed to update profile');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('Network error. Please try again.');
    }
}

function showProfileView() {
    document.getElementById('profileFormWrap').style.display = 'none';
    document.getElementById('profileView').style.display = 'block';
    const p = userProfile || {};
    const sym = p.currency === 'INR' ? '₹' : p.currency === 'USD' ? '$' : (p.currency || '');
    document.getElementById('profileFullName').textContent = p.full_name || '—';
    document.getElementById('profileEmail').textContent = p.email || '—';
    document.getElementById('profilePhone').textContent = p.phone || '—';
    document.getElementById('profileCurrency').textContent = p.currency ? (p.currency + '') : '—';
    document.getElementById('profilePhoneVerifiedBadge').style.display = p.phone_verified ? 'inline' : 'none';
    const income = p.monthly_income != null && p.monthly_income !== '' ? Number(p.monthly_income) : null;
    document.getElementById('profileMonthlyIncome').textContent = income != null && !isNaN(income) ? (sym + Number(income).toLocaleString('en-IN', { minimumFractionDigits: 2 })) : '—';
    document.getElementById('profileSalaryDay').textContent = p.salary_day != null && p.salary_day >= 1 && p.salary_day <= 31 ? p.salary_day : '—';
}

function showProfileEdit() {
    document.getElementById('profileView').style.display = 'none';
    document.getElementById('profileFormWrap').style.display = 'block';
    populateProfileForm();
}

// Fill profile form with signed-in user data (same details as login/profile API)
function populateProfileForm() {
    if (!userProfile) return;
    const fullNameEl = document.getElementById('fullName');
    const emailEl = document.getElementById('email');
    const phoneEl = document.getElementById('phone');
    const currencyEl = document.getElementById('currency');
    if (fullNameEl) fullNameEl.value = userProfile.full_name || '';
    if (emailEl) emailEl.value = userProfile.email || '';
    if (phoneEl) phoneEl.value = userProfile.phone || '';
    if (currencyEl) {
        currencyEl.value = userProfile.currency || 'USD';
    }
    const monthlyIncomeEl = document.getElementById('monthlyIncome');
    const salaryDayEl = document.getElementById('salaryDay');
    if (monthlyIncomeEl) monthlyIncomeEl.value = userProfile.monthly_income != null && userProfile.monthly_income !== '' ? userProfile.monthly_income : '';
    if (salaryDayEl) salaryDayEl.value = userProfile.salary_day != null && userProfile.salary_day >= 1 && userProfile.salary_day <= 31 ? userProfile.salary_day : '';
    const badge = document.getElementById('phoneVerifiedBadge');
    const otpGroup = document.getElementById('otpVerifyGroup');
    const otpError = document.getElementById('otpError');
    if (badge) badge.style.display = userProfile.phone_verified ? 'inline' : 'none';
    if (otpGroup) otpGroup.style.display = 'none';
    if (otpError) { otpError.style.display = 'none'; otpError.textContent = ''; }
    const oin = document.getElementById('otpInput');
    if (oin) oin.value = '';
}

async function sendPhoneOtp() {
    const phone = document.getElementById('phone')?.value?.trim();
    if (!phone || phone.length < 10) {
        alert('Please enter a valid phone number (at least 10 digits).');
        return;
    }
    const btn = document.getElementById('sendOtpBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
    try {
        const response = await fetch(`${API_BASE}/auth/send-phone-otp`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone })
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            document.getElementById('otpVerifyGroup').style.display = 'block';
            document.getElementById('otpInput').focus();
        } else {
            alert(data.error || 'Failed to send OTP');
        }
    } catch (e) {
        alert('Network error. Please try again.');
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = 'Send OTP'; }
    }
}

async function verifyPhoneOtp() {
    const otp = document.getElementById('otpInput')?.value?.trim();
    if (!otp || otp.length !== 6) {
        document.getElementById('otpError').textContent = 'Enter the 6-digit OTP';
        document.getElementById('otpError').style.display = 'block';
        return;
    }
    const errEl = document.getElementById('otpError');
    errEl.style.display = 'none';
    const btn = document.getElementById('verifyOtpBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Verifying...'; }
    try {
        const response = await fetch(`${API_BASE}/auth/verify-phone-otp`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ otp })
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            await loadUserProfile();
            document.getElementById('phoneVerifiedBadge').style.display = 'inline';
            document.getElementById('otpVerifyGroup').style.display = 'none';
            document.getElementById('otpInput').value = '';
        } else {
            errEl.textContent = data.error || 'Verification failed';
            errEl.style.display = 'block';
        }
    } catch (e) {
        errEl.textContent = 'Network error. Try again.';
        errEl.style.display = 'block';
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = 'Verify'; }
    }
}

// Navigation
async function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page).classList.add('active');
    if (page === 'transactions') loadTransactionsPage();
    if (page === 'budget') loadBudgetsPage();
    if (page === 'profile') {
        await loadUserProfile();
        showProfileView();
    }
}

// Modal Management
async function showModal(modalId) {
    if (modalId === 'addTransactionModal') {
        const type = document.getElementById('transType').value;
        const categories = await loadCategories(type);
        populateCategorySelect('transCategory', categories, 'Select category...');
        const dateInput = document.getElementById('transDate');
        if (dateInput && !dateInput.value) {
            const now = new Date();
            dateInput.value = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        }
    } else if (modalId === 'addBudgetModal') {
        const categories = await loadCategories('expense');
        populateCategorySelect('budgetCategory', categories, 'Select category...');
    }
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// Theme Toggle
function setupTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const isDark = localStorage.getItem('darkMode') === 'true';
    
    if (isDark) {
        document.body.classList.add('dark-mode');
        themeToggle.textContent = '☀️';
    }
    
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        themeToggle.textContent = isDark ? '☀️' : '🌙';
    });
}

// Event Listeners
function setupEventListeners() {
    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    });
    // When transaction type changes, update category dropdown
    const transTypeSelect = document.getElementById('transType');
    if (transTypeSelect) {
        transTypeSelect.addEventListener('change', async () => {
            const type = transTypeSelect.value;
            const categories = await loadCategories(type);
            populateCategorySelect('transCategory', categories, 'Select category...');
        });
    }
    // Search transactions (refetch when user types)
    let searchDebounce;
    const searchInput = document.getElementById('searchTransaction');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchDebounce);
            searchDebounce = setTimeout(loadTransactionsPage, 300);
        });
    }
}

// Logout
function logout() {
    window.location.href = 'login.html';
}

// Export Functions
window.showPage = showPage;
window.showModal = showModal;
window.closeModal = closeModal;
window.addTransaction = addTransaction;
window.addBudget = addBudget;
window.updateProfile = updateProfile;
window.logout = logout;
