// API Settings
const API_BASE_URL = 'http://localhost:8000/api';

// OTP Timer variables
let otpTimerInterval = null;
let otpTimerSeconds = 300; // 5 minutes in seconds

// Helper functions
function showMessage(message, type = 'info') {
    const messageEl = document.getElementById('message');
    if (!messageEl) return;
    
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    // Clear message after 5 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

function setLoading(buttonId, isLoading) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    
    if (isLoading) {
        btn.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (btnLoader) btnLoader.style.display = 'block';
    } else {
        btn.disabled = false;
        if (btnText) btnText.style.display = 'inline';
        if (btnLoader) btnLoader.style.display = 'none';
    }
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        credentials: 'include'
    };
    
    if (data && method !== 'GET') {
        // Remove null fields
        const cleanData = {};
        for (const key in data) {
            if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
                cleanData[key] = data[key];
            }
        }
        options.body = JSON.stringify(cleanData);
    }
    
    try {
        console.log(`[API] ${method} ${endpoint}`, data ? JSON.stringify(data) : '');
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        // Get content type
        const contentType = (response.headers.get('content-type') || '').toLowerCase();
        const isJson = contentType.includes('application/json');
        
        // Read response as text first
        let responseText = '';
        try {
            responseText = await response.text();
        } catch (e) {
            console.error('[API Error] Failed to read response:', e);
            throw new Error('Server connection error. Please ensure the server is running.');
        }
        
        // Check if response is empty
        if (!responseText || responseText.trim() === '') {
            console.error(`[API Error] Empty response. Status: ${response.status}`);
            throw new Error(`Server returned empty response (Status: ${response.status}). Please check the server.`);
        }
        
        // Try to parse as JSON
        // First check if it looks like JSON (starts with { or [)
        const looksLikeJson = responseText.trim().startsWith('{') || responseText.trim().startsWith('[');
        
        let result;
        if (isJson || looksLikeJson) {
            try {
                result = JSON.parse(responseText);
            } catch (parseError) {
                console.error(`[API Error] JSON parse error:`, parseError);
                console.error(`[API Error] Content-Type: ${contentType}`);
                console.error(`[API Error] Response text:`, responseText.substring(0, 200));
                throw new Error(`Invalid JSON response from server: ${responseText.substring(0, 100)}`);
            }
        } else {
            // Not JSON - might be HTML error page or plain text
            console.error(`[API Error] Non-JSON response. Content-Type: ${contentType}`);
            console.error(`[API Error] Response text:`, responseText.substring(0, 200));
            throw new Error(`Server returned non-JSON response (Status: ${response.status}). Please check the server.`);
        }
        
        // Check HTTP status
        if (!response.ok) {
            const errorMessage = result.message || `HTTP Error ${response.status}`;
            console.error(`[API Error] Status: ${response.status}, Message:`, errorMessage);
            throw new Error(errorMessage);
        }
        
        console.log(`[API Response]`, result);
        return result;
    } catch (error) {
        console.error('[API Error]', error);
        // If network error
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('NetworkError') ||
            error.message.includes('Network request failed') ||
            error.message.includes('fetch')) {
            throw new Error('Server connection error. Please ensure the server is running.');
        }
        throw error;
    }
}

