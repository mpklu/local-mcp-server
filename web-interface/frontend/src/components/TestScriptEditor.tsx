import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { 
  ChevronDownIcon, 
  ChevronRightIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  TrashIcon,
  ArrowUpTrayIcon,
  PlayIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../api';
import { TestScriptResponse } from '../types';
import TestOutput from './TestOutput';

interface TestScriptEditorProps {
  toolName: string;
  toolScriptType: 'python' | 'shell';
}

type ScriptType = 'python' | 'shell' | 'other';

const TestScriptEditor: React.FC<TestScriptEditorProps> = ({ toolName, toolScriptType }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [content, setContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [scriptType, setScriptType] = useState<ScriptType>(toolScriptType);
  const [exists, setExists] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any>(null);
  const [copyToast, setCopyToast] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getLanguageFromType = (type: ScriptType): string => {
    switch (type) {
      case 'python':
        return 'python';
      case 'shell':
        return 'shell';
      default:
        return 'plaintext';
    }
  };

  const getFileExtension = (type: ScriptType): string => {
    switch (type) {
      case 'python':
        return 'test.py';
      case 'shell':
        return 'test';
      default:
        return 'test';
    }
  };

  const getDefaultContent = (type: ScriptType): string => {
    if (type === 'python') {
      return `#!/usr/bin/env python3
"""
Test script for ${toolName} tool.
This script tests the functionality of the ${toolName} tool.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def test_${toolName.replace(/[^a-zA-Z0-9]/g, '_')}_basic():
    """Test basic functionality of the ${toolName} tool."""
    print(f"=== Testing {toolName} Tool ===")
    
    # Add your test logic here
    # Example:
    # result = subprocess.run([
    #     "uv", "--directory", "/path/to/local_mcp_server", 
    #     "run", "python3", "/path/to/tools/${toolName}/run.py",
    #     "your_test_arguments"
    # ], capture_output=True, text=True)
    
    # if result.returncode == 0:
    #     print("✅ Test passed!")
    #     return True
    # else:
    #     print(f"❌ Test failed: {result.stderr}")
    #     return False
    
    print("✅ Basic test template created")
    return True

def main():
    """Run all tests."""
    print(f"{toolName.charAt(0).toUpperCase() + toolName.slice(1)} Tool Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 1
    
    if test_${toolName.replace(/[^a-zA-Z0-9]/g, '_')}_basic():
        tests_passed += 1
    
    print(f"\\n=== Test Results ===")
    print(f"Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests*100):.1f}%")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
`;
    } else if (type === 'shell') {
      return `#!/bin/bash
# Test script for ${toolName} tool
# This script tests the functionality of the ${toolName} tool

set -e  # Exit on any error

echo "=== Testing ${toolName} tool ==="

# Test basic functionality
test_basic() {
    echo "Testing basic functionality..."
    
    # Add your test logic here
    # Example:
    # if /path/to/tools/${toolName}/run test_arguments; then
    #     echo "✅ Basic test passed"
    #     return 0
    # else
    #     echo "❌ Basic test failed"
    #     return 1
    # fi
    
    echo "✅ Basic test template created"
    return 0
}

# Run tests
echo "Running tests for ${toolName}..."
tests_passed=0
total_tests=1

if test_basic; then
    ((tests_passed++))
fi

echo ""
echo "=== Test Results ==="
echo "Passed: $tests_passed/$total_tests"
echo "Success Rate: $(( tests_passed * 100 / total_tests ))%"

if [ $tests_passed -eq $total_tests ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
`;
    } else {
      return `# Test script for ${toolName} tool
# Add your test logic here
echo "Test script for ${toolName}"
`;
    }
  };

  const loadTestScript = async () => {
    if (!isOpen) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response: TestScriptResponse = await apiClient.getTestScript(toolName);
      setExists(response.exists);
      setContent(response.content || '');
      setOriginalContent(response.content || '');
      
      if (response.exists && response.script_type) {
        setScriptType(response.script_type);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load test script');
      setExists(false);
      setContent('');
      setOriginalContent('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    if (!exists) {
      // Create new test script with default content
      const defaultContent = getDefaultContent(scriptType);
      setContent(defaultContent);
      setOriginalContent('');
    }
    setIsEditing(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    
    try {
      await apiClient.saveTestScript(toolName, content, scriptType);
      setExists(true);
      setOriginalContent(content);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save test script');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setContent(originalContent);
    setIsEditing(false);
    setError(null);
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this test script?')) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      await apiClient.deleteTestScript(toolName);
      setExists(false);
      setContent('');
      setOriginalContent('');
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete test script');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunTest = async () => {
    if (!exists) {
      setError('Please save the test script before running it');
      return;
    }
    
    setIsRunning(true);
    setError(null);
    setTestResult(null);
    
    try {
      const result = await apiClient.runTestScript(toolName);
      setTestResult(result);
      
      if (!result.success) {
        setError(result.message || 'Test execution failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run test script');
      setTestResult({
        success: false,
        message: 'Error executing test script',
        output: err instanceof Error ? err.message : 'Unknown error',
        has_test_script: true
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopyToast('Content copied to clipboard!');
      setTimeout(() => setCopyToast(null), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyToast('Failed to copy to clipboard');
      setTimeout(() => setCopyToast(null), 2000);
    }
  };

  const handleUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const fileContent = e.target?.result as string;
      setContent(fileContent);
      
      // Auto-detect script type from file extension
      const fileName = file.name.toLowerCase();
      if (fileName.endsWith('.py')) {
        setScriptType('python');
      } else if (fileName.endsWith('.sh') || fileName.endsWith('.bash')) {
        setScriptType('shell');
      } else {
        setScriptType('other');
      }
      
      if (!isEditing) {
        setIsEditing(true);
      }
    };
    
    reader.onerror = () => {
      setError('Failed to read file');
    };
    
    reader.readAsText(file);
    
    // Clear the input value so the same file can be uploaded again
    event.target.value = '';
  };

  const handleScriptTypeChange = (newType: ScriptType) => {
    setScriptType(newType);
  };

  useEffect(() => {
    loadTestScript();
  }, [isOpen, toolName]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
      >
        <div className="flex items-center space-x-2">
          {isOpen ? (
            <ChevronDownIcon className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRightIcon className="h-5 w-5 text-gray-500" />
          )}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Test Script
          </h3>
          {exists && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              {getFileExtension(scriptType)} exists
            </span>
          )}
          {!exists && isOpen && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
              No test script
            </span>
          )}
        </div>
      </button>

      {/* Content */}
      {isOpen && (
        <div className="px-4 pb-4 space-y-4">
          {/* Script Type Selector */}
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Type:
            </span>
            <div className="flex space-x-2">
              {(['python', 'shell', 'other'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => handleScriptTypeChange(type)}
                  disabled={!isEditing}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    scriptType === type
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  } ${!isEditing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Editor */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-900 rounded-md">
              <div className="text-gray-500 dark:text-gray-400">Loading...</div>
            </div>
          ) : (
            <div className="border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden">
              {/* Editor Toolbar */}
              <div className="flex items-center justify-between px-3 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                    {getFileExtension(scriptType)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-500">
                    {content.split('\n').length} lines • {content.length} chars
                  </span>
                  {exists && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      Saved
                    </span>
                  )}
                  {isEditing && !exists && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                      Unsaved
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  {content && (
                    <button
                      onClick={handleCopyToClipboard}
                      className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
                      title="Copy to clipboard"
                    >
                      <DocumentDuplicateIcon className="h-3 w-3 mr-1" />
                      Copy
                    </button>
                  )}
                  {!isEditing && content && (
                    <button
                      onClick={() => {
                        const blob = new Blob([content], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = getFileExtension(scriptType);
                        a.click();
                        URL.revokeObjectURL(url);
                        setCopyToast('File downloaded!');
                        setTimeout(() => setCopyToast(null), 2000);
                      }}
                      className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
                      title="Download file"
                    >
                      <ArrowUpTrayIcon className="h-3 w-3 mr-1 rotate-180" />
                      Download
                    </button>
                  )}
                  {isEditing && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Editing...
                    </span>
                  )}
                </div>
              </div>
              
              {/* Monaco Editor */}
              <Editor
                height="400px"
                language={getLanguageFromType(scriptType)}
                value={content}
                onChange={(value) => setContent(value || '')}
                options={{
                  readOnly: !isEditing,
                  minimap: { enabled: false },
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  fontSize: 14,
                  wordWrap: 'on',
                  theme: 'vs-dark', // You can make this configurable
                }}
                theme="vs-dark"
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <>
                <button
                  onClick={handleEdit}
                  disabled={isLoading}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <PencilIcon className="h-4 w-4 mr-1" />
                  {exists ? 'Edit' : 'Create'}
                </button>
                <button
                  onClick={handleUpload}
                  disabled={isLoading}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <ArrowUpTrayIcon className="h-4 w-4 mr-1" />
                  Upload
                </button>
                {exists && (
                  <button
                    onClick={handleRunTest}
                    disabled={isLoading || isRunning}
                    className="inline-flex items-center px-3 py-2 border border-green-300 dark:border-green-600 shadow-sm text-sm leading-4 font-medium rounded-md text-green-700 dark:text-green-400 bg-white dark:bg-gray-800 hover:bg-green-50 dark:hover:bg-green-900/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                  >
                    <PlayIcon className="h-4 w-4 mr-1" />
                    {isRunning ? 'Running...' : 'Run Test'}
                  </button>
                )}
                {exists && (
                  <button
                    onClick={handleDelete}
                    disabled={isLoading}
                    className="inline-flex items-center px-3 py-2 border border-red-300 dark:border-red-600 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 dark:text-red-400 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                  >
                    <TrashIcon className="h-4 w-4 mr-1" />
                    Delete
                  </button>
                )}
              </>
            ) : (
              <>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <CheckIcon className="h-4 w-4 mr-1" />
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <XMarkIcon className="h-4 w-4 mr-1" />
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={isSaving}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <ArrowUpTrayIcon className="h-4 w-4 mr-1" />
                  Upload
                </button>
              </>
            )}
          </div>

          {/* Test Output Section */}
          {testResult && (
            <div className="mt-4">
              <TestOutput 
                title="Test Results"
                data={testResult}
                showParameters={false}
              />
            </div>
          )}

          {/* Toast Notification */}
          {copyToast && (
            <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg">
              {copyToast}
            </div>
          )}

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".py,.sh,.bash,*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      )}
    </div>
  );
};

export default TestScriptEditor;
