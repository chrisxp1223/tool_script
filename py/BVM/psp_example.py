"""
PSP Replacement 實際使用範例

展示如何使用 PSP Replacement v2 進行各種操作
"""

from psp_replacement_v2 import PspReplacer, EntryOperationType
from bvm_config import BvmConfig


def example_1_replace_smu():
    """範例 1: 替換 SMU 韌體"""
    print("\n" + "="*60)
    print("範例 1: 替換 SMU 韌體")
    print("="*60)

    # 載入配置
    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # 設定檔案路徑
    smu_binary = config.get_binary_path("SMU_46.59.0.bin")
    download_path = config.get_download_path("smu_updated.FD")

    # 建立 replacement list
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

    # 執行 (取消註解來實際執行)
    print("⚠️  取消下面的註解來實際執行:")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print("#     revision='TRM1004B_804_804',  # 你的 BIOS 版本")
    print("#     download_path=download_path")
    print("# )")
    print("# print(f'✓ Request ID: {request_id}')")


def example_2_multiple_entries():
    """範例 2: 修改多個條目"""
    print("\n" + "="*60)
    print("範例 2: 修改多個 PSP 條目")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # 修改多個條目
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

    print(f"將修改 {len(replacement_list)} 個條目:")
    for i, entry in enumerate(replacement_list, 1):
        print(f"  {i}. Type {entry['type']}: {entry.get('detail', 'N/A')}")

    print()
    print("⚠️  實際執行請取消註解")


def example_3_point_entry():
    """範例 3: 使用 POINT_ENTRY"""
    print("\n" + "="*60)
    print("範例 3: 使用 POINT_ENTRY (指向特定偏移)")
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
            # POINT_ENTRY 需要指定 offset 和 size
            "offset": "0x855000",
            "size": "0x20000"
        }
    ]

    print("POINT_ENTRY 範例:")
    print(f"  Offset: {replacement_list[0]['offset']}")
    print(f"  Size: {replacement_list[0]['size']}")
    print()


def example_4_signed_bios():
    """範例 4: 簽署 BIOS"""
    print("\n" + "="*60)
    print("範例 4: BIOS 簽署")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # 取得簽署配置
    token_file = config.get_token_path(
        config.get("psp.signing.token_file", "token.stkn")
    )
    key_size = config.get("psp.signing.key_size", "0x200")

    replacement_list = [
        # 你的主要修改 (例如 SMU)
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
        # === 簽署所需條目 ===
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
            "filename": "",  # 簽名條目不需要檔案
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

    print("簽署配置:")
    print(f"  Token 檔案: {token_file}")
    print(f"  Key Size: {key_size}")
    print(f"  總共 {len(replacement_list)} 個條目 (1 個修改 + 4 個簽署)")
    print()

    print("執行時需要指定 sign_type='PK':")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print("#     revision='your_revision',")
    print("#     sign_type='PK',  # 啟用簽署")
    print("#     download_path='signed_bios.FD'")
    print("# )")


def example_5_user_generated_bios():
    """範例 5: 使用自訂 BIOS 檔案"""
    print("\n" + "="*60)
    print("範例 5: 使用 User-Generated BIOS")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    # 使用本地 BIOS 檔案
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

    print(f"使用自訂 BIOS: {local_bios}")
    print()
    print("執行:")
    print("# request_id = replacer.replace_psp_entries(")
    print("#     replacement_list=replacement_list,")
    print(f"#     bios_type='User-Generated',")
    print(f"#     revision=r'{local_bios}',")
    print("#     download_path='output.FD'")
    print("# )")


def example_6_check_available_operations():
    """範例 6: 查看可用的操作"""
    print("\n" + "="*60)
    print("範例 6: 查看可用的 PSP 操作")
    print("="*60)

    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    try:
        operations = replacer.get_available_operations()
        print("可用的操作類型:")
        for key, value in operations.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"無法取得操作類型: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PSP Replacement v2.0 - 實際使用範例")
    print("="*60)

    try:
        example_1_replace_smu()
        example_2_multiple_entries()
        example_3_point_entry()
        example_4_signed_bios()
        example_5_user_generated_bios()
        example_6_check_available_operations()

        print("\n" + "="*60)
        print("所有範例顯示完成！")
        print("="*60)
        print()
        print("提醒:")
        print("1. 範例中的實際執行都已註解")
        print("2. 取消註解前請確認:")
        print("   - BIOS 版本正確")
        print("   - 二進制檔案存在")
        print("   - 下載路徑正確")
        print("3. 建議先在測試環境執行")

    except Exception as e:
        print(f"\n錯誤: {e}")
