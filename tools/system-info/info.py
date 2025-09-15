#!/usr/bin/env python3
"""
System Information Tool

Get comprehensive system information including OS, CPU, memory, and disk usage.
This tool showcases simple execution, JSON output, and parameter handling.
"""

import json
import platform
import psutil
import fire
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


if __name__ == "__main__":
    fire.Fire()
