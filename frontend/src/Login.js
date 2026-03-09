import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [showPopup, setShowPopup] = useState(false);
    const [popupMessage, setPopupMessage] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const showPopupMessage = (message) => {
        setPopupMessage(message);
        setShowPopup(true);
    };

    const closePopup = () => {
        setShowPopup(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Basic validation
        if (!formData.email || !formData.password) {
            showPopupMessage('Please fill in all fields');
            return;
        }

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store tokens and user info
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                
                showPopupMessage('Login successful!');
                setTimeout(() => {
                    navigate('/profile');
                }, 1500);
            } else {
                showPopupMessage(data.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showPopupMessage('Connection error. Please ensure the backend is running.');
        }
    };

    const goBack = () => {
        navigate('/');
    };

    const goToRegister = () => {
        navigate('/register');
    };

    return (
        <div className="auth-layout">
            <div className="auth-left gradient-bg">
                <div style={{ textAlign: 'center', maxWidth: '400px' }}>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '20px', fontWeight: 700 }}>Welcome Back</h1>
                    <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>Access your wealth management dashboard</p>
                </div>
            </div>
            <div className="auth-right">
                <div className="auth-content">
                    <button 
                        style={{ marginBottom: '20px', color: '#4f46e5', fontSize: '18px', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer' }} 
                        onClick={goBack}
                    >
                        ← Back
                    </button>
                    <h2 style={{ fontSize: '2rem', marginBottom: '24px', color: '#111827', fontWeight: 700 }}>Login</h2>
                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="email" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Email</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                className="form-input"
                                required
                            />
                        </div>
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="password" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Password</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className="form-input"
                                required
                            />
                        </div>
                        <button type="submit" className="btn-primary" style={{ width: '100%', marginBottom: '20px' }}>Login</button>
                    </form>
                    <p style={{ color: '#4b5563' }}>
                        Don't have an account? <a href="#" onClick={goToRegister} className="nav-link">Register here</a>
                    </p>
                </div>
            </div>
            
            {showPopup && (
                <div className="popup-overlay" onClick={closePopup}>
                    <div className="popup-content" onClick={(e) => e.stopPropagation()}>
                        <span className="popup-close" onClick={closePopup}>&times;</span>
                        <p>{popupMessage}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Login;
