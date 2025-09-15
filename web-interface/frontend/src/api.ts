import { IndividualToolConfig, BulkUpdateRequest, ApiResponse, TestResult, DependencyStatus, EnvironmentInfo, TestScriptResponse, TestScriptExecutionResult, TagResponse, TagSuggestionsResponse, AllTagsResponse } from './types';

const API_BASE_URL = '/api';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }

  // Tool management
  async getTools(): Promise<IndividualToolConfig[]> {
    return this.request('/tools');
  }

  async getTool(toolName: string): Promise<IndividualToolConfig> {
    return this.request(`/tools/${toolName}`);
  }

  async updateTool(toolName: string, config: IndividualToolConfig): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}`, {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  async deleteTool(toolName: string): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}`, {
      method: 'DELETE',
    });
  }

  async createTool(toolData: {
    name: string;
    description: string;
    script_type: string;
    method: string;
    script_path?: string;
    parameters?: Array<{
      name: string;
      type: string;
      description: string;
      required: boolean;
    }>;
  }): Promise<ApiResponse> {
    return this.request('/tools', {
      method: 'POST',
      body: JSON.stringify(toolData),
    });
  }

  async bulkUpdateTools(updates: BulkUpdateRequest): Promise<{ results: Record<string, any> }> {
    return this.request('/tools/bulk-update', {
      method: 'POST',
      body: JSON.stringify(updates),
    });
  }

  // Discovery and building
  async scanForTools(): Promise<ApiResponse> {
    return this.request('/scan', {
      method: 'POST',
    });
  }

  async buildToolsJson(): Promise<ApiResponse> {
    return this.request('/build', {
      method: 'POST',
    });
  }

  // Tool testing
  async testTool(toolName: string, parameters: Record<string, any>): Promise<TestResult> {
    return this.request(`/tools/${toolName}/test`, {
      method: 'POST',
      body: JSON.stringify({
        tool_name: toolName,
        parameters,
      }),
    });
  }

  // Test script management
  async getTestScript(toolName: string): Promise<TestScriptResponse> {
    return this.request(`/tools/${toolName}/test-script`);
  }

  async saveTestScript(toolName: string, content: string, scriptType: string): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}/test-script`, {
      method: 'PUT',
      body: JSON.stringify({
        content,
        script_type: scriptType,
      }),
    });
  }

  async runTestScript(toolName: string): Promise<TestScriptExecutionResult> {
    return this.request(`/tools/${toolName}/test-script`, {
      method: 'POST',
    });
  }

  async deleteTestScript(toolName: string): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}/test-script`, {
      method: 'DELETE',
    });
  }

  // Dependency management
  async checkDependencies(toolName: string): Promise<DependencyStatus> {
    return this.request(`/tools/${toolName}/dependencies/check`, {
      method: 'POST',
    });
  }

  async installDependencies(toolName: string): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}/dependencies/install`, {
      method: 'POST',
    });
  }

  async getEnvironmentInfo(): Promise<EnvironmentInfo> {
    return this.request('/environment/info');
  }

  // Tag management
  async getAllTags(): Promise<AllTagsResponse> {
    return this.request('/tags');
  }

  async updateToolTags(toolName: string, tags: string[]): Promise<TagResponse> {
    return this.request(`/tools/${toolName}/tags`, {
      method: 'POST',
      body: JSON.stringify({ tags }),
    });
  }

  async deleteToolTag(toolName: string, tag: string): Promise<ApiResponse> {
    return this.request(`/tools/${toolName}/tags/${encodeURIComponent(tag)}`, {
      method: 'DELETE',
    });
  }

  async getTagSuggestions(query: string = ''): Promise<TagSuggestionsResponse> {
    const params = query ? `?q=${encodeURIComponent(query)}` : '';
    return this.request(`/tags/suggestions${params}`);
  }
}

export const apiClient = new ApiClient();
