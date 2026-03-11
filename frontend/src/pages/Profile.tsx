import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { RiskProfile, KYCStatus } from '../types';
import {
  UserIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

const Profile: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    risk_profile: user?.risk_profile || RiskProfile.MODERATE,
    kyc_status: user?.kyc_status || KYCStatus.PENDING,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await updateProfile(formData);
      setMessage('Profile updated successfully!');
      setIsEditing(false);
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Error updating profile');
    } finally {
      setLoading(false);
    }
  };

  const getRiskProfileDescription = (profile: RiskProfile) => {
    const descriptions = {
      [RiskProfile.CONSERVATIVE]: 'Low risk tolerance, prefers stable investments with minimal volatility',
      [RiskProfile.MODERATE]: 'Balanced risk tolerance, seeks mix of growth and stability',
      [RiskProfile.AGGRESSIVE]: 'High risk tolerance, seeks maximum growth potential',
    };
    return descriptions[profile];
  };

  const getKYCStatusColor = (status: KYCStatus) => {
    const colors = {
      [KYCStatus.PENDING]: 'bg-yellow-100 text-yellow-800',
      [KYCStatus.VERIFIED]: 'bg-green-100 text-green-800',
      [KYCStatus.REJECTED]: 'bg-red-100 text-red-800',
    };
    return colors[status];
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        </div>

        <div className="p-6">
          {message && (
            <div className={`mb-4 p-4 rounded-md ${
              message.includes('success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`}>
              {message}
            </div>
          )}

          <div className="flex items-center mb-6">
            <div className="h-20 w-20 rounded-full bg-blue-500 flex items-center justify-center">
              <span className="text-white text-2xl font-bold">
                {user?.full_name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="ml-6">
              <h2 className="text-xl font-semibold text-gray-900">{user?.full_name}</h2>
              <p className="text-gray-600">{user?.email}</p>
              <p className="text-sm text-gray-500 mt-1">
                Member since {new Date(user?.created_at || '').toLocaleDateString()}
              </p>
            </div>
          </div>

          {!isEditing ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <UserIcon className="h-5 w-5 mr-2 text-gray-400" />
                    Personal Information
                  </h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user?.full_name}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Email Address</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
                    </div>
                  </dl>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <ShieldCheckIcon className="h-5 w-5 mr-2 text-gray-400" />
                    Investment Profile
                  </h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Risk Profile</dt>
                      <dd className="mt-1">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                          {user?.risk_profile}
                        </span>
                      </dd>
                      <p className="mt-1 text-sm text-gray-600">
                        {getRiskProfileDescription(user?.risk_profile || RiskProfile.MODERATE)}
                      </p>
                    </div>
                  </dl>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <DocumentTextIcon className="h-5 w-5 mr-2 text-gray-400" />
                  KYC Status
                </h3>
                <div className="flex items-center space-x-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getKYCStatusColor(user?.kyc_status || KYCStatus.PENDING)}`}>
                    {user?.kyc_status}
                  </span>
                  {user?.kyc_status === KYCStatus.PENDING && (
                    <p className="text-sm text-gray-600">
                      Your KYC verification is pending. Please complete the verification process to unlock all features.
                    </p>
                  )}
                  {user?.kyc_status === KYCStatus.VERIFIED && (
                    <p className="text-sm text-green-600">
                      Your account has been verified. You have access to all features.
                    </p>
                  )}
                  {user?.kyc_status === KYCStatus.REJECTED && (
                    <p className="text-sm text-red-600">
                      Your verification was rejected. Please contact support for assistance.
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-6 border-t border-gray-200">
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Profile Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="full_name"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="risk_profile" className="block text-sm font-medium text-gray-700">
                      Risk Profile
                    </label>
                    <select
                      id="risk_profile"
                      value={formData.risk_profile}
                      onChange={(e) => setFormData({ ...formData, risk_profile: e.target.value as RiskProfile })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={RiskProfile.CONSERVATIVE}>Conservative</option>
                      <option value={RiskProfile.MODERATE}>Moderate</option>
                      <option value={RiskProfile.AGGRESSIVE}>Aggressive</option>
                    </select>
                    <p className="mt-1 text-sm text-gray-500">
                      {getRiskProfileDescription(formData.risk_profile)}
                    </p>
                  </div>
                </div>

                <div className="mt-6">
                  <label htmlFor="kyc_status" className="block text-sm font-medium text-gray-700">
                    KYC Status
                  </label>
                  <select
                    id="kyc_status"
                    value={formData.kyc_status}
                    onChange={(e) => setFormData({ ...formData, kyc_status: e.target.value as KYCStatus })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={KYCStatus.PENDING}>Pending</option>
                    <option value={KYCStatus.VERIFIED}>Verified</option>
                    <option value={KYCStatus.REJECTED}>Rejected</option>
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Note: In production, KYC status would be updated through a formal verification process.
                  </p>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setFormData({
                      full_name: user?.full_name || '',
                      risk_profile: user?.risk_profile || RiskProfile.MODERATE,
                      kyc_status: user?.kyc_status || KYCStatus.PENDING,
                    });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
