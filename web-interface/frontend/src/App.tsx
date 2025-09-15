import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Cog6ToothIcon, WrenchScrewdriverIcon, PlusIcon, BookOpenIcon, ServerIcon } from '@heroicons/react/24/outline';
import ToolList from './components/ToolList';
import ToolConfig from './components/ToolConfig';
import Dashboard from './components/Dashboard';
import AddToolWizard from './components/AddToolWizard';
import HelpDocumentation from './components/HelpDocumentation';
import ServerMonitoring from './components/ServerMonitoring';
import { NotificationProvider } from './contexts/NotificationContext';
import { apiClient } from './api';

function Navigation() {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: Cog6ToothIcon },
    { name: 'Tools', href: '/tools', icon: WrenchScrewdriverIcon },
    { name: 'Monitor', href: '/server', icon: ServerIcon },
    { name: 'Add Tool', href: '/tools/add', icon: PlusIcon },
    { name: 'Help', href: '/help', icon: BookOpenIcon },
  ];

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <WrenchScrewdriverIcon className="h-8 w-8 text-indigo-600" />
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                MCP Tools
              </span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive
                        ? 'border-indigo-500 text-gray-900 dark:text-white'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-300 dark:hover:text-white'
                    }`}
                  >
                    <item.icon className="h-5 w-5 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    // Check API health on startup
    const checkHealth = async () => {
      try {
        await apiClient.healthCheck();
        setIsHealthy(true);
      } catch (error) {
        console.error('API health check failed:', error);
        setIsHealthy(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkHealth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isHealthy) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">API Connection Failed</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Unable to connect to the backend API. Please ensure the server is running on port 8080.
          </p>
          <div className="mt-6">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <NotificationProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <Navigation />
          
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tools" element={<ToolList />} />
              <Route path="/tools/:toolName" element={<ToolConfig />} />
              <Route path="/tools/add" element={<AddToolWizard />} />
              <Route path="/tools/new" element={<ToolConfig />} />
              <Route path="/server" element={<ServerMonitoring />} />
              <Route path="/help" element={<HelpDocumentation />} />
            </Routes>
          </main>
        </div>
      </Router>
    </NotificationProvider>
  );
}

export default App;
