import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { IndividualToolConfig, ScriptConfig, ToolParameter, TestResult, DependencyStatus } from '../types';
import { apiClient } from '../api';
import TestScriptEditor from './TestScriptEditor';
import TestOutput from './TestOutput';
import TagDropdown from './TagDropdown';

const ToolConfig: React.FC = () => {
  const { toolName } = useParams<{ toolName: string }>();
  const navigate = useNavigate();
  const [config, setConfig] = useState<IndividualToolConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [testParameters, setTestParameters] = useState<Record<string, any>>({});
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [showTestModal, setShowTestModal] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [dependencyStatus, setDependencyStatus] = useState<DependencyStatus | null>(null);
  const [isCheckingDeps, setIsCheckingDeps] = useState(false);
  const [showDepsModal, setShowDepsModal] = useState(false);

  const isNewTool = toolName === 'new';

  useEffect(() => {
    if (!isNewTool && toolName) {
      loadToolConfig(toolName);
    } else {
      // Initialize empty config for new tool
      setConfig({
        enabled: true,
        last_modified: new Date().toISOString(),
        auto_detected: false,
        tags: [],
        script_config: {
          name: '',
          description: '',
          script_path: '',
          script_type: 'python',
          requires_confirmation: true,
          parameters: [],
          interactive: false,
          wrapper_function: undefined,
          dependencies: [],
          examples: [],
          enabled: true,
        }
      });
      setIsLoading(false);
    }
  }, [toolName, isNewTool]);

  const loadToolConfig = async (name: string) => {
    try {
      const toolConfig = await apiClient.getTool(name);
      setConfig(toolConfig);
    } catch (error) {
      console.error('Failed to load tool config:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config || !toolName) return;

    setIsSaving(true);
    try {
      await apiClient.updateTool(toolName, config);
      navigate('/tools');
    } catch (error) {
      console.error('Failed to save tool config:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestTool = async () => {
    if (!toolName || isNewTool) return;

    setIsTesting(true);
    setTestResult(null);
    
    try {
      const result = await apiClient.testTool(toolName, testParameters);
      console.log('Test result:', result);
      setTestResult(result);
      setShowTestModal(true);
    } catch (error) {
      console.error('Test failed:', error);
      setTestResult({
        success: false,
        message: 'Test failed - network or server error',
        parameters: testParameters,
        error: error instanceof Error ? error.message : String(error)
      });
      setShowTestModal(true);
    } finally {
      setIsTesting(false);
    }
  };

  const updateScriptConfig = (field: keyof ScriptConfig, value: any) => {
    if (!config) return;
    
    setConfig({
      ...config,
      script_config: {
        ...config.script_config,
        [field]: value,
      }
    });
  };

  const updateTags = (newTags: string[]) => {
    if (!config) return;
    
    setConfig({
      ...config,
      tags: newTags,
    });
  };

  const addParameter = () => {
    if (!config) return;
    
    const newParam: ToolParameter = {
      name: '',
      type: 'string',
      description: '',
      required: true,
    };
    
    updateScriptConfig('parameters', [...config.script_config.parameters, newParam]);
  };

  const removeParameter = (index: number) => {
    if (!config) return;
    
    const params = [...config.script_config.parameters];
    params.splice(index, 1);
    updateScriptConfig('parameters', params);
  };

  const updateParameter = (index: number, field: keyof ToolParameter, value: any) => {
    if (!config) return;
    
    const params = [...config.script_config.parameters];
    params[index] = { ...params[index], [field]: value };
    updateScriptConfig('parameters', params);
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading tool configuration...</div>;
  }

  if (!config) {
    return <div className="text-center py-8">Tool not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {isNewTool ? 'Add New Tool' : `Configure ${toolName}`}
        </h1>
        <div className="flex flex-wrap gap-2">
          {!isNewTool && (
            <>
              <button
                onClick={handleTestTool}
                disabled={isTesting}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isTesting ? 'Testing...' : 'Test Tool'}
              </button>
              
              <button
                onClick={() => {
                  const configJson = JSON.stringify(config, null, 2);
                  const blob = new Blob([configJson], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${toolName}_config.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Export Config
              </button>
            </>
          )}
          
          {isNewTool && (
            <label className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 cursor-pointer">
              Import Config
              <input
                type="file"
                accept=".json"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      try {
                        const importedConfig = JSON.parse(event.target?.result as string);
                        setConfig(importedConfig);
                      } catch (error) {
                        alert('Invalid configuration file');
                      }
                    };
                    reader.readAsText(file);
                  }
                }}
              />
            </label>
          )}
          
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Configuration Templates (for new tools) */}
      {isNewTool && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Start Templates</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                 onClick={() => setConfig({
                   enabled: true,
                   last_modified: new Date().toISOString(),
                   auto_detected: false,
                   tags: ['data', 'processing'],
                   script_config: {
                     name: '',
                     description: 'Python script for data processing',
                     script_path: '',
                     script_type: 'python',
                     requires_confirmation: true,
                     parameters: [
                       { name: 'input_file', type: 'string', description: 'Input file path', required: true },
                       { name: 'output_file', type: 'string', description: 'Output file path', required: false }
                     ],
                     interactive: false,
                     wrapper_function: undefined,
                     dependencies: ['pandas', 'numpy'],
                     examples: ['python script.py input.csv output.csv'],
                     enabled: true,
                   }
                 })}>
              <h3 className="font-medium text-gray-900 dark:text-white">📊 Data Processing Script</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Template for Python data processing scripts with pandas/numpy
              </p>
            </div>
            
            <div className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                 onClick={() => setConfig({
                   enabled: true,
                   last_modified: new Date().toISOString(),
                   auto_detected: false,
                   tags: ['data', 'processing'],
                   script_config: {
                     name: '',
                     description: 'REST API client script',
                     script_path: '',
                     script_type: 'python',
                     requires_confirmation: false,
                     parameters: [
                       { name: 'url', type: 'string', description: 'API endpoint URL', required: true },
                       { name: 'method', type: 'string', description: 'HTTP method (GET, POST, etc.)', required: false }
                     ],
                     interactive: false,
                     wrapper_function: undefined,
                     dependencies: ['requests', 'json'],
                     examples: ['python api_client.py https://api.example.com/data GET'],
                     enabled: true,
                   }
                 })}>
              <h3 className="font-medium text-gray-900 dark:text-white">🌐 API Client Script</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Template for REST API client scripts with requests
              </p>
            </div>
            
            <div className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                 onClick={() => setConfig({
                   enabled: true,
                   last_modified: new Date().toISOString(),
                   auto_detected: false,
                   tags: ['shell', 'utility'],
                   script_config: {
                     name: '',
                     description: 'Shell utility script',
                     script_path: '',
                     script_type: 'shell',
                     requires_confirmation: true,
                     parameters: [
                       { name: 'target', type: 'string', description: 'Target file or directory', required: true }
                     ],
                     interactive: false,
                     wrapper_function: undefined,
                     dependencies: [],
                     examples: ['./script.sh /path/to/target'],
                     enabled: true,
                   }
                 })}>
              <h3 className="font-medium text-gray-900 dark:text-white">🔧 Shell Utility</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Template for shell scripts and system utilities
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Basic Information</h2>
        
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tool Name</label>
            <input
              type="text"
              value={config.script_config.name}
              onChange={(e) => updateScriptConfig('name', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Script Type</label>
            <select
              value={config.script_config.script_type}
              onChange={(e) => updateScriptConfig('script_type', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="python">Python</option>
              <option value="shell">Shell</option>
            </select>
          </div>

          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
            <textarea
              value={config.script_config.description}
              onChange={(e) => updateScriptConfig('description', e.target.value)}
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Script Path</label>
            <input
              type="text"
              value={config.script_config.script_path}
              onChange={(e) => updateScriptConfig('script_path', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>

        <div className="mt-4 space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config.enabled}
              onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
              className="h-4 w-4 text-indigo-600 rounded border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Enabled</span>
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config.script_config.requires_confirmation}
              onChange={(e) => updateScriptConfig('requires_confirmation', e.target.checked)}
              className="h-4 w-4 text-indigo-600 rounded border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Requires Confirmation</span>
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config.script_config.interactive}
              onChange={(e) => updateScriptConfig('interactive', e.target.checked)}
              className="h-4 w-4 text-indigo-600 rounded border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Interactive</span>
          </label>
        </div>
      </div>

      {/* Dependencies Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Dependencies</h2>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Python Dependencies
              </label>
              <button
                onClick={() => {
                  const newDep = prompt('Enter dependency name (e.g., requests, numpy):');
                  if (newDep && config) {
                    updateScriptConfig('dependencies', [...config.script_config.dependencies, newDep.trim()]);
                  }
                }}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Dependency
              </button>
            </div>
            
            <div className="space-y-2">
              {config.script_config.dependencies.map((dep, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={dep}
                    onChange={(e) => {
                      const deps = [...config.script_config.dependencies];
                      deps[index] = e.target.value;
                      updateScriptConfig('dependencies', deps);
                    }}
                    className="flex-1 border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="e.g., requests>=2.28.0"
                  />
                  <button
                    onClick={() => {
                      const deps = [...config.script_config.dependencies];
                      deps.splice(index, 1);
                      updateScriptConfig('dependencies', deps);
                    }}
                    className="px-2 py-1 text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                </div>
              ))}
              
              {config.script_config.dependencies.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  No dependencies configured. Add dependencies that your script requires.
                </p>
              )}
            </div>
            
            {!isNewTool && (
              <div className="mt-3">
                <button
                  onClick={async () => {
                    setIsCheckingDeps(true);
                    try {
                      const result = await apiClient.checkDependencies(toolName!);
                      setDependencyStatus(result);
                      setShowDepsModal(true);
                    } catch (error) {
                      console.error('Failed to check dependencies:', error);
                      setDependencyStatus({
                        tool_name: toolName!,
                        dependencies: config?.script_config.dependencies || [],
                        status: {},
                        missing: [],
                        all_available: false
                      });
                      alert('Failed to check dependencies. Please check the console for details.');
                    } finally {
                      setIsCheckingDeps(false);
                    }
                  }}
                  disabled={isCheckingDeps}
                  className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50"
                >
                  {isCheckingDeps ? 'Checking...' : 'Check Dependencies'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Parameters Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Parameters</h2>
          <button
            onClick={addParameter}
            className="px-3 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
          >
            Add Parameter
          </button>
        </div>

        <div className="space-y-4">
          {config.script_config.parameters.map((param, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-600 rounded p-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                  <input
                    type="text"
                    value={param.name}
                    onChange={(e) => updateParameter(index, 'name', e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
                  <select
                    value={param.type}
                    onChange={(e) => updateParameter(index, 'type', e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="string">String</option>
                    <option value="number">Number</option>
                    <option value="boolean">Boolean</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                  <input
                    type="text"
                    value={param.description}
                    onChange={(e) => updateParameter(index, 'description', e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>

              <div className="mt-2 flex justify-between items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={param.required}
                    onChange={(e) => updateParameter(index, 'required', e.target.checked)}
                    className="h-4 w-4 text-indigo-600 rounded border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Required</span>
                </label>

                <button
                  onClick={() => removeParameter(index)}
                  className="px-2 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Advanced Configuration Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Advanced Configuration</h2>
        
        <div className="space-y-4">
          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tags
            </label>
            <TagDropdown
              toolName={toolName || 'new'}
              currentTags={config.tags}
              onTagsChange={updateTags}
              className="w-full"
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Tags help organize and categorize tools. They can be searched in the tool list.
            </p>
          </div>

          {/* Examples */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Usage Examples
              </label>
              <button
                onClick={() => {
                  const example = prompt('Enter usage example:');
                  if (example && config) {
                    updateScriptConfig('examples', [...config.script_config.examples, example.trim()]);
                  }
                }}
                className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                Add Example
              </button>
            </div>
            <div className="space-y-2">
              {config.script_config.examples.map((example, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={example}
                    onChange={(e) => {
                      const examples = [...config.script_config.examples];
                      examples[index] = e.target.value;
                      updateScriptConfig('examples', examples);
                    }}
                    className="flex-1 border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
                    placeholder="e.g., python script.py --input data.csv"
                  />
                  <button
                    onClick={() => {
                      const examples = [...config.script_config.examples];
                      examples.splice(index, 1);
                      updateScriptConfig('examples', examples);
                    }}
                    className="px-2 py-1 text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                </div>
              ))}
              {config.script_config.examples.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  No examples configured. Add examples to help users understand how to use this tool.
                </p>
              )}
            </div>
          </div>

          {/* Wrapper Function */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Wrapper Function (Optional)
            </label>
            <input
              type="text"
              value={config.script_config.wrapper_function || ''}
              onChange={(e) => updateScriptConfig('wrapper_function', e.target.value || undefined)}
              className="block w-full border border-gray-300 rounded-md shadow-sm p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
              placeholder="e.g., custom_wrapper_function"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Optional function to wrap the tool execution for custom handling.
            </p>
          </div>
        </div>
      </div>

      {/* Tool Validation Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Tool Validation</h2>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="p-4 border rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Script Path</h3>
              <div className="flex items-center space-x-2">
                {config.script_config.script_path ? (
                  <span className="text-green-600">✅ Path specified</span>
                ) : (
                  <span className="text-red-600">❌ No path specified</span>
                )}
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Parameters</h3>
              <div className="flex items-center space-x-2">
                <span className={config.script_config.parameters.length > 0 ? "text-green-600" : "text-gray-500"}>
                  {config.script_config.parameters.length > 0 ? "✅" : "ℹ️"} {config.script_config.parameters.length} parameter(s)
                </span>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Dependencies</h3>
              <div className="flex items-center space-x-2">
                <span className={config.script_config.dependencies.length > 0 ? "text-green-600" : "text-gray-500"}>
                  {config.script_config.dependencies.length > 0 ? "✅" : "ℹ️"} {config.script_config.dependencies.length} dependency(ies)
                </span>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Documentation</h3>
              <div className="flex items-center space-x-2">
                <span className={config.script_config.description ? "text-green-600" : "text-yellow-600"}>
                  {config.script_config.description ? "✅" : "⚠️"} {config.script_config.description ? "Description provided" : "Missing description"}
                </span>
              </div>
            </div>
          </div>
          
          {!isNewTool && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h3 className="font-medium text-blue-900 dark:text-blue-200 mb-2">Quick Actions</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={async () => {
                    setIsCheckingDeps(true);
                    try {
                      const result = await apiClient.checkDependencies(toolName!);
                      setDependencyStatus(result);
                      setShowDepsModal(true);
                    } catch (error) {
                      console.error('Failed to check dependencies:', error);
                      alert('Failed to check dependencies. Please check the console for details.');
                    } finally {
                      setIsCheckingDeps(false);
                    }
                  }}
                  disabled={isCheckingDeps}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {isCheckingDeps ? 'Checking...' : 'Check Dependencies'}
                </button>
                
                <button
                  onClick={() => {
                    const requiredParams = config.script_config.parameters.filter(p => p.required);
                    const testParams: Record<string, any> = {};
                    
                    for (const param of requiredParams) {
                      const value = prompt(`Enter value for required parameter '${param.name}' (${param.description || param.type}):`);
                      if (value === null) return; // User cancelled
                      testParams[param.name] = param.type === 'number' ? parseFloat(value) : value;
                    }
                    
                    setTestParameters(testParams);
                    handleTestTool();
                  }}
                  className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Quick Test
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Test Parameters Section */}
      {!isNewTool && config.script_config.parameters.length > 0 && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Test Parameters</h2>
          <div className="space-y-4">
            {config.script_config.parameters.map((param) => (
              <div key={param.name} className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {param.name} {param.required && <span className="text-red-500">*</span>}
                </label>
                <input
                  type={param.type === 'number' ? 'number' : 'text'}
                  placeholder={param.description || `Enter ${param.name}`}
                  value={testParameters[param.name] || ''}
                  onChange={(e) => setTestParameters({
                    ...testParameters,
                    [param.name]: param.type === 'number' ? parseFloat(e.target.value) : e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test Script Editor Section */}
      {!isNewTool && toolName && config.script_config.script_type && (
        <TestScriptEditor 
          toolName={toolName} 
          toolScriptType={config.script_config.script_type as 'python' | 'shell'} 
        />
      )}

      {/* Dependency Status Modal */}
      {showDepsModal && dependencyStatus && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Dependency Check Results: {dependencyStatus.tool_name}
                </h3>
                <button
                  onClick={() => setShowDepsModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {/* Overall Status */}
                <div className={`p-4 rounded-lg ${dependencyStatus.all_available ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
                  <div className="flex items-center">
                    <span className={`font-medium ${dependencyStatus.all_available ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}`}>
                      {dependencyStatus.all_available ? '✅ All Dependencies Available' : '❌ Missing Dependencies Found'}
                    </span>
                  </div>
                  {!dependencyStatus.all_available && (
                    <p className="mt-2 text-red-700 dark:text-red-300">
                      Missing: {dependencyStatus.missing.join(', ')}
                    </p>
                  )}
                </div>

                {/* Detailed Status */}
                {dependencyStatus.dependencies.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-3">Detailed Status:</h4>
                    <div className="space-y-2">
                      {dependencyStatus.dependencies.map((dep) => {
                        const isAvailable = dependencyStatus.status[dep];
                        return (
                          <div key={dep} className="flex items-center justify-between p-3 border rounded-lg">
                            <span className="font-mono text-sm text-gray-900 dark:text-white">{dep}</span>
                            <span className={`font-medium ${isAvailable ? 'text-green-600' : 'text-red-600'}`}>
                              {isAvailable ? '✅ Available' : '❌ Missing'}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {dependencyStatus.dependencies.length === 0 && (
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-gray-600 dark:text-gray-300">
                      No dependencies configured for this tool.
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                {!dependencyStatus.all_available && (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Next Steps:</h4>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-3">
                      Install missing dependencies using pip:
                    </p>
                    <code className="block p-2 bg-gray-900 text-green-400 rounded text-sm font-mono">
                      pip install {dependencyStatus.missing.join(' ')}
                    </code>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end space-x-2">
                <button
                  onClick={() => setShowDepsModal(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Close
                </button>
                {!dependencyStatus.all_available && (
                  <button
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(`pip install ${dependencyStatus.missing.join(' ')}`);
                        alert('Install command copied to clipboard!');
                      } catch (error) {
                        console.error('Failed to copy to clipboard:', error);
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Copy Install Command
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Test Results Modal */}
      {showTestModal && testResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Test Results: {toolName}
                </h3>
                <button
                  onClick={() => setShowTestModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <TestOutput 
                  title={`Test Results: ${toolName}`}
                  data={testResult}
                  showParameters={true}
                />
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowTestModal(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolConfig;
