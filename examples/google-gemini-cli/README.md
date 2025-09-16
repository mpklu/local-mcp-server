# Google Gemini CLI Configuration

This directory contains configuration examples for using the Local MCP Server with Google's Gemini CLI.

## Configuration File

Use the `gemini-config.json` as a template for connecting the Gemini CLI to the Local MCP Server.

## Setup Instructions

1. **Install Gemini CLI**: Follow Google's installation instructions
2. **Update Paths**: Replace `/absolute/path/to/local-mcp-server` with your actual installation path
3. **Configure Environment**: Set required environment variables
4. **Add Configuration**: Place configuration in Gemini CLI's config directory

## Usage

```bash
# Start the server in Gemini CLI mode
cd /path/to/local-mcp-server/server
./start_server.sh --host=google-gemini-cli

# Use with Gemini CLI
gemini-cli --mcp-config /path/to/gemini-config.json
```

## Environment Variables

Required for Gemini CLI integration:
- `GEMINI_CLI_CONFIG`: Path to Gemini CLI configuration directory
- `GOOGLE_AI_STUDIO_KEY`: Your Google AI Studio API key
- `GEMINI_PROJECT_ID`: Your Google Cloud project ID

Optional:
- `PYTHONPATH`: Ensure Python can find the server modules
- `GEMINI_DEBUG`: Enable debug logging for Gemini CLI

## Configuration Notes

⚠️ **Important**: This configuration is based on expected Gemini CLI behavior. 
The actual configuration format may differ. Please refer to the official 
Google Gemini CLI documentation for the most up-to-date configuration format.

## Troubleshooting

Common issues:
1. **Authentication**: Ensure your Google AI Studio key is valid
2. **Project Access**: Verify your project ID has Gemini API access
3. **CLI Version**: Make sure you have a compatible Gemini CLI version
4. **Network**: Check firewall and proxy settings

## Features

The Gemini CLI integration supports:
- All standard Local MCP Server tools
- Google AI Studio integration
- Project-based organization
- Environment-based configuration