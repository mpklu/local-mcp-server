#!/usr/bin/env python3
"""Quick test for MCP 1.25.0 upgrade."""

import asyncio
from pathlib import Path
from local_mcp.server import LocalMCPServer


async def test():
    # Tools are at project root, config is in server/config
    project_root = Path(__file__).parent.parent.parent
    server = LocalMCPServer(
        project_root / 'tools',
        Path(__file__).parent.parent / 'config'
    )
    
    # Discover tools first
    await server.discovery.discover_scripts()
    
    tools = await server.discovery.get_available_tools()
    
    print(f'\n✅ Successfully loaded {len(tools)} tools with MCP 1.25.0')
    print('=' * 70)
    
    for tool in tools:
        annotations = tool.annotations
        read_only = getattr(annotations, 'readOnly', False) if annotations else False
        destructive = getattr(annotations, 'destructive', False) if annotations else False
        
        flags = []
        if read_only:
            flags.append('🔍 read-only')
        if destructive:
            flags.append('💥 destructive')
        if not read_only and not destructive:
            flags.append('📝 normal')
        
        print(f'\n  {tool.name}')
        print(f'    Title: {tool.title}')
        print(f'    Flags: {", ".join(flags)}')
        print(f'    Description: {tool.description[:80]}...')

if __name__ == '__main__':
    asyncio.run(test())
