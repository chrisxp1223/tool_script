"""
PSP Replacement Practical Usage Examples

Demonstrates how to use PSP Replacement v2 for various operations
"""

from psp_replacement_v2 import PspReplacer, EntryOperationType
from bvm_config import BvmConfig


def example_1_replace_smu():
    """Example 1: Replace SMU firmware"""
    print("\n" + "="*60)
    print("Example 1: Replace SMU Firmware")
    print("="*60)

    # Load configuration
    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # Set file paths
    smu_binary = config.get_binary_path("SMU_46.59.0.bin")
    download_path = config.get_download_path("smu_updated.FD")

    # Create replacement list
    replacement_list = [
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",              # SMU firmware type
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": smu_binary,
            "level": "0x2A",            # BIOS L2 directory A
            "dirIndex": "0x1",
            "detail": "Update SMU to 46.59.0",
            "isPspEntry": True
        }
    ]

    print(f"Platform: {config.platform_name}")
    print(f"PSP Config: {config.psp_config}")
    print(f"SMU Binary: {smu_binary}")
    print(f"Download to: {download_path}")
    print()

    # Execute (uncomment to actually run)
    print("⚠️  Uncomment below to execute:")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print("#     revision='TRM1004B_804_804',  # Your BIOS version")
    print("#     download_path=download_path")
    print("# )")
    print("# print(f'✓ Request ID: {request_id}')")


def example_2_multiple_entries():
    """Example 2: Modify multiple entries"""
    print("\n" + "="*60)
    print("Example 2: Modify Multiple PSP Entries")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # Modify multiple entries
    replacement_list = [
        # SMU firmware
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": config.get_binary_path("SMU.bin"),
            "level": "0x2A",
            "dirIndex": "0x1",
            "detail": "Update SMU",
            "isPspEntry": True
        },
        # PSP Bootloader
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x2",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": config.get_binary_path("PSPBootloader.bin"),
            "level": "0x2",
            "dirIndex": "0x1",
            "detail": "Update PSP Bootloader",
            "isPspEntry": True
        }
    ]

    print(f"Will modify {len(replacement_list)} entries:")
    for i, entry in enumerate(replacement_list, 1):
        print(f"  {i}. Type {entry['type']}: {entry.get('detail', 'N/A')}")

    print()
    print("⚠️  Uncomment to execute")


def example_3_point_entry():
    """Example 3: Using POINT_ENTRY"""
    print("\n" + "="*60)
    print("Example 3: Using POINT_ENTRY (pointing to specific offset)")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")

    replacement_list = [
        {
            "entryType": "POINT_ENTRY",
            "type": "0x4",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": config.get_binary_path("firmware.bin"),
            "level": "0x2",
            "dirIndex": "0x1",
            "isPspEntry": True,
            # POINT_ENTRY requires offset and size
            "offset": "0x855000",
            "size": "0x20000"
        }
    ]

    print("POINT_ENTRY example:")
    print(f"  Offset: {replacement_list[0]['offset']}")
    print(f"  Size: {replacement_list[0]['size']}")
    print()


def example_4_signed_bios():
    """Example 4: Sign BIOS"""
    print("\n" + "="*60)
    print("Example 4: BIOS Signing")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # Get signing configuration
    token_file = config.get_token_path(
        config.get("psp.signing.token_file", "token.stkn")
    )
    key_size = config.get("psp.signing.key_size", "0x200")

    replacement_list = [
        # Your main modification (e.g. SMU)
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": config.get_binary_path("SMU.bin"),
            "level": "0x2A",
            "dirIndex": "0x1",
            "isPspEntry": True
        },
        # === Signing required entries ===
        # Type 0x5 - Signing Key Token (BIOS L2 A)
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x5",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": token_file,
            "level": "0x2A",
            "dirIndex": "0x0",
            "isPspEntry": False
        },
        # Type 0x5 - Signing Key Token (BIOS L2 B)
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x5",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": token_file,
            "level": "0x2B",
            "dirIndex": "0x1",
            "isPspEntry": False
        },
        # Type 0x7 - RTM Signature (BIOS L2 A)
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x7",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Add.value,
            "filename": "",  # Signing entry doesn't need file
            "size": key_size,
            "level": "0x2A",
            "dirIndex": "0x0",
            "isPspEntry": False
        },
        # Type 0x7 - RTM Signature (BIOS L2 B)
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x7",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Add.value,
            "filename": "",
            "size": key_size,
            "level": "0x2B",
            "dirIndex": "0x1",
            "isPspEntry": False
        }
    ]

    print("Signing configuration:")
    print(f"  Token file: {token_file}")
    print(f"  Key Size: {key_size}")
    print(f"  Total {len(replacement_list)} entries (1 modification + 4 signing)")
    print()

    print("When executing, specify sign_type='PK':")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print("#     revision='your_revision',")
    print("#     sign_type='PK',  # Enable signing")
    print("#     download_path='signed_bios.FD'")
    print("# )")


def example_5_user_generated_bios():
    """Example 5: Use custom BIOS file"""
    print("\n" + "="*60)
    print("Example 5: Using User-Generated BIOS")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # Use local BIOS file
    local_bios = r"D:\MyBIOS\custom_bios.FD"

    replacement_list = [
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": config.get_binary_path("SMU.bin"),
            "level": "0x2A",
            "dirIndex": "0x1",
            "isPspEntry": True
        }
    ]

    print(f"Using custom BIOS: {local_bios}")
    print()
    print("Execute:")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print(f"#     bios_type='User-Generated',")
    print(f"#     revision=r'{local_bios}',")
    print("#     download_path='output.FD'")
    print("# )")


def example_6_check_available_operations():
    """Example 6: Check available operations"""
    print("\n" + "="*60)
    print("Example 6: Check Available PSP Operations")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    try:
        operations = replacer.get_available_operations()
        print("Available operation types:")
        for key, value in operations.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Cannot get operation types: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PSP Replacement v2.0 - Practical Usage Examples")
    print("="*60)

    try:
        example_1_replace_smu()
        example_2_multiple_entries()
        example_3_point_entry()
        example_4_signed_bios()
        example_5_user_generated_bios()
        example_6_check_available_operations()

        print("\n" + "="*60)
        print("All examples displayed!")
        print("="*60)
        print()
        print("Reminder:")
        print("1. Actual execution in examples is commented out")
        print("2. Before uncommenting, verify:")
        print("   - BIOS version is correct")
        print("   - Binary files exist")
        print("   - Download paths are correct")
        print("3. Recommend testing in test environment first")

    except Exception as e:
        print(f"\nError: {e}")
