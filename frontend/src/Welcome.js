import React from 'react';
import { Link } from 'react-router-dom';

const Welcome = () => {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
        <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-6 text-indigo-600 text-3xl">
          💰
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">Wealth Management</h1>
        <p className="text-indigo-100 mb-8">Your personal wealth management platform</p>
        
        <div className="space-y-4">
          <Link to="/register">
            <button className="w-full bg-white hover:bg-gray-100 text-indigo-600 font-semibold py-3 px-6 rounded-lg transition-colors mb-4">
              Create Account
            </button>
          </Link>
          <Link to="/login">
            <button className="w-full bg-transparent border-2 border-white text-white hover:bg-white hover:text-indigo-600 font-semibold py-3 px-6 rounded-lg transition-colors">
              Sign In
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
