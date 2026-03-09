import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const decoded = JSON.parse(jsonPayload);
      setUser({
        full_name: decoded.full_name,
        email: decoded.sub,
        id: decoded.id
      });
    } catch (error) {
      console.error('Error decoding token:', error);
    }

    fetchProfile();
  }, [navigate]);

  const fetchProfile = async () => {
    try {
      const response = await fetch('/profile');
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const getKycBadgeClass = (status) => {
    switch (status) {
      case 'verified':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    }
  };

  const getRiskBadgeClass = (tolerance) => {
    switch (tolerance) {
      case 'conservative':
        return 'bg-blue-100 text-blue-800';
      case 'aggressive':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-purple-100 text-purple-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center text-white text-3xl">
              👋
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome, {user?.full_name}!
              </h1>
              <p className="text-gray-600">Manage your wealth and financial goals</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <button
              onClick={() => navigate('/goals')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors text-center"
            >
              🎯 View Goals
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors text-center"
            >
              👤 My Profile
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors text-center"
            >
              🚪 Logout
            </button>
          </div>
        </div>

        {profile && (
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Account Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Basic Information</h3>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Full Name</span>
                  <span className="font-medium text-gray-900">{profile.full_name}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Email</span>
                  <span className="font-medium text-gray-900">{profile.email}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Member Since</span>
                  <span className="font-medium text-gray-900">
                    {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Risk Profile</h3>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Risk Tolerance</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getRiskBadgeClass(profile.risk_tolerance)}`}>
                    {profile.risk_tolerance}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Investment Horizon</span>
                  <span className="font-medium text-gray-900">{profile.investment_horizon} years</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Annual Income</span>
                  <span className="font-medium text-gray-900">
                    {profile.annual_income ? `$${profile.annual_income.toLocaleString()}` : 'Not specified'}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">KYC Status</span>
                <span className={`px-4 py-2 rounded-full text-sm font-semibold uppercase border ${getKycBadgeClass(profile.kyc_status)}`}>
                  {profile.kyc_status}
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {profile.kyc_status === 'verified' 
                  ? 'Your account is fully verified. You have access to all features.'
                  : profile.kyc_status === 'pending'
                  ? 'Your KYC verification is pending. Please complete the verification process.'
                  : 'Your KYC verification was rejected. Please contact support.'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
