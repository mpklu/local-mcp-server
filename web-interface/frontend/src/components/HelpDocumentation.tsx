import React, { useState } from 'react';
import { 
  BookOpenIcon,
  CodeBracketIcon,
  FolderIcon,
  PlayIcon,
  CogIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChevronRightIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';

interface HelpDocumentationProps {}

interface HelpSection {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  content: React.ReactNode;
}

const HelpDocumentation: React.FC<HelpDocumentationProps> = () => {
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
    setActiveSection(sectionId);
  };

  const sections: HelpSection[] = [
    {
      id: 'overview',
      title: 'Project Overview',
      icon: BookOpenIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              What is the Local MCP System?
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The Local Model Context Protocol (MCP) system is a standardized framework for managing and executing tools. 
              It provides a unified interface for running scripts, managing dependencies, and testing functionality across 
              different programming languages and environments.
            </p>
            <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Key Benefits</h4>
                  <ul className="mt-2 text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Standardized tool structure and execution</li>
                    <li>• Automatic dependency management</li>
                    <li>• Built-in testing and validation</li>
                    <li>• Web-based configuration interface</li>
                    <li>• Support for Python and Shell scripts</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              System Architecture
            </h3>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="font-mono text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <div>📁 local_mcp/</div>
                <div className="ml-4">├── 🔧 local_mcp_server/ <span className="text-gray-500"># Core MCP server</span></div>
                <div className="ml-4">├── 🌐 web_config/ <span className="text-gray-500"># Web interface</span></div>
                <div className="ml-4">├── 🛠️ tools/ <span className="text-gray-500"># Your tools go here</span></div>
                <div className="ml-4">└── 🧪 tests/ <span className="text-gray-500"># System tests</span></div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'tool-structure',
      title: 'Tool Structure Requirements',
      icon: FolderIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Standard Tool Directory Structure
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Every tool must follow a standardized directory structure to be recognized by the MCP system.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Python Tools */}
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-3 flex items-center">
                  <span className="text-xl mr-2">🐍</span> Python Tools
                </h4>
                <div className="font-mono text-sm text-green-800 dark:text-green-200 space-y-1">
                  <div>tools/your-tool-name/</div>
                  <div className="ml-4">├── <strong>run.py</strong> <span className="text-green-600 dark:text-green-400"># Required entry point</span></div>
                  <div className="ml-4">├── test.py <span className="text-green-600 dark:text-green-400"># Optional test script</span></div>
                  <div className="ml-4">├── requirements.txt <span className="text-green-600 dark:text-green-400"># Optional dependencies</span></div>
                  <div className="ml-4">└── README.md <span className="text-green-600 dark:text-green-400"># Optional Documentation</span></div>
                </div>
              </div>

              {/* Shell Tools */}
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-3 flex items-center">
                  <span className="text-xl mr-2">🐚</span> Shell Tools
                </h4>
                <div className="font-mono text-sm text-purple-800 dark:text-purple-200 space-y-1">
                  <div>tools/your-tool-name/</div>
                  <div className="ml-4">├── <strong>run</strong> <span className="text-purple-600 dark:text-purple-400"># Required executable script</span></div>
                  <div className="ml-4">├── test <span className="text-purple-600 dark:text-purple-400"># Optional test script</span></div>
                  <div className="ml-4">├── requirements.txt <span className="text-purple-600 dark:text-purple-400"># Optional dependencies</span></div>
                  <div className="ml-4">└── README.md <span className="text-purple-600 dark:text-purple-400"># Optional Documentation</span></div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Entry Point Requirements
            </h3>
            <div className="space-y-4">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Critical Requirements</h4>
                    <ul className="mt-2 text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
                      <li>• Python tools MUST have a <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">run.py</code> file</li>
                      <li>• Shell tools MUST have an executable <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">run</code> script</li>
                      <li>• Entry points should handle command-line arguments</li>
                      <li>• Scripts should return appropriate exit codes (0 = success, non-zero = error)</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'creating-tools',
      title: 'Creating New Tools',
      icon: CodeBracketIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step-by-Step Guide
            </h3>
            
            <div className="space-y-6">
              {/* Step 1 */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  1
                </div>
                <div className="ml-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Create Tool Directory</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Create a new directory under <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">tools/</code> with a descriptive name using lowercase and hyphens.
                  </p>
                  <div className="mt-2 bg-gray-100 dark:bg-gray-800 rounded-md p-3">
                    <code className="text-sm text-gray-800 dark:text-gray-200">mkdir tools/my-awesome-tool</code>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  2
                </div>
                <div className="ml-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Create Entry Point</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Create the main entry point script for your tool.
                  </p>
                  
                  <div className="mt-3 space-y-3">
                    {/* Python Example */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-800 dark:text-gray-200">Python Example (run.py):</h5>
                      <div className="mt-1 bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                        <pre className="text-sm text-gray-800 dark:text-gray-200">
{`#!/usr/bin/env python3
"""
My Awesome Tool - Description of what it does
"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='My awesome tool')
    parser.add_argument('--input', help='Input parameter')
    parser.add_argument('--output', help='Output parameter')
    
    args = parser.parse_args()
    
    # Your tool logic here
    print(f"Processing input: {args.input}")
    print(f"Output will be saved to: {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())`}
                        </pre>
                      </div>
                    </div>

                    {/* Shell Example */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-800 dark:text-gray-200">Shell Example (run):</h5>
                      <div className="mt-1 bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                        <pre className="text-sm text-gray-800 dark:text-gray-200">
{`#!/bin/bash
# My Awesome Tool - Description of what it does

set -e  # Exit on any error

# Parse command line arguments
INPUT=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Your tool logic here
echo "Processing input: $INPUT"
echo "Output will be saved to: $OUTPUT"

exit 0`}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  3
                </div>
                <div className="ml-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Make Script Executable (Shell only)</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    For shell scripts, ensure the run script is executable.
                  </p>
                  <div className="mt-2 bg-gray-100 dark:bg-gray-800 rounded-md p-3">
                    <code className="text-sm text-gray-800 dark:text-gray-200">chmod +x tools/my-awesome-tool/run</code>
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  4
                </div>
                <div className="ml-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Add to MCP Configuration</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Use the web interface to configure your tool or manually add it to the configuration files.
                  </p>
                  <div className="mt-2 flex items-center text-blue-600 dark:text-blue-400 text-sm">
                    <ChevronRightIcon className="h-4 w-4 mr-1" />
                    Go to Tools → Add Tool in the web interface
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'testing',
      title: 'Testing Tools',
      icon: PlayIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Creating Test Scripts
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Test scripts are optional but highly recommended. They help validate that your tool works correctly and can be used for automated testing.
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Python Test */}
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-3">Python Test (test.py)</h4>
                <div className="bg-green-100 dark:bg-green-900/40 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-green-800 dark:text-green-200">
{`#!/usr/bin/env python3
"""
Test script for my-awesome-tool
"""
import subprocess
import sys
import tempfile
import os

def test_basic_functionality():
    """Test basic tool functionality"""
    try:
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test data")
            test_file = f.name
        
        # Run the tool
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'run.py'),
            '--input', test_file,
            '--output', '/tmp/test_output'
        ], capture_output=True, text=True)
        
        # Clean up
        os.unlink(test_file)
        
        # Check result
        if result.returncode == 0:
            print("✅ Basic functionality test passed")
            return True
        else:
            print(f"❌ Test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("Running tests for my-awesome-tool...")
    
    tests_passed = 0
    total_tests = 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    print(f"\\nResults: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())`}
                  </pre>
                </div>
              </div>

              {/* Shell Test */}
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-3">Shell Test (test)</h4>
                <div className="bg-purple-100 dark:bg-purple-900/40 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-purple-800 dark:text-purple-200">
{`#!/bin/bash
# Test script for my-awesome-tool

set -e

SCRIPT_DIR="$(cd "$(dirname "$\{BASH_SOURCE[0]}")" && pwd)"
TOOL_SCRIPT="$SCRIPT_DIR/run"

test_basic_functionality() {
    echo "Testing basic functionality..."
    
    # Create test data
    TEST_FILE=$(mktemp)
    echo "test data" > "$TEST_FILE"
    
    # Run the tool
    if "$TOOL_SCRIPT" --input "$TEST_FILE" --output "/tmp/test_output"; then
        echo "✅ Basic functionality test passed"
        rm -f "$TEST_FILE"
        return 0
    else
        echo "❌ Basic functionality test failed"
        rm -f "$TEST_FILE"
        return 1
    fi
}

main() {
    echo "Running tests for my-awesome-tool..."
    
    TESTS_PASSED=0
    TOTAL_TESTS=1
    
    if test_basic_functionality; then
        ((TESTS_PASSED++))
    fi
    
    echo ""
    echo "Results: $TESTS_PASSED/$TOTAL_TESTS tests passed"
    
    if [ "$TESTS_PASSED" -eq "$TOTAL_TESTS" ]; then
        echo "🎉 All tests passed!"
        exit 0
    else
        echo "💥 Some tests failed!"
        exit 1
    fi
}

main "$@"`}
                  </pre>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Running Tests
            </h3>
            <div className="space-y-3">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Web Interface</h4>
                <p className="text-blue-800 dark:text-blue-200 text-sm">
                  Use the built-in test runner in the web interface to execute and view test results with detailed output.
                </p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Command Line</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Python:</span>
                    <code className="ml-2 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">python tools/my-tool/test.py</code>
                  </div>
                  <div>
                    <span className="font-medium">Shell:</span>
                    <code className="ml-2 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">./tools/my-tool/test</code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'configuration',
      title: 'Configuration & Setup',
      icon: CogIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              MCP Configuration Files
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The MCP system uses several configuration files to manage tools and their execution environments.
            </p>

            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">global.json</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  Global system configuration and default settings.
                </p>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "server_name": "local-mcp-server",
  "server_version": "1.0.0",
  "temp_dir": null,
  "max_output_length": 10000,
  "timeout_seconds": 300,
  "auto_cleanup_temp": true,
  "temp_retention_hours": 24
}`}
                  </pre>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">tools.json</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  Registry of all available tools and their configurations.
                </p>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "tools": {
    "my-awesome-tool": {
      "name": "my-awesome-tool",
      "description": "Does awesome things",
      "type": "python",
      "entryPoint": "run.py",
      "testScript": "test.py",
      "parameters": {
        "input": {
          "type": "string",
          "required": true,
          "description": "Input file path"
        },
        "output": {
          "type": "string",
          "required": false,
          "description": "Output file path"
        }
      }
    }
  }
}`}
                  </pre>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Environment Setup
            </h3>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Environment Requirements</h4>
                  <ul className="mt-2 text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
                    <li>• Python 3.8+ for Python tools</li>
                    <li>• Bash shell for shell scripts</li>
                    <li>• Required system dependencies should be documented</li>
                    <li>• Virtual environments are automatically managed for Python tools</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mt-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Web Interface Management</h4>
                  <p className="mt-1 text-sm text-blue-800 dark:text-blue-200">
                    You can also manage server configuration through the web interface. Go to Server → Configuration 
                    to edit the server name, timeout, and other settings with a user-friendly interface.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'host-setup',
      title: 'MCP Host Setup (Claude Desktop)',
      icon: CogIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Connecting to Claude Desktop
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Once you've created and configured your tools, you need to connect the Local MCP Server to Claude Desktop 
              so you can actually use your tools in conversations with Claude.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Prerequisites</h4>
                  <ul className="mt-2 text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Claude Desktop app installed and running</li>
                    <li>• Local MCP Server configured with your tools</li>
                    <li>• Python 3.8+ installed on your system</li>
                    <li>• uv package manager installed (recommended)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step 1: Locate Claude Desktop Configuration
            </h3>
            
            <div className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center">
                    <span className="text-xl mr-2">🍎</span> macOS
                  </h4>
                  <div className="font-mono text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-2 rounded break-all overflow-wrap-anywhere">
                    ~/Library/Application Support/Claude/claude_desktop_config.json
                  </div>
                </div>
                
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center">
                    <span className="text-xl mr-2">🪟</span> Windows
                  </h4>
                  <div className="font-mono text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-2 rounded break-all overflow-wrap-anywhere">
                    %APPDATA%\\Claude\\claude_desktop_config.json
                  </div>
                </div>
              </div>
              
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-yellow-900 dark:text-yellow-100">Important</h4>
                    <p className="mt-1 text-sm text-yellow-800 dark:text-yellow-200">
                      If the config file doesn't exist, create it as an empty JSON file: <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">{"{}"}</code>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step 2: Configure MCP Server Connection
            </h3>
            
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Add your Local MCP Server configuration to Claude Desktop's config file. We recommend using the startup script for best logging support:
            </p>
            
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-green-900 dark:text-green-100">Recommended Configuration</h4>
                  <p className="mt-1 text-sm text-green-800 dark:text-green-200">
                    This configuration uses the startup script which includes automatic log redirection for monitoring.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 overflow-x-auto mb-4">
              <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "mcpServers": {
    "local-tools": {
      "command": "/absolute/path/to/local_mcp_server/start_mcp_server.sh",
      "args": [],
      "cwd": "/absolute/path/to/local_mcp_server"
    }
  }
}`}
              </pre>
            </div>
            
            <div className="space-y-3">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-red-900 dark:text-red-100">Replace Paths</h4>
                    <p className="mt-1 text-sm text-red-800 dark:text-red-200">
                      You MUST replace <code className="bg-red-200 dark:bg-red-800 px-1 rounded">/absolute/path/to/local_mcp_server</code> with the actual absolute path to your local_mcp_server directory.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Example with Real Path:</h4>
                <div className="font-mono text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-2 rounded break-all overflow-wrap-anywhere">
                  "/Users/yourname/Projects/local_mcp/local_mcp_server/start_mcp_server.sh"
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step 3: Alternative Configurations
            </h3>
            
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              If you need different startup modes or can't use the startup script, here are alternative configurations:
            </p>
            
            <div className="space-y-4">
              {/* Direct uv command */}
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-3">Option A: Direct uv Command</h4>
                <p className="text-yellow-800 dark:text-yellow-200 text-sm mb-3">
                  Direct command execution (logs won't be saved to file for monitoring):
                </p>
                <div className="bg-yellow-100 dark:bg-yellow-900/40 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-yellow-800 dark:text-yellow-200">
{`{
  "mcpServers": {
    "local-tools": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/local_mcp_server",
        "python", "-m", "local_mcp.server"
      ],
      "cwd": "/absolute/path/to/local_mcp_server"
    }
  }
}`}
                  </pre>
                </div>
              </div>

              {/* Python Direct */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-3">Option B: Using Python Directly</h4>
                <p className="text-blue-800 dark:text-blue-200 text-sm mb-3">
                  If you don't have uv installed, you can use Python directly (requires manual dependency management):
                </p>
                <div className="bg-blue-100 dark:bg-blue-900/40 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-blue-800 dark:text-blue-200">
{`{
  "mcpServers": {
    "local-tools": {
      "command": "python",
      "args": ["-m", "local_mcp.server"],
      "cwd": "/absolute/path/to/local_mcp_server"
    }
  }
}`}
                  </pre>
                </div>
              </div>

              {/* With Discovery */}
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-3">Option C: Startup Script with Tool Discovery</h4>
                <p className="text-purple-800 dark:text-purple-200 text-sm mb-3">
                  To automatically discover new tools on startup (slower but ensures latest tools):
                </p>
                <div className="bg-purple-100 dark:bg-purple-900/40 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-purple-800 dark:text-purple-200">
{`{
  "mcpServers": {
    "local-tools": {
      "command": "/absolute/path/to/local_mcp_server/start_mcp_server.sh",
      "args": ["--discover"],
      "cwd": "/absolute/path/to/local_mcp_server"
    }
  }
}`}
                  </pre>
                </div>
              </div>
            </div>
            
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mt-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-green-900 dark:text-green-100">Why Use the Startup Script?</h4>
                  <ul className="mt-2 text-sm text-green-800 dark:text-green-200 space-y-1">
                    <li>• <strong>Automatic log redirection</strong> - enables server monitoring in the web interface</li>
                    <li>• <strong>Environment handling</strong> - ensures proper uv virtual environment activation</li>
                    <li>• <strong>Error handling</strong> - provides better startup error messages</li>
                    <li>• <strong>Consistency</strong> - same startup behavior across different environments</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step 4: Restart Claude Desktop
            </h3>
            
            <div className="space-y-4">
              <p className="text-gray-700 dark:text-gray-300">
                After saving the configuration file, completely quit and restart Claude Desktop for the changes to take effect.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">🍎 macOS</h4>
                  <div className="text-sm text-blue-800 dark:text-blue-200">
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Cmd+Q to quit Claude Desktop</li>
                      <li>Reopen Claude Desktop from Applications</li>
                      <li>Wait for the connection indicator</li>
                    </ol>
                  </div>
                </div>
                
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">🪟 Windows</h4>
                  <div className="text-sm text-blue-800 dark:text-blue-200">
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Alt+F4 or close from system tray</li>
                      <li>Reopen Claude Desktop</li>
                      <li>Wait for the connection indicator</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Step 5: Verify Connection
            </h3>
            
            <div className="space-y-4">
              <p className="text-gray-700 dark:text-gray-300">
                Once Claude Desktop restarts, you should see your tools available in the conversation interface.
              </p>
              
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <div className="flex items-start">
                  <InformationCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-green-900 dark:text-green-100">Success Indicators</h4>
                    <ul className="mt-2 text-sm text-green-800 dark:text-green-200 space-y-1">
                      <li>• Look for a "🔌" or connection indicator in Claude's interface</li>
                      <li>• Your tools should appear in Claude's available tools list</li>
                      <li>• You can ask Claude: "What tools do you have access to?"</li>
                      <li>• Try running a simple tool to test the connection</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Test Command</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                  Try asking Claude to use one of your tools:
                </p>
                <div className="bg-gray-100 dark:bg-gray-700 rounded p-3">
                  <code className="text-sm text-gray-800 dark:text-gray-200">
                    "Can you run my-awesome-tool with the input parameter 'test'?"
                  </code>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Troubleshooting
            </h3>
            
            <div className="space-y-4">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <h4 className="font-medium text-red-900 dark:text-red-100 mb-3">Common Issues</h4>
                <div className="space-y-3 text-sm text-red-800 dark:text-red-200">
                  <div>
                    <strong>Tools not appearing:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Check that paths in config are absolute, not relative</li>
                      <li>Verify the local_mcp_server directory exists</li>
                      <li>Ensure Claude Desktop was completely restarted</li>
                    </ul>
                  </div>
                  <div>
                    <strong>Connection errors:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Check that Python and uv are installed and in PATH</li>
                      <li>Verify the MCP server can start manually</li>
                      <li>Look for JSON syntax errors in the config file</li>
                    </ul>
                  </div>
                  <div>
                    <strong>Tool execution fails:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Test tools manually in the web interface first</li>
                      <li>Check tool configurations in tools.json</li>
                      <li>Verify all dependencies are installed</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Debug Mode</h4>
                <p className="text-blue-800 dark:text-blue-200 text-sm mb-2">
                  To get more detailed error information, add debug flag:
                </p>
                <div className="bg-blue-100 dark:bg-blue-900/40 rounded p-2">
                  <code className="text-sm text-blue-800 dark:text-blue-200">
                    "args": [..., "--debug"]
                  </code>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          MCP System Documentation
        </h1>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Complete guide to understanding, creating, and managing tools in the Local Model Context Protocol system.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:w-1/4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Table of Contents
            </h2>
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                const isExpanded = expandedSections.has(section.id);
                
                return (
                  <button
                    key={section.id}
                    onClick={() => toggleSection(section.id)}
                    className={`w-full text-left flex items-center p-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    <span className="font-medium flex-1">{section.title}</span>
                    {isExpanded ? (
                      <ChevronDownIcon className="h-4 w-4" />
                    ) : (
                      <ChevronRightIcon className="h-4 w-4" />
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:w-3/4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            {sections.map((section) => (
              <div
                key={section.id}
                className={expandedSections.has(section.id) ? 'block' : 'hidden'}
              >
                <div className="flex items-center mb-6">
                  <section.icon className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-4" />
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {section.title}
                  </h2>
                </div>
                {section.content}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Start Banner */}
      <div className="mt-8 space-y-4">
        {/* Primary CTA */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-2">Ready to create your first tool?</h3>
              <p className="text-blue-100">
                Use our guided wizard to get started quickly with best practices built-in.
              </p>
            </div>
            <button
              onClick={() => window.location.href = '/tools/add'}
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors"
            >
              Start Wizard
            </button>
          </div>
        </div>

        {/* Complete Journey */}
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Complete User Journey
          </h3>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="font-bold">1</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">Learn Structure</h4>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Understand tool requirements and best practices
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="font-bold">2</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">Create Tools</h4>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Use the wizard or follow step-by-step guides
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="font-bold">3</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">Test & Configure</h4>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Validate tools work in the web interface
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="font-bold">4</span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">Connect Claude</h4>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Setup MCP host and use tools with Claude
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpDocumentation;
