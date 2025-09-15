import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiClient } from '../api';
import { useNotifications } from '../contexts/NotificationContext';

interface DashboardStats {
  totalTools: number;
  enabledTools: number;
  disabledTools: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({ totalTools: 0, enabledTools: 0, disabledTools: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);
  const [searchParams] = useSearchParams();
  const { addNotification } = useNotifications();

  useEffect(() => {
    loadStats();
    
    // Check for new tool notification
    const newTool = searchParams.get('newTool');
    if (newTool) {
      addNotification({
        type: 'success',
        title: 'Tool Created Successfully!',
        message: `Your tool "${newTool}" has been created and is ready to use.`,
        duration: 6000
      });
      
      // Clean up URL without triggering navigation
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [searchParams, addNotification]);

  const loadStats = async () => {
    try {
      const tools = await apiClient.getTools();
      const enabled = tools.filter(tool => tool.enabled).length;
      setStats({
        totalTools: tools.length,
        enabledTools: enabled,
        disabledTools: tools.length - enabled,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleScan = async () => {
    setIsScanning(true);
    try {
      await apiClient.scanForTools();
      await loadStats(); // Refresh stats after scan
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setIsScanning(false);
    }
  };

  const handleBuild = async () => {
    setIsBuilding(true);
    try {
      await apiClient.buildToolsJson();
    } catch (error) {
      console.error('Build failed:', error);
    } finally {
      setIsBuilding(false);
    }
  };

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-300 rounded w-1/4 mb-4"></div>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-300 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Overview of your MCP tools and quick actions
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">{stats.totalTools}</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Total Tools
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {stats.totalTools}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">{stats.enabledTools}</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Enabled Tools
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {stats.enabledTools}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gray-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">{stats.disabledTools}</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Disabled Tools
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {stats.disabledTools}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Quick Actions
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <button
              onClick={handleScan}
              disabled={isScanning}
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isScanning ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : null}
              {isScanning ? 'Scanning...' : 'Scan for New Tools'}
            </button>

            <button
              onClick={handleBuild}
              disabled={isBuilding}
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isBuilding ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
              ) : null}
              {isBuilding ? 'Building...' : 'Build tools.json'}
            </button>

            <a
              href="/tools"
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Manage All Tools
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