// Check authentication status
async function checkAuthStatus() {
    try {
        const result = await apiRequest('/check-auth');
        if (result.success && result.authenticated) {
            // User is logged in, redirect to dashboard
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
}

// Registration
async function register(event) {
    // Prevent form submission and page scroll
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const phone = document.getElementById('registerPhone').value.trim();
    
    // Validation
    if (!firstName || !lastName) {
        showMessage('Please enter first name and last name', 'error');
        return false;
    }
    
    if (!email && !phone) {
        showMessage('Please enter email or phone number', 'error');
        return false;
    }
    
    setLoading('registerBtn', true);
    
    try {
        const requestData = {
            first_name: firstName,
            last_name: lastName
        };
        
        if (email) {
            requestData.email = email;
        }
        if (phone) {
            requestData.phone = phone;
        }
        
        const result = await apiRequest('/register', 'POST', requestData);
        
        if (result.success) {
            // Display OTP form
            const identifier = result.data?.identifier || result.identifier || (email || phone);
            showOtpForm(identifier, 'register');
            showMessage(result.message || 'Verification code sent', 'success');
        } else {
            showMessage(result.message || 'Registration error', 'error');
        }
    } catch (error) {
        const errorMessage = error.message || 'Server connection error. Please ensure the server is running.';
        showMessage(errorMessage, 'error');
        console.error('Register error:', error);
    } finally {
        setLoading('registerBtn', false);
    }
    
    return false;
}

// Login
async function login(event) {
    // Prevent form submission and page scroll
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const email = document.getElementById('loginEmail').value.trim();
    const phone = document.getElementById('loginPhone').value.trim();
    
    // Validation
    if (!email && !phone) {
        showMessage('Please enter email or phone number', 'error');
        return false;
    }
    
    setLoading('loginBtn', true);
    
    try {
        const result = await apiRequest('/login', 'POST', {
            email: email || null,
            phone: phone || null
        });
        
        if (result.success) {
            if (result.data?.direct_login || result.direct_login) {
                // Direct login
                window.location.href = 'dashboard.html';
            } else {
                // Requires verification
                const identifier = result.data?.identifier || result.identifier || (email || phone);
                showOtpForm(identifier, 'login');
                showMessage(result.message || 'Verification code sent', 'success');
            }
        } else {
            showMessage(result.message || 'Login error', 'error');
        }
    } catch (error) {
        const errorMessage = error.message || 'Server connection error. Please ensure the server is running.';
        showMessage(errorMessage, 'error');
        console.error('Login error:', error);
    } finally {
        setLoading('loginBtn', false);
    }
    
    return false;
}

// Start OTP Timer
function startOtpTimer() {
    // Reset timer to 5 minutes (300 seconds)
    otpTimerSeconds = 300;
    
    // Clear any existing timer
    stopOtpTimer();
    
    // Get timer element
    const timerElement = document.getElementById('otpTimer');
    if (!timerElement) return;
    
    // Update timer display immediately
    updateTimerDisplay();
    
    // Start countdown
    otpTimerInterval = setInterval(() => {
        otpTimerSeconds--;
        updateTimerDisplay();
        
        if (otpTimerSeconds <= 0) {
            stopOtpTimer();
            timerElement.textContent = '00:00';
            timerElement.classList.add('expired');
            showMessage('Verification code has expired. Please request a new code.', 'error');
        }
    }, 1000);
}

// Stop OTP Timer
function stopOtpTimer() {
    if (otpTimerInterval) {
        clearInterval(otpTimerInterval);
        otpTimerInterval = null;
    }
}

// Update Timer Display
function updateTimerDisplay() {
    const timerElement = document.getElementById('otpTimer');
    if (!timerElement) return;
    
    const minutes = Math.floor(otpTimerSeconds / 60);
    const seconds = otpTimerSeconds % 60;
    const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    timerElement.textContent = formattedTime;
    
    // Add warning class when less than 1 minute
    if (otpTimerSeconds <= 60) {
        timerElement.classList.add('warning');
        timerElement.classList.remove('expired');
    } else {
        timerElement.classList.remove('warning', 'expired');
    }
}

// Show OTP form
function showOtpForm(identifier, type) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const otpForm = document.getElementById('otpForm');
    const otpIdentifier = document.getElementById('otpIdentifier');
    
    if (loginForm) loginForm.style.display = 'none';
    if (registerForm) registerForm.style.display = 'none';
    if (otpForm) {
        otpForm.style.display = 'block';
        if (otpIdentifier) otpIdentifier.textContent = identifier;
    }
    
    // Save operation type
    otpForm.dataset.type = type;
    otpForm.dataset.identifier = identifier;
    
    // Clear OTP field
    const otpInput = document.getElementById('otpCode');
    if (otpInput) otpInput.value = '';
    
    // Start OTP timer
    startOtpTimer();
}

// Return to main form
function backToForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const otpForm = document.getElementById('otpForm');
    
    // Stop timer when leaving OTP form
    stopOtpTimer();
    
    if (otpForm) {
        const type = otpForm.dataset.type;
        otpForm.style.display = 'none';
        
        // Reset timer display
        const timerElement = document.getElementById('otpTimer');
        if (timerElement) {
            timerElement.textContent = '05:00';
            timerElement.classList.remove('warning', 'expired');
        }
        
        if (type === 'login' && loginForm) {
            loginForm.style.display = 'block';
        } else if (type === 'register' && registerForm) {
            registerForm.style.display = 'block';
        }
    }
}

// Verify OTP
let isVerifyingOtp = false;

