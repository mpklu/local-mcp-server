"""
Resource limits and execution controls for Local MCP Server.

This module provides:
- Resource limits (CPU, memory, processes, file size)
- Concurrent execution control (semaphore)
- Rate limiting per tool
- Cross-platform compatibility (Unix-only features gracefully disabled on Windows)
"""

import asyncio
import logging
import sys
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Import resource module (Unix only)
RESOURCE_AVAILABLE = False
try:
    import resource
    RESOURCE_AVAILABLE = sys.platform != 'win32'
except ImportError:
    logger.warning("resource module not available - resource limits disabled")


class ResourceLimiter:
    """Apply resource limits to tool execution."""
    
    def __init__(
        self,
        max_cpu_seconds: int = 60,
        max_memory_mb: int = 512,
        max_processes: int = 10,
        max_file_size_mb: int = 100,
        enabled: bool = True
    ):
        """Initialize resource limiter.
        
        Args:
            max_cpu_seconds: CPU time limit per execution
            max_memory_mb: Memory limit in megabytes
            max_processes: Maximum number of child processes
            max_file_size_mb: Maximum file size in megabytes
            enabled: Whether to enforce limits
        """
        self.max_cpu_seconds = max_cpu_seconds
        self.max_memory_mb = max_memory_mb
        self.max_processes = max_processes
        self.max_file_size_mb = max_file_size_mb
        self.enabled = enabled and RESOURCE_AVAILABLE
        
        if enabled and not RESOURCE_AVAILABLE:
            logger.warning(
                "Resource limits requested but not available on this platform "
                "(Unix only). Limits will not be enforced."
            )
    
    def apply_limits(self) -> None:
        """Apply resource limits to current process.
        
        This should be called in the child process before executing the tool.
        Uses resource.setrlimit() on Unix systems.
        """
        if not self.enabled:
            return
        
        try:
            # CPU time limit (seconds)
            if self.max_cpu_seconds > 0:
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (self.max_cpu_seconds, self.max_cpu_seconds)
                )
                logger.debug(f"Set CPU limit: {self.max_cpu_seconds}s")
            
            # Memory limit (bytes)
            if self.max_memory_mb > 0:
                max_memory_bytes = self.max_memory_mb * 1024 * 1024
                resource.setrlimit(
                    resource.RLIMIT_AS,  # Address space (virtual memory)
                    (max_memory_bytes, max_memory_bytes)
                )
                logger.debug(f"Set memory limit: {self.max_memory_mb}MB")
            
            # Process limit
            if self.max_processes > 0:
                resource.setrlimit(
                    resource.RLIMIT_NPROC,
                    (self.max_processes, self.max_processes)
                )
                logger.debug(f"Set process limit: {self.max_processes}")
            
            # File size limit (bytes)
            if self.max_file_size_mb > 0:
                max_file_bytes = self.max_file_size_mb * 1024 * 1024
                resource.setrlimit(
                    resource.RLIMIT_FSIZE,
                    (max_file_bytes, max_file_bytes)
                )
                logger.debug(f"Set file size limit: {self.max_file_size_mb}MB")
                
        except Exception as e:
            logger.error(f"Failed to apply resource limits: {e}")
            # Don't fail execution - limits are best-effort
    
    def get_preexec_fn(self):
        """Get function to run before exec in subprocess.
        
        Returns:
            Function to pass as preexec_fn to subprocess.Popen
        """
        if not self.enabled:
            return None
        
        def preexec():
            """Apply limits in child process."""
            self.apply_limits()
        
        return preexec


