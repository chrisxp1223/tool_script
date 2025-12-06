# BVM 配置檔案使用指南

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 建立配置檔案

執行以下命令會自動建立 `bvm_config.yaml`：

```bash
python bvm_config.py
```

或手動編輯 `bvm_config.yaml`：

```yaml
# BVM 認證
bvm:
  username: your_username
  password: your_password
  base_url: http://bvm/

# 檔案路徑
paths:
  binary_dir: D:\BVM\binaries      # 二進制檔案 (SMU, PSP 韌體)
  download_dir: D:\BVM\downloads   # 下載的 BIOS
  token_dir: D:\BVM\tokens         # 簽署 Token 檔案

# 平台設定
platform:
  processor_name: Rembrandt - Family 19h
  platform_name: Rev_RMB_Mayan_Insyde_EDKII
  psp_config: RMB
```

### 3. 使用配置

```python
from bvm_client import BvmClient

# 自動載入 bvm_config.yaml
client = BvmClient(config_file="bvm_config.yaml")

# 或指定其他配置檔案
client = BvmClient(config_file="my_config.yaml")
```

## 配置檔案結構

### 核心配置

```yaml
bvm:
  username: lahan              # BVM 使用者名稱 (必填)
  password: your_password      # BVM 密碼 (必填)
  base_url: http://bvm/        # BVM 伺服器 URL (可選)
```

### 檔案路徑配置

```yaml
paths:
  # 二進制檔案目錄
  binary_dir: D:\BVM\binaries

  # 下載目錄
  download_dir: D:\BVM\downloads

  # Token 檔案目錄 (用於 BIOS 簽署)
  token_dir: D:\BVM\tokens
```

目錄會自動建立，不需要手動建立。

### 平台配置

```yaml
platform:
  processor_name: Rembrandt - Family 19h
  platform_name: Rev_RMB_Mayan_Insyde_EDKII
  psp_config: RMB
```

支援的平台:
- **Rembrandt (RMB)**: `Rev_RMB_*`
- **Phoenix (PHX)**: `Rev_PHX_*`
- **StrixPoint (STX)**: `Rev_STX_*`
- **Krackan (KRK)**: `Rev_KRK_*`

### 預設參數

```yaml
defaults:
  base_bios_type: PI BIOS      # Weekly BIOS | PI BIOS | User-Generated | By Request Id
  purpose: BVM API automation
  sign_type: NOSIGN            # NOSIGN | PK
  sign_hp: "0"
```

### PSP Replacement 配置

```yaml
psp:
  smu_firmware: SMU_46.59.0.bin

  signing:
    sp_function: SIGN REMBRANDT BIOS (4K)
    token_file: Rembrandt-4K-BIOS-SBR-0110.stkn
    key_size: "0x200"  # 4K=0x200, 2K=0x100
```

### CBS Override 配置

```yaml
cbs:
  config_program: Rev_RMB_Mayan_Insyde_EDKII
  is_gbs: "0"  # 0=CBS, 2=Binary CBS
```

### Option ROM 配置

```yaml
option_rom:
  roms:
    - guid: 348C4D62-BFBD-4882-9ECE-C80BB1C4783B
      file: OptionRom3.bin
    - guid: 61F0BA73-93A9-419D-BD69-ADE3C5D5217B
      file: OptionRom5.bin
```

## 使用範例

### 範例 1: 基本使用

```python
from bvm_config import BvmConfig

config = BvmConfig("bvm_config.yaml")

print(f"Username: {config.username}")
print(f"Platform: {config.platform_name}")
print(f"Binary Dir: {config.binary_dir}")
```

### 範例 2: 檔案路徑處理

```python
config = BvmConfig("bvm_config.yaml")

# 取得完整路徑
smu_path = config.get_binary_path("SMU_46.59.0.bin")
# → D:\BVM\binaries\SMU_46.59.0.bin

download_path = config.get_download_path("output.FD")
# → D:\BVM\downloads\output.FD

token_path = config.get_token_path("token.stkn")
# → D:\BVM\tokens\token.stkn
```

### 範例 3: PSP Replacement 使用配置

```python
from bvm_client import BvmClient
from bvm_config import BvmConfig

# 載入配置
config = BvmConfig("bvm_config.yaml")
client = BvmClient(config=config)

# 使用配置的路徑
smu_binary = config.get_binary_path("SMU_46.59.0.bin")
download_path = config.get_download_path("modified_bios.FD")

replacementList = [
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x8",
        "operation": 2,  # Modify
        "filename": smu_binary,  # 使用配置的路徑
        "level": "0x2A",
        "dirIndex": "0x1",
        "isPspEntry": True
    }
]

# 執行操作...
# client.download_bios(request_id, download_path)
```

### 範例 4: Option ROM 使用配置

