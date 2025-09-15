import React, { useState, useEffect, useRef } from 'react';
import { PlusIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { apiClient } from '../api';

interface TagDropdownProps {
  toolName: string;
  currentTags: string[];
  onTagsChange: (tags: string[]) => void;
  className?: string;
}

const TagDropdown: React.FC<TagDropdownProps> = ({ 
  toolName, 
  currentTags, 
  onTagsChange, 
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setInputValue('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (inputValue.trim()) {
      fetchSuggestions(inputValue);
    } else {
      setSuggestions([]);
    }
  }, [inputValue]);

  const fetchSuggestions = async (query: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.getTagSuggestions(query);
      // Filter out tags that are already assigned to this tool
      const filteredSuggestions = response.suggestions.filter(
        tag => !currentTags.includes(tag)
      );
      setSuggestions(filteredSuggestions);
    } catch (error) {
      console.error('Failed to fetch tag suggestions:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const addTag = async (tag: string) => {
    const trimmedTag = tag.trim();
    if (!trimmedTag || currentTags.includes(trimmedTag)) {
      return;
    }

    const newTags = [...currentTags, trimmedTag];
    
    try {
      await apiClient.updateToolTags(toolName, newTags);
      onTagsChange(newTags);
      setInputValue('');
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to add tag:', error);
    }
  };

  const removeTag = async (tagToRemove: string) => {
    try {
      await apiClient.deleteToolTag(toolName, tagToRemove);
      const newTags = currentTags.filter(tag => tag !== tagToRemove);
      onTagsChange(newTags);
    } catch (error) {
      console.error('Failed to remove tag:', error);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (inputValue.trim()) {
        addTag(inputValue);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setInputValue('');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    addTag(suggestion);
  };

  // Generate colors for tags based on hash of tag name
  const getTagColor = (tag: string) => {
    const colors = [
      'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    ];
    
    let hash = 0;
    for (let i = 0; i < tag.length; i++) {
      hash = ((hash << 5) - hash + tag.charCodeAt(i)) & 0xffffffff;
    }
    return colors[Math.abs(hash) % colors.length];
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Tag Display */}
      <div className="flex flex-wrap items-center gap-1">
        {currentTags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTagColor(tag)}`}
          >
            {tag}
            <button
              onClick={() => removeTag(tag)}
              className="ml-1 hover:bg-black hover:bg-opacity-10 rounded-full p-0.5"
            >
              <XMarkIcon className="h-3 w-3" />
            </button>
          </span>
        ))}
        
        {currentTags.length > 3 && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
            +{currentTags.length - 3} more
          </span>
        )}
        
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500 transition-colors"
        >
          <PlusIcon className="h-3 w-3 mr-1" />
          Add Tag
        </button>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md shadow-lg z-10">
          <div className="p-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="Type to add or search tags..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
            />
          </div>
          
          {suggestions.length > 0 && (
            <div className="border-t border-gray-200 dark:border-gray-600 max-h-40 overflow-y-auto">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-900 dark:text-white"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          
          {isLoading && (
            <div className="p-3 text-center text-sm text-gray-500 dark:text-gray-400">
              Loading suggestions...
            </div>
          )}
          
          {inputValue.trim() && suggestions.length === 0 && !isLoading && (
            <div className="p-3 text-center text-sm text-gray-500 dark:text-gray-400">
              Press Enter to add "{inputValue.trim()}" as a new tag
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TagDropdown;
