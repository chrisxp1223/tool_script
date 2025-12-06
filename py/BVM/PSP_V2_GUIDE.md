## PSP Replacement v2.0 使用指南

### 改進點

相比舊版 `PspReplacement.py`:

| 功能 | 舊版 | v2.0 |
|------|------|------|
| 配置管理 | ❌ 硬編碼 | ✅ 使用配置檔案 |
| 路徑處理 | ❌ 手動輸入完整路徑 | ✅ 自動處理 |
| 程式碼重複 | ❌ 200+ 行重複程式碼 | ✅ 繼承基礎類別 |
| 錯誤處理 | ❌ 返回 None | ✅ 拋出例外 |
| 物件導向 | ❌ 函數式 | ✅ 類別式 |
| 平台配置 | ❌ 每次都要輸入 | ✅ 從配置讀取 |

### 快速開始

```python
from psp_replacement_v2 import PspReplacer, EntryOperationType
from bvm_config import BvmConfig

# 1. 載入配置
config = BvmConfig("bvm_config.yaml")
replacer = PspReplacer(config=config)

# 2. 建立 replacement list
replacement_list = [
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x8",              # SMU firmware
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

# 3. 執行替換
request_id = replacer.replace_psp_entries(
    replacement_list=replacement_list,
    revision="TRM1004B_804_804",
    download_path=config.get_download_path("output.FD")
)

print(f"Request ID: {request_id}")
```

### 使用範例

#### 1. 基本 SMU 替換

```python
config = BvmConfig("bvm_config.yaml")
replacer = PspReplacer(config=config)

replacement_list = [{
    "entryType": "IMAGE_ENTRY",
    "type": "0x8",
    "romId": "0x0",
    "instance": "0x0",
    "subProgram": "0x0",
    "operation": EntryOperationType.Modify.value,
    "filename": config.get_binary_path("SMU_46.59.0.bin"),
    "level": "0x2A",
    "dirIndex": "0x1",
    "detail": "Update to 46.59.0",
    "isPspEntry": True
}]

request_id = replacer.replace_psp_entries(
    replacement_list=replacement_list,
    revision="TRM1004B_804_804",
    download_path=config.get_download_path("smu_updated.FD")
)
```

#### 2. 修改多個條目

```python
replacement_list = [
    # SMU
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x8",
        "operation": EntryOperationType.Modify.value,
        "filename": config.get_binary_path("SMU.bin"),
        # ... 其他欄位
    },
    # PSP Bootloader
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x2",
        "operation": EntryOperationType.Modify.value,
        "filename": config.get_binary_path("PSPBootloader.bin"),
        # ... 其他欄位
    }
]

request_id = replacer.replace_psp_entries(
    replacement_list=replacement_list,
    revision="your_revision",
    download_path="output.FD"
)
```

#### 3. BIOS 簽署

```python
# 從配置讀取簽署資訊
token_file = config.get_token_path(
    config.get("psp.signing.token_file")
)
key_size = config.get("psp.signing.key_size")

replacement_list = [
    # 你的修改
    {...},

    # 簽署條目 (Type 0x5 + 0x7)
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x5",
        "operation": EntryOperationType.Modify.value,
        "filename": token_file,
        "level": "0x2A",
        "dirIndex": "0x0",
        "isPspEntry": False
    },
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x7",
        "operation": EntryOperationType.Add.value,
        "filename": "",
        "size": key_size,
        "level": "0x2A",
        "dirIndex": "0x0",
        "isPspEntry": False
    }
]

request_id = replacer.replace_psp_entries(
    replacement_list=replacement_list,
    revision="your_revision",
    sign_type="PK",  # 啟用簽署
    download_path="signed.FD"
)
```

#### 4. 使用 User-Generated BIOS

```python
request_id = replacer.replace_psp_entries(
    replacement_list=replacement_list,
    bios_type="User-Generated",
    revision=r"D:\MyBIOS\custom.FD",  # 本地檔案
    download_path="output.FD"
)
```

#### 5. POINT_ENTRY (指定偏移)

```python
replacement_list = [{
    "entryType": "POINT_ENTRY",
    "type": "0x4",
    "operation": EntryOperationType.Modify.value,
    "filename": config.get_binary_path("firmware.bin"),
    "level": "0x2",
    "dirIndex": "0x1",
    "isPspEntry": True,
    # POINT_ENTRY 特有欄位
    "offset": "0x855000",
    "size": "0x20000"
}]
```

### 參數說明

#### replace_psp_entries() 參數

