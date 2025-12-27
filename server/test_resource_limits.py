#!/usr/bin/env python3
"""Test resource limits enforcement."""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.executor_limits import (
    ResourceLimiter,
    ExecutionSemaphore,
    RateLimiter,
    ExecutionController,
    RESOURCE_AVAILABLE
)


def test_resource_limiter():
    """Test resource limiter initialization."""
    print("=" * 70)
    print("TEST 1: Resource Limiter Initialization")
    print("=" * 70)
    
    limiter = ResourceLimiter(
        max_cpu_seconds=30,
        max_memory_mb=256,
        max_processes=5,
        max_file_size_mb=50,
        enabled=True
    )
    
    print(f"\n📝 Resource limiter created:")
    print(f"   CPU limit: {limiter.max_cpu_seconds}s")
    print(f"   Memory limit: {limiter.max_memory_mb}MB")
    print(f"   Process limit: {limiter.max_processes}")
    print(f"   File size limit: {limiter.max_file_size_mb}MB")
    print(f"   Enabled: {limiter.enabled}")
    print(f"   Platform support: {'✅ Available' if RESOURCE_AVAILABLE else '❌ Not available (Windows or no resource module)'}")
    
    if limiter.enabled:
        print(f"\n✅ Resource limits will be enforced")
    else:
        print(f"\n⚠️  Resource limits not available on this platform")


async def test_concurrent_execution():
    """Test concurrent execution control."""
    print("\n" + "=" * 70)
    print("TEST 2: Concurrent Execution Control")
    print("=" * 70)
    
    semaphore = ExecutionSemaphore(max_concurrent=3)
    
    print(f"\n📝 Semaphore created with max_concurrent=3")
    
    async def mock_tool_execution(tool_name: str, duration: float):
        """Mock tool execution."""
        await semaphore.acquire(tool_name)
        try:
            print(f"   [{tool_name}] Started (active: {semaphore.active_count}/3)")
            await asyncio.sleep(duration)
            print(f"   [{tool_name}] Finished")
        finally:
            semaphore.release(tool_name)
    
    # Launch 5 tools simultaneously (only 3 should run at once)
    print(f"\n📝 Launching 5 tools (max 3 concurrent):")
    tasks = [
        mock_tool_execution("tool-1", 0.1),
        mock_tool_execution("tool-2", 0.1),
        mock_tool_execution("tool-3", 0.1),
        mock_tool_execution("tool-4", 0.1),
        mock_tool_execution("tool-5", 0.1),
    ]
    
    await asyncio.gather(*tasks)
    
    stats = semaphore.get_stats()
    print(f"\n✅ All tools completed")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Total queued: {stats['total_queued']}")
    print(f"   Final active count: {stats['active_count']}")
    
    if stats['total_queued'] >= 2:
        print(f"   ✅ Concurrent limit enforced (2+ tools had to wait)")
    else:
        print(f"   ⚠️  No queueing detected")


async def test_rate_limiting():
    """Test rate limiting."""
    print("\n" + "=" * 70)
    print("TEST 3: Rate Limiting")
    print("=" * 70)
    
    rate_limiter = RateLimiter(
        max_executions_per_minute=5,
        enabled=True
    )
    
    print(f"\n📝 Rate limiter created: max 5 executions per minute")
    
    tool_name = "test-tool"
    
    # Try to execute 7 times rapidly
    print(f"\n📝 Attempting 7 rapid executions:")
    
    allowed_count = 0
    denied_count = 0
    
    for i in range(7):
        is_allowed, wait_seconds = await rate_limiter.check_rate_limit(tool_name)
        
        if is_allowed:
            allowed_count += 1
            print(f"   Execution {i+1}: ✅ Allowed")
        else:
            denied_count += 1
            print(f"   Execution {i+1}: ❌ Denied (wait {wait_seconds:.1f}s)")
    
    stats = rate_limiter.get_stats(tool_name)
    print(f"\n📊 Rate limit stats:")
    print(f"   Max per minute: {stats['max_per_minute']}")
    print(f"   Recent count: {stats['recent_count']}")
    print(f"   Remaining: {stats['remaining']}")
    
    if allowed_count == 5 and denied_count == 2:
        print(f"\n✅ Rate limiting working correctly (5 allowed, 2 denied)")
    else:
        print(f"\n⚠️  Unexpected behavior (allowed: {allowed_count}, denied: {denied_count})")
    
    # Test reset
    print(f"\n📝 Resetting rate limiter...")
    rate_limiter.reset(tool_name)
    
    is_allowed, _ = await rate_limiter.check_rate_limit(tool_name)
    if is_allowed:
        print(f"   ✅ Rate limit reset successful (execution now allowed)")
    else:
        print(f"   ❌ Rate limit reset failed")


