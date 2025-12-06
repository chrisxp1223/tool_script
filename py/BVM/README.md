# BVM API Client Tools

AMD BIOS Validation Manager (BVM) 的 Python API 客戶端工具集合，用於自動化 BIOS 修改、CBS 覆寫、PSP 條目替換及比較等操作。

## 功能概覽

| 工具 | 功能 | 版本 |
|------|------|------|
| `PspReplacement.py` | PSP 條目的增刪改操作 | v1.03 |
| `CbsOverride.py` | CBS 設定覆寫 | v1.03 |
| `BinaryCbsOverride.py` | 二進制級別 CBS 覆寫 | v1.00 |
| `OptionRomReplacement.py` | BIOS Option ROM 替換 | v1.00 |
| `ComparePSPEntry.py` | 比較兩個 BIOS 版本的 PSP 條目差異 | v1.00 |

## 環境需求

```bash
pip install requests
```

Python 3.6+

## 快速開始

### 1. PSP 條目替換

```python
# 編輯 PspReplacement.py
username = "your_username"
password = "your_password"

processorName = "Rembrandt - Family 19h"
platformName = "Rev_RMB_Mayan_Insyde_EDKII"
baseBIOSType = "PI BIOS"
revision = "TRM1004B_804_804"
pspConfig = "RMB"

replacementList = [
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x8",              # SMU 韌體
        "romId": "0x0",
        "instance": "0x0",
        "subProgram": "0x0",
        "operation": EntryOperationType.Modify.value,
        "filename": "C:\\path\\to\\SMU_46.59.0.bin",
        "level": "0x2A",
        "dirIndex": "0x1",
        "detail": "4.30.18.0 -> 46.59.0",
        "isPspEntry": True
    }
]

# 執行
python PspReplacement.py
```

### 2. CBS 設定覆寫

```python
# 編輯 CbsOverride.py
replacementList = [
    {"CbsCmnCpuSmuPspDebugMode": "0"},
    {"CbsDbgRomArmorSupport": "0"}
]

# 執行
python CbsOverride.py
```

### 3. Option ROM 替換

```python
# 編輯 OptionRomReplacement.py
replacementList = [
    {
        "guid": "348C4D62-BFBD-4882-9ECE-C80BB1C4783B",
        "file": r"D:\path\to\OptionRom3.bin"
    }
]

# 執行
python OptionRomReplacement.py
```

### 4. PSP 條目比較

```python
# 編輯 ComparePSPEntry.py
# Base BIOS
BASE_BIOS_TYPE = "Weekly BIOS"
REVISION = "WBK5709N_196"

# Compare BIOS
CMP_BIOS_TYPE = "User-Generated"
CMP_REVISION = r"D:\Input\BVM\WBK4B06N_102.FD"

# 執行
python ComparePSPEntry.py
```

## Base BIOS 類型

所有工具都支援 4 種 base BIOS 來源：

### Weekly BIOS
```python
baseBIOSType = "Weekly BIOS"
revision = "WXB4110N_312"
```

### PI BIOS
```python
baseBIOSType = "PI BIOS"
revision = "TXB0076C_313"
```

### User-Generated (本地檔案)
```python
baseBIOSType = "User-Generated"
revision = r"D:\temp\myBIOS.FD"
```

### By Request Id (使用先前的 BVM 請求)
```python
baseBIOSType = "By Request Id"
revision = "862589"
```

## PSP Replacement 詳細說明

### 條目操作類型

```python
from enum import Enum

class EntryOperationType(Enum):
    Add = 0      # 新增條目
    Remove = 1   # 移除條目
    Modify = 2   # 修改條目
```

### PSP 條目類型

#### IMAGE_ENTRY - 完整二進制檔案
```python
{
    "entryType": "IMAGE_ENTRY",
    "type": "0x8",              # Entry type (例如: 0x8=SMU, 0x2=PSP bootloader)
    "operation": EntryOperationType.Modify.value,
    "filename": "C:\\path\\to\\binary.bin",
    "level": "0x2A",            # Directory level
    "dirIndex": "0x1",
    "isPspEntry": True
}
```

#### POINT_ENTRY - 指向偏移量
```python
{
    "entryType": "POINT_ENTRY",
    "type": "0x4",
    "operation": EntryOperationType.Modify.value,
    "filename": "C:\\path\\to\\binary.bin",
    "level": "0x2",
    "dirIndex": "0x1",
    "isPspEntry": True,
    "offset": "0x855000",       # 必須指定
    "size": "0x20000"           # 必須指定
}
```