class ExecutionSemaphore:
    """Control concurrent tool execution."""
    
    def __init__(self, max_concurrent: int = 5):
        """Initialize execution semaphore.
        
        Args:
            max_concurrent: Maximum number of concurrent tool executions
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.total_executions = 0
        self.total_queued = 0
    
    async def acquire(self, tool_name: str) -> None:
        """Acquire execution slot.
        
        Args:
            tool_name: Name of tool being executed
        """
        if self.semaphore.locked():
            self.total_queued += 1
            logger.info(
                f"[{tool_name}] Waiting for execution slot "
                f"({self.active_count}/{self.max_concurrent} active)"
            )
        
        await self.semaphore.acquire()
        self.active_count += 1
        self.total_executions += 1
        
        logger.debug(
            f"[{tool_name}] Acquired execution slot "
            f"({self.active_count}/{self.max_concurrent} active)"
        )
    
    def release(self, tool_name: str) -> None:
        """Release execution slot.
        
        Args:
            tool_name: Name of tool that finished
        """
        self.semaphore.release()
        self.active_count -= 1
        
        logger.debug(
            f"[{tool_name}] Released execution slot "
            f"({self.active_count}/{self.max_concurrent} active)"
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get execution statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'max_concurrent': self.max_concurrent,
            'active_count': self.active_count,
            'total_executions': self.total_executions,
            'total_queued': self.total_queued
        }


class RateLimiter:
    """Rate limit tool executions using sliding window algorithm."""
    
    def __init__(
        self,
        max_executions_per_minute: int = 10,
        enabled: bool = True
    ):
        """Initialize rate limiter.
        
        Args:
            max_executions_per_minute: Maximum executions per tool per minute
            enabled: Whether to enforce rate limiting
        """
        self.max_per_minute = max_executions_per_minute
        self.enabled = enabled
        self.window_seconds = 60
        
        # Track executions per tool: tool_name -> deque of timestamps
        self.executions: Dict[str, deque] = defaultdict(lambda: deque())
    
    async def check_rate_limit(self, tool_name: str) -> Tuple[bool, Optional[float]]:
        """Check if tool execution is within rate limit.
        
        Args:
            tool_name: Name of tool to check
            
        Returns:
            Tuple of (is_allowed, wait_seconds)
            - is_allowed: True if execution is allowed
            - wait_seconds: If not allowed, how long to wait
        """
        if not self.enabled:
            return True, None
        
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get executions for this tool
        tool_executions = self.executions[tool_name]
        
        # Remove old executions outside the window
        while tool_executions and tool_executions[0] < window_start:
            tool_executions.popleft()
        
        # Check if we're at the limit
        if len(tool_executions) >= self.max_per_minute:
            # Calculate how long to wait
            oldest_execution = tool_executions[0]
            wait_seconds = oldest_execution + self.window_seconds - now
            
            logger.warning(
                f"[{tool_name}] Rate limit exceeded: "
                f"{len(tool_executions)}/{self.max_per_minute} executions in last 60s. "
                f"Wait {wait_seconds:.1f}s"
            )
            
            return False, wait_seconds
        
        # Record this execution
        tool_executions.append(now)
        
        logger.debug(
            f"[{tool_name}] Rate limit check passed: "
            f"{len(tool_executions)}/{self.max_per_minute} executions in window"
        )
        
        return True, None
    
    def get_stats(self, tool_name: str) -> Dict[str, any]:
        """Get rate limit statistics for a tool.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Dictionary with statistics
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        tool_executions = self.executions[tool_name]
        
        # Count recent executions
        recent_count = sum(1 for t in tool_executions if t >= window_start)
        
        return {
            'tool_name': tool_name,
            'max_per_minute': self.max_per_minute,
            'recent_count': recent_count,
            'remaining': max(0, self.max_per_minute - recent_count),
            'window_seconds': self.window_seconds
        }
    
    def reset(self, tool_name: Optional[str] = None) -> None:
        """Reset rate limit counters.
        
        Args:
            tool_name: Tool to reset, or None to reset all
        """
        if tool_name:
            self.executions[tool_name].clear()
            logger.info(f"Reset rate limit for tool: {tool_name}")
        else:
            self.executions.clear()
            logger.info("Reset rate limits for all tools")


class ExecutionController:
    """Unified execution control with resource limits, concurrency, and rate limiting."""
    
    def __init__(
        self,
        resource_limiter: ResourceLimiter,
        execution_semaphore: ExecutionSemaphore,
        rate_limiter: RateLimiter
    ):
        """Initialize execution controller.
        
        Args:
            resource_limiter: Resource limit enforcer
            execution_semaphore: Concurrent execution controller
            rate_limiter: Rate limiter
        """
        self.resource_limiter = resource_limiter
        self.execution_semaphore = execution_semaphore
        self.rate_limiter = rate_limiter
    
    async def acquire(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Acquire execution permission (rate limit + semaphore).
        
        Args:
            tool_name: Name of tool to execute
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check rate limit
        is_allowed, wait_seconds = await self.rate_limiter.check_rate_limit(tool_name)
        
        if not is_allowed:
            return False, (
                f"Rate limit exceeded for {tool_name}. "
                f"Please wait {wait_seconds:.1f} seconds."
            )
        
        # Acquire semaphore slot
        await self.execution_semaphore.acquire(tool_name)
        
        return True, None
    
    def release(self, tool_name: str) -> None:
        """Release execution resources.
        
        Args:
            tool_name: Name of tool that finished
        """
        self.execution_semaphore.release(tool_name)
    
    def get_preexec_fn(self):
        """Get preexec function for subprocess.
        
        Returns:
            Function to apply resource limits in child process
        """
        return self.resource_limiter.get_preexec_fn()
    
    def get_stats(self) -> Dict[str, any]:
        """Get execution statistics.
        
        Returns:
            Dictionary with all statistics
        """
        return {
            'semaphore': self.execution_semaphore.get_stats(),
            'resource_limits_enabled': self.resource_limiter.enabled,
            'rate_limiting_enabled': self.rate_limiter.enabled
        }
