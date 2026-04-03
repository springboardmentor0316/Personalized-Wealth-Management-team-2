import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { RiskProfile, KYCStatus } from '../types';
import { ChartBarIcon, BanknotesIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [fullName, setFullName] = useState('');
  const [riskProfile, setRiskProfile] = useState<RiskProfile>(RiskProfile.MODERATE);
  const [error, setError] = useState('');
  const { login, register, loading, isAuthenticated, error: authError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegistering) {
        await register({
          email,
          full_name: fullName,
          password,
          risk_profile: riskProfile,
          kyc_status: KYCStatus.PENDING,
        });
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="mb-8">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center mr-4">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <h1 className="text-3xl font-bold">Wealth Manager</h1>
            </div>
            <h2 className="text-4xl font-bold mb-4">
              Your Path to Financial Freedom
            </h2>
            <p className="text-xl text-blue-100 leading-relaxed">
              Take control of your financial future with intelligent goal tracking, 
              portfolio management, and personalized investment insights.
            </p>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center mr-4">
                <BanknotesIcon className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Smart Portfolio Management</h3>
                <p className="text-blue-100">Track investments and monitor performance</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center mr-4">
                <ShieldCheckIcon className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Secure & Private</h3>
                <p className="text-blue-100">Bank-level security for your financial data</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-72 h-72 bg-white opacity-5 rounded-full"></div>
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-white opacity-5 rounded-full"></div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-md w-full">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <ChartBarIcon className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Wealth Manager</h1>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                {isRegistering ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="text-gray-600">
                {isRegistering 
                  ? 'Start your journey to financial wellness' 
                  : 'Login to manage your wealth'
                }
              </p>
            </div>
            
            <form className="space-y-6" onSubmit={handleSubmit}>
              {(error || authError) && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  {error || authError}
                </div>
              )}
              
              <div className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-gray-900 placeholder-gray-400"
                    placeholder="you@example.com"
                  />
                </div>

                {isRegistering && (
                  <div>
                    <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <input
                      id="fullName"
                      name="fullName"
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-gray-900 placeholder-gray-400"
                      placeholder="John Doe"
                    />
                  </div>
                )}

                {isRegistering && (
                  <div>
                    <label htmlFor="riskProfile" className="block text-sm font-medium text-gray-700 mb-2">
                      Investment Risk Profile
                    </label>
                    <select
                      id="riskProfile"
                      name="riskProfile"
                      value={riskProfile}
                      onChange={(e) => setRiskProfile(e.target.value as RiskProfile)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-gray-900 bg-white"
                    >
                      <option value={RiskProfile.CONSERVATIVE}>Conservative - Low Risk, Stable Returns</option>
                      <option value={RiskProfile.MODERATE}>Moderate - Balanced Risk & Growth</option>
                      <option value={RiskProfile.AGGRESSIVE}>Aggressive - High Risk, High Returns</option>
                    </select>
                  </div>
                )}

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete={isRegistering ? 'new-password' : 'current-password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-gray-900 placeholder-gray-400"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02]"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    isRegistering ? 'Create Account' : 'Login'
                  )}
                </button>
              </div>

              <div className="text-center pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-600">
                  {isRegistering ? 'Already have an account?' : "Don't have an account?"}{' '}
                  <button
                    type="button"
                    onClick={() => setIsRegistering(!isRegistering)}
                    className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                  >
                    {isRegistering ? 'Login' : 'Create Account'}
                  </button>
                </span>
              </div>
            </form>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>By continuing, you agree to our Terms of Service and Privacy Policy</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
