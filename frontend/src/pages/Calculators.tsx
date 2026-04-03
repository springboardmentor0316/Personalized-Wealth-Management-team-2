import React, { useState } from 'react';
import { CalculatorIcon, ChartBarIcon, CurrencyDollarIcon, HomeIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';

interface SIPResult {
  monthly_investment: number;
  expected_return: number;
  time_period_years: number;
  total_investment: number;
  wealth_gained: number;
  future_value: number;
  monthly_rate: number;
  total_months: number;
}

interface RetirementResult {
  current_age: number;
  retirement_age: number;
  years_to_retirement: number;
  current_savings: number;
  monthly_contribution: number;
  expected_return: number;
  inflation_rate: number;
  retirement_corpus: number;
  monthly_income: number;
  monthly_income_today: number;
  total_contributions: number;
  wealth_gained: number;
}

interface LoanPayoffResult {
  principal: number;
  interest_rate: number;
  loan_term_years: number;
  extra_payment: number;
  monthly_payment: number;
  effective_monthly_payment: number;
  total_months: number;
  total_amount: number;
  total_interest: number;
  months_to_payoff: number;
  months_saved: number;
  years_saved: number;
  total_amount_extra: number | null;
  total_interest_extra: number | null;
  interest_saved: number | null;
}

const Calculators: React.FC = () => {
  const [activeTab, setActiveTab] = useState('sip');

  // SIP Calculator State
  const [sipData, setSIPData] = useState({
    monthly_investment: 5000,
    expected_return: 12,
    time_period_years: 10
  });
  const [sipResult, setSIPResult] = useState<SIPResult | null>(null);

  // Retirement Calculator State
  const [retirementData, setRetirementData] = useState({
    current_age: 30,
    retirement_age: 60,
    current_savings: 100000,
    monthly_contribution: 10000,
    expected_return: 10,
    inflation_rate: 6
  });
  const [retirementResult, setRetirementResult] = useState<RetirementResult | null>(null);

  // Loan Payoff Calculator State
  const [loanData, setLoanData] = useState({
    principal: 500000,
    interest_rate: 8,
    loan_term_years: 20,
    extra_payment: 0
  });
  const [loanResult, setLoanResult] = useState<LoanPayoffResult | null>(null);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const calculateSIP = async () => {
    try {
      const response = await fetch(`http://localhost:8003/api/calculators/sip`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          monthly_investment: sipData.monthly_investment,
          expected_return: sipData.expected_return,
          time_period_years: sipData.time_period_years
        })
      });
      const data = await response.json();
      if (data.success) {
        setSIPResult(data.data);
      } else {
        console.error('SIP calculation failed:', data);
      }
    } catch (error) {
      console.error('Error calculating SIP:', error);
    }
  };

  const calculateRetirement = async () => {
    try {
      const response = await fetch(`http://localhost:8003/api/calculators/retirement`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_age: retirementData.current_age,
          retirement_age: retirementData.retirement_age,
          current_savings: retirementData.current_savings,
          monthly_contribution: retirementData.monthly_contribution,
          expected_return: retirementData.expected_return,
          inflation_rate: retirementData.inflation_rate
        })
      });
      const data = await response.json();
      if (data.success) {
        setRetirementResult(data.data);
      } else {
        console.error('Retirement calculation failed:', data);
      }
    } catch (error) {
      console.error('Error calculating retirement:', error);
    }
  };

  const calculateLoanPayoff = async () => {
    try {
      const response = await fetch(`http://localhost:8003/api/calculators/loan-payoff`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          principal: loanData.principal,
          interest_rate: loanData.interest_rate,
          loan_term_years: loanData.loan_term_years,
          extra_payment: loanData.extra_payment || 0
        })
      });
      const data = await response.json();
      if (data.success) {
        setLoanResult(data.data);
      } else {
        console.error('Loan payoff calculation failed:', data);
      }
    } catch (error) {
      console.error('Error calculating loan payoff:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <CalculatorIcon className="h-8 w-8 mr-3 text-blue-600" />
            Financial Calculators
          </h1>
          <p className="mt-2 text-gray-600">
            Plan your finances with our powerful calculators
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'sip', name: 'SIP Calculator', icon: ArrowTrendingUpIcon },
              { id: 'retirement', name: 'Retirement Planner', icon: HomeIcon },
              { id: 'loan', name: 'Loan Payoff', icon: CurrencyDollarIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* SIP Calculator */}
        {activeTab === 'sip' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <ArrowTrendingUpIcon className="h-6 w-6 mr-2 text-blue-600" />
                SIP Calculator
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Investment (₹)
                  </label>
                  <input
                    type="number"
                    value={sipData.monthly_investment}
                    onChange={(e) => setSIPData({ ...sipData, monthly_investment: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Expected Return (%)
                  </label>
                  <input
                    type="number"
                    value={sipData.expected_return}
                    onChange={(e) => setSIPData({ ...sipData, expected_return: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time Period (Years)
                  </label>
                  <input
                    type="number"
                    value={sipData.time_period_years}
                    onChange={(e) => setSIPData({ ...sipData, time_period_years: parseInt(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  onClick={calculateSIP}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Calculate
                </button>
              </div>
            </div>

            {sipResult && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">SIP Results</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Future Value</p>
                    <p className="text-2xl font-bold text-blue-600">{formatCurrency(sipResult.future_value)}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Total Investment</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(sipResult.total_investment)}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Wealth Gained</p>
                      <p className="text-lg font-semibold text-green-600">{formatCurrency(sipResult.wealth_gained)}</p>
                    </div>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Investment Period</p>
                    <p className="text-lg font-semibold text-gray-900">{sipResult.total_months} months ({sipResult.time_period_years} years)</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Retirement Calculator */}
        {activeTab === 'retirement' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <HomeIcon className="h-6 w-6 mr-2 text-blue-600" />
                Retirement Planner
              </h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Current Age
                    </label>
                    <input
                      type="number"
                      value={retirementData.current_age}
                      onChange={(e) => setRetirementData({ ...retirementData, current_age: parseInt(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Retirement Age
                    </label>
                    <input
                      type="number"
                      value={retirementData.retirement_age}
                      onChange={(e) => setRetirementData({ ...retirementData, retirement_age: parseInt(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Savings (₹)
                  </label>
                  <input
                    type="number"
                    value={retirementData.current_savings}
                    onChange={(e) => setRetirementData({ ...retirementData, current_savings: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Contribution (₹)
                  </label>
                  <input
                    type="number"
                    value={retirementData.monthly_contribution}
                    onChange={(e) => setRetirementData({ ...retirementData, monthly_contribution: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Expected Return (%)
                    </label>
                    <input
                      type="number"
                      value={retirementData.expected_return}
                      onChange={(e) => setRetirementData({ ...retirementData, expected_return: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Inflation Rate (%)
                    </label>
                    <input
                      type="number"
                      value={retirementData.inflation_rate}
                      onChange={(e) => setRetirementData({ ...retirementData, inflation_rate: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <button
                  onClick={calculateRetirement}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Calculate
                </button>
              </div>
            </div>

            {retirementResult && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Retirement Results</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Retirement Corpus</p>
                    <p className="text-2xl font-bold text-blue-600">{formatCurrency(retirementResult.retirement_corpus)}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Monthly Income</p>
                      <p className="text-lg font-semibold text-green-600">{formatCurrency(retirementResult.monthly_income)}</p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Income Today's Value</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(retirementResult.monthly_income_today)}</p>
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Years to Retirement</p>
                    <p className="text-lg font-semibold text-purple-600">{retirementResult.years_to_retirement} years</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Total Contributions</p>
                    <p className="text-lg font-semibold text-gray-900">{formatCurrency(retirementResult.total_contributions)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Loan Payoff Calculator */}
        {activeTab === 'loan' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <CurrencyDollarIcon className="h-6 w-6 mr-2 text-blue-600" />
                Loan Payoff Calculator
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Principal (₹)
                  </label>
                  <input
                    type="number"
                    value={loanData.principal}
                    onChange={(e) => setLoanData({ ...loanData, principal: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interest Rate (%)
                  </label>
                  <input
                    type="number"
                    value={loanData.interest_rate}
                    onChange={(e) => setLoanData({ ...loanData, interest_rate: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Term (Years)
                  </label>
                  <input
                    type="number"
                    value={loanData.loan_term_years}
                    onChange={(e) => setLoanData({ ...loanData, loan_term_years: parseInt(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Extra Monthly Payment (₹)
                  </label>
                  <input
                    type="number"
                    value={loanData.extra_payment}
                    onChange={(e) => setLoanData({ ...loanData, extra_payment: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Optional - Pay off faster"
                  />
                </div>
                <button
                  onClick={calculateLoanPayoff}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Calculate
                </button>
              </div>
            </div>

            {loanResult && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Loan Payoff Results</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Monthly Payment</p>
                    <p className="text-2xl font-bold text-blue-600">{formatCurrency(loanResult.monthly_payment)}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Total Amount</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(loanResult.total_amount)}</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Total Interest</p>
                      <p className="text-lg font-semibold text-red-600">{formatCurrency(loanResult.total_interest)}</p>
                    </div>
                  </div>
                  {loanResult.extra_payment > 0 && loanResult.interest_saved && loanResult.interest_saved > 0 && (
                    <>
                      <div className="bg-green-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600">Interest Saved</p>
                        <p className="text-lg font-semibold text-green-600">{formatCurrency(loanResult.interest_saved || 0)}</p>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600">Time Saved</p>
                        <p className="text-lg font-semibold text-gray-900">{loanResult.years_saved.toFixed(1)} years ({loanResult.months_saved} months)</p>
                      </div>
                    </>
                  )}
                  <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Loan Term</p>
                    <p className="text-lg font-semibold text-purple-600">{loanResult.total_months} months ({loanResult.loan_term_years} years)</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Calculators;
