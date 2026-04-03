import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { goalsAPI, portfolioAPI } from '../services/api';
import { Goal, Portfolio } from '../types';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [goalsData, portfolioData] = await Promise.all([
          goalsAPI.getGoals(),
          portfolioAPI.getPortfolio(),
        ]);
        setGoals(goalsData);
        setPortfolio(portfolioData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const totalGoalTarget = goals.reduce((sum, goal) => sum + goal.target_amount, 0);
  const totalGoalProgress = goals.reduce((sum, goal) => sum + goal.current_amount, 0);
  const goalProgressPercentage = totalGoalTarget > 0 ? (totalGoalProgress / totalGoalTarget) * 100 : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-gray-600">
          Here's an overview of your financial goals and portfolio performance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Portfolio Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${portfolio?.summary.total_value.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Returns</p>
              <p className={`text-2xl font-bold ${
                (portfolio?.summary?.total_gain_loss ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${portfolio?.summary.total_gain_loss.toFixed(2) || '0.00'}
              </p>
              <p className={`text-sm ${
                (portfolio?.summary?.total_gain_loss_percent ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {portfolio?.summary.total_gain_loss_percent.toFixed(2) || '0.00'}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-full">
              <TagIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Goals Progress</p>
              <p className="text-2xl font-bold text-gray-900">
                {goalProgressPercentage.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">
                ${totalGoalProgress.toFixed(0)} / ${totalGoalTarget.toFixed(0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-full">
              <ChartBarIcon className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Risk Profile</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">
                {user?.risk_profile}
              </p>
              <p className="text-sm text-gray-600 capitalize">
                KYC: {user?.kyc_status}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Goals</h2>
          {goals.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No goals yet. Create your first goal!</p>
          ) : (
            <div className="space-y-4">
              {goals.slice(0, 5).map((goal) => (
                <div key={goal.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{goal.title}</p>
                    <p className="text-sm text-gray-600">
                      ${goal.current_amount.toFixed(0)} / ${goal.target_amount.toFixed(0)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {((goal.current_amount / goal.target_amount) * 100).toFixed(1)}%
                    </p>
                    <div className="w-16 h-2 bg-gray-200 rounded-full mt-1">
                      <div
                        className="h-2 bg-blue-600 rounded-full"
                        style={{
                          width: `${Math.min((goal.current_amount / goal.target_amount) * 100, 100)}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Investments</h2>
          {portfolio?.investments.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No investments yet. Start building your portfolio!</p>
          ) : (
            <div className="space-y-4">
              {portfolio?.investments.slice(0, 5).map((investment) => (
                <div key={investment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{investment.symbol}</p>
                    <p className="text-sm text-gray-600">{investment.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      ${investment.current_value.toFixed(2)}
                    </p>
                    <p className={`text-sm ${
                      investment.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {investment.gain_loss >= 0 ? '+' : ''}{investment.gain_loss_percent.toFixed(2)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
