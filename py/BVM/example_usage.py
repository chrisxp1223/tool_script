"""
BVM 配置檔案使用範例

示範如何使用 bvm_config.yaml 來管理設定
"""

from bvm_config import BvmConfig
from bvm_client import BvmClient

def example_1_basic_config():
    """範例 1: 基本配置載入"""
    print("=== 範例 1: 基本配置載入 ===")

    config = BvmConfig("bvm_config.yaml")

    print(f"Username: {config.username}")
    print(f"Processor: {config.processor_name}")
    print(f"Platform: {config.platform_name}")
    print(f"Binary Dir: {config.binary_dir}")
    print(f"Download Dir: {config.download_dir}")
    print()


def example_2_file_paths():
    """範例 2: 檔案路徑處理"""
    print("=== 範例 2: 檔案路徑處理 ===")

    config = BvmConfig("bvm_config.yaml")

    # 取得完整路徑
    smu_binary = config.get_binary_path("SMU_46.59.0.bin")
    output_bios = config.get_download_path("output.FD")
    token_file = config.get_token_path("Rembrandt-4K-BIOS-SBR-0110.stkn")

    print(f"SMU Binary: {smu_binary}")
    print(f"Output BIOS: {output_bios}")
    print(f"Token File: {token_file}")
    print()


def example_3_client_with_config():
    """範例 3: 使用配置建立 BVM 客戶端"""
    print("=== 範例 3: 使用配置建立客戶端 ===")

    # 方式 1: 直接傳入配置檔案路徑
    client = BvmClient(config_file="bvm_config.yaml")
    print(f"Client created for user: {client.username}")

    # 方式 2: 先建立配置，再傳入
    config = BvmConfig("bvm_config.yaml")
    client2 = BvmClient(config=config)

    # 可以使用配置的檔案路徑功能
    if client.config:
        download_path = client.config.get_download_path("modified_bios.FD")
        print(f"Will download to: {download_path}")

    # 完成後登出
    client.logout()
    client2.logout()
    print()


def example_4_psp_replacement_scenario():
    """範例 4: PSP Replacement 完整場景"""
    print("=== 範例 4: PSP Replacement 場景 ===")

    config = BvmConfig("bvm_config.yaml")

    # 建立 replacementList
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

    # 下載路徑
    download_path = config.get_download_path(f"modified_{config.psp_config}_bios.FD")
    print(f"\nWill download to: {download_path}")
    print()


def example_5_signing_config():
    """範例 5: BIOS 簽署配置"""
    print("=== 範例 5: BIOS 簽署配置 ===")

    config = BvmConfig("bvm_config.yaml")

    # 從配置讀取簽署參數
    sign_type = config.get("psp.signing.sp_function")
    token_file = config.get_token_path(config.get("psp.signing.token_file"))
    key_size = config.get("psp.signing.key_size")

    print(f"Sign Type: {sign_type}")
    print(f"Token File: {token_file}")
    print(f"Key Size: {key_size}")

    # 建立簽署所需的條目
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
    """範例 6: Option ROM 配置"""
    print("=== 範例 6: Option ROM 配置 ===")

    config = BvmConfig("bvm_config.yaml")

    # 從配置讀取 Option ROM 清單
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
    """範例 7: 修改配置並儲存"""
    print("=== 範例 7: 修改配置並儲存 ===")

    config = BvmConfig("bvm_config.yaml")

    # 修改配置值
    old_purpose = config.purpose
    config.set("defaults.purpose", "Modified purpose for testing")

    print(f"Old purpose: {old_purpose}")
    print(f"New purpose: {config.purpose}")

    # 儲存到新檔案
    # config.save("bvm_config_modified.yaml")
    print("\n(未實際儲存，避免修改原始檔案)")

    # 恢復原始值
    config.set("defaults.purpose", old_purpose)
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BVM 配置檔案使用範例")
    print("="*60 + "\n")

    try:
        example_1_basic_config()
        example_2_file_paths()
        # example_3_client_with_config()  # 需要 BVM 伺服器連線
        example_4_psp_replacement_scenario()
        example_5_signing_config()
        example_6_option_rom_config()
        example_7_modify_and_save()

        print("\n" + "="*60)
        print("所有範例執行完成!")
        print("="*60 + "\n")

    except FileNotFoundError as e:
        print(f"\n錯誤: 找不到配置檔案")
        print(f"請先建立 bvm_config.yaml")
        print(f"可以執行: python bvm_config.py")

    except Exception as e:
        print(f"\n錯誤: {e}")