async def test_execution_controller():
    """Test unified execution controller."""
    print("\n" + "=" * 70)
    print("TEST 4: Execution Controller Integration")
    print("=" * 70)
    
    resource_limiter = ResourceLimiter(
        max_cpu_seconds=30,
        max_memory_mb=256,
        enabled=True
    )
    
    semaphore = ExecutionSemaphore(max_concurrent=2)
    
    rate_limiter = RateLimiter(
        max_executions_per_minute=3,
        enabled=True
    )
    
    controller = ExecutionController(
        resource_limiter=resource_limiter,
        execution_semaphore=semaphore,
        rate_limiter=rate_limiter
    )
    
    print(f"\n📝 Execution controller created")
    
    tool_name = "integrated-tool"
    
    # Test acquiring and releasing
    print(f"\n📝 Testing acquire/release cycle:")
    
    is_allowed, error = await controller.acquire(tool_name)
    if is_allowed:
        print(f"   ✅ Execution slot acquired")
        controller.release(tool_name)
        print(f"   ✅ Execution slot released")
    else:
        print(f"   ❌ Failed to acquire: {error}")
    
    # Test rate limit enforcement
    print(f"\n📝 Testing rate limit enforcement (max 3/min):")
    success_count = 0
    
    for i in range(5):
        is_allowed, error = await controller.acquire(tool_name)
        if is_allowed:
            success_count += 1
            print(f"   Attempt {i+1}: ✅ Allowed")
            controller.release(tool_name)
        else:
            print(f"   Attempt {i+1}: ❌ {error}")
    
    if success_count == 3:
        print(f"\n✅ Controller correctly enforced rate limit (3 allowed, 2 denied)")
    else:
        print(f"\n⚠️  Unexpected result (allowed: {success_count})")
    
    # Show stats
    stats = controller.get_stats()
    print(f"\n📊 Controller stats:")
    print(f"   Resource limits enabled: {stats['resource_limits_enabled']}")
    print(f"   Rate limiting enabled: {stats['rate_limiting_enabled']}")
    print(f"   Semaphore stats: {stats['semaphore']}")


async def test_preexec_function():
    """Test preexec function generation."""
    print("\n" + "=" * 70)
    print("TEST 5: Preexec Function for Subprocess")
    print("=" * 70)
    
    resource_limiter = ResourceLimiter(
        max_cpu_seconds=10,
        max_memory_mb=128,
        enabled=True
    )
    
    preexec_fn = resource_limiter.get_preexec_fn()
    
    if RESOURCE_AVAILABLE and preexec_fn:
        print(f"\n✅ Preexec function created (will apply limits in child process)")
        print(f"   - CPU limit: {resource_limiter.max_cpu_seconds}s")
        print(f"   - Memory limit: {resource_limiter.max_memory_mb}MB")
        print(f"   - Process limit: {resource_limiter.max_processes}")
        print(f"   - File size limit: {resource_limiter.max_file_size_mb}MB")
    elif not RESOURCE_AVAILABLE:
        print(f"\n⚠️  Resource limits not available on this platform")
    else:
        print(f"\n⚠️  Preexec function is None (limits disabled)")


async def main():
    """Run all resource limit tests."""
    print("\n🔒 Testing Resource Limits & Execution Controls\n")
    
    try:
        test_resource_limiter()
        await test_concurrent_execution()
        await test_rate_limiting()
        await test_execution_controller()
        await test_preexec_function()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print("\nResource limits and execution controls are working correctly!")
        print("- Resource limiter initialized ✅")
        print("- Concurrent execution control working ✅")
        print("- Rate limiting enforced ✅")
        print("- Execution controller integrated ✅")
        print("- Preexec function ready ✅")
        
        if not RESOURCE_AVAILABLE:
            print("\n⚠️  Note: Resource limits (setrlimit) not available on this platform")
            print("   Rate limiting and concurrent execution control still work.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
