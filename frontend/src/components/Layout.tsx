import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  HomeIcon,
  ChartBarIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  BanknotesIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  CalculatorIcon,
  LightBulbIcon,
  BellIcon,
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Goals', href: '/goals', icon: ChartBarIcon },
    { name: 'Portfolio', href: '/portfolio', icon: BriefcaseIcon },
    { name: 'Transactions', href: '/transactions', icon: BanknotesIcon },
    { name: 'Market Data', href: '/market', icon: CurrencyDollarIcon },
    { name: 'Simulations', href: '/simulations', icon: CalculatorIcon },
    { name: 'Calculators', href: '/calculators', icon: CalculatorIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Recommendations', href: '/recommendations', icon: LightBulbIcon },
    { name: 'Alerts', href: '/alerts', icon: BellIcon },
    { name: 'Charts', href: '/charts', icon: ChartBarIcon },
    { name: 'Profile', href: '/profile', icon: UserIcon },
  ];

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="flex">
        <div className="fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-slate-800 via-slate-700 to-slate-900 shadow-xl">
          <div className="flex h-16 items-center justify-center border-b border-slate-600">
            <h1 className="text-xl font-bold text-white">Wealth Manager</h1>
          </div>
          
          <nav className="mt-8 px-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                          : 'text-slate-300 hover:bg-slate-600 hover:text-white'
                      }`}
                    >
                      <item.icon
                        className={`mr-3 h-5 w-5 ${
                          isActive ? 'text-white' : 'text-slate-400'
                        }`}
                        aria-hidden="true"
                      />
                      {item.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-600 bg-slate-800/50 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                  <span className="text-white text-sm font-medium">
                    {user?.full_name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-white">{user?.full_name}</p>
                  <p className="text-xs text-slate-400 capitalize">{user?.kyc_status}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded-lg transition-all duration-200"
                title="Logout"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 ml-64">
          <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-blue-100">
            <div className="px-6 py-4">
              <h2 className="text-2xl font-semibold text-gray-900">
                {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
              </h2>
            </div>
          </header>

          <main className="p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
