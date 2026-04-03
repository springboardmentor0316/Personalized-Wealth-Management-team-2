import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface PerformanceMetrics {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  benchmark_return: number;
  excess_return: number;
}

interface FinancialHealth {
  overall_score: number;
  grade: string;
  status: string;
  individual_scores: {
    portfolio_performance: number;
    risk_management: number;
    diversification: number;
    consistency: number;
    growth_trend: number;
  };
  recommendations: string[];
}

interface AssetAllocation {
  target_allocation: {
    stocks: number;
    bonds: number;
    real_estate: number;
    commodities: number;
    cash: number;
  };
  current_allocation: { [sector: string]: number };
  rebalancing_needed: boolean;
  drift_analysis: { [sector: string]: number };
}

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'risk' | 'allocation'>('overview');
  const [timeframe, setTimeframe] = useState('1M');
  const [loading, setLoading] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [financialHealth, setFinancialHealth] = useState<FinancialHealth | null>(null);
  const [assetAllocation, setAssetAllocation] = useState<AssetAllocation | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load performance metrics
      const perfResponse = await fetch(`http://localhost:8003/api/analytics/portfolio/performance?timeframe=${timeframe}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const perfData = await perfResponse.json();
      if (perfData.success) {
        setPerformanceMetrics(perfData.data.metrics);
      }

      // Load financial health
      const healthResponse = await fetch('http://localhost:8003/api/analytics/financial-health', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const healthData = await healthResponse.json();
      if (healthData.success) {
        setFinancialHealth(healthData.data);
      }

      // Load asset allocation
      const allocResponse = await fetch('http://localhost:8003/api/analytics/portfolio/asset-allocation', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const allocData = await allocResponse.json();
      if (allocData.success) {
        setAssetAllocation(allocData.data);
      }

    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getGradeColor = (grade: string) => {
    const colors = {
      'A': 'text-green-600 bg-green-100',
      'B': 'text-blue-600 bg-blue-100',
      'C': 'text-yellow-600 bg-yellow-100',
      'D': 'text-orange-600 bg-orange-100',
      'F': 'text-red-600 bg-red-100'
    };
    return colors[grade as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'Excellent': 'text-green-600',
      'Good': 'text-blue-600',
      'Fair': 'text-yellow-600',
      'Poor': 'text-orange-600',
      'Critical': 'text-red-600'
    };
    return colors[status as keyof typeof colors] || 'text-gray-600';
  };

  const timeframes = [
    { value: '1D', label: '1 Day' },
    { value: '1W', label: '1 Week' },
    { value: '1M', label: '1 Month' },
    { value: '3M', label: '3 Months' },
    { value: '6M', label: '6 Months' },
    { value: '1Y', label: '1 Year' },
    { value: 'ALL', label: 'All Time' }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Advanced Analytics</h1>
        <p className="text-gray-600">Comprehensive portfolio analysis and insights</p>
      </div>

      {/* Timeframe Selector */}
      <div className="mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Timeframe:</label>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeframes.map(tf => (
              <option key={tf.value} value={tf.value}>{tf.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: ChartBarIcon },
            { id: 'performance', name: 'Performance', icon: ArrowTrendingUpIcon },
            { id: 'risk', name: 'Risk Analysis', icon: ShieldCheckIcon },
            { id: 'allocation', name: 'Asset Allocation', icon: ChartBarIcon }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-5 w-5 inline mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {/* Financial Health Score */}
              {financialHealth && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Health Score</h3>
                  <div className="text-center">
                    <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getGradeColor(financialHealth.grade)}`}>
                      <span className="text-2xl font-bold">{financialHealth.grade}</span>
                    </div>
                    <p className={`mt-2 text-lg font-medium ${getStatusColor(financialHealth.status)}`}>
                      {financialHealth.status}
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {financialHealth.overall_score.toFixed(1)}/100
                    </p>
                  </div>
                  <div className="mt-4 space-y-2">
                    {financialHealth.recommendations.slice(0, 2).map((rec, index) => (
                      <div key={index} className="flex items-start">
                        <InformationCircleIcon className="h-4 w-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                        <p className="text-sm text-gray-600">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Performance Summary */}
              {performanceMetrics && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Return</span>
                      <span className={`text-lg font-semibold ${
                        performanceMetrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(performanceMetrics.total_return)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Annualized Return</span>
                      <span className={`text-lg font-semibold ${
                        performanceMetrics.annualized_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(performanceMetrics.annualized_return)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Volatility</span>
                      <span className="text-lg font-semibold text-gray-900">
                        {formatPercent(performanceMetrics.volatility)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Sharpe Ratio</span>
                      <span className="text-lg font-semibold text-gray-900">
                        {performanceMetrics.sharpe_ratio.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Max Drawdown</span>
                      <span className="text-lg font-semibold text-red-600">
                        {formatPercent(performanceMetrics.max_drawdown)}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Asset Allocation Summary */}
              {assetAllocation && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h3>
                  <div className="space-y-3">
                    {Object.entries(assetAllocation.current_allocation).map(([sector, percentage]) => (
                      <div key={sector} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">{sector}</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                  {assetAllocation.rebalancing_needed && (
                    <div className="mt-4 p-3 bg-yellow-50 rounded-md">
                      <p className="text-sm text-yellow-800">
                        <strong>Rebalancing Recommended:</strong> Portfolio has drifted from target allocation
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && performanceMetrics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Return Analysis</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">Total Return</span>
                      <span className={`text-lg font-semibold ${
                        performanceMetrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(performanceMetrics.total_return)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          performanceMetrics.total_return >= 0 ? 'bg-green-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${Math.min(Math.abs(performanceMetrics.total_return) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">Benchmark Return</span>
                      <span className="text-lg font-semibold text-blue-600">
                        {formatPercent(performanceMetrics.benchmark_return)}
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">Excess Return</span>
                      <span className={`text-lg font-semibold ${
                        performanceMetrics.excess_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(performanceMetrics.excess_return)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Volatility (Annual)</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {formatPercent(performanceMetrics.volatility)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Sharpe Ratio</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {performanceMetrics.sharpe_ratio.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Maximum Drawdown</span>
                    <span className="text-lg font-semibold text-red-600">
                      {formatPercent(performanceMetrics.max_drawdown)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Win Rate</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {formatPercent(performanceMetrics.win_rate)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Risk Analysis Tab */}
          {activeTab === 'risk' && financialHealth && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment</h3>
                <div className="space-y-4">
                  {Object.entries(financialHealth.individual_scores).map(([metric, score]) => (
                    <div key={metric}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-600 capitalize">
                          {metric.replace(/_/g, ' ')}
                        </span>
                        <span className="text-lg font-semibold text-gray-900">
                          {score.toFixed(1)}/100
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            score >= 80 ? 'bg-green-600' : 
                            score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                          }`}
                          style={{ width: `${score}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
                <div className="space-y-3">
                  {financialHealth.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start p-3 bg-blue-50 rounded-md">
                      <InformationCircleIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Asset Allocation Tab */}
          {activeTab === 'allocation' && assetAllocation && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Target vs Current</h3>
                <div className="space-y-4">
                  {Object.entries(assetAllocation.target_allocation).map(([asset, target]) => {
                    const current = assetAllocation.current_allocation[asset.charAt(0).toUpperCase() + asset.slice(1)] || 0;
                    const drift = current - target;
                    
                    return (
                      <div key={asset}>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600 capitalize">{asset}</span>
                          <div className="text-right">
                            <span className="text-sm font-medium text-gray-900">
                              Target: {target.toFixed(1)}%
                            </span>
                            <span className="text-sm text-gray-600 ml-2">
                              Current: {current.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full bg-blue-600"
                            style={{ width: `${target}%` }}
                          ></div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div 
                            className={`h-2 rounded-full ${
                              Math.abs(drift) > 5 ? 'bg-red-600' : 'bg-green-600'
                            }`}
                            style={{ width: `${current}%` }}
                          ></div>
                        </div>
                        {Math.abs(drift) > 5 && (
                          <p className="text-xs text-red-600 mt-1">
                            Drift: {drift > 0 ? '+' : ''}{drift.toFixed(1)}%
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Rebalancing Analysis</h3>
                {assetAllocation.rebalancing_needed ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-yellow-50 rounded-md">
                      <p className="text-sm text-yellow-800 font-medium mb-2">
                        Rebalancing Recommended
                      </p>
                      <p className="text-sm text-yellow-700">
                        Your portfolio has drifted from target allocation. Consider rebalancing to maintain optimal risk-return profile.
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Allocation Drift:</h4>
                      <div className="space-y-2">
                        {Object.entries(assetAllocation.drift_analysis).map(([sector, drift]) => (
                          <div key={sector} className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">{sector}</span>
                            <span className={`text-sm font-medium ${
                              Math.abs(drift) > 5 ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {drift > 0 ? '+' : ''}{drift.toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-green-50 rounded-md">
                    <p className="text-sm text-green-800 font-medium">
                      Portfolio is well balanced
                    </p>
                    <p className="text-sm text-green-700 mt-1">
                      No rebalancing needed at this time.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Analytics;
