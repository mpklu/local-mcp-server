import React, { useState, useEffect } from 'react';
import {
  ServerIcon,
  Cog6ToothIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  InformationCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface ServerStatus {
  running: boolean;
  uptime?: string;
  process_id?: number;
  server_name: string;
  last_started?: string;
}

interface ServerConfig {
  server_name: string;
  server_version: string;
  timeout_seconds: number;
  max_output_length: number;
}

interface ServerLogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

const ServerMonitoring: React.FC = () => {
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null);
  const [serverConfig, setServerConfig] = useState<ServerConfig | null>(null);
  const [logs, setLogs] = useState<ServerLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'status' | 'config' | 'logs'>('status');
  const [configEditing, setConfigEditing] = useState(false);
  const [configForm, setConfigForm] = useState<ServerConfig | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchServerData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchServerData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchServerData = async () => {
    try {
      if (!loading) setRefreshing(true);
      setError(null);

      // Fetch server status
      const statusResponse = await fetch('/api/server/status');
      if (statusResponse.ok) {
        const status = await statusResponse.json();
        setServerStatus(status);
      }

      // Fetch server config
      const configResponse = await fetch('/api/server/config');
      if (configResponse.ok) {
        const config = await configResponse.json();
        setServerConfig(config);
        setConfigForm(config);
      }

      // Fetch logs
      const logsResponse = await fetch('/api/server/logs?lines=50');
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setLogs(logsData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch server data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!configForm) return;

    try {
      const response = await fetch('/api/server/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configForm),
      });

      if (response.ok) {
        setServerConfig(configForm);
        setConfigEditing(false);
        await fetchServerData();
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    }
  };

  const getStatusColor = (running: boolean) => {
    return running ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
  };

  const getStatusIcon = (running: boolean) => {
    return running ? CheckCircleIcon : ExclamationTriangleIcon;
  };

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'bg-red-900 text-red-200';
      case 'WARN':
      case 'WARNING':
        return 'bg-yellow-900 text-yellow-200';
      case 'INFO':
        return 'bg-blue-900 text-blue-200';
      default:
        return 'bg-gray-900 text-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <ServerIcon className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-3" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Server Monitoring
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Monitor your Local MCP Server (managed by Claude Desktop)
            </p>
          </div>
        </div>

        {/* Status and Refresh */}
        <div className="flex items-center space-x-4">
          {serverStatus && (
            <div className="flex items-center">
              {React.createElement(getStatusIcon(serverStatus.running), {
                className: `h-6 w-6 ${getStatusColor(serverStatus.running)} mr-2`
              })}
              <span className={`text-sm font-medium ${getStatusColor(serverStatus.running)}`}>
                {serverStatus.running ? 'Running' : 'Not Running'}
              </span>
            </div>
          )}
          
          <button
            onClick={fetchServerData}
            disabled={refreshing}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-3 mt-0.5 flex-shrink-0" />
          <div className="text-blue-800 dark:text-blue-200">
            <p className="font-medium">Server Managed by Claude Desktop</p>
            <p className="text-sm mt-1">
              The MCP server is automatically started and managed by Claude Desktop. 
              Use this interface to monitor server status, view logs, and configure settings.
            </p>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400 mr-3" />
            <span className="text-red-800 dark:text-red-200">{error}</span>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'status', name: 'Status', icon: ServerIcon },
            { id: 'config', name: 'Configuration', icon: Cog6ToothIcon },
            { id: 'logs', name: 'Logs', icon: DocumentTextIcon }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'status' | 'config' | 'logs')}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {/* Status Tab */}
        {activeTab === 'status' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Server Status
              </h3>
              {serverStatus ? (
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</dt>
                    <dd className={`text-sm font-semibold ${getStatusColor(serverStatus.running)}`}>
                      {serverStatus.running ? 'Running' : 'Not Running'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Server Name</dt>
                    <dd className="text-sm text-gray-900 dark:text-white">{serverStatus.server_name}</dd>
                  </div>
                  {serverStatus.last_started && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Activity</dt>
                      <dd className="text-sm text-gray-900 dark:text-white">
                        {new Date(serverStatus.last_started).toLocaleString()}
                      </dd>
                    </div>
                  )}
                </dl>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">Loading...</p>
              )}
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Configuration
              </h3>
              {serverConfig ? (
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Version</dt>
                    <dd className="text-sm text-gray-900 dark:text-white">{serverConfig.server_version}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Timeout</dt>
                    <dd className="text-sm text-gray-900 dark:text-white">{serverConfig.timeout_seconds}s</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Max Output</dt>
                    <dd className="text-sm text-gray-900 dark:text-white">{serverConfig.max_output_length} chars</dd>
                  </div>
                </dl>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">Loading...</p>
              )}
            </div>
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Server Configuration
              </h3>
              <div className="space-x-3">
                {configEditing ? (
                  <>
                    <button
                      onClick={() => setConfigEditing(false)}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveConfig}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Changes
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setConfigEditing(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Edit Configuration
                  </button>
                )}
              </div>
            </div>

            {configForm && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="server_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Server Name
                  </label>
                  <input
                    id="server_name"
                    type="text"
                    value={configForm.server_name}
                    onChange={(e) => setConfigForm({...configForm, server_name: e.target.value})}
                    disabled={!configEditing}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label htmlFor="server_version" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Server Version
                  </label>
                  <input
                    id="server_version"
                    type="text"
                    value={configForm.server_version}
                    onChange={(e) => setConfigForm({...configForm, server_version: e.target.value})}
                    disabled={!configEditing}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label htmlFor="timeout_seconds" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Timeout (seconds)
                  </label>
                  <input
                    id="timeout_seconds"
                    type="number"
                    value={configForm.timeout_seconds}
                    onChange={(e) => setConfigForm({...configForm, timeout_seconds: parseInt(e.target.value) || 300})}
                    disabled={!configEditing}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label htmlFor="max_output_length" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Output Length
                  </label>
                  <input
                    id="max_output_length"
                    type="number"
                    value={configForm.max_output_length}
                    onChange={(e) => setConfigForm({...configForm, max_output_length: parseInt(e.target.value) || 10000})}
                    disabled={!configEditing}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
            )}

            {configEditing && (
              <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                  <strong>Note:</strong> Configuration changes require restarting Claude Desktop to take effect.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Server Logs
              </h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Last {logs.length} entries (auto-refreshes every 30s)
              </span>
            </div>

            <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
              {logs.length > 0 ? (
                logs.map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className="mb-1">
                    <span className="text-gray-400">{log.timestamp}</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${getLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className="text-gray-300 ml-2">[{log.source}]</span>
                    <span className="text-white ml-2">{log.message}</span>
                  </div>
                ))
              ) : (
                <div className="text-gray-400 text-center py-8">
                  No logs available
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServerMonitoring;