#### VALUE_ENTRY - 僅包含值
```python
{
    "entryType": "VALUE_ENTRY",
    "type": "0xb",
    "operation": EntryOperationType.Modify.value,
    "level": "0x2A",
    "dirIndex": "0x1",
    "isPspEntry": True,
    "value": "0x1"              # 必須指定
}
```

### PSP Directory 層級

| Level | 說明 |
|-------|------|
| `0x1` | PSP L1 directory |
| `0x2` | PSP L2 directory |
| `0x2A` | BIOS L2 directory (A copy) |
| `0x2B` | BIOS L2 directory (B copy) |

### 常見 PSP Entry Type

| Type | 說明 |
|------|------|
| `0x2` | PSP Bootloader |
| `0x8` | SMU Firmware |
| `0x12` | PSP S3 Resume Firmware |
| `0x30` | AGESA Binary |
| `0x60` | APCB Data |
| `0x68` | APCB Backup |

完整清單請參考 AMD PPR 文件。

## BIOS 簽署

當需要簽署 BIOS 時：

```python
signType = "PK"                          # NOSIGN=停用, PK=啟用
signUserName = username
signPassword = password
signSpFunction = "SIGN REMBRANDT BIOS (4K)"  # 平台特定
signHP = "0"
```

### 簽署所需額外條目

每個 BIOS directory 必須新增：

#### Type 0x5 - Signing Key Token
```python
{
    "entryType": "IMAGE_ENTRY",
    "type": "0x5",
    "operation": EntryOperationType.Modify.value,
    "filename": "C:\\path\\to\\Rembrandt-4K-BIOS-SBR-0110.stkn",
    "level": "0x2A",
    "dirIndex": "0x0",
    "isPspEntry": False
}
```

Token 檔案位置: https://confluence.amd.com/display/MMDS/AMD+Reference+Platform+BIOS+Signing+Key+Tokens

#### Type 0x7 - RTM Signature
```python
{
    "entryType": "IMAGE_ENTRY",
    "type": "0x7",
    "operation": EntryOperationType.Add.value,
    "filename": "",             # 簽名條目不需要檔案
    "size": "0x200",            # 2K key=0x100, 4K key=0x200
    "level": "0x2A",
    "dirIndex": "0x0",
    "isPspEntry": False
}
```

### SP Function 伺服器

- https://atlkds-proxy01.amd.com/pspsp
- https://atlkds-proxy02.amd.com/pspsp
- https://cybkds-proxy01.amd.com/pspsp
- https://cybkdsweb02/pspsp
- https://atlkdsappv02/pspsp
- https://atlkdsapp04.amd.com/pspsp
- https://atlkdsappdev01/pspsp

## CBS Override 說明

### 標準 CBS Override (CbsOverride.py)

```python
isGbs = "0"  # 0=CBS Override, 1=GBS (不支援 API), 2=Binary CBS Override

replacementList = [
    {"CbsCmnCpuSmuPspDebugMode": "0"},
    {"CbsDbgRomArmorSupport": "0"},
    {"CbsDbgCpuSnpMemCover": "1"}
]
```

- 處理時間: 30-60 分鐘
- 完成後會收到 Email 通知
- 適用於標準 CBS 選項修改

### 二進制 CBS Override (BinaryCbsOverride.py)

```python
isGbs = "2"  # Binary Level CBS Override

replacementList = [
    {"CbsDbgPcieAllPortsPresetMaskCtl": "1"},
    {"CbsDbgPciePortAllPorts": "1"},
    {"CbsDbgPcieAllPortsPresetMask": "12"}
]
```

- 處理時間: 較快
- 直接在二進制層級修改
- 適用於需要快速修改的情況

## Option ROM Replacement

通過 GUID 識別並替換 BIOS 中的 Option ROM 模組：

```python
replacementList = [
    {
        "guid": "348C4D62-BFBD-4882-9ECE-C80BB1C4783B",
        "file": r"D:\path\to\OptionRom3.bin"
    },
    {
        "guid": "61F0BA73-93A9-419D-BD69-ADE3C5D5217B",
        "file": r"D:\path\to\OptionRom5.bin"
    }
]
```

GUID 可以從原始 BIOS 或平台文件中獲取。

## PSP Entry Comparison

比較兩個 BIOS 版本的 PSP 條目差異：

