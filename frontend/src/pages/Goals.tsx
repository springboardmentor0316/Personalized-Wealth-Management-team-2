import React, { useState, useEffect } from 'react';
import { goalsAPI } from '../services/api';
import { Goal, GoalCreate, GoalCategory } from '../types';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  TagIcon,
  CalendarIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';

const Goals: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [formData, setFormData] = useState<GoalCreate>({
    title: '',
    description: '',
    target_amount: 0,
    current_amount: 0,
    target_date: '',
    monthly_contribution: 0,
    category: GoalCategory.OTHER,
  });

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const goalsData = await goalsAPI.getGoals();
      setGoals(goalsData);
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingGoal) {
        await goalsAPI.updateGoal(editingGoal.id, formData);
      } else {
        await goalsAPI.createGoal(formData);
      }
      setShowModal(false);
      setEditingGoal(null);
      setFormData({
        title: '',
        description: '',
        target_amount: 0,
        current_amount: 0,
        target_date: '',
        monthly_contribution: 0,
        category: GoalCategory.OTHER,
      });
      fetchGoals();
    } catch (error) {
      console.error('Error saving goal:', error);
    }
  };

  const handleEdit = (goal: Goal) => {
    setEditingGoal(goal);
    setFormData({
      title: goal.title,
      description: goal.description || '',
      target_amount: goal.target_amount,
      current_amount: goal.current_amount,
      target_date: goal.target_date.split('T')[0],
      monthly_contribution: goal.monthly_contribution,
      category: goal.category,
    });
    setShowModal(true);
  };

  const handleDelete = async (goalId: number) => {
    if (window.confirm('Are you sure you want to delete this goal?')) {
      try {
        await goalsAPI.deleteGoal(goalId);
        fetchGoals();
      } catch (error) {
        console.error('Error deleting goal:', error);
      }
    }
  };

  const getProgressPercentage = (goal: Goal) => {
    return (goal.current_amount / goal.target_amount) * 100;
  };

  const getCategoryColor = (category: GoalCategory) => {
    const colors = {
      [GoalCategory.RETIREMENT]: 'bg-blue-100 text-blue-800',
      [GoalCategory.EDUCATION]: 'bg-green-100 text-green-800',
      [GoalCategory.HOME]: 'bg-purple-100 text-purple-800',
      [GoalCategory.VACATION]: 'bg-yellow-100 text-yellow-800',
      [GoalCategory.EMERGENCY]: 'bg-red-100 text-red-800',
      [GoalCategory.OTHER]: 'bg-gray-100 text-gray-800',
    };
    return colors[category] || colors[GoalCategory.OTHER];
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
        <h1 className="text-2xl font-bold text-gray-900">Financial Goals</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Goal
        </button>
      </div>

      {goals.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <TagIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No goals yet</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating your first financial goal.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Add Goal
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {goals.map((goal) => (
            <div key={goal.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{goal.title}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(goal.category)}`}>
                    {goal.category}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(goal)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(goal.id)}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {goal.description && (
                <p className="text-gray-600 text-sm mb-4">{goal.description}</p>
              )}

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Progress</span>
                  <span className="text-sm font-medium text-gray-900">
                    {getProgressPercentage(goal).toFixed(1)}%
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(getProgressPercentage(goal), 100)}%` }}
                  ></div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Current</span>
                  <span className="font-medium text-gray-900">
                    ${goal.current_amount.toFixed(2)}
                  </span>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Target</span>
                  <span className="font-medium text-gray-900">
                    ${goal.target_amount.toFixed(2)}
                  </span>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center text-gray-500">
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    Target Date
                  </div>
                  <span className="font-medium text-gray-900">
                    {new Date(goal.target_date).toLocaleDateString()}
                  </span>
                </div>

                {goal.monthly_contribution > 0 && (
                  <div className="flex justify-between items-center text-sm">
                    <div className="flex items-center text-gray-500">
                      <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                      Monthly
                    </div>
                    <span className="font-medium text-gray-900">
                      ${goal.monthly_contribution.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {editingGoal ? 'Edit Goal' : 'Create New Goal'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value as GoalCategory })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={GoalCategory.RETIREMENT}>Retirement</option>
                  <option value={GoalCategory.EDUCATION}>Education</option>
                  <option value={GoalCategory.HOME}>Home</option>
                  <option value={GoalCategory.VACATION}>Vacation</option>
                  <option value={GoalCategory.EMERGENCY}>Emergency</option>
                  <option value={GoalCategory.OTHER}>Other</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Amount</label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="0.01"
                    value={formData.target_amount}
                    onChange={(e) => setFormData({ ...formData, target_amount: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Current Amount</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.current_amount}
                    onChange={(e) => setFormData({ ...formData, current_amount: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Date</label>
                  <input
                    type="date"
                    required
                    value={formData.target_date}
                    onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Monthly Contribution</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.monthly_contribution}
                    onChange={(e) => setFormData({ ...formData, monthly_contribution: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingGoal(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingGoal ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Goals;
