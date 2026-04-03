import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  InformationCircleIcon,
  CogIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface ChartData {
  type: string;
  data: any;
  metadata?: any;
}

const Charts: React.FC = () => {
  const [activeChart, setActiveChart] = useState<'portfolio' | 'allocation' | 'risk-return' | 'correlation' | 'stock'>('portfolio');
  const [timeframe, setTimeframe] = useState('1M');
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [stockSymbol, setStockSymbol] = useState('AAPL');
  const [benchmarkSymbols, setBenchmarkSymbols] = useState('SPY,QQQ');

  useEffect(() => {
    loadChartData();
  }, [activeChart, timeframe, stockSymbol, benchmarkSymbols]);

  const loadChartData = async () => {
    setLoading(true);
    try {
      let url = '';
      
      switch (activeChart) {
        case 'portfolio':
          url = `http://localhost:8003/api/charts/portfolio/performance?timeframe=${timeframe}`;
          break;
        case 'allocation':
          url = 'http://localhost:8003/api/charts/asset-allocation';
          break;
        case 'risk-return':
          url = 'http://localhost:8003/api/charts/risk-return-scatter';
          break;
        case 'correlation':
          url = 'http://localhost:8003/api/charts/correlation-heatmap';
          break;
        case 'stock':
          url = `http://localhost:8003/api/charts/stock/${stockSymbol}?timeframe=${timeframe}`;
          break;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setChartData(data.data);
      }
    } catch (error) {
      console.error('Error loading chart data:', error);
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

  const timeframes = [
    { value: '1D', label: '1 Day' },
    { value: '1W', label: '1 Week' },
    { value: '1M', label: '1 Month' },
    { value: '3M', label: '3 Months' },
    { value: '6M', label: '6 Months' },
    { value: '1Y', label: '1 Year' },
    { value: 'ALL', label: 'All Time' }
  ];

  const renderPortfolioChart = () => {
    if (!chartData || !chartData.data || !chartData.data.values) {
      return (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No portfolio data available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add investments to your portfolio to see performance charts.
          </p>
        </div>
      );
    }
    
    const { dates, values, moving_averages, daily_returns, metadata } = chartData.data;
    
    return (
      <div className="space-y-6">
        {/* Performance Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Performance</h3>
          
          {/* Simple Line Chart Visualization */}
          <div className="h-64 flex items-end space-x-1">
            {values.slice(-30).map((value: number, index: number) => {
              const maxValue = Math.max(...values.slice(-30));
              const heightPercent = (value / maxValue) * 100;
              const isPositive = index === 0 || value >= values.slice(-30)[index - 1];
              
              return (
                <div
                  key={index}
                  className={`flex-1 ${isPositive ? 'bg-green-500' : 'bg-red-500'} rounded-t`}
                  style={{ height: `${heightPercent}%` }}
                  title={`Value: ${formatCurrency(value)}`}
                />
              );
            })}
          </div>
          
          {/* Performance Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div>
              <p className="text-sm text-gray-600">Start Value</p>
              <p className="text-lg font-semibold text-gray-900">{formatCurrency(metadata.start_value)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">End Value</p>
              <p className="text-lg font-semibold text-gray-900">{formatCurrency(metadata.end_value)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Return</p>
              <p className={`text-lg font-semibold ${metadata.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercent(metadata.total_return)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Volatility</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(metadata.volatility)}</p>
            </div>
          </div>
        </div>

        {/* Daily Returns */}
        {daily_returns && daily_returns.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Returns</h3>
            
            <div className="h-32 flex items-center space-x-1">
              {daily_returns.slice(-30).map((ret: number, index: number) => {
                const heightPercent = Math.min(Math.abs(ret) * 1000, 100);
                
                return (
                  <div
                    key={index}
                    className={`flex-1 ${ret >= 0 ? 'bg-green-500' : 'bg-red-500'} rounded`}
                    style={{ height: `${heightPercent}%` }}
                    title={`Return: ${formatPercent(ret)}`}
                  />
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAllocationChart = () => {
    if (!chartData || !chartData.data || !chartData.data.labels) {
      return (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No allocation data available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add investments to your portfolio to see asset allocation.
          </p>
        </div>
      );
    }
    
    const { labels, values, colors, percentages, metadata } = chartData.data;
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h3>
        
        {/* Simple Pie Chart Visualization */}
        <div className="flex items-center justify-center">
          <div className="relative w-64 h-64">
            <div className="absolute inset-0 rounded-full overflow-hidden">
              {values.map((value: number, index: number) => {
                const percentage = value;
                const rotation = values.slice(0, index).reduce((sum: number, val: number) => sum + val, 0) * 3.6;
                
                return (
                  <div
                    key={index}
                    className={`absolute inset-0 origin-center`}
                    style={{
                      transform: `rotate(${rotation}deg)`,
                      clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * Math.sin((percentage * 3.6 * Math.PI) / 180)}% ${50 - 50 * Math.cos((percentage * 3.6 * Math.PI) / 180)}%)`
                    }}
                  >
                    <div 
                      className="w-full h-full"
                      style={{ backgroundColor: colors[index] || '#6B7280' }}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="grid grid-cols-2 gap-4 mt-6">
          {labels.map((label: string, index: number) => (
            <div key={index} className="flex items-center space-x-2">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: colors[index] || '#6B7280' }}
              />
              <span className="text-sm text-gray-700">{label}</span>
              <span className="text-sm font-medium text-gray-900">{percentages[index].toFixed(1)}%</span>
            </div>
          ))}
        </div>
        
        {/* Metadata */}
        {metadata && (
          <div className="mt-6 p-4 bg-gray-50 rounded-md">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Total Value: </span>
                <span className="font-medium text-gray-900">{formatCurrency(metadata.total_value)}</span>
              </div>
              <div>
                <span className="text-gray-600">Sectors: </span>
                <span className="font-medium text-gray-900">{metadata.number_of_sectors}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRiskReturnChart = () => {
    if (!chartData || !chartData.data || !chartData.data.portfolio) {
      return (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No risk-return data available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add investments to your portfolio to see risk analysis.
          </p>
        </div>
      );
    }
    
    const { portfolio, benchmarks, metadata } = chartData.data;
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk vs Return Analysis</h3>
        
        {/* Simple Scatter Plot */}
        <div className="h-64 relative bg-gray-50 rounded p-4">
          {/* Grid lines */}
          <div className="absolute inset-4 grid grid-cols-5 grid-rows-5 gap-0">
            {[...Array(25)].map((_, i) => (
              <div key={i} className="border border-gray-200" />
            ))}
          </div>
          
          {/* Portfolio points */}
          {portfolio.map((point: any, index: number) => (
            <div
              key={index}
              className="absolute w-3 h-3 bg-blue-600 rounded-full transform -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${25 + (point.return + 20) * 2.5}%`,
                top: `${75 - point.risk * 2.5}%`
              }}
              title={`${point.period}: ${formatPercent(point.return)} return, ${formatPercent(point.risk)} risk`}
            />
          ))}
          
          {/* Benchmark points */}
          {benchmarks.map((point: any, index: number) => (
            <div
              key={`bench-${index}`}
              className="absolute w-3 h-3 bg-red-600 rounded-full transform -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${25 + (point.return + 20) * 2.5}%`,
                top: `${75 - point.risk * 2.5}%`
              }}
              title={`${point.period}: ${formatPercent(point.return)} return, ${formatPercent(point.risk)} risk`}
            />
          ))}
        </div>
        
        {/* Legend */}
        <div className="flex justify-center space-x-6 mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-600 rounded-full" />
            <span className="text-sm text-gray-700">Portfolio</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-600 rounded-full" />
            <span className="text-sm text-gray-700">Benchmark</span>
          </div>
        </div>
        
        {/* Best Period */}
        {metadata?.best_period && (
          <div className="mt-6 p-4 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Best Period:</strong> {metadata.best_period.period} 
              (Sharpe: {metadata.best_period.sharpe_ratio?.toFixed(2)})
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderCorrelationChart = () => {
    if (!chartData || !chartData.data || !chartData.data.symbols) {
      return (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No correlation data available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add investments to your portfolio to see correlation analysis.
          </p>
        </div>
      );
    }
    
    const { symbols, matrix, metadata } = chartData.data;
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Correlation Matrix</h3>
        
        {/* Simple Correlation Matrix */}
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="px-4 py-2 text-sm font-medium text-gray-900"></th>
                {symbols.map((symbol: string, index: number) => (
                  <th key={index} className="px-4 py-2 text-sm font-medium text-gray-900">
                    {symbol}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {symbols.map((symbol: string, rowIndex: number) => (
                <tr key={rowIndex}>
                  <td className="px-4 py-2 text-sm font-medium text-gray-900">{symbol}</td>
                  {matrix[rowIndex].map((corr: number, colIndex: number) => (
                    <td 
                      key={colIndex} 
                      className={`px-4 py-2 text-sm text-center ${
                        corr >= 0.7 ? 'bg-red-100 text-red-800' :
                        corr >= 0.3 ? 'bg-yellow-100 text-yellow-800' :
                        corr >= -0.3 ? 'bg-gray-100 text-gray-800' :
                        'bg-green-100 text-green-800'
                      }`}
                    >
                      {corr.toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Metadata */}
        {metadata && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-600">Most Correlated</p>
              <p className="text-sm font-medium text-gray-900">
                {Object.keys(metadata.most_correlated)[0] || 'N/A'}
              </p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-600">Least Correlated</p>
              <p className="text-sm font-medium text-gray-900">
                {Object.keys(metadata.least_correlated)[0] || 'N/A'}
              </p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-600">Average Correlation</p>
              <p className="text-sm font-medium text-gray-900">
                {metadata.average_correlation?.toFixed(3) || 'N/A'}
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderStockChart = () => {
    if (!chartData || !chartData.data || !chartData.data.values) {
      return (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No stock data available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try selecting a different stock symbol or timeframe.
          </p>
        </div>
      );
    }
    
    const { ohlc, technical_indicators, metadata } = chartData.data;
    
    return (
      <div className="space-y-6">
        {/* Stock Symbol Input */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock Symbol</label>
              <input
                type="text"
                value={stockSymbol}
                onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="AAPL, TSLA, etc."
              />
            </div>
            <button
              onClick={loadChartData}
              className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Update
            </button>
          </div>
        </div>
        
        {/* Candlestick Chart */}
        {ohlc && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {stockSymbol} Price Chart
            </h3>
            
            {/* Simple OHLC Chart */}
            <div className="h-64 flex items-end space-x-1">
              {ohlc.slice(-30).map((candle: any, index: number) => {
                const maxPrice = Math.max(...ohlc.slice(-30).map((c: any) => c.high));
                const heightPercent = (candle.high / maxPrice) * 100;
                const isGreen = candle.close >= candle.open;
                
                return (
                  <div
                    key={index}
                    className="flex-1 flex flex-col items-center"
                    title={`O: ${candle.open} H: ${candle.high} L: ${candle.low} C: ${candle.close}`}
                  >
                    <div className="w-full flex flex-col items-center">
                      <div 
                        className={`w-1 ${isGreen ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ height: `${heightPercent * 0.8}%` }}
                      />
                      <div 
                        className={`w-3 ${isGreen ? 'bg-green-500' : 'bg-red-500'} rounded-t`}
                        style={{ height: `${heightPercent * 0.2}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Technical Indicators */}
            {technical_indicators && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div>
                  <p className="text-sm text-gray-600">Current Price</p>
                  <p className="text-lg font-semibold text-gray-900">{formatCurrency(metadata.current_price)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Change</p>
                  <p className={`text-lg font-semibold ${metadata.price_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(metadata.price_change)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">52W High</p>
                  <p className="text-lg font-semibold text-gray-900">{formatCurrency(metadata.high_52w)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">52W Low</p>
                  <p className="text-lg font-semibold text-gray-900">{formatCurrency(metadata.low_52w)}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderChart = () => {
    switch (activeChart) {
      case 'portfolio':
        return renderPortfolioChart();
      case 'allocation':
        return renderAllocationChart();
      case 'risk-return':
        return renderRiskReturnChart();
      case 'correlation':
        return renderCorrelationChart();
      case 'stock':
        return renderStockChart();
      default:
        return null;
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">Advanced Charts</h1>
            <p className="text-gray-600">Interactive visualizations for portfolio analysis</p>
          </div>
          <button
            onClick={loadChartData}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Chart Type Selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Chart:</label>
            <select
              value={activeChart}
              onChange={(e) => setActiveChart(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="portfolio">Portfolio Performance</option>
              <option value="allocation">Asset Allocation</option>
              <option value="risk-return">Risk vs Return</option>
              <option value="correlation">Correlation Matrix</option>
              <option value="stock">Stock Chart</option>
            </select>
          </div>

          {/* Timeframe Selector */}
          {(activeChart === 'portfolio' || activeChart === 'stock') && (
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Timeframe:</label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="px-3 <lambda_7> py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {timeframes.map(tf => (
                  <option key={tf.value} value={tf.value}>{tf.label}</option>
                ))}
              </select>
            </div>
          )}

          {/* Benchmark Symbols (for comparison charts) */}
          {activeChart === 'portfolio' && (
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Benchmarks:</label>
              <input
                type="text"
                value={benchmarkSymbols}
                onChange={(e) => setBenchmarkSymbols(e.target.value)}
                className="px-3 <lambda_7> -2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="SPY,QQQ"
              />
            </div>
          )}
        </div>
      </div>

      {/* Chart Display */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="min-h-64">
          {renderChart()}
        </div>
      )}
    </div>
  );
};

export default Charts;