```python
# Base BIOS
PROCESSOR_NAME = "ShimadaPeak - Family 1Ah"
PLATFORM_NAME = "Rev_SHP_BoulderGulch_AMD_EDKII"
BASE_BIOS_TYPE = "Weekly BIOS"
REVISION = "WBK5709N_196"

# Compare BIOS
CMP_BIOS_TYPE = "User-Generated"
CMP_REVISION = r"D:\Input\BVM\WBK4B06N_102.FD"
CMP_PROGRAM = "BRH"
```

執行後會輸出比較結果頁面 URL:
```
http://bvm/bvm/compare/{request_id}
```

## 工作流程

所有 BVM 工具都遵循相同的基本流程：

```
1. Login                    ← 認證並取得 JWT token
2. GetProcessorList         ← 取得可用的處理器/平台
3. Generate*Request         ← 建立 BVM 請求
4. UploadReplacement        ← 上傳需要替換的檔案
5. Submit*Request           ← 提交到 BVM 進行處理
6. DownloadBIOS/DownloadTar ← 下載修改後的 BIOS
```

## 常見問題

### Q: Directory Index (dirIndex) 如何設定？

**A:**
- 對於非 AB-recovery BIOS: `dirIndex = level - 1`
- 對於 AB-recovery BIOS:
  - A copy 通常是 `0x0`
  - B copy 通常是 `0x1`

### Q: User-Generated BIOS 路徑格式？

**A:** 使用原始字串避免反斜線轉義問題：
```python
revision = r"D:\path\to\BIOS.FD"  # 推薦
revision = "D:\\path\\to\\BIOS.FD"  # 也可以
```

### Q: 如何確定需要修改哪個 Entry Type？

**A:**
1. 查看平台的 PSP Directory 結構
2. 使用 PSP Directory Tool 或 UEFITool 分析原始 BIOS
3. 參考 AMD PPR (Processor Programming Reference) 文件

### Q: CBS 選項名稱從哪裡找？

**A:**
1. BVM Web 介面的 CBS Override 頁面
2. 平台的 CBS 文件
3. AGESA 原始碼中的 CBS 定義

### Q: 為什麼需要 pspConfig？

**A:** pspConfig 指定 PSP 配置檔案 (例如 "RMB", "PHX", "CZN")，不同平台有不同的 PSP 結構。

### Q: Request ID 有什麼用？

**A:**
- 追蹤請求狀態
- 作為後續操作的 base BIOS (`baseBIOSType="By Request Id"`)
- 在 BVM 網頁介面查看詳細資訊

### Q: DownloadBIOS 和 DownloadTar 有什麼差別？

**A:**
- `DownloadBIOS`: 只下載修改後的 BIOS 檔案 (.FD)
- `DownloadTar`: 下載完整的 tar 檔案，包含所有中間檔案和日誌

## BVM API 端點參考

```
Base URL: http://bvm/

認證:
  POST   /api/account/Login

主要功能:
  GET    /api/bvmmain/GetProcessorList
  POST   /api/bvmmain/UploadBaseBIOS
  POST   /api/bvmmain/UpdateNewName

PSP Operations:
  GET    /api/bvmpsp/GeneratePspRequest
  GET    /api/bvmpsp/GetAvailableOperations
  POST   /api/bvmpsp/UploadPspEntry
  POST   /api/bvmpsp/SubmitRequestAPI

CBS Override:
  GET    /api/bvmcbsoverride/GenerateConstructedRequest
  POST   /api/bvmcbsoverride/SubmitRequest
  POST   /api/bvmcbsoverride/SubmitBinaryLevelCbsOverrideRequest

Option ROM:
  GET    /api/bvmoptionrom/GenerateOptionRomRequest
  POST   /api/bvmoptionrom/UploadOptionRomAPI
  POST   /api/bvmoptionrom/SubmitOptionRomRequestAPI

Compare:
  GET    /api/bvmcompare/GenerateCompareRequest
  GET    /api/bvmcompare/GetPspDiff

下載:
  GET    /api/bvmresult/DownloadBIOSByRequestId
  GET    /api/bvmresult/DownloadTarByRequestId
```

## 版本歷史

### PspReplacement
- **v1.03** (current) - 最新版本
- v1.02 - 歷史版本
- v1.01 - 歷史版本
- v1.00 - 初始版本

### 其他工具
- **CbsOverride**: v1.03
- **BinaryCbsOverride**: v1.00
- **OptionRomReplacement**: v1.00
- **ComparePSPEntry**: v1.00

## 登出與資源管理

### 手動登出

完成操作後建議登出以釋放伺服器資源:

```python
from bvm_client import BvmClient

client = BvmClient(config_file="bvm_config.yaml")
# ... 執行操作 ...
client.logout()  # 手動登出
```