async function verifyOtp() {
    // Prevent concurrent requests
    if (isVerifyingOtp) {
        return;
    }
    
    const otpForm = document.getElementById('otpForm');
    const otpCode = document.getElementById('otpCode').value.trim();
    const type = otpForm ? otpForm.dataset.type : null;
    const identifier = otpForm ? otpForm.dataset.identifier : null;
    
    if (!otpCode || otpCode.length !== 6) {
        showMessage('Please enter a 6-digit code', 'error');
        return;
    }
    
    if (!identifier) {
        showMessage('Identifier not found. Please try again.', 'error');
        return;
    }
    
    isVerifyingOtp = true;
    setLoading('verifyOtpBtn', true);
    
    try {
        if (type === 'register') {
            // Verify OTP for registration
            const result = await apiRequest('/verify-otp', 'POST', {
                identifier: identifier,
                otp: otpCode
            });
            
            if (result.success) {
                stopOtpTimer();
                showMessage(result.message || 'Registration successful', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                showMessage(result.message || 'Invalid verification code', 'error');
            }
        } else if (type === 'login') {
            // Verify OTP for login
            const result = await apiRequest('/verify-login-otp', 'POST', {
                identifier: identifier,
                otp: otpCode
            });
            
            if (result.success) {
                stopOtpTimer();
                showMessage(result.message || 'Login successful', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                showMessage(result.message || 'Invalid verification code', 'error');
            }
        } else {
            showMessage('Unknown operation type', 'error');
        }
    } catch (error) {
        const errorMessage = error.message || 'Server connection error. Please ensure the server is running.';
        showMessage(errorMessage, 'error');
        console.error('Verify OTP error:', error);
    } finally {
        isVerifyingOtp = false;
        setLoading('verifyOtpBtn', false);
    }
}

// Resend OTP
async function resendOtp() {
    const otpForm = document.getElementById('otpForm');
    const type = otpForm ? otpForm.dataset.type : null;
    const identifier = otpForm ? otpForm.dataset.identifier : null;
    
    if (!identifier) {
        showMessage('Error retrieving information', 'error');
        return;
    }
    
    try {
        if (type === 'register') {
            // For registration, we need to resubmit the form
            showMessage('Please fill out the registration form again', 'info');
            backToForm();
        } else if (type === 'login') {
            // For login, resend OTP
            const email = document.getElementById('loginEmail')?.value.trim();
            const phone = document.getElementById('loginPhone')?.value.trim();
            
            const result = await apiRequest('/login', 'POST', {
                email: email || null,
                phone: phone || null
            });
            
            if (result.success) {
                // Restart timer when OTP is resent
                startOtpTimer();
                showMessage('Verification code resent', 'success');
            } else {
                showMessage(result.message || 'Error resending code', 'error');
            }
        }
    } catch (error) {
        showMessage('Server connection error', 'error');
    }
}

// Logout
async function logout() {
    try {
        const result = await apiRequest('/logout', 'POST');
        if (result.success) {
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Even on error, redirect to login page
        window.location.href = 'index.html';
    }
}

// Load user information
async function loadUserInfo() {
    try {
        const result = await apiRequest('/check-auth');
        if (result.success && result.authenticated && result.user) {
            const user = result.user;
            const userName = document.getElementById('userName');
            const userEmail = document.getElementById('userEmail');
            const userPhone = document.getElementById('userPhone');
            
            if (userName) {
                userName.textContent = `${user.first_name} ${user.last_name}`;
            }
            
            if (userEmail && user.email) {
                userEmail.textContent = `📧 ${user.email}`;
                userEmail.style.display = 'block';
            } else if (userEmail) {
                userEmail.style.display = 'none';
            }
            
            if (userPhone && user.phone) {
                userPhone.textContent = `📱 ${user.phone}`;
                userPhone.style.display = 'block';
            } else if (userPhone) {
                userPhone.style.display = 'none';
            }
        } else {
            // User is not logged in, redirect to login page
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Load user info error:', error);
        window.location.href = 'index.html';
    }
}

// Login page events
if (document.getElementById('loginBtn')) {
    const loginBtn = document.getElementById('loginBtn');
    loginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        login(e);
        return false;
    });
    
    // Login with Enter key
    ['loginEmail', 'loginPhone'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    login(e);
                    return false;
                }
            });
        }
    });
}

// Registration page events
if (document.getElementById('registerBtn')) {
    const registerBtn = document.getElementById('registerBtn');
    registerBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        register(e);
        return false;
    });
    
    // Register with Enter key
    ['firstName', 'lastName', 'registerEmail', 'registerPhone'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    register(e);
                    return false;
                }
            });
        }
    });
}

// OTP form events
if (document.getElementById('verifyOtpBtn')) {
    document.getElementById('verifyOtpBtn').addEventListener('click', verifyOtp);
    
    const otpInput = document.getElementById('otpCode');
    if (otpInput) {
        otpInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                verifyOtp();
            }
        });
        
        // Only numbers
        otpInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }
}

if (document.getElementById('resendOtpBtn')) {
    document.getElementById('resendOtpBtn').addEventListener('click', resendOtp);
}

if (document.getElementById('backToLoginBtn')) {
    document.getElementById('backToLoginBtn').addEventListener('click', backToForm);
}

if (document.getElementById('backToRegisterBtn')) {
    document.getElementById('backToRegisterBtn').addEventListener('click', backToForm);
}


