import React, { useState, useEffect } from 'react';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, CurrencyDollarIcon, CalendarIcon } from '@heroicons/react/24/outline';

interface MarketPrice {
  symbol: string;
  price: number;
  change?: number;
  changePercent?: number;
}

const MarketData: React.FC = () => {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [symbols, setSymbols] = useState('AAPL,TSLA,MSFT,GOOGL,AMZN');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [updating, setUpdating] = useState(false);

  const defaultSymbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'BTC-USD', 'ETH-USD'];

  useEffect(() => {
    fetchPrices();
  }, [symbols]);

  const fetchPrices = async () => {
    try {
      setLoading(true);
      const symbolList = symbols.split(',').map(s => s.trim()).filter(s => s);
      const response = await fetch(`http://localhost:8003/market/prices?symbols=${symbolList.join(',')}`);
      const data = await response.json();
      setPrices(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching prices:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePrices = async () => {
    try {
      setUpdating(true);
      const symbolList = symbols.split(',').map(s => s.trim()).filter(s => s);
      const response = await fetch(`http://localhost:8003/market/update?symbols=${symbolList.join(',')}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setPrices(data.prices);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Error updating prices:', error);
    } finally {
      setUpdating(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const addSymbol = (symbol: string) => {
    const currentSymbols = symbols.split(',').map(s => s.trim()).filter(s => s);
    if (!currentSymbols.includes(symbol.toUpperCase())) {
      setSymbols([...currentSymbols, symbol.toUpperCase()].join(','));
    }
  };

  const removeSymbol = (symbol: string) => {
    const currentSymbols = symbols.split(',').map(s => s.trim()).filter(s => s);
    setSymbols(currentSymbols.filter(s => s !== symbol).join(','));
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Market Data</h1>
        <p className="text-gray-600">Real-time market prices and updates</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Symbols (comma-separated)
            </label>
            <input
              type="text"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="AAPL,TSLA,MSFT"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchPrices}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <ArrowTrendingUpIcon className="h-4 w-4" />
              Fetch Prices
            </button>
            <button
              onClick={updatePrices}
              disabled={updating}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <CurrencyDollarIcon className="h-4 w-4" />
              {updating ? 'Updating...' : 'Update Prices'}
            </button>
          </div>
        </div>
        
        {/* Quick Add Symbols */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-2">Quick add:</p>
          <div className="flex flex-wrap gap-2">
            {defaultSymbols.map(symbol => (
              <button
                key={symbol}
                onClick={() => addSymbol(symbol)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                {symbol}
              </button>
            ))}
          </div>
        </div>

        {lastUpdate && (
          <div className="mt-4 text-sm text-gray-500 flex items-center gap-1">
            <CalendarIcon className="h-4 w-4" />
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Prices Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(prices).map(([symbol, price]) => (
            <div key={symbol} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{symbol}</h3>
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  ×
                </button>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {formatPrice(price)}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                Real-time price
              </div>
            </div>
          ))}
        </div>
      )}

      {Object.keys(prices).length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No market data available. Add symbols and fetch prices to get started.</p>
        </div>
      )}
    </div>
  );
};

export default MarketData;
