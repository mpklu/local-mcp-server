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
              The Local MCP Server is a universal Model Context Protocol server that automatically discovers and exposes 
              local tools to AI assistants through a modern web interface and pluggable host adapter system. It provides 
              directory-based tool organization with intelligent auto-discovery and dual configuration management.
            </p>
            <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Key Benefits</h4>
                  <ul className="mt-2 text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Directory-based auto-discovery of tools</li>
                    <li>• Multi-host support (Claude Desktop, Generic MCP, Google Gemini CLI)</li>
                    <li>• Pluggable host adapter architecture</li>
                    <li>• Intelligent discovery pipeline with dual-config system</li>
                    <li>• Automatic dependency isolation per tool</li>
                    <li>• Web-based configuration and monitoring interface</li>
                    <li>• Support for Python, Shell, and binary tools</li>
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
                <div>📁 local-mcp-server/</div>
                <div className="ml-4">├── 🔧 server/ <span className="text-gray-500"># MCP server core</span></div>
                <div className="ml-8">│   ├── src/local_mcp/ <span className="text-gray-500"># Server source code</span></div>
                <div className="ml-8">│   │   ├── adapters/ <span className="text-gray-500"># Host adapter system</span></div>
                <div className="ml-8">│   │   ├── discovery.py <span className="text-gray-500"># Tool discovery system</span></div>
                <div className="ml-8">│   │   └── server.py <span className="text-gray-500"># Main MCP server</span></div>
                <div className="ml-8">│   ├── config/ <span className="text-gray-500"># Configuration files</span></div>
                <div className="ml-8">│   │   ├── tools/ <span className="text-gray-500"># Individual tool configs</span></div>
                <div className="ml-8">│   │   └── tools.json <span className="text-gray-500"># Compiled config</span></div>
                <div className="ml-8">│   ├── discover_tools.py <span className="text-gray-500"># Discovery utility</span></div>
                <div className="ml-8">│   └── build_tools.py <span className="text-gray-500"># Config compiler</span></div>
                <div className="ml-4">├── 🌐 web-interface/ <span className="text-gray-500"># Web management interface</span></div>
                <div className="ml-4">├── 🛠️ tools/ <span className="text-gray-500"># Directory-based tools</span></div>
                <div className="ml-8">│   ├── demo-features/ <span className="text-gray-500"># Sample tool</span></div>
                <div className="ml-8">│   ├── file-ops/ <span className="text-gray-500"># Sample tool</span></div>
                <div className="ml-8">│   └── system-info/ <span className="text-gray-500"># Sample tool</span></div>
                <div className="ml-4">└── 📚 docs/ <span className="text-gray-500"># Documentation</span></div>
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
              Each tool must be in its own directory under <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">tools/</code>. 
              The discovery system automatically detects tools and generates configurations based on the directory structure.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Python Tools */}
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-3 flex items-center">
                  <span className="text-xl mr-2">🐍</span> Python Tools (Auto-Discovered)
                </h4>
                <div className="font-mono text-sm text-green-800 dark:text-green-200 space-y-1">
                  <div>tools/your-tool-name/</div>
                  <div className="ml-4">├── <strong>run.py</strong> <span className="text-green-600 dark:text-green-400"># Required entry point (Fire CLI)</span></div>
                  <div className="ml-4">├── processor.py <span className="text-green-600 dark:text-green-400"># Main functionality</span></div>
                  <div className="ml-4">├── requirements.txt <span className="text-green-600 dark:text-green-400"># Auto-detected dependencies</span></div>
                  <div className="ml-4">├── test.py <span className="text-green-600 dark:text-green-400"># Optional test script</span></div>
                  <div className="ml-4">└── README.md <span className="text-green-600 dark:text-green-400"># Documentation</span></div>
                </div>
              </div>

              {/* Shell Tools */}
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-3 flex items-center">
                  <span className="text-xl mr-2">🐚</span> Shell Tools (Auto-Discovered)
                </h4>
                <div className="font-mono text-sm text-purple-800 dark:text-purple-200 space-y-1">
                  <div>tools/your-tool-name/</div>
                  <div className="ml-4">├── <strong>run.sh</strong> <span className="text-purple-600 dark:text-purple-400"># Entry point (preferred)</span></div>
                  <div className="ml-4">├── <strong>run</strong> <span className="text-purple-600 dark:text-purple-400"># Alternative entry point</span></div>
                  <div className="ml-4">├── utils.sh <span className="text-purple-600 dark:text-purple-400"># Helper scripts</span></div>
                  <div className="ml-4">├── test <span className="text-purple-600 dark:text-purple-400"># Optional test script</span></div>
                  <div className="ml-4">└── README.md <span className="text-purple-600 dark:text-purple-400"># Documentation</span></div>
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
                      <li>• Each tool MUST be in its own directory under <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">tools/</code></li>
                      <li>• Entry point priority: <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">run.py</code> → <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">run.sh</code> → <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">run</code></li>
                      <li>• Python tools should use Fire CLI for parameter handling</li>
                      <li>• Discovery system automatically generates configurations</li>
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
                  <h4 className="font-medium text-gray-900 dark:text-white">Auto-Discovery & Configuration</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    The discovery system automatically detects your tool and generates configuration. No manual setup required!
                  </p>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm">
                      <ChevronRightIcon className="h-4 w-4 mr-1" />
                      Run discovery: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded ml-1">python server/discover_tools.py</code>
                    </div>
                    <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm">
                      <ChevronRightIcon className="h-4 w-4 mr-1" />
                      Compile config: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded ml-1">python server/build_tools.py</code>
                    </div>
                    <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm">
                      <ChevronRightIcon className="h-4 w-4 mr-1" />
                      Configure via web interface at http://localhost:3000
                    </div>
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
      id: 'discovery-system',
      title: 'Auto-Discovery System',
      icon: InformationCircleIcon,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              How Discovery Works
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The discovery system automatically scans the <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">tools/</code>{' '}
              directory, detects tool entry points, and generates individual configurations. This eliminates manual setup 
              and ensures all tools are properly configured.
            </p>

            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-4">Discovery Pipeline</h4>
              <div className="space-y-3">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">1</div>
                  <div>
                    <span className="font-medium text-blue-800 dark:text-blue-200">Directory Scan</span>
                    <span className="text-blue-600 dark:text-blue-400 text-sm ml-2">→ Finds all folders in tools/</span>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">2</div>
                  <div>
                    <span className="font-medium text-blue-800 dark:text-blue-200">Entry Point Detection</span>
                    <span className="text-blue-600 dark:text-blue-400 text-sm ml-2">→ Looks for run.py, run.sh, or run</span>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">3</div>
                  <div>
                    <span className="font-medium text-blue-800 dark:text-blue-200">Config Generation</span>
                    <span className="text-blue-600 dark:text-blue-400 text-sm ml-2">→ Creates individual tool configs</span>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">4</div>
                  <div>
                    <span className="font-medium text-blue-800 dark:text-blue-200">Compilation</span>
                    <span className="text-blue-600 dark:text-blue-400 text-sm ml-2">→ Builds server configuration</span>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">✓</div>
                  <div>
                    <span className="font-medium text-green-800 dark:text-green-200">Server Integration</span>
                    <span className="text-green-600 dark:text-green-400 text-sm ml-2">→ Tools available in MCP clients</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Discovery Commands
            </h3>
            <div className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Basic Discovery</h4>
                <div className="bg-green-100 dark:bg-green-900/40 rounded-md p-3">
                  <code className="text-sm text-green-800 dark:text-green-200">
                    cd server && python discover_tools.py
                  </code>
                </div>
                <p className="text-green-700 dark:text-green-300 text-sm mt-2">
                  Generates configuration for newly discovered tools
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">List Tools</h4>
                <div className="bg-blue-100 dark:bg-blue-900/40 rounded-md p-3">
                  <code className="text-sm text-blue-800 dark:text-blue-200">
                    python discover_tools.py --list
                  </code>
                </div>
                <p className="text-blue-700 dark:text-blue-300 text-sm mt-2">
                  Shows all discovered tools and their configuration status
                </p>
              </div>

              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-2">Compile Configuration</h4>
                <div className="bg-purple-100 dark:bg-purple-900/40 rounded-md p-3">
                  <code className="text-sm text-purple-800 dark:text-purple-200">
                    python build_tools.py
                  </code>
                </div>
                <p className="text-purple-700 dark:text-purple-300 text-sm mt-2">
                  Compiles individual configs into server configuration
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Dual Configuration System
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The system maintains two configuration layers for maximum flexibility:
            </p>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-3">Individual Configs</h4>
                <div className="space-y-2 text-sm text-yellow-800 dark:text-yellow-200">
                  <div>📁 <code className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">config/tools/*.json</code></div>
                  <div>• One file per tool</div>
                  <div>• Rich metadata and settings</div>
                  <div>• Editable via web interface</div>
                  <div>• User customizations preserved</div>
                </div>
              </div>
              
              <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
                <h4 className="font-medium text-indigo-900 dark:text-indigo-100 mb-3">Compiled Config</h4>
                <div className="space-y-2 text-sm text-indigo-800 dark:text-indigo-200">
                  <div>📄 <code className="bg-indigo-200 dark:bg-indigo-800 px-1 rounded">config/tools.json</code></div>
                  <div>• Optimized for server</div>
                  <div>• Generated from individual configs</div>
                  <div>• Fast server startup</div>
                  <div>• Rebuilt automatically</div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mt-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-gray-600 dark:text-gray-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-gray-100">Workflow</h4>
                  <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">
                    Make changes in the web interface → Individual configs updated → 
                    Run <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">build_tools.py</code> → 
                    Server config compiled → Restart server
                  </p>
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
              Dual Configuration System
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The system uses a dual-configuration approach with individual tool configs and a compiled server configuration.
            </p>

            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Individual Tool Config (config/tools/*.json)</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  Per-tool configurations edited via the web interface and automatically generated by discovery.
                </p>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "name": "System Information",
  "description": "Get detailed system information",
  "script_path": "tools/system-info/run.py",
  "dependencies": ["psutil", "platform"],
  "timeout": 30,
  "enabled": true,
  "tags": ["system", "monitoring"],
  "parameters": {
    "format": "json",
    "detailed": false
  }
}`}
                  </pre>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Server Config (config/tools.json)</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  Compiled configuration used by MCP server, generated from individual tool configs.
                </p>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "global_settings": {
    "python_env_path": "config/python_env",
    "timeout_seconds": 300
  },
  "tools": {
    "system-info": {
      "name": "System Information",
      "description": "Get detailed system information",
      "script_path": "tools/system-info/run.py",
      "dependencies": ["psutil", "platform"],
      "timeout": 30,
      "enabled": true,
      "tags": ["system", "monitoring"]
    }
  }
}`}
                  </pre>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Global Config (config/config.json)</h4>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  Server-wide settings and host adapter configuration.
                </p>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-md p-3 overflow-x-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200">
{`{
  "server": {
    "name": "local-mcp-server",
    "version": "2.0.0",
    "timeout_seconds": 300
  },
  "host_adapters": {
    "claude-desktop": {
      "enabled": true,
      "config_path": "examples/claude-desktop/mcp-config.json"
    },
    "generic": {
      "enabled": true,
      "stdio_mode": true
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
              Host Adapter System
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The system supports multiple AI host integration methods through specialized adapters.
            </p>

            <div className="space-y-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start">
                  <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">Claude Desktop Adapter</h4>
                    <p className="mt-2 text-sm text-blue-800 dark:text-blue-200">
                      Direct integration with Claude Desktop via MCP configuration. Provides seamless tool access within Claude's interface.
                    </p>
                    <div className="mt-3 bg-blue-100 dark:bg-blue-800/50 rounded p-2">
                      <code className="text-xs text-blue-900 dark:text-blue-100">examples/claude-desktop/mcp-config.json</code>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <div className="flex items-start">
                  <InformationCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-green-900 dark:text-green-100">Generic MCP Adapter</h4>
                    <p className="mt-2 text-sm text-green-800 dark:text-green-200">
                      Universal stdio-based MCP server for integration with any MCP-compatible AI assistant or custom client.
                    </p>
                    <div className="mt-3 bg-green-100 dark:bg-green-800/50 rounded p-2">
                      <code className="text-xs text-green-900 dark:text-green-100">server/start_server.sh</code>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <div className="flex items-start">
                  <InformationCircleIcon className="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-medium text-purple-900 dark:text-purple-100">Google Gemini CLI Adapter</h4>
                    <p className="mt-2 text-sm text-purple-800 dark:text-purple-200">
                      Experimental integration for Google Gemini via CLI interface. Future development planned.
                    </p>
                    <div className="mt-3 bg-purple-100 dark:bg-purple-800/50 rounded p-2">
                      <code className="text-xs text-purple-900 dark:text-purple-100">examples/google-gemini-cli/</code>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Environment Requirements
            </h3>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100">System Requirements</h4>
                  <ul className="mt-2 text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
                    <li>• Python 3.8+ for Python tools and server</li>
                    <li>• Bash shell for shell scripts and setup</li>
                    <li>• Node.js 16+ for web interface development</li>
                    <li>• UV package manager for Python dependency management</li>
                    <li>• Virtual environments automatically managed per tool</li>
                    <li>• Host-specific requirements (Claude Desktop, MCP clients)</li>
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
                    <strong>Tools not discovered:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Ensure tools are in <code className="bg-red-100 dark:bg-red-800 px-1 rounded">tools/</code> directory</li>
                      <li>Check entry point exists: <code className="bg-red-100 dark:bg-red-800 px-1 rounded">run.py</code>, <code className="bg-red-100 dark:bg-red-800 px-1 rounded">run.sh</code>, or <code className="bg-red-100 dark:bg-red-800 px-1 rounded">run</code></li>
                      <li>Run <code className="bg-red-100 dark:bg-red-800 px-1 rounded">python discover_tools.py</code> to regenerate configs</li>
                      <li>Verify <code className="bg-red-100 dark:bg-red-800 px-1 rounded">python build_tools.py</code> completed successfully</li>
                    </ul>
                  </div>
                  <div>
                    <strong>Host connection issues:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Check host adapter configuration in <code className="bg-red-100 dark:bg-red-800 px-1 rounded">config/config.json</code></li>
                      <li>For Claude: Verify MCP config path and restart Claude Desktop</li>
                      <li>For generic MCP: Check stdio communication and server startup</li>
                      <li>Ensure server starts without errors: <code className="bg-red-100 dark:bg-red-800 px-1 rounded">./start_server.sh</code></li>
                    </ul>
                  </div>
                  <div>
                    <strong>Configuration sync issues:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Individual configs out of sync: Run <code className="bg-red-100 dark:bg-red-800 px-1 rounded">python build_tools.py</code></li>
                      <li>Web interface changes not reflected: Restart MCP server after config compilation</li>
                      <li>Tools enabled but not working: Check individual tool config in <code className="bg-red-100 dark:bg-red-800 px-1 rounded">config/tools/</code></li>
                    </ul>
                  </div>
                  <div>
                    <strong>Tool execution failures:</strong>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      <li>Test tools first via web interface before using with AI host</li>
                      <li>Check virtual environment setup and dependencies</li>
                      <li>Verify tool script permissions and entry point execution</li>
                      <li>Review timeout settings in tool configuration</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Discovery Pipeline Debug</h4>
                <p className="text-blue-800 dark:text-blue-200 text-sm mb-2">
                  Debug the discovery and configuration system:
                </p>
                <div className="space-y-2">
                  <div className="bg-blue-100 dark:bg-blue-900/40 rounded p-2">
                    <code className="text-sm text-blue-800 dark:text-blue-200">
                      cd server && python discover_tools.py --list-all
                    </code>
                  </div>
                  <div className="bg-blue-100 dark:bg-blue-900/40 rounded p-2">
                    <code className="text-sm text-blue-800 dark:text-blue-200">
                      cd server && python build_tools.py --verbose
                    </code>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Host Adapter Testing</h4>
                <p className="text-green-800 dark:text-green-200 text-sm mb-2">
                  Test specific host adapter configurations:
                </p>
                <div className="space-y-2">
                  <div>
                    <strong className="text-green-900 dark:text-green-100">Claude Desktop:</strong>
                    <div className="bg-green-100 dark:bg-green-900/40 rounded p-2 mt-1">
                      <code className="text-sm text-green-800 dark:text-green-200">
                        Check ~/Library/Application Support/Claude/claude_desktop_config.json
                      </code>
                    </div>
                  </div>
                  <div>
                    <strong className="text-green-900 dark:text-green-100">Generic MCP:</strong>
                    <div className="bg-green-100 dark:bg-green-900/40 rounded p-2 mt-1">
                      <code className="text-sm text-green-800 dark:text-green-200">
                        cd server && ./start_server.sh # Test stdio communication
                      </code>
                    </div>
                  </div>
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
