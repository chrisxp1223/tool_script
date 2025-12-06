#!/usr/bin/env python3
"""
Context Manager Usage Example

Demonstrates automatic logout using 'with' statement
"""

from bvm_client import BvmClient
from psp_replacement_v2 import PspReplacer


def example_1_basic_context_manager():
    """Example 1: Basic context manager usage"""
    print("=== Example 1: Basic Context Manager ===")

    with BvmClient(config_file="bvm_config.yaml") as client:
        print(f"✓ Logged in as: {client.username}")
        processors = client.get_processor_list()
        print(f"✓ Found {len(processors)} processors")
        # Automatically logs out when exiting 'with' block

    print("✓ Automatically logged out\n")


def example_2_psp_with_context_manager():
    """Example 2: PSP Replacement with context manager"""
    print("=== Example 2: PSP Replacement with Context Manager ===")

    with PspReplacer(config_file="bvm_config.yaml") as replacer:
        print(f"✓ Logged in as: {replacer.username}")
        print(f"✓ Platform: {replacer.config.platform_name}")

        # Your PSP replacement operations here
        # replacer.replace_psp_entries(...)

        # Automatically logs out when done

    print("✓ Automatically logged out\n")


def example_3_exception_handling():
    """Example 3: Exception handling with context manager"""
    print("=== Example 3: Exception Handling ===")

    try:
        with BvmClient(config_file="bvm_config.yaml") as client:
            print(f"✓ Logged in as: {client.username}")

            # Even if an exception occurs, logout is guaranteed
            # raise Exception("Simulated error")

            print("✓ Operations completed")

    except Exception as e:
        print(f"✗ Error occurred: {e}")

    print("✓ Automatically logged out even if error occurred\n")


def example_4_traditional_vs_context_manager():
    """Example 4: Traditional vs Context Manager comparison"""
    print("=== Example 4: Traditional vs Context Manager ===\n")

    print("Traditional way (manual logout):")
    client = BvmClient(config_file="bvm_config.yaml")
    print(f"  Logged in as: {client.username}")
    # ... do operations ...
    client.logout()
    print("  Manually logged out")

    print("\nContext Manager way (automatic logout):")
    with BvmClient(config_file="bvm_config.yaml") as client:
        print(f"  Logged in as: {client.username}")
        # ... do operations ...
    print("  Automatically logged out\n")


if __name__ == "__main__":
    print("=== BVM Context Manager Examples ===\n")

    example_1_basic_context_manager()
    example_2_psp_with_context_manager()
    example_3_exception_handling()
    example_4_traditional_vs_context_manager()

    print("All examples completed!")
