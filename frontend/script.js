// Navigation functions
function goToRegister() {
    window.location.href = 'register.html';
}

function goToLogin() {
    window.location.href = 'login.html';
}

function goBack() {
    window.location.href = 'index.html';
}

// Popup functions
function showPopup(message) {
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popupMessage');
    popupMessage.textContent = message;
    popup.style.display = 'block';
}

function closePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

// Form validation and submission
document.addEventListener('DOMContentLoaded', function() {
    // Handle registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Basic validation
            if (!fullName || !email || !password) {
                showPopup('Please fill in all fields');
                return;
            }
            
            if (password.length < 6) {
                showPopup('Password must be at least 6 characters long');
                return;
            }
            
            // Send registration data to backend
            try {
                const response = await fetch('http://localhost:3000/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        fullName: fullName,
                        email: email,
                        password: password
                    })
                });
                
                const data = await response.json();
                
                if (response.status === 409) {
                    // User already registered
                    showPopup('You have already registered. Please login.');
                } else if (response.ok) {
                    showPopup('Registration successful! Please login.');
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                } else {
                    showPopup(data.message || 'Registration failed');
                }
            } catch (error) {
                console.error('Error:', error);
                showPopup('Connection error. Please try again.');
            }
        });
    }
    
    // Handle login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Basic validation
            if (!email || !password) {
                showPopup('Please fill in all fields');
                return;
            }
            
            // Send login data to backend
            try {
                const response = await fetch('http://localhost:3000/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showPopup('Login successful!');
                    // Store user info in localStorage for session management
                    localStorage.setItem('user', JSON.stringify(data.user));
                    setTimeout(() => {
                        // Redirect to dashboard or home page after successful login
                        // For now, let's go back to welcome page
                        window.location.href = 'index.html';
                    }, 1500);
                } else {
                    showPopup(data.message || 'Login failed');
                }
            } catch (error) {
                console.error('Error:', error);
                showPopup('Connection error. Please try again.');
            }
        });
    }
});

// Close popup when clicking outside
window.onclick = function(event) {
    const popup = document.getElementById('popup');
    if (event.target === popup) {
        closePopup();
    }
}
