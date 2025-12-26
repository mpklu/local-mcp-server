import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FolderPlusIcon,
  ArrowUpTrayIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  TrashIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { HelpIcon } from './Tooltip';
import { apiClient } from '../api';
import { ToolParameter } from '../types';
import TestScriptEditor from './TestScriptEditor';

interface AddToolWizardProps {}

type WizardStep = 'method' | 'structure' | 'configure' | 'test' | 'complete';

const AddToolWizard: React.FC<AddToolWizardProps> = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<WizardStep>('method');
  const [selectedMethod, setSelectedMethod] = useState<'manual' | 'import' | null>(null);
  const [toolData, setToolData] = useState({
    name: '',
    description: 'A sample text processing tool that demonstrates various MCP tool features.',
    scriptType: 'python' as 'python' | 'shell',
    hasExistingScript: false,
    scriptPath: '',
  });
  const [parameters, setParameters] = useState<ToolParameter[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [createdToolName, setCreatedToolName] = useState<string>('');
  const [creationError, setCreationError] = useState<string>('');

  const steps = [
    { id: 'method', title: 'Choose Method', description: 'How do you want to add your tool?' },
    { id: 'structure', title: 'Tool Structure', description: 'Set up the tool structure' },
    { id: 'configure', title: 'Configuration', description: 'Configure tool settings' },
    { id: 'test', title: 'Testing', description: 'Create and test your tool' },
    { id: 'complete', title: 'Complete', description: 'Tool successfully added' },
  ];

  const getCurrentStepIndex = () => steps.findIndex(step => step.id === currentStep);

  const renderMethodSelection = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          How would you like to add your tool?
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Choose the method that best fits your situation
        </p>
        <div className="inline-flex items-center px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-sm font-medium">
          <CheckCircleIcon className="h-4 w-4 mr-2" />
          Both methods provide a working template tool immediately
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Manual Creation */}
        <button 
          className={`relative rounded-lg border-2 p-6 text-left transition-all ${
            selectedMethod === 'manual' 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }`}
          onClick={() => setSelectedMethod('manual')}
        >
          <div className="flex items-center">
            <FolderPlusIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Create New Tool
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Get a complete, working text processing tool template
              </p>
            </div>
          </div>
          
          <div className="mt-4 space-y-2">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>Ready-to-use template</strong> with 4 operations
            </div>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>Complete test suite</strong> included
            </div>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>Documentation & examples</strong> generated
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-md">
            <div className="text-xs text-blue-800 dark:text-blue-200">
              <p><strong>🎯 What you'll get:</strong> A functional tool that processes text with uppercase, lowercase, reverse, and word count operations - perfect for learning or as a starting point!</p>
            </div>
          </div>

          <div className="mt-3 p-3 bg-gray-100 dark:bg-gray-800 rounded-md">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              <strong>Best for:</strong> First-time users, learning the system, quick prototyping
            </p>
          </div>
        </button>

        {/* Import Existing */}
        <button 
          className={`relative rounded-lg border-2 p-6 text-left transition-all ${
            selectedMethod === 'import' 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }`}
          onClick={() => setSelectedMethod('import')}
        >
          <div className="flex items-center">
            <ArrowUpTrayIcon className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Import Existing Tool
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Convert your existing script into a template-based tool
              </p>
            </div>
          </div>
          
          <div className="mt-4 space-y-2">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>Your script + template structure</strong>
            </div>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>Auto-generated documentation</strong>
            </div>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
              <strong>MCP integration</strong> ready
            </div>
          </div>

          <div className="mt-4 p-3 bg-purple-100 dark:bg-purple-900/30 rounded-md">
            <div className="text-xs text-purple-800 dark:text-purple-200">
              <p><strong>🔄 What happens:</strong> Your existing script becomes the template foundation, we add proper structure, documentation, and MCP compatibility!</p>
            </div>
          </div>

          <div className="mt-3 p-3 bg-gray-100 dark:bg-gray-800 rounded-md">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              <strong>Best for:</strong> Existing scripts, migration projects, preserving custom logic
            </p>
          </div>
        </button>
      </div>

      {/* Information Panel */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
        <div className="flex items-start">
          <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-3" />
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              Tool Structure Requirements
            </h4>
            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p>• Tools must be placed in the <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">tools/</code> directory</p>
              <p>• <strong>REQUIRED:</strong> All tools must have <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">run.sh</code> as universal entry point</p>
              <p>• Copy template: <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">tools/TEMPLATE/run.sh</code></p>
              <p>• Each tool manages its own virtual environment and dependencies</p>
            </div>
            <div className="mt-3">
              <a 
                href="/help" 
                target="_blank"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm inline-flex items-center"
              >
                <span className="mr-1">📖</span> View full documentation
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStructureGuide = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {selectedMethod === 'manual' ? 'Configure Your Text Processing Tool' : 'Configure Import Settings'}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {selectedMethod === 'manual' 
            ? 'Customize the template tool settings - you\'ll get a working tool with these features immediately'
            : 'Set up your existing script with proper MCP integration structure'
          }
        </p>
      </div>

      {selectedMethod === 'manual' ? (
        <div className="space-y-6">
          {/* Tool Basic Info */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Basic Information
            </h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="tool-name" className="flex items-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tool Name
                  <span className="ml-2">
                    <HelpIcon 
                      content="Use lowercase letters, numbers, and hyphens only. This will be your tool's directory name."
                      position="right"
                    />
                  </span>
                </label>
                <input
                  id="tool-name"
                  type="text"
                  value={toolData.name}
                  onChange={(e) => setToolData({...toolData, name: e.target.value})}
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="e.g., my-awesome-tool"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Use lowercase with hyphens. This will be your tool's directory name.
                </p>
              </div>
              
              <div>
                <label htmlFor="tool-description" className="flex items-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description
                  <span className="ml-2">
                    <HelpIcon 
                      content="This will be used in documentation and tool listings. You can change it later."
                      position="right"
                    />
                  </span>
                </label>
                <textarea
                  id="tool-description"
                  value={toolData.description}
                  onChange={(e) => setToolData({...toolData, description: e.target.value})}
                  rows={3}
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="A sample text processing tool that demonstrates various MCP tool features."
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  💡 Pre-filled with template description - feel free to customize or keep as-is for your first tool
                </p>
              </div>

              <div>
                <span className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Script Type
                </span>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setToolData({...toolData, scriptType: 'python'})}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      toolData.scriptType === 'python'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <span className="text-2xl">🐍</span>
                      <div className="mt-2 font-medium">Python</div>
                      <div className="text-xs text-gray-500">run.sh → main.py</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setToolData({...toolData, scriptType: 'shell'})}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      toolData.scriptType === 'shell'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <span className="text-2xl">🐚</span>
                      <div className="mt-2 font-medium">Shell</div>
                      <div className="text-xs text-gray-500">run.sh wrapper</div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Template Preview */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg p-6 border border-green-200 dark:border-green-700">
            <div className="flex items-center mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-400 mr-2" />
              <h4 className="font-medium text-gray-900 dark:text-white">
                🎯 Your Template Tool Will Include
              </h4>
            </div>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center text-gray-700 dark:text-gray-300">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  <strong>Text Processing Operations:</strong>
                </div>
                <div className="ml-4 space-y-1 text-gray-600 dark:text-gray-400">
                  <div>• Uppercase conversion</div>
                  <div>• Lowercase conversion</div>
                  <div>• Text reversal</div>
                  <div>• Word counting</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-gray-700 dark:text-gray-300">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  <strong>Professional Features:</strong>
                </div>
                <div className="ml-4 space-y-1 text-gray-600 dark:text-gray-400">
                  <div>• Command-line interface</div>
                  <div>• File output support</div>
                  <div>• Comprehensive test suite</div>
                  <div>• Usage documentation</div>
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white/50 dark:bg-gray-800/50 rounded-md">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                💡 <strong>Pro tip:</strong> This template is fully functional and ready to use immediately. You can test it, modify it, or use it as a learning reference for creating other tools!
              </p>
            </div>
          </div>

          {/* Directory Structure Preview */}
          {toolData.name && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <h4 className="font-medium text-gray-900 dark:text-white mb-4">
                📁 Directory Structure Preview
              </h4>
              <div className="font-mono text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <div>tools/</div>
                <div className="ml-4">└── {toolData.name}/</div>
                <div className="ml-8">├── run.sh <span className="text-green-600 dark:text-green-400">(universal entry point)</span></div>
                <div className="ml-8">├── {toolData.scriptType === 'python' ? 'main.py' : 'script.sh'} <span className="text-green-600 dark:text-green-400">(tool logic)</span></div>
                <div className="ml-8">├── {toolData.scriptType === 'python' ? 'requirements.txt' : 'README.md'} <span className="text-blue-600 dark:text-blue-400">(dependencies)</span></div>
                <div className="ml-8">└── README.md <span className="text-gray-500">(documentation)</span></div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Import existing tool interface */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Locate Your Tool
            </h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="script-path" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tool Directory or Script Path
                </label>
                <input
                  id="script-path"
                  type="text"
                  value={toolData.scriptPath}
                  onChange={(e) => setToolData({...toolData, scriptPath: e.target.value})}
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="/path/to/your/script.py or /path/to/tool/directory"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  We'll analyze your tool and help migrate it to the standard structure.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Parameter management functions
  const addParameter = () => {
    setParameters([...parameters, {
      name: '',
      type: 'string',
      description: '',
      required: true
    }]);
  };

  const updateParameter = (index: number, field: keyof ToolParameter, value: any) => {
    const updated = parameters.map((param, i) => 
      i === index ? { ...param, [field]: value } : param
    );
    setParameters(updated);
  };

  const removeParameter = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  // Tool creation function
  const createTool = async () => {
    setIsCreating(true);
    setCreationError('');
    
    try {
      const response = await apiClient.createTool({
        name: toolData.name,
        description: toolData.description,
        script_type: toolData.scriptType,
        method: selectedMethod!,
        script_path: selectedMethod === 'import' ? toolData.scriptPath : undefined,
        parameters: parameters
      });
      
      if (response.success) {
        setCreatedToolName(toolData.name.toLowerCase().replace(/[^a-z0-9]/g, '-'));
        
        // Auto-rebuild tools.json
        await apiClient.buildToolsJson();
        
        setCurrentStep('complete');
      } else {
        setCreationError(response.message || 'Failed to create tool');
      }
    } catch (error) {
      setCreationError(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setIsCreating(false);
    }
  };

  const renderConfigurationStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Configure Tool Parameters
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Define the parameters your tool accepts (optional but recommended)
        </p>
      </div>

      {/* Parameters Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Parameters</h3>
          <button
            onClick={addParameter}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Add Parameter
          </button>
        </div>

        {parameters.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <InformationCircleIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No parameters defined yet.</p>
            <p className="text-sm">Add parameters to make your tool more flexible.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {parameters.map((param, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      value={param.name}
                      onChange={(e) => updateParameter(index, 'name', e.target.value)}
                      placeholder="parameter_name"
                      className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Type
                    </label>
                    <select
                      value={param.type}
                      onChange={(e) => updateParameter(index, 'type', e.target.value)}
                      className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    >
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Description
                    </label>
                    <input
                      type="text"
                      value={param.description}
                      onChange={(e) => updateParameter(index, 'description', e.target.value)}
                      placeholder="What this parameter does..."
                      className="w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    />
                  </div>
                </div>

                <div className="mt-3 flex justify-between items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={param.required}
                      onChange={(e) => updateParameter(index, 'required', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Required parameter</span>
                  </label>

                  <button
                    onClick={() => removeParameter(index)}
                    className="inline-flex items-center px-2 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors"
                  >
                    <TrashIcon className="w-4 h-4 mr-1" />
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Configuration Summary */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
        <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
          📋 Configuration Summary
        </h4>
        <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
          <p><strong>Tool Name:</strong> {toolData.name || 'Not set'}</p>
          <p><strong>Description:</strong> {toolData.description || 'Not set'}</p>
          <p><strong>Script Type:</strong> {toolData.scriptType}</p>
          <p><strong>Method:</strong> {selectedMethod}</p>
          <p><strong>Parameters:</strong> {parameters.length} defined</p>
          {selectedMethod === 'import' && toolData.scriptPath && (
            <p><strong>Source:</strong> {toolData.scriptPath}</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderTestingStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Create and Test Your Tool
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Click "Create Tool" to generate the files, then test your tool
        </p>
      </div>

      {/* Create Tool Section */}
      {!createdToolName && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="text-center">
            <div className="mb-4">
              <FolderPlusIcon className="w-16 h-16 mx-auto text-blue-500" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Ready to Create Tool
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              This will create the directory structure and template files for your tool.
            </p>
            
            {creationError && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-md">
                <p className="text-red-800 dark:text-red-200 text-sm">{creationError}</p>
              </div>
            )}
            
            <button
              onClick={createTool}
              disabled={isCreating}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isCreating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Creating Tool...
                </>
              ) : (
                <>
                  <FolderPlusIcon className="w-5 h-5 mr-2" />
                  Create Tool
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Test Script Editor */}
      {createdToolName && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="mb-4">
            <div className="flex items-center mb-2">
              <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Tool Created Successfully!
              </h3>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Your tool has been created. You can now test it using the editor below.
            </p>
          </div>
          
          <TestScriptEditor 
            toolName={createdToolName}
            toolScriptType={toolData.scriptType as 'python' | 'shell'}
          />
        </div>
      )}
    </div>
  );

  const renderCompletionStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="mb-6">
          <CheckCircleIcon className="w-20 h-20 mx-auto text-green-500" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          {selectedMethod === 'manual' ? 'Template Tool Created!' : 'Tool Successfully Imported!'}
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
          {selectedMethod === 'manual' 
            ? `Your working text processing tool "${toolData.name}" is ready to use immediately!`
            : `Your tool "${toolData.name}" has been successfully integrated with MCP structure.`
          }
        </p>
        {selectedMethod === 'manual' && (
          <div className="inline-flex items-center px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-sm font-medium">
            <CheckCircleIcon className="h-4 w-4 mr-2" />
            Fully functional template with 4 text operations included
          </div>
        )}
      </div>

      {/* Summary Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          📊 Tool Summary
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Basic Information</h4>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div><strong>Name:</strong> {toolData.name}</div>
              <div><strong>Type:</strong> {toolData.scriptType}</div>
              <div><strong>Method:</strong> {selectedMethod}</div>
              <div><strong>Directory:</strong> tools/{createdToolName}/</div>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Configuration</h4>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div><strong>Parameters:</strong> {parameters.length} defined</div>
              <div><strong>Status:</strong> <span className="text-green-600">Active</span></div>
              <div><strong>Auto-rebuild:</strong> <span className="text-green-600">Completed</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-700">
        <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-4">
          {selectedMethod === 'manual' ? '� Your Template Tool is Ready!' : '�🎉 What\'s Next?'}
        </h3>
        <div className="space-y-3 text-blue-800 dark:text-blue-200">
          {selectedMethod === 'manual' ? (
            <>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Try it now with Claude</p>
                  <p className="text-sm opacity-90">Ask Claude to "process text using {toolData.name}" - it can uppercase, lowercase, reverse text, or count words!</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Explore the generated code</p>
                  <p className="text-sm opacity-90">Check tools/{createdToolName}/ for complete Python/Shell code, tests, and documentation.</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Customize or create new tools</p>
                  <p className="text-sm opacity-90">Use this template as a reference to build your own tools or modify it for your needs.</p>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Your tool is now available in the MCP system</p>
                  <p className="text-sm opacity-90">Claude can now use your imported tool with proper structure and documentation.</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Tool files have been organized</p>
                  <p className="text-sm opacity-90">Check the tools/{createdToolName}/ directory for your imported script and generated documentation.</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-medium">Configuration is complete</p>
                  <p className="text-sm opacity-90">The tools.json has been automatically rebuilt.</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => navigate('/tools?newTool=' + encodeURIComponent(toolData.name))}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center"
        >
          <span className="mr-2">👀</span>
          {selectedMethod === 'manual' ? 'View Template Tool' : 'View All Tools'}
        </button>
        <button
          onClick={() => navigate('/?newTool=' + encodeURIComponent(toolData.name))}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors flex items-center"
        >
          <span className="mr-2">🏠</span>
          Go to Dashboard
        </button>
        {selectedMethod === 'manual' && (
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center"
          >
            <span className="mr-2">➕</span>
            Create Another Tool
          </button>
        )}
      </div>
    </div>
  );

  const renderStepContent = () => {
    switch (currentStep) {
      case 'method':
        return renderMethodSelection();
      case 'structure':
        return renderStructureGuide();
      case 'configure':
        return renderConfigurationStep();
      case 'test':
        return renderTestingStep();
      case 'complete':
        return renderCompletionStep();
      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 'method':
        return selectedMethod !== null;
      case 'structure':
        return selectedMethod === 'manual' 
          ? toolData.name.trim() !== '' && toolData.description.trim() !== ''
          : toolData.scriptPath.trim() !== '';
      case 'configure':
        return true; // Configuration step is optional
      case 'test':
        return createdToolName !== ''; // Tool must be created to proceed
      case 'complete':
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1].id as WizardStep);
    }
  };

  const handlePrevious = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].id as WizardStep);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Add New Tool
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Follow our guided wizard to add your tool to the MCP system
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                getCurrentStepIndex() >= index
                  ? 'border-blue-500 bg-blue-500 text-white'
                  : 'border-gray-300 dark:border-gray-600 text-gray-500'
              }`}>
                {getCurrentStepIndex() > index ? (
                  <CheckCircleIcon className="w-5 h-5" />
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>
              <div className="ml-2 hidden sm:block">
                <div className={`text-sm font-medium ${
                  getCurrentStepIndex() >= index
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {step.description}
                </div>
              </div>
              {index < steps.length - 1 && (
                <ChevronRightIcon className="w-5 h-5 text-gray-400 mx-4" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        {renderStepContent()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={handlePrevious}
          disabled={getCurrentStepIndex() === 0}
          className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeftIcon className="w-4 h-4 mr-2" />
          Previous
        </button>

        <div className="flex space-x-3">
          <button
            onClick={() => navigate('/tools')}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
          
          {getCurrentStepIndex() < steps.length - 1 ? (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRightIcon className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={() => navigate('/tools')}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
            >
              <CheckCircleIcon className="w-4 h-4 mr-2" />
              Complete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddToolWizard;
