#!/usr/bin/env python3
"""
Logging Configuration Examples

Demonstrates different logging configurations for BVM client
"""

import logging
from bvm_client import BvmClient, setup_logging


def example_1_default_logging():
    """Example 1: Default logging (INFO to console, DEBUG to file)"""
    print("=== Example 1: Default Logging ===")
    print("Console: INFO and above | File: All DEBUG details\n")

    with BvmClient(config_file="bvm_config.yaml") as client:
        processors = client.get_processor_list()
        print(f"Found {len(processors)} processors")

    print("\nCheck 'bvm_client.log' for detailed debug information")
    print()


def example_2_quiet_mode():
    """Example 2: Quiet mode - only warnings/errors on console"""
    print("=== Example 2: Quiet Mode ===")
    print("Console: WARNING and above | File: All DEBUG details\n")

    with BvmClient(
        config_file="bvm_config.yaml",
        console_level=logging.WARNING  # Only warnings/errors on screen
    ) as client:
        processors = client.get_processor_list()
        print(f"Operation completed with {len(processors)} processors")

    print("\nNotice: No INFO messages on console, but logged to file")
    print()


def example_3_verbose_mode():
    """Example 3: Verbose mode - DEBUG on both console and file"""
    print("=== Example 3: Verbose Mode ===")
    print("Console: DEBUG | File: DEBUG\n")

    with BvmClient(
        config_file="bvm_config.yaml",
        console_level=logging.DEBUG  # Show everything on console
    ) as client:
        processors = client.get_processor_list()[:3]  # Just first 3
        print(f"\nShowing detailed logs for {len(processors)} processors")

    print("\nNotice: All DEBUG messages visible on console")
    print()


def example_4_custom_log_file():
    """Example 4: Custom log file location"""
    print("=== Example 4: Custom Log File ===")
    print("Using custom log file: 'my_app.log'\n")

    with BvmClient(
        config_file="bvm_config.yaml",
        log_file="my_app.log"  # Custom log file
    ) as client:
        processors = client.get_processor_list()
        print(f"Found {len(processors)} processors")

    print("\nCheck 'my_app.log' for this session's logs")
    print()


def example_5_production_mode():
    """Example 5: Production mode - minimal console output"""
    print("=== Example 5: Production Mode ===")
    print("Console: ERROR only | File: INFO and above\n")

    with BvmClient(
        config_file="bvm_config.yaml",
        log_file="production.log",
        console_level=logging.ERROR,  # Only errors on console
        file_level=logging.INFO      # Skip DEBUG in file
    ) as client:
        processors = client.get_processor_list()
        # Silent operation - no output unless error occurs

    print(f"Operation completed silently")
    print("Check 'production.log' for INFO-level logs")
    print()


def example_6_per_operation_logging():
    """Example 6: Different log files for different operations"""
    print("=== Example 6: Per-Operation Logging ===\n")

    # Operation 1: Processor query
    print("Step 1: Querying processors...")
    with BvmClient(config_file="bvm_config.yaml", log_file="step1_query.log") as client:
        processors = client.get_processor_list()
        print(f"✓ Found {len(processors)} processors")

    # Operation 2: Platform query
    print("\nStep 2: Querying platform...")
    with BvmClient(config_file="bvm_config.yaml", log_file="step2_platform.log") as client:
        proc_id, proc = client.get_processor_id("Rembrandt - Family 19h")
        plat_id, plat = client.get_platform_id(proc, "Rev_RMB_Mayan_Insyde_EDKII")
        print(f"✓ Platform ID: {plat_id}")

    print("\nEach step logged to separate file for easier debugging")
    print()


def example_7_global_logger_setup():
    """Example 7: Setup global logger for all BVM operations"""
    print("=== Example 7: Global Logger Setup ===\n")

    # Setup global logger once
    setup_logging(
        log_file="global_bvm.log",
        console_level=logging.INFO,
        file_level=logging.DEBUG
    )

    # All subsequent BvmClient instances will use this logger
    with BvmClient(config_file="bvm_config.yaml") as client1:
        print("Client 1 operation...")
        client1.get_processor_list()

    with BvmClient(config_file="bvm_config.yaml") as client2:
        print("Client 2 operation...")
        client2.get_processor_list()

    print("\nAll operations logged to 'global_bvm.log'")
    print()


if __name__ == "__main__":
    print("=== BVM Logging Examples ===\n")

    # Run only example 1 by default to avoid too much output
    example_1_default_logging()

    # Uncomment to try other examples:
    # example_2_quiet_mode()
    # example_3_verbose_mode()
    # example_4_custom_log_file()
    # example_5_production_mode()
    # example_6_per_operation_logging()
    # example_7_global_logger_setup()

    print("Examples completed! Check the .log files for detailed information.")
