import React, { useState } from 'react';
import { CalculatorIcon, ChartBarIcon, CurrencyDollarIcon, AcademicCapIcon } from '@heroicons/react/24/outline';

interface SimulationResult {
  initial_amount: number;
  monthly_investment: number;
  annual_rate: number;
  years: number;
  lumpsum_future_value: number;
  sip_future_value: number;
  total_future_value: number;
  total_investment: number;
  total_returns: number;
  return_percentage: number;
  yearly_breakdown?: Array<{
    year: number;
    lumpsum_value: number;
    sip_value: number;
    total_value: number;
    total_investment: number;
    returns: number;
    return_percentage: number;
  }>;
}

interface GoalProjectionResult {
  achievable: boolean;
  years_needed?: number;
  months_needed?: number;
  target_amount: number;
  final_amount: number;
}

interface Scenario {
  name: string;
  annual_rate: number;
  years: number;
}

const Simulations: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'basic' | 'whatif' | 'goals'>('basic');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | GoalProjectionResult | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioResults, setScenarioResults] = useState<any>(null);

  // Basic simulation form
  const [formData, setFormData] = useState({
    initial_amount: 10000,
    monthly_investment: 500,
    annual_rate: 0.08,
    years: 10
  });

  // Goal projection form
  const [goalData, setGoalData] = useState({
    target_amount: 1000000,
    current_amount: 10000,
    monthly_contribution: 1000,
    annual_rate: 0.08
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (rate: number) => {
    return `${(rate * 100).toFixed(2)}%`;
  };

  const runBasicSimulation = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/simulate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      }
    } catch (error) {
      console.error('Error running simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const runWhatIfSimulation = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/simulate/what-if', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          initial_amount: formData.initial_amount,
          monthly_investment: formData.monthly_investment,
          scenarios: scenarios
        })
      });
      const data = await response.json();
      if (data.success) {
        setScenarioResults(data.data);
      }
    } catch (error) {
      console.error('Error running what-if simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const runGoalProjection = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/simulate/goal-projection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(goalData)
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      }
    } catch (error) {
      console.error('Error running goal projection:', error);
    } finally {
      setLoading(false);
    }
  };

  const addScenario = () => {
    setScenarios([...scenarios, {
      name: `Scenario ${scenarios.length + 1}`,
      annual_rate: 0.08,
      years: 10
    }]);
  };

  const updateScenario = (index: number, field: keyof Scenario, value: string | number) => {
    const updated = [...scenarios];
    if (field === 'annual_rate') {
      updated[index][field] = parseFloat(value as string) / 100;
    } else if (field === 'years') {
      updated[index][field] = parseInt(value as string);
    } else {
      updated[index][field] = value as string;
    }
    setScenarios(updated);
  };

  const removeScenario = (index: number) => {
    setScenarios(scenarios.filter((_, i) => i !== index));
  };

  const isGoalProjectionResult = (obj: any): obj is GoalProjectionResult => {
    return obj && typeof obj === 'object' && 'achievable' in obj;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Investment Simulations</h1>
        <p className="text-gray-600">Plan your financial future with investment calculators</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'basic', name: 'Basic Calculator', icon: CalculatorIcon },
            { id: 'whatif', name: 'What-If Scenarios', icon: ChartBarIcon },
            { id: 'goals', name: 'Goal Projection', icon: CurrencyDollarIcon }
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

      {/* Basic Calculator Tab */}
      {activeTab === 'basic' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Investment Parameters</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Initial Amount
                </label>
                <input
                  type="number"
                  value={formData.initial_amount}
                  onChange={(e) => setFormData({...formData, initial_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Investment
                </label>
                <input
                  type="number"
                  value={formData.monthly_investment}
                  onChange={(e) => setFormData({...formData, monthly_investment: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Annual Return (%)
                </label>
                <input
                  type="number"
                  value={(formData.annual_rate * 100).toFixed(2)}
                  onChange={(e) => setFormData({...formData, annual_rate: parseFloat(e.target.value) / 100 || 0})}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Investment Period (Years)
                </label>
                <input
                  type="number"
                  value={formData.years}
                  onChange={(e) => setFormData({...formData, years: parseInt(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={runBasicSimulation}
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Returns'}
              </button>
            </div>
          </div>

          {result && !isGoalProjectionResult(result) && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Results</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Total Investment</p>
                    <p className="text-xl font-semibold text-gray-900">{formatCurrency(result.total_investment)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Future Value</p>
                    <p className="text-xl font-semibold text-green-600">{formatCurrency(result.total_future_value)}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Total Returns</p>
                    <p className="text-xl font-semibold text-blue-600">{formatCurrency(result.total_returns)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Return Percentage</p>
                    <p className="text-xl font-semibold text-purple-600">{formatPercent(result.return_percentage / 100)}</p>
                  </div>
                </div>
                <div className="border-t pt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Lumpsum Value</p>
                      <p className="font-semibold">{formatCurrency(result.lumpsum_future_value)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">SIP Value</p>
                      <p className="font-semibold">{formatCurrency(result.sip_future_value)}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* What-If Scenarios Tab */}
      {activeTab === 'whatif' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Scenarios</h2>
              <button
                onClick={addScenario}
                className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                Add Scenario
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {scenarios.map((scenario, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <input
                      type="text"
                      value={scenario.name}
                      onChange={(e) => updateScenario(index, 'name', e.target.value)}
                      className="font-medium text-gray-900 bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none"
                    />
                    <button
                      onClick={() => removeScenario(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-gray-600">Annual Return (%)</label>
                      <input
                        type="number"
                        value={(scenario.annual_rate * 100).toFixed(1)}
                        onChange={(e) => updateScenario(index, 'annual_rate', e.target.value)}
                        step="0.1"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">Years</label>
                      <input
                        type="number"
                        value={scenario.years}
                        onChange={(e) => updateScenario(index, 'years', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Initial Amount</label>
                <input
                  type="number"
                  value={formData.initial_amount}
                  onChange={(e) => setFormData({...formData, initial_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Investment</label>
                <input
                  type="number"
                  value={formData.monthly_investment}
                  onChange={(e) => setFormData({...formData, monthly_investment: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>

            <button
              onClick={runWhatIfSimulation}
              disabled={loading || scenarios.length === 0}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Compare Scenarios'}
            </button>
          </div>

          {scenarioResults && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Scenario Comparison</h2>
              <div className="space-y-4">
                {scenarioResults.scenarios.map((scenario: any, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{scenario.scenario_name}</h3>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-green-600">{formatCurrency(scenario.total_future_value)}</p>
                        <p className="text-sm text-gray-600">{formatPercent(scenario.return_percentage / 100)}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Return Rate</p>
                        <p className="font-medium">{formatPercent(scenario.annual_rate)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Period</p>
                        <p className="font-medium">{scenario.years} years</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Total Returns</p>
                        <p className="font-medium">{formatCurrency(scenario.total_returns)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Goal Projection Tab */}
      {activeTab === 'goals' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Goal Parameters</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Amount
                </label>
                <input
                  type="number"
                  value={goalData.target_amount}
                  onChange={(e) => setGoalData({...goalData, target_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Amount
                </label>
                <input
                  type="number"
                  value={goalData.current_amount}
                  onChange={(e) => setGoalData({...goalData, current_amount: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Contribution
                </label>
                <input
                  type="number"
                  value={goalData.monthly_contribution}
                  onChange={(e) => setGoalData({...goalData, monthly_contribution: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Annual Return (%)
                </label>
                <input
                  type="number"
                  value={(goalData.annual_rate * 100).toFixed(2)}
                  onChange={(e) => setGoalData({...goalData, annual_rate: parseFloat(e.target.value) / 100 || 0})}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={runGoalProjection}
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Project Timeline'}
              </button>
            </div>
          </div>

          {result && isGoalProjectionResult(result) && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Goal Projection</h2>
              <div className="space-y-4">
                {result.achievable ? (
                  <div className="text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                      <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-green-600 mb-2">Goal Achievable! 🎉</h3>
                    <p className="text-gray-600 mb-4">You can reach your target in:</p>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-2xl font-bold text-green-700">{result.years_needed} years</p>
                      <p className="text-sm text-green-600">{result.months_needed} months</p>
                    </div>
                    <div className="mt-4 grid grid-cols-2 gap-4 text-left">
                      <div>
                        <p className="text-sm text-gray-600">Target Amount</p>
                        <p className="font-semibold">{formatCurrency(result.target_amount)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Final Amount</p>
                        <p className="font-semibold">{formatCurrency(result.final_amount)}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                      <AcademicCapIcon className="h-8 w-8 text-red-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-red-600 mb-2">Goal Not Achievable</h3>
                    <p className="text-gray-600 mb-4">With current parameters, you won't reach this goal.</p>
                    <div className="bg-red-50 rounded-lg p-4">
                      <p className="text-sm text-red-600">Consider increasing contributions or extending time period</p>
                    </div>
                    <div className="mt-4">
                      <p className="text-sm text-gray-600">Maximum achievable in 50 years:</p>
                      <p className="font-semibold text-red-600">{formatCurrency(result.final_amount)}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Simulations;