| 參數 | 必填 | 說明 | 預設值 |
|------|------|------|--------|
| `replacement_list` | ✅ | PSP 條目清單 | - |
| `revision` | ✅ | BIOS 版本 | - |
| `processor_name` | ❌ | 處理器名稱 | 從配置讀取 |
| `platform_name` | ❌ | 平台名稱 | 從配置讀取 |
| `bios_type` | ❌ | BIOS 類型 | 從配置讀取 |
| `psp_config` | ❌ | PSP 配置 | 從配置讀取 |
| `purpose` | ❌ | 目的說明 | 從配置讀取 |
| `sign_type` | ❌ | 簽署類型 | 從配置讀取 (NOSIGN) |
| `download_path` | ❌ | 下載路徑 | None (不下載) |

### Entry 類型

#### IMAGE_ENTRY (完整檔案)
```python
{
    "entryType": "IMAGE_ENTRY",
    "type": "0x8",           # Entry type
    "filename": "path.bin",  # 檔案路徑
    # ... 標準欄位
}
```

#### POINT_ENTRY (偏移量)
```python
{
    "entryType": "POINT_ENTRY",
    "type": "0x4",
    "filename": "path.bin",
    "offset": "0x855000",    # 必須
    "size": "0x20000",       # 必須
    # ... 標準欄位
}
```

#### VALUE_ENTRY (數值)
```python
{
    "entryType": "VALUE_ENTRY",
    "type": "0xb",
    "value": "0x1",          # 必須
    # ... 標準欄位
}
```

### 標準欄位

所有 entry 都需要:

```python
{
    "entryType": "...",          # IMAGE_ENTRY | POINT_ENTRY | VALUE_ENTRY
    "type": "0x..",              # PSP entry type
    "romId": "0x0",              # 通常是 0x0
    "instance": "0x0",           # 通常是 0x0
    "subProgram": "0x0",         # Sub-program index
    "operation": 0/1/2,          # Add(0) | Remove(1) | Modify(2)
    "level": "0x..",             # 0x1/0x2 (PSP) or 0x2A/0x2B (BIOS)
    "dirIndex": "0x.",           # Directory index
    "isPspEntry": True/False,    # PSP entry or BIOS entry
    "detail": "..."              # 可選: 說明
}
```

### 常見 PSP Entry Types

| Type | 說明 |
|------|------|
| `0x2` | PSP Bootloader |
| `0x8` | SMU Firmware |
| `0x12` | PSP S3 Resume Firmware |
| `0x30` | AGESA Binary |
| `0x60` | APCB Data |

### Directory Levels

| Level | 說明 |
|-------|------|
| `0x1` | PSP L1 directory |
| `0x2` | PSP L2 directory |
| `0x2A` | BIOS L2 directory (A copy) |
| `0x2B` | BIOS L2 directory (B copy) |

### 錯誤處理

v2.0 使用例外處理:

```python
try:
    request_id = replacer.replace_psp_entries(
        replacement_list=replacement_list,
        revision="TRM1004B_804_804",
        download_path="output.FD"
    )
    print(f"成功! Request ID: {request_id}")

except FileNotFoundError as e:
    print(f"檔案不存在: {e}")
except ValueError as e:
    print(f"參數錯誤: {e}")
except Exception as e:
    print(f"執行失敗: {e}")
```

### 與舊版對比

#### 舊版 (PspReplacement.py)

```python
# 硬編碼所有設定
username = "lahan"
password = "*"
processorName = "Rembrandt - Family 19h"
platformName = "Rev_RMB_Mayan_Insyde_EDKII"
downloadPath = "D:\\temp\\1.FD"

replacementList = [{
    "filename": "C:\\Users\\lahan\\Desktop\\BVM\\SMU.bin",
    # ...
}]

# 執行
main()
```

#### v2.0 (psp_replacement_v2.py)

```python
# 從配置載入
config = BvmConfig("bvm_config.yaml")
replacer = PspReplacer(config=config)

# 使用配置的路徑
replacementList = [{
    "filename": config.get_binary_path("SMU.bin"),
    # ...
}]

# 執行 (所有設定從配置讀取)
request_id = replacer.replace_psp_entries(
    replacement_list=replacementList,
    revision="TRM1004B_804_804",
    download_path=config.get_download_path("output.FD")
)
```

### 更多範例

查看 `psp_example.py` 獲取 6 個完整範例:

```bash
python psp_example.py
```

### 下一步

- [ ] 整合 CBS Override v2
- [ ] 整合 Option ROM Replacement v2
- [ ] 整合 Compare PSP Entry v2
- [ ] 建立統一 CLI 工具
