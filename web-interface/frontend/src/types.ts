// Tool configuration types
export interface ToolParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default?: any;
}

export interface ScriptConfig {
  name: string;
  description: string;
  script_path: string;
  script_type: string;
  requires_confirmation: boolean;
  parameters: ToolParameter[];
  interactive: boolean;
  wrapper_function?: string;
  dependencies: string[];
  examples: string[];
  enabled: boolean;
}

export interface IndividualToolConfig {
  enabled: boolean;
  last_modified: string;
  auto_detected: boolean;
  tags: string[];
  script_config: ScriptConfig;
}

export interface ToolTestRequest {
  tool_name: string;
  parameters: Record<string, any>;
}

export interface BulkUpdateRequest {
  [toolName: string]: {
    action: 'update' | 'delete';
    enabled?: boolean;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface TestResult {
  success: boolean;
  message: string;
  parameters: Record<string, any>;
  output?: string;
  error?: string;
  tool_config?: any;
  dependencies_status?: Record<string, boolean>;
  missing_dependencies?: string[];
}

export interface DependencyStatus {
  tool_name: string;
  dependencies: string[];
  status: Record<string, boolean>;
  missing: string[];
  all_available: boolean;
}

// Test script types
export interface TestScriptResponse {
  exists: boolean;
  content: string;
  script_type: 'python' | 'shell' | 'other';
  path?: string;
  name?: string;
  message?: string;
}

export interface TestScriptExecutionResult {
  success: boolean;
  message: string;
  has_test_script: boolean;
  test_script_path?: string;
  output?: string;
  exit_code?: number;
  error?: string;
}

export interface EnvironmentInfo {
  python_executable: string;
  python_version: string;
  virtual_env_exists: boolean;
  virtual_env_path: string;
  config_dir: string;
  tools_dir: string;
}

// Tag management types
export interface TagRequest {
  tags: string[];
}

export interface TagResponse {
  success: boolean;
  message: string;
}

export interface TagSuggestionsResponse {
  suggestions: string[];
}

export interface AllTagsResponse {
  tags: string[];
}
