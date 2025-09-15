import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { IndividualToolConfig } from '../types';
import { apiClient } from '../api';
import TagDropdown from './TagDropdown';

const ToolList: React.FC = () => {
  const [tools, setTools] = useState<IndividualToolConfig[]>([]);
  const [filteredTools, setFilteredTools] = useState<IndividualToolConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTools, setSelectedTools] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadTools();
  }, []);

  useEffect(() => {
    // Filter tools based on search query
    if (!searchQuery.trim()) {
      setFilteredTools(tools);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = tools.filter(tool => {
        // Search in tool name
        if (tool.script_config.name.toLowerCase().includes(query)) {
          return true;
        }
        
        // Search in description
        if (tool.script_config.description.toLowerCase().includes(query)) {
          return true;
        }
        
        // Search in tags
        if (tool.tags.some(tag => tag.toLowerCase().includes(query))) {
          return true;
        }
        
        return false;
      });
      setFilteredTools(filtered);
    }
  }, [tools, searchQuery]);

  const loadTools = async () => {
    try {
      const toolsData = await apiClient.getTools();
      setTools(toolsData);
    } catch (error) {
      console.error('Failed to load tools:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTagsChange = (toolName: string, newTags: string[]) => {
    setTools(prevTools => 
      prevTools.map(tool => 
        tool.script_config.name === toolName 
          ? { ...tool, tags: newTags }
          : tool
      )
    );
  };

  const handleBulkUpdate = async (action: 'enable' | 'disable' | 'delete') => {
    if (selectedTools.size === 0) return;

    const updates: Record<string, any> = {};
    
    selectedTools.forEach(toolName => {
      if (action === 'delete') {
        updates[toolName] = { action: 'delete' };
      } else {
        updates[toolName] = { 
          action: 'update', 
          enabled: action === 'enable' 
        };
      }
    });

    try {
      await apiClient.bulkUpdateTools(updates);
      await loadTools();
      setSelectedTools(new Set());
    } catch (error) {
      console.error('Bulk update failed:', error);
    }
  };

  const toggleToolSelection = (toolName: string) => {
    const newSelection = new Set(selectedTools);
    if (newSelection.has(toolName)) {
      newSelection.delete(toolName);
    } else {
      newSelection.add(toolName);
    }
    setSelectedTools(newSelection);
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading tools...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tools</h1>
        
        <div className="flex items-center space-x-4">
          {selectedTools.size > 0 && (
            <div className="flex space-x-2">
              <button
                onClick={() => handleBulkUpdate('enable')}
                className="px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700"
              >
                Enable ({selectedTools.size})
              </button>
              <button
                onClick={() => handleBulkUpdate('disable')}
                className="px-3 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Disable ({selectedTools.size})
              </button>
              <button
                onClick={() => handleBulkUpdate('delete')}
                className="px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                Delete ({selectedTools.size})
              </button>
            </div>
          )}
          
          <Link
            to="/tools/add"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Tool
          </Link>
        </div>
      </div>

      {/* Search Box */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search tools by name, description, or tags..."
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="grid gap-4">
        {filteredTools.map((tool) => {
          const toolName = tool.script_config.name;
          const isSelected = selectedTools.has(toolName);
          
          return (
            <div
              key={toolName}
              className={`border rounded-lg p-4 ${
                isSelected ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-200 dark:border-gray-700'
              } ${tool.enabled ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleToolSelection(toolName)}
                    className="h-4 w-4 text-indigo-600 rounded border-gray-300"
                  />
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {toolName}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {tool.script_config.description}
                    </p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        tool.enabled 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {tool.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {tool.script_config.script_type}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {tool.script_config.parameters.length} parameters
                      </span>
                    </div>
                    
                    {/* Tags */}
                    <div className="mt-3">
                      <TagDropdown
                        toolName={toolName}
                        currentTags={tool.tags}
                        onTagsChange={(newTags) => handleTagsChange(toolName, newTags)}
                      />
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <a
                    href={`/tools/${toolName}`}
                    className="px-3 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
                  >
                    Configure
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredTools.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <div className="text-gray-500 dark:text-gray-400">
            {searchQuery ? (
              <>
                <p className="text-lg font-medium">No tools found</p>
                <p className="mt-1">Try adjusting your search query</p>
              </>
            ) : (
              <>
                <p className="text-lg font-medium">No tools found</p>
                <p className="mt-1">Scan for tools to get started</p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolList;
