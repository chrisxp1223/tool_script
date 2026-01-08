"""
BVM Config File Usage Examples

Demonstrates how to use bvm_config.yaml to manage settings
"""

from bvm_config import BvmConfig
from bvm_client import BvmClient

def example_1_basic_config():
    """Example 1: Basic config loading"""
    print("=== Example 1: Basic Config Loading ===")

    config = BvmConfig("bvm_config.yaml")

    print(f"Username: {config.username}")
    print(f"Processor: {config.processor_name}")
    print(f"Platform: {config.platform_name}")
    print(f"Binary Dir: {config.binary_dir}")
    print(f"Download Dir: {config.download_dir}")
    print()


def example_2_file_paths():
    """Example 2: File path handling"""
    print("=== Example 2: File Path Handling ===")

    config = BvmConfig("bvm_config.yaml")

    # Get full paths
    smu_binary = config.get_binary_path("SMU_46.59.0.bin")
    output_bios = config.get_download_path("output.FD")
    token_file = config.get_token_path("Rembrandt-4K-BIOS-SBR-0110.stkn")

    print(f"SMU Binary: {smu_binary}")
    print(f"Output BIOS: {output_bios}")
    print(f"Token File: {token_file}")
    print()


def example_3_client_with_config():
    """Example 3: Create BVM client with config"""
    print("=== Example 3: Create Client with Config ===")

    # Method 1: Pass config file path directly
    client = BvmClient(config_file="bvm_config.yaml")
    print(f"Client created for user: {client.username}")

    # Method 2: Create config first, then pass to client
    config = BvmConfig("bvm_config.yaml")
    client2 = BvmClient(config=config)

    # Can use config's file path functionality
    if client.config:
        download_path = client.config.get_download_path("modified_bios.FD")
        print(f"Will download to: {download_path}")

    # Logout when done
    client.logout()
    client2.logout()
    print()


def example_4_psp_replacement_scenario():
    """Example 4: PSP Replacement complete scenario"""
    print("=== Example 4: PSP Replacement Scenario ===")

    config = BvmConfig("bvm_config.yaml")

    # Create replacement list
    smu_binary = config.get_binary_path(config.get("psp.smu_firmware", "SMU_46.59.0.bin"))

    replacement_list = [
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": 2,  # Modify
            "filename": smu_binary,
            "level": "0x2A",
            "dirIndex": "0x1",
            "detail": "Auto updated via config",
            "isPspEntry": True
        }
    ]

    print("Replacement list created:")
    print(f"  - SMU firmware: {smu_binary}")
    print(f"  - Entry type: 0x8 (SMU)")
    print(f"  - Operation: Modify")

    # Download path
    download_path = config.get_download_path(f"modified_{config.psp_config}_bios.FD")
    print(f"\nWill download to: {download_path}")
    print()


def example_5_signing_config():
    """Example 5: BIOS signing configuration"""
    print("=== Example 5: BIOS Signing Configuration ===")

    config = BvmConfig("bvm_config.yaml")

    # Read signing parameters from config
    sign_type = config.get("psp.signing.sp_function")
    token_file = config.get_token_path(config.get("psp.signing.token_file"))
    key_size = config.get("psp.signing.key_size")

    print(f"Sign Type: {sign_type}")
    print(f"Token File: {token_file}")
    print(f"Key Size: {key_size}")

    # Create signing entries
    signing_entries = [
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x5",
            "operation": 2,  # Modify
            "filename": token_file,
            "level": "0x2A",
            "dirIndex": "0x0",
            "isPspEntry": False
        },
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x7",
            "operation": 0,  # Add
            "filename": "",
            "size": key_size,
            "level": "0x2A",
            "dirIndex": "0x0",
            "isPspEntry": False
        }
    ]

    print(f"\nCreated {len(signing_entries)} signing entries")
    print()


def example_6_option_rom_config():
    """Example 6: Option ROM configuration"""
    print("=== Example 6: Option ROM Configuration ===")

    config = BvmConfig("bvm_config.yaml")

    # Read Option ROM list from config
    roms = config.get("option_rom.roms", [])

    replacement_list = []
    for rom in roms:
        rom_path = config.get_binary_path(rom["file"])
        replacement_list.append({
            "guid": rom["guid"],
            "file": rom_path
        })
        print(f"ROM: {rom['guid']}")
        print(f"  -> {rom_path}")

    print(f"\nTotal: {len(replacement_list)} Option ROMs")
    print()


def example_7_modify_and_save():
    """Example 7: Modify config and save"""
    print("=== Example 7: Modify Config and Save ===")

    config = BvmConfig("bvm_config.yaml")

    # Modify config value
    old_purpose = config.purpose
    config.set("defaults.purpose", "Modified purpose for testing")

    print(f"Old purpose: {old_purpose}")
    print(f"New purpose: {config.purpose}")

    # Save to new file
    # config.save("bvm_config_modified.yaml")
    print("\n(Not actually saved to avoid modifying original file)")

    # Restore original value
    config.set("defaults.purpose", old_purpose)
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BVM Config File Usage Examples")
    print("="*60 + "\n")

    try:
        example_1_basic_config()
        example_2_file_paths()
        # example_3_client_with_config()  # Requires BVM server connection
        example_4_psp_replacement_scenario()
        example_5_signing_config()
        example_6_option_rom_config()
        example_7_modify_and_save()

        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60 + "\n")

    except FileNotFoundError as e:
        print(f"\nError: Config file not found")
        print(f"Please create bvm_config.yaml first")
        print(f"You can run: python bvm_config.py")

    except Exception as e:
        print(f"\nError: {e}")