### Context Manager (推薦)

使用 `with` 語句自動管理登入/登出:

```python
# 自動登出
with BvmClient(config_file="bvm_config.yaml") as client:
    processors = client.get_processor_list()
    # ... 執行操作 ...
# 離開 with block 時自動登出

# PSP Replacement 也支援
with PspReplacer(config_file="bvm_config.yaml") as replacer:
    replacer.replace_psp_entries(...)
# 自動登出
```

**優點:**
- 確保即使發生錯誤也會登出
- 程式碼更簡潔
- 符合 Python 最佳實踐

詳細範例請參考 `context_manager_example.py`

## 日誌機制

BVM 客戶端提供雙層日誌系統:
- **Console (螢幕)**: 只顯示主要訊息 (INFO 級別)
- **Log File**: 記錄詳細的調試資訊 (DEBUG 級別)

### 預設行為

```python
# 預設配置: Console=INFO, File=DEBUG
with BvmClient(config_file="bvm_config.yaml") as client:
    client.get_processor_list()  # 螢幕只顯示主要訊息
# 詳細資訊記錄在 bvm_client.log
```

**螢幕輸出:**
```
Logging in...
Log in successful
Retrieved 61 processors
```

**日誌檔案 (bvm_client.log):**
```
2025-12-06 13:31:45 - __main__ - INFO - Logging in...
2025-12-06 13:31:45 - __main__ - DEBUG - Login URL: http://bvm/api/account/Login
2025-12-06 13:31:45 - __main__ - DEBUG - Username: chri
2025-12-06 13:31:46 - __main__ - DEBUG - Login response status: 200
2025-12-06 13:31:46 - __main__ - DEBUG - Token received: eyJhbGci...
2025-12-06 13:31:46 - __main__ - INFO - Log in successful
```

### 自訂日誌配置

#### 1. Quiet Mode - 只顯示警告和錯誤

```python
import logging

with BvmClient(
    config_file="bvm_config.yaml",
    console_level=logging.WARNING  # 螢幕只顯示警告/錯誤
) as client:
    client.get_processor_list()  # 無輸出，除非有錯誤
```

#### 2. Verbose Mode - 螢幕也顯示調試資訊

```python
with BvmClient(
    config_file="bvm_config.yaml",
    console_level=logging.DEBUG  # 螢幕顯示所有詳細資訊
) as client:
    client.get_processor_list()
```

#### 3. 自訂日誌檔案

```python
with BvmClient(
    config_file="bvm_config.yaml",
    log_file="my_operation.log"  # 使用自訂日誌檔案
) as client:
    client.get_processor_list()
```

#### 4. Production Mode - 最小化輸出

```python
with BvmClient(
    config_file="bvm_config.yaml",
    log_file="production.log",
    console_level=logging.ERROR,  # 只顯示錯誤
    file_level=logging.INFO       # 日誌檔案不記錄 DEBUG
) as client:
    client.get_processor_list()
```

### 日誌級別說明

| 級別 | 用途 | 範例 |
|------|------|------|
| DEBUG | 系統詳細資訊 | API URLs, response codes, token details |
| INFO | 主要操作訊息 | "Logging in...", "Retrieved 61 processors" |
| WARNING | 警告訊息 | 非關鍵性錯誤 |
| ERROR | 錯誤訊息 | 登入失敗、下載失敗 |

### 最佳實踐

1. **開發環境**: 使用預設配置或 verbose mode
2. **生產環境**: 使用 quiet mode 或 production mode
3. **調試問題**: 檢查日誌檔案中的 DEBUG 資訊
4. **多步驟操作**: 為每個步驟使用不同的日誌檔案

詳細範例請參考 `logging_example.py`

## 安全注意事項

1. **不要提交密碼到版本控制**: 使用環境變數或配置檔案
2. **驗證 BIOS 修改**: 在實際設備上測試前，先用模擬器驗證
3. **備份原始 BIOS**: 在修改前務必備份
4. **簽署金鑰**: Token 檔案和簽署金鑰需要妥善保管

## 支援的平台

工具支援所有 AMD 平台，包括但不限於：

- **Family 19h**: Rembrandt, Phoenix, StrixPoint
- **Family 1Ah**: Krackan, ShimadaPeak
- **Family 17h**: Cezanne, Lucienne
- 其他在 BVM 系統中註冊的平台

## 授權

內部工具，僅供 AMD 及授權合作夥伴使用。

## 聯絡資訊

如有問題或建議，請聯絡 BVM 管理團隊或提交 issue。
