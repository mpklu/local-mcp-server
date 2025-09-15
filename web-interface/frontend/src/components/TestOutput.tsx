import React, { useState } from 'react';
import { 
  ClipboardDocumentIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

// Union type for different test result formats
type TestOutputData = {
  success: boolean;
  message: string;
  output?: string;
  error?: string;
  parameters?: Record<string, any>;
  exit_code?: number;
  test_script_path?: string;
  has_test_script?: boolean;
};

interface TestOutputProps {
  title: string;
  data: TestOutputData;
  showParameters?: boolean;
  className?: string;
}

const TestOutput: React.FC<TestOutputProps> = ({ 
  title, 
  data, 
  showParameters = false,
  className = ""
}) => {
  const [copyToast, setCopyToast] = useState<string | null>(null);

  const handleCopyOutput = async (content: string, label: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopyToast(`${label} copied to clipboard!`);
      setTimeout(() => setCopyToast(null), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyToast(`Failed to copy ${label.toLowerCase()}`);
      setTimeout(() => setCopyToast(null), 2000);
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Title */}
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
      )}
      
      {/* Status Banner */}
      <div className={`p-4 rounded-lg ${
        data.success 
          ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
          : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {data.success ? (
              <CheckIcon className="h-5 w-5 text-green-500 mr-2" />
            ) : (
              <XMarkIcon className="h-5 w-5 text-red-500 mr-2" />
            )}
            <span className={`font-medium ${
              data.success 
                ? 'text-green-800 dark:text-green-200' 
                : 'text-red-800 dark:text-red-200'
            }`}>
              {data.success ? '✅ Success' : '❌ Failed'}
            </span>
            {data.exit_code !== undefined && (
              <span className={`ml-2 text-sm ${
                data.success 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                (Exit code: {data.exit_code})
              </span>
            )}
          </div>
          {data.message && (
            <button
              onClick={() => handleCopyOutput(data.message, 'Status message')}
              className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${
                data.success
                  ? 'text-green-600 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-800 focus:ring-green-500'
                  : 'text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-800 focus:ring-red-500'
              }`}
              title="Copy status message"
            >
              <ClipboardDocumentIcon className="h-3 w-3 mr-1" />
              Copy
            </button>
          )}
        </div>
        {data.message && (
          <p className={`mt-2 ${
            data.success 
              ? 'text-green-700 dark:text-green-300' 
              : 'text-red-700 dark:text-red-300'
          }`}>
            {data.message}
          </p>
        )}
      </div>

      {/* Output Section */}
      {data.output && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Output:</h4>
            <button
              onClick={() => handleCopyOutput(data.output!, 'Output')}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
              title="Copy output to clipboard"
            >
              <ClipboardDocumentIcon className="h-3 w-3 mr-1" />
              Copy Output
            </button>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-3 border border-gray-200 dark:border-gray-700">
            <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-64">
              {data.output}
            </pre>
          </div>
        </div>
      )}

      {/* Error Section */}
      {data.error && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-red-700 dark:text-red-300">Error:</h4>
            <button
              onClick={() => handleCopyOutput(data.error!, 'Error')}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/20 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
              title="Copy error to clipboard"
            >
              <ClipboardDocumentIcon className="h-3 w-3 mr-1" />
              Copy Error
            </button>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 rounded-md p-3 border border-red-200 dark:border-red-800">
            <pre className="text-xs text-red-800 dark:text-red-200 whitespace-pre-wrap font-mono overflow-auto max-h-64">
              {data.error}
            </pre>
          </div>
        </div>
      )}

      {/* Parameters Section */}
      {showParameters && data.parameters && Object.keys(data.parameters).length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Parameters Used:</h4>
            <button
              onClick={() => handleCopyOutput(JSON.stringify(data.parameters, null, 2), 'Parameters')}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
              title="Copy parameters to clipboard"
            >
              <ClipboardDocumentIcon className="h-3 w-3 mr-1" />
              Copy Parameters
            </button>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-3 border border-gray-200 dark:border-gray-700">
            <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-32">
              {JSON.stringify(data.parameters, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Additional Info */}
      {data.test_script_path && (
        <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-md p-2 border border-gray-200 dark:border-gray-700">
          <span className="font-medium">Test Script:</span> {data.test_script_path}
        </div>
      )}

      {/* Toast Notification */}
      {copyToast && (
        <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg animate-pulse">
          {copyToast}
        </div>
      )}
    </div>
  );
};

export default TestOutput;
