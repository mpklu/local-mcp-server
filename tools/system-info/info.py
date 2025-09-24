#!/usr/bin/env python3
"""
System Information Tool

Get comprehensive system information including OS, CPU, memory, and disk usage.
This tool showcases simple execution, JSON output, and parameter handling.
Now uses argparse instead of Python Fire for command-line argument parsing.
"""

import json
import platform
import psutil
import argparse
import sys
from pathlib import Path
from datetime import datetime


def get_system_info():
    """Get comprehensive system information.
    
    Returns detailed information about the operating system,
    CPU, memory, and basic system metrics.
    """
    try:
        # Basic system information
        info = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "os": platform.system(),
                "os_version": platform.version(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "cpu": {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else "N/A",
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
                "cpu_usage_percent": psutil.cpu_percent(interval=1)
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "percentage": psutil.virtual_memory().percent
            }
        }
        
        return json.dumps(info, indent=2)
    
    except Exception as e:
        return f"Error getting system info: {str(e)}"


def get_disk_usage(path="/"):
    """Get disk usage information for a specified path.
    
    Args:
        path (str): The filesystem path to check (default: root "/")
        
    Returns:
        str: JSON formatted disk usage information
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return f"Error: Path '{path}' does not exist"
        
        disk_usage = psutil.disk_usage(str(path_obj))
        
        info = {
            "path": str(path_obj.resolve()),
            "total_gb": round(disk_usage.total / (1024**3), 2),
            "used_gb": round(disk_usage.used / (1024**3), 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 1)
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        return f"Error getting disk usage for '{path}': {str(e)}"


def get_network_info():
    """Get network interface information.
    
    Returns basic network statistics and interface information.
    """
    try:
        # Get network interfaces
        interfaces = {}
        for interface, addresses in psutil.net_if_addrs().items():
            interface_info = []
            for addr in addresses:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    interface_info.append({
                        "family": addr.family.name,
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
            if interface_info:
                interfaces[interface] = interface_info
        
        # Get network statistics
        net_io = psutil.net_io_counters()
        stats = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_received": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_received": net_io.packets_recv
        }
        
        result = {
            "interfaces": interfaces,
            "statistics": stats
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error getting network info: {str(e)}"


def main():
    """Main entry point using argparse."""
    parser = argparse.ArgumentParser(description="System Information Tool for Local MCP Server")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # System info subcommand
    subparsers.add_parser('get_system_info', help='Get comprehensive system information')
    
    # Disk usage subcommand
    disk_parser = subparsers.add_parser('get_disk_usage', help='Get disk usage information')
    disk_parser.add_argument('--path', default='/', 
                            help='Filesystem path to check (default: /)')
    
    # Network info subcommand
    subparsers.add_parser('get_network_info', help='Get network interface information')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the requested command
    if args.command == 'get_system_info':
        result = get_system_info()
    elif args.command == 'get_disk_usage':
        result = get_disk_usage(args.path)
    elif args.command == 'get_network_info':
        result = get_network_info()
    else:
        result = json.dumps({"error": f"Unknown command: {args.command}"})
    
    print(result)


if __name__ == "__main__":
    main()
