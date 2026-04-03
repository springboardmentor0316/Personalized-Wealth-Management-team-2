import React, { useState, useEffect } from 'react';
import { 
  BellIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  FlagIcon,
  PlayIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface Alert {
  id: number;
  alert_type: string;
  symbol?: string;
  condition: string;
  threshold_value: number;
  current_value?: number;
  is_active: boolean;
  is_triggered: boolean;
  notification_method: string;
  frequency: string;
  created_at: string;
  triggered_at?: string;
  last_notified?: string;
}

interface AlertTypes {
  [key: string]: {
    name: string;
    description: string;
    conditions: string[];
    requires_symbol: boolean;
    examples: Array<{
      condition: string;
      threshold: number;
      description: string;
    }>;
  };
}

const Alerts: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'create' | 'types'>('alerts');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);
  const [alertTypes, setAlertTypes] = useState<AlertTypes>({});
  const [statistics, setStatistics] = useState<any>(null);
  const [testingAlert, setTestingAlert] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    alert_type: 'price',
    symbol: '',
    condition: 'above',
    threshold_value: '',
    notification_method: 'email',
    frequency: 'once'
  });

  useEffect(() => {
    loadAlerts();
    loadAlertTypes();
    loadStatistics();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8003/api/alerts/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setAlerts(data.data.alerts);
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAlertTypes = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/alerts/types');
      const data = await response.json();
      if (data.success) {
        setAlertTypes(data.data.alert_types);
      }
    } catch (error) {
      console.error('Error loading alert types:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/alerts/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setStatistics(data.data);
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const createAlert = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/alerts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          ...formData,
          threshold_value: parseFloat(formData.threshold_value)
        })
      });
      
      if (response.ok) {
        setShowCreateForm(false);
        setFormData({
          alert_type: 'price',
          symbol: '',
          condition: 'above',
          threshold_value: '',
          notification_method: 'email',
          frequency: 'once'
        });
        loadAlerts();
        loadStatistics();
      }
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  const updateAlert = async (alertId: number, updates: Partial<Alert>) => {
    try {
      const response = await fetch(`http://localhost:8003/api/alerts/${alertId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(updates)
      });
      
      if (response.ok) {
        loadAlerts();
        setEditingAlert(null);
      }
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  const deleteAlert = async (alertId: number) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;
    
    try {
      const response = await fetch(`http://localhost:8003/api/alerts/${alertId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadAlerts();
        loadStatistics();
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  const testAlert = async (alertId: number) => {
    setTestingAlert(alertId);
    try {
      const response = await fetch(`http://localhost:8003/api/alerts/${alertId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        window.alert(`Alert Test Result:\nCurrent Value: ${data.data.current_value}\nThreshold: ${data.data.threshold_value}\nWould Trigger: ${data.data.would_trigger ? 'Yes' : 'No'}`);
      }
    } catch (error) {
      console.error('Error testing alert:', error);
    } finally {
      setTestingAlert(null);
    }
  };

  const createSmartAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/alerts/smart-alerts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadAlerts();
        loadStatistics();
      }
    } catch (error) {
      console.error('Error creating smart alerts:', error);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getAlertIcon = (alertType: string) => {
    const icons = {
      'price': ArrowTrendingUpIcon,
      'portfolio': CurrencyDollarIcon,
      'goal': FlagIcon,
      'market': BellIcon
    };
    return icons[alertType as keyof typeof icons] || BellIcon;
  };

  const getConditionIcon = (condition: string) => {
    if (condition === 'above' || condition === 'change_percent_up') return ArrowTrendingUpIcon;
    if (condition === 'below' || condition === 'change_percent_down') return ArrowTrendingDownIcon;
    return InformationCircleIcon;
  };

  const getConditionColor = (condition: string) => {
    if (condition === 'above' || condition === 'change_percent_up') return 'text-green-600';
    if (condition === 'below' || condition === 'change_percent_down') return 'text-red-600';
    return 'text-gray-600';
  };

  const getAlertTypeColor = (alertType: string) => {
    const colors = {
      'price': 'text-blue-600 bg-blue-100',
      'portfolio': 'text-green-600 bg-green-100',
      'goal': 'text-purple-600 bg-purple-100',
      'market': 'text-orange-600 bg-orange-100'
    };
    return colors[alertType as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  const renderAlertCard = (alert: Alert) => {
    const AlertIcon = getAlertIcon(alert.alert_type);
    const ConditionIcon = getConditionIcon(alert.condition);
    
    return (
      <div key={alert.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <AlertIcon className="h-6 w-6 text-gray-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAlertTypeColor(alert.alert_type)}`}>
                  {alertTypes[alert.alert_type]?.name || alert.alert_type}
                </span>
                {alert.symbol && (
                  <span className="text-lg font-semibold text-gray-900">{alert.symbol}</span>
                )}
              </div>
              
              <div className="flex items-center space-x-2 mt-2">
                <ConditionIcon className={`h-4 w-4 ${getConditionColor(alert.condition)}`} />
                <span className={`text-sm font-medium ${getConditionColor(alert.condition)}`}>
                  {alert.condition}
                </span>
                <span className="text-sm text-gray-600">
                  {alert.alert_type === 'price' || alert.alert_type === 'portfolio' 
                    ? formatCurrency(alert.threshold_value)
                    : `${alert.threshold_value}%`
                  }
                </span>
              </div>

              {alert.current_value !== undefined && (
                <div className="mt-2">
                  <span className="text-sm text-gray-600">Current: </span>
                  <span className="text-sm font-medium text-gray-900">
                    {alert.alert_type === 'price' || alert.alert_type === 'portfolio' 
                      ? formatCurrency(alert.current_value)
                      : `${alert.current_value}%`
                    }
                  </span>
                </div>
              )}

              <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                <span>{alert.notification_method}</span>
                <span>{alert.frequency}</span>
                <span>Created {formatDate(alert.created_at)}</span>
              </div>

              {alert.is_triggered && (
                <div className="mt-3 p-2 bg-yellow-50 rounded-md">
                  <p className="text-sm text-yellow-800">
                    <ExclamationTriangleIcon className="h-4 w-4 inline mr-1" />
                    Triggered {alert.triggered_at ? formatDate(alert.triggered_at) : 'recently'}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => testAlert(alert.id)}
              disabled={testingAlert === alert.id}
              className="text-gray-400 hover:text-blue-600 disabled:opacity-50"
            >
              <PlayIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setEditingAlert(alert)}
              className="text-gray-400 hover:text-blue-600"
            >
              <PencilIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => deleteAlert(alert.id)}
              className="text-gray-400 hover:text-red-600"
            >
              <TrashIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => updateAlert(alert.id, { is_active: !alert.is_active })}
              className={`${
                alert.is_active ? 'text-green-600' : 'text-gray-400'
              } hover:text-green-600`}
            >
              {alert.is_active ? <CheckCircleIcon className="h-5 w-5" /> : <XCircleIcon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">Smart Alerts</h1>
            <p className="text-gray-600">Stay informed with intelligent price and portfolio notifications</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={createSmartAlerts}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <BellIcon className="h-4 w-4 mr-2" />
              Smart Alerts
            </button>
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Alert
            </button>
          </div>
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BellIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Total Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_alerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.active_alerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Triggered</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.triggered_alerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.success_rate?.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Alert Modal */}
      {(showCreateForm || editingAlert) && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {editingAlert ? 'Edit Alert' : 'Create New Alert'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Alert Type</label>
                <select
                  value={editingAlert ? editingAlert.alert_type : formData.alert_type}
                  onChange={(e) => editingAlert 
                    ? setEditingAlert({...editingAlert, alert_type: e.target.value})
                    : setFormData({...formData, alert_type: e.target.value})
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  {Object.entries(alertTypes).map(([key, type]) => (
                    <option key={key} value={key}>{type.name}</option>
                  ))}
                </select>
              </div>

              {(editingAlert?.alert_type === 'price' || formData.alert_type === 'price') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Symbol</label>
                  <input
                    type="text"
                    value={editingAlert?.symbol || formData.symbol}
                    onChange={(e) => editingAlert 
                      ? setEditingAlert({...editingAlert, symbol: e.target.value})
                      : setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="AAPL, TSLA, etc."
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700">Condition</label>
                <select
                  value={editingAlert ? editingAlert.condition : formData.condition}
                  onChange={(e) => editingAlert 
                    ? setEditingAlert({...editingAlert, condition: e.target.value})
                    : setFormData({...formData, condition: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                  <option value="equals">Equals</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Threshold Value</label>
                <input
                  type="number"
                  step="0.01"
                  value={editingAlert?.threshold_value || formData.threshold_value}
                  onChange={(e) => editingAlert 
                    ? setEditingAlert({...editingAlert, threshold_value: parseFloat(e.target.value)})
                    : setFormData({...formData, threshold_value: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="100.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Notification Method</label>
                <select
                  value={editingAlert ? editingAlert.notification_method : formData.notification_method}
                  onChange={(e) => editingAlert 
                    ? setEditingAlert({...editingAlert, notification_method: e.target.value})
                    : setFormData({...formData, notification_method: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="email">Email</option>
                  <option value="push">Push Notification</option>
                  <option value="sms">SMS</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Frequency</label>
                <select
                  value={editingAlert ? editingAlert.frequency : formData.frequency}
                  onChange={(e) => editingAlert 
                    ? setEditingAlert({...editingAlert, frequency: e.target.value})
                    : setFormData({...formData, frequency: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="once">Once</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingAlert(null);
                  setFormData({
                    alert_type: 'price',
                    symbol: '',
                    condition: 'above',
                    threshold_value: '',
                    notification_method: 'email',
                    frequency: 'once'
                  });
                }}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (editingAlert) {
                    updateAlert(editingAlert.id, editingAlert);
                  } else {
                    createAlert();
                  }
                }}
                className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {editingAlert ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : alerts.length > 0 ? (
          alerts.map(renderAlertCard)
        ) : (
          <div className="text-center py-12">
            <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts configured</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create your first alert to start monitoring your portfolio and the market.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create Alert
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
