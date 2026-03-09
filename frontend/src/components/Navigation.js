import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Navigation = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    onLogout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  const navLinkClass = (path) => `
    px-4 py-2 rounded-lg font-medium transition-all duration-200
    ${isActive(path) 
      ? 'bg-indigo-100 text-indigo-700' 
      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'}
  `;

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                W
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Wealth Management
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-2">
            {user ? (
              <>
                <Link to="/profile" className={navLinkClass('/profile')}>
                  <span className="flex items-center gap-1">👤 Profile</span>
                </Link>
                <Link to="/goals" className={navLinkClass('/goals')}>
                  <span className="flex items-center gap-1">🎯 Goals</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="ml-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition-all duration-200 flex items-center gap-1"
                >
                  🚪 Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className={navLinkClass('/login')}>
                  <span className="flex items-center gap-1">🔐 Login</span>
                </Link>
                <Link 
                  to="/register" 
                  className="ml-4 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
