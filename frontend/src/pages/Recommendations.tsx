import React, { useState, useEffect } from 'react';
import { 
  LightBulbIcon, 
  ChartBarIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

interface Recommendation {
  id: number;
  type: string;
  title: string;
  description: string;
  reasoning?: string;
  suggested_symbols?: string[];
  expected_return?: number;
  risk_level?: string;
  confidence?: number;
  priority?: string;
  status?: string;
  goal_id?: number;
  goal_name?: string;
  opportunities?: Array<{
    symbol: string;
    loss: number;
    loss_percentage: number;
  }>;
  potential_tax_savings?: number;
  recommended_actions?: string[];
  trades?: Array<{
    action: string;
    category: string;
    amount: number;
    suggested_symbols: string[];
  }>;
}

const Recommendations: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'all' | 'portfolio' | 'rebalancing' | 'tax' | 'goals'>('all');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<{
    portfolio: Recommendation[];
    rebalancing: Recommendation | null;
    tax_optimization: Recommendation[];
    goal_based: Recommendation[];
  }>({
    portfolio: [],
    rebalancing: null,
    tax_optimization: [],
    goal_based: []
  });
  const [expandedRec, setExpandedRec] = useState<number | null>(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8003/api/recommendations/portfolio', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      if (data.success && data.data && data.data.recommendations) {
        const rawRecommendations = data.data.recommendations;
        
        // Categorize recommendations by type
        const categorized = {
          portfolio: rawRecommendations.filter((r: any) => 
            ['diversification', 'risk_adjustment', 'performance_optimization'].includes(r.type)
          ),
          rebalancing: rawRecommendations.find((r: any) => r.type === 'rebalancing') || null,
          tax_optimization: rawRecommendations.filter((r: any) => r.type === 'tax_optimization'),
          goal_based: rawRecommendations.filter((r: any) => r.type === 'goal_based')
        };
        
        setRecommendations(categorized);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateRecommendationStatus = async (recommendationId: number, status: string) => {
    try {
      const response = await fetch(`http://localhost:8003/api/recommendations/${recommendationId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        loadRecommendations(); // Reload recommendations
      }
    } catch (error) {
      console.error('Error updating recommendation status:', error);
    }
  };

  const generateFreshRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8003/api/recommendations/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadRecommendations();
      }
    } catch (error) {
      console.error('Error generating fresh recommendations:', error);
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

  const getPriorityColor = (priority?: string) => {
    const colors = {
      'high': 'text-red-600 bg-red-100',
      'medium': 'text-yellow-600 bg-yellow-100',
      'low': 'text-green-600 bg-green-100'
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  const getRiskColor = (risk?: string) => {
    const colors = {
      'low': 'text-green-600',
      'medium': 'text-yellow-600',
      'high': 'text-red-600'
    };
    return colors[risk as keyof typeof colors] || 'text-gray-600';
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-600';
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      'portfolio': ChartBarIcon,
      'diversification': ArrowTrendingUpIcon,
      'risk_adjustment': ExclamationTriangleIcon,
      'performance_optimization': ArrowTrendingUpIcon,
      'rebalancing': SparklesIcon,
      'tax_optimization': LightBulbIcon,
      'asset_location': LightBulbIcon,
      'goal_optimization': CheckCircleIcon
    };
    return icons[type as keyof typeof icons] || LightBulbIcon;
  };

  const renderRecommendationCard = (rec: Recommendation) => {
    const Icon = getTypeIcon(rec.type);
    const isExpanded = expandedRec === rec.id;
    
    return (
      <div key={rec.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Icon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">{rec.title}</h3>
              <p className="text-gray-600 mt-1">{rec.description}</p>
              
              <div className="flex flex-wrap items-center gap-4 mt-3">
                {rec.priority && (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                    {rec.priority} priority
                  </span>
                )}
                {rec.risk_level && (
                  <span className={`text-sm font-medium ${getRiskColor(rec.risk_level)}`}>
                    {rec.risk_level} risk
                  </span>
                )}
                {rec.confidence && (
                  <span className={`text-sm font-medium ${getConfidenceColor(rec.confidence)}`}>
                    {formatPercent(rec.confidence)} confidence
                  </span>
                )}
                {rec.expected_return && (
                  <span className="text-sm font-medium text-green-600">
                    +{formatPercent(rec.expected_return)} expected return
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setExpandedRec(isExpanded ? null : rec.id)}
              className="text-gray-400 hover:text-gray-600"
            >
              <InformationCircleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            {rec.reasoning && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Reasoning:</h4>
                <p className="text-sm text-gray-600">{rec.reasoning}</p>
              </div>
            )}

            {rec.suggested_symbols && rec.suggested_symbols.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Suggested Symbols:</h4>
                <div className="flex flex-wrap gap-2">
                  {rec.suggested_symbols.map((symbol, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-blue-100 text-blue-800">
                      {symbol}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {rec.opportunities && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Tax Loss Harvesting Opportunities:</h4>
                <div className="space-y-2">
                  {rec.opportunities.map((opp, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-red-50 rounded">
                      <span className="text-sm font-medium text-red-800">{opp.symbol}</span>
                      <div className="text-right">
                        <span className="text-sm text-red-600">
                          Loss: {formatCurrency(opp.loss)} ({opp.loss_percentage.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                {rec.potential_tax_savings && (
                  <p className="text-sm text-green-600 mt-2">
                    Potential tax savings: {formatCurrency(rec.potential_tax_savings)}
                  </p>
                )}
              </div>
            )}

            {rec.trades && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Recommended Trades:</h4>
                <div className="space-y-2">
                  {rec.trades.map((trade, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <div>
                        <span className={`text-sm font-medium ${
                          trade.action === 'buy' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {trade.action.toUpperCase()} {formatCurrency(trade.amount)}
                        </span>
                        <span className="text-sm text-gray-600 ml-2">
                          {trade.category}
                        </span>
                      </div>
                      <div className="flex gap-1">
                        {trade.suggested_symbols.slice(0, 3).map((symbol, idx) => (
                          <span key={idx} className="text-xs bg-gray-200 px-2 py-1 rounded">
                            {symbol}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {rec.recommended_actions && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Recommended Actions:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {rec.recommended_actions.map((action, index) => (
                    <li key={index} className="text-sm text-gray-600">{action}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3 mt-4">
              <button
                onClick={() => updateRecommendationStatus(rec.id, 'accepted')}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Accept
              </button>
              <button
                onClick={() => updateRecommendationStatus(rec.id, 'rejected')}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <XCircleIcon className="h-4 w-4 mr-1" />
                Reject
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  const getAllRecommendations = () => {
    const allRecs = [
      ...recommendations.portfolio,
      ...(recommendations.rebalancing ? [recommendations.rebalancing] : []),
      ...recommendations.tax_optimization,
      ...recommendations.goal_based
    ];
    
    // Sort by priority
    const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
    return allRecs.sort((a, b) => 
      (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
      (priorityOrder[a.priority as keyof typeof priorityOrder] || 0)
    );
  };

  const getTabRecommendations = () => {
    switch (activeTab) {
      case 'portfolio':
        return recommendations.portfolio;
      case 'rebalancing':
        return recommendations.rebalancing ? [recommendations.rebalancing] : [];
      case 'tax':
        return recommendations.tax_optimization;
      case 'goals':
        return recommendations.goal_based;
      default:
        return getAllRecommendations();
    }
  };

  const totalRecommendations = getAllRecommendations().length;

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">AI Recommendations</h1>
            <p className="text-gray-600">Personalized investment suggestions based on your portfolio</p>
          </div>
          <button
            onClick={generateFreshRecommendations}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <SparklesIcon className="h-4 w-4 mr-2" />
            {loading ? 'Generating...' : 'Generate Fresh'}
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <LightBulbIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Recommendations</p>
              <p className="text-2xl font-bold text-gray-900">{totalRecommendations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-gray-900">
                {getAllRecommendations().filter(r => r.priority === 'high').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Avg. Expected Return</p>
              <p className="text-2xl font-bold text-gray-900">
                {getAllRecommendations().length > 0 
                  ? formatPercent(getAllRecommendations().reduce((sum, r) => sum + (r.expected_return || 0), 0) / getAllRecommendations().length)
                  : '0%'
                }
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Implemented</p>
              <p className="text-2xl font-bold text-gray-900">
                {getAllRecommendations().filter(r => r.status === 'implemented').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'all', name: 'All Recommendations', count: totalRecommendations },
            { id: 'portfolio', name: 'Portfolio', count: recommendations.portfolio.length },
            { id: 'rebalancing', name: 'Rebalancing', count: recommendations.rebalancing ? 1 : 0 },
            { id: 'tax', name: 'Tax Optimization', count: recommendations.tax_optimization.length },
            { id: 'goals', name: 'Goals', count: recommendations.goal_based.length }
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
              {tab.name}
              {tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Recommendations List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {getTabRecommendations().length > 0 ? (
            getTabRecommendations().map(renderRecommendationCard)
          ) : (
            <div className="text-center py-12">
              <LightBulbIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations available</h3>
              <p className="mt-1 text-sm text-gray-500">
                Generate fresh recommendations to get personalized investment suggestions.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
