import React, { useState, useEffect } from 'react';
import {
  ServerIcon,
  Cog6ToothIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  InformationCircleIcon
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

const ServerManagement: React.FC = () => {
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null);
  const [serverConfig, setServerConfig] = useState<ServerConfig | null>(null);
  const [logs, setLogs] = useState<ServerLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'status' | 'config' | 'logs'>('status');
  const [configEditing, setConfigEditing] = useState(false);
  const [configForm, setConfigForm] = useState<ServerConfig | null>(null);

  useEffect(() => {
    fetchServerData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchServerData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchServerData = async () => {
    try {
      setLoading(true);
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
    }
  };

  // Note: Server start/stop functionality not yet implemented in UI
  // These endpoints will be added when server management is fully implemented

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

        {/* Status Indicator */}
        <div className="flex items-center space-x-3">
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
                onClick={() => setActiveTab(tab.id as any)}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        {activeTab === 'status' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Server Status
            </h2>
            
            {serverStatus && (
              <div className="space-y-6">
                {/* Status Overview */}
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Status</p>
                        <p className={`text-lg font-semibold ${getStatusColor(serverStatus.running)}`}>
                          {serverStatus.running ? 'Running' : 'Stopped'}
                        </p>
                      </div>
                      {React.createElement(getStatusIcon(serverStatus.running), {
                        className: `h-8 w-8 ${getStatusColor(serverStatus.running)}`
                      })}
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Server Name</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {serverStatus.server_name}
                        </p>
                      </div>
                      <ServerIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Process ID</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {serverStatus.process_id || 'N/A'}
                        </p>
                      </div>
                      <Cog6ToothIcon className="h-8 w-8 text-gray-600 dark:text-gray-400" />
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Uptime</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {serverStatus.uptime || 'N/A'}
                        </p>
                      </div>
                      <ClockIcon className="h-8 w-8 text-gray-600 dark:text-gray-400" />
                    </div>
                  </div>
                </div>

                {/* Implementation Note */}
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                    <div>
                      <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Implementation Note</h4>
                      <p className="mt-1 text-sm text-yellow-800 dark:text-yellow-200">
                        Server process management is not yet fully implemented. The start/stop functionality will be added in a future update.
                        For now, use the command line to start the MCP server manually.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'config' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Server Configuration
              </h2>
              <button
                onClick={() => setConfigEditing(!configEditing)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Cog6ToothIcon className="h-5 w-5 mr-2" />
                {configEditing ? 'Cancel' : 'Edit Config'}
              </button>
            </div>

            {configForm && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Server Name
                    </label>
                    <input
                      type="text"
                      value={configForm.server_name}
                      onChange={(e) => setConfigForm({ ...configForm, server_name: e.target.value })}
                      disabled={!configEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Server Version
                    </label>
                    <input
                      type="text"
                      value={configForm.server_version}
                      onChange={(e) => setConfigForm({ ...configForm, server_version: e.target.value })}
                      disabled={!configEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      value={configForm.timeout_seconds}
                      onChange={(e) => setConfigForm({ ...configForm, timeout_seconds: parseInt(e.target.value) })}
                      disabled={!configEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max Output Length
                    </label>
                    <input
                      type="number"
                      value={configForm.max_output_length}
                      onChange={(e) => setConfigForm({ ...configForm, max_output_length: parseInt(e.target.value) })}
                      disabled={!configEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                </div>

                {configEditing && (
                  <div className="flex justify-end space-x-3">
                    <button
                      onClick={() => {
                        setConfigEditing(false);
                        setConfigForm(serverConfig);
                      }}
                      className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveConfig}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Changes
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Server Logs
            </h2>
            
            <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-4 font-mono text-sm overflow-auto max-h-96">
              {logs.length > 0 ? (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    <span className="text-gray-400">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${
                      log.level === 'ERROR' ? 'bg-red-900 text-red-200' :
                      log.level === 'WARN' ? 'bg-yellow-900 text-yellow-200' :
                      'bg-blue-900 text-blue-200'
                    }`}>
                      {log.level}
                    </span>
                    <span className="text-gray-200 ml-2">{log.message}</span>
                  </div>
                ))
              ) : (
                <div className="text-gray-400 text-center py-8">
                  No logs available. Server logs will appear here when the server is running.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServerManagement;
