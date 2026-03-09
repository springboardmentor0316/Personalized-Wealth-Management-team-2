import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const navigate = useNavigate();
    
    console.log('Register component is rendering'); // Debug log

    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        password: '',
        risk_tolerance: 'moderate',
        investment_horizon: 5,
        annual_income: ''
    });
    const [showPopup, setShowPopup] = useState(false);
    const [popupMessage, setPopupMessage] = useState('');
    const [connectionStatus, setConnectionStatus] = useState('');

    const testConnection = async () => {
        try {
            setConnectionStatus('Testing...');
            const response = await fetch('/health', {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setConnectionStatus(`✅ Connected: ${data.message}`);
            } else {
                setConnectionStatus(`❌ Server error: ${response.status}`);
            }
        } catch (error) {
            setConnectionStatus(`❌ Connection failed: ${error.message || 'Check if backend is running'}`);
        }
    };

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
        if (!formData.fullName || !formData.email || !formData.password) {
            showPopupMessage('Please fill in all required fields');
            return;
        }
        
        if (formData.password.length < 6) {
            showPopupMessage('Password must be at least 6 characters long');
            return;
        }

        try {
            const backendData = {
                full_name: formData.fullName,
                email: formData.email,
                password: formData.password,
                risk_tolerance: formData.risk_tolerance,
                investment_horizon: parseInt(formData.investment_horizon),
                annual_income: formData.annual_income ? parseInt(formData.annual_income) : null
            };

            console.log('Attempting to connect to:', '/register');
            console.log('With data:', backendData);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

            const response = await fetch('/register', {
                method: 'POST',
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(backendData),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            console.log('Response received:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response body:', errorText);
                showPopupMessage(`Server error ${response.status}: ${errorText || 'Unknown error'}`);
                return;
            }
            
            const data = await response.json();
            console.log('Success:', data);
            
            showPopupMessage('Registration successful! Please login.');
            setTimeout(() => {
                navigate('/login');
            }, 2000);
            
        } catch (error) {
            console.error('Full error:', error);
            console.error('Error name:', error.name);
            console.error('Error message:', error.message);
            if (error.name === 'AbortError') {
                showPopupMessage('Connection timeout. Backend server may not be running.');
            } else if (error.name === 'TypeError') {
                showPopupMessage(`Network/CORS error: ${error.message}. Check backend.`);
            } else {
                showPopupMessage(`Connection failed: ${error.name} - ${error.message || 'Unknown error'}`);
            }
        }
    };

    const goBack = () => {
        navigate('/');
    };

    const goToLogin = () => {
        navigate('/login');
    };

    return (
        <div className="auth-layout">
            <div className="auth-left gradient-bg">
                <div style={{ textAlign: 'center', maxWidth: '400px' }}>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '20px', fontWeight: 700 }}>Create Account</h1>
                    <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>Join our wealth management platform</p>
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
                    <h2 style={{ fontSize: '2rem', marginBottom: '24px', color: '#111827', fontWeight: 700 }}>Register</h2>
                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="fullName" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Full Name</label>
                            <input
                                type="text"
                                id="fullName"
                                name="fullName"
                                value={formData.fullName}
                                onChange={handleChange}
                                className="form-input"
                                required
                            />
                        </div>
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
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="risk_tolerance" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Risk Tolerance</label>
                            <select
                                id="risk_tolerance"
                                name="risk_tolerance"
                                value={formData.risk_tolerance}
                                onChange={handleChange}
                                className="form-input"
                            >
                                <option value="conservative">Conservative</option>
                                <option value="moderate">Moderate</option>
                                <option value="aggressive">Aggressive</option>
                            </select>
                        </div>
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="investment_horizon" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Investment Horizon (years)</label>
                            <input
                                type="number"
                                id="investment_horizon"
                                name="investment_horizon"
                                value={formData.investment_horizon}
                                onChange={handleChange}
                                className="form-input"
                                min="1"
                                max="30"
                            />
                        </div>
                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="annual_income" style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>Annual Income ($)</label>
                            <input
                                type="number"
                                id="annual_income"
                                name="annual_income"
                                value={formData.annual_income}
                                onChange={handleChange}
                                className="form-input"
                                min="0"
                            />
                        </div>
                        <div style={{marginTop: '20px', marginBottom: '20px', padding: '10px', border: '2px dashed #ccc', borderRadius: '8px', textAlign: 'center'}}>
                            <button 
                                type="button" 
                                onClick={testConnection}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    marginBottom: '10px'
                                }}
                            >
                                Test Backend Connection
                            </button>
                            {connectionStatus && (
                                <div style={{
                                    fontSize: '14px',
                                    color: connectionStatus.includes('✅') ? '#065f46' : '#dc2626',
                                    fontWeight: '500',
                                    marginTop: '5px'
                                }}>
                                    {connectionStatus}
                                </div>
                            )}
                        </div>
                        <div style={{marginTop: '30px', marginBottom: '30px'}}>
                            <button type="submit" style={{
                                width: '100%',
                                height: '60px',
                                backgroundColor: '#2563eb',
                                color: 'white',
                                fontSize: '18px',
                                fontWeight: 'bold',
                                border: 'none',
                                cursor: 'pointer',
                                borderRadius: '8px',
                                textTransform: 'uppercase',
                                letterSpacing: '1px'
                            }}>
                                CREATE ACCOUNT
                            </button>
                        </div>
                        <div style={{marginTop: '20px', marginBottom: '30px', padding: '15px', backgroundColor: '#dc2626', color: 'white', borderRadius: '8px', textAlign: 'center'}}>
                            TEST ELEMENT - If you can see this, the button should be above
                        </div>
                    </form>
                    <p style={{ color: '#4b5563' }}>
                        Already have an account? <a href="#" onClick={goToLogin} className="nav-link">Login here</a>
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

export default Register;
