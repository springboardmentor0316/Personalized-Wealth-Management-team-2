import React from 'react';
import { useNavigate } from 'react-router-dom';

const Welcome = () => {
    const navigate = useNavigate();

    const goToRegister = () => {
        navigate('/register');
    };

    const goToLogin = () => {
        navigate('/login');
    };

    return (
        <div className="auth-layout">
            <div className="auth-left gradient-bg">
                <div style={{ textAlign: 'center', maxWidth: '400px' }}>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '20px', fontWeight: 700 }}>Personalized Wealth Management</h1>
                    <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>Please Register / Already registered? please login</p>
                </div>
            </div>
            <div className="auth-right">
                <div className="auth-content" style={{ textAlign: 'center' }}>
                    <h2 style={{ fontSize: '2rem', marginBottom: '10px', color: '#333' }}>Welcome to Wealth Management</h2>
                    <p style={{ marginBottom: '30px', color: '#666', fontSize: '1rem' }}>Choose an option to get started</p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        <button className="btn-primary" style={{ width: '100%' }} onClick={goToRegister}>
                            Register
                        </button>
                        <button className="btn-secondary" style={{ width: '100%' }} onClick={goToLogin}>
                            Login
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Welcome;