```python
config = BvmConfig("bvm_config.yaml")

# 從配置讀取 ROM 清單
roms = config.get("option_rom.roms", [])

replacementList = []
for rom in roms:
    rom_path = config.get_binary_path(rom["file"])
    replacementList.append({
        "guid": rom["guid"],
        "file": rom_path
    })
```

### 範例 5: BIOS 簽署使用配置

```python
config = BvmConfig("bvm_config.yaml")

# 簽署參數
signType = config.sign_type  # 從 defaults 讀取
signSpFunction = config.get("psp.signing.sp_function")
tokenFile = config.get_token_path(config.get("psp.signing.token_file"))
keySize = config.get("psp.signing.key_size")

# 建立簽署條目
signingEntries = [
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x5",
        "filename": tokenFile,  # 使用配置的 token 路徑
        "level": "0x2A",
        "isPspEntry": False
    },
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x7",
        "filename": "",
        "size": keySize,  # 使用配置的 key size
        "level": "0x2A",
        "isPspEntry": False
    }
]
```

## 高級用法

### 讀取任意配置值

```python
config = BvmConfig("bvm_config.yaml")

# 使用點號路徑
username = config.get("bvm.username")
binary_dir = config.get("paths.binary_dir")
smu_file = config.get("psp.smu_firmware")

# 提供預設值
custom = config.get("custom.setting", default="default_value")
```

### 修改並儲存配置

```python
config = BvmConfig("bvm_config.yaml")

# 修改值
config.set("defaults.purpose", "New purpose")
config.set("platform.psp_config", "PHX")

# 儲存到檔案
config.save("bvm_config_modified.yaml")
```

### 多個配置檔案

```python
# 不同平台使用不同配置
rmb_config = BvmConfig("config_rembrandt.yaml")
phx_config = BvmConfig("config_phoenix.yaml")

# 建立對應的客戶端
rmb_client = BvmClient(config=rmb_config)
phx_client = BvmClient(config=phx_config)
```

## 配置檔案範本

### Rembrandt 平台

```yaml
bvm:
  username: your_username
  password: your_password

paths:
  binary_dir: D:\BVM\RMB\binaries
  download_dir: D:\BVM\RMB\downloads
  token_dir: D:\BVM\RMB\tokens

platform:
  processor_name: Rembrandt - Family 19h
  platform_name: Rev_RMB_Mayan_Insyde_EDKII
  psp_config: RMB

psp:
  smu_firmware: SMU_RMB_46.59.0.bin
  signing:
    sp_function: SIGN REMBRANDT BIOS (4K)
    token_file: Rembrandt-4K-BIOS-SBR-0110.stkn
    key_size: "0x200"
```

### Phoenix 平台

```yaml
bvm:
  username: your_username
  password: your_password

paths:
  binary_dir: D:\BVM\PHX\binaries
  download_dir: D:\BVM\PHX\downloads
  token_dir: D:\BVM\PHX\tokens

platform:
  processor_name: Phoenix - Family 19h
  platform_name: Rev_PHX_Mayan_AMD_EDKII
  psp_config: PHX

psp:
  smu_firmware: SMU_PHX_latest.bin
  signing:
    sp_function: SIGN PHOENIX BIOS (4K)
    token_file: Phoenix-4K-BIOS-SBR-0110.stkn
    key_size: "0x200"
```

## 安全建議

### 1. 不要將密碼提交到 Git

在 `.gitignore` 中添加：

```
bvm_config.yaml
bvm_config.yml
*_config.yaml
```

### 2. 使用環境變數 (可選)

```python
import os
from bvm_config import BvmConfig

config = BvmConfig("bvm_config.yaml")

# 從環境變數覆寫密碼
password = os.getenv("BVM_PASSWORD", config.password)
client = BvmClient(username=config.username, password=password)
```

### 3. 使用權限受保護的配置檔案

```bash
# Linux/WSL
chmod 600 bvm_config.yaml

# Windows
icacls bvm_config.yaml /inheritance:r /grant:r "%USERNAME%:F"
```

## 疑難排解

### 找不到配置檔案

```
FileNotFoundError: Config file not found
```

**解決方法:**
1. 確認檔案存在: `ls bvm_config.yaml`
2. 使用絕對路徑: `BvmConfig("/full/path/to/bvm_config.yaml")`
3. 建立預設配置: `python bvm_config.py`

### YAML 解析錯誤

```
yaml.scanner.ScannerError: ...
```

**解決方法:**
1. 檢查 YAML 語法 (縮排、冒號、引號)
2. 使用線上 YAML 驗證器
3. 數字和布林值要加引號: `"0"`, `"false"`

### 路徑錯誤

```
FileNotFoundError: [Errno 2] No such file or directory
```

**解決方法:**
1. Windows 路徑使用雙反斜線: `D:\\BVM\\binaries`
2. 或使用正斜線: `D:/BVM/binaries`
3. 或使用原始字串 (在 Python 中): `r"D:\BVM\binaries"`

## 完整範例

查看 `example_usage.py` 獲取完整的使用範例：

```bash
python example_usage.py
```
