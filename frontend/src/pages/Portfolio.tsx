import React, { useState, useEffect } from 'react';
import { portfolioAPI, investmentsAPI } from '../services/api';
import { Portfolio, InvestmentCreate, InvestmentType } from '../types';
import {
  PlusIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

const PortfolioPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<InvestmentCreate>({
    symbol: '',
    name: '',
    type: InvestmentType.STOCK,
    quantity: 0,
    average_cost: 0,
    current_price: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const portfolioData = await portfolioAPI.getPortfolio();
      setPortfolio(portfolioData);
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    // Validate form data
    if (!formData.symbol.trim()) {
      setError('Symbol is required');
      return;
    }
    if (!formData.name.trim()) {
      setError('Name is required');
      return;
    }
    if (formData.quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }
    if (formData.average_cost <= 0) {
      setError('Average cost must be greater than 0');
      return;
    }
    if (formData.current_price <= 0) {
      setError('Current price must be greater than 0');
      return;
    }
    
    setSubmitting(true);
    try {
      await investmentsAPI.createInvestment(formData);
      setSuccess('Investment added successfully!');
      setShowModal(false);
      setFormData({
        symbol: '',
        name: '',
        type: InvestmentType.STOCK,
        quantity: 0,
        average_cost: 0,
        current_price: 0,
      });
      fetchData();
    } catch (error: any) {
      console.error('Error creating investment:', error);
      let errorMessage = 'Failed to add investment. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      } else if (error.message) {
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const getTypeColor = (type: InvestmentType) => {
    const colors = {
      [InvestmentType.STOCK]: 'bg-blue-100 text-blue-800',
      [InvestmentType.ETF]: 'bg-green-100 text-green-800',
      [InvestmentType.MUTUAL_FUND]: 'bg-purple-100 text-purple-800',
      [InvestmentType.BOND]: 'bg-yellow-100 text-yellow-800',
      [InvestmentType.CRYPTO]: 'bg-red-100 text-red-800',
    };
    return colors[type] || colors[InvestmentType.STOCK];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Investment Portfolio</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Investment
        </button>
      </div>

      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${portfolio.summary.total_value.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-gray-100 rounded-full">
                <ChartBarIcon className="h-6 w-6 text-gray-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Cost</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${portfolio.summary.total_cost.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-full ${
                portfolio.summary.total_gain_loss >= 0 ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {portfolio.summary.total_gain_loss >= 0 ? (
                  <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
                ) : (
                  <ArrowTrendingDownIcon className="h-6 w-6 text-red-600" />
                )}
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Gain/Loss</p>
                <p className={`text-2xl font-bold ${
                  portfolio.summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  ${portfolio.summary.total_gain_loss.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-full ${
                portfolio.summary.total_gain_loss_percent >= 0 ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {portfolio.summary.total_gain_loss_percent >= 0 ? (
                  <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
                ) : (
                  <ArrowTrendingDownIcon className="h-6 w-6 text-red-600" />
                )}
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Return %</p>
                <p className={`text-2xl font-bold ${
                  portfolio.summary.total_gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {portfolio.summary.total_gain_loss_percent.toFixed(2)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Investment Holdings</h2>
        </div>
        
        {portfolio?.investments.length === 0 ? (
          <div className="p-12 text-center">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No investments yet</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by adding your first investment.</p>
            <div className="mt-6">
              <button
                onClick={() => setShowModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Investment
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gain/Loss
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gain/Loss %
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {portfolio?.investments.map((investment) => (
                  <tr key={investment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {investment.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {investment.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(investment.type)}`}>
                        {investment.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {investment.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${investment.average_cost.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${investment.current_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${investment.current_value.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-medium ${
                        investment.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {investment.gain_loss >= 0 ? '+' : ''}${investment.gain_loss.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-medium ${
                        investment.gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {investment.gain_loss_percent >= 0 ? '+' : ''}{investment.gain_loss_percent.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add New Investment</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}
              
              {/* Success Message */}
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md text-sm">
                  {success}
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Symbol</label>
                  <input
                    type="text"
                    required
                    value={formData.symbol}
                    onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as InvestmentType })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={InvestmentType.STOCK}>Stock</option>
                    <option value={InvestmentType.ETF}>ETF</option>
                    <option value={InvestmentType.MUTUAL_FUND}>Mutual Fund</option>
                    <option value={InvestmentType.BOND}>Bond</option>
                    <option value={InvestmentType.CRYPTO}>Crypto</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Quantity</label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="0.001"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Average Cost</label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="0.01"
                    value={formData.average_cost}
                    onChange={(e) => setFormData({ ...formData, average_cost: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Current Price</label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={formData.current_price}
                  onChange={(e) => setFormData({ ...formData, current_price: parseFloat(e.target.value) })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setError(null);
                    setSuccess(null);
                  }}
                  disabled={submitting}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Adding...
                    </>
                  ) : (
                    'Add Investment'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioPage;
